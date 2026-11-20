# Business case: Agentic Analyst

Draft, 2026-11-20. Written as if we were the company. **Sourced** facts link to `docs/research/business-case-evidence.md`. Everything marked **(assumption)** is a hypothesis to test in practitioner interviews, not a finding.

## 1. The business in one paragraph

We sell a small AI model that runs on a consulting firm's own server. A consulting **Partner** types a plain-language question about a client's KPI numbers ("did sales really drop in Q3, or is that normal for the season?") and gets an answer in seconds. Code recomputes every number in the answer, and the Partner sees the calculation path and a chart. Today the same question goes to an analyst and takes days (team claim, unverified). Our **Buyer** is a mid-size or boutique consulting firm: it has the client-confidentiality problem but cannot build its own platform.

## 2. The problem, with evidence

| Pain | Evidence | Strength |
|---|---|---|
| Public AI tools can't be used on client data | 27% of organisations banned GenAI at least temporarily over privacy and security (Cisco 2024, n = 2,600); 55% avoid some GenAI uses over data concerns (Deloitte 2024, n = 2,770) | Strong |
| Big firms solved this with their own platforms; mid-size firms can't | McKinsey built Lilli; PwC and Bain bought enterprise contracts | Medium |
| AI gets numbers wrong, and people trust it anyway | BCG/Harvard experiment (758 consultants): on a data analysis task, AI-assisted consultants were 19 points less likely to be correct | Strong |
| Clients distrust AI-written reports | 70% of 3,887 companies said they wouldn't trust a consultant report produced with AI (secondary source) | Weak |
| Analysts spend much of their time on data work | Data preparation takes about 38% of data practitioners' time (Anaconda 2022); no consulting-specific study found | Medium |
| Partners wait days for data answers | Team claim | **Unverified. Needs interviews** |

## 3. The product, and why the design earns trust

1. The Partner asks a question about a KPI series.
2. **Spotting:** the time-series model decides what is worth saying (ADR 0001).
3. **Computing:** code calculates every figure and records the calculation path.
4. **Check:** code recomputes every claim before the Partner sees it. Failed claims are corrected or flagged.
5. The Partner sees the answer, the calculation path and the evidence (figures and chart).
6. Questions beyond the data ("why, really?") get "the data can't tell, ask your analyst to check X".

What it answers: what happened and when, whether a move is normal for the season, which component drove it (levels 1–2), and what moved with it (level 3, never "caused by").

**Competitors** (Power BI Copilot, Tableau Pulse, ThoughtSpot, Julius) are cloud services that need a prepared data model. Our wedge: runs on-site, works on the raw KPI file a client sends, and checks every number.

## 4. Worked example: one Partner, one question

We can't use real client data, so this runs on **public US trade data** (Time-MMD Economy, 447 months, Jan 1987 to Mar 2024) standing in for a client's monthly Exports and Imports. All numbers below come from the working prototype in `prototypes/kpi-qa-PROTOTYPE/`.

**Scenario:** a Partner is preparing a client meeting about March 2024 and asks four questions.

| Partner asks | The system answers (checked) | Calculation path shown |
|---|---|---|
| "What happened in March?" | The deficit widened by $4.4B to $79.8B | 79,818.8 − 75,439.9 = +4,378.9 |
| "What drove it?" | Imports rose $16.5B, exports $12.2B; imports were the larger mover | Imports 259,144.7 − 242,611.4; Exports 179,325.9 − 167,171.5 |
| "What moved with it?" | Exports and imports changes coincided strongly over 36 months (correlation +0.77); coincided, not caused | Pearson r on monthly changes |
| "Why, really?" | **The data can't tell.** Check the dollar index, tariffs and one-off shipments with the analyst | No calculation |

**Where the Check earns its keep.** In the prototype a model draft said "widened by $5.0B, the third month in a row". The data says $4.4B and the first month. The Check flagged both, and confirmed the three correct claims. A Partner couldn't have caught these without redoing the analysis, and repeating a wrong figure to a client costs credibility.

**Time comparison for this one question:**

| | Today | With the product |
|---|---|---|
| Who does the work | An analyst: find the data, compute, chart, write up | The system, then an analyst spot-reviews |
| Effort | About 4 analyst hours **(assumption)** | Seconds, plus about 0.5 analyst hours of review **(assumption)** |
| Waiting time for the Partner | Days **(team claim, unverified)** | Seconds |

