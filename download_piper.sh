#!/bin/bash

# Exit on any error
set -e

echo -e "Starting Piper setup..."

echo -e "Downloading Piper v1.2.0 ARM64..."
curl -L -o piper_arm64.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz

echo -e "Extracting to piper folder..."
mkdir -p tts
tar -xzf piper_arm64.tar.gz -C tts

echo -e "Downloading Piper voice model"
curl -L -o pt_BR-faber-medium.onnx "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx?download=true"

echo -e "Downloading Piper voice model config"
curl -L -o pt_BR-faber-medium.onnx.json "https://huggingface.co/rhasspy/piper-voices/resolve/main/pt/pt_BR/faber/medium/pt_BR-faber-medium.onnx.json?download=true"

mv pt_BR-faber-medium.onnx tts/
mv pt_BR-faber-medium.onnx.json tts/

rm piper_arm64.tar.gz

echo -e "Complete. Files are located in the 'piper' folder"
