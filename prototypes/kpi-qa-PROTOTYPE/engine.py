"""PROTOTYPE engine: standardized series, computed answers, and a checker for free text.
Pure logic (stdlib only). Loader raises on gaps/duplicates (TimeNet rule: never fill data)."""
import csv, math, os, re
from datetime import date, timedelta
from statistics import mean, median, pstdev

HERE = os.path.dirname(os.path.abspath(__file__))
MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
FULL = ["january","february","march","april","may","june","july","august","september","october","november","december"]

# Standardization: every domain becomes the same shape.  Units are labels only (not converted).
SPECS = {
    "economy": dict(file="Economy.csv", name="US trade deficit", unit="USD millions (assumed)", freq="M",
                    date="date", value=lambda r: -float(r["OT"]), parts={"Imports": lambda r: float(r["Imports"]), "Exports (inverted)": lambda r: -float(r["Exports"])}),
    "energy": dict(file="Energy.csv", name="US retail gasoline price (OT)", unit="USD per gallon (assumed)", freq="W",
                   date="date", value=lambda r: float(r["OT"]), parts=None),
    "traffic": dict(file="Traffic.csv", name="Traffic volume (OT)", unit="not documented", freq="M",
                    date="date", value=lambda r: float(r["OT"]), parts=None),
    "agriculture": dict(file="Agriculture.csv", name="Broiler price (OT)", unit="not documented", freq="M",
                        date="date", value=lambda r: float(r["OT"]), parts=None),
}

BIZ = {
 "swiss_basel_arrivals": dict(who="Basel tourism board, hotel association, or a consultancy advising Basel hotels",
   case="Where do visitors come from, which markets drive recovery after the 2020 collapse, and what to expect next quarter.",
   qs=["Which origins drove the latest month?", "Was April 2020 unusual?", "Is this a record?", "What is the forecast?"]),
 "swiss_basel_hotel_nights": dict(who="Hotel group revenue managers, or a consultancy advising on pricing and capacity",
   case="Weekly overnight stays by hotel category: is a weak week seasonal or a real drop, which category drove it, what is next. Fairs and events are outside the data, so the system must decline to explain them.",
   qs=["What happened in the latest week?", "Which hotel category drove the change?", "Why did it change?", "What is the forecast?"]),
 "swiss_basel_hotel_occupancy": dict(who="Hotel managers and asset owners",
   case="Occupancy against the same week last year, the capacity KPI hotels are steered on.",
   qs=["How does it compare with a year ago?", "Is this normal for the time of year?", "Is this a record?"]),
 "swiss_zh_pedestrians": dict(who="Retail chains, landlords and consultants advising on Bahnhofstrasse sites",
   case="Footfall as a sales proxy: is a weak week weather or demand, how does rain and temperature move with it, how many staff for the coming weeks.",
   qs=["What moved with it?", "Is this normal for the time of year?", "How does it compare with a year ago?", "What is the forecast?"]),
 "swiss_bfe_electricity": dict(who="Utilities, energy traders and consultants advising industrial buyers",
   case="National electricity demand against the day-ahead price: is demand normal for the season, does price move with demand, what is the near-term outlook. The price data's terms require asking permission for commercial use.",
   qs=["What moved with it?", "Is this normal for the time of year?", "What is the forecast?", "Is this a record?"]),
}
for _k, _f, _n, _u, _fr, _kind in [
    ("swiss_basel_arrivals", "swiss_basel_arrivals.csv", "Basel hotel arrivals, all origins", "guests per month", "M", "count"),
    ("swiss_basel_hotel_nights", "swiss_basel_hotel_nights.csv", "Basel hotel overnight stays", "nights per week", "W", "count"),
    ("swiss_basel_hotel_occupancy", "swiss_basel_hotel_occupancy.csv", "Basel hotel room occupancy", "share of rooms, weekly", "W", "ratio"),
    ("swiss_zh_pedestrians", "swiss_zh_pedestrians.csv", "Zurich Bahnhofstrasse (Mitte) pedestrians", "people per week", "W", "count"),
    ("swiss_bfe_electricity", "swiss_bfe_electricity.csv", "Swiss national electricity consumption", "GWh per week", "W", "count")]:
    pass
