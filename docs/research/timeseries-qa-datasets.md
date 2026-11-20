# Time-series Q&A and caption datasets for business Q&A

Researched 2026-11-19. Sources are primary: arXiv pages, Hugging Face (HF) cards and API, GitHub repos, and the
TimeNet repo (cloned at `main` on 2026-11-19; open PRs listed with `gh`). **(unverified)** means I could not
confirm it from a primary source. "Checkable" means code can recompute the gold answer from the series.

## Recommendation (ranked for our use: business series, code-verifiable answers, 1B OpenTSLM, TimeNet contribution)

| # | Dataset | Business domain? | Answers checkable by code? | Real series? | License | In TimeNet? | Use for us |
|---|---|---|---|---|---|---|---|
| 1 | **Our own template QA on business series** (Time-MMD Economy/Retail, M4, FRED, Walmart) | Yes | Yes, by construction | Real | Inherits source (Time-MMD ODC-BY) | No: our contribution | **Train + eval** (main set) |
| 2 | **MTBench finance** (GGLabYale) | Finance (stocks + news) | Partly: trend bins and MACD/Bollinger computed from prices; MCQ written by an LLM | Real | **None stated** on repo/HF (unverified) | No | Eval (trend/indicator tasks); a small amount of training |
| 3 | **TSAQA** | Partly (ExchangeRate, FRED-MD among 13 domains) | Partly: transform and temporal tasks computed or templated; characterization labeled by an LLM vote | Mostly real | MIT | **Yes** (`tsaqa/tsaqa-benchmark`) | Train + eval (T/F and MCQ only) |
| 4 | **CaTS-Bench** | Yes: Walmart sales, UK online retail, GDP, CPI and unemployment covariates | No (captions); MCQ matching/lookup partly | Real | Not stated (unverified) | No | Eval of captions ("what happened?"); has human-fixed gold captions |
| 5 | **ChengsenWang/TSQA** (ChatTime) | No (synthetic) | Yes (KernelSynth + labels) | Synthetic | Apache-2.0 | **Yes** (`chengsenwang/tsqa`) | Already OpenTSLM stage 1; keep as warm-up |
| 6 | **OpenTSLM M4-Caption** | Partly (M4 spans finance, macro, micro, industry, demographic) | No (GPT-4o captions) | Real | Captions MIT; M4 none stated | PR #790 (open) | Train captioning; style source |
| 7 | **TimeSeriesExam-1** | No | Yes (template-generated synthetic) | Synthetic | MIT | PR #799 (open) | Eval of basic concepts (746 MCQ) |
| 8 | **TSAIA** (TS-Reasoner) | Finance + energy | Task-specific success criteria (unverified whether automatic) | Real-world formulations (unverified) | CC-BY-4.0 | No | Eval if we add a code/agent path |
| 9 | **Time-MQA TSQA** | Weak (finance = NAB ad-exchange anomalies + earnings calls) | Forecast/impute/anomaly yes; open QA from GPT-4o | Real + synthetic | Apache-2.0 (gated) | PRs #719-723 (open) | Train (sub-sample); eval only for MCQ/TF |
| 10 | **ChatTS training + eval A/B** | No (synthetic; AIOps-flavoured eval) | Alignment answers come from the generator's attributes; SFT is LLM-written | Synthetic (train); real + synthetic (eval) | Train: HF says Apache-2.0, README says MIT; eval CC-BY-4.0 (Zenodo) | PR #620 (open) | Train alignment; borrow the attribute schema |
| 11 | **Context is Key (CiK)** | Yes: retail, US unemployment, ATM withdrawals | Yes for the forecast (RCRPS); not QA | Real | Apache-2.0 | PR #788 (open) | Eval only (already used) |
| 12 | **TSRBench** | Includes finance | Mixed (labels, numbers, text) | Not stated | Not stated | No | Eval (secondary) |
| 13 | **ARFBench** | No (observability) | MCQ from expert incident threads | Real | Apache-2.0 | **Yes** (`datadog/arfbench`) | Eval of "when did it start?" localization; template ideas |
| 14 | Merrill et al. TS reasoning | Mixed scenarios | MCQ about LLM-generated scenarios | Synthetic (LLM-written code) | Repo MIT; HF none | PR #603 (open) | Optional eval |
| 15 | SciTS | Economics = stock forecast + stock MCQ | Mixed | Mostly real | **CC-BY-NC-SA-4.0** | No | Eval only (NC, share-alike) |
| - | Skip: TimerBed, VerbalTS, FinTSB, FinTradeBench, Time-MMD as QA | see notes | | | | | |

