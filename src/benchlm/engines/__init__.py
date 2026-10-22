"""Engine registry + key handling (prompts for API keys when an engine requires one)."""
from __future__ import annotations

import sys
from typing import List

from ..config import Secrets, prompt_secret
from .base import AuthRequired, Engine, EngineUnavailable
from .lmstudio import LMStudio
from .ollama import Ollama

ENGINE_CLASSES = {"lmstudio": LMStudio, "ollama": Ollama}


def connect(secrets: Secrets, only=None, interactive: bool = True, quiet: bool = False) -> List[Engine]:
    """Return engines that are running and authorized. Asks for keys when needed."""
    engines = []
    for eid, cls in ENGINE_CLASSES.items():
        if only and eid not in only:
            continue
        eng = cls(secrets.get(eid, "base_url", cls.__dict__.get("default_url", "")) or
                  {"lmstudio": "http://localhost:1234", "ollama": "http://localhost:11434"}[eid],
                  secrets.get(eid, "api_key"))
        if not eng.available():
            if not quiet:
                print(f"  - {eng.name}: not running at {eng.base_url} (skipped)")
            continue
        for attempt in range(3):
            try:
                eng.check_auth()
                engines.append(eng)
                if not quiet:
                    print(f"  ✓ {eng.name}: connected at {eng.base_url}")
                break
            except AuthRequired:
                what = "API token" if eid == "lmstudio" else "API key"
                if attempt == 0 and not quiet:
                    reason = "is missing" if not eng.api_key else "was rejected"
                    print(f"  ! {eng.name} requires an {what} and the one in secrets.local.json {reason}.")
                    if eid == "lmstudio":
                        print("    Create one in LM Studio → Developer → Server Settings → API tokens.")
                if not (interactive and sys.stdin.isatty()):
                    print(f"    Add it to secrets.local.json → \"{eid}\": {{\"api_key\": \"...\"}} and re-run.")
                    break
                key = prompt_secret(f"    {eng.name} {what}")
                if not key:
                    print(f"    Skipping {eng.name}.")
                    break
                eng.api_key = key
                try:
                    eng.check_auth()
                except AuthRequired:
                    print("    That key was rejected, try again.")
                    continue
                secrets.set(eid, "api_key", key)
                secrets.set(eid, "base_url", eng.base_url)
                secrets.save()
                print(f"    Saved to {secrets.path.name} (git-ignored).")
                engines.append(eng)
                print(f"  ✓ {eng.name}: connected at {eng.base_url}")
                break
            except Exception as e:  # network / unexpected
                print(f"  ! {eng.name}: error talking to {eng.base_url}: {e}")
                break
    return engines
