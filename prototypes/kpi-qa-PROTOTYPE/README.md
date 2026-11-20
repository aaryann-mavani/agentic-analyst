# PROTOTYPE — wipe me

**Questions this answers**
1. (tui.py) Does the ADR 0001 design feel right when driven by hand? Economy only.
2. (server.py + index.html) What does a chat dashboard over Time-MMD look like, and how does a released,
   not-fine-tuned-by-us OpenTSLM checkpoint behave next to code-computed answers on the same question?

**First run:** `python3 prototypes/kpi-qa-PROTOTYPE/tools/fetch_data.py` downloads the public data into `data/` (not committed).

Run the dashboard: `python3 prototypes/kpi-qa-PROTOTYPE/server.py` then open http://127.0.0.1:8765
Terminal version:  `python3 prototypes/kpi-qa-PROTOTYPE/tui.py [--demo]`

Data (downloaded by fetch_data.py; Time-MMD pinned to commit 00281e2d86058286d5548b15a7670e8eda57ef62): Economy, Energy, Traffic, Agriculture, plus five Swiss series.
`engine.py` = standardized series + computed answers + Checks (portable logic). `server.py`/`index.html` = throwaway shell.

**The model panel is empty until someone runs `model_runner.py --batch` on a GPU machine** (needs `pip install opentslm torch`,
CUDA, and Hugging Face access to meta-llama/Llama-3.2-1B). `model_runner.py` is UNTESTED: written from the OpenTSLM README
demo and M4 dataset class, never run. Results land in `model_outputs.json`, which the dashboard reads.

## Added 2026-11-20
- Forecast (`forecast.py`): simple statistical stand-ins, evaluated on held-out windows against "repeat last value". Method is chosen on validation windows only.
- Swiss open data (5 series): `tools/prepare_swiss.py` builds `data/swiss_*.csv`; sources, terms and quality notes in `docs/research/swiss-open-data.md`.
- The dashboard's business-case box and question chips come from `BIZ` in `engine.py`.
- Not visually verified in a browser after the last UI change (the preview tool failed); JS syntax and API responses were checked.