SWISS = [
    ("swiss_basel_arrivals", "swiss_basel_arrivals.csv", "Basel hotel arrivals, all origins", "guests per month", "M", "count"),
    ("swiss_basel_hotel_nights", "swiss_basel_hotel_nights.csv", "Basel hotel overnight stays", "nights per week", "W", "count"),
    ("swiss_basel_hotel_occupancy", "swiss_basel_hotel_occupancy.csv", "Basel hotel room occupancy", "share of rooms, weekly", "W", "ratio"),
    ("swiss_zh_pedestrians", "swiss_zh_pedestrians.csv", "Zurich Bahnhofstrasse (Mitte) pedestrians", "people per week", "W", "count"),
    ("swiss_bfe_electricity", "swiss_bfe_electricity.csv", "Swiss national electricity consumption", "GWh per week", "W", "count")]
for k, f, n, u, fr, kind in SWISS:
    SPECS[k] = dict(prepared=f, name=n, unit=u, freq=fr, kind=kind, biz=BIZ[k])

class Series:
    def __init__(s, key, spec, dates, values, parts, cov=None):
        s.key, s.name, s.unit, s.freq = key, spec["name"], spec["unit"], spec["freq"]
        s.kind = spec.get("kind", "count"); s.biz = spec.get("biz")
        s.dates, s.values, s.parts, s.cov = dates, values, parts, cov
        s.pct_ok = all(v > 0 for v in values)
    def label(s, i):
        d = date.fromisoformat(s.dates[i])
        return f"{MON[d.month-1]} {d.year}" if s.freq == "M" else f"week of {s.dates[i]}"
    def season_key(s, i):
        d = date.fromisoformat(s.dates[i]); return d.month if s.freq == "M" else min(d.isocalendar()[1], 52)
    @property
    def year_lag(s): return 12 if s.freq == "M" else 52
    @property
    def period(s): return "month" if s.freq == "M" else "week"

def load_prepared(key, sp):
    with open(os.path.join(HERE, "data", sp["prepared"]), newline="") as f: rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: r["date"])
    step = (lambda a, b: (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7])) == 1) if sp["freq"] == "M" \
        else (lambda a, b: (date.fromisoformat(b) - date.fromisoformat(a)).days == 7)
    for a, b in zip(rows, rows[1:]):
        if not step(a["date"], b["date"]): raise ValueError(f"{key}: gap or duplicate between {a['date']} and {b['date']}")
    vals = [float(r["value"]) for r in rows]
    pk = [c for c in rows[0] if c.startswith("p_")]; ck = [c for c in rows[0] if c.startswith("c_")]
    parts = {c[2:]: [float(r[c]) for r in rows] for c in pk} or None
    if parts:
        for j, v in enumerate(vals):
            if abs(sum(p[j] for p in parts.values()) - v) > 1e-6 * max(1, abs(v)): raise ValueError(f"{key}: components do not add up at {rows[j]['date']}")
    return Series(key, sp, [r["date"] for r in rows], vals, parts, {c[2:]: [float(r[c]) for r in rows] for c in ck} or None)

