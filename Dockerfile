FROM ubuntu:latest

WORKDIR /app
COPY requirements_container.txt requirements.txt

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  nano curl git build-essential \
  python3 python3-full python3-pip python3-dev
RUN rm -rf /var/lib/apt/lists/*

RUN python3 -m venv .venv

RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
