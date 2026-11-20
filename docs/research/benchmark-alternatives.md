# Benchmark alternatives for the "small, local, cheap" claim

Researched 2026-11-19. Sources are primary (arXiv, Hugging Face model cards and API, official pricing pages) unless marked.
"Unverified" means I could not confirm it from a primary source. Cost assumption: ~1.5k input + ~150 output tokens per report.
GPU memory figures are my arithmetic for bf16 weights only (params x 2 bytes), not measured; add KV cache and overhead.

## Recommendation (add these, in this order, given 3 days and one Nebius GPU)

| # | Add | Why it matters for the claim | Effort | Runs locally | Cost / report |
|---|-----|------------------------------|--------|--------------|---------------|
| 1 | **Template/rule NLG baseline** (computed stats -> "X rose 4.2% to Y in March") | The floor. Zero invented numbers by construction. If the fine-tuned model cannot beat it on directional/numeric accuracy, the LLM adds style, not substance. | ~0.5 day | Yes, CPU | ~0 |
| 2 | **Llama-3.2-1B fine-tuned on series-as-text** (same base, same data, same steps, no TS encoder) + zero-shot **Llama-3.2-1B-Instruct** | Isolates the value of OpenTSLM's native time-series input. This is the comparison reviewers will ask for first. | ~1 day (reuse training loop, swap input) | Yes, ~2.5 GB | GPU time only |
| 3 | **Qwen3.5-4B** (or Qwen3.5-2B), zero/few-shot, series as text | "Why not just prompt a slightly bigger open model?" Same local/private property, no training. | ~2-3 h | Yes, ~8-9 GB | GPU time only |
| 4 | **Claude Haiku 5.5** (`claude-haiku-5-5`), series as text, same prompt as Opus | The cheap end of the frontier. Same SDK as the planned Opus run, so near-zero extra code. | ~1 h | No (API) | ~$0.00023 |
| 5 (stretch) | **ChatTS-8B** (native TS input, free-text answers, Apache-2.0) | The closest existing "native time-series LLM" competitor that can write free text. Shows whether our 1B matches an 8B TSLM. | ~0.5-1 day (custom code, `trust_remote_code`) | Yes, ~16 GB | GPU time only |

Skip for now: Sonnet 5.5 (Opus already covers the top end and Haiku the cheap end), Gemini/OpenAI small models
(adds a second API and SDK for little new information), Time-LLM (forecasts only), ChatTS-14B / TimeOmni-1-7B / Time-MQA (only if time is left).

### Important finding for the pitch: on per-token price alone, cheap APIs are very hard to beat

Claude Haiku 5.5 is ~$0.00023 per report; gpt-5-nano is ~$0.00014. A Nebius H100 is $4.50/GPU-hour on demand, so a local 1B model
breaks even with Haiku only above ~20,000 reports per hour (~5.6 reports/s) of sustained, batched throughput. That throughput is
plausible for a 1B model with vLLM batching but is **unverified**: measure it (reports/hour under batched inference) and report
cost as `$4.50 / measured reports-per-hour`. Lead the claim with **data never leaves the firm's hardware** and use cost as
"comparable to the cheapest APIs, with no per-token bill", unless the throughput measurement supports a stronger statement.
Note also that reasoning-capable API models bill thinking tokens as output (Opus 5.5 cannot disable thinking; set `effort: "low"`),
so real API cost per report can exceed the estimates below. Log actual `usage` from each response.

---

## 1. Small open text-only LLMs (series serialized as text in the prompt)

