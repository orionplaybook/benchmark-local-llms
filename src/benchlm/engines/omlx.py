"""oMLX adapter (github.com/jundot/omlx): OpenAI-compatible /v1/* plus its admin API (/admin/api/*).

oMLX caps every model at a server-wide context window (32k by default). For a run, the model's own
max_context_window setting is raised to the profile's context length, and put back when the model is unloaded.
"""
from __future__ import annotations

import hashlib
import json
import platform
import plistlib
import re
import time
from pathlib import Path
from typing import Callable, List, Optional
from urllib.parse import quote

from .. import http
from .base import AuthRequired, Engine, Turn, bits_from_quant, has_qat, hf_source, parse_params

APP_PLIST = "/Applications/oMLX.app/Contents/Info.plist"
DEFAULT_URL = "http://127.0.0.1:8000"
LLM_TYPES = ("llm", "vlm")


def quant_from_name(*names: str) -> Optional[str]:
    for n in names:
        m = re.search(r"(mxfp4(?:-q\d)?|nvfp4|oq\d+[a-z]*|q\d(?:_k)?(?:_[msl])?|\d+-?bit|bf16|fp16|f16)", (n or "").lower())
        if m:   # written like the other engines: MXFP4-Q8, Q4_K_M, BF16, but 4bit
            q = m.group(1)
            return q if q.endswith("bit") else "oQ" + q[2:] if q.startswith("oq") else q.upper()
    return None


