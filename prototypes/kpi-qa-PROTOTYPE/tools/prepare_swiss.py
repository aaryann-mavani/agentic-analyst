"""PROTOTYPE data prep: Swiss open data -> the standardized series format used by engine.py.
Reads raw downloads (path list in argv[1]); writes data/swiss_*.csv.  Rule (TimeNet): never fill missing data; incomplete periods are dropped,
and only the longest contiguous run is kept.  Format: date,value,p_<part>...,c_<covariate>..."""
import csv, collections, datetime as dt, os, sys
from zoneinfo import ZoneInfo
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
P = [l.strip() for l in open(sys.argv[1])]
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig")))
monday = lambda d: d - dt.timedelta(days=d.weekday())

def write(name, rows, parts, covs):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "value"] + ["p_" + p for p in parts] + ["c_" + c for c in covs])
        for r in rows: w.writerow(r)
    print(f"wrote {name}: {len(rows)} rows, {rows[0][0]} to {rows[-1][0]}")

def longest_run(keys, step):
    best, cur = [], []
    for k in keys:
        if cur and step(cur[-1], k): cur.append(k)
        else:
            cur = [k]
        if len(cur) > len(best): best = cur[:]
    return best
wk = lambda a, b: (b - a).days == 7

# 1. Basel monthly arrivals by origin: top 8 origins + rest (exactly additive)
bm = rd(P[0]); tot = collections.Counter(); by = collections.defaultdict(dict)
for r in bm: tot[r["herkunftsland"]] += int(r["anzankuenfte"]); by[r["datum"]][r["herkunftsland"]] = int(r["anzankuenfte"])
top = [k for k, _ in tot.most_common(8)]; months = sorted(by)
rows = []
for m in months:
    d = by[m]; parts = [d.get(k, 0) for k in top]; rest = sum(d.values()) - sum(parts)
    rows.append([m + "-01", sum(d.values())] + parts + [rest])
write("swiss_basel_arrivals.csv", rows, top + ["Other origins"], [])

# 2. Basel hotels: daily -> weekly (complete weeks only). nights by hotel category; occupancy as its own series
bd = rd(P[1]); day = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0, 0]))
cats = sorted({r["hotelkategorie"] for r in bd})
for r in bd:
    d = dt.date.fromisoformat(r["datum"]); a = day[d][r["hotelkategorie"]]
    a[0] += int(r["anzlogiernaechte"]); a[1] += int(r["anzzimmerverfuegbarundgeoeffnet"]); a[2] += int(r["anzzimmerbelegungen"])
weeks = collections.defaultdict(list)
for d in day: weeks[monday(d)].append(d)
full = sorted(w for w, ds in weeks.items() if len(ds) == 7 and all(len(day[d]) == len(cats) for d in ds))
full = longest_run(full, wk)
rows_n, rows_o = [], []
for w in full:
    ds = weeks[w]; n = [sum(day[d][c][0] for d in ds) for c in cats]; av = sum(day[d][c][1] for d in ds for c in cats); oc = sum(day[d][c][2] for d in ds for c in cats)
    rows_n.append([w.isoformat(), sum(n)] + n); rows_o.append([w.isoformat(), oc / av])
write("swiss_basel_hotel_nights.csv", rows_n, cats, [])
write("swiss_basel_hotel_occupancy.csv", rows_o, [], [])

# 3. Zuerich pedestrians (Bahnhofstrasse Mitte): hourly -> weekly; keep only weeks with all 168 hours, all measured, none flagged unverified
zp = [r for r in rd(P[2]) if r["location_id"] == "329"]; tz = ZoneInfo("Europe/Zurich")
hours = collections.defaultdict(list)
for r in zp:
    t = dt.datetime.fromisoformat(r["timestamp"].replace("Z", "+00:00")).astimezone(tz)
    hours[monday(t.date())].append((t, r))
bad = collections.Counter(); good = []
for w, rs in hours.items():
    if len({t for t, _ in rs}) < 168 - 1: bad["incomplete"] += 1; continue   # DST weeks have 167/169 local hours
    if any(r["collection_type"] != "measured" or r["unverified"] != "False" for _, r in rs): bad["not measured/unverified"] += 1; continue
    good.append(w)
print("pedestrian weeks: total", len(hours), "usable", len(good), "dropped", dict(bad))
good = longest_run(sorted(good), wk); rows = []
for w in good:
    rs = [r for _, r in hours[w]]; temp = [float(r["temperature"]) for r in rs if r["temperature"]]
    rain = sum(1 for r in rs if r["weather_condition"] in ("rain", "drizzle", "snow", "thunderstorm", "sleet"))
    rows.append([w.isoformat(), sum(int(r["pedestrians_count"]) for r in rs), sum(temp) / len(temp), rain])
write("swiss_zh_pedestrians.csv", rows, [], ["Mean temperature C", "Rainy hours"])
print(" weather labels seen:", sorted({r["weather_condition"] for r in zp}))

# 4. BFE electricity: daily -> weekly consumption (GWh) with weekly mean day-ahead price as covariate
bc = {dt.date.fromisoformat(r["Datum"]): float(r["Landesverbrauch_GWh"]) for r in rd(P[3])}
bp = {dt.date.fromisoformat(r["Datum"]): float(r["Baseload_EUR_MWh"]) for r in rd(P[4])}
ws = collections.defaultdict(list)
for d in bc: ws[monday(d)].append(d)
full = longest_run(sorted(w for w, ds in ws.items() if len(ds) == 7 and all((d in bp) for d in ds)), wk)
rows = [[w.isoformat(), sum(bc[d] for d in ws[w]), sum(bp[d] for d in ws[w]) / 7] for w in full]
write("swiss_bfe_electricity.csv", rows, [], ["Day-ahead price EUR/MWh"])
