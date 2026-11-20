"""PROTOTYPE — UNTESTED HERE. Runs a released OpenTSLM checkpoint on a window of one of our series.

Not run on this Mac: needs `pip install opentslm torch`, a CUDA GPU (MPS does not work for the released
checkpoints, CPU is slow), and Hugging Face access to the gated base model (meta-llama/Llama-3.2-1B).
Written against the OpenTSLM README demo (demo/huggingface/02_test_hf_m4.py) and the M4 dataset class.

Usage on a GPU box:  python3 model_runner.py --batch      (fills model_outputs.json, which the dashboard reads)
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

CACHE = os.path.join(E.HERE, "model_outputs.json")
REPOS = {"caption (M4 checkpoint)": "OpenTSLM/llama-3.2-1b-m4-sp", "tsqa (multiple-choice checkpoint)": "OpenTSLM/llama-3.2-1b-tsqa-sp"}
CAPTION_PROMPT = "Please generate a detailed caption for this time-series, describing it as accurately as possible."
_model = {}

def cache_key(series, end, window, mode, question, context, repo):
    return "|".join(map(str, [series, end, window, mode, question if mode == "question" else "", int(context), repo]))

def load_cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def build_sample(S, i, window, mode, question, context):
    import torch
    w = S.values[max(0, i - window + 1): i + 1]; t = torch.tensor(w, dtype=torch.float32)
    m, sd = t.mean(), t.std(); norm = (t - m) / sd if sd > 0 else t - m
    head = f"This is the time series, it has mean {m:.4f} and std {sd:.4f}:"
    if context:  # extra text our product would add: name, unit, frequency, date range
        head = f"{S.name}, {S.unit}, {S.period}ly, {S.label(max(0, i-window+1))} to {S.label(i)}. " + head
    return {"pre_prompt": "You are an expert in time series analysis.", "time_series_text": [head], "time_series": [norm],
            "post_prompt": question if mode == "question" else CAPTION_PROMPT, "answer": ""}

def generate(S, i, window, mode, question, context, repo):
    import torch
    from opentslm.model.llm.OpenTSLM import OpenTSLM
    from opentslm.model_config import PATCH_SIZE
    from opentslm.time_series_datasets.util import extend_time_series_to_match_patch_size_and_aggregate
    if repo not in _model:
        _model[repo] = OpenTSLM.load_pretrained(repo, device="cuda" if torch.cuda.is_available() else "cpu")
    batch = extend_time_series_to_match_patch_size_and_aggregate([build_sample(S, i, window, mode, question, context)], patch_size=PATCH_SIZE)
    t = time.perf_counter(); out = _model[repo].generate(batch, max_new_tokens=200)[0]
    return out, time.perf_counter() - t

def run_and_cache(series, end, window, mode, question, context, repo):
    S = E.load(series); out, secs = generate(S, end, window, mode, question, context, repo)
    c = load_cache(); c[cache_key(series, S.dates[end], window, mode, question, context, repo)] = {"output": out, "seconds": round(secs, 2), "repo": repo}
    json.dump(c, open(CACHE, "w"), indent=1); return c

if __name__ == "__main__" and "--batch" in sys.argv:
    QS = ["What happened in the latest period?", "Is the latest move unusual for this time of year?", "Which way is the series trending?"]
    for key in E.SPECS:
        S = E.load(key); i = len(S.values) - 1; win = 24 if S.freq == "M" else 52
        for ctx in (False, True):
            for repo in REPOS.values():
                run_and_cache(key, i, win, "caption", "", ctx, repo); print(key, "caption", ctx, repo)
                for q in QS: run_and_cache(key, i, win, "question", q, ctx, repo); print(key, q, ctx, repo)