**Bottom line.** No public dataset is an "ECG-QA for business series": real economic, finance or retail series with
templated, code-checkable questions about direction, peaks, seasonality and components. MTBench finance and TSAQA's
FRED/ExchangeRate slices come closest. Build #1 and use #2-#4 as outside evaluations.

---

## TimeNet: what exists (repo `OpenTSLM/TimeNet`, `packages/timenet-connectors/.../datasets/`)

Merged connectors: `chengsenwang/tsqa` (Apache-2.0), `tsaqa/tsaqa-benchmark` (MIT), `datadog/arfbench` and
`datadog/arfbench-charts` (Apache-2.0), `bash-lab/sensorcaps` (Hippocratic 3.0), `physionet/ecg-qa-cot`,
`physionet/ptb-xl`, `physionet/sleep-edfx`, `opentslm/har-cot`, `opentslm/sleep-cot`, `timenet/hello-world`,
`timenet/test-mean`.

Open PRs that matter to us: #790 M4-Caption, #788 Context is Key, #799 TimeSeriesExam, #719-723 Time-MQA TSQA,
#637 and #469 **Time-MMD** ("Economy and Energy tasks"), #620 ChatTS, #616 VerbalTS, #603 Merrill TS reasoning,
#640 VeriTime, #577 TRACE weather, #801 EngineMT-QA.

Not in TimeNet in any form: MTBench, CaTS-Bench, TSAIA, TSRBench, SciTS, FinTSB.
**Check #637/#469 before writing a Time-MMD connector.** Someone has already started one. We could build our QA
tasks on top of their Records rather than duplicate them.

## OpenTSLM's own curriculum (repo `src/opentslm/time_series_datasets/`)