def load(key):
    sp = SPECS[key]; rows = []
    if "prepared" in sp: return load_prepared(key, sp)
    with open(os.path.join(HERE, "data", sp["file"]), newline="") as f:
        for r in csv.DictReader(f):
            try: rows.append((r[sp["date"]][:10], sp["value"](r), {k: g(r) for k, g in (sp["parts"] or {}).items()}))
            except ValueError: raise ValueError(f"{key}: non-numeric value at {r[sp['date']]} (not filled in)")
    rows.sort(key=lambda t: t[0])
    step = (lambda a, b: (int(b[:4]) * 12 + int(b[5:7])) - (int(a[:4]) * 12 + int(a[5:7])) == 1) if sp["freq"] == "M" \
        else (lambda a, b: (date.fromisoformat(b) - date.fromisoformat(a)).days == 7)
    for a, b in zip(rows, rows[1:]):
        if not step(a[0], b[0]): raise ValueError(f"{key}: gap or duplicate between {a[0]} and {b[0]}")
    parts = {k: [r[2][k] for r in rows] for k in rows[0][2]} or None
    return Series(key, sp, [r[0] for r in rows], [r[1] for r in rows], parts)

def fmtd(S, ch):
    return f"{abs(ch)*100:.1f} points" if S.kind == "ratio" else fmt(S, abs(ch))

def fmt(S, x):
    if S.kind == "ratio": return f"{x*100:.1f}%"
    if S.key == "economy": return f"${abs(x)/1000:.1f}B"
    return f"{x:,.2f}" if abs(x) < 1000 else f"{x:,.0f}"

# ---- primitives (also used by the Check) ----
def change(S, i): return S.values[i] - S.values[i-1]
def pct(S, i): return S.values[i] / S.values[i-1] - 1 if S.pct_ok else None
def direction(S, i): return "up" if change(S, i) > 0 else "down"
def streak(S, i):
    d, n = direction(S, i), 0
    while i - n - 1 >= 0 and direction(S, i - n) == d: n += 1
    return d, n

def recompute(S, op, i):
    return {"level": lambda: S.values[i], "change": lambda: change(S, i), "pct": lambda: pct(S, i),
            "direction": lambda: direction(S, i), "streak": lambda: streak(S, i)[1]}[op]()

def seasonal_stats(S, i, years=10, vals=None):
    vals = S.values if vals is None else vals
    k = S.season_key(i)
    idxs = [j for j in range(1, i) if S.season_key(j) == k][-years:]
    f = lambda j: vals[j] / vals[j-1] - 1
    past = [(j, f(j)) for j in idxs]; xs = [v for _, v in past]
    med = median(xs); mad = median([abs(v - med) for v in xs]) * 1.4826 or pstdev(xs) or 1e-9
    return past, med, mad, (f(i) - med) / mad, f(i)

# ---- computed answers: each returns dict(title, level, text, claims, path) ----
def A(title, level, text, claims, path, declined=False): return dict(title=title, level=level, text=text, claims=claims, path=path, declined=declined)
def C(part, op, i, asserted): return dict(part=part, op=op, i=i, asserted=asserted)

def what_happened(S, i):
    ch, p = change(S, i), pct(S, i); w = direction(S, i)
    ptxt = f" ({p*100:+.1f}%)" if p is not None else ""
    text = f"{S.name}: {S.label(i)} was {fmt(S, S.values[i])}, {w} {fmtd(S, ch)}{ptxt} from the previous {S.period}."
    return A("What happened?", "description", text, [C(w, "direction", i, w), C(fmt(S, ch), "change", i, abs(ch))],
             [f"{S.label(i)}: {S.values[i]:,.3f}", f"{S.label(i-1)}: {S.values[i-1]:,.3f}", f"change = {ch:+,.3f}" + (f"; % = {p*100:+.2f}%" if p is not None else "")])

def when_started(S, i):
    d, n = streak(S, i)
    text = f"{S.name} has been {d} for {n} {S.period}{'s' if n != 1 else ''} in a row, up to {S.label(i)}."
    return A("When did it start?", "temporal localization", text, [C(d, "direction", i, d), C(str(n), "streak", i, n)],
             [f"{S.label(i-k-1)} -> {S.label(i-k)}: {change(S, i-k):+,.3f}" for k in range(min(n + 1, 6)) if i - k - 1 >= 0])

