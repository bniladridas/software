#!/usr/bin/env python3
"""
Production server script for Synthara AI application.
This script sets up and runs a Gunicorn server with proper configuration.
"""

import os
import sys
import argparse
import subprocess
import signal
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("production_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("production_server")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Synthara AI production server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes")
    parser.add_argument("--timeout", type=int, default=120, help="Worker timeout in seconds")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error", "critical"],
                        help="Log level")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    return parser.parse_args()

def kill_existing_gunicorn():
    """Kill any existing Gunicorn processes."""
    try:
        logger.info("Checking for existing Gunicorn processes...")
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        time.sleep(1)  # Give processes time to terminate
        logger.info("Killed existing Gunicorn processes")
    except Exception as e:
        logger.warning(f"Error killing existing Gunicorn processes: {e}")

def start_server(args):
    """Start the Gunicorn server with the specified arguments."""
    bind = f"{args.host}:{args.port}"
    
    # Build the command
    cmd = [
        "gunicorn",
        "--bind", bind,
        "--workers", str(args.workers),
        "--timeout", str(args.timeout),
        "--log-level", args.log_level,
        "--access-logfile", "access.log",
        "--error-logfile", "error.log",
    ]
    
    # Add reload flag if specified
    if args.reload:
        cmd.append("--reload")
    
    # Add the application
    cmd.append("simple_app:app")
    
    logger.info(f"Starting Gunicorn with command: {' '.join(cmd)}")
    
    try:
        # Start the server
        process = subprocess.Popen(cmd)
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            process.terminate()
            process.wait(timeout=5)
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait for the process to complete
        logger.info(f"Server running at http://{bind}")
        process.wait()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
        process.terminate()
        process.wait(timeout=5)
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    args = parse_args()
    
    # Ensure we're in a virtual environment
    if not os.environ.get("VIRTUAL_ENV"):
        logger.warning("Not running in a virtual environment. This is not recommended for production.")
    
    # Kill any existing Gunicorn processes
    kill_existing_gunicorn()
    
    # Start the server
    start_server(args)

if __name__ == "__main__":
    main()
