# Database schema — `data/results.json` (schema_version 1)

One JSON file. Written atomically (temp file + rename) by the CLI. The dashboard
receives it from `GET /api/db`, with `data/overrides.json` already merged in.

```jsonc
{
  "schema_version": 1,
  "tool_version": "0.1.0",
  "updated_at": "2026-10-19T22:14:03Z",

  "machines": {
    "<machine_id>": {                       // e.g. "Mac16,10-M4Pro-64GB" (stable, no hostname)
      "machine_id": "...",
      "label": "Mac mini M4 Pro 64GB",       // human-friendly
      "model_name": "Mac mini", "model_identifier": "Mac16,10",
      "chip": "Apple M4 Pro",
      "cpu_cores": 18, "cpu_cores_detail": "6 Super + 12 Performance",
      "gpu_cores": 20,
      "memory_bytes": 68719476736,
      "disk_bytes": 994662584320,
      "os": "macOS", "os_version": "27.0.1", "arch": "arm64",
      "specs_extra": { "memory_bandwidth_gbps": 307, "notes": "..." }  // optional, manual
    }
  },

  "models": {
    "<model_uid>": {                        // "<engine>:<key>@<variant>"  e.g. "lmstudio:google/gemma-4-31b-qat@q4_0"
      "model_uid": "...",
      "engine": "lmstudio",                 // "lmstudio" | "ollama"
      "key": "google/gemma-4-31b-qat",
      "variant": "q4_0",
      "display_name": "Gemma 4 31B QAT",
      "publisher": "google",
      "architecture": "gemma4",
      "params_string": "31B",
      "params_total_b": 31.0,               // null if unknown
      "params_active_b": null,              // MoE active params, else null
      "is_moe": false,                      // from the name, the architecture, HF config.json or overrides
      "params_active_source": null,         // "name" | "model card" | "estimated from config.json" |
                                            // "estimated from GGUF metadata" (estimates are rough)
      "moe_experts": null, "moe_experts_per_token": null,   // MoE only
      "format": "gguf",                     // "gguf" | "mlx" | "safetensors" | other
      "quantization": { "name": "Q4_0", "bits": 4 },
      "qat": true,
      "size_bytes": 18851800193,
      "max_context_length": 262144,
      "capabilities": {
        "vision": true, "tool_use": true,
        "reasoning": { "allowed_options": ["off","on","high"], "default": "on" }  // or null
      },
      "fingerprint": "sha1 of key+variant+size",
      "first_seen": "...", "last_seen": "..."
    }
  },

  "runs": [
    {
      "run_id": "20261019T221403Z-lmstudio-google-gemma-4-31b-qat",
      "model_uid": "...",
      "machine_id": "...",
      "started_at": "...", "finished_at": "...",
      "status": "complete",                 // "complete" | "partial" | "failed"
      "error": null,
      "tool_version": "0.1.0",
      "suite_version": "1",
      "profile_name": "standard-v1",
      "profile_hash": "ab12cd34",
      "profile": { "context_length": 81920, "temperature": 0, "top_p": 1, "top_k": 1, "seed": 42,
                   "repeats": 3, "warmup": 1, "max_tokens": {...} },
      "engine_info": { "name": "LM Studio", "version": "0.4.x", "runtime": "llama.cpp-metal|mlx-engine", "base_url": "http://localhost:1234" },
      "load_config": { "context_length": 81920, "flash_attention": true, "eval_batch_size": 512,
                       "offload_kv_cache_to_gpu": true, "num_experts": null, "parallel": 4 },

      "cold_start": {
        "cycles": [
          { "cycle": 1, "load_time_s": 9.1, "first_ttft_s": 0.82, "loaded_footprint_bytes": 18900000000 },
          { "cycle": 2, "load_time_s": 4.3, "first_ttft_s": 0.31, "loaded_footprint_bytes": 18900000000 }
        ],
        "warm_ttft_s": 0.12             // same short prompt, model already warm (median)
      },

      "memory": {
        "method": "footprint",          // "footprint" (macOS) | "process-rss" (Windows/Linux) | "engine-api"
        "system_total_bytes": 68719476736,
        "snapshots": {                   // engine process footprint, bytes (null if unavailable)
          "idle": 520000000,            // engine running, no model loaded
          "loaded_empty": 18900000000,  // model loaded, empty context
          "after_short": 19100000000,
          "after_long_prompt": 26400000000,  // right after the ~70k-token document was processed
          "end": 26500000000
        },
        "peak_bytes": 27000000000,
        "system_used_peak_bytes": 52000000000,
        "swap_used_delta_bytes": 0,
        "raw_file": "raw/<run_id>.json" // timeline lives here: [{t, engine_bytes, system_used_bytes, phase}]
      },

      "tests": {
        "short": {
          "off":  TestResult,
          "high": TestResult              // may be missing if not supported / not run
        },
        "long":       { "off": TestResult, "high": TestResult },
        "extraction": { "off": TestResult, "high": TestResult }
      },

      "summary": {                         // flattened numbers for tables/sorting (medians). null if n/a.
        "short_off_ttft_s": 0.14, "short_off_decode_tps": 31.2, "short_off_prefill_tps": 820,
        "short_high_ttft_s": 0.15, "short_high_first_visible_s": 6.3, "short_high_decode_tps": 30.8,
        "short_high_reasoning_tokens": 812,
        "long_off_ttft_s": 41.2, "long_off_prefill_tps": 1690, "long_off_decode_tps": 22.5,
        "long_off_followup_ttft_s": 0.9, "long_off_recall": 0.9,
        "long_high_first_visible_s": 60.1, "long_high_decode_tps": 22.1, "long_high_recall": 1.0,
        "extraction_off_total_s": 9.2, "extraction_off_accuracy": 0.92, "extraction_off_json_valid": true,
        "extraction_high_total_s": 40.0, "extraction_high_accuracy": 1.0,
        "cold_load_s": 9.1, "warm_load_s": 4.3, "cold_first_ttft_s": 0.82, "warm_ttft_s": 0.12,
        "mem_loaded_gb": 17.6, "mem_long_gb": 24.6, "mem_peak_gb": 25.1,
        "long_off_recall_start": 1.0, "long_off_recall_middle": 0.75, "long_off_recall_end": 1.0,
                                            // per document section; null for runs before answers were stored
        "long_high_recall_reasoning": 1.0,  // secondary: recall on the reasoning text (null when not available)
        "extraction_high_accuracy_reasoning": 0.95,
        "long_high_answer_in_reasoning_turns": 0,   // per test/mode; null when not checked
        "extraction_high_no_answer_scored": 2,   // per test/mode: scored answers (recall questions, the extraction
        "extraction_high_scored_answers": 3,     //   answer) that never arrived because thinking used the budget; null: not checked
        "swap_growth_gb": 0.0               // swap growth during the run (warning above swap_warning_gb)
      },
      "preflight": { "waited_s": 3.0, "free_gb": 42.4, "swap_used_gb": 0.0, "model_gb": 6.4 },
                                            // memory right before the model was loaded (after the cleanup pause)
      "warnings": ["..."],                  // incl. "swap grew by …", "started with … swap", "only … GB free",
                                            // and "… written only in the reasoning channel …"
      "contamination_events": [ {           // another model was loaded during the run
        "t": "...", "test": "long/high", "intruders": ["lmstudio:google/gemma-4-26b-a4b-qat"],
        "action": "abandoned at long/high/r0/t1; intruders unloaded; restarted (restart 1 of 3)",
        "detail": "other model loaded during long/high: … — <action>" } ],
      "stopped_by_intruders": ["..."],      // only when the restart limit stopped the model (status "partial")
      "reloads": [ { "t": "...", "test": "long/high", "unload_load_s": 6.1, "load_time_s": 4.2 } ]
                                            // only for engines that keep working on a cancelled request;
                                            // never counted as a measured load time
    }
  ],

  "public": {
    "<model_uid>": {
      "hf_repo": "google/gemma-4-31b-it",
      "base_model": "google/gemma-4-31b",
      "family": "Gemma 4",
      "license": "gemma",
      "release_date": "2026-04-02",
      "params_b": 31.0, "context_window": 262144,
      "modalities": ["text","image"],
      "links": [ { "label": "Model card", "url": "https://huggingface.co/..." } ],
      "benchmarks": [
        { "name": "GPQA Diamond",          // canonical name
          "raw_name": "GPQA-Diamond (0-shot)",
          "category": "reasoning",         // reasoning|knowledge|math|coding|agentic|vision|long_context|instruction_following|other
          "score": 71.3, "unit": "%",
          "applies_to": "base",            // "exact" (this quant) | "base" (the unquantized model)
          "method": "card-table",          // api|card-table|leaderboard|web|local-llm:<model_uid>|manual
          "effort": "high",                // reasoning effort the source ran (null if not stated)
          "effort_end": "max",             // "max" | "min" when the source ran several efforts (both kept; the
                                           // "min" entry is shown beside the main one, never averaged), else null
          "source_url": "https://...", "retrieved_at": "..." }
      ],
      "efforts": { "api": ["low", "high"], "leaderboard": ["low", "medium", "high"] },
                                            // reasoning efforts each source's scores were measured at
      "moe": { "experts": 32, "experts_per_token": 4, "params_active_b": 3.6,
               "active_source": "model card", "source_url": "https://huggingface.co/…/config.json" },
                                            // only for mixture-of-experts models
      "updated_at": "..."
    }
  }
}
```

