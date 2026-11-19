# Plan: Agentic Analyst (TimeNet hackathon + Agentic AI lecture project)

Last updated: Mon 16 Nov 2026, evening. This file is the handover document: someone with no other context should be able to continue from it.

## Where things stand

- The first dataset connector (Context is Key) is written, tested and pushed to our fork. Its pull request is not opened yet.
- No model has been trained and nothing has been evaluated.
- **One decision is waiting on the team** and blocks the next step: the training task (see "Decision needed").

## Idea in one sentence

An agentic analyst that turns a client's raw KPI time series into a verified, partner-ready insight memo in hours instead of weeks. The core is a time-series language model (OpenTSLM) that reads a series and writes about it in natural language.

## Two deliverables

| | TimeNet hackathon, Round 1 | Agentic AI lecture project (ETH) |
|---|---|---|
| Deadline | Sun 22 Nov, 23:59 PST (Mon 23 Nov, 08:59 CET) | Fri 11 Dec, end of day |
| Team | 4 of us (limit is 2–4) | All 5 |
| What we hand in | PR link adding a dataset to TimeNet, project link (demo, pitch or page), optional GitHub repo, public X and LinkedIn posts with metric screenshots, Discord post, submission form | 5-minute video with all members presenting, plus the code |
| What is judged | Use case and impact, technical execution, data and TimeNet, results and evaluation, showcase and social engagement | Problem with evidence, KPIs, business case, agentic proof of concept, performance on the KPIs. Business case counts more than the technical solution. |

Hackathon page: https://challenge.timenet.ai/#build. The task there is to onboard a dataset in TimeNet format and train or fine-tune a temporal model such as OpenTSLM.

The hackathon produces the dataset and the model. The lecture project wraps the model in an agent and adds the business case. The agent is not needed for the hackathon.

## Repositories and folders

| What | Where | Notes |
|---|---|---|
| Project repo | `BASI/code/`, remote `github.com/bwinner1/agentic-analyst`, branch `master` | Holds this plan, later the training, evaluation and agent code. This is the repo for the lecture hand-in and the optional hackathon repo link. |
| TimeNet clone | `BASI/code/TimeNet/` | A separate git repo nested in the project folder and git-ignored by the project repo. `origin` is our fork `github.com/bwinner1/TimeNet`, `upstream` is `github.com/OpenTSLM/TimeNet`. |
| Connector branch | `feat/connector-context-is-key` in the TimeNet clone, pushed to the fork | One commit, `feat(connectors): add the Context is Key connector`. |

Keep the two repos separate. The TimeNet pull request must contain only connector code.

## Working conventions

- Commits and PR descriptions carry no AI attribution lines (no `Co-Authored-By`).
- Batu usually commits and pushes himself. Prepare the change and propose a commit message.
- TimeNet requires Conventional Commits (`feat(connectors): ...`), Conventional Branch names, and the `area:connectors` label on connector PRs. See `TimeNet/CONTRIBUTING.md` and `TimeNet/AGENTS.md`.
- TimeNet's connector workflow is in `TimeNet/.agents/skills/add-dataset-connector/SKILL.md`. It requires the user's sign-off on the dataset id, task type and one example row before any connector code is written.
- Checks to run before a TimeNet PR: `make check`, `make check-ci`, `make test-unit`, `make test-connectors`, `make license-check`.
- Known local quirk: `make test` fails one test, `test_an_editable_install_outside_git_fails_with_the_git_error`, because it matches git's English error text and this machine's git is German. It fails on unmodified `main` too and passes with `LC_ALL=C`.
- `make install-hooks` has not been run in the clone, so pre-commit hooks do not run on commit yet.

## Done so far

### Organizers' answers (16 Nov, on Discord)

- Fine-tuning on other data than the onboarded dataset is allowed. The submission must say which data we trained on and which we evaluated on.
- A Time-MMD connector PR is accepted. On the dataset card: `license: ODC-By-1.0`, `source_url` pointing to the repo, and a line in the description saying that the repo has no LICENSE file and that the paper describes the sources as authorized for non-commercial distribution. Do not rehost the data in the PR.