| Stage | Data | Source | Text origin |
|---|---|---|---|
| 1 MCQ | TSQA | `load_dataset("ChengsenWang/TSQA")`, i.e. **ChatTime's TSQA, not Time-MQA's** | Template labels on KernelSynth series |
| 2 Captioning | M4-Caption | ETH polybox zip | GPT-4o captions (TimeNet PR #790) |
| 3-5 CoT | HAR-CoT, SleepEDF-CoT, ECG-QA-CoT | polybox zips; ECG-QA from Jwoo5/ecg-qa + PTB-XL | LLM rationales over labelled data |

Practical note: OpenTSLM z-normalizes each series. Its prompt gives only the mean and std as text
(`"This is the time series, it has mean {mean:.4f} and std {std:.4f}:"`, `M4QADataset.py`). The model never sees
timestamps or absolute levels unless we put them in the text. Questions like "what happened last month?" need the
dates (start date, frequency) in the prompt, and exact-number answers depend on the model de-normalizing
correctly. Prefer answers it can check with a tolerance (direction, rank, date, percent change rounded to 1 dp).

---

## Per-dataset notes

**MTBench** ([arXiv 2503.16858](https://arxiv.org/abs/2503.16858), [GitHub](https://github.com/Graph-and-Geometric-Learning/MTBench), HF org `GGLabYale`)

Domains: finance and weather.
- Finance: 20k news articles (2021-05 to 2023-09) aligned with stock series. Short windows are 7 days at 5-minute
  resolution; long windows are 30 days at 1-hour resolution.
- Weather: 2k pairs from 50 US airport stations.

Tasks: forecasting (numeric); trend classification into 3 or 5 bins from percent change, e.g. Bearish < -4%
(**computed from prices**); technical indicators (MACD, Bollinger upper band, MSE-scored, also computed);
news-driven correlation labels and MCQ (A-D), where an LLM wrote the true/false MCQ statements and GPT-4o annotated
article metadata.

Pitfalls the authors report: about 20% of finance news-series pairs are misaligned (kept on purpose); correlation
labels skew negative and models default to "moderate positive"; output-format failures; some weather narratives are
LLM-written.

HF sets are small (QA sets < 1k each; stock set 1k-10k). No dataset license on HF or GitHub (unverified, ask the
authors). Use: the best outside eval for "direction/size of move" on real finance; a TimeNet contribution candidate
if the license is clarified.

**TSAQA** ([arXiv 2601.23204](https://arxiv.org/abs/2601.23204), [HF](https://huggingface.co/datasets/TSAQA/TSAQA-Benchmark), MIT, in TimeNet)

Size: 210k items (147k train, 21k val, 42k test), 13 domains. The finance/economy slices are ExchangeRate and FRED-MD.

Six tasks (anomaly detection, classification, characterization, comparison, data transformation, temporal
relationship) in T/F, 4-way MCQ and "puzzle" (patch ordering) formats. Data transformation is computed with
NumPy/SciPy and temporal relationship is templated. Characterization and comparison questions were written by GPT-4o
and answered by a weighted vote of GPT-4.1, Gemini-2.5-Flash and Claude-3.5-Sonnet, so they are **not**
code-checkable.

The best commercial model scores 65.08 on average zero-shot. Use: training with the FRED/ExchangeRate rows filtered
in; eval on the computed task families only.

**CaTS-Bench** ([arXiv 2509.20823](https://arxiv.org/abs/2509.20823), Findings of ACL 2026)

Sources: 11 real datasets, including Walmart weekly sales with CPI and unemployment, UK online retail, CO2 with GDP,
and USDA agricultural productivity.

Captions: about 20k synthetic ones from Gemini 2.0 Flash (given series, precomputed stats and a plot), plus a gold
set of 1,746 LLM drafts rewritten and fact-checked by humans. MCQ: 910 questions in 5 types (series matching,
caption matching, plot matching, comparative, timestamp lookup). Pitfalls reported: hallucinated statistics;
"number-blind" BLEU-style metrics; models ignore the plot; single-oracle bias; a manual check found 98.6% of about
2.9k synthetic captions factually correct.

Release link and license: not found (unverified). Use: the closest public "what happened?" benchmark on retail series.

**ChengsenWang/TSQA** ([HF](https://huggingface.co/datasets/ChengsenWang/TSQA), [ChatTime arXiv 2412.11376](https://arxiv.org/abs/2412.11376))

48k MCQs, 12k each for trend, volatility, seasonality and outliers, 3 classes per feature. KernelSynth series of
length 64-512. Answers are option letters. Apache-2.0. Already in OpenTSLM and TimeNet.

**M4-Caption** (OpenTSLM; TimeNet PR #790)

100k M4 train series, each with a GPT-4o caption. There are no timestamps; series sit on an ordinal axis. The PR
says M4 states no license (`NONE`) and the captions are MIT. The captions can't be checked by code. Good for
caption style on business-like series, but **it may teach the model to invent numbers**; filter it with our checker
(see below).

**TimeSeriesExam-1** ([arXiv 2410.14752](https://arxiv.org/abs/2410.14752), [HF](https://huggingface.co/datasets/AutonLab/TimeSeriesExam1), MIT)

746 MCQ/binary items over 5 categories: pattern, noise, similarity, anomaly, causality. Synthetic series from
templates.
- v1.1 changed the templates to remove "ambiguous or incorrect" items.
- GPT-4o scores 75.2% from images vs 51.7% from text.
- The HF viewer shows minor label and answer string mismatches.

**TSAIA** ([HF Melady/TSAIA](https://huggingface.co/datasets/Melady/TSAIA), [arXiv 2509.01822](https://arxiv.org/abs/2509.01822); linked from the [TS-Reasoner repo](https://github.com/wen-ye-xwz/TS-Reasoner), TMLR 2026)

904 analysis questions and 150 MCQ. Finance (stock price, volatility, trend) and energy. 33 task formulations with
task-specific success criteria. CC-BY-4.0. Relevant if our answers come from code or tool calls.

**Time-MQA TSQA** ([arXiv 2503.01875](https://arxiv.org/abs/2503.01875), [HF](https://huggingface.co/datasets/Time-MQA/TSQA), Apache-2.0, gated)

About 193k items: forecasting 42.6k, imputation 38.7k, anomaly 37k, classification 37k, open QA 37.6k.
- The open QA was written by GPT-4o. The authors manually selected only 1.4k of 37.6k for continued pre-training.
- Finance coverage: NAB ad-exchange (43 anomaly items) and Motley Fool earnings calls.
- The authors note that **models answered even with the numeric data removed** (fabrication).

**ChatTS** ([arXiv 2412.03104](https://arxiv.org/abs/2412.03104), VLDB 2025)

Training data: [HF ChatTSRepo/ChatTS-Training-Dataset](https://huggingface.co/datasets/ChatTSRepo/ChatTS-Training-Dataset),
262k rows. Splits: align_256 105k, align_random 105k, sft 44.8k, ift 6.4k, dev 1k.
- Series come from an attribute-based generator (trend, season, noise, local fluctuations).
- SFT data comes from LLM seed QAs expanded with "TSEvol" (Qwen2.5-32B recommended).
- License conflict: HF metadata says Apache-2.0, the README says MIT.

Evaluation: "Dataset A/B" (real + synthetic) on Zenodo 10.5281/zenodo.14349206, CC-BY-4.0, scored with ragas
(an LLM judge). Use: copy the attribute schema for our generator; the alignment split is optional pre-training.

**CiK** ([HF](https://huggingface.co/datasets/ServiceNow/context-is-key), Apache-2.0)

355 context-aided forecasting tasks. Includes retail, US unemployment and ATM withdrawals. Forecasting, not QA.

**TSRBench** ([arXiv 2601.18744](https://arxiv.org/abs/2601.18744), [HF](https://huggingface.co/datasets/umd-zhou-lab/TSRBench))

4,125 problems, 15 tasks in 4 dimensions (perception, reasoning, prediction, decision), 14 domains including finance.
Answers are labels, numbers or text. How it was built and its license: not stated (unverified).

**ARFBench** ([arXiv 2604.21199](https://arxiv.org/abs/2604.21199), Apache-2.0, in TimeNet)

750 MCQ over 142 real Datadog metrics from 63 incidents. An LLM fit engineers' incident threads to 8 templates. Not
business, but its question templates ("when did the anomaly start/end?") map onto ours.

**Merrill et al.** ([arXiv 2404.11757](https://arxiv.org/abs/2404.11757), [repo](https://github.com/behavioral-data/TSandLanguage), MIT)

LLM-generated scenarios and series-generator code. Tasks: etiological MCQ, QA, counterfactual QA. Models score
barely above random and trail humans by up to 30 points.

**SciTS** ([HF OpenTSLab/SciTS](https://huggingface.co/datasets/OpenTSLab/SciTS), ICLR 2026)

54k instances, 43 tasks, 12 disciplines. Economics = stock forecasting and stock MCQ. CC-BY-NC-SA-4.0, so not
for a contributed or commercial training set.

**Skip**
- **TimerBed** ([arXiv 2411.06018](https://arxiv.org/abs/2411.06018), NAACL 2025): 6 real classification tasks
  (whale calls, lightning, ECG, EMG, computers, HAR) framed as MCQ. No business data; no repo license found.
- **VerbalTS** (ICML 2025, [repo](https://github.com/seqml/VerbalTS), README says MIT): text-to-series generation;
  data is Synth-M/U, Weather, BlindWays, augmented ETTm1/Traffic. Not QA, no business data. How the captions were
  made is not documented on the repo page (unverified).
- **FinTSB** ([arXiv 2502.18834](https://arxiv.org/abs/2502.18834), [repo](https://github.com/TongjiFinLab/FinTSB), GPL-3.0):
  20 datasets of 300 stocks each, 4 movement regimes, forecasting/ranking only. **No text.** At most a source of raw
  series; GPL-3.0 code licence.
- **FinTradeBench** ([arXiv 2603.19225](https://arxiv.org/abs/2603.19225)): 1,400 NASDAQ-100 questions (Core400
  expert-reviewed). Data "available upon publication", so not usable yet.
- **Time-MMD** (our current set): series + LLM-filtered reports in 9 domains, incl. Economy (HF mirrors say
  ODC-BY). Reports are not question-answer pairs and are not series-checkable.

---

## Should we generate our own QA by code from business series? Yes, with guards

**Why.**
- No public set covers our question types on real business series with checkable answers (see above).
- Templated QA from labels is how ECG-QA, OpenTSLM stage 5's base, was built.
- The datasets with the most trustworthy labels in this survey are the computed ones:
  - MTBench trend bins and indicators
  - TSAQA data transformation and temporal relationship
  - ChatTime TSQA
  - TimeSeriesExam
- The same code becomes our verifier. That matches the project's "answers code can verify" goal.

**Papers that generate TS QA synthetically, and what they report:**

| Paper | Method | Reported pitfall |
|---|---|---|
| ChatTS (2412.03104) | Attribute-based synthetic series; LLM "TSEvol" QA expansion | Trains only on synthetic data; real-data transfer must be shown separately (they evaluate on real Dataset A/B) |
| ChatTime TSQA (2412.11376) | KernelSynth series + 4 feature templates | 3-class labels only; no dates or levels |
| TimeSeriesExam (2410.14752) | Template exam over composed synthetic series | v1.1 had to remove ambiguous or incorrect templates; scores change a lot between text and image input |
| Fons et al., J.P. Morgan (2404.16563, ICML 2024) | Taxonomy-driven synthetic series with quantitative descriptions | LLMs are sensitive to number format, the position of the queried point, and series length |
| Merrill et al. (2404.11757) | LLM writes scenario + generator code + MCQ | Near-random model accuracy; label quality depends on the LLM |
| MTBench (2503.16858) | Labels computed from prices (bins, indicators) | Label skew; models collapse to the majority/default class; misaligned pairs |
| TSAQA (2601.23204) | Mix of computed, templated and LLM-vote labels | LLM-voted labels are not verifiable; distractors come from unrelated series (can be easy shortcuts) |
| CaTS-Bench (2509.20823) | LLM captions grounded in precomputed stats + human gold | About 1.4% wrong captions; number-blind metrics; single-oracle bias |
| Time-MQA (2503.01875) | GPT-4o QA, manual filter (1.4k of 37.6k kept) | Models answer with the series removed (fabrication) |
| Evidence-use study (arXiv 2610.05686) | Audits ChatTS, Time-MQA, TimeOmni | Predictions change little when the series is changed; rationales make unsupported numeric claims |
| Coding agents (arXiv 2606.16545) | LLM computes answers with Python | Code access helps by up to 10% but 22-34% still wrong; agents miss statistical subtleties |

**Guards for our generator (from those pitfalls):**
1. **Define every question operationally.** Write the definition down and ship it with the item. "Start of the fall"
   = first point of the longest run of declines whose total drop exceeds X% (or a change-point method with a fixed
   penalty). "Usual range" = 10th-90th percentile of the same calendar month over the prior N years. Accept a
   tolerance (±1 period for dates, ±0.5 pp for percentages). Drop items where the definition is fragile: near-ties,
   flat series, or two candidate peaks within 5%.
2. **Balance answers.** Balance up/down/flat, early/late dates and "normal"/"unusual" per template, or the model
   learns the prior (the MTBench lesson).
3. **Run a blind-baseline test.** Train or run a text-only model with the series shuffled or replaced. If it beats
   chance, the question text leaks the answer (Time-MQA, the evidence-use study).
4. **Run counterfactual pairs.** Perturb the series (flip the trend, move the peak) and regenerate the answer. Score
   the model on whether its answer changes with the series.
5. **Vary the phrasing.** Use several paraphrases per template, optionally LLM-paraphrased questions only. Keep the
   answer slot computed, never LLM-written. Hold out whole templates and whole series for test.
6. **Write free-text answers from computed facts.** Fill a template from the computed facts ("Sales fell 12.3% from
   March to June 2024, the largest 3-month drop in the series"). Verify by parsing the numbers and dates back out.
   Do not score with BLEU (CaTS-Bench).
7. **Put the calendar in the prompt** (start date, frequency, unit). OpenTSLM sees only a normalized series plus
   mean/std, so "last month", "same period last year" and levels are otherwise unanswerable.
8. **Treat component contribution ("which region drove the drop?") as multi-series.** It needs the component series
   plus an additive total. Compute shares of the change (Δcomponent / Δtotal). Exclude cases where components move in
   opposite directions and the shares are ill-defined, or mark them separately.
9. **Keep it real-series-first.** Use synthetic series (ChatTS-style attributes) only to cover rare patterns. Report
   eval on real held-out series (ChatTS's stated motivation; the TimeSeriesExam text/image gap shows synthetic scores
   do not transfer cleanly).

**Mapping to TimeNet task types:**

| Question family | TimeNet task type |
|---|---|
| direction | classification |
| largest change: when | change-point localization |
| largest change: size | scalar prediction |
| latest vs usual range | classification + scalar |
| same period last year | scalar (YoY %) |
| component contribution | classification (which) + scalar (share) |
| summary | captioning / answer |

All of these can be checked from the series. That makes the dataset a clean TimeNet contribution with
`generated-supervision` tags, the same tag TSAQA and SensorCaps use.
