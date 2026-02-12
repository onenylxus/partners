#!/bin/bash

# Check if Python 3 is installed, install if missing
if ! which python3 &>/dev/null; then
  echo "Installing Python..."
  sudo apt-get update
  sudo apt-get install -y python3 python3-full python3-pip python3-dev
  echo "Python installed successfully"
else
  echo "Python is already installed"
fi

# Check if Docker is installed, install if missing
if ! which docker &>/dev/null; then
  echo "Installing Docker..."
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
pip3 install -r requirements_main.txt

# Activate virtual environment and run main application
echo "Activating virtual environment and starting application..."
source .venv/bin/activate
python3 src/main.py