### Context is Key connector

- Dataset id `servicenow/context-is-key`, version 1.0.0, in `TimeNet/packages/timenet-connectors/src/timenet_connectors/datasets/servicenow/context_is_key/`.
- Source: Hugging Face repo `ServiceNow/context-is-key`, Apache-2.0, pinned to commit `32da467ade142a16d099675e78b1129745c5ef7d`, file `data/test-00000-of-00001.parquet`.
- Output: 355 `ForecastingTask`s, all in the test split. Each has a history record and a future record on a shared time origin. The prompt is background + scenario + constraints. The task metadata keeps the three text parts separately and the fields the benchmark's metric needs.
- Choices made: the `test` file and not `ICML2025` (they differ in the scenario text of 15 rows); naive timestamps read as UTC, as TimeNet's ARFBench connector does; monthly series get an irregular axis; values are dimensionless float64; domain `general`.
- Verified: full build from Hugging Face and read-back, 13 connector tests, and all checks listed above.
- Possible hardening a reviewer may ask for: a null value or malformed JSON in the source raises a plain Python error, not a TimeNet exception. The pinned file has neither.

### Finding that changed the plan: OpenTSLM writes text, not forecasts

OpenTSLM (`github.com/OpenTSLM/OpenTSLM`, `pip install opentslm`) takes time series plus text and generates text. Its published checkpoints cover question answering (TSQA), captioning (M4), and chain-of-thought classification (activity, sleep, ECG). None outputs numeric forecasts. Training runs through `curriculum_learning.py` with dataset classes under `src/opentslm/time_series_datasets/`. The default base model is `meta-llama/Llama-3.2-1B`, which is gated on Hugging Face.

So the earlier plan (fine-tune OpenTSLM, score its forecasts on Context is Key) does not fit the model.

## Decision needed

**Recommended, not yet confirmed by the team:** make Time-MMD the main dataset and fine-tune OpenTSLM to write the report for a window of a series.

- Training task: a window of a series as input, the aligned `fact` report text for that period as the target. In TimeNet this is an `AnswerTask`.
- Evaluation: hold out the most recent period of each domain. Compare fine-tuned OpenTSLM with pretrained OpenTSLM and with a text-only LLM that gets the numbers as plain text. Score with text overlap, an LLM judge, and a check that numbers in the generated text match the series.
- Context is Key stays a finished dataset PR that counts for "data and TimeNet", but it is no longer the evaluation set.

The alternative is to keep forecasting with a different model family. That drops OpenTSLM and the "numbers into natural-language insight" story, so it is not recommended.

## Time-MMD: what is known

- Source: `github.com/AdityaLab/Time-MMD`, latest commit `00281e2d86058286d5548b15a7670e8eda57ef62` (14 Jan 2025). Paper: arXiv 2406.08627.
- Layout: `numerical/<Domain>/<Domain>.csv` and `textual/<Domain>/<Domain>_report.csv` and `_search.csv`, for 10 domain folders: Agriculture, Climate, Economy, Energy, Environment, Health_AFR, Health_US, Security, SocialGood, Traffic.
- Numerical files: a target column `OT`, `start_date` and `end_date` per row, and covariate columns that differ per domain. Frequency differs per domain (Economy monthly, Energy and Health_US weekly, Environment daily). Economy is stored newest-first and needs sorting. Some covariate columns hold text placeholders such as `X` (Health_US).
- Text files: columns `start_date`, `end_date`, `fact`, `preds`, plus an unnamed index column. Economy has 435 report rows and 2,314 search rows.
- Text quality is uneven: the text is LLM-summarised and some rows are only `NA`. The connector needs to filter these. Report rows look more useful than search rows.
- Only Economy, Energy, Health_US and Environment have been inspected. The other six domains have not.
- Leakage to watch: `preds` holds predictions about the future, and `fact` describes its own period. Decide per task which text may be an input and which is the target.

