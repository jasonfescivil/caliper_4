import sys


def main() -> None:
    # Make src importable and delegate to Typer app
    sys.path.insert(0, "src")
    from caliper_v2.cli import app  # type: ignore

    app()


if __name__ == "__main__":
    main()
