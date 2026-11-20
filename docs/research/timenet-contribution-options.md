# TimeNet contribution options (researched 2026-11-19)

Sources: `gh` (read-only) against OpenTSLM/TimeNet at `main` 7ad336b (2026-11-18), a shallow clone,
challenge.timenet.ai, census.gov, ALFRED. "UNCONFIRMED" marks anything not checked directly.

## Recommendation

**Build a US Census Monthly Retail Trade connector that reads vintage-pinned ALFRED CSVs and adds
code-computed QA tasks (options a and c together). In parallel, finish the second revision of our
Context is Key PR (#788).**

- **Not a duplicate.** No PR or issue (open or closed) mentions Census retail, MRTS, FRED, M5,
  Walmart, Online Retail or "sales" as a dataset. 725 PRs and 2 issues were searched, both titles
  and full text. Business and retail data is absent from the merged catalog.
- **The overwrite problem is solved without hosting anything.** ALFRED serves a fixed vintage at
  `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<SERIES>&vintage_date=YYYY-MM-DD`. It
  needs no API key. Two downloads of the same URL gave the same sha256, so the URL works with
  `Artifact(url, path, sha256=...)` (see section 5).
- **The computed QA tasks have precedent.** #469's QA task (higher/lower/within, computed from
  means) and the merged `timenet/test_mean` connector (a label computed from the signal) both
  derive answers from the series. The category-to-total structure makes "which component drove
  the change" answerable, and that is the distinctive part.
- **Timing.** The Round 1 deadline is **Nov 22, 2026, 11:59 pm PST**. The rules ask for "a link to
  your PR adding your dataset to TimeNet". An opened PR appears to be enough (section 4).
- **CiK #788 is the cheapest win.** It is already open upstream. A maintainer (TimoStoff, Nov 16)
  requested changes but wrote: "will be happy to accept in the second revision". If time runs
  short, prioritise that revision. It is the PR most likely to be merged.
- **Avoid Time-MMD.** Three PRs already target `adityalab/time-mmd` (section 1). Another one would
  collide on the same dataset id and folder.
- **UCI Online Retail II** is unclaimed, but it is a fallback. It is transaction-level, so any
  series is our own aggregation. It also has no hierarchy that sums to totals, which the QA
  idea needs.

## 1. Time-MMD PRs #469 and #637

| | #469 (haznai) | #637 (kilibenz) |
|---|---|---|
| Title | feat(connectors): add Time-MMD Economy and Energy tasks | Time-MMD connector |
| Opened / last commit | 2026-10-14 / 2026-10-14 (1 commit) | 2026-11-02 / 2026-10-31 (4 commits) |
| Status | Open, MERGEABLE, review required, label `area:connectors` | Open, **CONFLICTING**, review required |
| CI | Fork runs on 2026-10-14 **failed** (3 runs) | Fork run is `action_required` (a maintainer has not approved it) |
| Reviews/comments | **None** | **None** |
| Domains | Economy (Census goods trade: exports, imports, OT = balance), Energy (EIA gasoline: OT plus 8 regions) | Energy (EIA gasoline), Environment (NY AQI, daily) |
| Tasks | 1941 QA tasks (compare the mean of the first 8 and last 8 of 64 OT values, answer `higher`/`lower`/`within`) and 1941 next-value forecasts | `ForecastingTask` windows following the MM-TSFlib protocol (70/10/20 split). Energy: lookback 36, horizons 12/24/36/48. Environment: lookback 96, horizons 48/96/192/336. Text is attached as `input_annotations` |
| Text | report/search fact and preds kept as per-Record annotations; tasks do not use them | facts and long/short predictions as interval annotations, fed into the forecasting tasks |
| Extras | `shape.svg`, gists for reproduction and model evaluation (ChatTS, OpenTSLM) | `sources.py` and `tasks.py` split, updates `docs/connectors.md` |

- Both use the same path, `datasets/adityalab/time_mmd/`. An earlier PR, **#286** (FeherF, Energy
  and Environment), was closed on 2026-09-24 with no comments.
- **No maintainer has said which PR will be merged.** Neither PR has any review activity. Merging
  one would conflict with the other.
- **Uncovered Time-MMD domains:** Agriculture, Climate, Health, Security, Social Good, Traffic
  (Time-MMD has 9 domains). A complementary PR is technically possible, but it would have to
  extend whichever PR wins, and we cannot know which in 3 days. We could stack a Time-MMD QA task
  set on top of #469, but #469 already ships a simple QA task. **Not recommended.**

## 2. Duplicate search (titles and full text of all PRs and issues)

