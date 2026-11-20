"""A thin chat box and chart over `ask` (standard library only). It only renders an Answer; no logic lives here.

    python -m agentic_analyst.web path/to/Economy.csv      then open http://127.0.0.1:8766
"""
from __future__ import annotations

import sys
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from .answer import Answer, Chart
from .ask import ask
from .series import Series
from .sources.time_mmd_economy import load_us_trade

PAGE = """<!doctype html><meta charset="utf-8"><title>Agentic Analyst</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;color:#1c2430}}
input[type=text]{{width:75%;padding:8px;font:inherit}}button{{padding:8px 14px;font:inherit}}
.ok{{color:#17803d}}.bad{{color:#c0392b}}.mut{{color:#6b7686;font-size:13px}}pre{{background:#f1f4f8;padding:8px;overflow:auto}}</style>
<h2>{title}</h2>
<form><input type="text" name="q" value="{q}" placeholder="What happened in March 2024?" autofocus> <button>Ask</button></form>
{body}"""


def chart_svg(chart: Chart, width: int = 860, height: int = 220, last: int = 120) -> str:
    n = len(chart.values)
    a = max(0, n - last)
    vals = chart.values[a:]
    lo, hi = min(vals), max(vals)
    x = lambda i: 10 + (i - a) / max(1, n - 1 - a) * (width - 20)
    y = lambda v: height - 10 - (v - lo) / ((hi - lo) or 1) * (height - 20)
    line = " ".join(f"{x(a + j):.1f},{y(v):.1f}" for j, v in enumerate(vals))
    dots = "".join(f'<circle cx="{x(i):.1f}" cy="{y(chart.values[i]):.1f}" r="5" fill="#c0392b"><title>{escape(chart.dates[i])}</title></circle>'
                   for i in chart.highlight if i >= a)
    return (f'<svg width="100%" viewBox="0 0 {width} {height}" role="img" aria-label="Series with the period highlighted">'
            f'<polyline fill="none" stroke="#1c2430" stroke-width="1.5" points="{line}"/>{dots}</svg>')


def answer_html(answer: Answer) -> str:
    out = [f"<p><b>{escape(answer.text)}</b></p>"]
    if answer.claims:
        out.append("<p>" + "<br>".join(
            f'<span class="{"ok" if c.passed else "bad"}">{"passed" if c.passed else "FAILED"}</span> '
            f'{escape(c.claim.measure)}: {escape(c.claim.shown)}' + ("" if c.passed else f" (code says {escape(c.recomputed)})")
            for c in answer.claims) + "</p>")
    if answer.calculation_path:
        out.append("<details open><summary>Calculation path</summary><pre>" + escape("\n".join(answer.calculation_path)) + "</pre></details>")
    if answer.evidence:
        out.append("<p>Evidence: " + "; ".join(f"{escape(f.label)} = {f.value:,.1f}" for f in answer.evidence.figures) + "</p>")
        out.append(chart_svg(answer.evidence.chart))
        out.append('<p class="mut">Red dots: the periods compared.</p>')
    return "".join(out)


def make_handler(series: Series):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0].strip()
            body = answer_html(ask(series, q)) if q else f'<p class="mut">Series covers {escape(series.coverage())}.</p>'
            page = PAGE.format(title=escape(series.name), q=escape(q, quote=True), body=body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)

    return Handler


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python -m agentic_analyst.web path/to/Economy.csv  (see README for how to download it)")
    print("Serving on http://127.0.0.1:8766")
    HTTPServer(("127.0.0.1", 8766), make_handler(load_us_trade(sys.argv[1]))).serve_forever()
