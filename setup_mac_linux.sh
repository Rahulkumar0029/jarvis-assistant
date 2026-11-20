#!/usr/bin/env bash
# One-time setup for Jarvis on macOS / Linux.  Run:  bash setup_mac_linux.sh
set -e
cd "$(dirname "$0")"

if [[ "$OSTYPE" == "darwin"* ]]; then
  command -v brew >/dev/null && brew install portaudio || echo "Install Homebrew, then: brew install portaudio"
else
  sudo apt-get update
  sudo apt-get install -y python3-venv python3-dev portaudio19-dev espeak-ng ffmpeg python3-tk scrot
fi

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
[ -f .env ] || cp .env.example .env

echo
echo "Setup complete!  Run:  source venv/bin/activate && python main.py"
