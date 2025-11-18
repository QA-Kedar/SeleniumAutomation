#!/bin/bash
set -e

# Debug: Show environment variables
echo "Environment variables:"
env | grep PORT || echo "PORT not set"

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=5000
    echo "PORT was not set, using default: 5000"
else
    echo "PORT is set to: $PORT"
fi

echo "Starting application on port $PORT..."

# Start gunicorn
exec gunicorn --worker-class eventlet -w 1 --bind "0.0.0.0:${PORT}" app:app
EOF