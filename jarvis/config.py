"""Settings, loaded from environment variables / the .env file."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _list(name: str, default: str) -> list[str]:
    return [w.strip().lower() for w in os.getenv(name, default).split(",") if w.strip()]


class Config:
    def __init__(self):
        self.load()

    def load(self):
        try:
            from dotenv import load_dotenv

            load_dotenv(ROOT / ".env", override=True)
        except ImportError:
            pass

        self.user_name = os.getenv("USER_NAME", "Sir")
        self.wake_words = _list("WAKE_WORDS", "jarvis,jarvish,jarvas")
        self.default_city = os.getenv("DEFAULT_CITY", "Delhi")

        # AI brain configuration
        self.ai_provider = os.getenv("AI_PROVIDER", "gemini").strip().lower()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434").strip().rstrip("/")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2").strip()
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5").strip()

        self.voice_rate = int(os.getenv("VOICE_RATE", "185"))
        self.voice_volume = float(os.getenv("VOICE_VOLUME", "1.0"))
        self.notes_file = ROOT / "notes.txt"
        self.screenshots_dir = ROOT / "screenshots"
        self.platform = (
            "win" if sys.platform.startswith("win")
            else "mac" if sys.platform == "darwin"
            else "linux"
        )


cfg = Config()


def update_env(updates: dict[str, str]) -> None:
    """Update or append keys in the .env file without removing existing settings."""
    env_path = ROOT / ".env"
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            k, _ = stripped.split("=", 1)
            k = k.strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}")
                updated_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in updates.items():
        if k not in updated_keys:
            new_lines.append(f"{k}={v}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    cfg.load()
