# File: command.py
# Summary: Handles slash commands for the interactive console.

from typing import Optional, Tuple
from pathlib import Path
import json
import os

from manager import list_containers


def _configured_container_order() -> dict[str, int]:
    """Return configured lowercase container name -> index order."""
    config_path = os.environ.get("CONTAINERS_CONFIG", "containers.json")
    try:
        with open(config_path, "r") as f:
            data = json.load(f)
        entries = data.get("containers", []) if isinstance(data, dict) else []
        names = [str(e.get("name", "")).strip() for e in entries if isinstance(e, dict)]
        names = [n for n in names if n]
        return {name.lower(): idx for idx, name in enumerate(names)}
    except Exception:
        return {}


def _format_containers_list() -> str:
    """Return a table of containers with index, name, status and port."""
    try:
        containers = list_containers()
    except Exception as e:
        return f"Failed to list containers: {e}"

    order = _configured_container_order()
    if order:

        def _container_name(c: object) -> str:
            return (getattr(c, "name", None) or "") or getattr(c, "attrs", {}).get(
                "Name", ""
            ).lstrip("/")

        containers.sort(
            key=lambda c: (
                order.get(_container_name(c).lower(), len(order)),
                _container_name(c).lower(),
            )
        )

    # Build rows of data
    rows = []
    for idx, c in enumerate(containers):
        try:
            c.reload()
        except Exception:
            pass

        name = getattr(c, "name", None) or ""
        if not name:
            name = getattr(c, "attrs", {}).get("Name", "").lstrip("/")

        status_raw = getattr(c, "status", None) or getattr(c, "attrs", {}).get(
            "State", {}
        ).get("Status")
        status = "active" if status_raw == "running" else "inactive"

        ports = getattr(c, "attrs", {}).get("NetworkSettings", {}).get("Ports", {})
        mapping = None
        if isinstance(ports, dict):
            mapping = ports.get("8080/tcp")

        host_port = None
        if (
            mapping
            and isinstance(mapping, list)
            and mapping
            and mapping[0].get("HostPort")
        ):
            host_port = mapping[0]["HostPort"]

        port_text = host_port if host_port else "N/A"

        rows.append((str(idx), name, status, port_text))

    if not rows:
        return "No containers found."

    # Determine column widths
    headers = ("ID", "NAME", "STATUS", "PORT")
    cols = list(zip(*([headers] + rows)))
    widths = [max(len(str(cell)) for cell in col) for col in cols]

    # Build format string
    fmt = "  ".join(f"{{:<{w}}}" for w in widths)

    lines = []
    lines.append(fmt.format(*headers))
    lines.append(fmt.format(*["-" * w for w in widths]))
    for r in rows:
        lines.append(fmt.format(*r))

    return "\n".join(lines)


def _show_help() -> str:
    """Return available console commands text."""
    help_path = Path(__file__).parent.parent / "res" / "help.txt"
    try:
        text = help_path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(str(e))
    else:
        return text


def handle_command(user_input: str) -> Tuple[bool, bool, Optional[str]]:
    """Handle slash-prefixed console commands.

    Returns (handled, should_exit, message).
    - handled: True if the input was a command and was handled (no HTTP should be sent).
    - should_exit: True if the console should exit/return.
    - message: Optional text to display to the user.
    """
    if not user_input.startswith("/"):
        return False, False, None

    cmd = user_input[1:].strip()
    if cmd == "exit":
        return True, True, "Goodbye!"

    if cmd == "help":
        return True, False, _show_help()

    if cmd == "list":
        return True, False, _format_containers_list()

    return True, False, f"Unknown command: /{cmd}"
