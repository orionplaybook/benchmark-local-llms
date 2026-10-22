/* Explain view (#/explain): what the tool does, the tests, how to read the numbers, how to choose,
   plus a response-time estimator built from the user's own results. */
(function () {
  "use strict";
  const BL = window.BL;
  const { esc, fmt, isNum } = BL;
  const t = (id, label) => BL.t(id, label);

  const TOC = [
    ["what", "What this tool does"],
    ["models", "Understanding a model's name"],
    ["fit-calc", "Will it fit? (calculator)"],
    ["run", "What happens during a run"],
    ["tests", "The three tests"],
    ["numbers", "Reading the speed numbers"],
    ["estimator", "Response-time estimator"],
    ["thinking", "Thinking modes"],
    ["memory", "Memory"],
    ["public", "Public benchmark scores"],
    ["fit", "The fit score"],
    ["choose", "How to choose a model"],
    ["caveats", "Caveats"],
    ["commands", "Command cheat sheet"],
  ];

  function box(title, body) {
    return '<div class="callout x-box"><h3>' + esc(title) + "</h3>" + body + "</div>";
  }

  // A model name split into labelled parts: [[text, caption, glossaryId], ...]
  function anatomy(parts) {
    return '<div class="anatomy">' + parts.map(([txt, cap, id], i) =>
      '<span class="seg s' + (i % 7) + '"><code class="term" data-term="' + id + '" tabindex="0">' + esc(txt) + "</code><small>" + esc(cap) + "</small></span>").join("") + "</div>";
  }

  // Rough memory check: weights from parameters × bits, context memory from your own runs.
  function fitCalc(el, ctx) {
    const idx = ctx.idx;
    const machines = Object.values(idx.machines || {});
    const ramGB = machines.length && machines[0].memory_bytes ? Math.round(machines[0].memory_bytes / BL.GB) : 64;
    const kv = idx.rows.map((r) => BL.sv(r.run, "mem_kv_long_gb")).filter(isNum).sort((a, b) => a - b);
    const state = BL.store.get("fitcalc", { params: 27, bits: 4, ram: ramGB, ctx: 64 });
    const draw = () => {
      const P = Math.max(0, Number(state.params) || 0), B = Number(state.bits) || 4, R = Math.max(1, Number(state.ram) || ramGB);
      const weights = P * B / 8 * 1.08;
      const ctxGB = kv.length ? kv[Math.floor(kv.length / 2)] * (Number(state.ctx) || 0) / 64 : (Number(state.ctx) || 0) / 64 * 4;
      const total = weights + ctxGB + 1.5;   // + engine overhead
      const share = total / R;
      const free = R - total, H = BL.SAFE_HEADROOM_GB;
      const verdict = share <= 0.75 ? ["good", "Comfortable: leaves plenty of room for the operating system and apps."]
        : free >= H ? ["warn", "Tight: it should work with " + free.toFixed(0) + " GB left, but close other heavy apps and avoid much longer contexts."]
          : free > 0 ? ["bad", "Very tight: less than " + H + " GB left for the system and apps; likely to slow down or swap. Use fewer bits or a smaller model."]
            : ["bad", "Too big for this memory."];
      el.querySelector("#fc-out").innerHTML =
        '<div class="fc-bars"><div class="fc-bar"><span class="w" style="width:' + Math.min(100, weights / R * 100) + '%"></span><span class="c" style="width:' + Math.min(100, ctxGB / R * 100) + '%"></span><span class="o" style="width:' + Math.min(100, 1.5 / R * 100) + '%"></span></div>' +
        '<div class="fc-legend"><span><i class="w"></i>weights ' + weights.toFixed(1) + ' GB</span><span><i class="c"></i>context ≈ ' + ctxGB.toFixed(1) + ' GB</span><span><i class="o"></i>engine ≈ 1.5 GB</span><span>of ' + R + " GB RAM</span></div></div>" +
        '<p><span class="badge ' + verdict[0] + '">' + Math.round(share * 100) + "% of RAM</span> " + verdict[1] + "</p>" +
        '<p class="muted small">Weights = parameters × bits ÷ 8, +8% for layers kept at higher precision. Context memory is scaled from ' +
        (kv.length ? "your own runs (median " + kv[Math.floor(kv.length / 2)].toFixed(1) + " GB for the ~64k-token document across " + kv.length + " models)" : "a typical ~4 GB per 64k tokens") +
        ". Context memory varies a lot between architectures: recent designs with sliding-window or hybrid attention (like the Gemma 4 and Qwen3.x models) need little, while older large dense models (e.g. Llama 3 70B) can need 10–20 GB for 64k tokens. For MoE models enter the <b>total</b> parameters. An estimate, not a guarantee.</p>";
      BL.store.set("fitcalc", state);
    };
    el.innerHTML = '<p>Check whether a model you’re considering will fit before downloading it.</p><div class="est-form">' +
      '<label>Parameters <input type="number" id="fc-p" min="0" step="1" value="' + esc(state.params) + '"> B</label>' +
      '<label>Bits <select id="fc-b">' + [2, 3, 4, 5, 6, 8, 16].map((b) => '<option value="' + b + '"' + (Number(state.bits) === b ? " selected" : "") + ">" + b + "</option>").join("") + "</select></label>" +
      '<label>Context <input type="number" id="fc-c" min="0" step="8" value="' + esc(state.ctx) + '">k tokens</label>' +
      '<label>RAM <input type="number" id="fc-r" min="1" step="8" value="' + esc(state.ram) + '"> GB</label></div><div id="fc-out"></div>';
    const bind = (id, key) => el.querySelector(id).addEventListener("input", (e) => { state[key] = e.target.value; draw(); });
    bind("#fc-p", "params"); bind("#fc-c", "ctx"); bind("#fc-r", "ram");
    el.querySelector("#fc-b").addEventListener("change", (e) => { state.bits = e.target.value; draw(); });
    draw();
  }

  function section(id, title, body) {
    return '<section class="card explain-sec" id="x-' + id + '"><h2>' + esc(title) + "</h2>" + body + "</section>";
  }

  function content() {
    return [
      section("what", "What this tool does",
        "<p>It answers one practical question: <b>which of the models I've downloaded runs best on this computer, for what I want to do?</b> To do that it combines two kinds of data:</p>" +
        '<div class="grid-2 explain-two">' +
        '<div class="callout"><h3>1 · Local performance (measured here)</h3><p>How fast each model runs on <i>your</i> computer: ' + t("ttft", "time to first token") + ", " + t("prefill", "reading speed") + ", " + t("decode", "writing speed") +
        ", load time and " + t("mem-engine", "memory") + ". Measured the same way for every model, with the same " + t("profile", "settings") + ", so the numbers are comparable.</p></div>" +
        '<div class="callout"><h3>2 · Intelligence (collected from public sources)</h3><p>How capable each model is, from published ' + t("public-benchmarks", "benchmark scores") + " (reasoning, coding, " + t("tool-use", "tool use") +
        ", vision…). Collected from " + t("model-card", "model cards") + ", " + t("epoch", "Epoch AI") + " and, with a free key, Artificial Analysis, with a source link for every number. Nothing here depends on your computer.</p></div></div>" +
        '<p class="muted">The local tests deliberately don\'t try to grade intelligence: a handful of prompts can\'t do that reliably. The recall and extraction scores are sanity checks that the model really processed the input.</p>' +
        '<h3 class="x-sub">Why speed is measured here and intelligence isn\'t</h3>' +
        "<p><b>Speed and memory depend on your machine</b> (chip, memory bandwidth, engine, file format, context length), so they can only be measured locally. <b>Intelligence doesn't</b>: a model reasons, codes and uses tools the same way on any computer, so reputable public benchmarks describe it better than a few local prompts could. That includes " + t("tool-use", "tool use") + " and agentic work (" + t("tau2", "τ²-bench") + ", " + t("bfcl", "BFCL") + ").</p>" +
        "<p><b>Compare like with like.</b> Scores are only comparable when they come from the same benchmark run the same way. Independent evaluators that test every model with one method (Artificial Analysis, " + t("epoch", "Epoch AI") + ") are the most consistent; " + t("model-card", "model-card") + " numbers are each vendor's own, with its own settings. Every score links to its source, so you can check which is which. Public scores are measured on the original, unquantized model; a 4-bit download usually does slightly worse.</p>" +
        '<p class="muted">Artificial Analysis data appears when a free key is set in <code>secrets.local.json</code> (see the README). Attribution: <a href="https://artificialanalysis.ai/" target="_blank" rel="noopener">artificialanalysis.ai</a>.</p>'),

      section("models", "Understanding a model's name and versions",
        "<p>A model name packs a lot of information. The same model is usually published in many versions (sizes, bits, formats), and it helps to know which parts change <i>what it can do</i> and which only change <i>how fast it runs and how much memory it needs</i>.</p>" +
        '<h3 class="x-sub">Reading a model name</h3>' +
        anatomy([["gemma-4", "family & generation", "model-card"], ["26B", "total parameters", "parameters"], ["A4B", "≈4B active per token (MoE)", "active-params"],
                 ["it", "instruct-tuned", "instruct"], ["QAT", "quantization-aware trained", "qat"], ["MLX", "file format", "mlx"], ["4bit", "bits per weight", "mlx-quant"]]) +
        anatomy([["Qwen3.8", "family & version", "model-card"], ["27B", "dense, 27B parameters", "dense"], ["GGUF", "file format", "gguf"], ["Q4_K_M", "4-bit K-quant, medium", "q4_k_m"]]) +
        anatomy([["gpt-oss", "family", "model-card"], [":20b", "Ollama tag: 20B parameters", "variant"], ["MXFP4", "shipped in 4-bit float", "mxfp4"]]) +
        anatomy([["Qwen3.8-27B", "the original model", "base-model"], ["Uncensored", "⚠ modified by a third party", "derived-model"], ["OptiQ-4bit", "community quantization recipe", "quant-recipes"]]) +
        '<p class="muted small">Hover the labels for definitions. Order and spelling vary between publishers (<code>Instruct</code> or <code>it</code>, <code>4bit</code> or <code>Q4_K_M</code>); the pieces are what matter.</p>' +

        '<div class="x-stack">' +
        box("1 · Parameters (“27B”)", "<p>The number of learned weights, in billions. More parameters usually means more knowledge and better reasoning, but also more memory and slower answers.</p>" +
          '<table class="data compact"><thead><tr><th>Class</th><th>Typical use</th></tr></thead><tbody>' +
          "<tr><td>1–4B</td><td>routing, classification, simple extraction; very fast</td></tr>" +
          "<tr><td>7–14B</td><td>everyday assistant tasks, summaries, simple tools</td></tr>" +
          "<tr><td>20–35B</td><td>the sweet spot for 32–64 GB machines: agents, coding, long documents</td></tr>" +
          "<tr><td>70B+ dense, 100B+ MoE</td><td>needs 96–128 GB or more</td></tr></tbody></table>" +
          "<p>Memory for the weights ≈ <b>parameters × bits ÷ 8</b> GB: 27B at 4 bits ≈ 13.5 GB, plus ~10% for layers kept at higher precision. See " + t("parameters", "Parameters") + ".</p>") +
        box("2 · Dense vs. MoE (“A3B”, “A4B”)", "<p>A " + t("dense", "dense") + " model uses all its parameters for every token. A " + t("moe", "Mixture-of-Experts") + " model has many small experts and only uses a few per token: “35B A3B” means 35B in total, about 3B " + t("active-params", "active") + ".</p>" +
          '<ul class="tight"><li><b>Memory</b> follows the <b>total</b>: all experts must be loaded.</li><li><b>Speed</b> follows the <b>active</b> count: it writes about as fast as a 3–4B model.</li>' +
          "<li><b>Quality</b> sits in between: often compared to a dense model of roughly 10–15B for a 35B-A3B (a rough rule of thumb, not a law).</li></ul>" +
          "<p>Your own data: Gemma 4 26B A4B writes ~82 tok/s, the dense Gemma 4 31B ~14 tok/s, on the same computer.</p>") +
        box("3 · Bits (“4bit”, “6bit”, “8bit”)", "<p>How precisely each weight is stored (" + t("quantization", "quantization") + "). Same model, same knowledge; fewer bits means smaller, faster, slightly less accurate.</p>" +
          '<table class="data compact"><thead><tr><th>Bits</th><th>Size (27B)</th><th>Writing speed</th><th>Quality vs. original</th></tr></thead><tbody>' +
          "<tr><td>16 (original)</td><td>~54 GB</td><td>slowest</td><td>reference</td></tr>" +
          "<tr><td>8</td><td>~29 GB</td><td>~2× faster than 16</td><td>practically identical</td></tr>" +
          "<tr><td>6</td><td>~21 GB</td><td>faster</td><td>very close (≈1% or less)</td></tr>" +
          "<tr><td>5</td><td>~18 GB</td><td>faster</td><td>close</td></tr>" +
          "<tr><td>4</td><td>~15 GB</td><td>~1.2–1.4× faster than 6-bit</td><td>small, measurable loss (more on maths, code, long documents)</td></tr>" +
          "<tr><td>3 and below</td><td>&lt;12 GB</td><td>fastest</td><td>drops quickly; experiments only</td></tr></tbody></table>" +
          "<p>Writing is faster with fewer bits because each new token reads every active weight from memory once (" + t("memory-bandwidth", "memory bandwidth") + "). Reading a long prompt (" + t("prefill", "prefill") + ") changes much less. The conversation's memory (" + t("kv-cache", "KV cache") + ") is not affected by the weight bits.</p>") +
        box("4 · QAT (“quantization-aware trained”)", "<p>Normally a model is trained at full precision and rounded to 4 bits afterwards, which costs a little quality. With " + t("qat", "QAT") + " the maker continues training while simulating the 4-bit rounding, so the model learns to cope with it. A QAT 4-bit file keeps almost all of the original quality at 4-bit size and speed.</p>" +
          "<p><b>When you see a QAT version, prefer it</b> over an ordinary 4-bit conversion of the same model. Google publishes QAT versions of Gemma (your Gemma 4 26B and 31B are QAT); QAT files are usually " + t("q4_0", "Q4_0") + " (GGUF) or 4-bit MLX.</p>") +
        box("5 · Base vs. Instruct (“it”) vs. Thinking", "<p>Most families publish several <i>trained</i> versions of the same architecture; unlike bits and formats, these behave differently:</p>" +
          '<ul class="tight"><li><b>' + t("base-model", "Base") + "</b>: only continues text. Useful for further training, not for chatting.</li>" +
          "<li><b>" + t("instruct", "Instruct") + "</b> (Google writes <code>it</code>, others <code>Instruct</code> or <code>Chat</code>): trained to follow instructions, chat and call tools. <b>This is the one you want</b> for Hermes and n8n. Names without “Base” are usually instruct models too.</li>" +
          "<li><b>Thinking / Reasoning</b> (e.g. <code>-Thinking</code>): an instruct model trained to think before answering. Many recent models do both and let you switch " + t("reasoning-model", "thinking") + " on or off instead.</li>" +
          "<li><b>Specialised</b>: <code>Coder</code> (programming), <code>VL</code> / vision (images), <code>Embedding</code> (search vectors, not chat).</li></ul>") +
        box("6 · File format: GGUF, MLX, Splash", "<p>The " + t("file-format", "format") + " decides which " + t("engine", "engine") + " can run the file; the model inside is the same.</p>" +
          '<ul class="tight"><li>' + t("gguf", "GGUF") + ": one file, runs everywhere (" + t("llama-cpp", "llama.cpp") + " in LM Studio and Ollama; Mac, Windows, Linux).</li>" +
          "<li>" + t("mlx", "MLX") + ": a folder of " + t("safetensors", "safetensors") + " for Apple's MLX engine; Macs only, often faster there (your gpt-oss: MLX read a 64k document 2.2× faster than GGUF).</li>" +
          "<li>" + t("splash", "Splash") + ": Inco AI's engine for Apple Silicon (available in LM Studio as an experimental engine), with its own packed format and speculative decoding for a few supported models.</li></ul>" +
          "<p>Formats can't load each other's files: an MLX folder won't run in llama.cpp and vice versa.</p>") +
        box("7 · Quantization labels decoded", '<table class="data compact"><thead><tr><th>Label</th><th>Meaning</th></tr></thead><tbody>' +
          "<tr><td>" + t("q8_0", "Q8_0") + "</td><td>GGUF 8-bit, near-lossless</td></tr>" +
          "<tr><td>Q6_K, Q5_K_M</td><td>GGUF 6- and 5-bit " + t("q4_k_m", "K-quants") + "</td></tr>" +
          "<tr><td>" + t("q4_k_m", "Q4_K_M") + "</td><td>GGUF 4-bit K-quant, Medium: the most popular default</td></tr>" +
          "<tr><td>" + t("q4_0", "Q4_0") + "</td><td>simple 4-bit; used by QAT releases</td></tr>" +
          "<tr><td>" + t("quant-recipes", "IQ4_XS, IQ3, IQ2") + "</td><td>“i-quants”: smaller for the same quality, using an importance matrix</td></tr>" +
          "<tr><td>" + t("quant-recipes", "UD-Q4_K_XL") + "</td><td>Unsloth Dynamic: precision chosen layer by layer</td></tr>" +
          "<tr><td>" + t("mlx-quant", "4bit / 6bit / 8bit") + "</td><td>MLX group-wise quantization (groups of 64 weights)</td></tr>" +
          "<tr><td>" + t("mxfp4", "MXFP4 / NVFP4 / MXFP8") + "</td><td>4- and 8-bit floating-point formats (gpt-oss ships in MXFP4)</td></tr>" +
          "<tr><td>" + t("bf16", "BF16 / F16") + "</td><td>the original 16-bit weights</td></tr></tbody></table>") +
        box("8 · Who published the file", "<p>The model maker (<code>google</code>, <code>Qwen</code>, <code>openai</code>, <code>mistralai</code>…) publishes the original weights and the " + t("model-card", "model card") + " with benchmark scores. " + t("community-converters", "Converters") + " (<code>lmstudio-community</code>, <code>mlx-community</code>, <code>unsloth</code>, <code>bartowski</code>, <code>ggml-org</code>) repackage <b>the same model</b> into GGUF/MLX at different bits: same abilities, different file.</p>" +
          "<p>⚠ " + t("derived-model", "Derived models") + " are <b>not</b> the same model: fine-tunes, <code>abliterated</code> / <code>uncensored</code> (safety refusals removed), <code>Distill</code> (a small model trained to imitate a big one), merges. The original's public scores don't apply to them.</p>" +
          "<p>LM Studio groups several downloads of one model as " + t("variant", "variants") + "; Ollama uses tags after the colon (<code>gemma4:26b-mlx</code>).</p>") +
        "</div>" +

        '<div class="callout rules"><h3>Rules of thumb</h3><ul class="tight">' +
        "<li>Keep the weights at roughly <b>half of your RAM or less</b>, so there's room for the conversation (long documents add several GB) and the operating system.</li>" +
        "<li><b>Small models (≤12B): 8-bit.</b> Memory is cheap at that size and small models lose more from rounding.</li>" +
        "<li><b>20–35B: 4-bit, or QAT when available</b>; 5–6-bit if you want maximum quality and don't need huge contexts.</li>" +
        "<li><b>MoE models</b> are the best speed/quality deal on a desktop: fast like a small model, smarter than one.</li>" +
        "<li>On a Mac with LM Studio, try the <b>MLX</b> version first, but benchmark both: it depends on the model.</li>" +
        "<li>Comparing the same model at two bit levels (like your Qwen3.8 27B 4-bit vs 6-bit) shows exactly what the extra precision costs on your machine.</li></ul></div>"),

      section("fit-calc", "Will it fit? (calculator)", '<div id="fitcalc"></div>'),

      section("run", "What happens during a run",
        "<ol class=\"steps\">" +
        "<li><b>Clean machine.</b> Every model loaded in LM Studio and Ollama (including the model your agents use, e.g. Hermes, and " + t("embedding-model", "embedding models") + ") is unloaded, so nothing competes for memory. A " + t("contamination", "watchdog") + " checks every 10 s that nothing else gets loaded.</li>" +
        "<li><b>Cold loads.</b> The model is loaded twice from scratch to time " + t("cold-load", "loading") + " and the " + t("cold-ttft", "first request after loading") + ".</li>" +
        "<li><b>Warm-up.</b> A few short requests so the tests measure normal, " + t("warm-ttft", "warmed-up") + " speed.</li>" +
        "<li><b>Three tests × two " + t("reasoning-model", "thinking") + " modes × 3 " + t("repeats", "repeats") + ".</b> Short chat, extraction and the long document, first with thinking " + t("thinking-off", "off") + ", then " + t("thinking-high", "High") + ". The " + t("median", "median") + " is reported.</li>" +
        "<li><b>Live extraction.</b> The model reads the real web page about itself and extracts its scores (a bonus " + t("live-extraction", "agreement check") + ").</li>" +
        "<li><b>Memory</b> is sampled every 250 ms throughout, then everything that was loaded before is " + t("clean-machine", "reloaded") + ".</li></ol>" +
        '<p class="muted">Every model gets the same ' + t("context-window", "context window") + " (112k tokens), " + t("temperature", "temperature 0") + " and the same fixed prompts (" + t("suite-version", "suite version") + "), so differences come from the model, the file format and the engine, not from the settings.</p>"),

      section("tests", "The three tests",
        '<div class="grid-3">' +
        '<div class="callout"><h3>' + t("short-test", "Short chat") + "</h3><p>5 turns, under 4k tokens: explain, summarise, extract JSON, a follow-up, plan.</p><p><b>Tells you:</b> how snappy the model feels for everyday assistant and automation calls (Hermes chats, n8n AI nodes).</p><p><b>Look at:</b> " + t("ttft", "TTFT") + " and " + t("decode", "decode tok/s") + ".</p></div>" +
        '<div class="callout"><h3>' + t("extraction-test", "Extraction") + "</h3><p>~3k tokens of web page text in, a JSON object with 20 fields out, checked against an answer key.</p><p><b>Tells you:</b> whether the model reliably produces correct structured output, as an automation pipeline needs.</p><p><b>Look at:</b> " + t("extraction-accuracy", "accuracy") + ", " + t("json-valid", "JSON valid") + ", total time.</p></div>" +
        '<div class="callout"><h3>' + t("long-test", "Long document (64k+)") + "</h3><p>A ~73–85k-token handbook, then questions about 10 facts hidden at the start, middle and end.</p><p><b>Tells you:</b> how long you wait when you paste a big document, how quick follow-up questions are, and whether details get lost.</p><p><b>Look at:</b> " + t("prefill", "64k prefill") + ", 64k TTFT, " + t("followup-ttft", "follow-up TTFT") + ", " + t("recall", "recall") + ".</p></div>" +
        "</div>"),

      section("numbers", "Reading the speed numbers",
        "<p>A response has two phases. First the model <b>reads</b> everything you send (" + t("prefill", "prefill") + "), then it <b>writes</b> the answer one token at a time (" + t("decode", "decode") + "):</p>" +
        '<div class="formula">response time ≈ <b>prompt tokens ÷ prefill speed</b> <span class="muted">(= TTFT)</span> + <b>answer tokens ÷ decode speed</b></div>' +
        '<ul class="tight">' +
        "<li>Short prompts: TTFT is under a second for every model, so <b>decode speed</b> decides how long you wait. A 500-token answer takes ~6 s at 80 tok/s, but ~35 s at 14 tok/s.</li>" +
        "<li>Long prompts: <b>prefill speed</b> dominates. 73k tokens at 1,400 tok/s ≈ 52 s; at 178 tok/s ≈ 7 minutes before the first word.</li>" +
        "<li>Follow-up questions about the same document are fast for every model thanks to the " + t("prompt-cache", "prompt cache") + ": only the new question is read.</li>" +
        "<li>" + t("moe", "MoE") + " models (" + t("active-params", "A4B") + ") only use a few billion parameters per token, so they decode several times faster than " + t("dense", "dense") + " models of similar size, and usually prefill faster too.</li>" +
        "<li>With thinking on, the model writes " + t("reasoning-tokens", "hidden thinking tokens") + " first. What you wait for is the " + t("first-visible", "first visible token") + ".</li></ul>"),

      section("estimator", "Response-time estimator", '<div id="estimator"></div>'),

      section("thinking", "Thinking modes",
        "<p>Many recent models can “think” (write a hidden chain of reasoning) before answering. It improves hard reasoning, coding and agent tasks (the public benchmarks are mostly measured with thinking on), but it costs time: every thinking token is generated at decode speed.</p>" +
        '<ul class="tight"><li><b>' + t("thinking-off", "Off") + ":</b> answer immediately. Some models can't switch thinking off; their lowest level (" + "“low”" + ") is used instead and recorded.</li>" +
        "<li><b>" + t("thinking-high", "High") + ":</b> the highest standard level the model offers (“high”, or “on” if there are no levels).</li>" +
        "<li>The level each test actually used is stored as " + t("reasoning-applied", "reasoning applied") + ". If a model thinks longer than its " + t("thinking-budget", "thinking budget") + ", the answer is " + t("truncated", "cut off") + " and the run shows a warning.</li></ul>" +
        '<p class="muted">Rule of thumb: thinking off for quick lookups, routing and formatting steps; thinking on for planning, multi-step tool use and anything where a wrong answer is expensive.</p>'),

      section("memory", "Memory",
        "<p>On an Apple Silicon Mac the CPU and GPU share the same " + t("apple-silicon", "unified memory") + ", so the model has to fit in your RAM together with macOS and your apps. On a Windows or Linux PC with a graphics card, the model mostly lives in the card's own memory (VRAM), and whatever doesn't fit spills into RAM and runs much slower.</p>" +
        '<ul class="tight"><li>' + t("mem-loaded", "Loaded") + ": memory right after loading. Roughly the file " + t("model-size", "size") + " plus engine overhead.</li>" +
        "<li>" + t("mem-kv", "After the long document") + ": grows because of the " + t("kv-cache", "KV cache") + ", the model's working memory for the conversation. Longer context, more memory.</li>" +
        "<li>" + t("mem-peak", "Peak") + ": the most it ever used. <b>Plan with this number.</b> Leave at least 8 GB for the operating system and your apps (on a 64 GB computer: a peak up to ~56 GB; under ~48 GB is comfortable); if you want two models loaded at once (e.g. Hermes plus another), add their peaks.</li>" +
        "<li>If " + t("swap", "swap") + " grows during a run, the computer ran out of RAM and the results are slower than they should be.</li>" +
        "<li>The peak usually happens <b>while reading a long prompt</b>: a temporary " + t("reading-spike", "reading spike") + " on top of the weights and the context. " + t("ctx-peak", "Ctx @ peak") + " shows how much context was in use at that moment.</li>" +
        "<li>" + t("safe-context", "Safe ctx") + " turns that into a suggestion: the largest context that keeps the peak below your RAM minus 8 GB (left for the operating system and apps); the tooltip also shows 60%, 75% and 85% of RAM. Use it as the context length you set for that model in LM Studio, Ollama or Hermes; values beyond the tested ~75k tokens are extrapolated.</li></ul>"),

      section("public", "Public benchmark scores",
        "<p>These are published numbers, not measured here. They're grouped into " + t("categories", "categories") + " (reasoning, knowledge, math, coding, agentic, vision, long context, instruction following), and each category score is the average of its 0–100 scores.</p>" +
        '<ul class="tight"><li>Each score shows its source and ' + t("method", "method") + ". Your own corrections in <code>data/overrides.json</code> always win.</li>" +
        "<li>“" + t("applies-to", "applies to: base") + "” means the score was measured on the original full-precision model. Your " + t("quantization", "quantized") + " copy will be slightly lower, less so with " + t("qat", "QAT") + ".</li>" +
        "<li>Vendors pick their own settings and usually report with thinking on, so compare the same benchmark across models rather than averages from different sources.</li>" +
        "<li>For agents (Hermes, n8n), the most relevant ones are " + t("tau2", "τ²-bench") + ", " + t("bfcl", "BFCL") + ", " + t("ifeval", "IFEval/IFBench") + ", " + t("terminal-bench", "Terminal-Bench") + " and " + t("swe-bench", "SWE-bench") + ".</li></ul>"),

      section("fit", "The fit score",
        "<p>The " + t("fit-score", "fit score") + " on the Models page combines everything into one 0–100 number using the sliders: " + t("fit-speed", "Speed") + ", " + t("fit-long", "Long context") + ", " + t("fit-intel", "Intelligence") + ", " + t("fit-agentic", "Agentic") + " and " + t("fit-memory", "Memory efficiency") + ".</p>" +
        '<ul class="tight"><li>Each metric is scaled from the worst (0) to the best (1) model <b>currently shown</b>, then weighted by the sliders. So it ranks your models against each other; it isn\'t an absolute grade.</li>' +
        "<li>Missing data counts as 0 unless you untick that option; a <b>*</b> marks scores with gaps.</li>" +
        "<li>Use it to shortlist two or three models, then open them in <a href=\"#/compare\">Compare</a> and look at the details.</li></ul>"),

      section("choose", "How to choose a model",
        '<div class="grid-2">' +
        '<div class="callout"><h3>Chat assistant / agent (e.g. Hermes)</h3><p>Most requests are short with some history and tools. Prioritise <b>short decode speed</b> and <b>TTFT</b>, then agentic scores (' + t("tau2", "τ²-bench") + ", " + t("bfcl", "BFCL") + "). A fast " + t("moe", "MoE") + " model often feels far better than a slightly smarter slow one.</p></div>" +
        '<div class="callout"><h3>n8n automations</h3><p>Reliability beats eloquence. Prioritise <b>' + t("extraction-accuracy", "extraction accuracy") + "</b>, " + t("json-valid", "valid JSON") + " and " + t("ifeval", "instruction following") + ". Speed matters if a workflow makes many calls; thinking can usually stay off for simple steps.</p></div>" +
        '<div class="callout"><h3>Long documents / RAG</h3><p>Prioritise <b>' + t("prefill", "64k prefill") + "</b> (how long before the first word) and <b>" + t("recall", "recall") + "</b>. Check " + t("mem-kv", "memory after the long document") + " if you plan to use even longer inputs.</p></div>" +
        '<div class="callout"><h3>Hard reasoning / coding</h3><p>Prioritise public reasoning and coding scores and use thinking High, accepting slower answers. Check the ' + t("first-visible", "first visible token") + " time with thinking High to see how long you'll wait.</p></div>" +
        "</div>" +
        '<p class="muted">Engines and formats matter too: the same model can run noticeably faster as ' + t("mlx", "MLX") + " in LM Studio than as " + t("gguf", "GGUF") + ", or the other way round. Benchmark both if you're unsure; each download is a separate row.</p>"),

      section("caveats", "Caveats",
        '<ul class="tight"><li>Results are for <b>this machine, these engine versions and these settings</b>. After an LM Studio or Ollama update, re-test with <code>./bench run --force</code>.</li>' +
        "<li>Background load (other apps, Time Machine, heat) can slow a run; the " + t("median", "median") + " of 3 " + t("repeats", "repeats") + " limits the effect.</li>" +
        "<li>Different " + t("tokenizer", "tokenizers") + " count the same document differently (73k–85k tokens), so compare tok/s rather than token counts.</li>" +
        "<li>Public scores are self-reported by vendors or measured by third parties under different conditions. Treat them as indicative.</li></ul>"),

      section("commands", "Command cheat sheet",
        '<table class="data compact cheat"><tbody>' +
        [["./bench list", "Downloaded models and whether they've been benchmarked"],
         ["./bench run --next", "Benchmark the next untested model only"],
         ["./bench run --no-input", "Benchmark every untested model, one after another"],
         ["./bench run qwen --force", "Re-test a specific model (after an engine update, say)"],
         ["./bench run --dry-run", "Show what would run, without loading anything"],
         ["./bench status", "What's loaded in LM Studio / Ollama right now"],
         ["./bench enrich --refresh", "Refresh public benchmark data"],
         ["./bench dashboard", "Regenerate and open this dashboard (no server)"],
         ["./bench dashboard --live", "Same dashboard from a local server (Ctrl+C stops it)"],
         ["./bench publish --out <folder>", "Copy for any web server, or to share"]]
          .map(([c, d]) => "<tr><td><code>" + esc(c) + "</code></td><td>" + esc(d) + "</td></tr>").join("") +
        "</tbody></table>"),
    ].join("");
  }

  // ---------------------------------------------------------------- estimator
  function estimator(el, ctx) {
    const rows = ctx.idx.rows.filter((r) => r.run && r.run.summary);
    const state = BL.store.get("estimator", { prompt: 2000, answer: 400, thinking: false });
    const draw = () => {
      const P = Math.max(0, Number(state.prompt) || 0), A = Math.max(0, Number(state.answer) || 0);
      const long = P > 8000;
      const est = rows.map((r) => {
        const s = (k) => BL.sv(r.run, k);
        const prefill = long ? s("long_off_prefill_tps") : s("short_off_prefill_tps");
        const decode = long ? s("long_off_decode_tps") : s("short_off_decode_tps");
        const base = isNum(s("warm_ttft_s")) ? s("warm_ttft_s") : 0;
        let think = 0;
        if (state.thinking) {
          const rt = s("short_high_reasoning_tokens");
          think = isNum(rt) ? rt / 5 : null; // average per turn in the 5-turn short test
        }
        if (!isNum(prefill) || !isNum(decode) || think === null) return { r, total: null };
        const ttft = long ? P / prefill : Math.max(base, P / prefill);
        const first = ttft + (think || 0) / decode;   // thinking happens before the first visible word
        const total = first + A / decode;
        return { r, first, total };
      }).sort((a, b) => (isNum(a.total) ? a.total : 1e12) - (isNum(b.total) ? b.total : 1e12));
      const max = Math.max(...est.map((e) => e.total || 0), 1);
      el.querySelector("#est-out").innerHTML = rows.length
        ? '<table class="data compact est"><thead><tr><th>Model</th><th class="num">Wait for first word</th><th class="num">Total</th><th></th></tr></thead><tbody>' +
          est.map((e) => "<tr><td><a href=\"" + BL.modelHref(e.r.uid) + "\">" + esc(BL.modelName(e.r.model)) + "</a> <span class=\"muted small\">" + BL.engineText(e.r.model.engine) + "</span></td>" +
            '<td class="num">' + (isNum(e.first) ? dur(e.first) : "—") + "</td>" +
            '<td class="num"><b>' + (isNum(e.total) ? dur(e.total) : "—") + "</b></td>" +
            '<td class="bar-cell"><span class="est-bar" style="width:' + (isNum(e.total) ? Math.max(2, (e.total / max) * 100) : 0) + '%"></span></td></tr>').join("") +
          "</tbody></table>" +
          '<p class="muted small">Uses each model\'s measured ' + (long ? "64k-test" : "short-test") + " prefill and decode speeds" + (state.thinking ? " plus its average thinking tokens per turn (short test, thinking High)" : "") +
          ". Prompts over 8,000 tokens use the long-context speeds. Real times vary with the content and context length.</p>"
        : '<p class="muted">No benchmark results yet: run <code>./bench run</code> first.</p>';
      BL.store.set("estimator", state);
    };
    const dur = (s) => (s < 60 ? s.toFixed(1) + " s" : Math.floor(s / 60) + " min " + Math.round(s % 60) + " s");
    el.innerHTML =
      "<p>How long would a typical request take with each model? Enter a prompt size and answer length (as a guide: a page of text ≈ 500 tokens, a long report ≈ 10k–20k, the test handbook ≈ 75k).</p>" +
      '<div class="est-form">' +
      '<label>Prompt <input type="number" id="est-p" min="0" step="500" value="' + esc(state.prompt) + '"> tokens</label>' +
      '<label>Answer <input type="number" id="est-a" min="0" step="100" value="' + esc(state.answer) + '"> tokens</label>' +
      '<label class="inline"><input type="checkbox" id="est-t"' + (state.thinking ? " checked" : "") + "> include thinking (High)</label>" +
      '<span class="est-presets">' + [["Quick chat", 800, 200], ["Agent tool call", 4000, 300], ["Summarise a report", 15000, 600], ["Ask the 64k handbook", 75000, 300]]
        .map(([l, p, a]) => '<button type="button" data-p="' + p + '" data-a="' + a + '">' + esc(l) + "</button>").join("") + "</span></div>" +
      '<div id="est-out"></div>';
    el.querySelector("#est-p").addEventListener("input", (e) => { state.prompt = e.target.value; draw(); });
    el.querySelector("#est-a").addEventListener("input", (e) => { state.answer = e.target.value; draw(); });
    el.querySelector("#est-t").addEventListener("change", (e) => { state.thinking = e.target.checked; draw(); });
    el.querySelectorAll(".est-presets button").forEach((b) => b.addEventListener("click", () => {
      state.prompt = Number(b.dataset.p); state.answer = Number(b.dataset.a);
      el.querySelector("#est-p").value = state.prompt; el.querySelector("#est-a").value = state.answer; draw();
    }));
    draw();
  }

  BL.views.explain = function (app, ctx) {
    app.innerHTML =
      '<div class="explain-page"><div class="page-head"><h1>How this works</h1>' +
      '<p class="muted">What the tool measures, how to read the numbers, and how to use them to pick a model. Underlined terms show a definition when you hover or tap them; the <a href="#/glossary">Glossary</a> lists them all.</p></div>' +
      '<div class="explain-layout"><nav class="toc">' + TOC.map(([id, l]) => '<a href="#/explain?s=' + id + '">' + esc(l) + "</a>").join("") + "</nav>" +
      '<div class="explain-body">' + content() + "</div></div></div>";
    estimator(app.querySelector("#estimator"), ctx);
    fitCalc(app.querySelector("#fitcalc"), ctx);
    if (ctx.params.s) {
      const target = document.getElementById("x-" + ctx.params.s);
      if (target) requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
    }
  };
})();
