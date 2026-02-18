#!/bin/bash

# Check if Python 3 is installed
if ! which python3 &> /dev/null; then
  echo "Error: Python 3 is not installed"
  exit 1
fi

# Check if Docker is installed
if ! which docker &> /dev/null; then
  echo "Error: Docker is not installed"
  exit 1
fi

# Start Docker service
echo "Starting Docker service..."
sudo systemctl start docker

# Build Docker image if it doesn't exist
if [ -z "$(docker images -q partners-agent:latest)" ]; then
  echo "Building Docker image 'partners-agent'..."
  sudo docker build -t partners-agent .
fi

# Verify Docker image was built successfully
if [ -z "$(docker images -q partners-agent:latest)" ]; then
  echo "Error: Docker image 'partners-agent' not found"
  exit 1
fi

echo "Docker image 'partners-agent' ready"

# Create Python virtual environment if it doesn't exist
if [ ! -d "./.venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
  echo "Virtual environment created"
else
  echo "Virtual environment already exists"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
./.venv/bin/pip3 install -r requirements_main.txt

# Run main application with virtual environment's Python interpreter
echo "Starting application..."
./.venv/bin/python3 src/main.py
