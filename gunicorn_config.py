import multiprocessing

# Bind to 0.0.0.0:8000
bind = "0.0.0.0:8000"

# Number of worker processes
# A good rule of thumb is (2 x number of cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout (in seconds)
timeout = 120

# Access log - records incoming HTTP requests
accesslog = "access.log"

# Error log - records Gunicorn server errors
errorlog = "error.log"

# Log level
loglevel = "info"

# Whether to send Django output to the error log
capture_output = True

# Process name
proc_name = "synthara_ai"

# Preload the application
preload_app = True

# Restart workers after this many requests
max_requests = 1000

# Restart workers after this many seconds
max_requests_jitter = 50
