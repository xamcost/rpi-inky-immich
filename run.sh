#!/bin/bash

# Set up python environment and run the main application
# Usage: ./run.sh
# Make sure to give execute permission: chmod +x run.sh

# Navigate to the script's directory
cd "$(dirname "$0")" || exit 1

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  echo "Activating virtual environment and installing dependencies..."
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "Activating existing virtual environment..."
  source venv/bin/activate
fi

# Source environment variables
if [ -f ".env" ]; then
  echo "Sourcing environment variables from .env file..."
  set -a
  source .env
  set +a
else
  echo ".env file not found."
  exit 1
fi

# Run the main application
echo "Running the main application..."
python main.py
