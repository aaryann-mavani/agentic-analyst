# Time-MMD: what the data says (insights for the Q&A demo and the evaluation)

Source: Time-MMD (github.com/AdityaLab/Time-MMD) pinned at `00281e2d86058286d5548b15a7670e8eda57ef62`. Only CSVs were read (pandas/numpy, `python3 -I`); the clone and scripts were deleted afterwards.
Builds on `time-mmd-structure.md` (not repeated). Usable domains: Economy, Traffic, Health_US, Environment, SocialGood, Energy, Agriculture, Climate.
Every number below was computed from the CSVs. "(uncertain)" marks inference or weak evidence. Dates are the row's start date. pp = percentage points. All sub-period splits use the series' own dates.

## How the data works (plain language)

- **A row** is one time period of one KPI. Monthly domains: one row per month (the date is the 1st). Weekly domains: one row per week, starting Monday (Climate: Tuesday). Environment: one row per day.
- **OT** ("Oil Temperature" in the ETT benchmark this format was copied from) is simply the *target KPI* column, the number the question is about. Other numeric columns are covariates (related series or components).
- **Text** comes in two files per domain. `report` = an official release summarised by an LLM (Census trade release, EIA weekly gasoline, FHWA traffic, BLS jobs...). `search` = web-search summaries. Each text row has a `start_date`/`end_date` window, and a `fact` sentence. Text and series are paired by overlapping dates. (How the Time-MMD loader does this internally was not read; uncertain.)
- **Frequency:** Economy, Traffic, SocialGood, Agriculture monthly; Health_US, Energy, Climate weekly; Environment daily (15,979 rows, 1980-2023).
- **Train/test split** is by time: earlier rows train, the last rows test. Illustration with an 80/10/10 split (the real Time-MMD ratio may differ; uncertain): Energy trains up to 2018-02-05 and tests from 2021-03-22 to 2024-04-29, a period that contains the 2022 price record.

Worked example (Energy, weekly; text and series from the CSVs):

| series row (`date`, `end_date`) | OT = US avg gasoline $/gal (all grades) |
|---|---|
| 2011-07-25 .. 2011-07-31 | 3.754 |
| 2011-08-01 .. 2011-08-07 | 3.766 |
| 2011-08-08 .. 2011-08-14 | 3.730 |

Report row, window 2011-08-01 .. 2011-08-05 (Mon-Fri): "The national average retail regular gasoline price decreased to $3.674 per gallon on **August 8, 2011**, $0.037 per gallon less than last week but $0.891 above a year ago."

How they pair: the text row overlaps the series row dated 2011-08-01 (value 3.766). But the sentence describes the price on the *next* Monday: its weekly change (-$0.037) matches the series' 08-01 -> 08-08 move (3.766 -> 3.730 = -$0.036) and its year-ago gap ($0.891) matches the series ($0.895). In 349 of 351 parsed Energy rows the date in the text is exactly 7 days after the window start. Consequence: text attached to week t already contains week t+1's value. The level differs because the text is "regular" gasoline while OT is "all grades" (series is on average $0.089 higher).

## Findings table

