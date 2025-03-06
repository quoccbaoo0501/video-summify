#!/bin/bash
# This script runs before the Node.js server starts to ensure proper permissions

# Make sure the app can write temporary files
touch /app/temp_input.json
touch /app/temp_output.json
chmod 777 /app/temp_input.json
chmod 777 /app/temp_output.json

# Create directory for temporary files if it doesn't exist
mkdir -p /app/tmp
chmod 777 /app/tmp

# Allow execution of Python scripts
chmod +x /app/*.py

# Set environment variables for proper operation
export PORT=${PORT:-3000}
export NODE_ENV=${NODE_ENV:-production}
export RENDER=true

echo "Starting server with configuration:"
echo "PORT: $PORT"
echo "NODE_ENV: $NODE_ENV"
echo "In Render: $RENDER"

# Execute the command passed to this script (usually npm run start)
exec "$@" 