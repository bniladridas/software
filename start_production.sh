#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Start Gunicorn with our configuration
gunicorn -c gunicorn_config.py simple_app:app