| Domain | 3 headline facts (value, date, size) | Seasonality verdict | Level-1 (drivers) verdict | Level-3 (co-movement) verdict | Quality caveats |
|---|---|---|---|---|---|
| Economy (monthly, USD m) | (1) Record deficit -116,662 on 2022-03 (prior record -88,776 on 2018-10); the 2022-03 MoM move of -32,998 is the largest one-month widening of the deficit. (2) 2009: avg monthly deficit fell from -68,017 (2008) to -41,965 (2009); imports -46.2% peak (2008-07) to trough (2009-02) vs exports -33.1% (2008-06 to 2009-01). (3) 2020-04: exports -28.9% MoM, imports -14.6%, yet deficit widened only $10.3bn (-60.6bn to -70.9bn). | Strong in exports/imports (detrended month R2 0.72/0.67); weak for the balance itself: its "usual move" is within noise in 61% of months. Series is not seasonally adjusted. | Exact (Exports - Imports), but one component is the clear main driver (>70% of gross movement) in only 49% of months (Imports 34%, Exports 16%). | None beyond components. | Rows unsorted. Report text describes a different measure than OT (see Q6). |
| Traffic (monthly, million veh-miles) | (1) 2020-04 YoY -40.0% (167,617 vs 279,148): lowest month since 1994-02. (2) Record month 294,328 on 2019-07; 2023-07 289,796 is -1.5% below. (3) Annual total -10.5% in 2020, +8.1% in 2021; 2023 total 3,263,356 is 0.6% above 2019 (3,242,931). | Strongest in the set: detrended month R2 0.95; Jul +7.7% vs Feb -14.4% vs trend; effect/noise = 4.7. | Not available (OT only). | Not available. | Month length drives part of the pattern (Mar +16.9% MoM). Leap Feb 2020 inflates its YoY (+8.3%). |
| Health_US (weekly, % ILI) | (1) Record 7.80% on 2018-01-29 (2009-10-12 had 7.62%, an autumn H1N1 peak). (2) 2020-03-16 7.35% -> 1.35% on 2020-05-04 (-82%); winter 2020/21 peak only 1.50% (2020-11-23). (3) 2022-11-14 7.37%, +1.64pp in one week, the earliest >= 7% peak apart from H1N1 2009 (z = +15 vs usual week). | Strong: peak in Dec-Mar in 19 of 21 seasons (2000-2019); Jan/Feb mean ~3.1% vs Jul 0.66%; week-of-year R2 0.51 (0.41 incl. 2020+). | Exact two-level: OT = ILI visits / patients; ILI visits = sum of age groups. ILI visits main in 70% of big weeks; no single age group dominates (6%). | % WEIGHTED ILI is a near-duplicate (0.97-0.99). Provider and patient counts: spurious. | Summer zeros 1998-2002 (0/0), age schema change 2009, provider counts grow 14x, report text ends 2019-12. |
| Environment (daily AQI, NYC) | (1) Mean AQI 117 (1980) -> 52.7 (2020); days with AQI >= 151: 83 (1980), 0 (2020). (2) Level break after 1991 (mean 104.2 before, 69.8 after). (3) 2023-06-07 AQI 254, highest since 1988-07-11 (261); June 2023 monthly mean 87.5 vs 61-82 in 2015-2022. | Strong at monthly aggregation: Jul +40.7% vs trend, Jun +30%, Oct -23.5%; month R2 0.76. | None. | "Defining Parameter" shifts CO/NO2 (1980s) -> PM2.5 (2000s+). | One metro; Category is derived from OT (leakage); report text only 2021-05..2023-10. |
| SocialGood (monthly, unemployment %) | (1) 2020-04 14.4% (from 4.5% in 2020-03, +9.9pp, largest one-month jump). (2) Record low 2.4% (1952-10); 2023-04 3.1% is lowest since 1969-05 (2.9%). (3) 2010-01 10.6%, the post-2008 peak on this series (above the ~10.0% usually quoted for the adjusted rate; consistent with NSA, uncertain). | Strong: Jan +0.83pp avg MoM (sd 0.23, 1990-2019), Oct -9% of the rate; series is not seasonally adjusted. | Not available. | Not available. | Report text quotes the seasonally adjusted rate (exact match 4%). 9% of month-to-month changes are ties. |
| Energy (weekly, $/gal) | (1) Record 5.107 on 2022-06-13; low 0.949 on 1999-02-22. (2) 2008-07-07 4.165 -> 2008-12-29 1.670 (-59.9% in 25 weeks). (3) Largest weekly jumps: +$0.495 (+13.4%) on 2022-03-07; +$0.464 (+17.5%) on 2005-09-05. | Weak. | Approximate (weighted regional average). | Strong and stable in changes (0.52-0.93), meaningless in levels (0.88-1.00 always). | Report text carries the next week's value (leak). |
| Agriculture (monthly, c/lb) | (1) Record 254.17 on 2022-09 vs 93.3 in 1980-01. (2) From 1990-01 to 2023-12 OT rose 104.4c: spread +69.1c (66%), wholesale +35.3c. (3) 2020-04 -> 2022-09 +51.1c, 95% wholesale (+48.8c). | None (month R2 3.5% of changes). | Exact (Wholesale + Spread); a clear main driver in 49% of months (spread 31%, wholesale 18%). | Components only. | Covariates missing 1980-01..1989-12 and 2024-01..04 (correction: the structure doc said "first 124 rows"). Report text starts 2018-11. |
| Climate (weekly, % area not in drought) | (1) Min 27.6% on 2012-07-17 (72.4% of US area in D0+); max 91.5% on 2019-05-14. (2) 2017-10-24 69.5% -> 2018-01-30 38.1% (-31.4pp in 14 weeks); 2022-12-27 38.0% -> 2024-05-14 73.6% (+35.6pp). (3) D4 (exceptional) peak 9.99% on 2011-07-12. | None. | Exact (100 - D0), but tiers are nested; with 5 exclusive bands one band is >70% of movement in only 24% of weeks (D0-only band in 89% of those). | D1-D4 are tiers of the same quantity. | File sorted descending. OT higher = better (inverted business meaning). |

## Q1. Stories per domain (checkable facts)

