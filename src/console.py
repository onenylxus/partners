# File: console.py
# Summary: Runs the interactive terminal UI and forwards prompts to selected containers.

from typing import Any
import requests
from command import handle_command
from rich.console import Console
from manager import list_containers

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
        output = getattr(result, "output")
    else:
        output = result

    if isinstance(output, (bytes, bytearray)):
        try:
            output = output.decode("utf-8", errors="replace")
        except Exception:
            output = str(output)

    return "" if output is None else str(output)


def interactive_console(configured_entries: list[dict[str, str]]) -> None:
    """Run an interactive loop with config-ordered coordinator routing."""

    order = {entry.get("name", ""): idx for idx, entry in enumerate(configured_entries)}
    briefs = {
        entry.get("name", ""): entry.get("brief", "") for entry in configured_entries
    }

    def build_running_nodes() -> list[dict[str, str]]:
        containers = list_containers()
        nodes = []
        for c in containers:
            try:
                c.reload()
                attrs = getattr(c, "attrs", {})
                ports = attrs.get("NetworkSettings", {}).get("Ports", {})
                mapping = ports.get("8080/tcp")
                if (
                    mapping
                    and isinstance(mapping, list)
                    and mapping[0].get("HostPort")
                    and getattr(c, "status", "") == "running"
                ):
                    name = getattr(c, "name", None) or attrs.get("Name", "").lstrip("/")
                    nodes.append(
                        {
                            "name": name,
                            "host_port": mapping[0]["HostPort"],
                            "brief": briefs.get(name, ""),
                        }
                    )
            except Exception:
                continue
        if order:
            nodes.sort(key=lambda n: order.get(n["name"], len(order)))
        return nodes

    initial_nodes = build_running_nodes()
    if not initial_nodes:
        print_tagged(
            "system",
            "bold yellow",
            "No running containers with mapped 8080/tcp ports available.",
        )
        return

    lines = ["Available containers:"]
    for idx, node in enumerate(initial_nodes):
        lines.append(f"  [{idx}] {node['name']} (port: {node['host_port']})")
    print_tagged("system", "bold cyan", "\n".join(lines))

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
                        break
                continue

            # Rebuild each time to keep runtime state and ports fresh.
            nodes = build_running_nodes()
            if not nodes:
                print_tagged("system", "bold yellow", "No running containers available")
                continue

            if len(nodes) == 1:
                target_node = nodes[0]
                route_reason = "single container; routing skipped"
                print_tagged(
                    "system",
                    "bold cyan",
                    "Sending prompt",
                )
            else:
                coordinator = nodes[0]
                candidates = nodes[1:]
                print_tagged(
                    "system",
                    "bold cyan",
                    "Sending prompt to coordinator",
                )

                if not candidates:
                    target_node = coordinator
                    route_reason = "no secondary container found; using coordinator"
                else:
                    try:
                        route_resp = requests.post(
                            f"http://localhost:{coordinator['host_port']}/route",
                            json={
                                "input": user_input,
                                "candidates": [
                                    {
                                        "name": n["name"],
                                        "brief": n.get("brief", ""),
                                    }
                                    for n in candidates
                                ],
                            },
                            timeout=60,
                        )
                        route_resp.raise_for_status()
                        route_data = route_resp.json()
                        target_name = str(route_data.get("target", "")).strip()
                        route_reason = str(route_data.get("reason", "model-selected"))
                        target_node = next(
                            (n for n in candidates if n["name"] == target_name),
                            candidates[0],
                        )
                    except Exception as exc:
                        target_node = candidates[0]
                        route_reason = (
                            f"route request failed; fallback first candidate ({exc})"
                        )

            target_idx = next(
                (i for i, n in enumerate(nodes) if n["name"] == target_node["name"]),
                -1,
            )
            if len(nodes) > 1:
                coordinator_idx = 0
                coordinator_tag = f"[{coordinator_idx}] {coordinator['name']}"
                print_tagged(
                    coordinator_tag,
                    "bold magenta",
                    route_reason,
                )
                print_tagged(
                    "system",
                    "bold cyan",
                    f"Prompt passed to [{target_idx}] {target_node['name']}",
                )

            try:
                resp = requests.post(
                    f"http://localhost:{target_node['host_port']}/exec",
                    json={
                        "input": user_input,
                        "system": target_node.get("brief", "") or None,
                    },
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
            tag = f"[{target_idx}] {target_node['name']}"
            print_tagged(tag, "bold magenta", output)

    except KeyboardInterrupt:
        print_tagged("system", "bold yellow", "Console interrupted.")
