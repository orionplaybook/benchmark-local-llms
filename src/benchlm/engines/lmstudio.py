"""LM Studio adapter: native REST API v1 (/api/v1/*)."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import plistlib
import shutil
import subprocess
import time
from typing import Callable, List, Optional

from .. import http
from .base import (REASONING_LEVELS, AuthRequired, Engine, EngineUnavailable, Turn, bits_from_quant,
                   has_qat, parse_params)


class LMStudio(Engine):
    id = "lmstudio"
    name = "LM Studio"
    stops_on_disconnect = True   # measured 2026-10-21: GPU idle ~1 s (MLX), ~2 s (llama.cpp) after a cancel mid-prefill

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

    # --- discovery -------------------------------------------------------
    def available(self) -> bool:
        return http.port_open(self.base_url)

    def check_auth(self) -> None:
        self._get("/api/v1/models", timeout=10)

    def _app_version(self) -> Optional[str]:
        if platform.system() == "Darwin":
            p = "/Applications/LM Studio.app/Contents/Info.plist"
            try:
                with open(p, "rb") as f:
                    return plistlib.load(f).get("CFBundleShortVersionString")
            except (OSError, ValueError):
                pass
        lms = self._lms()
        if lms:
            try:
                out = subprocess.run([lms, "version"], capture_output=True, text=True, timeout=15).stdout
                for line in out.splitlines():
                    if "version" in line.lower() and any(c.isdigit() for c in line):
                        return line.strip()
            except (OSError, subprocess.SubprocessError):
                pass
        return None

    def _lms(self) -> Optional[str]:
        cand = os.path.expanduser("~/.lmstudio/bin/lms")
        if platform.system() == "Windows":
            cand += ".exe"
        return cand if os.path.exists(cand) else shutil.which("lms")

    def _runtimes(self) -> dict:
        lms = self._lms()
        if not lms:
            return {}
        try:
            out = subprocess.run([lms, "runtime", "ls", "--json"], capture_output=True, text=True, timeout=20).stdout
            data = json.loads(out)
        except (OSError, subprocess.SubprocessError, ValueError):
            return {}
        result = {}
        items = data if isinstance(data, list) else data.get("runtimes", []) if isinstance(data, dict) else []
        for rt in items:
            if not isinstance(rt, dict):
                continue
            if rt.get("selected") or rt.get("isSelected") or rt.get("active"):
                for fmt in rt.get("supportedModelFormats") or rt.get("formats") or [rt.get("engine", "")]:
                    result[str(fmt).lower()] = f"{rt.get('name') or rt.get('engine')} {rt.get('version', '')}".strip()
        return result

    def info(self) -> dict:
        return {"id": self.id, "name": self.name, "version": self._app_version(),
                "base_url": self.base_url, "runtimes": self._runtimes()}

    def list_models(self) -> List[dict]:
        data = self._get("/api/v1/models")
        out = []
        for m in data.get("models", []):
            if m.get("type") != "llm":
                continue
            out.append(self._normalize(m))
        return out

    def _normalize(self, m: dict) -> dict:
        key = m.get("key")
        variant_full = m.get("selected_variant") or key
        variant = variant_full.split("@", 1)[1] if "@" in variant_full else None
        q = m.get("quantization") or {}
        total, active = parse_params(m.get("params_string") or "", key, m.get("display_name") or "")
        caps = m.get("capabilities") or {}
        fmt = (m.get("format") or "").lower() or None
        fp = hashlib.sha1(f"{key}|{variant}|{m.get('size_bytes')}".encode()).hexdigest()[:12]
        return {
            "model_uid": f"lmstudio:{key}@{variant}" if variant else f"lmstudio:{key}",
            "engine": "lmstudio", "key": key, "variant": variant,
            "display_name": m.get("display_name") or key, "publisher": m.get("publisher"),
            "architecture": m.get("architecture"), "params_string": m.get("params_string"),
            "params_total_b": total, "params_active_b": active,
            # LM Studio doesn't report experts; MoE shows in the name (A3B) or the architecture (glm4_moe_lite).
            # gpt-oss has neither: Hugging Face's config.json fills it in (bench enrich).
            "is_moe": active is not None or "moe" in (m.get("architecture") or "").lower(),
            "params_active_source": "name" if active is not None else None,
            "format": fmt,
            "quantization": {"name": q.get("name"), "bits": q.get("bits_per_weight") or bits_from_quant(q.get("name"))},
            "qat": has_qat(key, m.get("display_name") or ""),
            "size_bytes": m.get("size_bytes"), "max_context_length": m.get("max_context_length"),
            "capabilities": {"vision": bool(caps.get("vision")), "tool_use": bool(caps.get("trained_for_tool_use")),
                             "reasoning": caps.get("reasoning")},
            "description": m.get("description"),
            "fingerprint": fp,
            "_load_key": variant_full,
        }

    def loaded(self) -> List[dict]:
        data = self._get("/api/v1/models", timeout=10)
        out = []
        for m in data.get("models", []):
            for inst in m.get("loaded_instances") or []:
                out.append({"engine": self.id, "model_key": m.get("key"), "instance_id": inst.get("id"),
                            "type": m.get("type"), "config": inst.get("config") or {}})
        return out

    # --- lifecycle -------------------------------------------------------
    def load(self, model: dict, profile: dict) -> dict:
        payload = {"model": model.get("_load_key") or model["key"],
                   "context_length": int(profile["context_length"]), "echo_load_config": True}
        if model.get("format") == "gguf":
            for k in ("flash_attention", "offload_kv_cache_to_gpu", "eval_batch_size"):
                if profile.get(k) is not None:
                    payload[k] = profile[k]
        t0 = time.perf_counter()
        try:
            r = self._post("/api/v1/models/load", payload, timeout=1800)
        except http.HTTPError as e:
            if e.status != 404 or payload["model"] == model["key"]:
                raise
            payload["model"] = model["key"]          # single-variant models load by plain key
            t0 = time.perf_counter()
            r = self._post("/api/v1/models/load", payload, timeout=1800)
        client = time.perf_counter() - t0
        return {"instance_id": r.get("instance_id"), "load_time_s": r.get("load_time_seconds") or client,
                "client_load_time_s": client, "load_config": r.get("load_config") or {}}

    def unload(self, instance: dict) -> None:
        self._post("/api/v1/models/unload", {"instance_id": instance["instance_id"]}, timeout=120)

    def restore(self, instance: dict) -> None:
        cfg = instance.get("config") or {}
        payload = {"model": instance["model_key"]}
        for k in ("context_length", "flash_attention", "offload_kv_cache_to_gpu", "eval_batch_size", "num_experts"):
            if cfg.get(k) is not None:
                payload[k] = cfg[k]
        self._post("/api/v1/models/load", payload, timeout=1800)

    def unload_hint(self, instance: dict) -> str:
        return (f'LM Studio: eject "{instance["model_key"]}" in the Developer tab, or run: '
                f'lms unload "{instance["instance_id"]}"')

    # --- inference -------------------------------------------------------
    def resolve_reasoning(self, model: dict, mode: str) -> Optional[str]:
        r = (model.get("capabilities") or {}).get("reasoning") or {}
        allowed = r.get("allowed_options") or []
        if not allowed:
            if mode == "off":
                return None
            raise ValueError("model has no configurable reasoning")
        if mode == "off":
            if "off" in allowed:
                return "off"
            for lvl in REASONING_LEVELS:          # lowest available
                if lvl in allowed:
                    return lvl
            return None
        for lvl in ("high", "on", "xhigh", "medium"):
            if lvl in allowed:
                return lvl
        raise ValueError("no high reasoning option")

    def chat(self, instance_id, model, system_prompt, user_text, state, reasoning, max_tokens, profile,
             on_phase: Optional[Callable[[str], None]] = None, cancel: Optional[http.Cancel] = None) -> Turn:
        payload = {"model": instance_id, "input": user_text, "stream": True, "store": True,
                   "temperature": profile["temperature"], "top_p": profile["top_p"], "top_k": profile["top_k"],
                   "min_p": profile.get("min_p", 0), "repeat_penalty": profile.get("repeat_penalty", 1),
                   "max_output_tokens": int(max_tokens)}
        if state:
            payload["previous_response_id"] = state
        elif system_prompt:
            payload["system_prompt"] = system_prompt
        if reasoning:
            payload["reasoning"] = reasoning
        t = Turn()
        t.t_send = time.perf_counter()
        pp_start = None
        try:
            for ev, data in http.stream_sse(self.base_url + "/api/v1/chat", payload, self._headers(),
                                            timeout=profile.get("request_timeout_s", 1800), cancel=cancel):
                if ev == "reasoning.delta":
                    t.mark_token(False)
                    t.reasoning_text += data.get("content", "")
                elif ev == "message.delta":
                    t.mark_token(True)
                    t.text += data.get("content", "")
                elif ev == "prompt_processing.start":
                    pp_start = time.perf_counter()
                    if on_phase:
                        on_phase("prefill")
                elif ev == "prompt_processing.end":
                    if pp_start:
                        t.prompt_processing_s = time.perf_counter() - pp_start
                    if on_phase:
                        on_phase("decode")
                elif ev == "model_load.end":
                    t.load_time_s = data.get("load_time_seconds")
                elif ev == "error":
                    raise RuntimeError(f"LM Studio error: {data.get('error')}")
                elif ev == "chat.end":
                    res = data.get("result") or {}
                    st = res.get("stats") or {}
                    t.prompt_tokens = st.get("input_tokens")
                    t.completion_tokens = st.get("total_output_tokens")
                    t.reasoning_tokens = st.get("reasoning_output_tokens") or 0
                    t.server_ttft_s = st.get("time_to_first_token_seconds")
                    t.server_decode_tps = st.get("tokens_per_second")
                    if st.get("model_load_time_seconds"):
                        t.load_time_s = st.get("model_load_time_seconds")
                    t.state = res.get("response_id")
                    if not t.text:
                        for item in res.get("output") or []:
                            if item.get("type") == "message":
                                t.text += item.get("content") or ""
                            elif item.get("type") == "reasoning" and not t.reasoning_text:
                                t.reasoning_text += item.get("content") or ""
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            raise
        t.total_s = time.perf_counter() - t.t_send
        if t.completion_tokens is not None and t.completion_tokens >= int(max_tokens) - 1:
            t.finish_reason = "length"
        else:
            t.finish_reason = "stop"
        return t

    # --- memory ----------------------------------------------------------
    def process_match(self, cmdline: str) -> bool:
        exe = self.executable(cmdline)
        return ".lmstudio" in exe or "lm studio" in exe or "lmstudio" in exe or "llmster" in exe
