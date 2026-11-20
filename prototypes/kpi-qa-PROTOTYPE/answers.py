"""PROTOTYPE logic: computed answers, claims, and the checker. Pure, no I/O except load()."""
import csv
from dataclasses import dataclass, field
from statistics import mean, pstdev

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def load(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            rows.append((r["date"][:7], float(r["Exports"]), float(r["Imports"]), float(r["OT"])))
    rows.sort()
    # TimeNet rule: bad data raises, never filled in
    for (a, *_), (b, *_) in zip(rows, rows[1:]):
        ay, am = map(int, a.split("-")); by, bm = map(int, b.split("-"))
        if (by * 12 + bm) - (ay * 12 + am) != 1:
            raise ValueError(f"gap or duplicate between {a} and {b}")
    for ym, ex, im, ot in rows:
        if abs((ex - im) - ot) > 0.5:
            raise ValueError(f"{ym}: OT != Exports - Imports")
    return {"ym": [r[0] for r in rows], "ex": [r[1] for r in rows],
            "im": [r[2] for r in rows], "ot": [r[3] for r in rows]}

def label(ym): y, m = ym.split("-"); return f"{MONTHS[int(m)-1]} {y}"
def bn(x): return f"${x/1000:.1f}B"
def deficit(S, i): return -S["ot"][i]
def idx(S, ym): return S["ym"].index(ym)

@dataclass
class Claim:
    sentence_part: str      # the words as written in the answer
    op: str                 # what to recompute
    ym: str
    asserted: object        # the value the text asserts
    path: list = field(default_factory=list)

@dataclass
class Answer:
    title: str
    level: str
    text: str
    claims: list
    path: list
    chart_ym: str = ""
    declined: bool = False

# ---- recomputation (the Check). Independent of how the text was produced ----
def recompute(S, op, ym):
    i = idx(S, ym)
    if op == "deficit": return deficit(S, i)
    if op == "deficit_change": return deficit(S, i) - deficit(S, i - 1)
    if op == "exports_change": return S["ex"][i] - S["ex"][i - 1]
    if op == "imports_change": return S["im"][i] - S["im"][i - 1]
    if op == "direction": return "widened" if deficit(S, i) > deficit(S, i - 1) else "narrowed"
    if op == "streak":
        d = "widened" if deficit(S, i) > deficit(S, i - 1) else "narrowed"; n = 0
        while i - n - 1 >= 0 and ("widened" if deficit(S, i - n) > deficit(S, i - n - 1) else "narrowed") == d: n += 1
        return n
    raise KeyError(op)

def fmt(op, v):
    if op in ("deficit", "deficit_change", "exports_change", "imports_change"): return bn(abs(v))
    return str(v)

def check(S, claim):
    actual = recompute(S, claim.op, claim.ym)
    if isinstance(actual, float): ok = abs(abs(actual) / 1000 - abs(float(claim.asserted)) / 1000) <= 0.051
    else: ok = actual == claim.asserted
    return ok, actual

def checked_text(S, text, claims):
    out, lines = text, []
    for c in claims:
        ok, actual = check(S, c)
        lines.append((ok, c, actual))
        if not ok: out = out.replace(c.sentence_part, fmt(c.op, actual) if not isinstance(actual, str) else actual)
    return out, lines

# ---- computed answers ----
def what_happened(S, ym):
    i = idx(S, ym); d, dp = deficit(S, i), deficit(S, i - 1); ch = d - dp
    word = "widened" if ch > 0 else "narrowed"
    text = f"The US trade deficit {word} by {bn(abs(ch))} to {bn(d)} in {label(ym)}."
    claims = [Claim(word, "direction", ym, word), Claim(bn(abs(ch)), "deficit_change", ym, abs(ch)), Claim(bn(d), "deficit", ym, d)]
    path = [f"deficit = -(OT) = -(Exports - Imports)", f"{label(ym)}: {d:,.1f}", f"{label(S['ym'][i-1])}: {dp:,.1f}", f"change = {d:,.1f} - {dp:,.1f} = {ch:+,.1f} (millions USD, assumed)"]
    return Answer("What happened?", "description", text, claims, path, ym)

def streak(S, ym):
    n = recompute(S, "streak", ym); w = recompute(S, "direction", ym)
    text = f"The deficit has {w} for {n} month{'s' if n != 1 else ''} in a row, up to {label(ym)}."
    i = idx(S, ym)
    path = [f"{label(S['ym'][i-k-1])} -> {label(S['ym'][i-k])}: {deficit(S,i-k)-deficit(S,i-k-1):+,.1f}" for k in range(min(n + 1, 6))]
    return Answer("When did it start?", "temporal localization", text, [Claim(w, "direction", ym, w), Claim(str(n), "streak", ym, n)], path, ym)

def seasonal(S, ym, years=5):
    i = idx(S, ym); m = ym[5:]
    ch = deficit(S, i) - deficit(S, i - 1)
    past = [(S["ym"][j], deficit(S, j) - deficit(S, j - 1)) for j in range(1, len(S["ym"])) if S["ym"][j][5:] == m and S["ym"][j] < ym][-years:]
    vals = [v for _, v in past]; mu, sd = mean(vals), pstdev(vals)
    z = (ch - mu) / sd if sd else 0
    verdict = "in line with" if abs(z) <= 1 else ("larger than" if z > 0 else "smaller than")
    text = (f"The {label(ym)} change of {ch:+,.0f}M is {verdict} the usual {MONTHS[int(m)-1]} move "
            f"(last {len(vals)} years: average {mu:+,.0f}M, typical spread {sd:,.0f}M).")
    path = [f"{label(y)}: {v:+,.1f}" for y, v in past] + [f"mean = {mu:+,.1f}, std = {sd:,.1f}", f"z = ({ch:+,.1f} - {mu:+,.1f}) / {sd:,.1f} = {z:+.2f}  (|z| <= 1 counts as in line)"]
    return Answer("Is this normal for the time of year?", "level 2: seasonal comparison", text, [Claim(f"{ch:+,.0f}M", "deficit_change", ym, ch)], path, ym)

def drivers(S, ym):
    i = idx(S, ym); de, di = S["ex"][i] - S["ex"][i-1], S["im"][i] - S["im"][i-1]; ch = di - de
    big = "imports" if abs(di) >= abs(de) else "exports"
    text = (f"The deficit changed by {ch:+,.0f}M. Imports moved {di:+,.0f}M and exports {de:+,.0f}M; "
            f"the larger mover was {big}.")
    path = ["deficit = Imports - Exports  (components add up exactly, max residual 0.1)",
            f"Imports: {S['im'][i]:,.1f} - {S['im'][i-1]:,.1f} = {di:+,.1f}", f"Exports: {S['ex'][i]:,.1f} - {S['ex'][i-1]:,.1f} = {de:+,.1f}",
            f"deficit change = {di:+,.1f} - ({de:+,.1f}) = {ch:+,.1f}"]
    return Answer("What drove it?", "level 1: driver", text, [Claim(f"{di:+,.0f}M", "imports_change", ym, di), Claim(f"{de:+,.0f}M", "exports_change", ym, de)], path, ym)

def comove(S, ym, window=36):
    i = idx(S, ym); lo = max(1, i - window + 1)
    dx = [S["ex"][j] - S["ex"][j-1] for j in range(lo, i + 1)]; dm = [S["im"][j] - S["im"][j-1] for j in range(lo, i + 1)]
    mx, mm = mean(dx), mean(dm); sx, sm = pstdev(dx), pstdev(dm)
    r = mean([(a - mx) * (b - mm) for a, b in zip(dx, dm)]) / (sx * sm)
    strength = "strongly" if abs(r) > 0.7 else "somewhat" if abs(r) > 0.4 else "barely"
    text = f"Over the last {len(dx)} months, monthly changes in exports and imports {strength} coincided (correlation {r:+.2f}). This shows they moved together, not that one caused the other."
    path = [f"changes of Exports and Imports, {label(S['ym'][lo])} to {label(ym)}", f"Pearson r on monthly changes = {r:+.2f}", "thresholds: |r|>0.7 strongly, >0.4 somewhat"]
    return Answer("What else moved with it?", "level 3: co-movement", text, [], path, ym)

def why_really(S, ym):
    text = ("The data can't tell. Likely reasons (exchange rates, tariffs, demand abroad) are outside these series. "
            "Ask your analyst to check: dollar index, tariff changes, major one-off shipments in that month.")
    return Answer("Why, really?", "level 4-5: outside the data", text, [], ["no calculation: the series contain only Exports and Imports"], ym, declined=True)

# ---- stubbed "model": spotting + a draft with planted errors ----
def spot(S, last=24):
    n = len(S["ym"]); ch = [(S["ym"][j], deficit(S, j) - deficit(S, j - 1)) for j in range(n - last, n)]
    sd = pstdev([c for _, c in ch]); mu = mean([c for _, c in ch])
    return sorted([(ym, c, (c - mu) / sd) for ym, c in ch], key=lambda t: -abs(t[2]))[:3]

def model_draft(ym):
    return ("The deficit widened by $5.0B in the month, the third month in a row, "
            "driven by imports (+$16.5B) while exports rose $12.2B.", [
        Claim("widened", "direction", ym, "widened"),
        Claim("$5.0B", "deficit_change", ym, 5000.0),
        Claim("third", "streak", ym, 3),
        Claim("+$16.5B", "imports_change", ym, 16500.0),
        Claim("$12.2B", "exports_change", ym, 12200.0)])

def sparkline(S, ym, n=13):
    i = idx(S, ym); xs = list(range(max(0, i - n + 1), i + 1)); v = [deficit(S, j) for j in xs]
    lo, hi = min(v), max(v); bars = "▁▂▃▄▅▆▇█"
    line = "".join(bars[int((x - lo) / (hi - lo or 1) * 7)] for x in v)
    return line, f"{label(S['ym'][xs[0]])} .. {label(ym)}   min {bn(lo)}  max {bn(hi)}   (latest highlighted below)", len(v) - 1
