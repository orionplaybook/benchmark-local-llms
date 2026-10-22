"""Paths, profile, and secrets (API keys) handling."""
from __future__ import annotations

import getpass
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
LOG_DIR = DATA_DIR / "logs"
DB_PATH = DATA_DIR / "results.json"
OVERRIDES_PATH = DATA_DIR / "overrides.json"
CACHE_DIR = DATA_DIR / "cache"
SITE_DIR = DATA_DIR / "site"          # local, no-server copy of the dashboard (`bench dashboard`)
BENCH_DIR = ROOT / "benchmarks"
DASHBOARD_DIR = ROOT / "dashboard"
PROFILE_PATH = ROOT / "config" / "profile.json"
SECRETS_PATH = ROOT / "secrets.local.json"

PLACEHOLDER_PREFIX = "PASTE_"

DEFAULT_SECRETS = {
    "lmstudio": {"base_url": "http://localhost:1234", "api_key": ""},
    "ollama": {"base_url": "http://localhost:11434", "api_key": ""},
    "huggingface": {"token": ""},
    "artificial_analysis": {"api_key": ""},
    "brave_search": {"api_key": ""},
    "searxng": {"base_url": ""},
}


def load_profile() -> dict:
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)
    profile["hash"] = profile_hash(profile)
    return profile


# Settings that change how a run is carried out, not what is measured: left out of the hash so that changing
# them never makes existing results look outdated.
OPERATIONAL_KEYS = ("hash", "description", "max_test_restarts", "swap_warning_gb", "cleanup_wait_s")


def profile_hash(profile: dict) -> str:
    clean = {k: v for k, v in profile.items() if k not in OPERATIONAL_KEYS}
    blob = json.dumps(clean, sort_keys=True).encode()
    return hashlib.sha1(blob).hexdigest()[:8]


def _clean(value):
    if isinstance(value, str) and value.startswith(PLACEHOLDER_PREFIX):
        return ""
    return value


class Secrets:
    """Reads/writes secrets.local.json (git-ignored). Placeholders count as empty."""

    def __init__(self, path: Path = SECRETS_PATH):
        self.path = path
        self.exists = path.exists()
        data = {}
        if self.exists:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (OSError, ValueError) as e:
                print(f"! Could not read {path.name}: {e}", file=sys.stderr)
        merged = json.loads(json.dumps(DEFAULT_SECRETS))
        for section, values in data.items():
            if isinstance(values, dict):
                merged.setdefault(section, {}).update(values)
        self.data = merged

    def get(self, section: str, key: str, default: str = "") -> str:
        env = os.environ.get(f"BENCH_{section.upper()}_{key.upper()}")
        if env:
            return env
        return _clean(self.data.get(section, {}).get(key, default)) or default

    def set(self, section: str, key: str, value: str) -> None:
        self.data.setdefault(section, {})[key] = value

    def save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)
            f.write("\n")
        os.replace(tmp, self.path)
        try:
            os.chmod(self.path, 0o600)
        except OSError:
            pass
        self.exists = True


def prompt_secret(label: str) -> str:
    """Hidden-input prompt. Returns '' when not interactive."""
    if not sys.stdin.isatty():
        return ""
    try:
        return getpass.getpass(f"{label} (input hidden, Enter to skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return ""


def ensure_dirs() -> None:
    for d in (DATA_DIR, RAW_DIR, LOG_DIR, CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
