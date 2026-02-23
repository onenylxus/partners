from typing import Optional
import shlex

from manager import (
    create_container,
    list_containers,
    start_all_containers,
    stop_all_containers,
    remove_all_containers,
)


def _choose_target_container() -> Optional[object]:
    containers = list_containers()
    # prefer a running container
    for c in containers:
        try:
            if getattr(c, "status", None) == "running":
                return c
        except Exception:
            continue
    # fall back to first container if any
    return containers[0] if containers else None


if __name__ == "__main__":
    create_container()
    containers = list_containers()
    print(containers)

    start_all_containers()

    target = _choose_target_container()
    if not target:
        print("No container available to run the echo script.")
    else:
        try:
            while True:
                try:
                    user_input = input("input> ")
                except EOFError:
                    break
                if not user_input:
                    continue

                quoted = shlex.quote(user_input + "\n")
                cmd = ["sh", "-c", f"printf {quoted} | python3 /app/container.py"]

                try:
                    result = target.exec_run(cmd)
                except Exception as exc:
                    print(f"exec_run failed: {exc}")
                    break

                # docker-py may return (exit_code, output) or an object
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

                print(output, end="")

        except KeyboardInterrupt:
            print("\nInterrupted by user")

    stop_all_containers()
    remove_all_containers()
