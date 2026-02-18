from containers import (
    create_container,
    list_containers,
    start_all_containers,
    stop_all_containers,
    remove_all_containers,
)

if __name__ == "__main__":
    create_container()
    containers = list_containers()
    print(containers)
    start_all_containers()
    stop_all_containers()
    remove_all_containers()
