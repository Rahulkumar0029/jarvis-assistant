"""Command router: turns what you said into an action.

Every handler takes the lowercase command text and returns:
  None    -> "not mine", the next handler gets a try
  True    -> handled
  "exit"  -> stop Jarvis
"""

import datetime
import logging
import os
import random
import re
import subprocess
import webbrowser
from urllib.parse import quote_plus

from .config import cfg
from .speech import listen, speak

log = logging.getLogger("jarvis")

SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
    "stack overflow": "https://stackoverflow.com",
    "stackoverflow": "https://stackoverflow.com",
    "netflix": "https://www.netflix.com",
    "maps": "https://maps.google.com",
    "drive": "https://drive.google.com",
}

# name -> command per platform. Add your own apps here!
APPS = {
    "notepad": {"win": "notepad", "mac": 'open -a "TextEdit"', "linux": "gedit"},
    "calculator": {"win": "calc", "mac": 'open -a "Calculator"', "linux": "gnome-calculator"},
    "paint": {"win": "mspaint", "mac": 'open -a "Preview"', "linux": "pinta"},
    "command prompt": {"win": "start cmd", "mac": 'open -a "Terminal"', "linux": "gnome-terminal"},
    "terminal": {"win": "start cmd", "mac": 'open -a "Terminal"', "linux": "gnome-terminal"},
    "file explorer": {"win": "explorer", "mac": "open .", "linux": "xdg-open ."},
    "explorer": {"win": "explorer", "mac": "open .", "linux": "xdg-open ."},
    "chrome": {"win": "start chrome", "mac": 'open -a "Google Chrome"', "linux": "google-chrome"},
    "edge": {"win": "start msedge", "mac": 'open -a "Microsoft Edge"', "linux": "microsoft-edge"},
    "vs code": {"win": "code", "mac": "code", "linux": "code"},
    "visual studio code": {"win": "code", "mac": "code", "linux": "code"},
    "vscode": {"win": "code", "mac": "code", "linux": "code"},
    "spotify": {"win": "start spotify:", "mac": 'open -a "Spotify"', "linux": "spotify"},
    "word": {"win": "start winword", "mac": 'open -a "Microsoft Word"', "linux": "libreoffice --writer"},
    "excel": {"win": "start excel", "mac": 'open -a "Microsoft Excel"', "linux": "libreoffice --calc"},
    "powerpoint": {"win": "start powerpnt", "mac": 'open -a "Microsoft PowerPoint"', "linux": "libreoffice --impress"},
    "task manager": {"win": "taskmgr", "mac": 'open -a "Activity Monitor"', "linux": "gnome-system-monitor"},
    "settings": {"win": "start ms-settings:", "mac": 'open -a "System Settings"', "linux": "gnome-control-center"},
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "There are only 10 kinds of people: those who understand binary and those who don't.",
    "A SQL query walks into a bar, walks up to two tables and asks: can I join you?",
    "I would tell you a UDP joke, but you might not get it.",
    "Why did the developer go broke? Because he used up all his cache.",
]



# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _run(cmd: str) -> None:
    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _confirm(question: str) -> bool:
    speak(question)
    try:
        answer = listen(timeout=5, phrase_time_limit=4)
    except Exception:
        answer = ""
    if not answer:
        try:
            answer = input("Confirm (yes/no): ").strip().lower()
        except Exception:
            answer = ""
    return any(w in answer for w in ("yes", "yeah", "confirm", "do it", "sure"))


# --------------------------------------------------------------------------- #
# handlers
# --------------------------------------------------------------------------- #
def h_exit(text):
    if any(p in text for p in ("goodbye", "good bye", "exit jarvis", "quit jarvis",
                               "shut down jarvis", "stop listening", "go to sleep")):
        speak(f"Goodbye {cfg.user_name}. Shutting down.")
        return "exit"


def h_help(text):
    if "what can you do" in text or text in ("help", "help me"):
        speak(
            "I can open apps and websites, search Google, play YouTube, tell the time, "
            "weather and jokes, take notes, control volume, take screenshots, check battery "
            "and CPU, lock or shut down the laptop, and answer questions."
        )
        return True


def h_time(text):
    if re.search(r"\b(what('s| is)? the time|what time|current time|time now)\b", text):
        speak(datetime.datetime.now().strftime("It is %I:%M %p."))
        return True
    if re.search(r"\b(today'?s date|what('s| is)? the date|what day|which day|current date)\b", text):
        speak(datetime.datetime.now().strftime("Today is %A, %d %B %Y."))
        return True


def h_open(text):
    m = re.match(r"^(?:open|launch|start|run)\s+(.+)$", text)
    if not m:
        return None
    name = re.sub(r"^(the|my)\s+", "", m.group(1).strip())
    name = re.sub(r"\s+(app|website|site)$", "", name)

    if name in SITES:
        speak(f"Opening {name}.")
        webbrowser.open(SITES[name])
        return True
    if name in APPS:
        speak(f"Opening {name}.")
        _run(APPS[name][cfg.platform])
        return True
    # Looks like a domain, e.g. "open example.com"
    if re.fullmatch(r"[\w-]+(\.[\w-]+)+", name.replace(" dot ", ".")):
        speak(f"Opening {name}.")
        webbrowser.open("https://" + name.replace(" dot ", "."))
        return True
    speak(f"I don't know how to open {name} yet. You can add it in commands dot py.")
    return True


def h_search(text):
    m = re.match(r"^(?:search|google|look up)(?:\s+for)?\s+(.+)$", text)
    if m:
        q = m.group(1)
        speak(f"Searching Google for {q}.")
        webbrowser.open("https://www.google.com/search?q=" + quote_plus(q))
        return True


