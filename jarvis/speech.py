"""Ears and mouth: speech-to-text (listen) and text-to-speech (speak)."""

import logging

from .config import cfg

log = logging.getLogger("jarvis")

_recognizer = None
_calibrated = False


def speak(text: str) -> None:
    """Say `text` out loud (and always print it)."""
    print(f"Jarvis: {text}")
    try:
        import pyttsx3

        # A fresh engine each time avoids the well-known pyttsx3 "stops talking
        # after the first sentence" bug on Windows.
        engine = pyttsx3.init()
        engine.setProperty("rate", cfg.voice_rate)
        engine.setProperty("volume", cfg.voice_volume)
        _prefer_male_voice(engine)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as exc:  # no voice available -> text-only still works
        log.warning("Text-to-speech failed: %s", exc)


def _prefer_male_voice(engine) -> None:
    """Pick a deeper voice if one is installed (Jarvis vibes)."""
    try:
        for voice in engine.getProperty("voices"):
            name = (voice.name or "").lower()
            if any(k in name for k in ("david", "mark", "male", "daniel", "alex")):
                engine.setProperty("voice", voice.id)
                return
    except Exception:
        pass


def listen(timeout: float = 5, phrase_time_limit: float = 8) -> str:
    """Listen on the microphone once. Returns lowercase text, or '' if nothing."""
    global _recognizer, _calibrated
    import speech_recognition as sr

    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.pause_threshold = 0.8

    try:
        with sr.Microphone() as source:
            if not _calibrated:
                print("(calibrating for background noise...)")
                _recognizer.adjust_for_ambient_noise(source, duration=1)
                _calibrated = True
            audio = _recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
    except sr.WaitTimeoutError:
        return ""
    except (OSError, IOError, AttributeError) as exc:
        raise RuntimeError(
            "No microphone found. Check that your mic is plugged in, enabled in "
            "Windows Settings > Privacy & security > Microphone, and not used by another app."
        ) from exc

    try:
        text = _recognizer.recognize_google(audio, language="en-IN").lower().strip()
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("(speech service unreachable - check your internet connection)")
        return ""
