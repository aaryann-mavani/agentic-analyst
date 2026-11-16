# Plan: Agentic Analyst (TimeNet hackathon + Agentic AI lecture project)

Status: draft, 16 Nov 2026. Open points are listed at the end.

## Idea in one sentence

An agentic analyst that turns a client's raw KPI time series into a verified, partner-ready insight memo in hours instead of weeks. The core is a time-series language model (OpenTSLM) that forecasts and explains series using textual context.

## Two deliverables, one codebase

| | TimeNet hackathon, Round 1 | Agentic AI lecture project |
|---|---|---|
| Deadline | Sun 22 Nov, 23:59 PST (Mon 23 Nov, 08:59 CET) | Fri 11 Dec, end of day |
| Team | 4 of us (limit is 2–4) | All 5 |
| What we hand in | Dataset PR to TimeNet, trained model with results, project link, X + LinkedIn posts, Discord post, submission form | 5-minute video with all members presenting, plus the code |
| What is judged | Use case and impact, technical execution, data and TimeNet, results and evaluation, showcase and social engagement | Problem with evidence, KPIs, business case, agentic proof of concept, performance on the KPIs |

The hackathon produces the dataset and the model. The lecture project wraps that model in an agent and adds the business case. The agent is not needed for the hackathon.

## Datasets

| Dataset | Role | What we checked |
|---|---|---|
| Context is Key (`ServiceNow/context-is-key` on Hugging Face) | TimeNet PR and evaluation benchmark | One Parquet file, Apache-2.0 on the dataset card, fits TimeNet's existing Hugging Face base connector. Only 355 instances and no training split, so it cannot be the fine-tuning set. |
| Time-MMD (`AdityaLab/Time-MMD` on GitHub) | Fine-tuning data, second connector if time allows | Plain CSVs: one numerical file and two text files (reports, search results) for each of 10 domain folders, including Economy. The repo has no LICENSE file. The paper states ODC-By 1.0 and says the sources are authorized for non-commercial distribution. |
| UCI Online Retail II or synthetic client data | "Client engagement" in the lecture demo | Not inspected yet. Not needed before 23 Nov. |

Context is Key is the easiest to integrate. Each row has a background text, a scenario text, a past series and a future series, which maps onto a TimeNet `ForecastingTask` with the text as context.

## Phase 1: hackathon (16–22 Nov)

| When | Work | Owner |
|---|---|---|
| Mon | Register the team, request Nebius credits, join the Discord. Ask the organizers two questions: does training on one dataset and evaluating on the onboarded one satisfy the rules, and is Time-MMD's license acceptable for a PR. | A |
| Mon–Tue | Fork TimeNet, run `make sync`, build `timenet/hello-world` to confirm the toolchain works. | B |
| Tue–Wed | Context is Key connector: `dataset.yaml`, `connector.py`, fixture test, local build and round-trip read, `make check` and `make test`. Open the PR. | B, C |
| Tue–Thu | Time-MMD training set: build sliding windows (past values + aligned text, future values as target). Write it as a second connector if the license question is answered positively, otherwise keep it as a local loader. | C, D |
| Wed–Sat | Fine-tune OpenTSLM on Nebius. Start with a small run on Wednesday to prove the training loop, then the full run. | D, A |
| Fri–Sat | Evaluate on Context is Key against three baselines: naive and seasonal naive, pretrained OpenTSLM without fine-tuning, and the model without the text context. | D |
| Sat | Project page or short demo: the problem, the dataset, the results, the limits, who benefits. | A |
| Sun | X and LinkedIn posts with metric screenshots, Discord post, submission form. Aim to submit by Sunday evening CET. | A, all |

Fallback if the fine-tune is not usable by Friday evening: submit the Context is Key PR with the pretrained OpenTSLM evaluation and the baselines, and enter the trained model in a later round.

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
 ├─ Forecaster and explainer: the fine-tuned OpenTSLM from Phase 1
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
| Forecast accuracy | MASE or sMAPE on held-out data against naive baselines |
| Outlier detection quality | Precision and recall on injected anomalies |
| Insight accuracy | Share of claims the verifier confirms |
| Partner acceptance | LLM judge plus a small human rating |

## Open points

1. Who are A–D on the hackathon team, and who is the fifth member? The fifth can start on the business-case evidence this week.
2. Buyer: consulting firm on fixed-fee engagements, or corporate FP&A team. Decide by 25 Nov. Both use the same agent; only the ROI model and the story differ.
3. Organizers' answers to the two questions from Monday (training/evaluation split, Time-MMD license).
4. Compute after the hackathon: the Nebius credits may be used up. The agent only needs inference, so a small GPU or CPU inference may be enough.
5. Agent framework in Python (for example LangGraph or the Claude Agent SDK). Decide in the week of 23 Nov.