Facts are in the table; extra context a partner may ask about:
- **Economy:** exports 17,346 (1987-01) -> 179,326 (2024-03); imports 30,799 -> 259,144. Annual avg deficit: -12.7k (1987), -69.0k (2006), -42.0k (2009), -98.1k (2022), -88.6k (2023). Volatility: sd of MoM change in OT is 1,837 (1980s), 2,612 (1990s), 6,157 (2000s), 8,959 (2010s), 10,321 (2020s): in % of the level it is stable (12-24%).
- **Traffic:** annual totals (million miles): 1,120,328 (1970), 2,147,501 (1990), 3,029,821 (2007), 2,956,763 (2009); the only annual declines 1970-2023 are 1974 (-1.4%), 1979 (-1.2%), 1980 (-0.5%), 2008 (-1.9%), 2009 (-0.6%), 2011 (-0.6%), 2020 (-10.5%). 2020 monthly YoY: Mar -16.1%, Apr -40.0%, May -22.8%, Jun -10.5%, Dec -7.8%; 2021-04 +50.5% (base effect). Rolling-12-month total peaked 3,275,187 at 2020-02; 2024-03 is 3,267,804, still 0.2% below it.
- **Health_US:** 30 weeks with ILI >= 6% (9 in the 2019/20 season, 5 each in 2017/18 and 2022/23). Summer 2020 mean 1.08% vs 1.04% (2019), but summers 2021/22 ~1.83/1.88%: off-season baseline roughly doubled after COVID. Last data point 2.03% (2024-05-06).
- **Environment:** days > 150 AQI per year: 83/43/18/12/0/1 in 1980/1990/2000/2010/2020/2022. Share of days "Unhealthy+": 15.8% (1980s), 10.2%, 5.7%, 1.2%, 0.8% (2020s). Daily sd 44 (1980s) -> 22.6 (2020s): volatility fell with the level.
- **SocialGood:** annual avg 3.77 (1948), 8.47 (1975), 9.71 (1982), 9.62 (2010), 8.09 (2020), 3.63 (2023). Biggest falls: 2020-08 -2.0pp, 2020-06 -1.8pp; first month <= 4.0% after the shock: 2021-11. Latest 3.5% (2024-04).
- **Energy:** annual avg $1.07 (1998), 3.30 (2008), 2.41 (2009), 3.68 (2012), 2.25 (2016), 2.26 (2020), 4.06 (2022). 2014-06-23 3.778 -> 2015-01-26 2.133 (-43.5%). 2020-01-06 2.665 -> 2020-04-27 1.870 (-29.8%). 2022-02-28 -> 2022-06-13: +38.0% in 15 weeks. Latest 3.777 (2024-04-29), +1.8% YoY. Weekly volatility (sd of log change): 1.12% (1993-2000), 2.53% (2001-2008), 1.83%, 1.87% (2017-2024).
- **Agriculture:** yearly avg 97.0 (1980), 145.5 (1990), 175.3 (2010), 199.2 (2020), 242.8 (2022), 246.0 (2023). Biggest MoM: -9.1% (2006-02), +9.0% (1986-07). Volatility (sd of MoM %) fell from 2.77 (1980s) to 1.65 (2020s). Spread avg 83 (1990) -> 153 (2023): the retail-wholesale margin is the long-run trend.
- **Climate:** yearly mean no-drought share 77.6% (2019, wettest), 39.5% (2022, driest), 40.3% (2012). Share of weeks below 60%: 69% (2000s), 45% (2010s), 79% (2020-24). D3 peak 22.4% on 2021-08-17.

## Q2. Seasonality, done properly

**Method.** Seasonal index = 100*ln(y / centred 12-month moving average), averaged by calendar month over 1990-2019 (Unemployment 1950-2019; Economy balance as % of |moving average|, 1995-2019). "Reliable" = |mean| > 2 standard errors and the sign agrees in >= 80% of years. Month R2 = share of detrended variance explained by month. Effect/noise = sd of the 12 monthly means / sd of the residual.

| Series | Month R2 | Effect/noise | Reliably HIGH months (mean vs trend) | Reliably LOW months |
|---|---|---|---|---|
| Traffic | 0.95 | 4.7 | Jul +7.7%, Aug +7.4%, May +5.5%, Jun +5.0%, Oct +3.4% | Feb -14.4%, Jan -9.2%, Nov -3.6%, Dec -2.3% (Mar, Sep not reliable) |
| Exports | 0.72 | 1.7 | Mar +7.8%, Oct +5.5%, Jun +2.8% | Jan -6.7%, Feb -5.1%, Jul -5.3% |
| Imports | 0.67 | 1.5 | Oct +7.7%, Aug +3.0%, Jul +2.1% | Feb -10.1%, Jan -5.1%, Dec -2.8% |
| Trade balance (% of avg) | 0.62 | n/a | Deficit narrowest Feb +19.4%, Mar +12.6%, Dec +9.2% | Deficit widest Jul -17.7%, Oct -10.8%, Aug -9.4% |
| Unemployment rate | 0.63 | 1.4 | Jan +11.5%, Feb +10.8%, Mar +6.2%, Jun +5.7% | Oct -9.4%, Sep -6.0%, Nov -5.8%, Dec -5.3% |
| AQI monthly mean | 0.76 | 1.9 | Jul +40.7%, Jun +30.0%, Aug +27.7% | Oct -23.5%, Nov -20.0%, Dec -15.4% |
| Health_US ILI % | 0.51 (week-of-year, levels) | n/a | Feb 3.12, Jan 3.04, Dec 2.99 (monthly means, 2000-2019) | Jul 0.66, Jun/Aug 0.83 |

