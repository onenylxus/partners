FROM ubuntu:latest

WORKDIR /app
COPY .env .env
COPY requirements_container.txt requirements.txt
COPY src/container.py container.py

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
  nano curl git build-essential \
  python3 python3-full python3-pip python3-dev
RUN rm -rf /var/lib/apt/lists/*

RUN python3 -m venv .venv

RUN .venv/bin/pip install --upgrade pip
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3", "/app/container.py" ]
