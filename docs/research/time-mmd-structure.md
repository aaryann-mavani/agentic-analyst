# Time-MMD data structure (commit 00281e2)

Source: https://github.com/AdityaLab/Time-MMD @ `00281e2d86058286d5548b15a7670e8eda57ef62`. Read-only inspection of CSVs (pandas, `python3 -I`); clone deleted afterwards.
Repo OT table (DescriptionOfOT.png) names targets; it lists Climate as monthly, but the CSV is weekly.

## Summary

| Domain | Freq | Years | Level 1 possible? | Level 2 possible? | Level 3 candidates | Quality issues |
|---|---|---|---|---|---|---|
| Agriculture | monthly | 44.3 (1980-01..2024-04) | **Yes, exact**: OT = Wholesale + Spread (max resid 1e-12) | Weak; no seasonality (ACF diff lag12 0.04) | none beyond the two components | Both covariates empty for first 124 rows (1980-1990) |
| Climate | weekly | 24.4 (2000-01..2024-05) | **Yes, exact**: OT = 100 - D0 (max resid 1.4e-14) | Weak; no seasonality (lag52 ACF 0.23; diff 0.03) | D1-D4 (nested severity shares, corr -0.92..-0.41) | File sorted **descending** |
| Economy | monthly | 37.2 (1987-01..2024-03) | **Yes, exact**: OT = Exports - Imports (max resid 0.1, rounding) | **Yes**: ACF diff lag12 0.54, month explains 33% of diff variance | none beyond components | Rows **not sorted** (2024 first, then 2023, ...) |
| Energy | weekly | 31.1 (1993-04..2024-04) | Near-exact only: OT ~ weighted avg of 5 PADD regions (max resid 0.019 $/gal; plain mean 0.085) | Weak (week-of-year 12% of diff variance) | 8 regional prices (corr 0.98-1.0, diff corr 0.76-0.95) | Clean |
| Environment | daily | 43.7 (1980-01..2023-09) | No | **Yes** at monthly agg: summer peak (Jul mean 116 vs Mar 66), monthly ACF12 0.89 | Category (derived from OT), Defining Parameter, sites reporting (corr -0.10) | Only one CBSA (NYC); covariates mostly categorical |
| Health_AFR | weekly | 28.3 (1996-01..2024-04) | No (OT only) | Poor: lag52 ACF 0.01 | none | 3 NA, 3 `inf`, 12 values >1 for a proportion (max 20.25), 201 zeros, 3 multi-week gaps |
| Health_US | weekly | 26.6 (1997-09..2024-05) | **Yes, exact**: OT = 100·ILITOTAL/TOTAL PATIENTS (max resid 5e-6); ILITOTAL = sum of age columns (resid 0) | **Yes**: strong flu season, lag52 ACF 0.54, week-of-year 44% of level variance | % WEIGHTED ILI (0.98), providers | `X` placeholders; 5 duplicate dates; 5 2-week gaps; 95 zero rows (off-season 1998-2000s, 0/0) |
| Security | monthly | 25.7 (1998-09..2024-05) | No (OT only) | No: lag12 ACF 0.26, diff 0.00 | none | Extremely spiky (max 2.0e10 in 2020-09 vs median 3.5e8) |
| SocialGood | monthly | 76.3 (1948-01..2024-04 data) | No (OT only) | **Yes**: ACF diff lag12 0.45 (looks not seasonally adjusted) | none | 8 trailing empty rows 2024-05..2024-12 |
| Traffic | monthly | 54.2 (1970-01..2024-03) | No (OT only) | **Yes, strongest**: ACF diff lag12 0.87, month explains 86% of diff variance | none | Clean |

"Years" = span of rows. Seasonality tests: autocorrelation of first differences at the seasonal lag, and share of differenced variance explained by month/week-of-year means.

## Per domain

### Agriculture
- 532 rows, monthly (first of month), ascending, no gaps/duplicates. Columns: `Date`, `date`, `start_date`, `end_date` (all the same date info).
- OT = retail broiler composite price (cents/lb, 88-254). `Wholesale broiler composite` and `Retail-wholesale spread for broiler composite` (same units).
- L1: OT = Wholesale + Spread, max abs residual 9.9e-13 over 408 rows with both present.
- L3: corr with OT levels 0.80 / 0.89; diffs 0.07 / 0.62. The spread drives month-to-month moves; both are components, not independent drivers.
- L2: 44 years; ACF lag12 of diffs 0.04, month explains 3.5% of diff variance -> no real seasonality, strong trend.
- Quality: covariates empty for the first 124 rows (1980-01..1990-04).
- Text: report 890 rows, 2018-11..2024-05 (USDA broiler market notes), 0% NA fact; search 1653 rows, 1979-12..2024-04, 23% NA fact. Example: "The national whole broiler/fryer prices are showing mixed undertones, mostly steady to weak, with offerings of all sizes light to moderate."

