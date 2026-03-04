from typing import Optional
import json
import os
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


def load_containers_config(path: str = "containers.json") -> list:
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data.get("containers", [])
    except Exception:
        return []


if __name__ == "__main__":
    # Read configured containers and create each with its model
    entries = load_containers_config(
        os.environ.get("CONTAINERS_CONFIG", "containers.json")
    )
    if entries:
        for entry in entries:
            name = entry.get("name", "default")
            model = entry.get("model", "")
            create_container(name, model)
    else:
        # fallback to creating a single default container using env
        create_container("default", "")

    start_all_containers()

    print_header("Partners", "0.1.0")

    target = _choose_target_container()
    interactive_console(target)

    stop_all_containers()
    remove_all_containers()
