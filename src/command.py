from typing import Optional, Tuple
from pathlib import Path


def show_help() -> str:
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
        return True, False, show_help()

    return True, False, f"Unknown command: /{cmd}"
