from typing import Optional
from console import interactive_console, print_header

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
    start_all_containers()

    print_header("Partners", "0.1.0")

    target = _choose_target_container()
    interactive_console(target)

    stop_all_containers()
    remove_all_containers()