### Climate
- 1272 rows, weekly (Tuesday map dates), **sorted descending**, no gaps/dups. Columns: `MapDate` (yyyymmdd int), `AreaOfInterest`="Total", `ValidStart/ValidEnd`, `StatisticFormatID`=1, `date/start_date/end_date`.
- OT = % of US area with no drought (US Drought Monitor; range 27.6-91.5). D0..D4 = cumulative % of area in D0-or-worse ... D4 (exceptional) drought.
- L1: OT = 100 - D0 exactly (max resid 1.4e-14). D0 >= D1 >= ... >= D4 are nested.
- L3: D1-D4 correlate -0.92, -0.83, -0.69, -0.41 (diffs -0.51..-0.10); they are severity tiers of the same quantity.
- L2: 24 years; lag52 ACF 0.23 (levels), diff 0.03; week-of-year explains 3% of level variance -> no usable seasonality.
- Text: report 590 rows, monthly 1999-01..2024-04 (NOAA climate reports), 1% NA; search 2261, 14% NA. Example: "April 2002 was slightly drier than average, ranking 39th driest, with a precipitation anomaly of -0.23 inches ..."

### Economy
- 447 rows, monthly, 1987-01..2024-03, complete (447 months), no dups, **not sorted** (block order: 2024, 2023, ...). Columns: `Month` ("January 2024"), `Exports`, `Imports`, `OT`, dates.
- OT = US goods & services trade balance (USD millions, always negative, -116,662..-1,889).
- L1: OT = Exports - Imports, max abs resid 0.1 (mean 0.011), i.e. rounding only.
- L3: corr levels Exports -0.90, Imports -0.96; diffs -0.02 / -0.73. Imports drive changes. Components only.
- L2: 37 years; ACF of diffs lag12 0.54, month explains 33% of diff variance -> clear seasonality (not seasonally adjusted). ACF lag1 of diffs -0.42.
- Text: report 435 rows 1995-01..2024-03 (Census trade releases), 0% NA; search 2314, 0% NA. Example: "The goods and services deficit decreased $1.6 billion from February 2012 to February 2013. Exports were up $5.8 billion ..."

### Energy
- 1622 rows, weekly (Mondays), 1993-04-05..2024-04-29, ascending, no gaps/dups.
- OT = US average retail gasoline price, all grades, all formulations ($/gal, 0.95-5.11). Covariates: same price for East Coast, PADD 1A New England, 1B Central Atlantic, 1C Lower Atlantic, Midwest, Gulf Coast, Rocky Mountain, West Coast.
- L1: not an exact sum. Plain mean of the 8 columns: max resid 0.085. OLS on the 5 PADD regions (East, Midwest, Gulf, Rocky, West): weights 0.38/0.29/0.12/0.04/0.17, const -0.006, max resid 0.019 -> volume-weighted average with time-varying weights. East Coast ~ 0.13·1A + 0.35·1B + 0.53·1C (max resid 0.014). Approximate L1 only.
- L3: all regions corr 0.98-1.00 levels; diffs 0.95 (East), 0.94 (Gulf), 0.91 (Midwest), 0.77 (Rocky), 0.76 (West). Regional prices are both components and co-movers; no external driver (e.g. crude) included.
- L2: 31 years; ACF diff lag52 0.07, week-of-year explains 12% of diff variance -> mild spring-summer pattern; diff lag1 ACF 0.57 (momentum).
- Text: report 354 rows 2011-07..2024-04 (EIA weekly), 0% NA; search 2314. Example: "The national average retail regular gasoline price decreased for the sixth week in a row to $1.759 per gallon on February 8, 2016 ..."

### Environment
- 15979 rows, daily, 1980-01-01..2023-09-30, ascending, no gaps/dups.
- OT = daily AQI for one CBSA (New York-Newark-Jersey City; 13-279). Covariates: `CBSA`, `CBSA Code` (constant), `Category` (AQI band: Moderate 8967, Good 3693, USG 2106, Unhealthy 819, Very Unhealthy 394), `Defining Parameter` (Ozone, PM2.5, NO2, CO, PM10), `Defining Site`, `Number of Sites Reporting` (corr -0.10).
- L1: none numeric. `Category` is a deterministic banding of OT (leakage, not a sum).
- L3: Defining Parameter is the plausible "driver" story (ozone summers vs. PM2.5/CO winters); sites reporting uninformative.
- L2: 43 years; daily lag365 ACF 0.42 (diff ~0); monthly-mean ACF12 0.89, Jun-Aug peak (103/116/101 vs ~66 in winter) -> seasonal at monthly aggregation; long downward trend.
- Text: report 156 rows only, 2021-05..2023-10, 10% NA fact (6% fact+preds NA); search 2312, 2% NA. Example: "The New York City area is experiencing poor air quality due to wildfires in eastern Canadian provinces ..."

### Health_AFR
- 1461 rows, weekly, 1996-01-01..2024-04-29, ascending. Columns: `date`, a second `date` (duplicate header -> `date.1`), `end_date`, `OT`; no `start_date`.
- OT = share of influenza-positive / flu patients in WHO African region (median 0.12).
- L1/L3: no covariates.
- L2: 28 years but lag1 ACF 0.76, lag52 ACF 0.01 -> no seasonality.
- Quality: 3 empty OT (first 3 weeks of 1996), 3 `inf` (1997-05-19, 1997-06-09, 2001-11-05; divide-by-zero), 12 values >1 (max 20.25) impossible for a proportion, 201 zeros, gaps of 14/63/70 days (around 1997-10..12, 2000-10..12, 2001-12).
- Text: report 482 rows 2017-08..2024-05, 49% fact = NA plus ~32% "no information..." phrasing; search 1911, 5% NA. Example (typical): "There is no information about the proportion of flu patients ... The report only discusses an outbreak of Ebola Virus Disease in Uganda."

