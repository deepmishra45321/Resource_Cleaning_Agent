#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Pulling Qwen2.5:1.5b model..."
ollama pull qwen2.5:1.5b
echo "Setup complete."
