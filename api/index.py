import os
import sys
import logging
import json
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the absolute path to the static folder
static_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
template_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')

# Log folder paths for debugging
logger.info(f"Static folder path: {static_folder}")
logger.info(f"Template folder path: {template_folder}")

# Check if we're running in Vercel environment
is_vercel = os.environ.get('VERCEL') == '1'
logger.info(f"Running in Vercel environment: {is_vercel}")

# In Vercel, the file structure might be different
if is_vercel:
    # Try alternative paths for Vercel
    alt_static_folder = os.path.join(os.getcwd(), 'static')
    alt_template_folder = os.path.join(os.getcwd(), 'templates')

    # Check if alternative paths exist
    if os.path.exists(alt_static_folder):
        logger.info(f"Using alternative static folder: {alt_static_folder}")
        static_folder = alt_static_folder

    if os.path.exists(alt_template_folder):
        logger.info(f"Using alternative template folder: {alt_template_folder}")
        template_folder = alt_template_folder

# Initialize Flask app with template and static folders
app = Flask(__name__,
            template_folder=template_folder,
            static_folder=static_folder)

# Add explicit route for static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(static_folder, path)

# Add a route to serve the base.html template directly
@app.route('/debug/base-html')
def serve_base_html():
    try:
        return render_template('base.html')
    except Exception as e:
        return f"Error rendering base.html: {str(e)}"

