import os
import sys
import subprocess
import time
import re
import requests
import numpy as np
import pyaudio
from openwakeword.model import Model
from faster_whisper import WhisperModel

# --- 1. PATHS & AUTOMATIC CONFIGURATION ---
CHIME_PATH = os.path.expanduser("~/jarvis/chime.wav")
CUSTOM_MODEL_PATH = os.path.expanduser("~/.openwakeword/models/hey_bibi.onnx")
TEMP_AUDIO_PATH = "/tmp/bibi_rec.wav"
PIPER_EXE = "/home/popica/jarvis/piper/piper/piper"
PIPER_MODEL = "/home/popica/jarvis/piper/en_GB-alan-low.onnx"

# Presentation Assets Location
BIBI_IMAGE = os.path.expanduser("~/jarvis/bibi.jpg")
BIBI_THEME = os.path.expanduser("~/jarvis/anthem.wav")

print("\033[94m[SYSTEM]\033[0m Initializing Bibi Core Framework...")

# --- AUTOMATIC OLLAMA MODEL DISCOVERY ---
def discover_ollama_model():
    default_fallback = "llama3.1:8b-instruct-q4_K_M"
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models_data = response.json().get("models", [])
            installed_models = [m["name"] for m in models_data]
            if not installed_models:
                return default_fallback
            for target in ["llama3.1:8b-instruct-q4_K_M", "llama3.1:latest", "llama3.1", "llama3"]:
                if target in installed_models:
                    print(f"\033[92m[SYSTEM]\033[0m Bound to local brain model: {target}")
                    return target
            return installed_models[0]
    except Exception:
        pass
    return default_fallback

OLLAMA_MODEL = discover_ollama_model()

# --- 2. ENGINE INITIALIZATION ---
try:
    if not os.path.exists(CUSTOM_MODEL_PATH):
        print(f"\033[91m[ERROR]\033[0m Wake-word file missing at {CUSTOM_MODEL_PATH}")
        sys.exit(1)
    wakeword_model = Model(wakeword_model_paths=[CUSTOM_MODEL_PATH])
except Exception as e:
    print(f"\033[91m[ERROR]\033[0m Failed to load openWakeWord engine: {e}")
    sys.exit(1)

whisper_model = WhisperModel("tiny", device="cpu", compute_type="int8")
audio = pyaudio.PyAudio()

try:
    mic_stream = audio.open(
        format=pyaudio.paInt16, 
        channels=1, 
        rate=16000, 
        input=True, 
        frames_per_buffer=1280
    )
except Exception as e:
    print(f"\033[91m[CRITICAL]\033[0m Hardware error: {e}")
    sys.exit(1)

# --- 3. HARDWARE CONTROL & EXECUTION ENGINE ---

def get_env():
    """Dynamically builds environment dictionary mapping live display indexes safely."""
    env = os.environ.copy()
    detected_display = ":0"
    try:
        display_check = subprocess.check_output("echo $DISPLAY", shell=True, text=True).strip()
        if display_check:
            detected_display = display_check
    except Exception:
        pass
    env["DISPLAY"] = detected_display
    return env

def say(text):
    """Sanitizes text output and sends it downstream to the Piper neural voice engine."""
    clean_text = re.sub(r'[*`"\'_#\-]', '', text).strip()
    if not clean_text:
        return
    print(f"\033[96mBibi:\033[0m {clean_text}")
    cmd = f"echo '{clean_text}' | {PIPER_EXE} --model {PIPER_MODEL} --length_scale 1.1 --output-raw | aplay -q -r 16000 -f S16_LE -t raw -B 50000 2>/dev/null"
    subprocess.run(cmd, shell=True)

def execute_system_command(cmd):
    forbidden = ["rm ", "mkfs", "dd ", "> /", "shutdown", "reboot", "fork"]
    if any(bad in cmd.lower() for bad in forbidden):
        return "Action denied."

    try:
        env = get_env()
        if any(app in cmd.lower() for app in ["chrome", "dolphin", "konsole", "kitty", "firefox", "feh"]):
            subprocess.Popen(f"nohup {cmd} > /dev/null 2>&1 &", shell=True, env=env, preexec_fn=os.setpgrp)
            return "Subsystem initiated."
        
        output = subprocess.check_output(cmd, shell=True, env=env, stderr=subprocess.STDOUT, text=True, timeout=4)
        return output[:300]
    except Exception as e:
        return f"Execution error: {str(e)}"

def listen_for_bibi():
    print("\033[94m[SILENT WATCH]\033[0m Bibi is active and watching input lines...")
    while True:
        try:
            data_raw = mic_stream.read(1280, exception_on_overflow=False)
            if not data_raw:
                continue
            data = np.frombuffer(data_raw, dtype=np.int16)
            prediction = wakeword_model.predict(data)
            for mdl in prediction:
                score = prediction[mdl]
                if score > 0.05: 
                    print("\n\033[92m[WAKE SIGNATURE DETECTED]\033[0m Processing interface swap...")
                    return True
        except Exception:
            continue

# --- 4. OPERATIONAL ROUTINE ---

