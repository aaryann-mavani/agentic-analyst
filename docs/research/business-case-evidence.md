# Business case evidence: analyst time, rates, confidentiality, accuracy, market, competitors

Research date: 2026-11-19. Purpose: evidence for a bottom-up "reduce analyst time by X and save Y" case.

Source strength key: **[S]** strong (peer-reviewed paper, primary survey with stated method, official press release or price list); **[M]** medium (reputable press, or an industry body quoted secondhand); **[W]** weak (vendor blog, aggregator, unverified secondary claim). Use [W] figures only as ranges, never as headline claims.

---

## 1. How analysts spend their time; turnaround

No rigorous study isolates *management consultants'* time on data work. The best evidence comes from studies of data professionals in general plus a few consulting-specific claims.

| Figure | Source | Strength |
|---|---|---|
| Data prep and cleansing take about 38% of data practitioners' time (2022). In 2020, loading plus cleansing took 45%. | [Anaconda State of Data Science 2022](https://know.anaconda.com/rs/387-XNW-688/images/ANA_2022SODSReport.pdf), [2020 report](https://know.anaconda.com/rs/387-XNW-688/images/Anaconda-SODS-Report-2020-Final.pdf) | M (vendor survey, large sample) |
| Data scientists spend about 40% of their time gathering and cleaning data and about 11% finding and communicating insights (Kaggle, 23k respondents). | [Business Over Broadway](https://businessoverbroadway.com/?p=9445) | M/W (secondary summary) |
| 60% of IT staff and analysts spend at least half their time on data quality and preparation. | [Trifacta survey via Solutions Review](https://solutionsreview.com/data-integration/data-preparation-is-the-most-wasteful-part-of-the-data-analytics-process) | W (vendor-commissioned) |
| One third of BI professionals spend 50-90% of their time cleaning raw data. | [eWeek (Xplenty survey, n>200, 2015)](https://www.eweek.com/database/one-third-of-bi-pros-spend-up-to-90-of-time-cleaning-data/) | W (old, vendor) |
| On data-heavy consulting projects, about 1/3 of the time goes to collection, 1/3 to cleaning and validation and 1/3 to analysis. | [Thinkinsights](https://thinkinsights.net/insights/clients-have-data-problems) | W (practitioner blog) |
| BCG/HBS field experiment with 758 BCG consultants using GPT-4: on tasks *inside* the frontier, 12.2% more tasks completed, 25.1% faster and more than 40% higher quality. On a task *outside* the frontier (data and interview analysis), consultants were 19 percentage points *less* likely to be correct. | [Dell'Acqua et al. 2023, SSRN 4573321](https://mitsloan.mit.edu/sites/default/files/2023-10/SSRN-id4573321.pdf) | S |
| McKinsey Lilli: used by more than 70% of about 45k staff, about 17 times a week per user. Engagement teams save 4-6 hours a week on research and presentations. The often-quoted "30% time saved on information gathering" figure also circulates. | [Business Insider (NL)](https://www.businessinsider.nl/inside-the-ai-boom-thats-transforming-how-consultants-work-at-mckinsey-bcg-and-deloitte), [McKinsey people-function page](https://www.mckinsey.com/featured-insights/people-in-progress/ai-in-the-people-function), [Entrepreneur](https://www.entrepreneur.com/business-news/mckinsey-consultants-are-letting-ai-take-over-their-work) | M (firm self-report) |
| Professionals expect GenAI to save 4 h/week within a year (2024 survey) and 5 h/week (2025 survey), about 200-240 h/year. | [Thomson Reuters Future of Professionals 2024](https://www.thomsonreuters.com/en-us/posts/technology/future-of-professionals-2024), [CPA Practice Advisor](https://www.cpapracticeadvisor.com/2024/07/09/ai-can-save-professionals-12-hours-per-week-according-to-thomson-reuters-report/107760/) | M (self-reported expectations; legal, tax and risk professionals, not consultants) |

**Gaps:**
- I found no published figure for how long partner data requests take to turn around. The team's "days" claim, and its "3 weeks to 3 months of consolidation per engagement" claim, remain **unverified**. Validate them with 3-5 practitioner interviews; that is the cheapest strong evidence available.
- The BCG result matters for us: general-purpose LLMs *hurt* accuracy on quantitative analysis tasks. This supports the "every number checked by code" design.

## 2. Billing rates, costs, engagement size

| Figure | Source | Strength |
|---|---|---|
| McKinsey from public contracts: senior partner about $1,100-1,200/h, engagement manager about $800/h, analyst or associate $300-500/h. | [Slidescience](https://slidescience.co/?p=7147) | W (blog; original contracts not checked) |
| GSA terminated McKinsey's federal schedule in 2020 because its prices were "higher, sometimes substantially so" than comparable firms. | [Consulting.us](https://www.consulting.us/news/4278/gsa-stops-mckinseys-contract-claims-fees-were-too-high) | M |
| Guidehouse GSA price list (a Big Four spin-off): Partner/MD about $414/h, Business Analyst about $152/h (government-discounted). | [Guidehouse GSA price list 2023](https://guidehouse.com/-/media/new-library/corporate/government-contract-vehicles/contract-documents/2023/0yb6c63u1j6u47qraa19d008547qraa19d0085modpa0024revised05092023rev.ashx) | S (official price list, but discounted government rates) |
| US management-consulting benchmark price: $297/h (2026). | [IBISWorld](https://www.ibisworld.com/united-states/procurement/management-consulting-services/53923535/) | M |
| Median consulting fee $190/h globally, $290/h in North America. | [Consulting Success fees survey](https://www.consultingsuccess.com/consulting-industry-trends) | W/M (mostly independents) |
| Europe: £50/h (interim) to more than £300/h (strategy firm). Senior BCG staff billed more than £6,000/day on the UK Test and Trace programme. | [Consultancy.org fees & rates](https://www.consultancy.org/consulting-industry/fees-rates) | M (indicative) |
| Germany (Lünendonk): a senior consultant costs on average €1,300/day for some clients and €3,820/day for others. | [Consultancy.eu fees news](https://www.consultancy.eu/news/consulting/fees-rates) | M (dated) |
| Freelance strategy consultants: median €1,200/day. | [Fratch](https://fratch.io/en/role/strategy-consultant/switzerland) | W |
| Switzerland: specialist consultants CHF 160-300+/h. Swiss firms usually bill day rates (Tagessätze). | [MagicHeidi](https://magicheidi.ch/en/hourly-rates), [consultant.dev](https://consultant.dev/blog/it-consultant-switzerland-2026) | W |
| Swiss mid-career management consultant base salary about CHF 109k. | [Payscale CH](https://www.payscale.com/research/CH/Job=Management_Consultant/Salary/84827dbc/Mid-Career-Zurich-Consulting-Management) | W/M |
| A mid-tier 8-week strategy engagement costs about $150k-400k. Typical strategy projects run 4-12 weeks. | [Slideworks](https://slideworks.io/resources/management-consulting-fees-how-mc-kinsey-prices-projects), [ConsultingDemand](https://consultingdemandastro.pages.dev/blog/consulting-fees-by-industry) | W |
| MBB firms tie about 25% of fees to outcomes (WSJ via AI Weekly). | [AI Weekly](https://aiweekly.co/node/4358) | W/M |

**Working rates for the model (assumption, built from the ranges above):**
- Analyst/associate, fully loaded *cost* to a Swiss mid-size firm: about CHF 100-150/h. Derivation: about CHF 100-130k salary × 1.3 overhead ÷ about 1,700 h/year ≈ CHF 75-100/h, raised for non-billable overhead.
- Analyst *billing* rate: about CHF 150-250/h.
- Partner billing rate: about CHF 400-700/h.

## 3. Confidentiality and GenAI policies

| Evidence | Source | Strength |
|---|---|---|
| 27% of organisations had banned GenAI at least temporarily over privacy and security risk. 48% of employees admitted entering non-public company information into GenAI tools. (n = 2,600 privacy and security professionals) | [Cisco 2024 Data Privacy Benchmark](https://investor.cisco.com/news/news-details/2024/More-than-1-in-4-Organizations-Banned-Use-of-GenAI-Over-Privacy-and-Data-Security-Risks---New-Cisco-Study/default.aspx) | S |
| 55% of organisations avoid specific GenAI use cases because of data concerns (quality, privacy, security). Only 23% feel highly prepared for AI risk. (n = 2,770) | [Deloitte State of GenAI in the Enterprise, Q3 2024](https://www.deloitte.com/southeast-asia/en/about/press-room/data-and-risk-remain-key-challenges-to-scaling-generative-ai.html) | S |
| UK consulting clients: 40% say data security and privacy concerns hold back AI progress (MCA survey). | [Consultancy.uk](https://www.consultancy.uk/news/44009/uk-consulting-clients-turning-to-sector-for-ai-transformation-support) | M |
| 70% of 3,887 companies surveyed said they would not trust a consultant report produced with AI. | [ResultSense, citing Source Global Research](https://www.resultsense.com/news/2026-08-04-consultancy-clients-distrust-ai-reports/) | W (secondary; primary not found). It does support the "show the calculation path" claim. |
| Samsung banned ChatGPT, Bard and Bing AI on company devices after engineers pasted source code into ChatGPT. JPMorgan and Goldman restricted ChatGPT; Amazon warned staff. | [NBC News](https://www.nbcnews.com/tech/tech-news/samsung-bans-use-chatgpt-employees-misuse-chatbot-rcna82407), [CSO Online](https://www.csoonline.com/article/3695170/samsung-bans-staff-ai-use-over-data-leak-concerns.html) | M |
| Consulting firms build walled-garden tools instead of using public chatbots: McKinsey **Lilli** (internal, built for confidential data), Bain **Sage** (built on OpenAI) plus ChatGPT Enterprise for 13k staff, PwC ChatGPT Enterprise for more than 100k US/UK staff, EY.ai ($1.4bn investment), KPMG Clara and Copilot. | [Entrepreneur](https://www.entrepreneur.com/business-news/ai-creates-powerpoints-at-mckinsey-replacing-junior-workers/492624), [Bain press release](https://www.bain.com/about/media-center/press-releases/2023/bain--company-makes-pioneering-deployments-of-state-of-the-art-ai-tools-worldwide/), [TechCrunch](https://techcrunch.com/2024/05/29/openai-signs-on-100k-pwc-workers-to-its-chatgpt-enterprise-tier-as-the-consultant-becomes-its-first-resale-partner) | M |
| Some firms use "private, air-gapped LLM instances" for client documents. | [NetSuite](https://www.netsuite.com/portal/resource/articles/business-strategy/ai-in-consulting.shtml) | W |

**Reading:**
- The evidence that confidentiality *restricts* GenAI use is strong (Cisco, Deloitte).
- The big firms' answer has been enterprise cloud contracts or their own platforms, which cost $100m+. Mid-size firms cannot build a Lilli. That is the gap an on-prem product fills.
- I found no public document saying a client *contractually forbade* a consultant from using AI on its data. This is plausible (NDAs, FINMA outsourcing rules, banking secrecy) but unverified. Ask practitioners about it.

## 4. LLM numeric errors on financial and data analysis

| Finding | Source | Strength |
|---|---|---|
| FinanceBench: GPT-4-Turbo with retrieval answered wrongly or refused **81%** of 150 questions on public-company filings. With long context it failed 21%. | [Islam et al. 2023, arXiv 2311.11944](https://arxiv.org/abs/2311.11944v1), [Patronus release](https://prnewswire.com/news-releases/patronus-ai-launches-industry-first-llm-benchmark-for-finance-to-address-hallucinations-301990858.html) | S (models now dated) |
| DocMath-Eval (ACL 2024, 48 LLMs, numeric reasoning over financial tables): the best models lag human experts (76%) by a large margin. | [arXiv 2311.09805](https://arxiv.org/html/2311.09805v3), [ACL 2024](https://aclanthology.org/2024.acl-long.852.pdf) | S |
| FinanceMath: the best system (GPT-4o, chain-of-thought prompting) reaches 60.9% accuracy. | [arXiv 2311.09797](https://arxiv.org/html/2311.09797v2) | S |
| MTBench (financial and weather time series): models struggle with "precise mathematical operations on time series data". | [arXiv 2503.16858](https://alphaxiv.org/overview/2503.16858v1) | S/M |
| TSAIA: GPT-4o is prone to execution and constraint errors on multi-series and covariate tasks. | [arXiv 2509.01822](https://api.emergentmind.com/papers/2509.01822) | M |
| BCG field experiment: on quantitative analysis, AI-assisted consultants were 19 pp less likely to be correct (see §1). | [SSRN 4573321](https://mitsloan.mit.edu/sites/default/files/2023-10/SSRN-id4573321.pdf) | S |

**Reading:**
- The evidence is consistent: free-text LLM arithmetic over tables and series is unreliable.
- Frontier models have improved since 2023, so do not cite the 81% figure as current.
- The robust message is that even the best models make material numeric errors, and that people trust them anyway (BCG). Code-checked claims with a calculation path address both problems.

## 5. Market size

| Figure | Source | Strength |
|---|---|---|
| Global consulting market about $275bn in 2025 (+6%). | [Source Global Research](https://www.sourceglobalresearch.com/?p=131220) | M/S (headline only seen) |
| US consulting market about $110bn. | [Bloomberg Law on Source data](https://news.bloomberglaw.com/daily-tax-report/consulting-growth-to-double-after-sluggish-2024-research-finds) | M |
| Global tech consulting market above $400bn in 2026 (different scope). | [Consultancy.uk](https://www.consultancy.uk/news/42532/global-technology-consulting-market-to-surpass-400-billion-in-2026) | M |
| Swiss management consulting fee revenue about CHF 2bn (2017, ASCO). | [Consultancy.eu](https://www.consultancy.eu/news/1830/switzerlands-growing-consulting-industry-approaches-2-billion-mark) | M (dated) |
| Swiss consulting and audit, ASCO/EXPERTsuisse members: about CHF 3.8bn turnover (2021). | [Forvis Mazars market study](https://www.forvismazars.com/ch/en/insights/publications/surveys/asco-and-expertsuisse-market-study-2021) | S |
| Swiss management consulting services about USD 3.6bn (2025). | [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/switzerland-management-consulting-services-market) | W |
| Worldwide GenAI spending $644bn in 2025, of which software is about $37bn and services about $28bn (about 80% is hardware). | [Gartner press release, 31 Mar 2025](https://www.gartner.com/en/newsroom/press-releases/2025-03-31-gartner-forecasts-worldwide-genai-spending-to-reach-644-billion-in-2025) | S |

**Gap:** I found no credible figure for "analytics and AI tool spend in professional services" specifically.

**Proxy for sizing (assumption):** if a firm spends 0.5-1% of revenue on analytics tooling, the Swiss consulting market (about CHF 2-4bn) implies a CHF 10-40m serviceable tooling pool. Treat this as a sanity check, not a sourced figure.

## 6. Comparable products and prices

| Product | What it does | List price | Source | Gap vs. ours |
|---|---|---|---|---|
| Power BI Copilot | Natural-language Q&A and report summaries over a Power BI model | Pro $14/user/mo; PPU $24/user/mo; Copilot needs Fabric capacity, F64 about $5.0k/mo reserved or about $8.4k/mo pay-as-you-go | [Azure Fabric pricing](https://azure.microsoft.com/en-us/pricing/details/microsoft-fabric/?country=us), [AlphaBold](https://www.alphabold.com/microsoft-fabric-pricing-and-licensing/) | Cloud (Azure); needs a modelled dataset; numbers come from DAX, but the narrative is LLM text without per-claim checks |
| Tableau Pulse / Tableau+ | Automated KPI digests and "what changed" insights | Creator $75, Explorer $42, Viewer $15/user/mo (Standard); Enterprise $115/$70/$35; Tableau+ via sales | [Tableau pricing](https://www.tableau.com/pricing/cloud) | Cloud (Salesforce Einstein trust layer); needs a curated metric layer; closest functional competitor for "what happened" |
| ThoughtSpot (Spotter) | Search and agentic NL analytics over a warehouse | Essentials about $25, Pro about $50/user/mo; Spotter capped at 25 queries/user/mo on Pro; enterprise about $137k/yr average | [Toucan Toco](https://www.toucantoco.com/en/blog/thoughtspot-pricing), [Upsolve](https://upsolve.ai/blog/thoughtspot-pricing-2025) | Cloud SaaS; needs a warehouse and semantic model; generates SQL (verifiable) but no time-series reasoning layer |
| Julius AI | Chat-with-your-spreadsheet; writes Python | Free; Plus $20, Pro $45/mo; Business $450/mo for 10 seats | [Julius pricing](https://julius.ai/pricing), [Toolradar](https://toolradar.com/tools/julius-ai/pricing) | Public cloud with uploads, which is exactly what confidentiality policies block |
| ChatGPT Enterprise / Copilot M365 | General assistants; code interpreter for data | Per seat, via sales | [TechCrunch](https://techcrunch.com/2024/05/29/openai-signs-on-100k-pwc-workers-to-its-chatgpt-enterprise-tier-as-the-consultant-becomes-its-first-resale-partner) | Contractual (not physical) data isolation; no systematic check of numbers |

**Our differentiation (claims to substantiate in the demo):**
1. On-prem. Data physically never leaves the firm, which fits FINMA and banking-secrecy clients and NDAs.
2. Works on raw client KPI files without a BI semantic layer or warehouse project. Consultants get a new client dataset every engagement and cannot build a Tableau or Power BI model each time. This is probably our strongest wedge.
3. Every claim is code-checked and comes with a calculation path, which answers the BCG and FinanceBench failure modes.
4. A small (~1B) model runs on a single workstation GPU.

**Caution on value claim (4), cost vs. frontier APIs:** per-question API costs are cents. Cost is a weak argument unless it means "no enterprise contract or capacity SKU needed". Lead with confidentiality and trust.

---

## 7. Bottom-up estimate: analyst time saved for a mid-size firm

**Scope:**
- Partner ad-hoc KPI questions ("what happened", "is this normal", "which region drove it"), plus first-draft KPI commentary.
- Excludes the upfront data consolidation phase (the team's 3 weeks to 3 months claim). That is upside, but the product does not do ETL.

**Firm profile (assumption):** Swiss or European mid-size consultancy, about 100-200 consultants.

| Parameter | Conservative | Base | Optimistic | Basis |
|---|---|---|---|---|
| Engagements per year with client KPI data | 40 | 80 | 150 | **Assumption.** A 4-12 week engagement length ([W](https://consultingdemandastro.pages.dev/blog/consulting-fees-by-industry)) implies 4-8 engagements per team per year; × 10-20 teams |
| Partner/manager data questions per engagement | 10 | 20 | 40 | **Assumption.** About 2 per week over an 8-10 week engagement; validate in interviews |
| Analyst hours per question (find data, clean, compute, chart, write up) | 3 | 4 | 6 | **Assumption.** Consistent with data prep taking 38-50% of data work ([Anaconda](https://know.anaconda.com/rs/387-XNW-688/images/ANA_2022SODSReport.pdf)) |
| Share of questions the system answers acceptably (verified, in scope at Explanation levels 1-3) | 30% | 50% | 70% | **Assumption.** Bounded by the BCG "jagged frontier" ([S](https://mitsloan.mit.edu/sites/default/files/2023-10/SSRN-id4573321.pdf)) and Lilli's ~30% research-time saving ([M](https://www.entrepreneur.com/business-news/mckinsey-consultants-are-letting-ai-take-over-their-work)) |
| Residual analyst review time per automated question | 0.5 h | 0.5 h | 0.25 h | **Assumption** |
| Value per analyst hour (CHF) | 100 (cost) | 150 (loaded cost/low bill) | 200 (billing) | Derived from §2 ranges |
| **Questions per year** | 400 | 1,600 | 6,000 | = engagements × questions |
| **Analyst hours on questions today** | 1,200 | 6,400 | 36,000 | = questions × hours |
| **Hours saved per year** | 300 | 2,800 | 24,150 | = questions × share × (hours − review) |
| **Share of question-hours saved (X)** | 25% | 44% | 67% | = saved ÷ today |
| **FTE equivalent** (1,700 h/FTE) | 0.2 | 1.6 | 14.2 | |
| **CHF saved per year (Y)** | CHF 30k | **CHF 420k** | CHF 4.8m | = hours × rate |
| **USD saved per year** (1 CHF ≈ 1.20 USD, assumption) | $36k | **$504k** | $5.8m | |

Arithmetic: conservative 400 × 0.30 × (3 − 0.5) = 300 h × CHF 100; base 1,600 × 0.50 × 3.5 = 2,800 h × CHF 150; optimistic 6,000 × 0.70 × 5.75 = 24,150 h × CHF 200. Base case per engagement: 35 analyst hours saved (about one analyst-week).

**Not monetised:**
- Turnaround: answers in seconds instead of the days the team claims, so partners can ask questions live in client meetings.
- Freed analyst hours redeployed to billable work: revenue upside, not cost saving.
- Lower error risk.
- Cost side: hardware is one workstation or server (about CHF 10-30k, assumption) plus integration and support.

**Sensitivity:**
- The result is roughly linear in each factor.
- The biggest unknowns are questions per engagement and hours per question. Both are unsourced and should be measured in 3-5 practitioner interviews (ask about the last engagement: how many data requests, and how long each took).
- The automatable share is the main product risk.

## 8. Evidence gaps to close before pitching

1. Practitioner interviews covering:
   - questions per engagement
   - hours per question
   - turnaround in days
   - whether clients have forbidden AI use contractually.
2. The primary Source Global Research report behind the 70% "would not trust AI report" figure.
3. A Big Four or Swiss mid-size rate card. Public procurement (e.g. simap.ch award notices) may list day rates.
4. Current-model numeric accuracy on a time-series QA benchmark (our own eval can provide this).