**Limits shown by the prototype, to say openly:**
- The seasonal verdict is weak. April 2020 (the start of COVID) comes out "in line with the usual April move", because the rule compares raw changes in a trending series. It needs a better rule before it goes in a demo.
- The Check works on claims we listed by hand. Extracting claims from free model text is not built yet.
- The model is a stub. Nothing here shows that OpenTSLM can do the spotting.

## 5. Value to the Buyer

Mid-size firm, 100–200 consultants **(assumption)**. Full table in `business-case-evidence.md` §7.

| | Conservative | **Base** | Optimistic |
|---|---|---|---|
| Analyst hours saved per year | 300 | **2,800** | 24,150 |
| Share of question-hours saved (X) | 25% | **44%** | 67% |
| Saved per year (Y) | CHF 30k | **CHF 420k** | CHF 4.8m |

Base inputs, all **assumptions**: 80 engagements a year × 20 Partner questions × 4 analyst hours, half answered by the product with 0.5 hours of review, at CHF 150 per hour. That is about 35 analyst hours saved per engagement.

Not counted: faster answers in client meetings, freed analyst hours redeployed to billable work, fewer wrong numbers reaching clients.

## 6. What we'd charge, and whether it pays back

Price is a **hypothesis**. A first guess: an annual licence of about CHF 60k per firm, plus one-off hardware of CHF 10–30k **(assumptions)**.

| | Conservative | Base |
|---|---|---|
| Firm's saving per year | CHF 30k | CHF 420k |
| Firm's first-year cost (CHF 60k licence + CHF 20k hardware) | CHF 80k | CHF 80k |
| Net in year one | **−CHF 50k** | **+CHF 340k** |
| Payback | Not in year one | About 2.3 months |

What this tells us:
- At CHF 60k the product pays for itself only if it saves roughly **400+ analyst hours a year** (60k ÷ CHF 150 per hour). That's between our conservative and base cases, so the price is justified only if the firm's real volume is at or above the base case.
- The business works for firms with many engagements and loses money for the smallest ones. Interviews should find out where real firms sit.
- A lower price, or a per-engagement fee, would protect the small end.

**Our side (assumptions):** support and integration for each customer, GPU hardware that the customer owns, and updates. Not costed yet.

**Market:** the number of Swiss and European mid-size firms is **not counted yet**. Illustration only: 100 firms × CHF 60k = CHF 6m a year. The evidence file's rough sanity check puts the Swiss tooling pool at CHF 10–40m **(assumption)**.

## 7. What we'd measure (KPIs)

| KPI | How | Status |
|---|---|---|
| Claims that survive the Check | Code-computed answers against model output, same code for every system | To build (issues #5, #6) |
| Invented-number rate | Numbers not in or derivable from the data | To build |
| Accuracy against Claude, Llama-1B on the same series as text, template baseline | Same test questions, same scoring | To run |
| Does it decline when the data can't tell? | Unanswerable questions mixed in | To build |
| Time to insight | Analyst vs product, same questions | Lecture: a small test with classmates |
| Analyst hours saved per question | Interviews, then measured | Lecture |
| Cost per answer and speed | Reports per hour on the GPU. **Unmeasured**; the research found cheap APIs cost about the same | To measure |

## 8. Risks, and what would change the plan

1. **The model may not beat a text-only model at spotting.** Then ADR 0001 has no reason to use OpenTSLM. The Llama-1B-as-text baseline tests this.
2. **Our biggest numbers are unsourced:** questions per engagement and hours per question. If interviews give half of our base case, the base case is about CHF 210k a year and the price needs rethinking.
3. **Large firms already have in-house tools,** so the market is mid-size firms only.
4. **Cost against API models is not an argument.** Cheap APIs cost cents per question. Lead with confidentiality and trust.
5. **Real client data differs from public data.** Training on Time-MMD says nothing yet about a firm's own KPI files. Holding out whole domains in the test tells us part of it.
6. **We have no real user yet.** Evidence will come from 3–5 practitioner interviews.

## 9. Next steps

1. 3–5 practitioner interviews: questions per engagement, hours per question, days of turnaround, any client ban on AI use. (Issue #9.)
2. Replace the assumed inputs in §5 with what they say, and re-run the price test in §6.
3. Fix the seasonal rule, then run the demo on Census retail data, which is closer to client sales.
4. Add the measured accuracy and invented-number rate from the evaluation to §7 before the Sunday submission.
