from typing import Any
import shlex
import requests
from command import handle_command


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
        print(
            "Target container has no 8080/tcp host port mapped. Ensure manager publishes the port."
        )
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
                handled, should_exit = handle_command(user_input)
                if handled and should_exit:
                    return
                if handled:
                    continue

            try:
                resp = requests.post(
                    f"http://localhost:{host_port}/exec",
                    json={"input": user_input},
                    timeout=5,
                )
                resp.raise_for_status()
                data = resp.json()
                output = data.get("output", "")
            except Exception as exc:
                print(f"HTTP request failed: {exc}")
                break

            print(output)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