### TestResult

```jsonc
{
  "reasoning_requested": "off",            // "off" | "high"
  "reasoning_applied": "off",              // "off" | "high" | "on" | "default" | "unsupported"
  "repeats": 3,
  "turns": [
    {
      "turn": 1, "label": "Load document + question",
      "prompt_tokens": 71234,              // engine-reported (median)
      "completion_tokens": 120, "reasoning_tokens": 0,
      "ttft_s":        { "median": 41.2, "min": 40.9, "max": 41.8, "n": 3 },  // first token of any kind
      "first_visible_s": { ... },          // first non-reasoning token
      "prefill_tps":   { ... },
      "decode_tps":    { ... },
      "total_s":       { ... },
      "answer_in_reasoning": 0,            // repeats whose visible answer was empty, answer in the reasoning text
      "no_answer_budget": 0                // repeats with no visible answer because thinking used the whole budget
    }
  ],
  "answer_in_reasoning_turns": 0,          // total over turns and repeats (backfilled for older runs)
  "no_answer_budget_turns": 0,             // total answers that never arrived: thinking ran out of budget (scored wrong)
  "answers_total": 3,                      // turns x repeats checked
  "cache_hit_ttft_s": 0.4,                 // turn 1 re-sent identically (prompt cache), optional
  "quality": {                             // test-specific, all optional
    "recall_correct": 9, "recall_total": 10, "recall": 0.9,      // long (official: visible answer)
    "facts": [ { "id": "f1", "section": "start", "position_pct": 3.1, "expected": "TANGERINE-4471",
                 "hits": 3, "of": 3 } ],                         // long: per fact over the repeats
    "recall_by_section": { "start": 1.0, "middle": 0.75, "end": 1.0 },
    "recall_reasoning": 1.0, "recall_reasoning_correct": 10,      // long, thinking on: on the reasoning text
    "accuracy_reasoning": 0.95,                                   // extraction, thinking on: on the reasoning text
    "json_valid": true, "accuracy": 0.92, "fields_correct": 23, "fields_total": 25   // extraction
  },
  "totals": { "wall_s": 132.1, "output_tokens": 1450 }
}
```

### Dashboard API (served by `bench dashboard`)

- `GET /api/db` → merged database (above).
- `GET /api/raw/<run_id>` → raw trace `{ "memory_timeline": [{ "t": 0.25, "engine_bytes": ..., "system_used_bytes": ..., "phase": "load" }], "requests": [...] }`.
  Each request record also has `"text"` (the visible answer; from 2026-10-21), `"outcome"`
  (`"answer_in_reasoning_channel"`, `"no_answer_thinking_budget"` or null) and, only with `bench run --store-reasoning`, `"reasoning_text"`.
  Prompts are never stored. `bench publish` removes `text`/`reasoning_text` unless `--include-answers` is given.
  When a test was interrupted because another model was loaded, its requests and memory samples stay in the raw
  file with `"discarded": true` (requests also carry `"discard_reason"`; the cancelled one has `"abandoned": true`),
  and `"discarded_windows": [{ "t_from", "t_to", "reason" }]` lists the spans. Discarded data never counts in
  results, medians, memory peaks or dashboard charts.
- Everything else → static files in `dashboard/`.
