# OpenTSLM capabilities (commit 2968f4b)

Source: https://github.com/OpenTSLM/OpenTSLM @ `2968f4b891baab4307f7e9d0043e87677b593a30` (default branch, 2026-07-17). I read the code only and did not install or run anything. The clone is deleted. I also read the README, the paper (arXiv 2510.02410v3, 14 Feb 2026, HTML; Appendix A.1 onward and Figure 4 / Table 11 were not read word for word), the HF org page and two model cards, and the `open-flamingo` 0.0.2 sdist (the version pinned in `uv.lock:2096-2097`; sha256 checked).
Paths below are relative to the repo root. **[unconfirmed]** marks claims I could not check.

## What this means for us

- **Several series per prompt: yes, in both variants.** A sample is a list of `(text label, 1-D series)` pairs placed between a pre-prompt and a post-prompt. The repo already trains on 3 series (HAR x/y/z), 12 (ECG leads) and up to 24 (two ECG recordings). So the *format* covers Level 1 (total + components) and Level 3 (KPI + covariate).
- **Use SP for our questions, not Flamingo.** In SP each series' soft tokens sit directly after its own text label, so the LLM can tell which series is which. In Flamingo, every series in a sample is stacked into one "media" item. The Perceiver then squashes them all into 64 latents, with no per-series embedding. The labels are not tied to their series in cross-attention (see section 2). Asking which component drove the total needs that link.
- **The model never sees levels, only shapes.** Each series is z-scored on its own, and the mean and std go into the text label as strings. So "components add up to the total" cannot be seen in the series embeddings. **Our tool code must compute the additive split (shares, deltas) and put it in the prompt text**, or the model must read numbers from the labels, which it was never trained to do.
- **No dates, frequency or units in the time-series input.** None of the dataset classes passes timestamps. The only position signal is a learned per-patch embedding (patch = 4 points). "Same month last year" (Level 2) can only work if we state the dates and frequency in the text. The model would then still have to count patches back, which it was never trained for. **Precompute YoY in code and pass it as text.** (This is my inference from the code; untested.)
- **Must go in each series label:** name and role ("Total revenue", "Component: Region EU", "Covariate: marketing spend"), unit, frequency, start and end date, length, and `mean=…, std=…` in the existing style. Facts we computed ourselves (component deltas, YoY %) go in the pre- or post-prompt. Series in one sample are zero-padded to the longest one, so **align every series to the same date range and length.**
- **Fine-tuning is needed.** The released checkpoints are trained on medical, HAR and M4-caption tasks. None does decomposition or covariate reasoning. A TimeNet adapter is a small `QADataset` subclass (section 5). There is no existing TimeNet integration (grep for `timenet` finds nothing).
- **Hardware:** use CUDA. Apple Silicon (MPS) is officially "does NOT work" for the released checkpoints (README:91). CPU inference is supported. Using any checkpoint needs gated access to `meta-llama/Llama-3.2-1B` on Hugging Face, because the base weights are downloaded at load time.

## 1. Variants and base LLMs

**OpenTSLM-SP (soft prompt)**, `src/opentslm/model/llm/OpenTSLMSP.py`
- Encoder `TransformerCNNEncoder`: a Conv1d patch embed (kernel = stride = 4), a learned positional embedding (`max_patches=1024`), then 6 Transformer layers with 8 heads, d=128 and ff=1024 (`model/encoder/TransformerCNNEncoder.py:15-66`).
- Projector `MLPProjector`: LayerNorm, then Linear(128 to hidden_size), then GELU (`model/projector/MLPProjector.py:13-18`).
- Each series becomes `ceil(L/4)` LLM input embeddings. These are interleaved as `[pre_prompt, text_1, ts_1, text_2, ts_2, …, post_prompt]` (`OpenTSLMSP.py:223-310`). The LLM is frozen (`:66-68`). LoRA (r=16, alpha=32, all attention and MLP projections) is switched on for stages 3-5 (`curriculum_learning.py:1547-1563`).

**OpenTSLM-Flamingo**, `src/opentslm/model/llm/OpenTSLMFlamingo.py`
- Encoder `CNNTokenizer`: a Conv1d patch embed plus positional embedding only, with no Transformer (`model/encoder/CNNTokenizer.py:37-48`).
- Then an open_flamingo `PerceiverResampler` (64 latents by default, `open_flamingo/src/helpers.py:76`), then gated cross-attention after **every** decoder layer (`cross_attn_every_n_layers=1`, `curriculum_learning.py:166-171`).
- Trainable parts: the encoder, the Perceiver, the cross-attention layers and the LM input embeddings (`OpenTSLMFlamingo.py:137-149`).
- The prompt text is `pre_prompt <image> label_1 <|endofchunk|> <image> label_2 <|endofchunk|> … post_prompt` (`:205-211`). Note that here the series token comes before its label, while SP puts the label first.

