#!/bin/bash

# Exit on any error
set -e

echo -e "Starting Vosk Speech Recognition model setup..."

echo -e "Downloading Vosk Portuguese model..."
curl -L -o vosk-model.zip "https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip"

echo -e "Extracting model..."
7z x vosk-model.zip

mkdir -p speechRecognition
mv vosk-model-small-pt-0.3 model

mv model speechRecognition/

rm vosk-model.zip

echo -e "Complete. Model is located at: speechRecognition/model"
