import os
import base64
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dotenv import load_dotenv
from together import Together

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Available models
AVAILABLE_TEXT_MODELS = [
    {"id": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "name": "Llama-3.3-70B"},
    {"id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", "name": "DeepSeek-R1-70B"},
    {"id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "name": "Llama-4-Maverick-17B", "requires_api_key": True}
]

AVAILABLE_IMAGE_MODELS = [
    {"id": "black-forest-labs/FLUX.1-dev", "name": "FLUX.1-dev", "requires_api_key": True}
]

# Initialize Together client
api_key = os.getenv("TOGETHER_API_KEY")
if api_key:
    client = Together(api_key=api_key)
    logger.info("Together API client initialized successfully")
else:
    client = None
    logger.warning("TOGETHER_API_KEY not found in environment variables. Some features may not work.")

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
    api_key = data.get('apiKey', None)

    # Enhanced prompt for natural, conversational text generation
    enhanced_prompt = f"""Write a natural, conversational response to the following prompt.
Use a friendly tone and write in flowing paragraphs without bullet points, bold text, or headings.
Keep the response informative but conversational, as if you're having a casual discussion.

Prompt: {prompt}

Remember to write in a natural, flowing style with regular paragraphs."""

    try:
        # If using Llama-4-Maverick with custom API key
        if model == "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8" and api_key:
            logger.info("Using custom API key for Llama-4-Maverick model")
            # Create a custom client with the user's API key
            custom_client = Together(api_key=api_key)

            response = custom_client.chat.completions.create(
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                messages=[{"role": "user", "content": enhanced_prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:
            # Check if default client is initialized
            if client is None:
                return jsonify({
                    'success': False,
                    'error': "API key not configured. Please set the TOGETHER_API_KEY environment variable."
                }), 500

            # Use the default client
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": enhanced_prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )

        generated_text = response.choices[0].message.content

        return jsonify({
            'success': True,
            'text': generated_text
        })
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    model = data.get('model', 'black-forest-labs/FLUX.1-dev')
    n = data.get('n', 1)
    size = data.get('size', '1024x1024')
    api_key = data.get('apiKey', None)

    logger.info(f"Generating image with prompt: {prompt}")
    logger.info(f"Model: {model}, N: {n}, Size: {size}")

    try:
        # If using FLUX.1-dev with custom API key
        if model == "black-forest-labs/FLUX.1-dev" and api_key:
            logger.info("Using custom API key for FLUX.1-dev model")
            # Create a custom client with the user's API key
            custom_client = Together(api_key=api_key)

            logger.debug("Calling Together API for image generation with custom API key")
            response = custom_client.images.generate(
                prompt=prompt,
                model=model,
                n=n,
                size=size
            )
        else:
            # Check if default client is initialized
            if client is None:
                return jsonify({
                    'success': False,
                    'error': "API key not configured. Please set the TOGETHER_API_KEY environment variable."
                }), 500

            logger.debug("Calling Together API for image generation with default API key")
            response = client.images.generate(
                prompt=prompt,
                model=model,
                n=n,
                size=size
            )

        # Process the response
        images = []
        image_urls = []

        # Extract base64 images if available
        if hasattr(response, 'data') and response.data:
            for item in response.data:
                if hasattr(item, 'b64_json') and item.b64_json:
                    images.append(item.b64_json)
                if hasattr(item, 'url') and item.url:
                    image_urls.append(item.url)

        logger.info(f"Successfully generated {len(images)} images and {len(image_urls)} image URLs")

        return jsonify({
            'success': True,
            'images': images,
            'image_urls': image_urls
        })
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Ensure the app is configured for production when deployed
app.debug = False
app.config['PROPAGATE_EXCEPTIONS'] = True

# For Vercel deployment, we need to export the app variable
# This is what Vercel will use as the entry point
# The app variable is already defined above

# Only run the development server when this file is executed directly
if __name__ == '__main__':
    app.run(debug=True, port=5001)
