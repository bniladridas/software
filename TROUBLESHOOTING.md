# Troubleshooting Guide for Synthara AI

This guide will help you troubleshoot common issues when setting up and running the Synthara AI application.

## Common Issues and Solutions

### 1. Python Command Not Found

**Issue**: When running `python -m venv .venv`, you get an error like `bash: python: command not found`.

**Solution**: 
- Try using `python3` instead: `python3 -m venv .venv`
- If that doesn't work, ensure Python is installed on your system:
  - For macOS: `brew install python`
  - For Ubuntu/Debian: `sudo apt install python3`
  - For Windows: Download from [python.org](https://www.python.org/downloads/)

### 2. Module 'together' Not Found

**Issue**: When running the application, you get an error like `ModuleNotFoundError: No module named 'together'`.

**Solution**:
1. Make sure you've activated the virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
   Your command prompt should show `(.venv)` at the beginning.

2. Install the 'together' package:
   ```bash
   pip install together
   ```

3. If you still have issues, try installing with specific version:
   ```bash
   pip install together==1.4.6
   ```

### 3. API Key Issues

**Issue**: The application fails with an error about missing API key.

**Solution**:
1. Make sure you have a `.env` file in the root directory with your Together AI API key:
   ```
   TOGETHER_API_KEY=your_api_key_here
   ```

2. You can get an API key by signing up at [Together AI](https://www.together.ai).

3. If you have the `.env` file but still get errors, check that the `python-dotenv` package is installed:
   ```bash
   pip install python-dotenv
   ```

### 4. Script Not Found or Permission Issues

**Issue**: When trying to run scripts like `./start_simple.sh`, you get "No such file or directory" or permission errors.

**Solution**:
1. Make sure you're in the correct directory:
   ```bash
   cd /path/to/software
   ```

2. Check if the script has execute permissions:
   ```bash
   ls -la start_simple.sh
   ```
   If it doesn't show `x` permissions, add them:
   ```bash
   chmod +x start_simple.sh
   ```

3. Try running with bash explicitly:
   ```bash
   bash start_simple.sh
   ```

## Step-by-Step Guide to Run the Application

Here's a foolproof way to run the application:

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/bniladridas/software.git
   cd software
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   
   # Activate it
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install all dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install together
   pip install Flask==2.0.1 Werkzeug==2.0.1
   ```

4. **Set up your API key**:
   ```bash
   # Create .env file if it doesn't exist
   echo "TOGETHER_API_KEY=your_api_key_here" > .env
   ```
   Replace `your_api_key_here` with your actual Together AI API key.

5. **Run the application**:
   ```bash
   # Make sure you're in the software directory
   python simple_app.py
   ```

6. **Access the application**:
   Open your browser and go to: http://127.0.0.1:5001

## Verifying the Application is Running

When the application starts successfully, you should see output similar to:
```
INFO:__main__:Together API client initialized successfully
* Serving Flask app 'simple_app' (lazy loading)
* Environment: production
  WARNING: This is a development server. Do not use it in a production deployment.
* Debug mode: on
INFO:werkzeug: * Running on http://127.0.0.1:5001/ (Press CTRL+C to quit)
```

## Still Having Issues?

If you're still experiencing problems:

1. Check that your Python version is 3.9 or higher:
   ```bash
   python --version
   ```

2. Try running with verbose logging:
   ```bash
   PYTHONVERBOSE=1 python simple_app.py
   ```

3. Check for any error messages in the console output.

4. Make sure all required ports are available (especially port 5001).

5. If you're behind a corporate firewall or proxy, you might need to configure your network settings to allow API calls to Together AI.