- Unusable for seasonal comparison: Agriculture (3.5% of changes), Climate (3% of levels), Energy (12% of changes; mild spring-summer bump). Use the seasonal template only on the five seasonal domains.
- Raw changes are trend-contaminated: sd of raw MoM change in Traffic is 7,662 (1970s) -> 21,326 (2020s), a 2.8x growth, but 7.1% -> 9.5% in % terms (6.4-7.4% before 2020). Economy OT: 1,837 -> 10,321 raw (5.6x). A raw-change threshold calibrated on one era is wrong on another. Use % changes (balance: change as % of the trailing-12-month |average|).
- Typical % MoM moves (Traffic, 1990-2019): Jan -6.2 (sd 2.3), Feb -5.0, Mar +16.9 (sd 1.9), May +4.8, Sep -8.0 (sd 1.3), Nov -6.8. Several of these are mostly month-length effects (28/30/31 days); the rule below handles this automatically because it compares the same calendar month.

**Rule: "in line with the usual seasonal move"** (tested; code-friendly):
1. Move x = % change vs previous period (log-change x100, so -34.2 log points = -28.9%; balance: change / |trailing-12m average| x100; Health_US: weekly pp change).
2. Reference = the same calendar month (Health_US: same ISO week +-2 weeks) in the previous 10 years only (no look-ahead). typical = median of those moves; sigma = 1.4826 x median absolute deviation of all reference moves around their calendar-month medians (pooled over months).
3. z = (x - typical) / sigma. Verdict: |z| <= 2.5 -> "in line with the usual seasonal move"; z > 2.5 -> "stronger/higher than usual for this month"; z < -2.5 -> "weaker/lower than usual". If |typical| < sigma, add "this month has no clear seasonal norm, the move is within normal noise".

Out-of-line rate in calm history (false alarms): k=2.5: balance 3%, exports 6%, imports 4%, Traffic 5%, Unemployment 7%, AQI 6%, Health_US 7%. At k=2: 8-14%; at k=3: 1-3%. Months with a clear norm (|typical| > sigma): balance 39%, exports 62%, imports 34%, Traffic 70%, Unemployment 60%, AQI 43%, Health_US 36%. In months with a clear norm, the actual move had the typical sign in 77% (balance), 98% (exports), 87% (imports), 96% (Traffic), 89% (Unemployment), 85% (AQI), 90% (Health_US).

Verdicts on known shocks (move vs typical, z):
- **Economy April 2020:** balance -14.8% of avg (-$10.3bn) vs typical -7.9, z = -0.7: "in line" (balance barely moved relative to its noise). Components: exports -34.2% vs typical -6.8 (z = -14.8), imports -15.8% vs -2.7 (z = -3.8). So run the rule on components, not only on the balance. Other: 2008-11 balance +34.1% vs +7.6 (z = +3.8, flagged); 2022-03 -35.7% vs -11.1 (z = -2.1, in line; borderline because March always moves a lot).
- **Traffic spring 2020:** Mar -6.8% vs typical +17.3 (z = -17.8); Apr -30.2% vs +1.2 (z = -23.2); May +27.7% vs +3.0 (z = +18.2); Jun +12.5% vs -0.4 (z = +9.5). 2021-04 -3.8% vs +1.2 (z = -3.5).
- **Unemployment 2020:** Mar +16.9% vs -3.5 (z = +8.1); Apr +116.3% vs -9.0 (z = +49.6); May z = -4.6; Jun z = -8.5.
- **Health_US 2020:** week 03-09 +1.00pp vs typical -0.24 (z = +7.5); 03-23 -1.13pp (z = -6.4); 04-06 -1.36pp (z = -9.3). 2009-10-05 +1.15pp (z = +23.7). 2022-11-07 +0.06pp (z = -0.8, in line); 2022-11-14 +1.64pp (z = +15.2).
- **AQI June 2023:** monthly mean +41.9% vs typical +16.0 (z = +2.7): flagged, mildly; the daily peak (254) is far more extreme than the monthly mean shows.

## Q3. Drivers (level 1): shares of months with a clear main driver

"Clear main driver" = the larger component contributes > 70% of gross movement (|c_i| / (|c_1| + |c_2|)). "Clean" = one component explains 70-130% of the net change and the other < 30%. Months with a negligible net change are excluded (Economy: |dOT| < $1bn, n = 366 of 446; Agriculture |dOT| < 1c, n = 291 of 407; Climate |dD0| < 1pp, n = 749 of 1,271).