SEAS_Z = 2.5
def seasonal(S, i):
    past, med, mad, z, cur = seasonal_stats(S, i)
    verdict = "in line with" if abs(z) <= SEAS_Z else ("larger than" if z > 0 else "smaller than")
    text = (f"The {S.label(i)} move of {cur*100:+.1f}% is {verdict} the usual move for this time of year "
            f"(typical {med*100:+.1f}% over the last {len(past)} years; robust z = {z:+.1f}; in line means |z| <= {SEAS_Z}).")
    path = [f"{S.label(j)}: {v*100:+.2f}%" for j, v in past] + [f"median = {med*100:+.2f}%, robust spread = {mad*100:.2f}%", f"z = ({cur*100:+.2f} - {med*100:+.2f}) / {mad*100:.2f} = {z:+.2f}"]
    if S.parts:
        comp = {"Imports": S.parts["Imports"], "Exports": [-x for x in S.parts["Exports (inverted)"]]} if S.key == "economy" else S.parts
        for name, vals in comp.items():
            _, m2, d2, z2, c2 = seasonal_stats(S, i, vals=vals)
            path.append(f"component {name}: move {c2*100:+.1f}%, typical {m2*100:+.1f}%, z = {z2:+.1f}")
            if abs(z2) > SEAS_Z and abs(z) <= SEAS_Z:
                text += f" But {name} on its own is unusual ({c2*100:+.1f}% against a typical {m2*100:+.1f}%, z = {z2:+.1f}); the total hides it."
    return A("Is this normal for the time of year?", "level 2: seasonal comparison", text, [], path)

def yoy(S, i):
    j = i - S.year_lag
    if j < 0: return A("Versus last year", "level 2", "Not enough history for a year-ago comparison.", [], [], True)
    ch = S.values[i] - S.values[j]; p = S.values[i] / S.values[j] - 1 if S.pct_ok else None
    text = f"{S.label(i)} is {fmt(S, S.values[i])}, {'up' if ch > 0 else 'down'} {fmtd(S, ch)}" + (f" ({p*100:+.1f}%)" if p is not None else "") + f" on {S.label(j)}."
    return A("Versus a year ago", "level 2: same period last year", text, [C("up" if ch > 0 else "down", "direction", i, "up" if ch > 0 else "down")],
             [f"{S.label(i)}: {S.values[i]:,.3f}", f"{S.label(j)}: {S.values[j]:,.3f}", f"change = {ch:+,.3f}"])

def extremes(S, i):
    v = S.values[i]; hi = lo = 0
    for k in range(i - 1, -1, -1):
        if S.values[k] < v: hi += 1
        else: break
    for k in range(i - 1, -1, -1):
        if S.values[k] > v: lo += 1
        else: break
    if hi >= 12: text = f"{S.label(i)} is the highest in {hi} {S.period}s (since {S.label(i-hi-1) if i-hi-1>=0 else 'the start'})."
    elif lo >= 12: text = f"{S.label(i)} is the lowest in {lo} {S.period}s."
    else: text = f"{S.label(i)} is neither a recent high nor low (highest in {hi}, lowest in {lo} {S.period}s)."
    mx = max(range(i + 1), key=lambda k: S.values[k]); mn = min(range(i + 1), key=lambda k: S.values[k])
    return A("Is this a record?", "temporal localization", text, [],
             [f"value {v:,.3f}; consecutive lower {S.period}s before: {hi}; consecutive higher: {lo}", f"all-time high to date: {S.label(mx)} = {S.values[mx]:,.3f}", f"all-time low to date: {S.label(mn)} = {S.values[mn]:,.3f}"])

