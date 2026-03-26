# File: manager.py
# Summary: Provides Docker container lifecycle helpers used by the Partners app.

from typing import List

from docker import DockerClient
from docker.models.containers import Container

dockerClient: DockerClient = DockerClient()


def list_containers() -> List[Container]:
    """List all containers (running and stopped)."""
    containers = dockerClient.containers.list(all=True)
    return containers


def create_container(name: str, model: str) -> bool:
    """Create a new container from the partners-agent image with the
    provided `name` and `model` passed as environment variables.
    """
    # Remove any existing container with the same name to avoid conflicts
    try:
        existing = dockerClient.containers.get(name)
        existing.remove(force=True)
    except Exception:
        pass  # If not found, ignore

    # Create the container with stdin open and a TTY so the process
    # keeps running even when not attached. Return the container object.
    container = dockerClient.containers.create(
        "partners-agent:latest",
        stdin_open=True,
        tty=True,
        detach=True,
        ports={"8080/tcp": None},
        name=name,
        environment={
            "OPENAI_MODEL": model,
            "CONTAINER_NAME": name,
        },
    )
    return True


def start_container(container_id: str) -> bool:
    """Start a specific container by ID."""
    container = dockerClient.containers.get(container_id)
    container.start()
    return True


def start_all_containers() -> bool:
    """Start all containers."""
    result = True
    containers = dockerClient.containers.list(all=True)
    for container in containers:
        if not container.id:
            continue
        result = result and start_container(container.id)
    return result


def stop_container(container_id: str) -> bool:
    """Stop a specific container by ID."""
    container = dockerClient.containers.get(container_id)
    container.stop()
    return True


def stop_all_containers() -> bool:
    """Stop all containers."""
    result = True
    containers = dockerClient.containers.list(all=True)
    for container in containers:
        if not container.id:
            continue
        result = result and stop_container(container.id)
    return result


def remove_container(container_id: str) -> bool:
    """Remove a specific container by ID."""
    container = dockerClient.containers.get(container_id)
    container.remove()
    return True


def remove_all_containers() -> bool:
    """Remove all containers."""
    result = True
    containers = dockerClient.containers.list(all=True)
    for container in containers:
        if not container.id:
            continue
        result = result and remove_container(container.id)
    return result