**Base LLMs** (README:58-72): `meta-llama/Llama-3.2-1B` (default), `meta-llama/Llama-3.2-3B`, `google/gemma-3-270m`, `google/gemma-3-1b-pt`. The HF loader maps checkpoint names to base IDs in `model/llm/OpenTSLM.py:153-171`. Gemma uses `google/gemma-3-1b` there. The paper's Table 2 note says Gemma has a 32k context and Llama 128k.

## 2. Multiple series per sample

Data structures, in `src/opentslm/prompt/`:
- `TextTimeSeriesPrompt(text: str, time_series)` holds **one** 1-D numeric non-empty series. 2-D input is rejected with "You can input multiple time series, but each … must be one-dimensional" (`text_time_series_prompt.py:20-37`).
- `PromptWithAnswer(pre_prompt, [TextTimeSeriesPrompt…], post_prompt, answer).to_dict()` produces the sample dict `{pre_prompt, time_series: [arrays], time_series_text: [labels], post_prompt, answer}` (`prompt_with_answer.py:17-45`). `FullPrompt` is the same thing without an answer, used for inference (`full_prompt.py:11-40`).
- The collate step `extend_time_series_to_match_patch_size_and_aggregate` stacks a sample's series into `[N_ts, L_pad]`. It **zero-pads every series to the longest in the sample**, rounded up to a multiple of 4 (`time_series_datasets/util.py:46-64`). SP does not mask this padding: patch tokens all get attention mask 1 (`OpenTSLMSP.py:296-300`).

Example from an existing dataset, `HARCoTQADataset` (`time_series_datasets/har_cot/HARCoTQADataset.py:20-24, 113-145`):
```python
TIME_SERIES_LABELS = ["The following is the accelerometer data on the x-axis", ...y..., ...z...]
means = series.mean(dim=1, keepdim=True); stds = series.std(dim=1, keepdim=True).clamp(min=1e-6)
series_norm = (series - means) / stds
text_prompt = f"{time_series_label}, it has mean {mean:.4f} and std {std:.4f}:"
prompts.append(TextTimeSeriesPrompt(text_prompt, time_series))
```
Other multi-series datasets:
- `ECGQACoTQADataset` builds 12 leads per recording, labelled `"This is ECG Lead II (Recording 2), it has mean … and std …:"`. Comparison questions carry two recordings (`ecg_qa/ECGQACoTQADataset.py:422-480`).
- `SimulationQADataset(length, num_series)` builds synthetic N x L data (`simulation/SimulationQADataset.py:20-112`). The memory sweep runs N = 1-5 and L = 10 to 10,000 (`evaluation/memory/run_all_memory.sh`).

Limits:
- No explicit cap on the number of series.
- **Per-series length is at most 4096 points** in both variants (1024 patches x 4). Longer series raise `ValueError` unless you change `max_patches` (`TransformerCNNEncoder.py:93-96`, `CNNTokenizer.py:79-82`).
- SP: the total LLM sequence (text plus the sum of ceil(L_i/4)) is bounded by the LLM context and by VRAM.
- Flamingo: the LLM sequence holds only text. The series cost Perceiver compute over N x L/4 tokens.
- Flamingo `torch.stack`s per-sample tensors (`OpenTSLMFlamingo.py:184`), so every sample in a batch must have the same number of series. **[inference from code]**

**Flamingo series identity (code reading, not run):**
- The input is reshaped to `[B, 1, N_ts, L]` (`OpenTSLMFlamingo.py:194-197`), so the series are the "frames" of one media item (`TimeSeriesFlamingoWithTrainableEncoder.py:30-45`).
- The Perceiver flattens `b T F v d -> b T (F v) d` with no frame embedding, because `max_num_frames=None` (`open_flamingo/src/flamingo.py:36`, `helpers.py:118-123`).
- In 0.0.2 the cross-attention masks text to "immediate media" by counting `<image>` tokens (`helpers.py:190-225`). With N `<image>` tokens but only one media item, only text up to and including the first `<image>` token attends normally. Label tokens of series 2 to N get uniform attention over all latents. Label 1 and the text after the last `<image>` (last label, post-prompt, answer) get zero cross-attention.
- I did not verify this at runtime, and a newer open_flamingo version would behave differently. Either way, labels are not bound to their own series.

