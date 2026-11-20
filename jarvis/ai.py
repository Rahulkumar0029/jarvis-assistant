"""Provider-switchable AI brain for Jarvis.

Supported providers:
  - gemini   (Google Gemini generateContent REST API)
  - groq     (Groq OpenAI-compatible chat completions)
  - ollama   (Local Ollama /api/chat)
  - anthropic (Optional legacy Anthropic SDK)
  - none     (Disabled)
"""

import logging
import re
import requests

from .config import cfg

log = logging.getLogger("jarvis")

SYSTEM_PROMPT = (
    "You are Jarvis, a voice assistant on the user's laptop. "
    "Reply in one to three short plain-text sentences for speech. "
    "No markdown, no lists, no emojis."
)

_history: list[dict[str, str]] = []


def clean_markdown(text: str) -> str:
    """Strip markdown formatting (*, #, `, _, ~) to ensure clean speech output."""
    if not text:
        return ""
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[\*#`_~]", "", text)
    text = re.sub(r"^\s*[-+*]\s+", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def _ask_gemini(text: str, history: list[dict[str, str]]) -> str:
    if not cfg.gemini_key:
        return "Add a Gemini API key to the dot env file, or run python main.py --setup-ai."

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{cfg.gemini_model}:generateContent"
    )
    headers = {
        "x-goog-api-key": cfg.gemini_key,
        "Content-Type": "application/json",
    }

    contents = []
    for msg in history:
        role = "model" if msg.get("role") == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
    contents.append({"role": "user", "parts": [{"text": text}]})

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": contents,
        "generationConfig": {
            "maxOutputTokens": 300,
            "temperature": 0.7,
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    if resp.status_code in (401, 403):
        log.warning("Gemini authentication failed (HTTP %d)", resp.status_code)
        return "Your Gemini API key is invalid. Please check your key in the dot env file."
    if resp.status_code == 429:
        log.warning("Gemini rate limit reached (HTTP 429)")
        return "I'm rate limited, try again in a minute."
    if resp.status_code >= 400:
        log.warning("Gemini returned HTTP %d: %s", resp.status_code, resp.text[:200])
        return "Something went wrong contacting my AI brain."

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return "I have no answer for that."
    parts = candidates[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in parts).strip()


def _ask_groq(text: str, history: list[dict[str, str]]) -> str:
    if not cfg.groq_key:
        return "Add a Groq API key to the dot env file, or run python main.py --setup-ai."

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {cfg.groq_key}",
        "Content-Type": "application/json",
    }

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": text})

    payload = {
        "model": cfg.groq_model,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.7,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    if resp.status_code in (401, 403):
        log.warning("Groq authentication failed (HTTP %d)", resp.status_code)
        return "Your Groq API key is invalid. Please check your key in the dot env file."
    if resp.status_code == 429:
        log.warning("Groq rate limit reached (HTTP 429)")
        return "I'm rate limited, try again in a minute."
    if resp.status_code >= 400:
        log.warning("Groq returned HTTP %d: %s", resp.status_code, resp.text[:200])
        return "Something went wrong contacting my AI brain."

    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        return "I have no answer for that."
    return choices[0].get("message", {}).get("content", "").strip()


def _ask_ollama(text: str, history: list[dict[str, str]]) -> str:
    url = f"{cfg.ollama_url}/api/chat"
    headers = {"Content-Type": "application/json"}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": text})

    payload = {
        "model": cfg.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {
            "num_predict": 300,
            "temperature": 0.7,
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    if resp.status_code == 429:
        log.warning("Ollama rate limit reached (HTTP 429)")
        return "I'm rate limited, try again in a minute."
    if resp.status_code >= 400:
        log.warning("Ollama returned HTTP %d: %s", resp.status_code, resp.text[:200])
        return "Something went wrong contacting my AI brain."

    data = resp.json()
    return data.get("message", {}).get("content", "").strip()


def _ask_anthropic(text: str, history: list[dict[str, str]]) -> str:
    if not cfg.anthropic_key:
        return "Add an Anthropic API key to the dot env file, or run python main.py --setup-ai."

    try:
        import anthropic  # type: ignore

        client = anthropic.Anthropic(api_key=cfg.anthropic_key)
        messages = []
        for msg in history:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": text})

        resp = client.messages.create(
            model=cfg.anthropic_model,
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        return "".join(b.text for b in resp.content if b.type == "text").strip()
    except ImportError:
        log.warning("Anthropic library not installed")
        return "The Anthropic package is not installed. Run pip install anthropic or switch to Gemini or Groq."
    except Exception as exc:
        status_code = getattr(exc, "status_code", None)
        log.warning("Anthropic error: %s", exc)
        if status_code in (401, 403):
            return "Your Anthropic API key is invalid. Please check your key in the dot env file."
        if status_code == 429:
            return "I'm rate limited, try again in a minute."
        return "I couldn't reach my AI brain. Check your API key and internet."


def ask(text: str, history: list[dict[str, str]] | None = None) -> str:
    """Send text to the configured AI provider, maintaining the last 8 messages."""
    global _history
    provider = cfg.ai_provider

    if provider == "none":
        return "AI responses are currently disabled in your dot env file. Run python main.py --setup-ai to enable one."

    active_history = _history if history is None else history
    history_slice = active_history[-8:]

    try:
        if provider == "gemini":
            reply = _ask_gemini(text, history_slice)
        elif provider == "groq":
            reply = _ask_groq(text, history_slice)
        elif provider == "ollama":
            reply = _ask_ollama(text, history_slice)
        elif provider == "anthropic":
            reply = _ask_anthropic(text, history_slice)
        else:
            log.warning("Unknown AI_PROVIDER: %s", provider)
            return (
                f"Unknown AI provider '{provider}'. "
                "Supported providers are gemini, groq, ollama, anthropic, or none."
            )
    except requests.exceptions.Timeout:
        log.warning("AI request timed out for provider: %s", provider)
        return "My AI brain timed out. Check your internet connection."
    except requests.exceptions.ConnectionError:
        log.warning("AI connection refused/failed for provider: %s", provider)
        if provider == "ollama":
            return (
                "I couldn't connect to Ollama. "
                "Make sure Ollama is installed and running on your laptop."
            )
        return "I couldn't reach my AI brain. Check your internet connection."
    except requests.exceptions.RequestException as exc:
        log.warning("AI request exception for provider %s: %s", provider, exc)
        return "Something went wrong contacting my AI brain."
    except Exception as exc:
        log.exception("Unexpected error in AI provider %s: %s", provider, exc)
        return "Something went wrong contacting my AI brain."

    clean_reply = clean_markdown(reply)
    if not clean_reply:
        return "I have no answer for that."

    # Update conversation history if reply was not an error/prompt
    if active_history is _history and not clean_reply.startswith(("Add a", "Your ", "I couldn't", "My AI", "Something went", "Unknown ")):
        _history.append({"role": "user", "content": text})
        _history.append({"role": "assistant", "content": clean_reply})

    return clean_reply