| Decomposition | Main driver (gross >70%) | Clean attribution | Components offset each other |
|---|---|---|---|
| Economy MoM (Exports vs -Imports) | 49% (Imports 34%, Exports 16%) | 31% | 68% (exports and imports rose/fell together) |
| Economy YoY | 40% (Imports 29%, Exports 11%) | 23% | 82% |
| Agriculture MoM (Wholesale vs Spread) | 49% (Spread 31%, Wholesale 18%) | 31% | 70% |
| Agriculture YoY | 45% (22% each) | 31% | 70% |
| Climate weekly, D0-only band vs D1+ | 66% (D0-only 45%, D1+ 21%) | 56% | 31% |
| Climate weekly, 5 exclusive bands | 24% (D0-only band in 89% of these) | n/a | n/a |
| Health_US weekly: ILI visits vs patients (weeks with |dlnOT| >= 10%, n = 497) | 70% ILI visits, 13% patients (16% mixed) | n/a | 60% (opposite signs) |
| Health_US weekly ILI visits by 4 age groups (>= 5% change, n = 997) | 6% (5-24 years in 87% of them); >50% in 40% | 12% | n/a |

Era check (Economy, gross main driver): 51% (1987-99), 51% (2000-19), 38% (2020+). Agriculture: 47% / 54% / 40% (1990-2004 / 2005-19 / 2020+).

Notable decompositions:
- Economy 2008-11: deficit narrowed $24.2bn: imports -$38.4bn (158% of the change), exports -$14.2bn (-58%). 2009-01: +$5.0bn: imports fall = 306%, exports -206%. 2020-03: -$13.6bn: imports +$15.8bn (116%), exports +$2.2bn (-16%). 2022-03: -$33.0bn: imports +$61.8bn (187%), exports +$28.8bn (-87%). YoY 2023-03 vs 2022-03: +$38.5bn = imports -$33.2bn + exports +$5.3bn.
- Agriculture 2020-04: +10.3c = spread +18.3c, wholesale -8.0c. 2022-09 -> 2023-12: -9.9c = wholesale -17.4c, spread +7.4c (offset).
- Climate 2012-05-29 -> 07-17: no-drought -18.8pp: D2-only band +12.5pp, D3-only +6.7pp, D1-only +2.4pp, D0-only -3.1pp (drought deepening, not spreading). 2017-10-24 -> 2018-01-30: -31.4pp: D2-only +11.5, D1-only +9.8, D0-only +9.4 (broad onset). 2022-12-27 -> 2024-05-14: +35.6pp: D2-only -11.2, D1-only -10.3, D3-only -6.4, D0-only -5.8, D4 -1.9.
- Health_US 2022-11-07 -> 11-14: OT 5.74 -> 7.37 (+0.251 log). ILI visits 137,419 -> 164,936 (+0.183, 73%); total patients 2,396,019 -> 2,237,505 (-6.6%; +0.069, 27%). Visits by age: 0-4 +4,690, 5-24 +7,696, 25-64 +11,190, 65+ +3,941 (sum +27,517, exact). 2020-03-16 -> 03-23: ILI visits 78,584 -> 53,142, patients 1,068,755 -> 853,431 (patients fell 20% too).
- Patient-volume-driven weeks cluster in Nov-Dec (45 of 64 such weeks): holiday visit volume, not flu.
- Implication: "X was the main driver" is only defensible about half the time for sum-type KPIs; the demo should state shares and say "no single driver" when neither exceeds 70%. Climate bands need exclusive bands (D0 - D1, D1 - D2, ...): the raw D columns are cumulative. Age groups reconcile exactly only after merging AGE 25-49 + 50-64 (post-2009) with AGE 25-64 (pre-2009): residual 0.

## Q4. Co-movement (level 3)

**Energy regional prices** (weekly log changes unless noted):
- Correlation with US average: East 0.94, Gulf 0.93, Midwest 0.90, West 0.76, Rocky 0.73. Pairs, full sample [sub-period range over 1993-2000 / 2001-08 / 2009-16 / 2017-24]: East-Gulf 0.93 [0.90-0.96]; Gulf-Midwest 0.77 [0.60-0.83]; Gulf-West 0.66 [0.59-0.72]; Midwest-West 0.52 [0.28-0.62]; Rocky-West 0.67 [0.37-0.83]; Rocky-Midwest 0.55 [0.27-0.67].
- **Stability:** computed on 1993-2008, tested on 2009-2024: 0.69 -> 0.64, 0.78 -> 0.76, 0.49 -> 0.55, 0.95 -> 0.92, 0.67 -> 0.67, 0.54 -> 0.56 (all within 0.07). Changes correlations hold; the 1993-2000 Rocky/Midwest/West pairs are the weak spot (0.27-0.37: thinner or smoother regional data; uncertain).
- **Spurious levels:** level correlations are 0.88-1.00 in every sub-period for every pair, which says nothing (all prices trend with crude). Demo: monthly US gasoline vs US broiler retail price (Agriculture): levels corr 0.77, changes corr -0.03 (n = 373). Never report level correlations of trending series.
- **Lead/lag:** peak is at lag 0 (0.55-0.93); lag-1 neighbours are 0.33-0.58 and are mostly weekly momentum (autocorrelation of weekly changes 0.57). Gulf -> West/East: Gulf_t with West_{t+1} 0.56 (West_t with Gulf_{t+1} 0.42), stable in both halves (0.61/0.53 vs 0.45/0.39). Midwest leads Gulf and Rocky by a week (Gulf_t vs Midwest_{t-1} 0.56 vs 0.33 the other way; Midwest_t vs Rocky_{t+1} 0.53 vs 0.27). Not causal; use only "moved a week earlier".
- **Trending spread:** West-Gulf gap averages $0.16 (1993-2000), 0.28, 0.50, 1.09 (2017-2024); peak 2.65 on 2022-10-03 (lag-1 autocorrelation 0.993). "West vs Gulf" statements need a period, not a global average.
- Event check: 2005-09-05 weekly rise by region: Central Atlantic +25.6%, East +22.9%, Midwest +16.5%, Gulf +15.0%, West +10.2%. 2022-03-07: +10.7% (West) to +16.0% (New England).

