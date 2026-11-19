# Plan: Agentic Analyst

Updated Thu 19 Nov 2026. This is the handover document for the team and for any agent taking over.

## The idea

Analysts spend weeks turning business time series into written insight: what moved, when, and why. We fine-tune a time-series language model (OpenTSLM) to write the first draft: given a window of a series, it writes the report for that period. For the lecture, an agent wraps this model and turns client KPIs into a verified memo for a partner.

## Deadlines

| | TimeNet hackathon, Round 1 | Agentic AI lecture (ETH) |
|---|---|---|
| Due | **Sun 22 Nov, 23:59 PST** (Mon 08:59 CET) | Fri 11 Dec |
| Team | 4 people | 5 people |
| Hand in | PR link adding a dataset to TimeNet, trained model with results, project page, X + LinkedIn posts with metric screenshots, Discord post, submission form | 5-minute video with all members presenting, plus the code |
| Judged on | Use case, technical execution, data and TimeNet, results and evaluation, showcase and social reach | Problem with evidence, KPIs, business case, agentic proof of concept, performance on the KPIs. Business case counts more than the tech. |

## Status

| Item | State |
|---|---|
| Team registration, Nebius credits | Done |
| Context is Key connector | Done and pushed to the fork. PR not opened yet (Batu opens it later). |
| Time-MMD connector | Not started. Design needs sign-off first. |
| Training code, fine-tuning, evaluation | Not started |
| Project page, posts, submission form | Not started |
| Hugging Face access to `meta-llama/Llama-3.2-1B` | Unknown. Required for training. |

Three days are left, so the schedule below is tight. Monday's plan had the proof training run by Wednesday.

## Decisions made

- **Task: report generation, not forecasting.** OpenTSLM takes series plus text and generates text. Its checkpoints do QA, captioning and chain-of-thought classification; none forecasts. So we train it to write reports from series.
- **Training and test data: Time-MMD**, split by time. Context is Key stays a finished dataset PR but is used for neither training nor evaluation (see open point 1).
- **Three systems are compared:** Claude, pretrained OpenTSLM, fine-tuned OpenTSLM (see Evaluation).
- **Organizers confirmed:** training on one dataset and onboarding another is fine (the submission must say which is which), and a Time-MMD connector PR is accepted with the license wording below.

## Datasets

### 1. Context is Key: dataset PR, done

- ServiceNow benchmark, ICML 2025, Apache-2.0. Hugging Face `ServiceNow/context-is-key`, pinned to commit `32da467ade142a16d099675e78b1129745c5ef7d`, file `data/test-00000-of-00001.parquet`.
- 355 instances (71 task types × 5 seeds) from 7 domains, built so that a good forecast needs the text.
- TimeNet id `servicenow/context-is-key`: per instance, one history record, one future record, and one `ForecastingTask` in the test split. The prompt is background + scenario + constraints.

Example (`ElectricityIncreaseInPredictionTask`, seed 1):

```
background:  "This is the electricity consumption recorded in Kilowatt (kW) in city A."
scenario:    "Suppose that there is a heat wave in city A from 2013-05-28 12:00:00 for 2 hours
              in city A, leading to excessive use of air conditioning, and 4 times the usual
              electricity being consumed."
history:     144 hourly values, 2013-05-22 04:00 → 2013-05-28 03:00   (351.25, 296.45, ...)
future:       24 hourly values, 2013-05-28 04:00 → 2013-05-29 03:00   (345.31, 297.40, ...)
```

### 2. Time-MMD: training data and second PR, to do

- NeurIPS 2024 dataset pairing series with text. GitHub `AdityaLab/Time-MMD`, pin commit `00281e2d86058286d5548b15a7670e8eda57ef62`.
- 10 domain folders: Agriculture, Climate, Economy, Energy, Environment, Health_AFR, Health_US, Security, SocialGood, Traffic.
- Per domain: `numerical/<D>/<D>.csv` (target column `OT`, covariates, `start_date`, `end_date`) and `textual/<D>/<D>_report.csv` and `_search.csv` (`start_date`, `end_date`, `fact`, `preds`).
- Frequency differs per domain: Economy monthly, Energy and Health_US weekly, Environment daily.
- License: the repo has no LICENSE file. On the dataset card, as the organizers asked: `license: ODC-By-1.0`, `source_url` to the repo, and a description line saying the repo has no LICENSE file and that the paper describes the sources as authorized for non-commercial distribution. Do not rehost the data.

