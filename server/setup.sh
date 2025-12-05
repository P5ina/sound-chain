#!/bin/bash

# SoundChain Server Setup Script

set -e

echo "Setting up SoundChain server..."

# Create virtual environment
python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run the server:"
echo "  source venv/bin/activate"
echo "  python main.py"
