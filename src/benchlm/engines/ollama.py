"""Ollama adapter: native API (/api/*)."""
from __future__ import annotations

import hashlib
import re
import time
from typing import Callable, List, Optional

from .. import http
from .base import AuthRequired, Engine, Turn, bits_from_quant, has_qat, moe_active_estimate, parse_params

NS = 1e9
# Families whose thinking takes low/medium/high and cannot be switched off (Ollama ignores think=false).
THINK_LEVELS = re.compile(r"gpt-?oss", re.I)


class Ollama(Engine):
    id = "ollama"
    name = "Ollama"
    stops_on_disconnect = True   # measured 2026-10-21: GPU idle ~3 s after a cancel mid-prefill

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _get(self, path, timeout=30):
        try:
            return http.get_json(self.base_url + path, self._headers(), timeout)
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            raise

    def _post(self, path, payload, timeout=900):
        try:
            return http.post_json(self.base_url + path, payload, self._headers(), timeout)
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            raise

    def available(self) -> bool:
        return http.port_open(self.base_url)

    def check_auth(self) -> None:
        self._get("/api/tags", timeout=10)

    def info(self) -> dict:
        try:
            v = self._get("/api/version", timeout=5).get("version")
        except Exception:
            v = None
        return {"id": self.id, "name": self.name, "version": v, "base_url": self.base_url, "runtimes": {}}

    def list_models(self) -> List[dict]:
        out = []
        for m in self._get("/api/tags").get("models", []):
            name = m.get("name") or m.get("model")
            try:
                show = self._post("/api/show", {"model": name}, timeout=30)
            except Exception:
                show = {}
            norm = self._normalize(m, show)
            if norm:
                out.append(norm)
        return out

    def _normalize(self, m: dict, show: dict) -> Optional[dict]:
        name = m.get("name") or m.get("model")
        details = show.get("details") or m.get("details") or {}
        caps = show.get("capabilities") or []
        if caps and "completion" not in caps:
            return None  # embedding-only
        info = show.get("model_info") or {}
        arch = info.get("general.architecture") or details.get("family")
        ctx = info.get(f"{arch}.context_length") if arch else None
        pcount = info.get("general.parameter_count")
        total, active = parse_params(details.get("parameter_size") or "", name)
        if pcount:
            total = round(pcount / 1e9, 2)
        experts = info.get(f"{arch}.expert_count") if arch else None
        source = "name" if active is not None else None
        if experts and active is None:
            _, active = parse_params(name)
            source = "name" if active is not None else None
        if experts and active is None:
            # from the GGUF metadata: expert count / experts per token / sizes
            active = moe_active_estimate(total, info.get(f"{arch}.block_count"), info.get(f"{arch}.embedding_length"),
                                         info.get(f"{arch}.expert_feed_forward_length"), experts,
                                         info.get(f"{arch}.expert_used_count"),
                                         info.get(f"{arch}.leading_dense_block_count"))
            source = "estimated from GGUF metadata" if active is not None else None
        qname = details.get("quantization_level")
        key, _, tag = name.partition(":")
        fp = hashlib.sha1(f"{name}|{m.get('digest')}".encode()).hexdigest()[:12]
        return {
            "model_uid": f"ollama:{name}", "engine": "ollama", "key": key, "variant": tag or "latest",
            "display_name": name, "publisher": key.split("/")[0] if "/" in key else None,
            "architecture": arch, "params_string": details.get("parameter_size"),
            "params_total_b": total, "params_active_b": active, "is_moe": bool(experts) or active is not None,
            "params_active_source": source,
            "moe_experts": experts, "moe_experts_per_token": info.get(f"{arch}.expert_used_count") if experts else None,
            "format": (details.get("format") or "gguf").lower(),
            "quantization": {"name": qname, "bits": bits_from_quant(qname)},
            "qat": has_qat(name),
            "size_bytes": m.get("size"), "max_context_length": ctx,
            "capabilities": {"vision": "vision" in caps, "tool_use": "tools" in caps,
                             "reasoning": (({"allowed_options": ["low", "medium", "high"], "default": "medium",
                                             "levels": True} if THINK_LEVELS.search(f"{arch} {name}") else
                                            {"allowed_options": ["off", "on"], "default": "on"})
                                           if "thinking" in caps else None)},
            "description": None, "fingerprint": fp, "digest": m.get("digest"),
            "_load_key": name,
        }

    def loaded(self) -> List[dict]:
        out = []
        for m in self._get("/api/ps", timeout=10).get("models", []):
            out.append({"engine": self.id, "model_key": m.get("name") or m.get("model"),
                        "instance_id": m.get("name") or m.get("model"), "type": "llm",
                        "config": {"context_length": m.get("context_length"), "size": m.get("size"),
                                   "size_vram": m.get("size_vram")}})
        return out

    def load(self, model: dict, profile: dict) -> dict:
        name = model.get("_load_key") or model["model_uid"].split(":", 1)[1]
        t0 = time.perf_counter()
        r = self._post("/api/generate", {"model": name, "prompt": "", "stream": False, "keep_alive": "2h",
                                         "options": {"num_ctx": int(profile["context_length"])}}, timeout=1800)
        client = time.perf_counter() - t0
        cfg = {"context_length": int(profile["context_length"])}
        for inst in self.loaded():
            if inst["instance_id"] == name:
                cfg.update({k: v for k, v in inst["config"].items() if v is not None})
        return {"instance_id": name, "load_time_s": (r.get("load_duration") or 0) / NS or client,
                "client_load_time_s": client, "load_config": cfg}

    def unload(self, instance: dict) -> None:
        self._post("/api/generate", {"model": instance["instance_id"], "keep_alive": 0, "stream": False}, timeout=120)
        for _ in range(60):
            if not any(i["instance_id"] == instance["instance_id"] for i in self.loaded()):
                return
            time.sleep(0.5)

    def restore(self, instance: dict) -> None:
        opts = {}
        ctx = (instance.get("config") or {}).get("context_length")
        if ctx:
            opts["num_ctx"] = ctx
        self._post("/api/generate", {"model": instance["instance_id"], "prompt": "", "stream": False,
                                     "options": opts}, timeout=1800)

    def unload_hint(self, instance: dict) -> str:
        return f'Ollama: run  ollama stop {instance["instance_id"]}'

    def resolve_reasoning(self, model: dict, mode: str):
        r = (model.get("capabilities") or {}).get("reasoning")
        if not r:
            if mode == "off":
                return None
            raise ValueError("model has no thinking capability")
        if r.get("levels"):
            return "low" if mode == "off" else "high"
        return False if mode == "off" else "high"

    def chat(self, instance_id, model, system_prompt, user_text, state, reasoning, max_tokens, profile,
             on_phase: Optional[Callable[[str], None]] = None, cancel: Optional[http.Cancel] = None) -> Turn:
        messages = list(state or [])
        if not messages and system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_text})
        options = {"num_ctx": int(profile["context_length"]), "temperature": profile["temperature"],
                   "top_p": profile["top_p"], "top_k": profile["top_k"], "min_p": profile.get("min_p", 0),
                   "repeat_penalty": profile.get("repeat_penalty", 1), "seed": profile.get("seed", 42),
                   "num_predict": int(max_tokens)}
        payload = {"model": instance_id, "messages": messages, "stream": True, "keep_alive": "2h",
                   "options": options}
        if reasoning is not None:
            payload["think"] = reasoning
        try:
            return self._chat(payload, messages, on_phase, profile, cancel)
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            if reasoning == "high" and e.status == 400:
                payload["think"] = True   # model supports on/off only
                t = self._chat(payload, messages, on_phase, profile, cancel)
                t.reasoning_applied = "on"
                return t
            raise

    def _chat(self, payload, messages, on_phase, profile, cancel=None) -> Turn:
        t = Turn()
        t.reasoning_applied = None
        t.t_send = time.perf_counter()
        if on_phase:
            on_phase("prefill")
        decoding = False
        for chunk in http.stream_ndjson(self.base_url + "/api/chat", payload, self._headers(),
                                        timeout=profile.get("request_timeout_s", 1800), cancel=cancel):
            if chunk.get("error"):
                raise RuntimeError(f"Ollama error: {chunk['error']}")
            msg = chunk.get("message") or {}
            if msg.get("thinking"):
                t.mark_token(False)
                t.reasoning_text += msg["thinking"]
            if msg.get("content"):
                t.mark_token(True)
                t.text += msg["content"]
            if not decoding and t.ttft_s is not None and on_phase:
                on_phase("decode")
                decoding = True
            if chunk.get("done"):
                t.prompt_tokens = chunk.get("prompt_eval_count")
                t.new_prompt_tokens = chunk.get("prompt_eval_count")
                t.completion_tokens = chunk.get("eval_count")
                pe_d, ev_d = chunk.get("prompt_eval_duration"), chunk.get("eval_duration")
                if pe_d and t.prompt_tokens:
                    t.server_prefill_tps = t.prompt_tokens / (pe_d / NS)
                if ev_d and t.completion_tokens:
                    t.server_decode_tps = t.completion_tokens / (ev_d / NS)
                if chunk.get("load_duration"):
                    t.load_time_s = chunk["load_duration"] / NS
                t.finish_reason = chunk.get("done_reason")
        t.total_s = time.perf_counter() - t.t_send
        if t.reasoning_text:
            # Ollama doesn't split eval_count; estimate reasoning share by characters.
            total_chars = len(t.reasoning_text) + len(t.text)
            if t.completion_tokens and total_chars:
                t.reasoning_tokens = round(t.completion_tokens * len(t.reasoning_text) / total_chars)
        assistant = {"role": "assistant", "content": t.text}
        t.state = messages + [assistant]
        return t

    def process_match(self, cmdline: str) -> bool:
        return "ollama" in self.executable(cmdline)
