# partners

Asynchronous projct development using multiple AI agents

> [!WARNING]
> This project is completely driven by artificial intelligence.
> By using this repository, you agree to accept the risks and side effects that may be produced from code genration.

## Setup

### Prerequisites

- Linux or macOS shell environment
- Python 3 with venv support
- Docker engine and docker CLI
- sudo access (used by partners.sh to start Docker)

### 1. Clone and enter the repository

```bash
git clone https://github.com/onenylxus/partners.git
cd partners
```

### 2. Configure environment variables

Create a .env file in the repository root:

```bash
cp .env.example .env
```

If you do not have .env.example, create .env manually with at least:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4.1-mini
```

Optional:

```env
DEV=1
```

When DEV=1 is present in .env, partners.sh always rebuilds the partners-agent Docker image.

### 3. Configure partner containers

Create containers.json from the example and define your agent containers:

```bash
cp containers.json.example containers.json
```

Example format:

```json
{
	"version": 1,
	"containers": [
		{ "name": "research", "model": "gpt-4.1-mini" },
		{ "name": "coding", "model": "gpt-4.1" }
	]
}
```

## Usage

### Recommended start command

```bash
./partners.sh
```

What this script does:

- Verifies Python and Docker are installed
- Starts Docker service
- Builds partners-agent:latest if needed
- Creates .venv and installs requirements_main.txt
- Launches src/main.py

### Interactive console flow

After startup:

1. Containers from containers.json are created and started.
2. You are shown available containers with mapped host ports.
3. Select a container index (or press Enter for 0).
4. Enter prompts to send to that container's HTTP endpoint.

Supported slash commands:

- /help: Show help text
- /list: List managed containers with status and mapped port
- /exit: Exit the console

On exit, all managed containers are stopped and removed.

## Architecture

### High-level design

The project has two runtimes:

- Host runtime: orchestrates Docker containers and provides the terminal UI.
- Container runtime: runs a FastAPI service that calls the OpenAI chat API.

### Main components

- src/main.py
  - Application entry point.
  - Reads containers.json.
  - Creates, starts, then later stops and removes containers.
  - Starts interactive console session.

- src/manager.py
  - Docker lifecycle layer.
  - Creates containers from partners-agent:latest.
  - Starts, stops, lists, and removes containers.

- src/console.py
  - Interactive terminal loop with rich output.
  - Lets user pick a target container.
  - Sends prompts to POST /exec on the selected container.

- src/command.py
  - Handles slash-prefixed console commands.
  - Loads and returns help text from res/help.txt.

- src/container.py
  - FastAPI app running inside each container.
  - Exposes:
    - GET /health for health checks.
    - POST /exec for prompt processing.
  - Uses OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL.

### Request path

1. User enters prompt in console.
2. Host sends HTTP POST to selected container at localhost:<mapped_port>/exec.
3. Container calls OpenAI chat completions API.
4. Response text is returned to host and displayed in console.