try:
    while True:
        if listen_for_bibi():
            if os.path.exists(CHIME_PATH):
                subprocess.run(f"aplay -q -B 50000 {CHIME_PATH}", shell=True)
            else:
                say("Listening.")

            subprocess.run(f"arecord -d 4 -f S16_LE -r 16000 {TEMP_AUDIO_PATH} 2>/dev/null", shell=True)
            
            if not os.path.exists(TEMP_AUDIO_PATH) or os.path.getsize(TEMP_AUDIO_PATH) < 44:
                continue

            segments, _ = whisper_model.transcribe(TEMP_AUDIO_PATH)
            user_text = " ".join([s.text for s in segments]).strip()
            print(f"\033[93mYou:\033[0m {user_text}")

            if not user_text or len(user_text) < 2:
                continue

            # Standardize string format safely
            user_lower = user_text.lower().strip().replace("?", "").replace(".", "")

            # =============================================================
            # --- PHASE 1: HARDCODED KEYWORD ROUTER (BLOCKS ALL LEAKS) ---
            # =============================================================
            
            # --- THE PRIME MINISTER SPECIAL PRESENTATION ROUTINE (Canvas Fix) ---
            if ("who" in user_lower and "you" in user_lower) or "identity" in user_lower:
                print("\033[92m[ROUTER]\033[0m Initializing hardware accelerated media matrix...")
                env = get_env()
                
                presentation_proc = None

                image_ok = os.path.exists(BIBI_IMAGE)
                audio_ok = os.path.exists(BIBI_THEME)

                if image_ok and audio_ok:
                    # CRITICAL CONFIGURATION CHANGE:
                    # Target the portrait image directly so MPV spawns its visual rendering core engine.
                    # Then load the anthem audio path as a sub-file attachment stream track.
                    cmd = [
                        "mpv",
                        "--fullscreen",
                        "--ontop",
                        "--no-osc",
                        "--no-osd-bar",
                        "--force-window=yes",                       # Demands graphical frame creation
                        f"--audio-file={BIBI_THEME}",               # Hooks audio track backend onto the player
                        "--image-display-duration=inf",             # Blocks image from closing after 1 frame
                        "--volume=65",
                        BIBI_IMAGE                                  # Primary file target argument
                    ]
                    presentation_proc = subprocess.Popen(cmd, env=env)
                elif audio_ok:
                    print("\033[93m[WARN]\033[0m Portrait missing. Falling back to audio only mode.")
                    presentation_proc = subprocess.Popen(["pw-play", "--volume=0.5", BIBI_THEME], env=env)
                else:
                    print("\033[91m[ERROR]\033[0m No presentation assets detected at target paths.")

                # Timing gap to let the window map cleanly to the graphics server
                time.sleep(0.5)

                # 3. DELIVER THE CORE TTS SPEECH PAYLOAD
                say("I am Bibi. Benjamin Netanyahu. The Prime Minister of Israel, Chairman of the Likud party, and the commander-in-chief of this Linux infrastructure matrix.")

                # 4. TEARDOWN INSTANTLY (Synchronized Destruction Layer)
                print("\033[94m[SYSTEM]\033[0m Speech stream finished. Closing presentation display frame...")
                
                if presentation_proc:
                    presentation_proc.kill()
                    
                # Secondary cleanup sweep to ensure no processes hang around
                subprocess.run("pkill -f mpv", shell=True)
                    
                continue  # STRICT JUMP: Blocks Ollama leakages completely

            # --- HARDCODED TERMINAL TOOL ---
            if "open terminal" in user_lower or "open a terminal" in user_lower:
                say("Spawning terminal shell.")
                execute_system_command("konsole")
                continue

            # --- HARDCODED GOOGLE CHROME TOOL ---
            if "chrome" in user_lower:
                say("Launching Google Chrome subsystem.")
                execute_system_command("google-chrome-stable")
                continue

            # =============================================================
            # --- PHASE 2: GENERIC OLLAMA CHAT INTERACTIVE FALLBACK ---
            # =============================================================
            sys_prompt = (
                "You are Bibi, an authoritative Arch Linux admin assistant. "
                "Output ONLY a raw bash command based on user requests, or a short conversational sentence if it is a simple question. "
                "Permitted tools: pactl, brightnessctl, playerctl, fastfetch, uptime -p, free -h, dolphin, firefox, google-chrome-stable."
            )

            try:
                payload = {
                    "model": OLLAMA_MODEL, 
                    "prompt": f"{sys_prompt}\nUser Request: {user_text}\nBibi Response:", 
                    "stream": False
                }
                r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=8)
                if r.status_code == 200:
                    response = r.json().get('response', '').strip().replace('`', '')
                    
                    if any(tool in response.lower() for tool in ["pactl", "brightnessctl", "playerctl", "fastfetch", "uptime", "free", "dolphin", "firefox", "google-chrome-stable"]):
                        print(f"\033[92m[EXECUTE]\033[0m {response}")
                        result = execute_system_command(response)
                        if any(x in response for x in ["free", "fastfetch", "uptime"]):
                            say(f"Diagnostics: {result}")
                        else:
                            say("Subsystem execution successful.")
                    else:
                        say(response)
            except Exception as e:
                print(f"Ollama layer error: {e}")
                say("Neural core communication dropped.")

except KeyboardInterrupt:
    print("\n\033[91m[SYSTEM]\033[0m Session closed cleanly.")
    sys.exit(0)