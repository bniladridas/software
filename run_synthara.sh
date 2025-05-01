#!/bin/bash

# Synthara AI Setup and Run Script
# This script automates the setup and running of the Synthara AI application

echo "=== Synthara AI Setup and Run Script ==="
echo "This script will set up and run the Synthara AI application."

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"

# Check if we're in the right directory
if [ ! -f "simple_app.py" ]; then
    echo "ERROR: simple_app.py not found. Make sure you're in the software directory."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment. Try installing venv:"
        echo "pip install virtualenv"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source .venv/Scripts/activate
else
    # Unix/Linux/MacOS
    source .venv/bin/activate
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install together
pip install Flask==2.0.1 Werkzeug==2.0.1

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found."
    echo "You need a Together AI API key to use this application."
    read -p "Do you have a Together AI API key? (y/n): " has_key
    
    if [[ "$has_key" == "y" || "$has_key" == "Y" ]]; then
        read -p "Enter your Together AI API key: " api_key
        echo "TOGETHER_API_KEY=$api_key" > .env
        echo ".env file created with your API key."
    else
        echo "You can get an API key from https://www.together.ai"
        echo "Creating .env file with placeholder. You'll need to update it later."
        echo "TOGETHER_API_KEY=your_api_key_here" > .env
    fi
fi

# Run the application
echo "Starting Synthara AI application..."
echo "The application will be available at http://127.0.0.1:5001"
echo "Press Ctrl+C to stop the server."
$PYTHON_CMD simple_app.py
