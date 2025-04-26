# Running Synthara AI in Production

This document provides instructions for running the Synthara AI application in a production environment.

## Prerequisites

- Python 3.9 or higher
- Virtual environment
- Gunicorn
- Together AI API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bniladridas/software.git
   cd software
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. Create a `.env` file with your Together AI API key:
   ```bash
   echo "TOGETHER_API_KEY=your_api_key_here" > .env
   ```

## Running the Production Server

### Option 1: Using the Production Server Script

The `production_server.py` script provides a convenient way to run the application in production:

```bash
./production_server.py
```

This script supports various command-line options:

- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--workers`: Number of worker processes (default: 4)
- `--timeout`: Worker timeout in seconds (default: 120)
- `--log-level`: Log level (default: info)
- `--reload`: Enable auto-reload on code changes

Example:
```bash
./production_server.py --port 8080 --workers 8 --log-level warning
```

### Option 2: Using Gunicorn Directly

You can also run Gunicorn directly:

```bash
gunicorn --bind 0.0.0.0:8000 --workers 4 simple_app:app
```

For more advanced configuration:

```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --timeout 120 \
         --access-logfile access.log \
         --error-logfile error.log \
         --log-level info \
         simple_app:app
```

### Option 3: Using Systemd (Linux)

For a more robust setup on Linux servers, you can use systemd:

1. Edit the `synthara-ai.service` file to update paths:
   ```bash
   nano synthara-ai.service
   ```

2. Copy the service file to systemd:
   ```bash
   sudo cp synthara-ai.service /etc/systemd/system/
   ```

3. Reload systemd and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start synthara-ai
   sudo systemctl enable synthara-ai
   ```

4. Check the status:
   ```bash
   sudo systemctl status synthara-ai
   ```

## Nginx Configuration (Recommended)

For production deployments, it's recommended to use Nginx as a reverse proxy:

1. Install Nginx:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. Create a site configuration:
   ```bash
   sudo nano /etc/nginx/sites-available/synthara-ai
   ```

3. Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static/ {
           alias /path/to/synthara-ai/static/;
       }
   }
   ```

4. Enable the site and restart Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/synthara-ai /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

## SSL Configuration (Recommended)

For secure HTTPS connections, you can use Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your_domain.com
```

## Monitoring

For production monitoring, consider using tools like:

- Prometheus for metrics
- Grafana for visualization
- Sentry for error tracking

## Troubleshooting

If you encounter issues:

1. Check the logs:
   ```bash
   tail -f error.log
   tail -f access.log
   ```

2. Verify the application is running:
   ```bash
   ps aux | grep gunicorn
   ```

3. Test the application directly:
   ```bash
   curl http://localhost:8000/
   ```

4. Check system resources:
   ```bash
   top
   free -m
   df -h
   ```
