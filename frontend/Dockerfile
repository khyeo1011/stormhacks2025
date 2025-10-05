# Development Dockerfile for React + TypeScript + Vite frontend
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application

EXPOSE 5173

# Start Vite with hot reload and allow external access
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
# FOR PROD

# RUN npm run build

# Stage 2: Serve the application with nginx


# Copy nginx configuration (optional - using default for now)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
# FROM nginx:alpine AS production

# # Copy built assets from builder stage
# COPY --from=builder /app/dist /usr/share/nginx/html

# # Start nginx
# CMD ["nginx", "-g", "daemon off;"]
