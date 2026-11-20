"""Settings, loaded from environment variables / the .env file."""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # python-dotenv is optional at import time
    pass

ROOT = Path(__file__).resolve().parent.parent


def _list(name: str, default: str) -> list[str]:
    return [w.strip().lower() for w in os.getenv(name, default).split(",") if w.strip()]


class Config:
    user_name = os.getenv("USER_NAME", "Sir")
    wake_words = _list("WAKE_WORDS", "jarvis,jarvish,jarvas")
    default_city = os.getenv("DEFAULT_CITY", "Delhi")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    voice_rate = int(os.getenv("VOICE_RATE", "185"))
    voice_volume = float(os.getenv("VOICE_VOLUME", "1.0"))
    notes_file = ROOT / "notes.txt"
    screenshots_dir = ROOT / "screenshots"
    platform = (
        "win" if sys.platform.startswith("win")
        else "mac" if sys.platform == "darwin"
        else "linux"
    )


cfg = Config()
