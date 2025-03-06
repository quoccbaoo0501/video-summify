# Use an official Node 18 image as the base.
# We choose Debian Bullseye for an easy 'apt-get' to install Python.
FROM node:18-bullseye

# Install Python & pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Create an /app directory (and switch to it)
WORKDIR /app

# Copy requirements.txt before installing
COPY requirements.txt ./requirements.txt

# Upgrade pip and install dependencies
# Note: Older pip version doesn't support --root-user-action
RUN pip3 install --upgrade pip
RUN pip3 install --default-timeout=300 --no-cache-dir -r requirements.txt

# Verify Python packages are installed correctly
RUN python3 -c "import youtube_transcript_api; import requests; import bs4; print('Python packages verified')"

# Now copy your Node package files
COPY package*.json ./
RUN npm install

# Copy the entrypoint script first to ensure it's available
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Finally, copy everything else
COPY . .

# Set environment variables
ENV NODE_ENV=production
ENV RENDER=true
ARG PORT=3000
ENV PORT=${PORT}

# Build Next.js
RUN npm run build

# Expose the port that will be used by the application
EXPOSE ${PORT}

# Set the entrypoint script to run before the Node.js server
ENTRYPOINT ["/docker-entrypoint.sh"]

# Set command to run the Next.js production server with the custom server
CMD ["npm", "run", "start"] 