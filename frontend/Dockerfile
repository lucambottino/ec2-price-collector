# Dockerfile for Next.js
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the Next.js application
RUN npm run build

# Expose the Next.js port
EXPOSE 3001

# Start the Next.js application
CMD ["npm", "run", "start"]