**Health_US covariates** (OT = % ILI; eras 1997-2008 / 2009-19 / 2020-24):
- % WEIGHTED ILI: levels 0.97 / 0.99 / 0.99, changes 0.88 / 0.95 / 0.98: same quantity (mean gap +0.21pp pre-2009, max |gap| 2.52 on 1999-02-01).
- Age-group ILI counts: level corr 0.65-0.74 (1997-2008) -> 0.78-0.93 (2009-19) -> 0.80-0.92 (2020-24); changes 0.55-0.86. Real, but grows with sample size (more providers), not a stable parameter.
- NUM. OF PROVIDERS / TOTAL PATIENTS vs OT: levels 0.29/0.25, 0.51/0.40, 0.30/0.32; changes 0.09/-0.12, 0.04/-0.20, 0.03/0.09. **Spurious/unstable**: both counts trend (corr with time 0.91, 0.89; providers 270 in 1998 -> 3,753 in 2023; patients 68k -> 2.29M) while OT has none (0.22). In-season (Nov-Mar) OT-patients 0.11 / 0.41 / 0.26.
- Age lead/lag: season peak of 65+ minus peak of 5-24: mean -0.4 weeks, range -4..+2 over 10 seasons; cross-correlation is highest at lag 0 (0.86 vs 0.85 at +1). No reliable lead; do not claim "children lead the elderly".

## Q5. Class balance of code-generated questions

Share of "yes" over all valid positions (first 12/52/365 periods dropped). Ties count as "no" for rise. Environment is daily, so "12 periods" = 12 days (monthly-mean version in the last row).

| Domain | n | Rise vs prev | Ties | Above avg of prev 12 | Highest in last 12 | Above same period last year |
|---|---|---|---|---|---|---|
| Economy | 435 | 48% | 0% | 38% | 7% | 36% |
| Traffic | 639 | 53% | 0% | 61% | 14% | 83% |
| Health_US (from 2003-06) | 1,037 | 50% | 0% | 51% | 28% | 58% |
| Environment (daily) | 15,614 | 50% | 3% | 43% | 10% | 47% |
| Environment (monthly mean) | 513 | 54% | 0% | 35% | 8% | 45% |
| SocialGood | 904 | 34% | 9% | 41% | 11% | 33% |
| Energy | 1,570 | 48% | 1% | 55% | 27% | 62% |
| Agriculture | 520 | 52% | 0% | 59% | 19% | 61% |
| Climate | 1,220 | 53% | 0% | 53% | 21% | 54% |

- "Highest in last 12" is skewed to "no" everywhere (72-93% no): always answering "no" scores 72-93%. Sample "yes" cases deliberately.
- SocialGood rise is only 34% (9% flat: a third class; 13% in the 2020s). "Above 12-period average" is 41% overall but 45% in the first 80% of time vs 29% in the last 20%, so the balance shifts between train and test.
- Rise/fall is near 50/50 overall but almost deterministic by calendar month in seasonal domains. Traffic rise by month: Jan 2%, Feb 0%, Mar 98%, May 100%, Sep 0%, Oct 100%, Nov 0%. Unemployment: Jan 99%, Jun 97%, Mar 5%, Apr 3%. Economy: Feb 89%, Jul 11%.
- Baselines on the last 20% of time (accuracy, majority-class / repeat-last-answer / calendar-month majority from train): rise: Economy 53/33/78, Traffic 48/34/82, Unemployment 62/60/78, AQI monthly 48/55/78, Health_US 48/79/58, Energy 49/72/63, Agriculture 55/48/47, Climate 54/62/57. Above-12-avg: Health_US 49/93/60, Energy 55/94/65, Climate 51/91/51, Traffic 61/61/84. So a model that merely knows the month scores 78-82% on seasonal rise/fall; one that repeats the last answer scores 91-94% on weekly "above average" questions.
- Economy and Climate semantic traps: Economy OT is negative (rise = deficit narrows; "highest" = smallest deficit). Climate OT = share *not* in drought.

## Q6. Text vs numbers (`fact` only)

