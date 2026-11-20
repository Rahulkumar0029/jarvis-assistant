"""Jarvis entry point.

  python main.py          voice mode (say "Jarvis ..." to wake it)
  python main.py --text   type commands instead of speaking (good for testing)
  python main.py --mic    list microphones and exit
"""

import argparse
import logging
import sys

from jarvis.commands import handle
from jarvis.config import ROOT, cfg
from jarvis.speech import listen, speak

logging.basicConfig(
    filename=ROOT / "jarvis.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def greeting() -> str:
    from datetime import datetime

    hour = datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    return f"Good {part} {cfg.user_name}"


def run_text() -> None:
    speak(f"{greeting()}. Text mode is on. Type 'exit jarvis' to quit.")
    while True:
        try:
            command = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if command and handle(command) == "exit":
            break


def run_voice() -> None:
    speak(f"{greeting()}. Jarvis is online. Say {cfg.wake_words[0]} to wake me.")
    while True:
        heard = listen(timeout=5, phrase_time_limit=8)
        if not heard:
            continue
        wake = next((w for w in cfg.wake_words if w in heard), None)
        if not wake:
            continue

        command = heard.split(wake, 1)[1].strip(" ,.")
        if not command:  # they only said the wake word
            speak("Yes?")
            command = listen(timeout=6, phrase_time_limit=10)
            if not command:
                speak("I didn't catch that.")
                continue
        if handle(command) == "exit":
            break


def list_mics() -> None:
    import speech_recognition as sr

    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{i}: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis voice assistant")
    parser.add_argument("--text", action="store_true", help="type instead of speak")
    parser.add_argument("--mic", action="store_true", help="list microphones")
    args = parser.parse_args()

    try:
        if args.mic:
            list_mics()
        elif args.text:
            run_text()
        else:
            run_voice()
    except KeyboardInterrupt:
        print("\nBye.")
    except RuntimeError as exc:
        print(f"\nERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
