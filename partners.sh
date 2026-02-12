#!/bin/bash

# Parse flags
FORCE=0
while getopts ":f" opt; do
  case $opt in
    f)
      FORCE=1
      ;;
    \?)
      echo "Unknown option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Check if Python 3 is installed, install (or force-install) if requested
if [ "$FORCE" -eq 1 ] || ! which python3 &> /dev/null; then
  if [ "$FORCE" -eq 1 ]; then
    echo "Force flag detected: reinstalling Python packages..."
  else
    echo "Installing Python..."
  fi
  sudo apt-get update
  sudo apt-get install -y python3 python3-full python3-pip python3-dev
  echo "Python installed successfully"
else
  echo "Python is already installed"
fi

# Check if Docker is installed, install (or force-install) if requested
if [ "$FORCE" -eq 1 ] || ! which docker &> /dev/null; then
  if [ "$FORCE" -eq 1 ]; then
    echo "Force flag detected: reinstalling Docker..."
  else
    echo "Installing Docker..."
  fi
  sudo apt-get update
  sudo apt-get install -y ca-certificates curl
  sudo install -m 0755 -d /etc/apt/keyrings
  sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc

  sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

  sudo apt-get update
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  echo "Docker installed successfully"
else
  echo "Docker is already installed"
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