| Model | Source | Size | License / access | Memory (bf16 weights) | Notes |
|---|---|---|---|---|---|
| Llama-3.2-1B (base) | [HF meta-llama/Llama-3.2-1B-Instruct card](https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct) | 1.23B | Llama 3.2 Community License, gated | ~2.5 GB | Same base as OpenTSLM-SP. Fine-tuning the base on series-as-text is the clean "no encoder" ablation. Released 2024-09-25, 128k context. |
| Llama-3.2-1B-Instruct | same | 1.23B | gated | ~2.5 GB | Zero-shot version of the ablation; cheap to add next to #2. |
| Llama-3.2-3B-Instruct | [HF API](https://huggingface.co/api/models/meta-llama/Llama-3.2-3B-Instruct) | 3.21B | gated | ~6.4 GB | Same family, one size up. Optional. |
| Qwen3.5-0.8B / 2B / 4B / 9B | [HF Qwen/Qwen3.5-2B](https://huggingface.co/Qwen/Qwen3.5-2B), [HF Qwen org listing](https://huggingface.co/api/models?author=Qwen&search=Qwen3.5) | 0.8B-9B | Apache-2.0 | 2B ~4 GB; 4B ~8 GB; 9B ~18 GB | Newest small Qwen line (Feb 2026). Post-trained; non-thinking mode is the default; 262k context; includes a vision encoder (adds some memory). Qwen3.8 (Aug 2026) exists only at 27B and above, so Qwen3.5 is the current small Qwen. |
| Gemma 4 E2B-it / E4B-it | [Gemma 4 model card](https://gemma.ai/models/gemma-4/model-card/), [HF google listing](https://huggingface.co/api/models?author=google&search=gemma-4) | E2B: 2.3B effective (5.1B with embeddings); E4B: 4.5B eff. (8B) | Apache-2.0 | E2B ~10 GB; E4B ~16 GB (full weights incl. embeddings) | Repos `google/gemma-4-E2B-it`, `google/gemma-4-E4B-it`; QAT int4 GGUF variants exist. 128k context. Good alternative to Qwen if you want a second family. |
| Phi-4-mini-instruct | [HF API](https://huggingface.co/api/models/microsoft/Phi-4-mini-instruct) | 3.84B | MIT | ~7.7 GB | Latest small Phi instruct model is still from Feb 2025 (no newer small Phi instruct on HF as of this date). Optional. |

Cost per report for all of these: GPU time only (see the break-even note above). Integration: same prompt builder as the Opus
baseline (series as a text table/CSV), served with vLLM or HF `generate`. Proves: "native TS encoder beats/matches text
serialization at the same size" (Llama-1B) and "1B fine-tuned matches/beats 2-4B general models prompted zero-shot" (Qwen/Gemma).

## 2. Time-series + language models

| Model | Source | Size / base | Weights | Free-text output? | Fit for us |
|---|---|---|---|---|---|
| **ChatTS-8B** | [HF card](https://huggingface.co/bytedance-research/ChatTS-8B), paper [arXiv 2412.03104](https://arxiv.org/abs/2412.03104) (VLDB'25) | Qwen3-8B base (the card also says Qwen2.5-14B-Instruct in one place; inconsistent) | Public, Apache-2.0 | Yes: conversational analysis, attribute/statistic questions; series passed as arrays with `<ts><ts/>` placeholders; vLLM supported | Best native-TS competitor that writes text. ~16 GB. Zero-shot only (no time to fine-tune). |
| ChatTS-14B | [HF card](https://huggingface.co/bytedance-research/ChatTS-14B) | Qwen2.5-14B-Instruct | Public, Apache-2.0 | Yes | ~28-30 GB, fits one H100. A GPTQ-Int4 and a "14B-0801" release are mentioned in search snippets of the project repo (unverified on HF). |
| TimeOmni-1-7B | [arXiv 2509.24803](https://arxiv.org/abs/2509.24803) (ICLR 2026), [HF](https://huggingface.co/anton-hugging/TimeOmni-1-7B) | Qwen2.5-7B-Instruct, 7.6B | Public, Apache-2.0 | Yes (reasoning text; text-generation pipeline). Whether series go in as text or a special encoder: unverified | Reasoning tasks (causality, event-aware forecasting); a stretch alternative to ChatTS. |
| Time-MQA | [arXiv 2503.01875](https://arxiv.org/abs/2503.01875) (ACL 2025), [HF org](https://huggingface.co/api/models?author=Time-MQA) | Mistral-7B, Llama-3-8B, Qwen-2.5-7B (continued pretraining on ~200k TS QA pairs) | Public (`Time-MQA/Qwen-2.5-7B` etc.), license unverified | QA incl. open-ended reasoning; series as text | Text-only LLMs tuned on TS QA. Optional. |
| OpenTSLM-Flamingo | [arXiv 2510.02410](https://arxiv.org/abs/2510.02410) | Llama-3.2-1B / Gemma-3 bases | Public checkpoints on HF (e.g. `OpenTSLM/llama-3.2-1b-tsqa-sp`; Flamingo names unverified) | Yes | The other OpenTSLM variant (cross-attention). Interesting internal ablation, not a competitor. |
| ChatTime | [arXiv 2412.11376](https://arxiv.org/abs/2412.11376) (AAAI 2025) | Size/base not stated in abstract | Unverified | Bimodal in/out, but focus is zero-shot forecasting | Low priority. |
| Time-LLM | [arXiv 2310.01728](https://arxiv.org/abs/2310.01728) (ICLR 2024) | Reprogrammed frozen LLM | Code public | **No**: outputs forecasts only | Not applicable to report generation. |
| OpenTSLM TeeMoE | [NeurIPS 2026 listing](https://neurips.cc/virtual/2026/175111) | Unverified | Unverified | Unverified | Watch; do not plan on it. |

Relevant evaluation literature (useful for the write-up, not systems to run):
- **BEDTime** ([arXiv 2509.05215](https://arxiv.org/abs/2509.05215)): first benchmark for automatically describing time series; 17 models;
  vision-language models did well, language-only methods worst, dedicated TSLMs "fall short", all fragile under robustness tests.
  Supports including both a text-only LLM and a TSLM baseline.
- **Do Time-Series QA Systems Read the Time Series?** ([arXiv 2610.05686](https://arxiv.org/abs/2610.05686), Oct 2026): intervenes on the
  input series (question fixed) for ChatTS, TimeOmni-1, Time-MQA; finds fallback behavior and rationales with unsupported numbers.
  Directly motivates your shuffled-series ablation and invented-number rate.
- **TSQueryBench** ([arXiv 2604.02118](https://arxiv.org/abs/2604.02118)): models that write numerically wrong explanations can still judge
  them well; supports an optional LLM-judge alongside your code-based checks.

## 3. Cheaper frontier API models (official pricing pages, fetched 2026-11-19)

Cost per report = 1,500 x input price + 150 x output price (per 1M tokens), standard tier, excluding thinking tokens.

| Model | Pricing source | Input $/MTok | Output $/MTok | ~$/report | Notes |
|---|---|---|---|---|---|
| Claude Opus 5.5 `claude-opus-5-5` (already planned) | [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing) | 4.00 | 20.00 | 0.0090 | Thinking cannot be disabled; use low effort. Batch API: 50% off. |
| Claude Sonnet 5.5 `claude-sonnet-5-5` | same | 2.00 | 10.00 | 0.0045 | Optional middle point. |
| **Claude Haiku 5.5 `claude-haiku-5-5`** | same | 0.10 (prompts <=100k) | 0.50 | **0.00023** | Batch: $0.05 / $0.25. Recommended. |
| gpt-6-luna (OpenAI, newest small tier) | [OpenAI pricing](https://developers.openai.com/api/docs/pricing) | 0.10 | 0.50 | 0.00023 | Same price as Haiku 5.5. |
| gpt-5-nano (older gen) | same | 0.05 | 0.40 | 0.00014 | Cheapest API found. |
| gpt-5.4-nano | same | 0.20 | 1.25 | 0.00049 | |
| gemini-3.1-flash-lite | [Google AI pricing](https://aistudio.google.com/docs/pricing) | 0.25 | 1.50 | 0.00060 | Cheapest Gemini; output price includes thinking. |
| gemini-3.6-flash / 3.8-flash | same | 0.75 (1.50 from 2027-01-01) | 3.75 (7.50 from 2027-01-01) | 0.0017 | Prices double on 2027-01-01. |

Effort: Claude models ~1 h each (same SDK and prompt as Opus). Other providers: ~2-3 h each (new SDK, key, retries).
Proves: where on the accuracy/cost curve our model sits relative to the cheapest frontier tiers; and that the remaining
advantage is privacy/on-prem, not only price. For local cost use [Nebius prices](https://nebius.com/prices): H100 $4.50/GPU-h,
H200 $5.40, L40S from $1.55 (on demand, excl. VAT). An L40S (48 GB) would also run the 1B model and lowers the break-even.

## 4. Non-LLM baselines: template / rule-based data-to-text

What to build (half a day): compute from the window the same quantities your evaluator checks (direction over window,
percent change first->last, largest period-over-period change and its date, latest value vs min/max, optional
seasonal comparison), then fill 3-5 fixed sentence templates. Variants worth reporting:
- **Template-full**: all computed facts. Upper bound on numeric accuracy, zero invented numbers; usually stilted.
- **Repeat last period's report** (already planned): checks whether the model just copies style from history.

Literature showing this is an accepted baseline class:
- Reiter, "An Architecture for Data-to-Text Systems", ENLG 2007 ([ACL W07-2315](https://aclanthology.org/W07-2315/)): the classic
  pipeline (signal analysis -> data interpretation -> document planning -> realisation) behind rule-based time-series NLG (e.g. SumTime weather forecasts; the SumTime system papers themselves I did not re-verify).
- Murakami et al., "Learning to Generate Market Comments from Stock Prices", ACL 2017 ([P17-1126](https://aclanthology.org/P17-1126)):
  neural generation of market commentary from price series with explicit numeric operations; a third-party summary says the
  baseline was more fluent but far less informative because it could not output numbers (baseline type not verified from the PDF).
- Jhamtani & Berg-Kirkpatrick, "Truth-Conditional Captions for Time Series Data", EMNLP 2021 ([2021.emnlp-main.55](https://aclanthology.org/2021.emnlp-main.55), [arXiv 2110.01839](https://arxiv.org/abs/2110.01839)):
  generates captions conditioned on learned programs that are checked to be true on the series; motivated by fluent but
  factually wrong neural captions. Closest prior work to your "check claims against the series" evaluation.

Proves: whether the fine-tuned model adds value beyond deterministic statistics. Expect templates to win on numeric
accuracy and lose on "what moved and why"/fluency; frame that honestly (an LLM is justified only if it covers more
salient facts at a comparable invented-number rate, or if templates cannot match the target `fact` style).

---

## Suggested results table (one row per system)

Columns: params | runs on-prem | directional acc. | numeric acc. | invented-number rate | QA accuracy (direction,
largest change, latest vs range) | $/report (API: from logged usage; local: GPU-h price / measured throughput) | latency.
Rows: template, repeat-last, Llama-1B-Instruct zero-shot, Llama-1B text fine-tuned, Qwen3.5-4B, OpenTSLM pretrained,
OpenTSLM fine-tuned, OpenTSLM fine-tuned + shuffled series, (ChatTS-8B), Claude Haiku 5.5, Claude Opus 5.5.

## Open items / unverified
- Real throughput of the 1B model on one Nebius GPU (determines whether "cheaper than APIs" holds). Measure it.
- ChatTS-8B exact base (card is inconsistent), memory use, and whether it handles Time-MMD window lengths well.
- TimeOmni-1 input format (text vs encoder); Time-MQA model licenses; OpenTSLM Flamingo checkpoint names.
- Gemini/OpenAI prices were read via a page summarizer; re-check the pages before quoting in the final slides.
