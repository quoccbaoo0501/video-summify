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
RUN pip3 install --upgrade pip
RUN pip3 install --default-timeout=300 --no-cache-dir -r requirements.txt

# Now copy your Node package files
COPY package*.json ./
RUN npm install

# Copy the entrypoint script first to ensure it's available
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Finally, copy everything else
COPY . .

# Build Next.js
RUN npm run build

# Expose port 3000 at runtime
EXPOSE 3000

# Set the entrypoint script to run before the Node.js server
ENTRYPOINT ["/docker-entrypoint.sh"]

# Set command to run the Next.js production server
CMD ["npm", "run", "start"] 