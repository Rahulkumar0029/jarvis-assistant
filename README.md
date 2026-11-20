# Jarvis - Voice Assistant for Your Laptop

Say **"Jarvis, open YouTube"** and your laptop obeys. One repo, one setup script, runs fully on your laptop with a **free, provider-switchable AI brain** (Google Gemini, Groq, Ollama, or Anthropic).

## What it can do

| Say | Result |
|---|---|
| "Jarvis, open Chrome / VS Code / Notepad / Spotify" | Opens the app |
| "Jarvis, open GitHub / YouTube / Gmail" | Opens the website |
| "Jarvis, search for python tutorials" | Google search |
| "Jarvis, play arijit singh songs" | YouTube search |
| "Jarvis, what time is it" / "what's the date" | Time / date |
| "Jarvis, weather" / "weather in Jaipur" | Weather (via wttr.in) |
| "Jarvis, take a note buy charger" / "read my notes" | Notes in `notes.txt` |
| "Jarvis, volume up / down / mute" | Volume control |
| "Jarvis, take a screenshot" | Saved in `screenshots/` |
| "Jarvis, battery" / "CPU usage" | System status (psutil) |
| "Jarvis, lock the laptop" / "shut down the laptop" | Asks to confirm first |
| "Jarvis, who is Elon Musk" | Wikipedia summary |
| "Jarvis, tell me a joke" | Built-in jokes |
| Anything else | AI answer (Free Gemini, Groq, or local Ollama) |
| "Jarvis, goodbye" | Stops Jarvis |

---

## Free AI Brain (Gemini, Groq, Ollama)

Jarvis includes a zero-cost, provider-switchable AI engine that uses only standard HTTP requests (no heavy extra SDKs required).

### Option A: One-Command Interactive Setup
Run:
```powershell
python main.py --setup-ai
```
This interactive helper lets you select your provider, opens the API key page in your browser, securely accepts your key (input hidden), and writes it directly to `.env`.

### Option B: Manual Configuration (`.env`)
Open `.env` and set `AI_PROVIDER`:

1. **Google Gemini (Default - Free Tier)**
   - Get a free key: https://aistudio.google.com/apikey
   - Settings in `.env`:
     ```env
     AI_PROVIDER=gemini
     GEMINI_API_KEY=your_gemini_key_here
     GEMINI_MODEL=gemini-2.0-flash
     ```

2. **Groq (Free Ultra-Fast LPU Cloud)**
   - Get a free key: https://console.groq.com/keys
   - Settings in `.env`:
     ```env
     AI_PROVIDER=groq
     GROQ_API_KEY=your_groq_key_here
     GROQ_MODEL=llama-3.3-70b-versatile
     ```

3. **Ollama (100% Free & Local / Offline)**
   - Download & install: https://ollama.com/download
   - Pull the default 3B model: `ollama pull llama3.2`
   - Settings in `.env`:
     ```env
     AI_PROVIDER=ollama
     OLLAMA_URL=http://localhost:11434
     OLLAMA_MODEL=llama3.2
     ```

4. **Disable AI (Built-in commands only)**
   - Set `AI_PROVIDER=none` in `.env`.

### Test Your AI Brain
Verify your connection and measure latency at any time:
```powershell
python main.py --test-ai
```

---

## Setup on Windows (step by step)

### Step 1 - Install Python (once)
1. Download **Python 3.11 or 3.12** from https://www.python.org/downloads/
   (3.11 or 3.12 is recommended for native PyAudio wheels).
2. In the installer, **tick "Add python.exe to PATH"**, then Install.
3. Check: open Command Prompt and run `python --version`.

### Step 2 - Install Git (once)
Download from https://git-scm.com/downloads and install with default options.

### Step 3 - One-click setup
Double-click **`setup_windows.bat`**. It creates a virtual environment, upgrades pip, installs all packages, and creates your `.env` file.

### Step 4 - Configure AI Brain
Run:
```powershell
.\venv\Scripts\python.exe main.py --setup-ai
```
Pick Gemini (or Groq / Ollama), paste your key, and you're ready!

### Step 5 - Test without a mic first
Double-click **`run_text_mode.bat`**, type `open youtube` or ask any question and press Enter.

### Step 6 - Run with voice
1. Windows Settings > Privacy & security > Microphone > allow desktop apps.
2. Double-click **`run_jarvis.bat`**.
3. Wait for "(calibrating for background noise...)", then say **"Jarvis"**, and after it says "Yes?", give a command. You can also say it in one go: **"Jarvis open notepad"**.

---

## Put it on GitHub (your single repository)

```powershell
git init
git add .
git commit -m "Jarvis voice assistant"
git branch -M main
git remote add origin https://github.com/<your-username>/jarvis-assistant.git
git push -u origin main
```
`.env` (your API keys and private settings) is in `.gitignore`, so it is never uploaded.

---

## Make Jarvis start automatically when Windows starts
1. Press `Win + R`, type `shell:startup`, press Enter.
2. Right-click `run_jarvis.bat` > Show more options > Create shortcut.
3. Move that shortcut into the Startup folder.

---

## Add your own commands
Open `jarvis/commands.py`.
- New app: add an entry to the `APPS` dictionary.
- New website: add an entry to `SITES`.
- New skill: write a function `h_something(text)` that returns `None` if the text isn't for it, `True` if handled, and add it to the `HANDLERS` list.

## Project layout
```
jarvis-assistant/
  main.py              entry point (voice / --text / --mic / --setup-ai / --test-ai)
  jarvis/
    __init__.py
    config.py          settings from .env & environment
    ai.py              switchable AI brain (Gemini / Groq / Ollama / Anthropic)
    speech.py          microphone + voice output
    commands.py        command router & handlers
  requirements.txt
  .env.example
  setup_windows.bat / run_jarvis.bat / run_text_mode.bat
  setup_mac_linux.sh
```

---

## Troubleshooting

**HTTP 401 / 403 (Invalid API Key)**
- Your configured provider rejected the key. Rerun `python main.py --setup-ai` and paste a fresh API key, or check `.env`.

**HTTP 429 (Rate Limit Reached)**
- Free tier requests per minute were exceeded. Wait 60 seconds, or switch to Groq (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) or local Ollama (`llama3.2`).

**Ollama Connection Refused**
- Ensure Ollama is installed and running (`ollama serve` or launch the Ollama desktop app). Run `ollama pull llama3.2` to download the model.

**PyAudio fails to install on Windows**
- Use Python 3.11 or 3.12 (64-bit), then run in the activated venv:
  ```powershell
  pip install --upgrade pip
  pip install PyAudio
  ```

**"No microphone found"**
- Run `python main.py --mic` to list devices. Confirm desktop access in Windows Settings > Privacy & security > Microphone.

**Jarvis doesn't hear the wake word / mishears it**
- Add what it hears to `WAKE_WORDS` in `.env` (e.g. `jarvis,service,jarvas`).

**"speech service unreachable"**
- Google speech recognition requires an active internet connection.

**No voice output**
- `pyttsx3` uses Windows SAPI voices. Check Settings > Time & language > Speech; text is also printed to the console.
