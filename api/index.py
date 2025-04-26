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

app = Flask(__name__,
            template_folder=template_folder,  # Specify the template folder
            static_folder=static_folder)       # Specify the static folder

# Add explicit route for static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(static_folder, path)

# Available models
AVAILABLE_TEXT_MODELS = [
    {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "name": "Llama-3.3-70B"},
    {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", "name": "DeepSeek-R1-70B"},
    {"id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "name": "Llama-4-Maverick-17B", "requires_api_key": True}
]

AVAILABLE_IMAGE_MODELS = [
    {"id": "black-forest-labs/FLUX.1-dev", "name": "FLUX.1-dev"}
]

# Get API key from environment - try multiple methods
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY and "TOGETHER_API_KEY" in os.environ:
    TOGETHER_API_KEY = os.environ["TOGETHER_API_KEY"]

# Try loading from .env file directly if not found in environment
if not TOGETHER_API_KEY:
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        if key == "TOGETHER_API_KEY":
                            TOGETHER_API_KEY = value
                            break
    except Exception as e:
        logger.error(f"Error loading API key from .env file: {e}")

logger.info(f"API Key available: {bool(TOGETHER_API_KEY)}")

# Add a debug route to check environment variables
@app.route('/debug/env')
def debug_env():
    env_vars = {
        "TOGETHER_API_KEY_SET": bool(TOGETHER_API_KEY),
        "PYTHON_VERSION": sys.version,
        "ENV_VARS": {k: (v if k != "TOGETHER_API_KEY" else "REDACTED") for k, v in os.environ.items()},
        "STATIC_FOLDER": static_folder,
        "TEMPLATE_FOLDER": template_folder
    }
    return jsonify(env_vars)

# Add a route to test the API key
@app.route('/debug/api-key-test')
def api_key_test():
    if not TOGETHER_API_KEY:
        return jsonify({
            "success": False,
            "message": "API key not found in environment variables"
        })

    try:
        # Make a simple API call to test the key
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            "https://api.together.xyz/v1/models",
            headers=headers
        )

        if response.status_code == 200:
            return jsonify({
                "success": True,
                "message": "API key is valid",
                "status_code": response.status_code,
                "models_count": len(response.json().get("data", []))
            })
        else:
            return jsonify({
                "success": False,
                "message": "API key validation failed",
                "status_code": response.status_code,
                "response": response.text
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error testing API key: {str(e)}"
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/synthara')
def synthara():
    return render_template('synthara.html')

@app.route('/deployment-protection')
def deployment_protection():
    return render_template('deployment-protection.html')

@app.route('/api-key')
def api_key():
    return render_template('api-key.html')

@app.route('/privacy-policy')
def privacy_policy():
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
