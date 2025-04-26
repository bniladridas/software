#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Start Gunicorn with minimal configuration
gunicorn --bind 0.0.0.0:8000 --workers 4 simple_app:app