## Next steps

### Things with waiting time (team members, start now)

1. Request the Nebius compute credits, if not done with the registration.
2. Request access to `meta-llama/Llama-3.2-1B` on Hugging Face and create a read token. Training is blocked without it.
3. Confirm the training direction (see "Decision needed").

### Tue–Wed: data

4. Time-MMD connector design: dataset id, task type and one example row, for the team's sign-off.
5. Implement the connector with tests, on a second branch, with the organizers' license wording on the dataset card.
6. Open the Context is Key PR against `OpenTSLM/TimeNet` with the title `feat(connectors): add the Context is Key connector` and the label `area:connectors`. Batu wants to open it later rather than now. Note that the branch on the fork is already public, and that another team could open a PR for the same dataset first.

### Wed–Fri: model

7. Training code in the project repo: a loader that reads the Time-MMD dataset through TimeNet and feeds OpenTSLM's training loop.
8. Small proof run on Nebius with a few hundred samples, by Wednesday evening. This is the riskiest step.
9. Full fine-tuning run.

### Fri–Sat: results

10. Evaluation on the held-out period against the two baselines.
11. Friday evening: fallback decision. If the fine-tune is not usable, submit the dataset PRs with a pretrained-model evaluation and enter the trained model in a later round.

### Sat–Sun: submission

12. Project page or demo: the problem, the data, the results, the limits, who benefits.
13. X and LinkedIn posts with metric screenshots, and the Discord post.
14. Submission form, by Sunday evening CET.

Steps 5 and 7 can run in parallel. One person can prepare 12 and 13 from Thursday. The fifth team member can start on the business-case evidence.

## Phase 2: lecture project (23 Nov – 11 Dec)

| When | Work |
|---|---|
| 23–29 Nov | Business case: choose the buyer, collect evidence (analyst time use, day rates, market size), define the KPIs, build a bottom-up ROI model (hours × rate × engagements per year). In parallel, build the agent skeleton in Python. |
| 30 Nov – 6 Dec | Complete the agent, run it on the client dataset, measure the KPIs. |
| 7–10 Dec | Video script, recording with all five presenting, edit to 5 minutes. |
| 11 Dec | Upload the video and the code to Polybox. |
| 16 Dec | Presentation, if we are selected. |

### Agent architecture

```
Orchestrator LLM (planner)
 ├─ Data tool: load client KPIs (TimeNet loader or CSV)
 ├─ Explainer: the fine-tuned OpenTSLM from Phase 1 (series in, text out)
 ├─ Forecaster: a separate forecasting model, since OpenTSLM does not forecast
 ├─ Anomaly detector: flag outliers and structural breaks
 ├─ Context retriever: news and reports for the period
 ├─ Verifier: check every number in the text against the data
 └─ Report writer: memo for the partner, with human approval
```

### KPIs

| Business KPI | How the proof of concept measures it |
|---|---|
| Time to insight | Pipeline run time against an estimated manual baseline |
| Analyst hours and cost per deliverable | Hours saved × blended rate |
| Insight accuracy | Share of claims the verifier confirms |
| Forecast accuracy | MASE or sMAPE on held-out data against naive baselines |
| Outlier detection quality | Precision and recall on injected anomalies |
| Partner acceptance | LLM judge plus a small human rating |

Client data for the demo: UCI Online Retail II or synthetic data. Not inspected yet.

## Open points

1. The training direction (see "Decision needed").
2. Who takes which hackathon task, and who is the fifth member.
3. Whether the TimeNet PR must be merged by the deadline or only opened. The hackathon page says "a PR link". Worth one question on Discord.
4. Buyer for the business case: consulting firm on fixed-fee engagements, or corporate FP&A team. Decide by 25 Nov. Both use the same agent; only the ROI model and the story differ.
5. Compute after the hackathon, once the Nebius credits are used up. The agent only needs inference.
6. Agent framework in Python (for example LangGraph or the Claude Agent SDK). Decide in the week of 23 Nov.
