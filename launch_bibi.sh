#!/bin/bash

# 1. Check if the lock file exists to prevent multiple instances
# (This is a backup to the Python fcntl check)
if pgrep -f "jarvis_voice.py" > /dev/null; then
    exit 0
fi

# 2. Launch Konsole with a specific title and run the script
# --noclose is optional, but helps if the script crashes so you can see why
konsole --title "BIBI_CORE" -e /home/popica/jarvis/jarvis_env/bin/python /home/popica/jarvis/jarvis_voice.py
