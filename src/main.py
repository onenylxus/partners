from typing import List
from docker.models.containers import Container
import docker

dockerClient: docker.DockerClient = docker.DockerClient()


def list_containers() -> List[Container]:
    """List all containers (running and stopped)."""
    containers = dockerClient.containers.list(all=True)
    return containers


def create_container() -> bool:
    """Create a new container from the partners-agent image."""
    container = dockerClient.containers.create("partners-agent:latest")
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
        result = result and remove_container(container.id)
    return result


if __name__ == "__main__":
    create_container()
    containers = list_containers()
    print(containers)
    start_all_containers()
    stop_all_containers()
    remove_all_containers()
