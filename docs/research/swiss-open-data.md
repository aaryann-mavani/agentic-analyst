# Swiss open data used by the prototype

Acquired 2026-11-20 through public APIs. **No API key was needed** for any of them.
Only complete periods are kept, nothing is filled in, and only the longest contiguous run is used (`prototypes/kpi-qa-PROTOTYPE/tools/prepare_swiss.py`).

| Series (as in the dashboard) | Source and API | Raw size | Prepared as | Terms (from the opendata.swiss catalogue) |
|---|---|---|---|---|
| Basel hotel arrivals by origin | Canton Basel-Stadt, `data.bs.ch` Opendatasoft API, dataset `100107`, `/exports/csv` | 10,881 rows, 142 months, Jan 2015 to Oct 2026, 77 origin labels | Monthly total; 8 largest origins plus "Other origins" so components add up exactly | **Not checked** |
| Basel hotel overnight stays and occupancy | `data.bs.ch` dataset `100106` | 17,288 rows, 4,322 days, 4 hotel categories, no gaps | Weekly (Mon to Sun), 616 weeks; nights by category (additive) and occupancy = occupied / available rooms | **Not checked** |
| Zurich Bahnhofstrasse (Mitte) pedestrians | City of Zurich, CKAN `data.stadt-zuerich.ch`, dataset `hystreet_fussgaengerfrequenzen` (CSV) | 180,312 hourly rows, 4 sensors, 2021-09 to now | Weekly, Mitte sensor only; 267 weeks; covariates: mean temperature, rainy hours | `terms_by` (attribution) |
| Swiss electricity consumption | BFE, `bfe-ogd.ch/ogd103_stromverbrauch_swissgrid_lv_und_endv.csv` | 3,560 days, 2017-01-01 to 2026-09-30 | Weekly Landesverbrauch (GWh), 508 weeks | **`terms_by_ask`: attribution, and permission must be requested for commercial use** |
| Day-ahead power price (covariate) | BFE, `bfe-ogd.ch/ogd106_preise_strom_boerse.csv` | 3,609 days | Weekly mean EUR/MWh | **`terms_by_ask`** |

Discovery: `ckan.opendata.swiss/api/3/action/package_search` returns 403 to curl's default client string; it answers a plain generic client name.
KOF barometer and Zurich commercial-register entries were found on the catalogue (`kof-konjunkturbarometer`, `eintragungen-im-handelsregister-des-kantons-zurich`) but not loaded: the barometer is an index, the register series is about 70 quarterly rows.

## Data-quality facts found while preparing
- Basel arrivals: the label "Mittelamerika, Karibik" exists for only 89 of 142 months (a category was renamed or split), and the other origin buckets ("Übriges ...") are residuals. Components were rebuilt as top 8 plus the remainder so they add up exactly.
- Pedestrians: four sensors cover overlapping segments of the street, so they are not additive; only Mitte is used. 2 of 269 weeks were incomplete and dropped.
- Timestamps are UTC; weeks were cut on Europe/Zurich local time.
- BFE price runs to 2026-11-18, consumption to 2026-09-30; the weekly series is limited to weeks where both exist.

## Still to do before any of this goes into a TimeNet connector or a public post
- Check licences for the two Basel datasets and request permission for the BFE data if used commercially.
- Check whether any of these are already in TimeNet or its open PRs (only retail and sales data were searched).
