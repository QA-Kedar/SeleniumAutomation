#!/bin/bash

# Set default port if not provided
export PORT=${PORT:-5000}

echo "Starting application on port $PORT..."

# Start gunicorn
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app