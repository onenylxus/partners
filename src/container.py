import sys


def main() -> None:
    try:
        for line in sys.stdin:
            sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
