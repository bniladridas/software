
# Synthara AI  
**Create with intelligence.**  

[![Synthara AI](https://img.shields.io/badge/Synthara_AI-7C3AED.svg?style=for-the-badge&color=white&labelColor=white)](https://github.com/bniladridas/synthara-ai) [![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org) [![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/) [![Together AI](https://img.shields.io/badge/Together_AI-API-6366f1.svg?style=for-the-badge)](https://www.together.ai) [![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)](https://vercel.com) [![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)  

Synthara AI is a web application that brings text and image generation to life, powered by Together AI’s advanced models. Simple. Powerful. Yours to explore.  

![Synthara AI Usage](static/images/usage.png)  

## Get Started  

Bring your ideas to life in moments.  

```bash
# Clone the repository
git clone https://github.com/bniladridas/software.git
cd software

# Set up your environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install together Flask==2.0.1 Werkzeug==2.0.1

# Add your API key
echo "TOGETHER_API_KEY=your_api_key_here" > .env

# Launch the app
python simple_app.py
```

Open [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser. Watch your app evolve with every code change, thanks to debug mode.  

Expect to see:  
```
INFO:__main__:Together API client initialized successfully
* Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
```

## What You Can Do  

- **Generate Text**: Craft stories, ideas, or answers with models like Llama-3.3-70B, DeepSeek-R1-70B, or Llama-4-Maverick-17B.  
- **Create Images**: Transform prompts into stunning visuals with the FLUX.1-dev model.  
- **Stay Simple**: Enjoy a clean, intuitive interface.  
- **Unlock Premium**: Use your Together AI API key for exclusive models.  

### How to Use  

**Text Generation**  
1. Choose a model.  
2. Write your prompt.  
3. Hit "Generate" or press Enter.  
4. Copy your text with a single click.  

**Image Generation**  
1. Select an image model.  
2. Describe your vision.  
3. Click "Generate" or press Enter.  
4. See your image come to life.  

**Premium Models**  
1. Visit the API Key Setup page.  
2. Get your Together AI API key.  
3. Enter it in the form—it’s stored securely in your browser.  
4. Access premium models like Llama-4-Maverick-17B.  

## Deploy with Ease  

Ready to share your creation? Deploy on Vercel:  

1. Fork or clone this repository.  
2. Link it to Vercel.  
3. Set the `TOGETHER_API_KEY` environment variable.  
4. Deploy.  

Learn more in [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md).  

## Environment  

- `TOGETHER_API_KEY`: Your key to Together AI’s power (required).  

## Created By  

**Niladri Das**  
[GitHub](https://github.com/bniladridas)  

## License  

© 2025 Synthara AI  
Licensed under the [Apache License, Version 2.0](LICENSE).  
