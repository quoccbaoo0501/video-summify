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

# Execute the command passed to this script (usually npm run start)
exec "$@" 