def h_play(text):
    m = re.match(r"^play\s+(.+?)(?:\s+on youtube)?$", text)
    if m:
        q = m.group(1)
        speak(f"Playing {q} on YouTube.")
        webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(q))
        return True


def h_weather(text):
    if "weather" not in text and "temperature" not in text:
        return None
    import requests

    m = re.search(r"\bin\s+([a-z\s]+)$", text)
    city = (m.group(1).strip() if m else cfg.default_city)
    try:
        r = requests.get(f"https://wttr.in/{quote_plus(city)}?format=%C,+%t,+humidity+%h", timeout=8)
        r.raise_for_status()
        speak(f"Weather in {city}: {r.text.strip()}.")
    except Exception:
        speak("I couldn't fetch the weather. Check your internet connection.")
    return True


def h_notes(text):
    m = re.match(r"^(?:take a note|note down|make a note|remember(?: that)?)\s+(.+)$", text)
    if m:
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(cfg.notes_file, "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {m.group(1)}\n")
        speak("Noted.")
        return True
    if "read my notes" in text or "read notes" in text:
        if cfg.notes_file.exists():
            lines = [l for l in cfg.notes_file.read_text(encoding="utf-8").strip().splitlines() if l.strip()]
            if not lines:
                speak("You have no notes yet.")
                return True
            lines = lines[-5:]
            speak("Your latest notes. " + " ... ".join(l.split("] ", 1)[-1] for l in lines))
        else:
            speak("You have no notes yet.")
        return True


def h_joke(text):
    if "joke" in text:
        speak(random.choice(JOKES))
        return True


def h_system(text):
    import psutil

    if "battery" in text:
        b = psutil.sensors_battery()
        if b is None:
            speak("I can't read a battery on this machine.")
        else:
            plug = "and charging" if b.power_plugged else "and not charging"
            speak(f"Battery is at {int(b.percent)} percent {plug}.")
        return True
    if "cpu" in text or "ram" in text or "memory usage" in text or "system status" in text:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        speak(f"CPU is at {cpu:.0f} percent and RAM is at {ram:.0f} percent.")
        return True

    if "screenshot" in text:
        import pyautogui

        cfg.screenshots_dir.mkdir(exist_ok=True)
        path = cfg.screenshots_dir / datetime.datetime.now().strftime("shot_%Y%m%d_%H%M%S.png")
        pyautogui.screenshot(str(path))
        speak("Screenshot saved.")
        return True

    if "volume" in text or "mute" in text or "unmute" in text:
        import pyautogui

        if "mute" in text:
            pyautogui.press("volumemute")
            speak("Done.")
        elif any(w in text for w in ("up", "increase", "raise", "louder")):
            pyautogui.press("volumeup", presses=5)
            speak("Volume up.")
        elif any(w in text for w in ("down", "decrease", "lower", "quieter")):
            pyautogui.press("volumedown", presses=5)
            speak("Volume down.")
        else:
            return None
        return True

    if "lock" in text and ("laptop" in text or "computer" in text or "screen" in text or "pc" in text):
        speak("Locking.")
        if cfg.platform == "win":
            import ctypes

            ctypes.windll.user32.LockWorkStation()
        elif cfg.platform == "mac":
            _run("pmset displaysleepnow")
        else:
            _run("loginctl lock-session")
        return True

    if re.search(r"\b(shut ?down|power off|turn off)\b", text) and any(
        w in text for w in ("laptop", "computer", "pc", "system")
    ):
        if _confirm("Are you sure you want to shut down the laptop?"):
            speak("Shutting down in 5 seconds.")
            _run({"win": "shutdown /s /t 5", "mac": "osascript -e 'tell app \"System Events\" to shut down'",
                  "linux": "systemctl poweroff"}[cfg.platform])
        else:
            speak("Cancelled.")
        return True

    if "restart" in text and any(w in text for w in ("laptop", "computer", "pc", "system")):
        if _confirm("Are you sure you want to restart the laptop?"):
            speak("Restarting in 5 seconds.")
            _run({"win": "shutdown /r /t 5", "mac": "osascript -e 'tell app \"System Events\" to restart'",
                  "linux": "systemctl reboot"}[cfg.platform])
        else:
            speak("Cancelled.")
        return True


def h_wiki(text):
    m = re.match(r"^(?:who is|who was|what is|what are|tell me about)\s+(.+)$", text)
    if not m:
        return None
    topic = m.group(1).strip().rstrip("?")
    import requests

    try:
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(topic.title()),
            headers={"User-Agent": "JarvisAssistant/1.0"},
            timeout=8,
        )
        if r.status_code == 200 and r.json().get("extract"):
            summary = r.json()["extract"]
            speak(". ".join(summary.split(". ")[:2]).strip())
            return True
    except Exception:
        pass
    return None  # let the AI fallback try


HANDLERS = [h_exit, h_help, h_time, h_open, h_search, h_play, h_weather,
            h_notes, h_joke, h_system, h_wiki]


# --------------------------------------------------------------------------- #
# AI brain (provider-switchable)
# --------------------------------------------------------------------------- #
def ai_fallback(text: str):
    from .ai import ask

    answer = ask(text)
    speak(answer)
    return True


def handle(text: str):
    """Run one command. Returns 'exit' if Jarvis should stop."""
    text = re.sub(r"\s+", " ", text.lower().strip())
    log.info("command: %s", text)
    for handler in HANDLERS:
        try:
            result = handler(text)
        except Exception as exc:
            log.exception("handler %s crashed", handler.__name__)
            speak("Something went wrong running that command.")
            return None
        if result is not None:
            return result
    return ai_fallback(text)
