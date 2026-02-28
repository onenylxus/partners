from typing import Tuple
from pathlib import Path


def show_help() -> None:
    """Print available console commands."""
    help_path = Path(__file__).parent.parent / "res" / "help.txt"
    try:
        text = help_path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(str(e))
    else:
        print(text, end="")


def handle_command(user_input: str) -> Tuple[bool, bool]:
    """Handle slash-prefixed console commands.

    Returns (handled, should_exit).
    - handled: True if the input was a command and was handled (no HTTP should be sent).
    - should_exit: True if the console should exit/return.
    """
    if not user_input.startswith("/"):
        return False, False

    cmd = user_input[1:].strip()
    if cmd == "exit":
        return True, True

    if cmd == "help":
        show_help()
        return True, False

    print(f"Unknown command: /{cmd}")
    return True, False
