import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from the root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Conditionally import Together to allow for mock mode
try:
    from together import Together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False
    logging.warning("Together package not available. Using mock mode.")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            template_folder='../templates',  # Specify the template folder
            static_folder='../static')       # Specify the static folder

# Import the routes and models from the main app
from simple_app import AVAILABLE_TEXT_MODELS, AVAILABLE_IMAGE_MODELS

# Initialize Together client
api_key = os.getenv("TOGETHER_API_KEY")
client = None

if TOGETHER_AVAILABLE and api_key:
    try:
        client = Together(api_key=api_key)
        logger.info("Together API client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Together API client: {e}")
else:
    logger.warning("Together API not available or API key not found. Using mock mode.")

# Import all routes from the main app
from simple_app import index, resources, synthara, deployment_protection, api_key, privacy_policy
from simple_app import get_prompt_suggestions, get_models, generate_text, generate_image

# For Vercel serverless functions, we need to export the app variable
# This is what Vercel will use as the entry point