# Available models
AVAILABLE_TEXT_MODELS = [
    {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "name": "Llama-3.3-70B"},
    {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", "name": "DeepSeek-R1-70B"},
    {"id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "name": "Llama-4-Maverick-17B", "requires_api_key": True}
]

AVAILABLE_IMAGE_MODELS = [
    {"id": "black-forest-labs/FLUX.1-dev", "name": "FLUX.1-dev", "requires_api_key": True}
]

# Get API key from environment - try multiple methods with detailed logging
logger.info("Attempting to load API key from environment variables")
TOGETHER_API_KEY = None

# Method 1: os.getenv
api_key_from_getenv = os.getenv("TOGETHER_API_KEY")
logger.info(f"API key from os.getenv: {'Found' if api_key_from_getenv else 'Not found'}")

# Method 2: os.environ
api_key_from_environ = os.environ.get("TOGETHER_API_KEY")
logger.info(f"API key from os.environ: {'Found' if api_key_from_environ else 'Not found'}")

# Method 3: Vercel specific environment variables
# Sometimes Vercel uses different naming conventions
api_key_from_vercel = os.environ.get("VERCEL_TOGETHER_API_KEY")
logger.info(f"API key from VERCEL_TOGETHER_API_KEY: {'Found' if api_key_from_vercel else 'Not found'}")

# Try loading from .env file directly if not found in environment
api_key_from_file = None
try:
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    logger.info(f"Checking for .env file at: {env_path}")
    if os.path.exists(env_path):
        logger.info(".env file found, attempting to read")
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    try:
                        key, value = line.strip().split('=', 1)
                        if key == "TOGETHER_API_KEY":
                            api_key_from_file = value
                            logger.info("API key found in .env file")
                            break
                    except ValueError:
                        continue
    else:
        logger.info(".env file not found")
except Exception as e:
    logger.error(f"Error loading API key from .env file: {e}")

# Use the first available API key
TOGETHER_API_KEY = api_key_from_getenv or api_key_from_environ or api_key_from_vercel or api_key_from_file

# Hardcoded API key as a last resort (for testing only)
if not TOGETHER_API_KEY:
    logger.warning("No API key found in environment variables or .env file. Using hardcoded key for testing.")
    TOGETHER_API_KEY = "14d0c8d9b0e3569e437c5d5083f706215fd5b71f283dca2e6186b5823d6d2b35"

logger.info(f"API Key available: {bool(TOGETHER_API_KEY)}")

# Add a debug route to check environment variables
@app.route('/debug/env')
def debug_env():
    # Get template folder contents
    template_files = []
    if os.path.exists(template_folder):
        template_files = os.listdir(template_folder)

    # Get static folder contents
    static_files = []
    if os.path.exists(static_folder):
        static_files = os.listdir(static_folder)

    # Check if base.html exists
    base_html_path = os.path.join(template_folder, 'base.html')
    base_html_exists = os.path.exists(base_html_path)
    base_html_content = None
    if base_html_exists:
        try:
            with open(base_html_path, 'r') as f:
                base_html_content = f.read()[:500] + "... (truncated)"
        except Exception as e:
            base_html_content = f"Error reading file: {str(e)}"

    env_vars = {
        "TOGETHER_API_KEY_SET": bool(TOGETHER_API_KEY),
        "API_KEY_SOURCES": {
            "os.getenv": bool(api_key_from_getenv),
            "os.environ": bool(api_key_from_environ),
            "VERCEL_TOGETHER_API_KEY": bool(api_key_from_vercel),
            "env_file": bool(api_key_from_file),
            "hardcoded": bool(TOGETHER_API_KEY) and not any([api_key_from_getenv, api_key_from_environ, api_key_from_vercel, api_key_from_file])
        },
        "PYTHON_VERSION": sys.version,
        "ENV_VARS_KEYS": list(os.environ.keys()),
        "ENV_VARS_COUNT": len(os.environ),
        "VERCEL_ENV_VARS": {k: (v if not k.endswith("API_KEY") and not k.endswith("SECRET") and not k.endswith("PASSWORD") else "REDACTED")
                            for k, v in os.environ.items() if k.startswith("VERCEL_")},
        "STATIC_FOLDER": static_folder,
        "TEMPLATE_FOLDER": template_folder,
        "STATIC_FOLDER_EXISTS": os.path.exists(static_folder),
        "TEMPLATE_FOLDER_EXISTS": os.path.exists(template_folder),
        "TEMPLATE_FILES": template_files,
        "STATIC_FILES": static_files,
        "BASE_HTML_EXISTS": base_html_exists,
        "BASE_HTML_CONTENT": base_html_content,
        "CWD": os.getcwd(),
        "FILES_IN_CWD": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else []
    }
    return jsonify(env_vars)

# Add a route to test the API key
@app.route('/debug/api-key-test')
def api_key_test():
    result = {
        "api_key_set": bool(TOGETHER_API_KEY),
        "api_key_sources": {
            "os.getenv": bool(api_key_from_getenv),
            "os.environ": bool(api_key_from_environ),
            "VERCEL_TOGETHER_API_KEY": bool(api_key_from_vercel),
            "env_file": bool(api_key_from_file),
            "hardcoded": bool(TOGETHER_API_KEY) and not any([api_key_from_getenv, api_key_from_environ, api_key_from_vercel, api_key_from_file])
        },
        "api_key_length": len(TOGETHER_API_KEY) if TOGETHER_API_KEY else 0,
        "api_key_prefix": TOGETHER_API_KEY[:5] + "..." if TOGETHER_API_KEY else None
    }

    if not TOGETHER_API_KEY:
        result.update({
            "success": False,
            "message": "API key not found in environment variables"
        })
        return jsonify(result)

    try:
        # Make a simple API call to test the key
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        logger.info("Making test request to Together API")
        response = requests.get(
            "https://api.together.xyz/v1/models",
            headers=headers
        )

        result.update({
            "request_made": True,
            "status_code": response.status_code
        })

        if response.status_code == 200:
            models_data = response.json().get("data", [])
            result.update({
                "success": True,
                "message": "API key is valid",
                "models_count": len(models_data),
                "models_sample": [m.get("id") for m in models_data[:3]] if models_data else []
            })
        else:
            result.update({
                "success": False,
                "message": "API key validation failed",
                "response": response.text
            })
    except Exception as e:
        logger.error(f"Error testing API key: {e}", exc_info=True)
        result.update({
            "success": False,
            "message": f"Error testing API key: {str(e)}",
            "error_type": type(e).__name__,
            "request_made": False
        })

    return jsonify(result)

@app.route('/')
def index():
    # Always use the standalone HTML for consistency
    # This bypasses the template system entirely
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Generation - Synthara AI</title>

        <!-- Author and Description Meta Tags -->
        <meta name="author" content="Niladri Das">
        <meta name="description" content="Synthara AI: Create professional-quality text and images with state-of-the-art AI models. Access premium AI capabilities including FLUX.1 and Llama models through our intuitive, mobile-friendly interface.">

        <!-- Open Graph / Social Media Meta Tags -->
        <meta property="og:title" content="Synthara AI - Advanced Text & Image Generation Platform">
        <meta property="og:description" content="Synthara AI: Create professional-quality text and images with state-of-the-art AI models. Access premium AI capabilities including FLUX.1 and Llama models through our intuitive, mobile-friendly interface.">
        <meta property="og:image" content="https://software-bniladridas.vercel.app/static/images/og-image.png">
        <meta property="og:url" content="https://software-bniladridas.vercel.app/">
        <meta property="og:type" content="website">
        <meta property="og:site_name" content="Synthara AI">
        <meta property="article:author" content="Niladri Das (bniladridas)">

        <!-- Twitter Card Meta Tags -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Synthara AI - Advanced Text & Image Generation Platform">
        <meta name="twitter:description" content="Synthara AI: Create professional-quality text and images with state-of-the-art AI models. Access premium AI capabilities including FLUX.1 and Llama models through our intuitive, mobile-friendly interface.">
        <meta name="twitter:image" content="https://software-bniladridas.vercel.app/static/images/og-image.svg">
        <meta name="twitter:creator" content="@bniladridas">

        <!-- LinkedIn Specific Meta Tags -->
        <meta property="linkedin:owner" content="Niladri Das (bniladridas)">
        <meta property="linkedin:title" content="Synthara AI - Advanced Text & Image Generation Platform">
        <meta property="linkedin:description" content="Create professional-quality text and images with state-of-the-art AI models. Access premium AI capabilities including FLUX.1 and Llama models through our intuitive, mobile-friendly interface.">
        <meta name="image" content="https://software-bniladridas.vercel.app/static/images/og-image.png">

        <!-- Favicon -->
        <link rel="icon" href="/static/images/favicon.ico">

        <!-- CSS -->
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="stylesheet" href="/static/css/mobile.css">
        <link rel="stylesheet" href="/static/css/software-layout.css">

        <!-- Font Awesome -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

        <style>
            /* Mobile styles - navigation always visible */
            @media (max-width: 768px) {
                header {
                    position: relative !important;
                    padding-top: 16px !important;
                }

                .nav-links {
                    display: flex !important;
                    flex-wrap: wrap;
                    justify-content: center;
                    width: 100%;
                    margin-top: 16px;
                }

                .nav-link {
                    padding: 8px 16px;
                    margin: 4px;
                    text-align: center;
                    font-size: 1rem;
                    border-radius: 4px;
                    background-color: #f5f5f5;
                }
            }
        </style>
    </head>
    <body>
        <div class="software-container">
            <div class="software-header">
                <div class="software-logo">
                    <img src="/static/images/logo.png" alt="Synthara AI Logo">
                    <h1>AI Generation</h1>
                </div>
                <div class="software-nav">
                    <a href="/" class="software-nav-link active">Home</a>
                    <a href="/resources" class="software-nav-link">Models</a>
                    <a href="/synthara" class="software-nav-link">About</a>
                    <a href="/deployment-protection" class="software-nav-link">Protection</a>
                    <a href="/api-key" class="software-nav-link">API Key</a>
                </div>
            </div>

            <div class="software-main">
                <div class="software-sidebar">
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Generation</div>
                        <div class="sidebar-item active">Text Generation</div>
                        <div class="sidebar-item">Image Generation</div>
                    </div>
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Models</div>
                        <div class="sidebar-item">Llama-3.3-70B</div>
                        <div class="sidebar-item">DeepSeek-R1-70B</div>
                        <div class="sidebar-item">Llama-4-Maverick-17B</div>
                        <div class="sidebar-item">FLUX.1-dev</div>
                    </div>
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Settings</div>
                        <div class="sidebar-item">API Key Setup</div>
                        <div class="sidebar-item">Deployment Protection</div>
                    </div>
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">About</div>
                        <div class="sidebar-item">Synthara AI</div>
                        <div class="sidebar-item">Documentation</div>
                    </div>
                </div>

                <div class="software-content">
                    <div class="software-toolbar">
                        <button class="software-toolbar-button primary">New Generation</button>
                        <button class="software-toolbar-button">Clear All</button>
                        <button class="software-toolbar-button">Save Output</button>
                    </div>

                    <div class="software-combined-interface">
                        <!-- Text Generation Section -->
                        <div class="software-section">
                            <div class="software-section-header">Text Generation</div>
                            <div class="software-section-content">
                                <div class="software-form-group">
                                    <label class="software-form-label" for="text-model">Model</label>
                                    <select class="software-form-select" id="text-model">
                                        <option value="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free">Llama-3.3-70B</option>
                                        <option value="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free">DeepSeek-R1-70B</option>
                                        <option value="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8">Llama-4-Maverick-17B (API Key Required)</option>
                                    </select>
                                </div>
                                <div class="software-form-group">
                                    <label class="software-form-label" for="text-prompt">Prompt <span style="font-size: 12px; color: #666;">(Press Enter to generate)</span></label>
                                    <textarea class="software-form-textarea" id="text-prompt" placeholder="Type here..."></textarea>
                                </div>
                                <div class="software-output">
                                    <div class="software-output-header">
                                        <h3 class="software-output-title">Output</h3>
                                        <button id="copy-text-btn" title="Copy" style="background: none; border: none; cursor: pointer;">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                            </svg>
                                        </button>
                                    </div>
                                    <div id="text-output" class="software-output-content">
                                        <p class="software-placeholder">Output will appear here</p>
                                    </div>
                                </div>
                            </div>
                            <div class="software-section-footer">
                                <button id="generate-text-btn" class="software-toolbar-button primary">Generate</button>
                            </div>
                        </div>

                        <!-- Image Generation Section -->
                        <div class="software-section">
                            <div class="software-section-header">Image Generation</div>
                            <div class="software-section-content">
                                <div class="software-form-group">
                                    <label class="software-form-label" for="image-model">Model</label>
                                    <select class="software-form-select" id="image-model">
                                        <option value="black-forest-labs/FLUX.1-dev">FLUX.1-dev (API Key Required)</option>
                                    </select>
                                </div>
                                <div class="software-form-group">
                                    <label class="software-form-label" for="image-prompt">Prompt <span style="font-size: 12px; color: #666;">(Press Enter to generate)</span></label>
                                    <textarea class="software-form-textarea" id="image-prompt" placeholder="Type here..."></textarea>
                                </div>
                                <div class="software-output">
                                    <div class="software-output-header">
                                        <h3 class="software-output-title">Output</h3>
                                    </div>
                                    <div id="image-output" class="software-output-content">
                                        <p class="software-placeholder">Output will appear here</p>
                                    </div>
                                </div>
                            </div>
                            <div class="software-section-footer">
                                <button id="generate-image-btn" class="software-toolbar-button primary">Generate</button>
                            </div>
                        </div>
                    </div>

                    <div class="software-status-bar">
                        <div class="software-status-item">Ready</div>
                        <div class="software-status-item">API Status: Connected</div>
                        <div class="software-status-item">Models: 4 Available</div>
                    </div>
                </div>
            </div>

            <div class="software-footer">
                <div>© 2025 Synthara AI</div>
                <div class="contact">Contact: <a href="mailto:synthara.company@gmail.com">synthara.company@gmail.com</a></div>
            </div>
        </div>

        <!-- Inline script for critical mobile functionality -->
        <script>
            // Ensure hamburger menu works even if external scripts fail to load
            document.addEventListener('DOMContentLoaded', function() {
                const hamburgerBtn = document.querySelector('.hamburger-menu');
                const navLinks = document.querySelector('.nav-links');

                if (hamburgerBtn && navLinks) {
                    hamburgerBtn.addEventListener('click', function() {
                        this.classList.toggle('open');
                        navLinks.classList.toggle('open');
                    });
                }
            });

            // Execute immediately as well
            (function() {
                const hamburgerBtn = document.querySelector('.hamburger-menu');
                const navLinks = document.querySelector('.nav-links');

                if (hamburgerBtn && navLinks) {
                    hamburgerBtn.addEventListener('click', function() {
                        this.classList.toggle('open');
                        navLinks.classList.toggle('open');
                    });
                }
            })();
        </script>

        <!-- Core Scripts -->
        <script src="/static/js/main.js"></script>
        <script src="/static/js/notifications.js"></script>
        <script src="/static/js/mobile.js"></script>
    </body>
    </html>
    """
    return html_content

@app.route('/resources')
def resources():
    # Return a simple HTML page with the hamburger menu
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>About Our Models - Synthara AI</title>

        <!-- Author and Description Meta Tags -->
        <meta name="author" content="Niladri Das">
        <meta name="description" content="Learn about the AI models available in Synthara AI. Access premium AI capabilities including FLUX.1 and Llama models through our intuitive, mobile-friendly interface.">

        <!-- Favicon -->
        <link rel="icon" href="/static/images/favicon.ico">

        <!-- CSS -->
        <link rel="stylesheet" href="/static/css/styles.css">
        <link rel="stylesheet" href="/static/css/mobile.css">

        <!-- Font Awesome -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

        <style>
            /* Critical mobile styles inline */
            @media (max-width: 768px) {
                .hamburger-menu {
                    display: block !important;
                    position: absolute !important;
                    top: 16px !important;
                    right: 0 !important;
                    z-index: 100 !important;
                    background: none !important;
                    border: none !important;
                    cursor: pointer !important;
                    padding: 8px !important;
                    width: 44px !important;
                    height: 44px !important;
                }

                .hamburger-icon {
                    display: block;
                    position: relative;
                    width: 24px;
                    height: 18px;
                    margin: 0 auto;
                }

                .hamburger-icon span {
                    display: block;
                    position: absolute;
                    height: 2px;
                    width: 100%;
                    background: #000;
                    border-radius: 2px;
                    opacity: 1;
                    left: 0;
                    transform: rotate(0deg);
                    transition: .25s ease-in-out;
                }

                .hamburger-icon span:nth-child(1) {
                    top: 0px;
                }

                .hamburger-icon span:nth-child(2) {
                    top: 8px;
                }

                .hamburger-icon span:nth-child(3) {
                    top: 16px;
                }

                .hamburger-menu.open .hamburger-icon span:nth-child(1) {
                    top: 8px;
                    transform: rotate(135deg);
                }

                .hamburger-menu.open .hamburger-icon span:nth-child(2) {
                    opacity: 0;
                    left: -60px;
                }

                .hamburger-menu.open .hamburger-icon span:nth-child(3) {
                    top: 8px;
                    transform: rotate(-135deg);
                }

                header {
                    position: relative !important;
                    padding-top: 16px !important;
                }

                .nav-links {
                    display: none;
                    width: 100%;
                }

                .nav-links.open {
                    display: flex;
                    flex-direction: column;
                    position: absolute;
                    top: 70px;
                    left: 0;
                    right: 0;
                    background: #fff;
                    padding: 24px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    z-index: 99;
                    border-radius: 2px;
                    border: 1px solid rgba(0, 0, 0, 0.05);
                }

                .nav-link {
                    padding: 16px 0;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
                    width: 100%;
                    text-align: center;
                    font-size: 1rem;
                }

                .nav-link:last-child {
                    border-bottom: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <header>
                <div class="logo">
                    <img src="/static/images/logo.png" alt="Synthara AI Logo" class="header-logo">
                    <h1>About Our Models</h1>
                </div>

                <div class="nav-links">
                    <a href="/" class="nav-link">Home</a>
                    <a href="/resources" class="nav-link">About Our Models</a>
                    <a href="/synthara" class="nav-link">About Synthara AI</a>
                    <a href="/deployment-protection" class="nav-link">Deployment Protection</a>
                    <a href="/api-key" class="nav-link">API Key Setup</a>
                </div>
            </header>

            <main>
                <div class="section">
                    <h2>About Our Models</h2>
                    <p>Synthara AI provides access to state-of-the-art AI models for text and image generation.</p>

                    <h3>Text Generation Models</h3>
                    <ul>
                        <li><strong>Llama-3.3-70B</strong> - Meta's latest large language model with 70 billion parameters</li>
                        <li><strong>DeepSeek-R1-70B</strong> - A powerful 70B parameter model from DeepSeek AI</li>
                        <li><strong>Llama-4-Maverick-17B</strong> - Meta's Llama 4 model (requires API key)</li>
                    </ul>

                    <h3>Image Generation Models</h3>
                    <ul>
                        <li><strong>FLUX.1-dev</strong> - A 12B parameter rectified flow transformer for high-quality image generation</li>
                    </ul>

                    <p>Our API Key Orchestration Pipeline allows you to access premium AI models with your own API keys.</p>
                </div>
            </main>

            <footer>
                <p>&copy; 2024 Synthara AI. All rights reserved.</p>
            </footer>
        </div>

        <!-- Mobile functionality script removed -->

        <!-- Core Scripts -->
        <script src="/static/js/main.js"></script>
        <script src="/static/js/notifications.js"></script>
        <script src="/static/js/mobile.js"></script>
    </body>
    </html>
    """
    return html_content

@app.route('/synthara')
def synthara():
    # Check if we're in Vercel environment and if base.html exists
    base_html_path = os.path.join(template_folder, 'base.html')
    base_html_exists = os.path.exists(base_html_path)

    # If we're in Vercel and base.html doesn't exist, redirect to home with a query parameter
    if is_vercel and not base_html_exists:
        return redirect('/?page=synthara')

    return render_template('synthara.html')

@app.route('/deployment-protection')
def deployment_protection():
    # Check if we're in Vercel environment and if base.html exists
    base_html_path = os.path.join(template_folder, 'base.html')
    base_html_exists = os.path.exists(base_html_path)

    # If we're in Vercel and base.html doesn't exist, redirect to home with a query parameter
    if is_vercel and not base_html_exists:
        return redirect('/?page=deployment-protection')

    return render_template('deployment-protection.html')

@app.route('/api-key')
def api_key():
    # Check if we're in Vercel environment and if base.html exists
    base_html_path = os.path.join(template_folder, 'base.html')
    base_html_exists = os.path.exists(base_html_path)

    # If we're in Vercel and base.html doesn't exist, redirect to home with a query parameter
    if is_vercel and not base_html_exists:
        return redirect('/?page=api-key')

    return render_template('api-key.html')

@app.route('/privacy-policy')
def privacy_policy():
    # Check if we're in Vercel environment and if base.html exists
    base_html_path = os.path.join(template_folder, 'base.html')
    base_html_exists = os.path.exists(base_html_path)

    # If we're in Vercel and base.html doesn't exist, redirect to home with a query parameter
    if is_vercel and not base_html_exists:
        return redirect('/?page=privacy-policy')

    return render_template('privacy-policy.html')

@app.route('/api/prompt-suggestions', methods=['GET'])
def get_prompt_suggestions():
    """Get creative prompt suggestions for the interface."""
    count = request.args.get('count', default=3, type=int)

    # Sample prompts
    sample_prompts = [
        {"text": "Explain quantum computing to a 10-year-old", "category": "Educational", "language": "English"},
        {"text": "Write a short story about a robot discovering emotions", "category": "Creative", "language": "English"},
        {"text": "What are the ethical implications of artificial intelligence?", "category": "Philosophical", "language": "English"},
        {"text": "Describe the process of photosynthesis", "category": "Scientific", "language": "English"},
        {"text": "Create a business plan for a virtual reality startup", "category": "Business", "language": "English"},
        {"text": "Write a poem about the changing seasons", "category": "Poetry", "language": "English"}
    ]

    # Return a subset of sample prompts
    return jsonify({
        'success': True,
        'prompts': sample_prompts[:count],
        'categories': ["Educational", "Creative", "Philosophical", "Scientific", "Business", "Poetry"],
        'languages': ["English", "Spanish", "French", "German", "Chinese", "Japanese"]
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    model_type = request.args.get('type', 'all')

    if model_type == 'text':
        return jsonify({
            'success': True,
            'models': AVAILABLE_TEXT_MODELS
        })
    elif model_type == 'image':
        return jsonify({
            'success': True,
            'models': AVAILABLE_IMAGE_MODELS
        })
    else:
        return jsonify({
            'success': True,
            'text_models': AVAILABLE_TEXT_MODELS,
            'image_models': AVAILABLE_IMAGE_MODELS
        })

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free')
    temperature = data.get('temperature', 0.3)
    max_tokens = data.get('max_tokens', 2048)
    api_key = data.get('apiKey', TOGETHER_API_KEY)

    # Log API key status
    logger.info(f"API request received. Default API key available: {bool(TOGETHER_API_KEY)}")
    logger.info(f"User provided API key: {bool(data.get('apiKey'))}")
    logger.info(f"Final API key available: {bool(api_key)}")

    # Enhanced prompt for natural, conversational text generation
    enhanced_prompt = f"""Write a natural, conversational response to the following prompt.
Use a friendly tone and write in flowing paragraphs without bullet points, bold text, or headings.
Keep the response informative but conversational, as if you're having a casual discussion.

Prompt: {prompt}

Remember to write in a natural, flowing style with regular paragraphs."""

    # Check if API key is available
    if not api_key:
        # Return mock response if API key is not available
        mock_response = f"This is a mock response to your prompt: '{prompt}'\n\n"
        mock_response += "The API key is not configured. Please set the TOGETHER_API_KEY environment variable."
        mock_response += "\n\nDebug info: Default API key available: " + str(bool(TOGETHER_API_KEY))
        mock_response += "\nUser provided API key: " + str(bool(data.get('apiKey')))

        return jsonify({
            'success': True,
            'text': mock_response,
            'mock': True
        })

    try:
        # Make direct API call to Together API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": enhanced_prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            response_data = response.json()
            generated_text = response_data["choices"][0]["message"]["content"]

            return jsonify({
                'success': True,
                'text': generated_text
            })
        else:
            error_message = f"API Error: {response.status_code} - {response.text}"
            logger.error(error_message)

            return jsonify({
                'success': False,
                'text': f"Error calling Together API: {error_message}",
                'error': True
            })

    except Exception as e:
        logger.error(f"Error generating text: {e}")

        # Return a user-friendly error message
        error_response = f"Sorry, there was an error generating text: {str(e)}\n\n"
        error_response += "This could be due to API limits, network issues, or server load. Please try again later."

        return jsonify({
            'success': False,
            'text': error_response,
            'error': True
        })

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', 'black-forest-labs/FLUX.1-dev')
    n = data.get('n', 1)
    size = data.get('size', '1024x1024')
    api_key = data.get('apiKey', TOGETHER_API_KEY)

    logger.info(f"Generating image with prompt: {prompt}")
    logger.info(f"Model: {model}, N: {n}, Size: {size}")

    # Check if API key is available
    if not api_key:
        # Return mock response with placeholder image
        placeholder_image_url = "https://placehold.co/600x400/gray/white?text=API+Key+Missing"

        return jsonify({
            'success': True,
            'message': "API key not configured. Please set the TOGETHER_API_KEY environment variable.",
            'images': [],
            'image_urls': [placeholder_image_url],
            'mock': True
        })

    try:
        # Make direct API call to Together API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size
        }

        response = requests.post(
            "https://api.together.xyz/v1/images/generations",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            response_data = response.json()

            # Process the response
            images = []
            image_urls = []

            # Extract base64 images if available
            if "data" in response_data:
                for item in response_data["data"]:
                    if "b64_json" in item:
                        images.append(item["b64_json"])
                    if "url" in item:
                        image_urls.append(item["url"])

            logger.info(f"Successfully generated {len(images)} images and {len(image_urls)} image URLs")

            return jsonify({
                'success': True,
                'images': images,
                'image_urls': image_urls
            })
        else:
            error_message = f"API Error: {response.status_code} - {response.text}"
            logger.error(error_message)

            # Return a user-friendly error with a placeholder image
            placeholder_image_url = "https://placehold.co/600x400/gray/white?text=Error+Generating+Image"

            return jsonify({
                'success': False,
                'message': f"Error calling Together API: {error_message}",
                'images': [],
                'image_urls': [placeholder_image_url],
                'error': True
            })

    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)

        # Return a user-friendly error with a placeholder image
        placeholder_image_url = "https://placehold.co/600x400/gray/white?text=Error+Generating+Image"

        return jsonify({
            'success': False,
            'message': f"Error generating image: {str(e)}",
            'images': [],
            'image_urls': [placeholder_image_url],
            'error': True
        })