## 3. Normalization and metadata

- **Per-series z-score is done inside each dataset class.** Examples: HAR `:113-121`, ECG `:401-411`, Sleep `sleep/SleepEDFCoTQADataset.py:47-54`, M4 `m4/M4QADataset.py:90-98`. In TSQA (`TSQADataset.py:68-75`) the 1-D series is normalized with `dim=0`, i.e. over the whole series.
- The collate function also has a `normalize` flag, but it defaults to False (`util.py:18-44`).
- **Mean and std are passed as text in the label** (`"it has mean X and std Y:"`, 4 decimals).
- The paper says the encoder "expects inputs normalized to x∈[−1,1]" and that the text should carry "mean, standard deviation, and time scale", for example "heart-rate data over 24 hours sampled at 50 Hz with mean=61 and std=12" (§3.1). The code uses z-score, not [-1,1].
- **Dates, frequency, units:** no dataset class passes timestamps. M4 knows the frequency (`m4/m4_loader.py:40`), but its prompt is a fixed "You are an expert in time series analysis." (`M4QADataset.py:55-73`). The paper's limitations admit the "rely on including the mean and standard deviation in accompanying texts".
- Metadata can only enter as free text in the labels or the pre/post prompt.
- **"Same month last year"** is not reliably answerable from text dates alone (see top). **[unconfirmed, no experiment]**

## 4. Length and context

- Per-series maximum is 4096 points by default (section 2). There is no automatic truncation or downsampling. Downsampling is done by hand per dataset; for example ECG takes 500 Hz down to 100 Hz with `[::5]` (`ECGQACoTQADataset.py:393`).
- Patching is fixed at `PATCH_SIZE=4` (`model_config.py:12`).
- SP token cost is ceil(L/4) per series. The paper gives "12 ECG leads of 10s tokenize to 80k tokens, requiring >100GB VRAM" (Table 2 note), but that refers to the *text-tokenized* baseline. SP costs 12 x 250 = 3000 soft tokens there.
- The SP text tokenizer runs with `truncation=True` and no `max_length`, so the tokenizer's model maximum applies (`OpenTSLMSP.py:237-239`).
- Small hazard: `QADataset._format_sample_str` uses `sys.maxsize` but `QADataset.py` never imports `sys` (`:108-113`). The text-only baseline path would crash. **[inference from code]**

## 5. Dataset interface (for a TimeNet adapter)

Subclass `QADataset` (`time_series_datasets/QADataset.py:17-100`) and implement:
- `_load_splits() -> (train, val, test)`. Each is an indexable collection of rows; HF `Dataset` or a list of dicts both work.
- `_get_pre_prompt(row) -> str`: instructions and question.
- `_get_text_time_series_prompt_list(row) -> List[TextTimeSeriesPrompt]`: one entry per series, already z-scored, with the label carrying mean and std.
- `_get_post_prompt(row) -> str`, e.g. `"Answer:"` or `"Rationale:"`.
- `_get_answer(row) -> str`. EOS is appended automatically (`:91-93`). The loss covers answer tokens only (SP `OpenTSLMSP.py:330-363`; Flamingo `:233-242`).
- Constructor: `(split, EOS_TOKEN, format_sample_str=False, time_series_format_function=None)`. Splits are cached as class attributes (`:40-56`), so one class equals one fixed dataset.
- You can override `_format_sample` to keep extra fields for evaluation (HAR `:163-169`).

Existing answer formats:
- MCQ letter or answer (TSQA, post-prompt `"Predict the {Task} Answer:"`).
- Free caption (M4).
- CoT paragraph ending in `"Answer: <label>"` (HAR, Sleep, ECG pre-prompts, e.g. `HARCoTQADataset.py:61-87`).
- The curriculum scores the label after "Answer:" (`curriculum_learning.py:686-704`, `_calculate_accuracy`).

To train on it, add a stage method like `stage1_mcq` (`curriculum_learning.py:1232-1255`) and its name to the stage list (`:61-67`). **No TimeNet integration exists.**

## 6. Training

