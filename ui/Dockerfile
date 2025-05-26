# Stage 1: Build the React app
FROM node:18-alpine AS builder
WORKDIR /app

# Define an ARG for the API URL, which can be passed during 'docker build'
ARG REACT_APP_API_URL
# Set it as an ENV variable so 'npm run build' can access it
ENV REACT_APP_API_URL=${REACT_APP_API_URL}

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
# ... rest of Dockerfile ...
