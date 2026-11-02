# Benchmark suite (suite_version 1)

This folder holds the fixed test content that `bench run` sends to every local
model. Every model gets the same prompts with temperature 0 and the same
`max_tokens` caps, so timings can be compared. All content is fictional and
written for this tool.

| Test | Files | Measures |
|---|---|---|
| A. Short conversation | `short_conversation.json` | Time to first token, generation tokens/s and memory with a small, growing context (under ~3k tokens) |
| B. Long context | `long_context/` | Prompt processing speed and time to first token on a 73–85k-token prompt (depends on the tokenizer, always ≥64k), generation speed with a full KV cache, peak memory, plus recall of 10 planted facts |
| C. Extraction | `extraction/` | Speed and accuracy of turning two web-page snapshots into a JSON object |

## A. Short conversation

Five user turns for an assistant inside an automation workflow: (1) a short
explanation, (2) a summary of a ~180-word customer note, (3) JSON extraction
from an email with given keys, (4) a follow-up that depends on turns 2 and 3,
(5) a short plan as a numbered list. Each turn is sent with the full history
so far. `max_tokens` (192–360) caps output per turn. The answers are not
scored; this test is for speed and memory.

## B. Long context

- `long_context/document.md` is a ~300k-character document (≈73k tokens for Gemma, ≈83k at 3.6 chars/token) handbook for the fictional company Northwind Orbital
  Logistics: policies, specification tables, changelogs, code blocks, meeting
  notes, incident reviews, FAQs and a glossary.
- It is produced by `long_context/generate_document.py` (fixed seed
  `20261019`, standard library only). The generated file is stored in the
  folder; `long_context/document.sha256` holds its hash so the runner can
  check the file has not changed. Running the generator again reproduces the
  same bytes.
- `long_context/facts.json` lists the 10 planted facts: question, accepted
  answers and position in the document (2 in the first 10 %, 3 between 40 %
  and 60 %, 2 in the last 10 %, the rest elsewhere). Each canonical answer
  appears exactly once in the document.
- `long_context/conversation.json`: turn 1 sends the whole document
  (`<<DOCUMENT>>` in `user_template` is replaced by `document.md`) and asks
  for a 3-sentence overview. Turns 2–4 ask about the facts near the start,
  middle and end; `fact_ids` says which facts each turn covers.

**Recall scoring.** For every fact, the runner takes the model's answer to
the turn that lists that fact in `fact_ids` and checks, case-insensitively,
whether any string in the fact's `answers` is a substring of that answer
(after removing any `<think>…</think>` block). A fact counts as recalled if
it matches. The recall score is the number of recalled facts out of 10.

## C. Extraction

- `extraction/page_model_card.md`: a model card for the fictional
  "Aurora-Lite 14B Instruct", with metadata and two benchmark tables in
  different layouts, plus distracting numbers (other models, a preview
  checkpoint, footnotes, non-thinking scores).
- `extraction/page_leaderboard.md`: a leaderboard snippet with three more
  scores for the same model (Arena Elo, Agentic Index, Coding Index).
- `extraction/prompt.json`: system prompt and `user_template`; the runner
  replaces `<<PAGE1>>` and `<<PAGE2>>` with the files named in `page1` and
  `page2`.
- `extraction/answer_key.json`: expected values (5 fields + 15 benchmarks =
  20 scored fields). A list value means any of those strings is accepted.
- `extraction/score_extraction.py`: `score(output_text, answer_key) -> dict`
  returns `json_valid`, `fields_correct`, `fields_total`, `accuracy` and
  per-field `details`. It strips `<think>` blocks and code fences, takes the
  first balanced JSON object, compares numbers with an absolute tolerance of
  0.051 and strings case-insensitively after trimming. Run
  `python3 score_extraction.py` for the self-test, or
  `python3 score_extraction.py output.txt answer_key.json` to score a file.

## suite_version rule

`short_conversation.json`, `long_context/conversation.json`, `extraction/prompt.json` and
`extraction/answer_key.json` carry `"suite_version": "1"`, and results store it.
**Any change to any file in this folder** (a prompt, a `max_tokens` value, the
generator, the document, the facts, the pages or the answer key) means bumping
`suite_version` in all of them to `"2"` (then `"3"`, and so on), regenerating
`document.md` and `document.sha256` if the generator changed. Results with
different suite versions must not be compared with each other.
