# Use an explicit LTS Node Alpine footprint for fast, secure builds
FROM node:22-alpine

WORKDIR /app

# Copy package configurations and install node modules
COPY package*.json /app/
RUN npm install

# Copy the frontend application source code
COPY . /app/

# Expose Vite's default network development server port
EXPOSE 5173

# Launch Vite's dev server bound to all local network interfaces for container mapping
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]