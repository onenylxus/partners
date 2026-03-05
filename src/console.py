from typing import Any
import requests
from command import handle_command
from rich.console import Console
from rich.panel import Panel

# Rich console for colored prompts and output
console = Console()


def print_tagged(tag: str, style: str, message: str) -> None:
    """Print tagged output and indent multiline content from the second line."""
    text = "" if message is None else str(message)
    lines = text.splitlines()

    if not lines:
        formatted = ""
    elif len(lines) == 1:
        formatted = lines[0]
    else:
        indent = " " * (len(tag) + 1)  # +1 for the space after the tag
        formatted = lines[0] + "\n" + "\n".join(f"{indent}{line}" for line in lines[1:])

    console.print(f"[{style}]{tag}[/{style}] {formatted}", highlight=False)


def print_header(app_name: str, version: str) -> None:
    """Print a simple application header with name and version."""
    # Single-line system message consistent with other system outputs
    print_tagged("system", "bold cyan", f"{app_name} v{version}")


def format_exec_result(result: Any) -> str:
    """Normalize docker exec_run result to a string."""
    output = None
    if isinstance(result, tuple) and len(result) == 2:
        _, output = result
    elif hasattr(result, "output"):
        output = result.output
    else:
        output = result

    if isinstance(output, (bytes, bytearray)):
        try:
            output = output.decode("utf-8", errors="replace")
        except Exception:
            output = str(output)

    return "" if output is None else str(output)


def interactive_console(target) -> None:
    """Run an interactive loop that sends input to the container and prints output.

    If `target` is falsy the function will print an explanatory message and return.
    """
    if not target:
        print_tagged(
            "system",
            "bold yellow",
            "No container available to run the echo script.",
        )
        return

    # Ensure we have up-to-date container information and a mapped host port
    host_port = None
    try:
        # refresh attributes
        target.reload()
        ports = getattr(target, "attrs", {}).get("NetworkSettings", {}).get("Ports", {})
        mapping = ports.get("8080/tcp")
        if mapping and isinstance(mapping, list) and mapping[0].get("HostPort"):
            host_port = mapping[0]["HostPort"]
    except Exception:
        host_port = None

    if not host_port:
        print_tagged(
            "system",
            "bold yellow",
            "Target container has no 8080/tcp host port mapped. Ensure manager publishes the port.",
        )
        return

    try:
        while True:
            try:
                user_input = console.input("[bold blue]user[/bold blue] ")
            except EOFError:
                break
            if not user_input:
                continue

            # commands start with '/'
            if user_input.startswith("/"):
                handled, should_exit, command_message = handle_command(user_input)
                if handled:
                    if command_message:
                        print_tagged("system", "bold cyan", command_message.rstrip())
                    if should_exit:
                        return
                    continue

            try:
                resp = requests.post(
                    f"http://localhost:{host_port}/exec",
                    json={"input": user_input},
                    timeout=60,
                )
                resp.raise_for_status()
                data = resp.json()
                output = data.get("output", "")
            except Exception as exc:
                print_tagged("system", "bold yellow", f"HTTP request failed: {exc}")
                break

            # Prefix container output with a styled label. Preserve multiline output.
            if output is None:
                output = ""
            # Print label + content
            print_tagged("container", "bold magenta", output)

    except KeyboardInterrupt:
        print_tagged("system", "bold yellow", "Interrupted by user")
