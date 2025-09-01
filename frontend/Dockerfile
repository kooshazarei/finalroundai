FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Set environment variable for hot reload
ENV CHOKIDAR_USEPOLLING=true

# Run in development mode with hot reload
CMD ["npm", "start"]
