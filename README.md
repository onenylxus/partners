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
		{ "name": "router", "model": "gpt-4.1-mini" },
		{
			"name": "research",
			"model": "gpt-4.1-mini",
			"brief": "Literature review, references, and fact-checking"
		},
		{
			"name": "coding",
			"model": "gpt-4.1",
			"brief": "Code implementation, debugging, and refactoring"
		}
	]
}
```

Notes:

- If multiple containers exist, the first container in config is the coordinator and the rest are candidates.
- If only one container is configured, routing is skipped.
- `brief` is optional and intended for non-coordinator containers.
- When a target container has `brief`, it is sent as a system message before the user prompt.

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
3. Enter prompts in the CLI.
4. If multiple containers are running, the first configured container decides which other container should handle each prompt.
5. If only one container exists, prompt routing is skipped and prompts go directly to that container.

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
  - Calls the first configured container /route when multiple containers are available.
  - Sends prompts to POST /exec on the chosen target (or direct target in single mode).
  - Passes target `brief` as system message when available.

- src/command.py
  - Handles slash-prefixed console commands.
  - Loads and returns help text from res/help.txt.

- src/container.py
  - FastAPI app running inside each container.
  - Exposes:
    - GET /health for health checks.
    - POST /exec for prompt processing (supports optional system message).
    - POST /route for master routing decisions.
  - Uses OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL.

### Request path

1. User enters prompt in console.
2. If multiple containers are running, host sends prompt + candidate names to the first configured container /route.
3. Coordinator selects the target container.
4. Host sends HTTP POST to selected target at localhost:<mapped_port>/exec.
5. Container calls OpenAI chat completions API.
6. Response text is returned to host and displayed in console.