def drivers(S, i):
    if not S.parts: return A("What drove it?", "level 1: driver", f"{S.name} has no components in this dataset, so there is nothing to split it into.", [], [], True)
    ch = change(S, i); mv = {k: v[i] - v[i-1] for k, v in S.parts.items()}
    mv = dict(sorted(mv.items(), key=lambda kv: -abs(kv[1]))[:4]) if len(mv) > 4 else mv   # show the 4 largest movers; the sum line below uses all
    big = max(mv, key=lambda k: abs(mv[k])); off = [k for k in mv if k != big and mv[k] * mv[big] < 0]
    text = (f"Net change {ch/1000:+.1f}B = " if S.key == "economy" else f"Net change {ch:+,.0f} = ") + " ".join((f"{k} {mv[k]/1000:+.1f}B" if S.key == "economy" else f"{k} {mv[k]:+,.0f}") for k in mv) + f". Largest mover: {big}" + (f", partly offset by {', '.join(off)}." if off else ".")
    return A("What drove it?", "level 1: driver", text, [], [f"{k}: {v[i]:,.1f} - {v[i-1]:,.1f} = {v[i]-v[i-1]:+,.1f}" for k, v in S.parts.items()] + [f"sum of all components = {sum(v[i]-v[i-1] for v in S.parts.values()):+,.1f} = net change {ch:+,.1f}"])

def why(S, i):
    t = ("The data can't tell why. Causes such as policy, prices elsewhere or one-off events are outside this series. "
         "Ask the analyst to check: events and news around that date, related series, and the client's own explanation.")
    part = drivers(S, i) if S.parts else None
    return A("Why, really?", "level 4-5: outside the data", t + (" What the data does show: " + part["text"] if part and not part["declined"] else ""), [], part["path"] if part else ["no calculation possible: the question asks about causes outside the series"], True)

def comove(S, i, window=None):
    window = window or (36 if S.freq == "M" else 52)
    cov = S.cov or ({"Exports": [-x for x in S.parts["Exports (inverted)"]], "Imports": S.parts["Imports"]} if S.key == "economy" else None)
    if not cov: return A("What moved with it?", "level 3: co-movement", f"{S.name} has no related series in this dataset.", [], [], True)
    def r(x, y, lo, hi):
        dx = [x[j] / x[j-1] - 1 if x[j-1] else 0 for j in range(lo, hi)]; dy = [y[j] / y[j-1] - 1 for j in range(lo, hi)] if min(y) > 0 else [y[j] - y[j-1] for j in range(lo, hi)]
        mx, my = mean(dx), mean(dy); sx, sy = pstdev(dx), pstdev(dy)
        return mean([(a - mx) * (b - my) for a, b in zip(dx, dy)]) / (sx * sy) if sx and sy else 0.0
    lo = max(1, i - window + 1); out, path = [], []
    for name, v in cov.items():
        rn = r(S.values, v, lo, i + 1); rb = r(S.values, v, max(1, lo - window), lo) if lo - window >= 1 else None
        word = "strongly" if abs(rn) > 0.7 else "somewhat" if abs(rn) > 0.4 else "barely"
        out.append(f"{name}: {word} ({rn:+.2f})"); path.append(f"{name}: correlation of period changes over the last {window} {S.period}s = {rn:+.2f}" + (f"; the {window} before = {rb:+.2f}" + (" (stable)" if abs(rn - rb) < 0.25 else " (changed)") if rb is not None else ""))
    text = f"Related series moved with {S.name} over the last {window} {S.period}s (changes, not levels): " + "; ".join(out) + ". This shows they moved together, not that one caused the other."
    path.append("levels are not compared: trending series correlate in levels by accident")
    return A("What moved with it?", "level 3: co-movement", text, [], path)

