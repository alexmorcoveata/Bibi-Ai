#!/bin/bash

# Load your function manually at the top so we don't have to call zsh -c every time
# Make sure this path to your piper/model is correct!
say_it() {
    echo "$1" | /home/popica/jarvis/piper/piper/piper \
    --model /home/popica/jarvis/piper/en_GB-alan-low.onnx \
    --length_scale 1.15 --noise_scale 0.7 --noise_w 0.9 \
    --output-raw | aplay -r 16000 -f S16_LE -t raw 2>/dev/null
}

echo "Jarvis: Systems online. Standing by, Sir."
say_it "Systems online. Standing by, Sir."

while true; do
    echo -n "Sir? "
    read user_input
    
    if [[ "$user_input" == "exit" || "$user_input" == "quit" ]]; then
        say_it "Understood. Powering down."
        break
    fi

    echo "Thinking..."
    # We use --stream to get text, but we'll collect it for the voice
    response=$(ollama run llama3 "$user_input")
    
    echo "Jarvis: $response"
    
    # Pass the response as a direct argument to the function
    # This avoids the "unmatched quote" shell error
    say_it "$response"
done
