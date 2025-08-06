#!/bin/bash

echo "Starting API Tester..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if virtual environment exists
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Installing dependencies globally..."
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Run the application
echo "Starting API Tester application..."
python3 main.py 