class OMLX(Engine):
    id = "omlx"
    name = "oMLX"
    default_url = DEFAULT_URL
    stops_on_disconnect = False   # not measured yet: the runner reloads the model after a cancel

    def __init__(self, base_url: str, api_key: str = ""):
        super().__init__(base_url, api_key)
        self._ctx_restore = {}    # model id -> max_context_window it had before the run

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _call(self, method, path, payload=None, timeout=60):
        try:
            if method == "GET":
                return http.get_json(self.base_url + path, self._headers(), timeout)
            if method == "POST":
                return http.post_json(self.base_url + path, payload or {}, self._headers(), timeout)
            with http._request(self.base_url + path, method, payload, self._headers(), timeout) as r:
                body = r.read()
            return json.loads(body) if body else {}
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            raise

    # --- discovery -------------------------------------------------------
    def available(self) -> bool:
        if not http.port_open(self.base_url):
            return False
        try:   # port 8000 is a common default: make sure it's oMLX answering
            return "engine_pool" in http.get_json(self.base_url + "/health", {}, 5)
        except Exception:
            return False

    def check_auth(self) -> None:
        self._call("GET", "/admin/api/models", timeout=15)

    def _version(self) -> Optional[str]:
        if platform.system() == "Darwin":
            try:
                with open(APP_PLIST, "rb") as f:
                    return plistlib.load(f).get("CFBundleShortVersionString")
            except (OSError, ValueError):
                pass
        try:
            return http.get_json(self.base_url + "/openapi.json", {}, 10).get("info", {}).get("version")
        except Exception:
            return None

    def info(self) -> dict:
        v = self._version()
        return {"id": self.id, "name": self.name, "version": v, "base_url": self.base_url,
                "runtimes": {"mlx": f"oMLX {v} (mlx-lm)" if v else "oMLX (mlx-lm)"}}

    def _models(self) -> List[dict]:
        data = self._call("GET", "/admin/api/models", timeout=60)
        return data.get("models", data) if isinstance(data, dict) else data

    def list_models(self) -> List[dict]:
        out = []
        for m in self._models():
            if m.get("model_type") in LLM_TYPES and not m.get("is_helper"):
                out.append(self._normalize(m))
        return out

    @staticmethod
    def _config(path: str) -> dict:
        try:
            return json.loads((Path(path) / "config.json").read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return {}

    @staticmethod
    def _tool_use(path: str) -> Optional[bool]:
        """Trained for tool use when the chat template handles a `tools` list (same test LM Studio applies)."""
        texts = []
        for name in ("chat_template.jinja", "tokenizer_config.json", "chat_template.json"):
            try:
                texts.append((Path(path) / name).read_text(encoding="utf-8"))
            except (OSError, TypeError):
                pass
        return any("tools" in t for t in texts) if texts else None

    def _normalize(self, m: dict) -> dict:
        mid = m.get("id")
        path = m.get("model_path") or ""
        repo = m.get("source_repo_id") or ""
        cfg = self._config(path)
        text_cfg = cfg.get("text_config") or cfg
        experts = text_cfg.get("num_local_experts") or text_cfg.get("num_experts") or text_cfg.get("n_routed_experts")
        total, active = parse_params(mid, repo, m.get("display_name") or "")
        qname = quant_from_name(mid, repo)
        qcfg = cfg.get("quantization") or cfg.get("quantization_config") or {}
        bits = qcfg.get("bits") if isinstance(qcfg, dict) else None
        # reasoning_levels is what oMLX's own settings UI offers: ["off", "on"] (a template switch such as
        # enable_thinking) or ["low", "medium", "high"] (gpt-oss: effort levels, can't be switched off)
        levels = list(m.get("reasoning_levels") or m.get("reasoning_efforts") or [])
        thinking = m.get("thinking_default")
        if "high" in levels:
            reasoning = {"allowed_options": levels, "default": "low", "levels": True}
        elif "on" in levels or thinking is not None:
            reasoning = {"allowed_options": ["off", "on"], "default": "on" if thinking else "off"}
        else:
            reasoning = None
        size = m.get("actual_size") or m.get("estimated_size") or None
        fp = hashlib.sha1(f"{mid}|{path}|{size}".encode()).hexdigest()[:12]
        return {
            "model_uid": f"omlx:{mid}", "engine": "omlx", "key": mid, "variant": None,
            "display_name": m.get("display_name") or mid,
            "publisher": repo.split("/")[0] if "/" in repo else (Path(path).parent.name or None),
            "architecture": m.get("config_model_type") or cfg.get("model_type"),
            "params_string": None, "params_total_b": total, "params_active_b": active,
            "is_moe": bool(experts) or active is not None,
            "params_active_source": "name" if active is not None else None,
            "moe_experts": experts,
            "moe_experts_per_token": text_cfg.get("num_experts_per_tok") or text_cfg.get("experts_per_token"),
            "format": (m.get("model_format") or "mlx").lower(),
            "quantization": {"name": qname, "bits": bits or bits_from_quant(qname)},
            "qat": has_qat(mid, repo),
            "size_bytes": size, "max_context_length": m.get("model_context_length"),
            "capabilities": {"vision": m.get("model_type") == "vlm", "tool_use": self._tool_use(path),
                             "reasoning": reasoning},
            "description": None, "fingerprint": fp, "model_path": path, "source": self._source(m),
            "_load_key": mid,
        }

    @staticmethod
    def _source(m: dict) -> Optional[dict]:
        """Downloaded repos sit in <models>/<user>/<repo> (two levels), as oMLX's downloader lays them out."""
        repo = m.get("source_repo_id")
        if not repo:
            parts = Path(m.get("model_path") or "").parts
            name = (m.get("display_name") or "")
            repo = name if name.count("/") == 1 and parts and name.endswith(parts[-1]) else None
        if not repo:
            return None
        path = m.get("model_path") or ""
        return hf_source(repo, Path(path).name if path.lower().endswith(".gguf") else None)

    def loaded(self) -> List[dict]:
        out = []
        for m in self._models():
            if m.get("loaded") and m.get("model_type") not in ("markitdown",):
                s = m.get("settings") or {}
                out.append({"engine": self.id, "model_key": m.get("id"), "instance_id": m.get("id"),
                            "type": m.get("model_type"),
                            "config": {"context_length": s.get("max_context_window"), "pinned": m.get("pinned")}})
        return out

    # --- lifecycle -------------------------------------------------------
    def _settings(self, mid: str) -> dict:
        for m in self._models():
            if m.get("id") == mid:
                return m.get("settings") or {}
        return {}

    def _set_context(self, mid: str, ctx) -> None:
        self._call("PUT", f"/admin/api/models/{quote(mid, safe='')}/settings", {"max_context_window": ctx})

    def load(self, model: dict, profile: dict) -> dict:
        mid = model.get("_load_key") or model["key"]
        ctx = int(profile["context_length"])
        before = self._settings(mid).get("max_context_window")
        if before != ctx:
            self._ctx_restore.setdefault(mid, before)
            self._set_context(mid, ctx)
        t0 = time.perf_counter()
        self._call("POST", f"/v1/models/{quote(mid, safe='')}/load", timeout=1800)
        client = time.perf_counter() - t0
        return {"instance_id": mid, "load_time_s": client, "client_load_time_s": client,
                "load_config": {"context_length": ctx, **{k: v for k, v in self._settings(mid).items()
                                                          if v not in (None, "", [], {}, False)}}}

    def unload(self, instance: dict) -> None:
        mid = instance["instance_id"]
        self._call("POST", f"/v1/models/{quote(mid, safe='')}/unload", timeout=120)
        if mid in self._ctx_restore:
            try:
                self._set_context(mid, self._ctx_restore.pop(mid))
            except Exception:
                pass

    def restore(self, instance: dict) -> None:
        self._call("POST", f"/v1/models/{quote(instance['instance_id'], safe='')}/load", timeout=1800)

    def unload_hint(self, instance: dict) -> str:
        return f'oMLX: unload "{instance["model_key"]}" in the admin panel (http://127.0.0.1:8000/admin) or the menu bar app'

    # --- inference -------------------------------------------------------
    def resolve_reasoning(self, model: dict, mode: str):
        r = (model.get("capabilities") or {}).get("reasoning")
        if not r:
            if mode == "off":
                return None
            raise ValueError("model has no thinking capability")
        if r.get("levels"):
            allowed = r.get("allowed_options") or []
            if mode == "off":
                return "low" if "low" in allowed else allowed[0]
            if "high" in allowed:
                return "high"
            raise ValueError("no high reasoning option")
        return "off" if mode == "off" else "on"

    def chat(self, instance_id, model, system_prompt, user_text, state, reasoning, max_tokens, profile,
             on_phase: Optional[Callable[[str], None]] = None, cancel: Optional[http.Cancel] = None) -> Turn:
        messages = list(state or [])
        if not messages and system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_text})
        payload = {"model": instance_id, "messages": messages, "stream": True,
                   "stream_options": {"include_usage": True}, "return_progress": True,
                   "temperature": profile["temperature"], "top_p": profile["top_p"], "top_k": profile["top_k"],
                   "min_p": profile.get("min_p", 0), "repetition_penalty": profile.get("repeat_penalty", 1),
                   "seed": profile.get("seed", 42), "max_tokens": int(max_tokens)}
        if reasoning in ("on", "off"):
            payload["enable_thinking"] = reasoning == "on"
            payload["chat_template_kwargs"] = {"enable_thinking": reasoning == "on"}
        elif reasoning:
            payload["reasoning_effort"] = reasoning
        t = Turn()
        t.t_send = time.perf_counter()
        if on_phase:
            on_phase("prefill")
        decoding = False
        try:
            for _, data in http.stream_sse(self.base_url + "/v1/chat/completions", payload, self._headers(),
                                           timeout=profile.get("request_timeout_s", 1800), cancel=cancel):
                if data.get("error"):
                    err = data["error"]
                    raise RuntimeError(f"oMLX error: {err.get('message') if isinstance(err, dict) else err}")
                for ch in data.get("choices") or []:
                    d = ch.get("delta") or {}
                    if d.get("reasoning_content"):
                        t.mark_token(False)
                        t.reasoning_text += d["reasoning_content"]
                    if d.get("content"):
                        t.mark_token(True)
                        t.text += d["content"]
                    if ch.get("finish_reason"):
                        t.finish_reason = ch["finish_reason"]
                if not decoding and t.ttft_s is not None and on_phase:
                    on_phase("decode")
                    decoding = True
                u = data.get("usage")
                if u:
                    t.prompt_tokens = u.get("prompt_tokens")
                    cached = (u.get("prompt_tokens_details") or {}).get("cached_tokens")
                    if t.prompt_tokens is not None and cached is not None:
                        t.new_prompt_tokens = max(0, t.prompt_tokens - cached)
                    t.completion_tokens = u.get("completion_tokens")
                    t.reasoning_tokens = (u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0
                    t.server_ttft_s = u.get("time_to_first_token")
                    t.server_prefill_tps = u.get("prompt_tokens_per_second")
                    t.server_decode_tps = u.get("generation_tokens_per_second")
                    if u.get("model_load_duration"):
                        t.load_time_s = u["model_load_duration"]
        except http.HTTPError as e:
            if e.status in (401, 403):
                raise AuthRequired(e.body) from None
            raise
        t.total_s = time.perf_counter() - t.t_send
        if t.reasoning_text and not t.reasoning_tokens:
            # not reported: estimate the reasoning share by characters, as for Ollama
            total_chars = len(t.reasoning_text) + len(t.text)
            if t.completion_tokens and total_chars:
                t.reasoning_tokens = round(t.completion_tokens * len(t.reasoning_text) / total_chars)
        t.state = messages + [{"role": "assistant", "content": t.text}]
        return t

    # --- memory ----------------------------------------------------------
    def process_match(self, cmdline: str) -> bool:
        return "omlx" in self.executable(cmdline)   # the server renames its process "omlx-server"
