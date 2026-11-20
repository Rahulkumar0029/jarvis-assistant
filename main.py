"""Jarvis entry point.

  python main.py             voice mode (say "Jarvis ..." to wake it)
  python main.py --text      type commands instead of speaking (good for testing)
  python main.py --mic       list microphones and exit
  python main.py --setup-ai  configure free AI brain (Gemini, Groq, Ollama)
  python main.py --test-ai   test AI connection and latency
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
            if "goodbye" in heard:
                handle("goodbye")
                break
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

    try:
        names = sr.Microphone.list_microphone_names()
    except Exception as exc:
        print(f"Error accessing microphones: {exc}")
        print("Please check: Settings > Privacy & security > Microphone")
        return

    if not names:
        print("No microphones detected!")
        print("Please enable your microphone in: Settings > Privacy & security > Microphone")
        return

    for i, name in enumerate(names):
        print(f"{i}: {name}")


def setup_ai() -> None:
    import getpass
    import shutil
    import subprocess
    import webbrowser
    from jarvis.config import cfg, update_env

    print("\n=== Jarvis AI Brain Setup ===")
    print("Choose an AI provider:")
    print("  1. Google Gemini (Free tier, fast - Recommended)")
    print("  2. Groq (Free tier, ultra-fast Llama)")
    print("  3. Ollama (100% Free, runs locally on your laptop)")
    print("  4. None (Disable open-ended AI questions)")

    choice = input("\nEnter choice (1-4) [1]: ").strip()
    if not choice:
        choice = "1"

    if choice == "1":
        print("\nOpening https://aistudio.google.com/apikey in your browser to get a free Gemini API key...")
        webbrowser.open("https://aistudio.google.com/apikey")
        key = getpass.getpass("Paste your Gemini API key (input hidden): ").strip()
        if not key:
            print("No key entered. Gemini configuration cancelled.")
            return
        update_env({"AI_PROVIDER": "gemini", "GEMINI_API_KEY": key})
        print("✓ Gemini configured successfully in .env!")

    elif choice == "2":
        print("\nOpening https://console.groq.com/keys in your browser to get a free Groq API key...")
        webbrowser.open("https://console.groq.com/keys")
        key = getpass.getpass("Paste your Groq API key (input hidden): ").strip()
        if not key:
            print("No key entered. Groq configuration cancelled.")
            return
        update_env({"AI_PROVIDER": "groq", "GROQ_API_KEY": key})
        print("✓ Groq configured successfully in .env!")

    elif choice == "3":
        update_env({"AI_PROVIDER": "ollama"})
        ollama_bin = shutil.which("ollama")
        if ollama_bin:
            print(f"\nOllama detected! Pulling model '{cfg.ollama_model}'...")
            try:
                subprocess.run(["ollama", "pull", cfg.ollama_model], check=True)
                print(f"✓ Model '{cfg.ollama_model}' pulled and ready.")
            except Exception as exc:
                print(f"Note: Could not pull model automatically: {exc}")
                print(f"Run manually: ollama pull {cfg.ollama_model}")
        else:
            print("\nOllama is not installed on this laptop.")
            print("Opening https://ollama.com/download in your browser...")
            webbrowser.open("https://ollama.com/download")
            print("Please install Ollama, start it, and run: ollama pull " + cfg.ollama_model)
        print("✓ Ollama set as AI provider in .env!")

    elif choice == "4":
        update_env({"AI_PROVIDER": "none"})
        print("✓ AI responses disabled in .env (built-in commands remain active).")
    else:
        print("Invalid selection. Setup cancelled.")


def test_ai() -> None:
    import time
    from jarvis.ai import ask
    from jarvis.config import cfg

    provider = cfg.ai_provider
    print(f"\n=== Testing AI Brain (Provider: {provider}) ===")

    if provider == "gemini" and not cfg.gemini_key:
        print("GEMINI_API_KEY is not set in .env.")
        print("Run 'python main.py --setup-ai' to configure it.")
        return
    elif provider == "groq" and not cfg.groq_key:
        print("GROQ_API_KEY is not set in .env.")
        print("Run 'python main.py --setup-ai' to configure it.")
        return
    elif provider == "anthropic" and not cfg.anthropic_key:
        print("ANTHROPIC_API_KEY is not set in .env.")
        print("Run 'python main.py --setup-ai' to configure it.")
        return
    elif provider == "none":
        print("AI_PROVIDER is set to 'none' in .env.")
        print("Run 'python main.py --setup-ai' to choose a provider.")
        return

    test_prompt = "say hello in five words"
    print(f"Sending prompt: \"{test_prompt}\"...")
    start_time = time.time()
    result = ask(test_prompt)
    latency = time.time() - start_time

    print(f"Result:  {result}")
    print(f"Latency: {latency:.2f}s")


def main() -> int:
    parser = argparse.ArgumentParser(description="Jarvis voice assistant")
    parser.add_argument("--text", action="store_true", help="type instead of speak")
    parser.add_argument("--mic", action="store_true", help="list microphones")
    parser.add_argument("--setup-ai", action="store_true", help="configure AI provider interactively")
    parser.add_argument("--test-ai", action="store_true", help="test configured AI brain and show latency")
    args = parser.parse_args()

    try:
        if args.mic:
            list_mics()
        elif args.setup_ai:
            setup_ai()
        elif args.test_ai:
            test_ai()
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