### Health_US
- 1389 rows, weekly, 1997-09-29..2024-05-06, ascending. Columns: dates, `REGION TYPE`="National", `REGION`="X" (all), `YEAR`, `WEEK`, `YEAR_WEEK`, `% WEIGHTED ILI`, `OT`, `AGE 0-4`, `AGE 5-24`, `AGE 25-49`, `AGE 25-64`, `AGE 50-64`, `AGE 65`, `ILITOTAL`, `NUM. OF PROVIDERS`, `TOTAL PATIENTS`.
- OT = % unweighted ILI (CDC ILINet; 0-7.8). Age columns = ILI visit counts by age group; ILITOTAL = ILI visits; TOTAL PATIENTS = all visits.
- L1: OT = 100·ILITOTAL/TOTAL PATIENTS (ratio, max resid 5e-6, 1289 rows with nonzero denominators). ILITOTAL = sum of age columns (X treated as 0), resid exactly 0. Two-level hierarchy: ages -> ILITOTAL -> OT.
- L3: % WEIGHTED ILI corr 0.98 (diff 0.91) - a sibling estimate, near-duplicate; age groups 0.61-0.79; providers 0.46 / patients 0.41 (diff ~0).
- L2: 26 years; lag52 ACF 0.54, diff lag52 0.35; week-of-year explains 44% of level variance -> strong winter flu season.
- Quality: `X` placeholders: AGE 25-49 and 50-64 are X in 532 rows (1997-2009 partly), AGE 25-64 X in 762 rows (2009+) - age schema change in 2009. 5 duplicate dates (week 53 and week 1 of next year share date, e.g. 1997-12-29), and 5 two-week gaps at other new years. 95 rows of all-zero counts (summer off-season 1998-2000s; OT=0 from 0/0).
- Text: report 864 rows 1999-01..2019-12 (ends 2020 - no reports after), 43% NA fact; search 2087, 4% NA. Example: "The proportion of outpatient visits for influenza-like illness (ILI) was 3.2%, which is above the national baseline of 2.1%."

### Security
- 309 rows, monthly, 1998-09..2024-05, complete, ascending. Only `date`, `OT`, `start_date`, `end_date`.
- OT = FEMA disaster and emergency grant amounts (USD; 8.1e5..2.0e10, median 3.5e8).
- L1/L3: no covariates.
- L2: lag12 ACF 0.26, diff lag12 0.00, month explains 3% -> no seasonality; heavy-tailed spikes (2020-09 2.0e10, 2021-01 8.7e9, COVID era).
- Text: **report is unusable**: 19569 rows (1980-04..2024-04) with 100% empty `fact` and `preds`. Search 2311 rows, 1% NA. Example: "The Federal Emergency Management Agency (FEMA) is an independent agency of the federal government ... established in 1979."

### SocialGood
- 924 rows, monthly, 1948-01..2024-12, ascending, no gaps; data ends 2024-04.
- OT = US unemployment rate (%; 2.4-14.4). No covariates.
- L2: 76 years; diff lag12 ACF 0.45, month explains 40% of diff variance -> appears **not seasonally adjusted**; good for seasonal decomposition.
- Quality: last 8 rows (2024-05..2024-12) empty OT.
- Text: report 371 rows 1994-01..2024-04 (BLS Employment Situation), 6% NA; search 4590, 2% NA. Example: "The unemployment rate was unchanged at 4.7 percent in October 2007. The number of unemployed persons, at 7.2 million, was essentially unchanged in October."

### Traffic
- 651 rows, monthly, 1970-01..2024-03, ascending, complete. Columns: `OT`, `Date`, `date`, `start_date`, `end_date`.
- OT = US vehicle miles traveled, not seasonally adjusted (millions; 77,442-294,328). No covariates.
- L2: 54 years; diff lag12 ACF 0.87, month explains 86% of diff variance -> strongest seasonality in the set; COVID drop 2020.
- Text: report 367 rows 2002-01..2024-03 (FHWA Traffic Volume Trends), 0% NA; search 2309, 1% NA. Example: "Travel on all roads and streets in the US changed by -2.9% in February 2003 compared to February 2002, resulting in an estimated 200.3 billion vehicle-miles traveled."

## Common notes
- All textual files share columns `<index>, start_date, end_date, fact, preds`; `preds` packs long-term and short-term predictions separated by `;`. Search files all start around 1979-12-31 and end 2024-04-29. Facts are LLM-summarised, often with "NA" when the source had nothing relevant.
- Numerical files carry redundant date columns (`date`, `Date`, `start_date`, `MapDate`, ...); pick `date`/`start_date` and sort explicitly (Climate and Economy are not ascending).
