from typing import Any
import shlex


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
        print("No container available to run the echo script.")
        return

    try:
        while True:
            try:
                user_input = input("input> ")
            except EOFError:
                break
            if not user_input:
                continue

            # commands start with '/'
            if user_input.startswith("/"):
                cmd = user_input[1:].strip()
                if cmd == "exit":
                    return
                print(f"Unknown command: /{cmd}")
                continue

            quoted = shlex.quote(user_input + "\n")
            cmd = ["sh", "-c", f"printf {quoted} | python3 /app/container.py"]

            try:
                result = target.exec_run(cmd)
            except Exception as exc:
                print(f"exec_run failed: {exc}")
                break

            output = format_exec_result(result)
            print(output, end="")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
