"""Engine adapter interface + shared helpers."""
from __future__ import annotations

import re
import time
from typing import Callable, List, Optional

REASONING_LEVELS = ["low", "medium", "high", "xhigh"]


class AuthRequired(Exception):
    """Engine answered 401/403: an API key is needed."""


class EngineUnavailable(Exception):
    pass


def parse_params(*texts: str):
    """Returns (total_b, active_b) parsed from strings like '26B', 'gemma-4-26b-a4b', '30B-A3B'."""
    total = active = None
    for t in texts:
        if not t:
            continue
        s = t.lower()
        if active is None:
            m = re.search(r"(?:^|[-_ ])a(\d+(?:\.\d+)?)b(?:$|[-_ ])", s)
            if m:
                active = float(m.group(1))
        if total is None:
            m = re.search(r"(\d+(?:\.\d+)?)\s*b(?:$|[-_ @])", s)
            if m:
                total = float(m.group(1))
    return total, active


def moe_active_estimate(total_b, layers, hidden, expert_ffn, experts, used, dense_layers=0) -> Optional[float]:
    """Active parameters of a mixture-of-experts model, estimated as the total minus the experts a token doesn't
    use (each expert: 3 weight matrices of hidden x expert_ffn). Rough (attention/shared parts are counted as
    always active): gpt-oss-20b gives 4.2B where its card says 3.6B."""
    try:
        moe_layers = int(layers) - int(dense_layers or 0)
        unused = moe_layers * (int(experts) - int(used)) * 3 * int(hidden) * int(expert_ffn) / 1e9
    except (TypeError, ValueError):
        return None
    if not total_b or int(experts) <= 1:
        return None
    active = float(total_b) - unused
    return round(active, 1) if 0 < active < float(total_b) else None


def bits_from_quant(name: Optional[str]) -> Optional[float]:
    if not name:
        return None
    s = name.lower()
    m = re.search(r"(\d+)\s*-?bit", s) or re.search(r"q(\d+)", s) or re.search(r"(?:fp|bf|f)(\d+)", s)
    return float(m.group(1)) if m else None


def has_qat(*texts: str) -> bool:
    return any(t and re.search(r"(?:^|[-_ /])qat(?:$|[-_ @])", t.lower()) for t in texts)


class Turn:
    """Result of one chat request (one user turn)."""

    def __init__(self):
        self.t_send = 0.0
        self.ttft_s = None            # first token of any kind (reasoning or visible)
        self.first_visible_s = None   # first visible (non-reasoning) token
        self.total_s = None
        self.prompt_tokens = None
        self.new_prompt_tokens = None  # tokens actually processed (excluding cache), if known
        self.completion_tokens = None
        self.reasoning_tokens = 0
        self.server_ttft_s = None
        self.server_decode_tps = None
        self.server_prefill_tps = None
        self.load_time_s = None
        self.finish_reason = None
        self.text = ""
        self.reasoning_text = ""
        self.state = None             # engine-specific conversation state after this turn
        self.prompt_processing_s = None

    def mark_token(self, visible: bool):
        now = time.perf_counter() - self.t_send
        if self.ttft_s is None:
            self.ttft_s = now
        if visible and self.first_visible_s is None:
            self.first_visible_s = now

    @property
    def decode_tps(self):
        if self.server_decode_tps:
            return self.server_decode_tps
        if self.completion_tokens and self.total_s and self.ttft_s is not None:
            dt = self.total_s - self.ttft_s
            if dt > 0 and self.completion_tokens > 1:
                return (self.completion_tokens - 1) / dt
        return None

    @property
    def prefill_tps(self):
        if self.server_prefill_tps:
            return self.server_prefill_tps
        n = self.new_prompt_tokens if self.new_prompt_tokens is not None else self.prompt_tokens
        t = self.server_ttft_s or self.ttft_s
        if n and t and t > 0:
            return n / t
        return None

    def to_dict(self) -> dict:
        return {
            "ttft_s": self.ttft_s, "first_visible_s": self.first_visible_s, "total_s": self.total_s,
            "prompt_tokens": self.prompt_tokens, "new_prompt_tokens": self.new_prompt_tokens,
            "completion_tokens": self.completion_tokens, "reasoning_tokens": self.reasoning_tokens,
            "server_ttft_s": self.server_ttft_s, "decode_tps": self.decode_tps,
            "prefill_tps": self.prefill_tps, "load_time_s": self.load_time_s,
            "finish_reason": self.finish_reason,
            "text_chars": len(self.text), "reasoning_chars": len(self.reasoning_text),
        }


class Engine:
    id = "base"
    name = "Base"
    # True when closing the connection of a streaming request makes the engine stop working on it (checked
    # by measuring GPU use right after a cancel). When False, the runner reloads the model after a cancel.
    stops_on_disconnect = False

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    # --- discovery -------------------------------------------------------
    def available(self) -> bool:
        raise NotImplementedError

    def info(self) -> dict:
        raise NotImplementedError

    def list_models(self) -> List[dict]:
        """Normalized model dicts (see docs/SCHEMA.md 'models'). LLMs only."""
        raise NotImplementedError

    def loaded(self) -> List[dict]:
        """[{engine, model_key, instance_id, type, config}] currently in memory."""
        raise NotImplementedError

    # --- lifecycle -------------------------------------------------------
    def load(self, model: dict, profile: dict) -> dict:
        """Returns {instance_id, load_time_s, client_load_time_s, load_config}."""
        raise NotImplementedError

    def unload(self, instance: dict) -> None:
        raise NotImplementedError

    def restore(self, instance: dict) -> None:
        """Reload a previously loaded instance with its previous config."""
        raise NotImplementedError

    def unload_hint(self, instance: dict) -> str:
        return ""

    # --- inference -------------------------------------------------------
    def resolve_reasoning(self, model: dict, mode: str) -> Optional[str]:
        """Map 'off'/'high' to the engine/model value. None = don't send. Raises ValueError if unsupported."""
        raise NotImplementedError

    def chat(self, instance_id: str, model: dict, system_prompt: str, user_text: str, state,
             reasoning: Optional[str], max_tokens: int, profile: dict,
             on_phase: Optional[Callable[[str], None]] = None, cancel=None) -> Turn:
        """cancel: an http.Cancel; when fired (from another thread) the request is abandoned and
        http.Cancelled is raised."""
        raise NotImplementedError

    # --- memory ----------------------------------------------------------
    @staticmethod
    def executable(cmdline: str) -> str:
        """Executable part of a command line (drops arguments), lower-cased."""
        return re.split(r"\s+-", cmdline, maxsplit=1)[0].strip().strip('"').lower()

    def process_match(self, cmdline: str) -> bool:
        return False

    def memory_from_api(self) -> Optional[int]:
        return None
