"""PROTOTYPE dashboard server (stdlib only).  python3 prototypes/kpi-qa-PROTOTYPE/server.py  ->  http://127.0.0.1:8765"""
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E, model_runner as M

SERIES = {k: E.load(k) for k in E.SPECS}

def model_panel(S, i, window, mode, question, context, repo_label, live):
    repo = M.REPOS[repo_label]; key = M.cache_key(S.key, S.dates[i], window, mode, question, context, repo)
    c = M.load_cache()
    if key not in c and live:
        try: c = M.run_and_cache(S.key, i, window, mode, question, context, repo)
        except Exception as e: return dict(status="error", message=f"{type(e).__name__}: {e}")
    if key not in c:
        return dict(status="not_run", message="No model output for this setting yet. This Mac has no GPU, torch or Hugging Face access, so the model has not run here. "
                    "On a GPU machine with access to meta-llama/Llama-3.2-1B run: python3 model_runner.py --batch", repo=repo)
    r = c[key]; return dict(status="ok", output=r["output"], seconds=r.get("seconds"), repo=repo, check=E.check_free_text(S, i, window, r["output"]))

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, obj, code=200, ctype="application/json"):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if self.path == "/": return self.send(open(os.path.join(E.HERE, "index.html"), "rb").read(), ctype="text/html; charset=utf-8")
        if self.path == "/api/series":
            return self.send({k: dict(name=S.name, unit=S.unit, freq=S.freq, n=len(S.values), start=S.label(0), end=S.label(len(S.values) - 1),
                                      dates=S.dates, values=S.values, biz=getattr(S, 'biz', None)) for k, S in SERIES.items()} | {"_models": list(M.REPOS)})
        self.send({"error": "not found"}, 404)
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        if self.path != "/api/ask": return self.send({"error": "not found"}, 404)
        S = SERIES[d["series"]]; q = d.get("question", "")
        ans, i = E.ask(S, q)
        if i is None: return self.send({"error": ans["error"]})
        ans["checks"] = E.check_claims(S, ans["claims"]); ans["claims"] = None
        ans["period"] = S.label(i); ans["i"] = i
        window = int(d.get("window", 24)); mode = d.get("mode", "caption")
        ans["model"] = model_panel(S, i, window, mode, q, bool(d.get("context")), d.get("model", list(M.REPOS)[0]), bool(d.get("live")))
        self.send(ans)

if __name__ == "__main__":
    print("PROTOTYPE dashboard on http://127.0.0.1:8765"); HTTPServer(("127.0.0.1", 8765), H).serve_forever()
