---
license: apache-2.0
language:
- en
- de
- fr
- es
- ja
pipeline_tag: image-text-to-text
library_name: transformers
base_model: lumenfold/Aurora-Lite-14B-Base
tags:
- chat
- reasoning
- tool-use
---

# Aurora-Lite 14B Instruct

<p align="center">
  <a href="#">Blog</a> | <a href="#">Technical report</a> | <a href="#">Demo</a> | <a href="#">Discord</a>
</p>

## Introduction

**Aurora-Lite 14B Instruct** is the instruction-tuned, mid-sized member of the Aurora-Lite family from Lumenfold Labs, released on **September 23, 2025**. It is designed to run on a single workstation GPU or a 32 GB laptop while staying competitive with larger open models on reasoning, coding and agentic tasks. Compared with the preview checkpoint we shared in July (v0.9-preview, which scored 68.9 on MMLU-Pro and 51.0 on GPQA Diamond), this release adds a vision encoder, a longer context window and a much stronger tool-calling stack.

Highlights:

- **Hybrid reasoning**: a single model that can answer directly or think step by step. Thinking is enabled by default and can be switched off with `enable_thinking=False`.
- **Long context**: natively trained on 32,768-token sequences and extended with YaRN to a full context of 131,072 tokens.
- **Agentic use**: native function calling in the OpenAI-compatible format, tuned on multi-turn tool trajectories.
- **Multilingual**: strong performance in English, German, French, Spanish and Japanese, with basic support for 20+ further languages.

## Model Overview

| Property | Value |
|---|---|
| Type | Causal language model with vision encoder |
| Training stages | Pre-training (18T tokens), SFT, preference optimisation, agentic RL |
| Number of parameters | 14.8B in total (13.9B non-embedding; vision encoder 0.4B included in total) |
| Layers | 48 |
| Attention heads (GQA) | 40 for Q, 8 for KV |
| Context length | 131,072 tokens (native 32,768) |
| Vocabulary size | 151,936 |
| License | Apache 2.0 |
| Release date | 2025-09-23 |

> **Note on memory:** in BF16 the weights need about 29.6 GB. The 4-bit community quantizations (GGUF Q4_K_M) are around 9.0 GB.

## Quickstart

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "lumenfold/Aurora-Lite-14B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto", device_map="auto")

messages = [{"role": "user", "content": "Give me a short introduction to large language models."}]
text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=True)
inputs = tokenizer([text], return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=2048, temperature=0.6, top_p=0.95)
print(tokenizer.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True))
```

For best results in thinking mode we recommend `temperature=0.6`, `top_p=0.95`, `top_k=20`. For non-thinking mode use `temperature=0.7`, `top_p=0.8`.

## Evaluation

All results below are for **thinking mode** unless stated otherwise. Scores for other models are taken from their official reports where available, otherwise reproduced with our internal harness (marked with †).

### Knowledge, reasoning and coding

| Benchmark | Corvus-13B-Chat | **Aurora-Lite 14B Instruct** | Aurora-Lite 8B Instruct | Meridian-15B-it |
|---|---|---|---|---|
| MMLU-Pro | 66.8 | **71.2** | 63.5 | 69.0 |
| GPQA Diamond | 52.1 | **58.4** | 49.7 | 55.3† |
| AIME 2025¹ | 47.9 | **62.7** | 51.2 | 55.6 |
| MATH-500 | 86.4 | **91.3** | 88.0 | 89.7 |
| LiveCodeBench² | 40.2† | **48.9** | 39.4 | 45.1 |
| HumanEval | 82.9 | **87.2** | 81.7 | 85.4 |
| IFEval (strict prompt) | 79.8 | **84.6** | 80.2 | 83.1 |

¹ AIME 2025: average pass@1 over 16 samples. With majority voting over 64 samples, Aurora-Lite 14B Instruct reaches 73.3.
² LiveCodeBench v6, problems released between 2025-02-01 and 2025-05-01.

### Agentic, multimodal and long-context

The table below is transposed: each row is a model.

| Model | SWE-bench Verified | BFCL v3 | τ²-bench³ | MMMU (val) | RULER 128k |
|---|---|---|---|---|---|
| Aurora-Lite 8B Instruct | 28.4 | 63.0 | 44.9 | 55.2 | 71.8 |
| **Aurora-Lite 14B Instruct** | **39.8** | **68.1** | **52.3** | **61.5** | **79.4** |
| Corvus-13B-Chat | 33.0 | 61.7 | 47.5 | n/a | 66.2 |
| Meridian-15B-it | 36.5 | 66.4 | 50.8 | 58.9 | 74.0 |

³ τ²-bench: average over the retail and airline domains (retail alone: 58.7; airline alone: 45.9).

Non-thinking mode is faster but scores lower; for example MMLU-Pro drops to 64.0 and LiveCodeBench to 33.7. See the technical report for the full non-thinking table.

## Limitations

The model can produce incorrect or outdated information, especially about events after its training cutoff (March 2025). Long thinking traces can exceed 16k tokens on hard maths problems; set `max_new_tokens` accordingly. Vision performance on dense documents and charts is weaker than on natural images.

## Citation

```bibtex
@misc{auroralite2025,
  title  = {Aurora-Lite: Efficient Hybrid-Reasoning Models},
  author = {Lumenfold Labs},
  year   = {2025}
}
```