Example (Economy, US trade balance; the series appears to be in millions of USD):

```
series window (OT = Exports − Imports), monthly:
  2014-07  -71,807.5
  2014-08  -59,686.3
  ...
  2015-05  -58,364.8
  2015-06  -66,404.0

report for 2015-06-01 → 2015-06-30:
  fact:  "The U.S. international trade deficit increased by $2.9 billion to $43.8 billion in
          June 2015, with exports decreasing by $0.1 billion to $188.6 billion and imports
          increasing by $2.8 billion to $232.4 billion."
  preds: "In the long term (next 4-18 months), the trade deficit may narrow as the dollar's
          strength begins to fade, ..."
```

Things to handle in the connector:

- **The report numbers do not match the series.** The report says a $43.8B deficit and $188.6B exports. The series has −$66.4B and $131.0B. The report probably quotes goods-and-services figures and the series looks like goods only (an inference, not confirmed). The direction can differ too. This affects the evaluation (see below).
- Economy numbers are stored newest-first; sort them.
- Some rows hold only `NA` text, and some covariates hold placeholders such as `X` (Health_US). Filter or skip, and never fill in values.
- `preds` talks about the future. Use only `fact` as a target.
- Text coverage is shorter than the series: Economy reports start in 1995, the series in 1987.
- Only Economy, Energy, Health_US and Environment have been looked at.

## Training task

- Input: a window of a series (for example 12 months) plus a short prompt naming the variable.
- Target: the `fact` text of the report for the window's last period.
- TimeNet task type: `AnswerTask`.
- Split by time: the most recent period of each domain is the test set, and nothing from it is used in training.
- Model: OpenTSLM (`pip install opentslm`, repo `OpenTSLM/OpenTSLM`) on `meta-llama/Llama-3.2-1B`. Soft-prompt (SP) variant first, as it needs less memory. Training goes through OpenTSLM's dataset classes in `src/opentslm/time_series_datasets/`, so we need an adapter from TimeNet to that format.

## Evaluation

Do not rely on an LLM judge alone. Many report sentences rely on outside knowledge that is not in the series, so similarity to the reference text is a weak measure. Score what the series determines.

| Layer | Measures | Scoring |
|---|---|---|
| 1. Series questions (main) | Does the model read the series correctly: direction over the window, largest change, latest value vs. range? | Exact accuracy, computed from the series by code |
| 2. Claim check (main) | Are the numbers and directions in the generated text true? | Extract claims, check against the series by code. Report directional accuracy, numeric accuracy within a tolerance, and the rate of invented numbers. |
| 3. LLM judge | Overall quality | Blind pairwise comparison with a rubric. The team rates 30–50 pairs to measure agreement with the judge. |
| 4. Reference similarity | Closeness to the real report | ROUGE-L or BERTScore, context only |

Because the reference reports use other figures than the series, layer 2 must check claims against the **series**, not against the reference text, and layer 4 is a weak signal.

### The three systems

All three get the same test tasks from the Time-MMD dataset loaded through TimeNet, with the same prompt. Only the model and the way the series is passed in differ.

| # | System | How it gets the series | Role |
|---|---|---|---|
| 1 | Claude (`claude-opus-5-5`, Anthropic API) | Numbers written into the prompt as text | Strong general LLM, upper reference |
| 2 | OpenTSLM, pretrained | Native time-series input | Baseline: the model before fine-tuning |
| 3 | OpenTSLM, fine-tuned on the Time-MMD train period | Native time-series input | Our model |

- Train on the Time-MMD train period, test on the Time-MMD test period (the most recent period of each domain). State both in the submission, as the organizers asked.
- Extra rows if time allows: system 3 with shuffled series (if its scores do not drop, the model ignores the series), and "repeat last period's report" as a trivial baseline.
- How to read the results: 3 beating 2 shows the fine-tune works. 3 close to 1 shows that a 1B model on our own GPU, where client data never leaves the firm, approaches a frontier API model. 3 below 1 is still a valid result if reported with the cost per report.
- Claude may have seen the real reports in its training data, since they describe public events from 1995–2024. That can inflate its scores on layers 3 and 4, but not on layers 1 and 2, which are checked against the series.
- Claude needs an Anthropic API key; the Nebius credits do not cover it. Fix the model ID and effort level and record both with the results. A few hundred test reports at Opus 5.5 prices ($4 input / $20 output per million tokens) should stay in the tens of dollars.

