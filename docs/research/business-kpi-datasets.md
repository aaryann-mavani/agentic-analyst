# Public business-KPI time-series datasets for TimeNet connectors

Researched 2026-11-19. Claims come from primary sources (dataset pages, license records, live API/file checks
run today) unless marked **(unverified)**. "L1/L2/L3" are the explanation levels in `CONTEXT.md`:
L1 Driver (components sum to the total), L2 Seasonal comparison (needs 2-3+ years), L3 Co-movement (covariate).

TimeNet constraint that drives the ranking ([docs/connectors.md](https://github.com/OpenTSLM/TimeNet/blob/main/docs/connectors.md)):
*"Pin every source file outside the Hub. Use a versioned or commit-pinned URL, never a moving branch ... and pass its
`sha256`."* The dataset card (`dataset.yaml`) must state a `license`. So the ideal source is a **static file at a
stable URL, no login, under a license that permits redistribution**. A moving file (re-published monthly) breaks
the sha256 pin; for public-domain/CC0 data the workaround is to snapshot it to a Hugging Face dataset repo and
pin a commit.

## Ranked table

| # | Dataset | Freq / history | L1 exact sums | L2 | L3 covariates | License / download | Connector effort | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **US Census Monthly Retail Trade (MRTS)** | Monthly, 1992-present (35 yearly sheets) | **Yes, verified**: NSA 3-digit NAICS kinds of business sum exactly to "Retail sales, total"; + food services (722) = grand total | Excellent (34 yrs) | None in file; pair with BLS CPI (unverified) | US Gov work, public domain (unverified wording); xlsx, no login; **file is overwritten monthly** | Low (one xlsx) | **Hackathon pick** |
| 2 | **UCI Online Retail II** | Transactions -> daily, 2009-12-01 to 2011-12-09 | Yes by construction (revenue = qty x price, by country / product / customer) | Weak (1 prior year) | Unit price (L3 price) | **CC BY 4.0**, static zip on UCI, no login | Low (xlsx -> aggregate) | **Hackathon pick** |
| 3 | **Wikimedia pageviews (API)** | Daily/monthly, 2015-07-01-present | **Yes, verified**: desktop + mobile-web + mobile-app = all-access | Excellent (11 yrs) | Weak; holiday calendar or related articles | **CC0**; REST API, no key | Low-medium (many calls; pin is fragile) | Lecture (license-clean) |
| 4 | **M5 (Walmart)** | Daily, 1,941 days (2011-2016) (unverified count) | Yes, 12 levels, 42,840 series (unverified count) | Good (5 yrs) | **Best**: sell prices, SNAP days, events | **Unclear**: Kaggle origin; Zenodo mirror says CC BY 4.0 | Medium | Lecture, if the license is confirmed |
| 5 | **Australian domestic tourism (hts, Wickramasuriya et al.)** | Monthly, 1998-2016 (228 months) | Yes by construction: 304 bottom series = 76 regions x 4 purposes; state/zone codes in names | Good (19 yrs) | None | **License unverified**; static CSV on robjhyndman.com, no login | Low | Lecture backup |
| 6 | Eurostat retail trade `sts_trtu_m` | Monthly, long history | **No**: indices, not additive | Good | Cross-country | CC BY 4.0 (unverified wording); open API, no key (verified) | Low | L2/L3 support only |
| 7 | SEC XBRL (company financials) | Quarterly/annual, about 2009+ | **No** in the API (entity-level facts only) | Good | Other line items | Public; no key (verified); User-Agent required (unverified) | High for segments | Skip for now |
| 8 | Monash Forecasting Repository (Zenodo) | Various | No hierarchy metadata | Varies | Mostly none | Zenodo says CC BY 4.0, but the site says "research purpose only" | Low | Skip (weak business story) |
| 9 | Iowa Liquor Sales | Daily transactions, 2012-present | Yes (store/county/category/vendor) | Excellent | Bottle prices | CC0 per data.gov; **the API endpoint I tested no longer works** | Medium-high | Watch; unverified access |
| 10 | Favorita (Kaggle), Rossmann (Kaggle) | Daily, about 4.5 / 2.5 yrs (unverified) | Yes (store / family) | OK | **Rich**: promotions, oil, holidays / promo, holidays, customers | **Kaggle competition rules; login + rule acceptance** | n/a | **Exclude** (no redistribution, no login-free URL) |

### Recommendation

- **Hackathon (Sun 22 Nov 2026): US Census MRTS as the main KPI dataset, with UCI Online Retail II as the "company"
  dataset.** Both download without a login and have clean licenses. MRTS gives exact L1 drivers
  (e.g. "retail sales up, driven by nonstore retailers") and 30+ years of L2 history. Online Retail II reads like a
  client ("UK online retailer revenue by country/product") and has price for a simple L3. Because the MRTS xlsx is
  overwritten every month, snapshot it once (it is public domain) to an HF dataset repo or a pinned GitHub release and pin
  that copy's sha256. Or accept that the pin will break at the next release and record the date.
- **Lecture project (11 Dec): M5, if its license allows redistribution; otherwise Wikimedia pageviews plus MRTS with a
  BLS/holiday covariate.** M5 is the only candidate with exact hierarchy, multi-year history and real price/promo/event
  covariates, so it covers L1-L3 in one source. Its license is the blocker (see section 4). Wikimedia is the fully
  license-clean fallback: CC0, verified exact L1 by access method, 11 years for L2.

---

## 1. US Census Monthly Retail Trade (MRTS)

- **What:** Estimates of monthly retail and food services sales by kind of business, in millions of USD, from the Monthly
  Retail Trade Survey ([census.gov/retail](https://www.census.gov/retail/index.html)). Not adjusted and seasonally
  adjusted blocks.
- **File (verified today):** `https://www.census.gov/retail/mrts/www/mrtssales92-present.xlsx`. HTTP 200, no login,
  444 KB, 35 sheets `1992` ... `2026`, `last-modified: Tue, 17 Nov 2026`. sha256 today:
  `50dc85091a4b0e815acb08956d24fbdd3ba6ea139dd2ad4c8980bdaaa98793ae`. **It changes with each monthly release and
  revision.**
- **Series:** about 60-70 rows per block (totals, 3- to 6-digit NAICS); some deeper cells are suppressed `(S)`.
- **L1 (verified):** for Jan 2025, not adjusted: 441 + (442,443) + 444 + 445 + 446 + 447 + 448 + 451 + 452 + 453 + 454 =
  552,246 = "Retail sales, total"; + 722 food services (76,754) = 629,000 = "Retail and food services sales, total".
  Use the not-adjusted block for drivers. Seasonally adjusted components are usually adjusted separately and need not
  sum **(unverified for MRTS specifically)**. Deeper levels have suppressed cells, so stay at 3-digit.
- **L2:** 1992-present, so strong year-over-year comparisons, including the 2020 shock.
- **L3:** none in the file. Natural pairs are BLS CPI gasoline with gas-station sales, or the holiday calendar. The BLS
  public API is **unverified**.
- **API alternative:** `api.census.gov/data/timeseries/eits/mrts` now **requires an API key**
  ([Census developers page](https://www.census.gov/data/developers/data-sets/economic-indicators.html)). Prefer the xlsx.
- **License:** a US federal work, so public domain under 17 U.S.C. 105 **(unverified: the Census ToS page I read covers
  only API attribution: "This product uses the Census Bureau Data API but is not endorsed or certified...")**
  ([ToS](https://www.census.gov/data/developers/about/terms-of-service.html)).
- **Effort:** about 0.5 day. Parse 35 sheets with openpyxl (an extra requirement) and map NAICS codes to a tree.
- **Fit:** "US retail is up 3% YoY, driven by nonstore retailers; gasoline stations fell." Reads like a macro
  consulting deck.

## 2. UCI Online Retail II

- **What:** all transactions of a UK-based online retailer, 01/12/2009-09/12/2011. 1,067,371 rows, 8 columns: Invoice,
  StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country
  ([UCI page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)).
- **Download:** `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip` (HTTP 200 without login, verified),
  43.5 MB xlsx. It is a static archive, so a sha256 pin is stable. It is also available through `ucimlrepo` id 502.
- **Series you build:** daily/weekly revenue (Quantity x Price) in total and by country (about 40 countries, UK
  dominant, **count unverified**) and by product or category (no category field; only free-text Description).
- **L1:** exact by construction. Cancellations (invoices prefixed "C") have negative quantity; decide whether to net
  them **(prefix convention unverified)**.
- **L2:** only about 2 years, so one same-period-last-year comparison (Nov 2011 vs Nov 2010). It cannot support "the
  usual for the time of year".
- **L3:** unit price per item (price changes vs volume), number of customers or orders (mix). No promotions or weather.
- **License:** **CC BY 4.0** (UCI page). Redistribution is allowed with attribution.
- **Effort:** about 0.5 day (openpyxl or pandas read, clean, aggregate).
- **Fit:** the most "client-like" dataset: "December revenue up 12%, driven by the Netherlands and EIRE wholesale
  orders."

## 3. Wikimedia pageviews

- **What:** pageviews per project/article. REST endpoints
  `.../metrics/pageviews/aggregate/{project}/{access}/{agent}/{granularity}/{start}/{end}` and `.../per-article/...`.
  Data start on 1 July 2015 ([AQS docs](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html)).
  Older pagecounts back to Dec 2007 exist as dumps.
- **License:** *"All Analytics datasets are available under the Creative Commons CC0 dedication"*
  ([dumps readme](https://dumps.wikimedia.org/other/pageview_complete/readme.html)).
- **L1 (verified today):** en.wikipedia, agent=user, Jan 2024: desktop 2,844,940,099 + mobile-web 5,638,637,547 +
  mobile-app 201,177,828 = all-access 8,684,755,474 (exact). Further splits: agent (user/spider/automated, **sum
  unverified**), projects (languages). Per-article views do not sum to the project total.
- **L2:** 11+ years of daily data.
- **L3:** no native covariates. Pair an article with an event calendar (e.g. `Black_Friday_(shopping)`, verified to
  return monthly data), or a company article with its product launches.
- **Download:** no key. I sent a User-Agent; Wikimedia's UA/rate-limit policy is **unverified**. Pinning: API JSON for
  closed past ranges should be stable but is not guaranteed byte-identical. Snapshot to the HF Hub (CC0 allows it) or
  pin the immutable monthly `pageview_complete` dump files (large).
- **Effort:** about 0.5-1 day.
- **Fit:** medium. "Web traffic" is a real KPI ("visits fell 8%, driven by mobile web"), but it is not revenue.
  Monash/Kaggle web-traffic copies ([Zenodo 4656664](https://zenodo.org/records/4656664), 145,063 weekly series,
  2015-07-01-2017-09-05, CC BY 4.0) are derived from the Kaggle competition. Go to the CC0 source instead.

## 4. M5 (Walmart, M5 Forecasting competition)

- **What:** daily unit sales for Walmart items across 3 states / 10 stores / 3 categories / 7 departments, with
  `calendar` (events, SNAP days) and `sell_prices` (weekly prices per store-item). About 30,490 bottom series and
  42,840 across 12 aggregation levels, 2011-01-29 to 2016-06-19 **(all counts and dates from memory, unverified)**.
- **L1:** exact (unit sales sum up the hierarchy; revenue = units x weekly price, also additive).
- **L2:** about 5 years.
- **L3:** the best of all candidates: price changes, SNAP days, sporting/religious/national events.
- **License: unclear.** The original is Kaggle competition data (rules page not machine-readable; **unverified**).
  A Zenodo record ([10.5281/zenodo.12636070](https://zenodo.org/records/12636070)) hosts `m5-forecasting-accuracy.zip`
  (48.0 MB, md5 `86f57416a314197f40a17cc6fc60cbb4`, verified: HTTP 200, 48,009,163 bytes) with author "Kaggle" and
  license CC BY 4.0. Its description reads only "Taken over from Kaggle", so **the CC BY label is the uploader's and
  probably not authoritative**. Before the lecture project, read the M5 Rules tab on Kaggle (logged in) and the
  University of Nicosia / MOFC terms.
- **Effort:** about 1 day (wide CSV melt, join prices/calendar). The size is fine.
- **Fit:** excellent: "Food sales in CA up 6%, driven by store CA_3, coinciding with a SNAP week and a price cut."

## 5. Australian domestic tourism (hierarchical, visitor nights)

- **What:** monthly visitor nights, 1998-2016 (228 rows verified), 304 bottom series named by state/zone/region code +
  purpose (Hol, Vis, Bus, Oth), e.g. `AAAHol` (verified: 306 columns = Year, Month + 304). It is the dataset used in the
  `hts`/MinT reconciliation literature. Source: Tourism Research Australia National Visitor Survey **(attribution per
  the tsibble docs; license unverified)**.
- **Download:** `https://robjhyndman.com/data/TourismData_v3.csv`. HTTP 200, 643,891 bytes, sha256
  `d059b3d18036d116fba319e21bee9c02bac066ed9128a558c874b005ff553219`. It is a personal site, not versioned.
- **Related:** `tsibble::tourism`, quarterly, 23,408 rows, Region/State/Purpose, Trips (thousands), source TRA
  ([docs](https://tsibble.tidyverts.org/reference/tourism.html)). The tsibble package is **GPL-3**, and TimeNet's
  `make license-check` fails on copyleft dependencies. Read the CSV directly; do not depend on the R package.
- **L1:** exact by construction (groups by code prefix). **L2:** 19 years. **L3:** none.
- **Effort:** about 0.5 day. **Fit:** a tourism-board client ("Holiday nights in Queensland down, driven by the Gold
  Coast"). The license must be confirmed with TRA or the authors before contributing.
- Not recommended: `tsibbledata::aus_retail` (ABS 8501.0 table 11, 152 State x Industry series from 1982,
  [docs](https://tsibbledata.tidyverts.org/reference/aus_retail.html)), because ABS **ceased Retail Trade with the
  June 2025 release** and replaced it with the Monthly Household Spending Indicator
  ([ABS cessation notice](https://www.abs.gov.au/about/cessation-retail-business-survey-and-retail-trade-publication)).

## 6. Eurostat retail trade (`sts_trtu_m`)

- Monthly turnover/volume of retail trade by NACE and country. The JSON API
  (`ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_trtu_m?...`) answers without a key (verified;
  dataset updated 2026-11-17).
- **Values are indices (e.g. 2021 = 100), so components do not add to totals: no L1.** Useful for L2 and for an L3
  covariate (another country's index). License: Eurostat reuse policy, CC BY 4.0 **(unverified)**.
  The query response moves, so snapshot it.

## 7. SEC XBRL financial data

- `data.sec.gov/api/xbrl/{companyfacts,companyconcept,frames}`; *"These APIs do not require any authentication or API
  keys"*. Nightly `companyfacts.zip` bulk file
  ([SEC API page](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)). The frames call
  returned data today.
- The APIs aggregate only standard-taxonomy facts that apply to the whole entity, so **segment revenues (L1) are not
  in the API**. Getting them means parsing dimensional XBRL from individual filings. Fiscal calendars differ, tags vary
  by company, and there are about 60 quarters per company. A User-Agent header is required by SEC fair-access rules
  **(unverified)**.
- **Fit:** great story (real company revenue), poor verifiability for drivers. Skip unless time remains.

## 8. Monash Forecasting Repository

- Zenodo records are labelled CC BY 4.0 (e.g. Tourism Monthly, 366 series,
  [4656096](https://zenodo.org/records/4656096)), but [forecastingdata.org](https://forecastingdata.org/) says
  *"All datasets are intended to use only for research purpose"*, and many are re-hosts of upstream data (Kaggle,
  Dominick's) whose terms the label cannot override. The series are flat, often anonymised, and have no hierarchy keys.
  Not a good fit for L1.

## 9. Iowa Liquor Sales

- Spirits purchases by Iowa Class "E" licensees by product, store and date since 2012-01-01, with sale dollars and
  bottle prices. data.gov lists the license as CC0
  ([catalog](https://catalog.data.gov/dataset/iowa-liquor-sales)). That would give exact L1, 14 years of L2 and price
  L3, a great combination.
- **Access problem (verified today):** `data.iowa.gov/resource/m3tr-qhgy.json` and `/api/views/m3tr-qhgy.json` return
  the HTML of the new "Iowa Data Hub", not data, so the portal seems to have moved off Socrata. The full CSV is millions of rows
  (size unverified). Revisit if a stable bulk URL turns up.

## 10. Favorita (Kaggle "Store Sales") and Rossmann (Kaggle)

- Both have exactly the covariates we want: Favorita has `onpromotion`, oil price, holidays/events and transactions;
  Rossmann has Promo, StateHoliday, SchoolHoliday, Customers and competition distance **(from memory, unverified)**.
- **Both are Kaggle competition datasets.** Downloading needs a Kaggle login and accepting the rules. I could not read
  the rules pages (JS-rendered). Kaggle competition rules typically restrict data to competition use and forbid
  redistribution **(unverified for these two)**. A TimeNet connector cannot download them from a pinnable, login-free
  URL, and we should not re-host them. **Exclude** from contributed connectors. Local experiments only, if at all.

## Open items to verify before contributing

1. M5 license (Kaggle Rules tab + MOFC/University of Nicosia statement). This decides the lecture-project pick.
2. Census MRTS public-domain statement, and whether past monthly releases are archived at stable URLs (if they are,
   that replaces the HF snapshot).
3. Wikimedia API User-Agent/rate-limit policy, and whether agent values sum to all-agents.
4. Tourism CSV redistribution rights (Tourism Research Australia).
5. BLS CPI API access (no key, v1) as the MRTS L3 covariate.