| Term | Hits |
|---|---|
| Census | Only #469, which uses Census *goods trade* through Time-MMD, not retail |
| retail | Only #286, which uses EIA *retail gasoline price* |
| Online Retail, Walmart, FRED | none |
| M5 | No dataset PR (only unrelated perf/test PRs) |
| sales | Only #638 TSAQA (merged); the keyword match is incidental |
| UCI | #608 UCI hydraulic, #341/342/343 UCI HAR/mHealth/PAMAP2 (all open). Not Online Retail |
| Context is Key | **#788 by bwinner1 (ours), open, changes requested** |

- Merged connectors: timenet/{hello_world, test_mean}, opentslm/{har_cot, sleep_cot},
  physionet/{ptb_xl, sleep_edfx, ecg_qa_cot}, bash_lab/sensorcaps, tsaqa/tsaqa_benchmark,
  datadog/{arfbench, arfbench_charts}, chengsenwang/tsqa. None of them is business or retail data.
- Dozens of other connector PRs are open (e.g. M4-Caption #790, TimeSeriesExam #799, swiss-grid
  #795). None covers retail or sales.
- **Conclusion:** options (a), (b) and (c) are all unclaimed.

## 3. Repo rules (CONTRIBUTING.md, AGENTS.md, add-dataset-connector skill)

**Changing sources.** The skill says: "Pin every source file outside the Hub. Use a versioned or
commit-pinned URL (never a moving branch such as `master`), and pass its `sha256` to
`ensure_archive` / `Artifact`." Hub sources pin a commit through `SOURCE_REVISION`.

- **No written rule says where a snapshot may be hosted.** The merged precedent is OpenTSLM's
  connectors (har_cot, sleep_cot, ecg_qa_cot), which download ETH **polybox share links** with a
  pinned sha256.
- A Census Excel snapshot could therefore go on a share link or a HF dataset repo. That is
  UNCONFIRMED as acceptable for a third-party contributor.
- ALFRED vintages avoid the question.

**Data integrity.** AGENTS.md says: "Never write code that fills in missing data or synthetically
repairs data issues". On a data issue, raise `TimeNetConnectorError` or `TimeFValidationError`.

**License.** The `License` enum offers MIT, Apache-2.0, BSD-2/3, GPL-3.0, LGPL-3.0, MPL-2.0,
CC0-1.0, CC-BY-4.0, CC-BY-SA-4.0, CC-BY-NC-4.0, ODC-By-1.0, ODbL-1.0, OTHER and NONE.

- There is **no "public domain" value**. `OTHER` "requires a `license_url` on the card". US
  federal works would be `OTHER` plus a Census or FRED URL, or arguably `CC0-1.0`
  (UNCONFIRMED which one maintainers prefer).
- Online Retail II maps cleanly to `CC-BY-4.0`.
- Contributions are MIT, inbound equals outbound.
- `domains` values include `economics` and `finance`. There is no "retail" or "business" domain.

**Task types:** `ClassificationTask` (needs a `LabelSet`), `AnswerTask` (free text),
`ScalarPredictionTask` (float plus unit), `TemporalLocalizationTask`, `ForecastingTask`,
`TSEditingTask`, `TSGenerationTask`, `TSCorrespondenceTask`. Any of them can carry a `rationale`.

- There is no dedicated change-point type. Use `TemporalLocalizationTask` (a span) or
  `ClassificationTask` over a `scope`.
- For our QA:
  - direction: `ClassificationTask` with up/down/flat
  - largest change and when: `TemporalLocalizationTask`, or `ScalarPredictionTask` for the size
  - same period last year: `ScalarPredictionTask` with a unit
  - driving component: `ClassificationTask` with category labels

**Computed QA tasks.** No rule forbids them. The skill frames task choice by "the kind of answer
the dataset supervises", so a reviewer may ask us to justify derived tasks.

- Precedents: the merged `timenet/test_mean` (a label computed from the signal) and #469 (QA
  computed from means). The merged "recordings with QA tasks" (#163, ecg_qa_cot) uses upstream QA,
  not computed QA.
- Document the thresholds and formulas in the connector README, as #469 does.

**Process:**

- HARD GATE: confirm the id, source, task and example row before coding.
- Fixture-based offline test in `<org>/<name>/tests/`.
- `make check`, `make lint-fix`, `make test`, `make test-connectors`.
- Conventional Commits, label `area:connectors`.
- The PR body should state which checks ran.

**Pending policy PRs (open, not binding yet):**

- #582 would require a `VERIFICATION.md` (a 54-item checklist) per connector.
- #675 defines the connector layout (`source.py`, `records.py`, `tasks.py`).
- Following #675's layout is low cost.

## 4. Hackathon rules (challenge.timenet.ai; README banner from #775)

The repo has no rules beyond the README banner and link. Discussions are disabled and there are
no pinned issues.

**Submission and deadlines:**

- Dataset: "A link to your PR adding your dataset to TimeNet." The site **does not say the PR must
  be merged**, so an opened PR appears sufficient (UNCONFIRMED; ask in the OpenTime Discord).
- Round 1 closes Nov 22, 2026, 11:59 pm PST. Judging is the following Monday. More rounds will be
  announced in Discord. Teams may enter several rounds "with a different use case each time".
- A team is 2-4 people, all registered. Existing projects are allowed if what was added during the
  hackathon is clearly identified.

**What else is required beyond the PR:**

- A pitch or demo link.
- Public X **and** LinkedIn posts with metrics screenshots.
- A Discord post.
- The submission form.
- The README banner says to also "train or fine-tune a Temporal AI Model". Judging includes
  "Results and evaluation", so a small model run (e.g. OpenTSLM or ChatTS on the QA tasks)
  matters. #469's gists show what that looks like.

**Judging criteria:** use case and impact, technical execution, data and TimeNet, results and
evaluation, showcase and social engagement (post traction counts).

**Duplicates:** the site has **no rule about duplicate datasets or claiming a dataset**.

**Implication for #788:** CiK #788 was opened on Nov 16, during the hackathon, so it may already
count as our dataset PR. A second use case could go to a later round.

## 5. Census MRTS: stable sources and license

- **Census Excel** (`census.gov/retail/mrts/www/mrtssales92-present.xlsx`): Last-Modified is
  2026-11-17, which confirms it is overwritten. Its sha256 will change monthly.
- **Census EITS API** (`api.census.gov/data/timeseries/eits/mrts`, and `.../marts` for advance
  estimates):
  - **Requires an API key.** A request without one redirects to `missing_key.html`.
  - It serves current revised values, and no vintage parameter was found (UNCONFIRMED).
  - It is not byte-stable, so a pinned sha256 is impossible.
- **ALFRED vintages (recommended):**
  - Tested: `alfredgraph.csv?id=RSXFS&vintage_date=2025-01-15` returns
    `observation_date,RSXFS_20250115` from 1992-01 onward.
  - Two fetches gave the same sha256 (`aefd0300...bdf11`).
  - Category series also work with vintages: MRTSSM44000USS (retail total), MRTSSM4541USS
    (nonstore), MRTSSM448USS (clothing), RSAFS (retail and food services, advance).
  - At vintage 2025-01-15, the MRTS series end 2024-10 and the advance RSAFS ends 2024-11.
  - Long-term byte stability of the CSV export is UNCONFIRMED. ALFRED could change formatting. If
    it does, the sha256 check fails loudly, as intended.
  - Fallback: host a snapshot on a share link or HF dataset with a sha256, following the polybox
    precedent.
- **Additivity:** check before promising "components sum to totals".
  - Census generally says seasonally adjusted components need not add exactly to totals.
    Not-seasonally-adjusted series (`...USN`) should add, up to rounding and unpublished
    residual categories (UNCONFIRMED).
  - Raise an error on mismatch, or store the residual as its own signal. Do not "repair" it.
- **License:**
  - Census data is a US federal work and in the public domain (17 U.S.C. section 105).
  - ALFRED tags the series "Public Domain: Citation Requested". FRED's page also shows a generic
    "Data in this graph are copyrighted" banner, so cite the U.S. Census Bureau and FRED.
  - Card: `license: OTHER` with `license_url` pointing to the Census terms, or `CC0-1.0`
    (maintainer preference UNCONFIRMED).
- **UCI Online Retail II:** static URL
  `https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip` returns HTTP 200. Pin its
  sha256. License CC BY 4.0.

## Suggested 3-day plan

1. **Day 1:**
   - Address the #788 review comments: pydantic or typed rows, named types, reuse
     `time_offsets_from_datetimes` and `axis_for_offsets`, re-check the timestamp arithmetic.
   - Draft the MRTS id (e.g. `census/monthly-retail-trade`), the category list, the vintage date
     and the task sketch.
2. **Day 2:**
   - Write the MRTS connector: one Record, one Signal per category (NSA and/or SA), month axis.
   - Write the computed QA tasks with documented formulas, plus a fixture test.
3. **Day 3:**
   - Build round-trip, run `make check`, `make test` and `make test-connectors`, and open the PR.
   - Run a small model evaluation, write the posts, submit before Nov 22, 23:59 PST.
