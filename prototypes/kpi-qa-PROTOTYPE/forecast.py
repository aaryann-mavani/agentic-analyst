"""PROTOTYPE forecasting + honest evaluation (stdlib only).
Methods are simple statistical stand-ins for a real forecasting model. Every origin uses only data up to that origin."""
from statistics import mean, quantiles

def naive(v, h, L): return [v[-1]] * h
def snaive(v, h, L): return [v[len(v) - L + (k % L)] for k in range(h)]
def snaive_drift(v, h, L):
    g = mean(v[-L:]) / mean(v[-2 * L:-L]); return [x * g for x in snaive(v, h, L)]
METHODS = {"repeat last value": naive, "same period last year": snaive, "last year x growth": snaive_drift}

def horizon(S): return 6 if S.freq == "M" else 8

def windows(S, lo, hi):
    """forecast origins (index of last observed value) from lo to hi, step = horizon"""
    h = horizon(S); return list(range(lo, hi - h + 1, h))

def run(S, origins, key):
    v, L, h = S.values, S.year_lag, horizon(S); out = []
    for o in origins:
        f = METHODS[key](v[:o + 1], h, L); a = v[o + 1:o + 1 + h]
        out.append(dict(o=o, rel=[x / y - 1 for x, y in zip(a, f)], ape=[abs(x - y) / abs(x) for x, y in zip(a, f)], actual=a, fc=f))
    return out

def mape(runs, skip_covid=False):
    r = [w for w in runs if not (skip_covid and S_overlaps_covid(w))]
    xs = [e for w in r for e in w["ape"]]; return mean(xs) if xs else None

_S = None
def S_overlaps_covid(w):
    d = _S.dates; return any("2020-03" <= d[i][:7] <= "2021-12" for i in range(w["o"] + 1, w["o"] + 1 + horizon(_S)))

def evaluate(S):
    global _S; _S = S
    n, L, h = len(S.values), S.year_lag, horizon(S)
    span = min(5 * L, int(0.3 * n)); test_lo = n - span; val_lo = test_lo - span
    if val_lo < 2 * L or span < 3 * h: return None   # not enough history to evaluate honestly
    val_o, test_o = windows(S, val_lo, test_lo + h - 1), windows(S, test_lo, n - 1)
    tab = {}
    for k in METHODS:
        v, t = run(S, val_o, k), run(S, test_o, k)
        vc = [w for w in v if not S_overlaps_covid(w)] or v      # method choice and ranges ignore the 2020-21 shock windows
        tab[k] = dict(val=mape(vc), test=mape(t), test_ex_covid=mape(t, True), test_runs=t, val_runs=vc)
    chosen = min(tab, key=lambda k: tab[k]["val"])   # picked on validation only, never on test
    return dict(table=tab, chosen=chosen, test_from=S.dates[test_lo], n_test=len(test_o), n_val=len(val_o))

def forecast(S):
    ev = evaluate(S)
    if ev is None: return None
    k = ev["chosen"]; v, L, h = S.values, S.year_lag, horizon(S)
    fc = METHODS[k](v, h, L)
    errs = [[w["rel"][j] for w in ev["table"][k]["val_runs"]] for j in range(h)]   # signed relative errors per horizon step
    band = []
    for j in range(h):
        q = quantiles(errs[j], n=10, method="inclusive")   # deciles
        band.append((fc[j] * (1 + q[0]), fc[j] * (1 + q[-1])))
    cov = None
    t = ev["table"][k]["test_runs"]
    if t:
        hits = tot = 0
        for w in t:
            for j in range(h):
                q = quantiles(errs[j], n=10, method="inclusive"); lo, hi = w["fc"][j] * (1 + q[0]), w["fc"][j] * (1 + q[-1])
                hits += lo <= w["actual"][j] <= hi; tot += 1
        cov = hits / tot
    last = S.dates[-1]; idx = list(range(len(v), len(v) + h))
    return dict(method=k, values=fc, band=band, coverage=cov, eval=ev, h=h, last=last)