def future_dates(S, h):
    d = date.fromisoformat(S.dates[-1]); out = []
    for k in range(1, h + 1):
        if S.freq == "M":
            m = d.month - 1 + k; out.append(date(d.year + m // 12, m % 12 + 1, 1))
        else: out.append(d + timedelta(days=7 * k))
    return [x.isoformat() for x in out]

def forecast_answer(S, i):
    import forecast as F
    f = F.forecast(S)
    if f is None: return A("What is the forecast?", "future-directed: forecast", "Not enough history to evaluate a forecast honestly (needs at least about 3 seasons before and 2 evaluation periods). No forecast shown.", [], [], True)
    ev = f["eval"]; k = f["method"]; t = ev["table"]
    n_, c_ = t["repeat last value"]["test"], t[k]["test"]; r = c_ / n_
    fd = future_dates(S, f["h"]); lab = lambda d: (f"{MON[int(d[5:7])-1]} {d[:4]}" if S.freq == "M" else f"week of {d}")
    first, last = f["values"][0], f["values"][-1]
    verdict = ("better than repeating the last value" if r < 0.9 else
               "no better than repeating the last value, so read it as roughly flat" if r <= 1.1 else
               "worse than repeating the last value, so it should not be relied on")
    best = min(t, key=lambda m: t[m]["test"]); disagree = ""
    if best != k and t[best]["test"] < 0.8 * c_:
        disagree = (f" Warning: the method picked on validation data ('{k}') did worse on the held-out windows than '{best}' ({c_*100:.1f}% against {t[best]['test']*100:.1f}%); "
                    "the validation windows contain the 2020-22 shock, so the choice is unreliable. Not changed after seeing test results.")
    cov = f["coverage"]; cwarn = "" if cov >= 0.65 else " The range was too narrow: treat it as optimistic."
    text = (f"Forecast with '{k}': {lab(fd[0])} {fmt(S, first)}, {lab(fd[-1])} {fmt(S, last)} "
            f"(range for the last point {fmt(S, f['band'][-1][0])} to {fmt(S, f['band'][-1][1])}). "
            f"Track record: on {ev['n_test']} held-out windows since {ev['test_from'][:7]} the average error was {c_*100:.1f}% against {n_*100:.1f}% for repeating the last value, which makes this forecast {verdict}. "
            f"The 10-90% range held {cov*100:.0f}% of actual values (should be 80%).{cwarn}{disagree}")
    path = [f"method chosen on validation windows only: {k}", f"horizon {f['h']} {S.period}s; test windows start {ev['test_from']}"] + \
           [f"{m}: validation error {r_['val']*100:.1f}%, test error {r_['test']*100:.1f}%, test excluding 2020-21 {r_['test_ex_covid']*100:.1f}%" for m, r_ in t.items()] + \
           [f"ratio to repeat-last (test) = {c_*100:.1f}% / {n_*100:.1f}% = {r:.2f}"]
    a = A("What is the forecast?", "future-directed: forecast", text, [], path, declined=(r > 1.1 or cov < 0.65 or bool(disagree)))
    if S.kind == "ratio": f["band"] = [(max(0, lo), min(1.0, hi)) for lo, hi in f["band"]]
    a["forecast"] = dict(dates=fd, values=f["values"], band=f["band"], method=k, ratio=r, coverage=cov)
    return a

ROUTES = [  # first match wins
    (r"\b(forecast|outlook|predict\w*|next (few )?(months?|weeks?|periods?|quarter)|going forward|ahead|what('s| is) next)\b", forecast_answer),
    (r"\b(why|because|cause|reason|explain)\b", why),
    (r"\b(drove|driver|drives|contribut|component|which (one|part|origin|categor\w*|market)|origins?|categor\w*)\b", drivers),
    (r"\b(moved with|co-?mov\w*|correlat\w*|related|along with|what else|weather|temperature|rain\w*|price)\b", comove),
    (r"\b(normal|usual|typical|season|expected|unusual)\b", seasonal),
    (r"\b(last year|year ago|year over year|yoy|same (month|week)|compared? )\b", yoy),
    (r"\b(record|highest|lowest|peak|max|min|best|worst)\b", extremes),
    (r"\b(start|began|since when|streak|in a row|how long)\b", when_started),
]
def route(question):
    q = question.lower()
    for pat, fn in ROUTES:
        if re.search(pat, q): return fn
    return what_happened

def parse_target(S, question):
    q = question.lower(); yr = re.search(r"\b(19[89]\d|20[0-3]\d)\b", q)
    mon = next((n for n, name in enumerate(FULL, 1) if re.search(r"\b" + name[:3] + r"[a-z]*\b", q)), None)
    iso = re.search(r"\b(\d{4})-(\d{2})(?:-(\d{2}))?\b", q)
    if iso: y, m = int(iso.group(1)), int(iso.group(2))
    elif yr and mon: y, m = int(yr.group(1)), mon
    else: return len(S.values) - 1
    cands = [k for k, d in enumerate(S.dates) if int(d[:4]) == y and int(d[5:7]) == m]
    return cands[-1] if cands else None

def ask(S, question):
    i = parse_target(S, question)
    if i is None: return dict(error=f"No data for that period. Series covers {S.label(0)} to {S.label(len(S.values)-1)}."), None
    if i < 1: return dict(error="Need a previous period to compare with."), None
    return route(question)(S, i), i

def check_claims(S, claims):
    out = []
    for c in claims:
        actual = recompute(S, c["op"], c["i"])
        ok = actual == c["asserted"] if isinstance(actual, str) else abs(abs(actual) - abs(c["asserted"])) <= max(1e-6, 1e-9 * abs(actual))
        out.append(dict(part=c["part"], op=c["op"], ok=bool(ok)))
    return out

# ---- Check for FREE TEXT (e.g. a model's output): which numbers can be derived from the window it saw? ----
NUM = re.compile(r"(?<![\w.])-?\d[\d,]*(?:\.\d+)?%?")
UP = re.compile(r"\b(rise|rises|rising|rose|increase[sd]?|increasing|upward|up|grow\w*|climb\w*|higher)\b", re.I)
DOWN = re.compile(r"\b(fall|falls|falling|fell|decrease[sd]?|decreasing|downward|down|declin\w*|drop\w*|lower)\b", re.I)

def derivable(S, i, window):
    w = S.values[max(0, i - window + 1): i + 1]; m, sd = mean(w), pstdev(w)
    base = set(w) | {m, sd, min(w), max(w), w[0], w[-1], w[-1] - w[0]}
    base |= {b - a for a, b in zip(w, w[1:])} | {abs(b - a) for a, b in zip(w, w[1:])}
    if S.pct_ok:
        base |= {(b / a - 1) * 100 for a, b in zip(w, w[1:])} | {(w[-1] / w[0] - 1) * 100}
    base |= {(x - m) / sd for x in w} if sd else set()
    scaled = base | {x / 1000 for x in base} | {x / 1e6 for x in base}
    return {abs(x) for x in scaled}

def check_free_text(S, i, window, text):
    pool = derivable(S, i, window); nums, bad = [], []
    for m in NUM.findall(text):
        raw = m.rstrip("%").replace(",", ""); 
        try: x = abs(float(raw))
        except ValueError: continue
        if 1900 <= x <= 2100 and "." not in raw: continue          # looks like a year
        if x <= window and float(raw) == int(float(raw)): continue   # small counts such as "12 months"
        nums.append(m)
        if not any(abs(x - p) <= max(0.051, 0.01 * p) for p in pool): bad.append(m)
    w = S.values[max(0, i - window + 1): i + 1]; tot = w[-1] / w[0] - 1 if w[0] else 0
    actual = "up" if tot > 0.01 else "down" if tot < -0.01 else "flat"
    up, dn = len(UP.findall(text)), len(DOWN.findall(text))
    said = "up" if up > dn else "down" if dn > up else "none/mixed"
    return dict(numbers=len(nums), not_derivable=bad, direction_said=said, direction_actual=actual,
                direction_ok=(said == actual) if said != "none/mixed" else None, window=window)
