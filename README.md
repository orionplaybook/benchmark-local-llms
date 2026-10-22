# benchmark-local-llms

> **Vibe-coded by [Gérard Métrailler](https://www.orionplaybook.com) with Claude Opus 5.5 (Anthropic)** · [www.orionplaybook.com](https://www.orionplaybook.com)
>
> **⚠️ Disclaimer:** this tool is provided **as is**, without warranty of any kind: no guarantee that it is useful, correct or fit for any purpose, and **no support** is offered. Benchmark results and the public data it collects are indicative only; use them, and the tool, at your own risk. See [LICENSE](LICENSE).

Measures **how fast** the LLMs you've downloaded run on **this** computer (not how smart they are), and puts the results next to **public intelligence benchmarks**. Everything goes into one JSON database that grows as you add models, and a local web dashboard shows the table, a page per model, and side-by-side comparisons.

### What it measures, and what it doesn't
- **Measured here: local performance.** Speed (time to first token, reading/prefill and writing/decode speed, load times) and memory depend on *your* hardware, the engine, the file format and the context length, so they can only be measured on your machine. That is this tool's job.
- **Not measured here: intelligence.** How capable a model is (reasoning, knowledge, coding, **tool use / agentic work**, long-context understanding) doesn't depend on your computer, and a handful of local prompts can't grade it reliably. The tool **collects it from reputable public sources** instead, with a link to the source of every number (see [§6](#6-public-intelligence-data)). Scores are only comparable between models when they come from the **same benchmark, run the same way**: independent evaluators that test every model with one harness (Artificial Analysis, Epoch AI) are the most consistent; numbers from model cards are published by each vendor with its own settings.
- The local **recall** and **extraction** scores are sanity checks that a model really processed the input and returns usable JSON; they are not intelligence scores.
- Public scores are measured on the original, unquantized model. A 4-bit download usually scores slightly lower; the tool doesn't measure that difference.

It works with **LM Studio** and **Ollama**, through their HTTP APIs only. It needs **Python 3.9+ with no extra packages**, so there's nothing to `pip install`.

---

## 1. Quick start

```bash
cd benchmark-local-llms
./bench setup        # finds LM Studio / Ollama, asks for API keys if needed, detects this machine
./bench list         # shows downloaded models and whether they've been benchmarked
./bench run --next   # benchmarks the next untested model (or ./bench run for all of them)
./bench dashboard    # opens the dashboard in your browser (no server, nothing to stop)
```

On **Windows**, use `bench.cmd` instead of `./bench` (for example `bench run`). Install Python 3 from python.org once if it isn't there already, and tick "Add python.exe to PATH".

### Requirements
- macOS (Apple Silicon or Intel), Windows 10/11, or Linux, with Python 3.9 or newer. On a Mac the built-in `/usr/bin/python3` works.
- LM Studio with its **local server running** (Developer tab → Start server, default port 1234), and/or Ollama (default port 11434).
- Internet access only for the public benchmark data (Hugging Face, Epoch AI). The benchmarks themselves run offline.

---

## 2. API keys (`secrets.local.json`)

Keys live in `secrets.local.json` next to the tool. **Git ignores it** and only your user account can read it (mode 600).

```json
{
  "lmstudio":   { "base_url": "http://localhost:1234",  "api_key": "<LM Studio API token>" },
  "ollama":     { "base_url": "http://localhost:11434", "api_key": "" },
  "huggingface":         { "token": "" },
  "artificial_analysis": { "api_key": "" },
  "brave_search":        { "api_key": "" },
  "searxng":             { "base_url": "" }
}
```

- **LM Studio token:** needed only if "Require API token" is on in LM Studio. Create one in **LM Studio → Developer → Server Settings → API tokens**. If the file or key is missing, or LM Studio rejects the key, `bench` asks for it (input is hidden), tests it and saves it. With `--no-input` it stops and tells you what to add instead.
- **Optional keys:**
  - `huggingface.token`: a read-only token that raises Hugging Face rate limits.
  - `artificial_analysis.api_key`: a free key (create one on [artificialanalysis.ai](https://artificialanalysis.ai/api-access-preview)) that adds Artificial Analysis benchmark data: its Intelligence Index and the evaluations behind it (agentic and tool-use tasks, coding, long context…), run by Artificial Analysis itself on every model with the same method. **Recommended**: it's the most consistent public source for comparing models. The free tier allows 1,000 requests a day (the tool needs about one a day; it caches the list) and **requires attribution** to artificialanalysis.ai wherever its data is shown: the dashboard links every such score to its Artificial Analysis page. Keep the key in `secrets.local.json`: the dashboard never sees it.
  - `brave_search.api_key` or a self-hosted `searxng.base_url`: a web search provider, used only when a model has little public data.
- You can also set any of these as environment variables, e.g. `BENCH_LMSTUDIO_API_KEY`, or `BENCH_OLLAMA_BASE_URL=http://other-host:11434`.

---

## 3. Commands

| Command | What it does |
|---|---|
| `./bench setup` | Detects engines, stores keys, records this machine. |
| `./bench status` | Lists engines and which models are loaded right now. |
| `./bench list` | Lists downloaded models with a status: `✓ done`, `○ new`, `◐ incomplete` (failed or interrupted, re-run automatically) or `⚠ settings changed` (tested with an older suite or profile). |
| `./bench run` | Benchmarks every model that isn't done yet. Models already analysed are **skipped**. |
| `./bench run --next` | Benchmarks only the next untested model, then stops. `--limit N` does the next N. |
| `./bench run --dry-run` | Shows what would be benchmarked, without loading anything. |
| `./bench run qwen gemma-4-31b` | Only models whose name or key contains one of those words. |
| `./bench run <model> --force` | Re-tests a model. The new run is added, and older runs stay in the history. |
| `./bench run --quick` | 1 repeat instead of 3 (a smoke test; results are still saved). |
| `./bench run --only short,long` | Runs only some of the tests (`short`, `extraction`, `long`). |
| `./bench run --reasoning off\|high\|both` | Which thinking modes to run (default `both`). |
| `./bench run --engine ollama` | Only one engine. |
| `./bench run --no-restore` | Don't reload the models that were loaded before the run. |
| `./bench run --store-reasoning` | Also keep the models' thinking texts in `data/raw/` (they can be large). The visible answers are always kept. |
| `./bench run --max-restarts N` | How many times a test restarts when another model gets loaded, before the model is stopped (default 3; see [section 4](#4-keeping-the-machine-clean)). |
| `./bench run --no-input` | Never prompt; use this for unattended runs. |
| `./bench enrich [model] [--refresh]` | Collects public model info and benchmark scores only (no performance run). |
| `./bench dashboard` | Regenerates the dashboard from the latest results (in `data/site/`) and opens it straight from disk. No server runs. |
| `./bench dashboard --live [--port 8765]` | Serves the dashboard from a small local web server instead, which always reads the newest data. **Ctrl+C stops it.** |
| `./bench publish --out <folder>` | Writes a self-contained copy of the dashboard + results for **any web server** (see §7). The models' answer texts are left out unless you add `--include-answers`. |
| `./bench show <model>` | Prints a model's latest results in the terminal. |
| `./bench merge <path> [--dry-run]` | Adds results benchmarked on another computer (its `results.json`, `data/` folder or tool folder). See §9. |
| `./bench sync [--public] [--dry-run] [-m "message"]` | *Maintainer copy only.* Commits **everything in the git repository the tool lives in** and pushes it to `main`; `--public` also publishes the public snapshot. See below. |
| `./bench recompute` | Re-derives every run's summary from the stored data (e.g. after a tool update adds a new metric), then regenerates the dashboard. No benchmarking. |
| `./bench export --csv results.csv` | Writes one row per run for spreadsheets. |
| `./bench machine --set memory_bandwidth_gbps=307` | Adds manual hardware specs (shown in the dashboard). |

Every `run` is also logged to `data/logs/run-<date>.log`.

### One model at a time
Benchmarking a model takes roughly **30–75 minutes**, depending on its size and how much it thinks. To do them one at a time:

```bash
./bench run --next        # benchmarks only the next untested model (the first ○ in ./bench list), then stops
./bench run --limit 2     # the next two
./bench run qwen          # a specific model (any part of its name or key)
./bench run --dry-run     # shows what would run, without loading anything
```

`./bench list` shows which model `--next` will pick. At the end of each run, the tool tells you what's left and reloads the models that were loaded before.

### Several versions of one model in LM Studio (variants)
If you download several versions of the same model in LM Studio (for example the GGUF and the MLX version of gpt-oss-20b), LM Studio lists them as one model with several **variants**, such as `openai/gpt-oss-20b@gguf-mxfp4` and `@mlx-mxfp4`. Neither LM Studio's API nor its `lms` command can load a specific variant: they always load the one selected in the app. So the tool benchmarks the **selected** variant, and you switch variants by hand between runs. Each variant gets its own row in the results.

1. Check which variant is selected and whether it has been benchmarked:
   ```bash
   ./bench list
   ```
   The row shows the selected variant, e.g. `lmstudio:openai/gpt-oss-20b@mlx-mxfp4`.
2. Benchmark it, using any part of the name:
   ```bash
   ./bench run lmstudio:openai --no-input
   ```
3. Switch to the next variant in LM Studio:
   - open **My Models** (the folder icon in the left sidebar);
   - find the model (e.g. *gpt-oss-20b*) and open its **variant** selector (it shows the current one, e.g. *MLX · MXFP4*);
   - choose the other variant (e.g. *GGUF · MXFP4*).
4. Run `./bench list` again: a new `○ new` row appears for the newly selected variant. Then repeat step 2.

Tip: `./bench run --dry-run lmstudio:openai` shows which variant would be tested without loading anything. Ollama doesn't need any of this: each download has its own tag (e.g. `gemma4:26b-mlx`, `gemma4:26b-a4b-it-qat`) and is benchmarked separately.

To do everything in one go, run `./bench run --no-input`. The tool works through every untested model in turn. Results are saved after **each** model, so an interrupted run (Ctrl+C, a crash or a reboot) only re-does the model it was on.

---

### Saving results to GitHub (`bench sync`, maintainer copy only)

> The public copy of this tool doesn't include `bench sync` or `scripts/export-public.sh`: they're the author's tools for keeping a private working copy (with benchmark data) and publishing clean snapshots of it. If you use the public copy, manage your own repository with git as usual.

After a run or a merge that produced new data, the tool reminds you that it isn't in git yet. Then:

```bash
./bench sync --dry-run   # optional: list what would be committed
./bench sync
```

- It works on the **whole repository the tool lives in** (e.g. a parent folder that holds several tools), not just `benchmark-local-llms`: `git add -A`, one commit, `git push origin main`.
- The commit message names the new runs (e.g. *"Benchmark results 2026-10-20 07:12: 3 new run(s) — …"*). Use `-m "..."` for your own message, or `--no-push` to commit without pushing.
- Safety: it only runs on `main` or `master`, and it refuses if an API key file (`secrets.local.json`) would be included.
- If GitHub has commits this computer doesn't have yet (pushed from another computer), the push is refused and the tool shows the fix: `git pull --rebase`, then `./bench sync` again.
- The equivalent by hand: `cd <repository root> && git add -A && git commit -m "Benchmark results" && git push`.
- `--public` then rebuilds the public snapshot with `scripts/export-public.sh` (no data, no keys, leak-checked; default clone `~/code/public-repositories/benchmark-local-llms`, or `--public-dir`) and pushes it. Each publish adds a commit on top of the public history; add `--reset-public-history` (one-off) to make the snapshot the repository's only commit instead (force push). Without `--public`, `bench sync` ends with a reminder about the public snapshot and highlights when the tool's code has changed since the last one; data changes never count.

## 4. Keeping the machine clean

To keep results comparable, nothing else may be loaded while a model is being measured:

1. Before starting, `bench run` lists every model loaded in LM Studio (LLMs and embedding models) and in Ollama, then **unloads them all** through the APIs.
2. **Pre-flight check**, before each model: after the unloads it waits for the system to release the memory (until memory use is steady, at most 30 s: `cleanup_wait_s` in the profile). It then logs the free memory and the swap in use, and adds a warning to the run if swap is already above 1 GB, or if less memory is free than the model's size plus 8 GB. It never stops an unattended run and needs no password or extra tool. Swap only clears with a restart, so **restart the computer before a long overnight run**; quit other big apps (browsers, Docker, Xcode) too.
3. If unloading fails, it stops and prints exact instructions for each model (for example `lms unload "<id>"`, `ollama stop <model>`, or eject it in LM Studio).
4. During the run, a watchdog checks every 10 s whether another model has been loaded, for example by Hermes or n8n. If one is found during a test:
   - The test is **stopped at once**: the request in progress is cancelled (LM Studio and Ollama stop working on it within a few seconds) and no further request of that test is sent.
   - The other model is unloaded and the test **restarts from its warm-up**. Tests that already finished cleanly for this model are kept.
   - Everything the interrupted attempt measured is **discarded**: it is kept in the raw file (flagged `"discarded": true`, with the reason) but never counts in any result, median, memory peak or dashboard chart. The event is recorded on the run (time, test, which model, what was done).
   - The terminal shows where the test was interrupted, roughly how much time that saved, and the restart number, e.g. `! long/high interrupted at request 4 of 14 … about 22 min saved versus finishing it; restarting (attempt 2 of 4).`
   - The model being tested is never counted as "another model", also while it is still loading (LM Studio already lists a model during a slow load, e.g. 45 s for a Splash model). A second copy of it loaded by someone else still counts.
   - **Restart limit:** a test is restarted at most 3 times (`max_test_restarts` in [config/profile.json](config/profile.json), or `./bench run --max-restarts N`; changing it doesn't affect results). If another model is still being loaded after that, the tool stops that model, marks it incomplete, names the model that kept appearing, and moves on to the next one. Pause whatever loads it (e.g. Hermes or n8n schedules), then run again.
5. When the run ends, it **reloads the models that were loaded before**, with their previous context length, so your agents (e.g. Hermes) keep working. Use `--no-restore` to skip this.

Tip: pause Hermes or n8n schedules during the run, so they don't keep reloading their model and interrupting tests.

---

## 5. What gets measured

Every model is loaded by the tool with the same **standard profile** ([config/profile.json](config/profile.json)):

| Setting | Value |
|---|---|
| Context length | 114,688 tokens (112k: fits the 73–85k-token document plus thinking) |
| Sampling | temperature 0, top_p 1, top_k 1, min_p 0, repeat penalty 1, seed 42 (seed applies to Ollama only) |
| Repeats | 1 warm-up, then 3 timed repeats. The median is reported, along with min and max. |
| Flash attention / KV cache / batch | Engine defaults. The actual values are recorded from the engine's reported load config. |

Changing the profile changes its hash. Older results then show as `⚠ settings changed`, so old and new results are never mixed by accident.

### Thinking modes
Each test runs twice:
- **off:** thinking is disabled. If a model can't disable it, the lowest level is used: Muse Glimmer uses `low`, and gpt-oss uses `low`.
- **High:** the `high` level where the model offers it, otherwise `on`, then `xhigh`, then `medium`. This is deliberately the **high setting, not the maximum**: models that also offer `xhigh` (Muse Glimmer, Qwen3.8 27B) are tested at `high` or `on`, so every model is compared at the same level.

The level **actually applied** is stored for every test. Thinking tokens are counted separately from the answer.

**Answer in the reasoning channel.** Some models, with thinking on, write their whole answer inside the thinking text and leave the visible answer empty (Nemotron 3 Nano 4B does this on the long test). The tool records such a turn as `answer_in_reasoning_channel` and adds a run warning, instead of treating it as a plain wrong answer. The **official score still uses the visible answer**, because that is all an agent receives. For tests where that happened, a **secondary score** on the reasoning text is shown next to it (`recall_reasoning` for the long test, `accuracy_reasoning` for extraction), so you can see that the model did find the answer. Short, extraction and long tests are all checked. For runs before 2026-10-21 the flag is derived from the stored text lengths; the secondary score is not available for them. With thinking on, the important number is the **time to first visible token** (when the answer actually starts). Thinking runs get extra output tokens per turn for the thinking itself: 3,072 for the short test, 8,192 for extraction and 4,096 for the long test (`reasoning_extra_tokens` in the profile). If a model still runs out, the answer is cut off; the run records `truncated_turns` and a warning. When thinking used the whole budget before *any* visible answer, the turn is recorded as `no_answer_thinking_budget` (`no_answer_budget_turns` per test). It still counts as wrong, but when that happened on a *scored* answer (a recall question or the extraction answer) the dashboard labels the score (“2 of 3 answers never arrived: ran out of thinking budget” on the model page, “2/3 no answer” in Compare), so a low accuracy or recall from a model that thinks too long isn't read as wrong answers. Runs from before this was recorded get it on `./bench recompute`. If a model still thinks when asked not to, the run is flagged `reasoning_observed`.

### Cold vs. warm loading
- **Cold cycle 1:** everything unloaded → load → first request. This gives the load time and the first token right after loading.
- **Cold cycle 2:** unload → load again. The second load is usually faster because the OS keeps the model file in memory.
- **Warm:** the first token for the same short prompt, with the model already loaded.
- **Cache hit:** the first turn sent again word for word, to measure the engine's prompt cache. It's measured in the **off** mode of the short and long tests, also for models that can't fully turn thinking off (gpt-oss runs "off" as `low`): the time to first token counts the first token of any kind, so the thinking doesn't change it. Runs of gpt-oss before 2026-10-21 have no cache-hit value.

Each timed repeat starts with a unique session tag at the top of the system prompt. That stops the engine reusing a cached prompt from a previous repeat, so prefill is really measured each time.

### Tests (fixed and versioned in [benchmarks/](benchmarks/README.md))
1. **Short:** a 5-turn assistant/agent conversation, under 4k tokens of context: explain, summarise, extract JSON, a follow-up, plan. It measures time to first token, prefill and decode speed for small prompts, the kind Hermes and n8n send all the time.
2. **Extraction:** the model turns a saved web page (a model card plus a leaderboard snippet) into JSON. It's timed, and scored against a known answer key: valid JSON plus 20 fields. This is the same job the tool gives models for public data.
3. **Long:** a ~300k-character Markdown handbook with 10 hidden facts. That's about 73k tokens with Gemma's tokenizer and about 83k with Llama/Qwen-style ones, so it is above 64k for every model; a run is flagged if it isn't.
   - Turn 1 loads the document, which measures **prefill speed at 64k+** and the time to first token with a full context.
   - Turns 2–4 ask about facts at the start, middle and end of the document, which measures follow-up speed with a cached prefix and decode speed with a full context.
   - **Recall** (hidden facts found out of 10) shows the model really read the document. It's a sanity check, not an intelligence score. Answers are matched leniently on typography: Unicode dashes and no-break spaces count as plain hyphens and spaces (gpt-oss writes `BLUE‑HERON‑82` with non-breaking hyphens). Runs before 2026-10-21 were scored without this, which understated gpt-oss (5/10 instead of 10/10); re-run them to correct it.
   - **Recall per fact:** which facts were found, grouped by where they sit in the document (**start / middle / end**), with the expected answer. A model that only misses the middle facts has a "lost in the middle" problem rather than a reading problem. The answers are kept in `data/raw/` (see Memory below), so a miss can be checked by reading what the model actually said. Older runs show "not available": their answers weren't stored.

### Live extraction (an extra test)
After the timed tests, the **model being tested** is given the real public web page about itself (usually its Hugging Face model card) and asked to extract its benchmark scores as JSON. The tool records how long that takes and how well it **agrees** with the pattern-based table parser. Values that only the model found are added to its public data, marked `local-llm:<model>`. No cloud LLM is ever used.

### Memory
A background sampler runs every 250 ms for the whole run.
- **macOS:** for each engine process, the larger of its `phys_footprint` (from `footprint`, which covers MLX/Metal allocations) and its resident memory (which covers GGUF weights llama.cpp maps from disk). It also records system memory used, wired (GPU-locked) memory and swap. No sudo needed.
- **Windows:** process private bytes / working set. `nvidia-smi` is used for the graphics card if it's present.
- **Linux:** RSS.

**Context at peak and safe context.** The peak usually happens *while reading* the long document: a temporary working-memory spike on top of the weights and the stored context. Each run records how many tokens were in context at the peak (**Ctx @ peak**). From the long-document test the dashboard estimates a **Safe ctx**: the largest context that keeps the peak below the machine's RAM minus 8 GB (the tooltip also shows 60%, 75% and 85% of RAM), by scaling the memory above "loaded" linearly with context. When at least a 128k window (131,072 tokens) fits, the table shows "128k+"; the tooltip and the model page also estimate the peak memory at a 128k and a 256k window and whether each fits (or exceeds the model's maximum). Everything beyond the ~75k tokens actually tested is an extrapolation, and it's a starting point for the context length you set in LM Studio, Ollama or Hermes, not a guarantee.

Snapshots are recorded at **idle → model loaded with an empty context → after the short test → right after the long document → end**, plus the peak. The full timeline, coloured by phase, is shown on each model's page.

**Swap.** When the model plus its context doesn't fit in memory, macOS moves memory to disk (swap), and everything gets slower. The run records how much swap grew (`swap_growth_gb`). Above **1 GB** (`swap_warning_gb` in [config/profile.json](config/profile.json); changing it doesn't affect results) the run gets a warning, shown on the model page and in `./bench list`: its speeds are probably lower than usual and shouldn't be compared with clean runs. Close other apps and re-test with `--force`. `./bench recompute` re-applies the threshold to older runs.

**What's stored per request** (in `data/raw/<run>.json`): timings, token counts, the **visible answer text**, and the outcome (`answer_in_reasoning_channel`, `no_answer_thinking_budget`). The prompts are never stored. Thinking texts are only stored with `./bench run --store-reasoning`.

---

## 6. Public intelligence data

Collected automatically on each `run`, or with `bench enrich`. Each benchmark is stored with its **source URL, retrieval date and method**.

| Method | Source |
|---|---|
| `card-table` | Benchmark tables in the original model's Hugging Face card, read from Markdown and HTML tables. The column for the right model is picked by name (e.g. "Gemma 4 31B" and not "Gemma 4 26B A4B"). |
| `model-index` | Structured eval results in the card's metadata. |
| `leaderboard` | **Epoch AI Benchmarking Hub**: free, CC-BY data, downloaded and cached for 7 days. |
| `api` | **Artificial Analysis** (free key, see §2): an independent evaluator that runs the same benchmarks on every model, including agentic / tool-use evaluations. Attribution: data from [artificialanalysis.ai](https://artificialanalysis.ai/). |
| `card-link` / `web` | Official blog, report or GitHub pages linked from the card, or a web search (Brave/SearXNG if configured; DuckDuckGo otherwise, which may block automated searches; the tool respects that and doesn't retry). |
| `local-llm:<model>` | Values the tested model extracted itself (see Live extraction). |
| `manual` | Your own values from `data/overrides.json`. These always win. |

Where several sources give the same benchmark, this order applies: manual → card-table → model-index → leaderboard → api → card-link → web → local-llm.

Scores marked `applies_to: base` were measured on the original, unquantized model, not on your quantized file.

**Reasoning effort.** Public evaluators often run a thinking model at several efforts (Artificial Analysis lists gpt-oss-20b at Low and High, and Qwen models as Reasoning and Non-reasoning; Epoch AI runs several efforts too). When a source has several, the tool keeps **both ends**: the **highest** effort is the main score (used for category scores, the radar, Compare and the speed-vs-intelligence chart) and the **lowest** is shown next to it on the model page, with a line saying which efforts each source ran. Read the highest-effort score with your local **Thinking High** results and the lowest with your **off** results. A benchmark a source only ran at low effort keeps that as its main score.

**Consistency.** Compare models on scores from the **same source and benchmark**. The source table on each model page shows where every number comes from. Independent evaluators (Artificial Analysis, Epoch AI) run every model the same way; model-card numbers are each vendor's own, with its own prompts, settings and reasoning effort, so a 2-point gap between two vendors' cards means little. For tool use and agents, look at agentic benchmarks such as τ²-bench, BFCL or Terminal-Bench, preferably from the same evaluator for all the models you compare.

**Mixture of experts (MoE).** A MoE model only uses some of its weights for each token, so its speed depends on the **active** parameters (e.g. gpt-oss-20b: 21B total, 3.6B active). The tool fills in `is_moe` and `params_active_b` from, in this order: the model's name (`30B-A3B`), the original model's Hugging Face card ("21B parameters with 3.6B active"), and an estimate from its Hugging Face `config.json` or Ollama's GGUF metadata (number of experts, experts per token, layer sizes; shown with a `~`). The number of experts and experts per token are stored too. LM Studio itself doesn't report experts. `./bench enrich --refresh` re-derives this for downloaded models, and `./bench recompute` copies it to older rows of the same model. You can always set it yourself in `data/overrides.json` (below).

Benchmarks are grouped into categories: **reasoning, knowledge, math, coding, agentic, vision, long_context, instruction_following**. The mapping is in `src/benchlm/enrich/benchnames.py`.

### Manual corrections: `data/overrides.json`
```json
{
  "public": {
    "lmstudio:meta/muse-glimmer@q4_k_m": {
      "benchmarks": [ { "name": "BFCL", "category": "agentic", "score": 71.2, "unit": "%",
                        "source_url": "https://example.com/report" } ],
      "release_date": "2026-09-30"
    }
  },
  "machines": { "Mac16,10-M4Pro-64GB": { "specs_extra": { "memory_bandwidth_gbps": 273 } } },
  "models": { "lmstudio:openai/gpt-oss-20b@mxfp4": { "is_moe": true, "params_active_b": 3.6 } }
}
```

---

## 7. Dashboard

`./bench dashboard` regenerates a self-contained copy of the dashboard in `data/site/` and opens it from disk (`file://`), so no server runs and there's nothing to stop. `./bench run` regenerates that copy after each model it benchmarks; if the dashboard is already open, reload the page in your browser to see the new results (the **Refresh** button only appears in `--live` mode). `--no-browser` only prints the address.

The top-right corner shows **Updated** with the time the copy was generated, in your time zone (with `--live`: when the results last changed).

`./bench dashboard --live` instead starts a small web server on 127.0.0.1 ("Press Ctrl+C to stop the server and exit") that reads `data/results.json` fresh each time you press **Refresh**. Both modes show exactly the same dashboard and work offline (Chart.js is included in `dashboard/vendor/`).

- **Models:** a sortable, filterable table of every model, with speed, long-context, memory and intelligence-by-category columns. The **fit score** sliders (speed, long context, intelligence, agentic, memory) rank models for your own needs, and the slider positions are remembered.
- **Model page:** identity, engine, load config and machine (including MoE experts and active parameters); cold vs. warm charts; per-turn charts with thinking off and High; answers written only in the reasoning channel (red badge) with the score on the reasoning text; recall per fact (start / middle / end of the document); memory snapshots and timeline, with a swap badge when swap grew; an intelligence radar and the full source table; run history; warnings.
- **Explain:** how the tool works, what each test tells you, how to read the speed and memory numbers, how to choose a model for chat, automations, long documents or hard reasoning, and a **response-time estimator** built from your own results.
- **Glossary:** about 130 terms in plain language (GGUF, MLX, QAT, A4B/MoE, TTFT, prefill, KV cache, every public benchmark…), searchable.
- **Definitions everywhere:** column headers, badges and labels with a dotted underline show a short definition when you hover or tap them, with a link to the full Glossary entry.
- **Platform** column: Mac, Win or Linux, next to Engine. With results from several computers, the machine filter offers **All machines** (the default) or one machine at a time.
- **Compare:** tick up to **8** models (the same model on two computers counts as two). Every chart legend says which engine, format and, when several computers are involved, which machine each colour is.
- **Compare details:** → key metrics side by side (best highlighted), speed and memory charts, an overlaid radar chart, and a benchmark-by-benchmark table.


### Sharing the dashboard (any web server)
```bash
./bench publish --out ~/Sites/llm-bench
```
This writes a static folder: the dashboard files plus `data/results.json` (with your `data/overrides.json` corrections applied) and the memory timelines in `data/raw/`. Upload the **whole folder** to any static host (your own web server, GitHub Pages, Netlify, an S3 bucket…) and open its address. Visitors see the same dashboard, marked **Snapshot**, with all views, definitions, Explain and Glossary.

- It's a snapshot: run `./bench publish --out <same folder>` again after new benchmarks, then re-upload.
- `--no-raw` leaves out the memory timelines for a smaller upload (the memory timeline chart then shows "no timeline").
- The tool only overwrites a folder it created itself (it leaves a `.bench-publish` marker); use `--force` to replace another folder's contents.
- Nothing private is included: no API keys, no hostname, no prompt text, only results, model details and your machine's hardware specs. The models' **answer texts** are left out of the published raw files too; add `--include-answers` to keep them. (The local dashboard copy in `data/site/` follows the same rule.)
- The folder also works without a web server: double-click `index.html`. The data is included as scripts (`data/*.js`), which browsers allow from local files.

---

## 8. Files

```
bench, bench.cmd           launchers (macOS/Linux, Windows)
config/profile.json        standard load + sampling profile
benchmarks/                fixed test content (versioned, see benchmarks/README.md)
src/benchlm/               the tool (Python standard library only)
dashboard/                 static web dashboard
data/results.json          THE database (commit it, or copy it to another machine)
data/raw/<run_id>.json     memory timelines + every request's raw timings
data/overrides.json        your manual corrections (optional)
data/site/                 the generated dashboard opened by `./bench dashboard` (git-ignored, regenerated)
data/cache/                cached downloads (safe to delete)
data/logs/                 run logs (git-ignored)
docs/SCHEMA.md             database format
secrets.local.json         API keys (git-ignored)
```

Results from several machines can live in the same `results.json`. Every run records the machine (model, chip, CPU/GPU cores, RAM, disk, OS), and the dashboard has a machine filter.

---

## 9. Several computers (e.g. a Mac and a Windows PC)

Benchmark each computer with its own copy of the tool, then combine the results in one database:

1. On the other computer (Windows: use `bench.cmd`), install the tool the same way, run `bench setup`, then `bench run`.
2. Copy that computer's **`benchmark-local-llms/data` folder** to this one (USB stick, shared folder, cloud drive…). It contains `results.json` and the memory timelines in `raw/`.
3. Merge it here:
   ```bash
   ./bench merge /path/to/copied/data --dry-run   # shows what would be added
   ./bench merge /path/to/copied/data
   ```
   It adds the runs, models, machines and public data that aren't here yet, copies the memory timelines, keeps a backup of your previous database (`data/results.backup-<date>.json`, git-ignored) and regenerates the dashboard. Merging the same folder again adds nothing, so you can repeat it after new benchmarks on the other computer. It works in both directions.

Each run records its machine, so the same model benchmarked on both computers appears as two rows, with the **Platform** column showing Mac or Win. Each computer only skips the models *it* has already benchmarked.

Windows notes: memory is measured per process (private bytes / working set), and with a graphics card most of the model sits in its VRAM; the engine-reported size is stored in the run's load config. The Windows code paths haven't been tested on a real PC yet, so check the first results with a critical eye.

## 10. FAQ

- **A model shows `failed` or `incomplete`.** Look at `data/logs/` and run `./bench run <model>` again. Incomplete models are re-run automatically.
- **LM Studio says "model not found".** The model has to appear in LM Studio's *My Models*. The tool uses the same keys as `lms ls`.
- **I changed the test content or profile.** Bump `suite_version` (benchmarks) or edit `config/profile.json`. Existing results then show `⚠ settings changed`, and `--force` re-tests.
- **The numbers vary between nights.** Check for thermal throttling (other heavy apps), Low Power Mode, and whether something else was running. Runs where another model was loaded are flagged.
- **gpt-oss shows 50% recall in older runs.** That was a scoring bug, fixed on 2026-10-21: it writes Unicode hyphens and spaces, which weren't matched. Its real recall is 10/10; re-run it (`./bench run gpt-oss --force`) to update the stored score.
- **A run says it "started with … GB of swap already in use".** Swap left over from earlier work only clears with a restart. Restart the computer before a long run, then re-test with `--force`.
- **A thinking model scores 0 recall with thinking on, but full marks with it off.** Look for the red "answer(s) only in the reasoning channel" badge on its model page: the model wrote its answers in the thinking text and left the visible answer empty. The secondary score next to it shows what it found there. In an agent, such a model gives empty replies with thinking on.
- **A model's speeds look much worse than in another run.** Check for the swap warning (model page and `./bench list`). Memory ran short and macOS swapped to disk; close other apps and re-test with `--force`.
- **A model shows as MoE "no" although it is one.** Run `./bench enrich --refresh <model>`, which reads the experts from Hugging Face. If the repo has no `config.json`, set `is_moe` and `params_active_b` in `data/overrides.json`.
- **Which facts did a model miss in the long test?** Open the model page → Long context → *Recall per fact*: hover a fact to see the expected answer. The model's actual answers are in `data/raw/<run>.json` (`text` of the `long/…/t2`–`t4` requests).
- **Windows memory numbers look low.** With a discrete GPU, model weights are held in graphics-card memory. The engine-reported size (Ollama `size_vram`) is stored in `load_config`.