- **Entry point:** `curriculum_learning.py --model {OpenTSLMSP|OpenTSLMFlamingo} --stages … --llm_id … --batch_size … --gradient_checkpointing --device`. DDP is supported (README:199-238).
- **Stages:** stage1_mcq (TSQA, 30 epochs), stage2_captioning (M4, 20), stage3_cot (HAR, 30), stage4_sleep_cot (60), stage5_ecg_cot (60) (`curriculum_learning.py:1232-1353`). Each stage loads the best checkpoint of the stage before. The paper groups these as stage one (TSQA + M4 "encoder warmup") and stage two (the CoT sets).
- **Hyperparameters** (`model_config.py:10-24`, `curriculum_learning.py`):
  - Batch 4, AdamW, linear schedule with 3% warmup (`:1043-1050`). The paper summary says 10% warmup, which does not match **[unconfirmed]**.
  - Grad clip 1.0. Early stopping with patience 5 on validation loss.
  - SP: encoder LR 2e-4, projector and LoRA LR 1e-4, weight decay 0.01.
  - Flamingo: LR 2e-4, weight decay 0.1 on cross-attention and 0 elsewhere (`:270-300`).
- **GPU memory:** the paper reports training VRAM (peak per step at batch size 1, `evaluation/memory/get_memory_use.py:101-108, 173`):
  - Flamingo stays near-constant across datasets and grows little with N and L. It reaches "up to 60GB for Llama-3.2-3B with five 10,000-length series" (§5).
  - SP grows with N and L: ">180GB in simulations with 10,000-length series" (§5), and "around 110 GB compared to 40 GB VRAM when training on ECG-QA with LLaMA-3B" (abstract).
  - **Per-dataset GB numbers for Llama-3.2-1B (Figure 4 / Table 11) were not readable [unconfirmed].** Short single-series tasks (TSQA, M4) with a 1B model are likely to fit on a 24-40 GB GPU. That is a guess, not a reported number.
- **Training time and GPU type:** not found in the repo or in the parts of the paper I read **[unconfirmed]**.

## 7. Inference

- No inference latency or memory figures are reported in the repo or paper (as far as I read).
- Weights are bf16 for SP (`OpenTSLMSP.py:44-49`). Flamingo loads the LLM at its default dtype (`OpenTSLMFlamingo.py:59-66`), probably fp32 **[unconfirmed]**.
- A 1B model is roughly 2.5 GB of weights in bf16, plus a small encoder.
- **CPU:** supported, and used by the demos and card code as the fallback.
- **MPS:** auto-selected if available (`model/llm/OpenTSLM.py:112-114`). The README (:91, :195-197) and the model cards say "MPS does NOT work for pretrained HF checkpoints". Training on MPS gives a warning (`curriculum_learning.py:128-131`).
- **Security:** the SP checkpoint load uses `torch.load(..., weights_only=False)` (`OpenTSLMSP.py:380`; also `curriculum_learning.py:477, 620`). Loading a `.pt` file can therefore run arbitrary pickled code. Only load trusted checkpoints.

## 8. Licenses

- **Code: MIT** (`LICENSE.md`, `LICENSES/MIT.txt`, `pyproject.toml` `license = "MIT"`, REUSE annotations in `REUSE.toml`).
- **Checkpoints:** 52 models under `huggingface.co/OpenTSLM`, named `{llama-3.2-1b|llama-3.2-3b|gemma-3-1b-pt|gemma-3-270m[-pt]}-{tsqa|m4|har|sleep|ecg}-{sp|flamingo}`, plus `TeeMoE` and `llama3b-ecg-flamingo`.
  - The cards checked (`llama-3.2-1b-tsqa-sp`, `llama-3.2-1b-ecg-flamingo`) say "released under the MIT license". They are not gated and have no YAML license metadata.
  - The cards do not mention base-model license inheritance. These are derivatives of Llama 3.2 or Gemma 3, so the base terms still apply.
- **Llama 3.2 Community License** (from the meta-llama/Llama-3.2-1B page):
  - Commercial use is allowed. A separate Meta license is needed above 700M monthly active users (§2).
  - You must show "Built with Llama" visibly and start any distributed derivative model's name with "Llama" (§1.b.i). You must ship the Notice file (§1.b.iii).
  - The Acceptable Use Policy applies (§1.b.iv).
  - HF access is gated: you must accept the terms and share your HF info.
  - The EU-domicile exclusion covers only Llama 3.2 *multimodal* models, not the 1B text model.
  - OpenTSLM's lowercase `llama-…` names may not satisfy the naming rule (not legal advice).
- **Gemma:** governed by Google's Gemma Terms of Use (gated on HF per README:44). **[terms not read in detail]**
