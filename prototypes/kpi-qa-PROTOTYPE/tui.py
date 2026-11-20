"""PROTOTYPE shell. python3 tui.py [--demo]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import answers as A

B, D, R, G, RED = "\x1b[1m", "\x1b[2m", "\x1b[0m", "\x1b[32m", "\x1b[31m"
S = A.load(os.path.join(os.path.dirname(__file__), "data", "Economy.csv"))

def render(ans, ym):
    text, lines = A.checked_text(S, ans.text, ans.claims)
    print(f"{B}Question:{R} {ans.title}   {D}[{ans.level}]{R}\n")
    print(f"{B}Answer (after Check):{R}\n  {text}\n")
    if ans.claims:
        print(f"{B}Checks:{R}")
        for ok, c, actual in lines:
            mark = f"{G}✔{R}" if ok else f"{RED}✘{R}"
            print(f"  {mark} '{c.sentence_part}' [{c.op}] " + ("" if ok else f"{RED}text said {c.asserted}, data says {A.fmt(c.op, actual) if not isinstance(actual,str) else actual}{R}"))
        print()
    print(f"{B}Calculation path:{R}")
    for p in ans.path: print(f"  {D}{p}{R}")
    if ans.chart_ym:
        line, cap, pos = A.sparkline(S, ans.chart_ym)
        print(f"\n{B}Evidence (deficit, last 13 months):{R}\n  {line}\n  {' ' * pos}^ {A.label(ans.chart_ym)}\n  {D}{cap}{R}")

def draft_view(ym):
    text, claims = A.model_draft(ym)
    print(f"{B}Model draft (stub, errors planted):{R}\n  {text}\n")
    fixed, lines = A.checked_text(S, text, claims)
    print(f"{B}Checks:{R}")
    for ok, c, actual in lines:
        print(f"  {G+'✔' if ok else RED+'✘'}{R} '{c.sentence_part}' " + ("" if ok else f"{RED}said {c.asserted}, data says {A.fmt(c.op, actual) if not isinstance(actual,str) else actual}{R}"))
    print(f"\n{B}What the Partner sees:{R}\n  {fixed}\n  {D}(wrong claims corrected from the data; checker catches {sum(not o for o,_,_ in lines)} of {len(lines)} planted-or-real errors){R}")

def spot_view():
    print(f"{B}Spotting (stub: heuristic standing in for the model){R}\n  Months worth a sentence, last 24 months:")
    for ym, c, z in A.spot(S): print(f"  {A.label(ym)}: deficit change {c:+,.0f}M  (z={z:+.1f})")
    print(f"  {D}code then computes the figures for these; the model only decides where to look{R}")

ACTIONS = {"1": A.what_happened, "2": A.streak, "3": A.seasonal, "4": A.drivers, "5": A.comove, "6": A.why_really}

def frame(ym, key):
    print(f"{B}KPI Q&A prototype{R} {D}— US trade balance, Time-MMD Economy, {A.label(S['ym'][0])} to {A.label(S['ym'][-1])}, {len(S['ym'])} months{R}")
    print(f"{B}Month:{R} {A.label(ym)}\n")
    if key in ACTIONS: render(ACTIONS[key](S, ym), ym)
    elif key == "7": draft_view(ym)
    elif key == "8": spot_view()
    else: print("Pick a question below.")
    print(f"\n{D}{'─'*70}{R}\n{B}[1]{R} what happened  {B}[2]{R} when did it start  {B}[3]{R} normal for season?  {B}[4]{R} what drove it?")
    print(f"{B}[5]{R} what moved with it  {B}[6]{R} why, really?  {B}[7]{R} model draft + Check  {B}[8]{R} spotting")
    print(f"{B}[m]{R} change month (YYYY-MM)  {B}[q]{R} quit")

if __name__ == "__main__":
    ym = S["ym"][-1]
    if "--demo" in sys.argv:
        for k in "1234567": frame(ym, k); print("\n" + "=" * 70 + "\n")
        frame("2020-04", "3"); sys.exit()
    key = ""
    while True:
        os.system("clear"); frame(ym, key)
        c = input("> ").strip()
        if c == "q": break
        if c == "m":
            n = input("month YYYY-MM > ").strip()
            if n in S["ym"][1:]: ym = n
        else: key = c