Minimum for Sunday: layers 1 and 2 with all comparisons. Layers 3 and 4 if time allows.

## Schedule to Sunday

| Day | Work |
|---|---|
| Thu 19 | Time-MMD connector design → sign-off → implementation. In parallel: TimeNet-to-OpenTSLM adapter, Nebius machine set up, Llama access checked. |
| Fri 20 | Proof run on a few hundred samples in the morning, full run started by the evening. Layer 1 and 2 scoring code. **Friday evening: fallback decision.** |
| Sat 21 | Evaluation and results table. Project page drafted. |
| Sun 22 | Open both PRs at the latest, posts with metric screenshots, Discord post, form. Submit by Sunday evening CET. |

Fallback if the fine-tune is not usable by Friday evening: submit both dataset PRs with the pretrained OpenTSLM evaluation and the baselines, and enter the trained model in a later round.

## Repos and conventions

- **Project repo**: `BASI/code/` → `github.com/bwinner1/agentic-analyst` (branch `master`). Plan, training, evaluation and agent code. Lecture hand-in.
- **TimeNet clone**: `BASI/code/TimeNet/`, a separate repo, git-ignored by the project. `origin` = fork `bwinner1/TimeNet`, `upstream` = `OpenTSLM/TimeNet`. Branch `feat/connector-context-is-key`, one commit `feat(connectors): add the Context is Key connector`. Only connector code goes into TimeNet PRs.
- **No AI attribution** in commits or PRs. Batu usually commits and pushes himself.
- **TimeNet rules** (`CONTRIBUTING.md`, `AGENTS.md`): Conventional Commits and branch names, `area:connectors` label on the PR, Google-style docstrings, TimeNet exceptions on bad data, never fill missing data. The connector workflow in `.agents/skills/add-dataset-connector/SKILL.md` requires sign-off on dataset id, task type and an example row before coding.
- **Checks before a PR**: `make check`, `make check-ci`, `make test-unit`, `make test-connectors`, `make license-check`. Local quirk: one `make test` case fails because git here is German; it passes with `LC_ALL=C`.
- Open item on the Context is Key connector: a null value or malformed JSON in the source raises a plain Python error instead of a TimeNet exception. The pinned file has neither.

## Lecture project, after the hackathon

- 23–29 Nov: business case (choose the buyer, collect evidence, KPIs, bottom-up ROI) and the agent skeleton in Python.
- 30 Nov – 6 Dec: finish the agent, run it on client data (UCI Online Retail II or synthetic), measure the KPIs.
- 7–10 Dec: video. 11 Dec: upload to Polybox. 16 Dec: presentation if selected.

Agent: an orchestrator LLM with tools for data loading, OpenTSLM as the explainer, a separate forecasting model, anomaly detection, context retrieval, a verifier that checks every number against the data, and a report writer with human approval.

KPIs: time to insight, analyst hours and cost per deliverable, insight accuracy (share of verified claims, the same check as evaluation layer 2), forecast accuracy, outlier detection, partner acceptance.

## Open points

1. **Fine-tune on Context is Key and evaluate on Time-MMD?** The team considered this. Not recommended: Context is Key teaches number forecasting while the evaluation asks for reports; it has only 355 instances from 71 templates, so the model would memorize them; and it is published as a test-only benchmark (our connector puts every task in the test split). If a train ≠ test story is wanted, hold out whole Time-MMD domains instead, for example train on eight domains and test on Economy.
2. Who on the team takes which task this week.
3. Whether the TimeNet PR must be merged by the deadline or only opened. Ask on Discord.
4. Buyer for the business case: consulting firm on fixed fees, or corporate FP&A team. Decide by 25 Nov.
5. Agent framework (for example LangGraph or the Claude Agent SDK). Decide in the week of 23 Nov.
