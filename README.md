# Jarvis - Voice Assistant for Your Laptop

Say **"Jarvis, open YouTube"** and your laptop obeys. One repo, one setup script, runs fully on your laptop.

## What it can do

| Say | Result |
|---|---|
| "Jarvis, open Chrome / VS Code / Notepad / Spotify" | Opens the app |
| "Jarvis, open GitHub / YouTube / Gmail" | Opens the website |
| "Jarvis, search for python tutorials" | Google search |
| "Jarvis, play arijit singh songs" | YouTube search |
| "Jarvis, what time is it" / "what's the date" | Time / date |
| "Jarvis, weather" / "weather in Jaipur" | Weather |
| "Jarvis, take a note buy charger" / "read my notes" | Notes in `notes.txt` |
| "Jarvis, volume up / down / mute" | Volume control |
| "Jarvis, take a screenshot" | Saved in `screenshots/` |
| "Jarvis, battery" / "CPU usage" | System status |
| "Jarvis, lock the laptop" / "shut down the laptop" | Asks to confirm first |
| "Jarvis, who is Elon Musk" | Wikipedia summary |
| "Jarvis, tell me a joke" | Joke |
| Anything else | AI answer (needs optional API key) |
| "Jarvis, goodbye" | Stops Jarvis |

---

## Setup on Windows (step by step)

### Step 1 - Install Python (once)
1. Download **Python 3.11 or 3.12** from https://www.python.org/downloads/
   (3.13 can work, but 3.11/3.12 is safest for PyAudio.)
2. In the installer, **tick "Add python.exe to PATH"**, then Install.
3. Check: open Command Prompt and run `python --version`.

### Step 2 - Install Git (once)
Download from https://git-scm.com/downloads and install with default options.

### Step 3 - Get the project
Option A - you downloaded the zip: right-click, Extract All, open the folder.

Option B - from GitHub (after you push it, see below):
```
git clone https://github.com/<your-username>/jarvis-assistant.git
cd jarvis-assistant
```

### Step 4 - One-click setup
Double-click **`setup_windows.bat`**. It creates a virtual environment, installs all packages, and creates your `.env` file.

### Step 5 - Configure (optional but recommended)
Open `.env` in Notepad and set:
- `USER_NAME` - what Jarvis calls you
- `DEFAULT_CITY` - for the weather
- `ANTHROPIC_API_KEY` - optional, gives Jarvis an AI brain for open questions (get one at https://console.anthropic.com)

### Step 6 - Test without a mic first
Double-click **`run_text_mode.bat`**, type `open youtube` and press Enter. If it works, the logic is fine.

### Step 7 - Run with voice
1. Windows Settings > Privacy & security > Microphone > allow desktop apps.
2. Double-click **`run_jarvis.bat`**.
3. Wait for "calibrating", then say **"Jarvis"**, and after it says "Yes?", give a command. You can also say it in one go: **"Jarvis open notepad"**.

An internet connection is needed (Google's free speech recognition).

---

## Put it on GitHub (your single repository)

1. Create an empty repo named `jarvis-assistant` on https://github.com/new (no README, no .gitignore).
2. In the project folder:
```
git init
git add .
git commit -m "Jarvis voice assistant"
git branch -M main
git remote add origin https://github.com/<your-username>/jarvis-assistant.git
git push -u origin main
```
`.env` (your API key) is in `.gitignore`, so it is never uploaded.

To get it on another laptop: `git clone`, run `setup_windows.bat`, make a new `.env`.

---

## Make Jarvis start automatically when Windows starts
1. Press `Win + R`, type `shell:startup`, press Enter.
2. Right-click `run_jarvis.bat` > Show more options > Create shortcut.
3. Move that shortcut into the Startup folder.

---

## Add your own commands
Open `jarvis/commands.py`.
- New app: add a line to the `APPS` dictionary.
- New website: add a line to `SITES`.
- New skill: write a function `h_something(text)` that returns `None` if the text isn't for it, `True` if handled, and add it to the `HANDLERS` list.

## Project layout
```
jarvis-assistant/
  main.py              entry point (voice / --text / --mic)
  jarvis/
    config.py          settings from .env
    speech.py          microphone + voice output
    commands.py        all commands and the AI fallback
  requirements.txt
  .env.example
  setup_windows.bat / run_jarvis.bat / run_text_mode.bat
  setup_mac_linux.sh
```

## Troubleshooting

**PyAudio fails to install on Windows**
Make sure you use Python 3.11 or 3.12 (64-bit), then run in the activated venv:
```
pip install --upgrade pip
pip install PyAudio
```
If it still fails, install `pipwin`: `pip install pipwin` then `pipwin install pyaudio`.

**"No microphone found"**
Run `python main.py --mic` to list devices. Check Windows microphone privacy settings and that no other app is using the mic.

**Jarvis doesn't hear the wake word / mishears it**
Add what it hears to `WAKE_WORDS` in `.env` (for example `jarvis,service,jarvish`). Speak clearly, closer to the mic, in a quiet room.

**"speech service unreachable"**
You need internet. Check your connection or firewall.

**No voice output**
`pyttsx3` uses the Windows voices. Check Settings > Time & language > Speech for installed voices; text is always printed in the console as well.

**Volume keys do nothing**
`pyautogui` sends media keys; some laptops need the Fn-lock off.

## Ideas to extend later
Offline speech with Vosk or Whisper, a custom wake-word engine (Porcupine), sending WhatsApp messages, controlling smart devices, a small GUI.