Economy, Energy, Traffic (clean text, 0% NA) sampled, 15 each (`random_state` 1/2/3; rows #4,122,164,173,185,201,413,407,224,233,256,368,283,348,285 for Economy). Systematic regex checks over all rows supplement the 15; regex coverage is partial (uncertain).

**Energy: report agrees with the series almost perfectly, one week late.**
- 15/15 weekly-change claims match the series change at the *mentioned* Monday within $0.003 (e.g. +0.494 vs +0.495 on 2022-03-07); 15/15 year-ago gaps within $0.031 (median $0.007); 0/15 levels match (regular vs all grades; series +$0.09).
- All 351 rows: change sign agrees 97.7% (100% for moves >= $0.03, n = 204); 99% within $0.01; year-ago sign 98.5% (n = 332); streak claims ("for the seventh week in a row", n = 81): direction 100%, exact length 85%, misses off by one.
- Against the window's own date instead (the natural pairing), change sign agrees only 74%: the leak is real.
- Claim types: level (99% of facts), vs last week (98%), vs year ago (93%), streak (23%), all series-determined except inventories/production (2%, outside knowledge).

**Economy: direction often right, magnitude and level almost never.**

| Row | Deficit direction vs series | Exports | Imports |
|---|---|---|---|
| 2000-05 | up, +4.6 OK | "decreased" vs +1.4 X | up OK |
| 2010-05 | up +2.0 vs 0.0 (flat) X | +3.0 vs +3.0 OK | +4.9 vs +3.0 (dir OK) |
| 2013-11 | down OK (-5 vs -10.6) | +1.7 vs -5.9 X | down OK |
| 2014-08 | down OK | +0.4 vs +4.3 OK | +0.2 vs -7.8 X |
| 2015-09 | down OK | +3.0 vs +2.2 OK | -4.2 vs +1.6 X |
| 2017-01 | up OK (+4.2 vs +11.0) | +1.1 vs -9.1 X | +5.3 vs +1.9 OK |
| 2018-03 | down -7.8 vs -0.1 (dir only) | +3.4 vs +21.3 OK | -4.4 vs +21.2 X |
| 2018-09 | up +0.6 vs -9.8 X | +2.5 vs -0.8 X | +3.1 vs -10.6 X |
| 2018-12 | up +9.5 vs -1.6 X | not stated | not stated |
| 2019-09 | down OK (-2.6 vs -4.8) | not stated | not stated |
| 2021-08 | up OK (+2.9 vs +3.9) | +1.0 vs +4.0 OK | +4.0 vs +7.9 OK |
| 2022-04 | down OK (-20.0 vs -17.0) | +5.2 vs -5.8 X | -14.8 vs -22.8 OK |
| 2023-11 | down OK (-1.3 vs -10.1) | -4.8 vs -10.8 OK | -6.1 vs -20.9 OK |
| 2023-12 | down OK (-0.9 vs -9.1) | +4.1 vs +0.6 OK | +3.2 vs -8.5 X |
| 2024-01 | up OK (+3.3 vs +13.6) | +0.3 vs -7.2 X | +3.6 vs +6.4 OK |

- Directions: deficit 12/15 (incl. one tiny), exports 7/13, imports 8/13. Magnitude within ~25%: 1/15 (2022-04); levels: 0/15 (e.g. 2024-01 text 67.4bn vs series 93.2bn). Over all rows a regex finds a deficit direction in 207 of 435 facts; 69% agree with the series.
- Why (likely, uncertain): reports quote the monthly Census/BEA release (seasonally adjusted; goods *and* services deficit in some years, goods only in others, first-release vintage), while OT looks like a not-seasonally-adjusted goods series: its exports 173.5k (2022-04) match "goods exports 173.9bn" in the text, but the 2017-01 text gives goods and services exports of 192.1bn vs series 117.5bn. The structure doc calls OT "goods & services"; the text comparison suggests otherwise (uncertain).
- Claim types: exports/imports (83%), goods/services split (90%, not in the data), 3-month average or year-to-date (6%, computable only with the same measure), country or commodity detail (0%). Roughly 1/3 of claims (goods vs services split, averages, SA) cannot be verified from the dataset.

**Traffic: matches within first-release noise.**
- 15 sampled: 4 are weekly interstate reports (2020-04..2022-12, 85 of 367 rows) with no counterpart in OT; 11 monthly: direction 11/11, YoY % within 0.5pp 6/11, within 1pp 9/11; level (billions) within 2% 11/11 (largest 2.0%).
- All monthly rows parsed (n = 197): YoY sign agrees 88% (96% when |YoY| >= 1pp); within 1pp 70%, within 2pp 90%; level within 2% for 85%, within 3% for 94%. Notable misses: 2020-02 (+2.2% vs +8.3%, leap day), 2008-05 (+3.7% vs -2.3%, likely a first-release or parse issue; uncertain), 2020-08/09.
- 2020-04: text -39.8% / 169.6bn, series -40.0% / 167.6bn. The monthly text also quotes seasonally adjusted figures (22% of facts) that OT does not contain.

**SocialGood (extra check):** 47 parsed rate claims; exact match to OT only 4%, within 0.1pp 17%, mean abs gap 0.27pp. The gap follows the seasonal pattern (Jan series +0.5, Nov -0.35 vs text): text is seasonally adjusted, OT is not. 78% of facts start with an "Objective..." boilerplate prefix.

## Q7. Pitfalls for the evaluation

1. **Repeat-last-value is very hard to beat.** Mean absolute error on the last 20% of time: repeat-last 1-step MAE is 0.04x (Energy, Agriculture), 0.12x (Climate), 0.18-0.20x (Economy, Traffic, SocialGood, Health_US) and 0.46x (Environment daily) of the train-mean predictor's MAE. Seasonal-naive (value one year ago) beats repeat-last only for Traffic (MAE 9,571 vs 14,754); elsewhere repeat-last wins (ratios 0.08-0.91). A model with trend/level shift handling will look good simply by echoing the last value; always report the naive baseline and skill relative to it.
2. **Level shifts between train and test.** Share of test values outside the train range: Agriculture 36%, Traffic 34%, Economy 29%, Energy 7%, SocialGood 1%. Test mean / train mean: Economy 2.18x, Traffic 1.44x, Energy 1.44x, Agriculture 1.38x, Health_US 1.53x. Models trained on raw levels will fail on records ("highest ever" questions have a built-in test advantage).
3. **COVID and 2022 inside the test window.** With 80/10/10 splits, 2020 sits in the test or at the val/test boundary for Economy (boundary 2020-06), Traffic, Health_US (test from 2021-09: post-COVID flu regime), Climate, Energy (2022 spike). Test performance mixes normal and shock periods; report them separately.
4. **Units are not comparable across domains.** USD millions (Economy, negative), million vehicle-miles (Traffic), $/gal, % ILI, % area, cents/lb, AQI index, unemployment %. Use scale-free metrics (MASE, % error); never average raw MAE across domains.
5. **Length and frequency imbalance.** 447 (Economy) to 15,979 (Environment daily) rows; Environment would dominate a pooled sample. Sample per domain; monthly aggregation for Environment is the demo-friendly choice.
6. **Text coverage vs time split** (80/10/10 split; rows with non-NA `fact`):
   - Environment report: 141 rows, all in the test third (0 train). Agriculture report: 0 train, 482 val, 408 test (starts 2018-11). Health_US report: 438 train, 51 val, 0 test (ends 2019-12). Traffic report: 136 train vs 166 test. Economy 259/87/89, Energy 186/98/70, Climate 467/57/58, SocialGood 179/94/74.
   - Text-vs-no-text comparisons are confounded by period (the text domains differ in coverage and regime). Do not train a text model on Environment or Agriculture reports.
7. **Text leakage.** (a) Energy report attached to week t describes week t+1's price (349 of 351 rows), including its direction (98%). (b) Economy/Traffic/SocialGood report rows contain the same month's value as the target; they can only be an input for questions about earlier periods. (c) The release lag (data published 1-6 weeks later) is ignored by the pairing. (d) `search` text: 2-3% of rows mention a year later than the row's year (Economy 3.0%, SocialGood 2.7%, Traffic 2.7%); small but non-zero look-ahead. (e) An LLM may know 2020-2023 events from pretraining; check "text helps" claims on pre-cutoff periods too.
8. **Text and series measure different things.** Energy: regular vs all grades; Economy: SA release vs NSA series (and possibly goods vs goods-and-services); SocialGood: SA vs NSA; Traffic: first release (monthly OK, weekly interstate not in OT). Facts that disagree with the series are not hallucinations; score "text-consistent" questions against the text's own measure or restrict to Energy and Traffic.
9. **Zero and placeholder values.** Health_US has 0/0 summer weeks in 1998-2002 (OT = 0.0, e.g. 1998-05-18): "lowest" and "% change" questions are broken there; 5 duplicate dates at year ends; age schema change in 2009.
10. **Semantics and mechanics.** Economy OT negative (rise = deficit narrows); Climate OT = non-drought share; Traffic month-length effects and the leap Feb 2020 (YoY +8.3%); SocialGood has 9% ties; Health_US counts (providers 14x) are not comparable across years (use rates).
11. **Boilerplate in text.** 51% of Economy, 78% of SocialGood, 41% of Health_US facts start with "Objective facts..." prefixes; 31% of Agriculture and 23% of SocialGood report rows are exact duplicates. Strip before use and de-duplicate across splits.
12. **Structure-doc correction.** Agriculture covariates are empty for 1980-01..1989-12 (120 rows) and 2024-01..04 (4 rows), not the "first 124 rows".

## Uncertain items

- Real Time-MMD split ratios and the loader's text-window matching were not read; 80/10/10 is an assumption.
- Economy OT being a goods, NSA series is inferred from the text/series mismatch, not from documentation.
- Environment "wildfire smoke" attribution of 2023-06-07 comes from the report text (a different series' claim), not the data; avoid causal wording.
- Regex-based claim parsing (Energy 351/354, Traffic 197/282 monthly, Economy 207/435, SocialGood 47/347) covers a subset; percentages are for parsed rows only.
