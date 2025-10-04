from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", errors="ignore")


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = (p.stdout or "") + ("\n" + (p.stderr or "") if p.stderr else "")
        return p.returncode, out
    except Exception as exc:
        return 1, f"<error: {exc}>"


def capture_cli_help(dst: Path) -> None:
    # Import Typer app without requiring poetry install
    try:
        sys.path.insert(0, str(Path("src").resolve()))
        import caliper_v2.cli_main as cm  # type: ignore
        from typer.main import get_command  # type: ignore
        import click  # type: ignore

        cmd = get_command(cm.app)
        ctx_main = click.Context(cmd)
        write_text(dst / "cli_help_main.txt", cmd.get_help(ctx_main))

        sub = cmd.get_command(click.Context(cmd), "retrieve")
        if sub:
            write_text(dst / "cli_help_retrieve.txt", sub.get_help(click.Context(sub)))
        sub = cmd.get_command(click.Context(cmd), "generate")
        if sub:
            write_text(dst / "cli_help_generate.txt", sub.get_help(click.Context(sub)))
    except Exception as exc:
        write_text(dst / "cli_help_errors.txt", f"Failed to capture CLI help: {exc}")


def capture_versions(dst: Path) -> None:
    _, py = run([sys.executable, "--version"])
    write_text(dst / "python_version.txt", py)
    _, pip = run([sys.executable, "-m", "pip", "list", "--format=freeze"])
    write_text(dst / "pip_list.txt", pip)
    code, poetry = run(["poetry", "--version"]) if os.name == "nt" else run(["poetry", "--version"]) 
    write_text(dst / "poetry_version.txt", poetry)


def capture_static(dst: Path) -> None:
    # File listing
    code, out = run(["rg", "--files", "-g", "!**/.venv/**", "-g", "!**/__pycache__/**"])
    write_text(dst / "files.txt", out)
    # TODO/FIXME/legacy sweep
    code, out = run(["rg", "-n", "TODO|FIXME|XXX|deprecated|legacy|dead code", "-S", "--no-heading"])
    write_text(dst / "static_sweep.txt", out)


def capture_doctor(dst: Path) -> None:
    try:
        sys.path.insert(0, str(Path("src").resolve()))
        from caliper_v2.cli_main import doctor  # type: ignore

        # Redirect stdout/stderr via subprocess to capture colors as text where possible
        code, out = run([sys.executable, "-c", "import sys;sys.path.insert(0,'src');from caliper_v2.cli_main import doctor;doctor()"])
        write_text(dst / "doctor_output.txt", out)
    except Exception as exc:
        write_text(dst / "doctor_error.txt", f"Failed to run doctor(): {exc}")


def main() -> None:
    root = Path(".artifacts").resolve()
    base = ensure_dir(root / "review-codex" / timestamp())
    capture_versions(base)
    capture_static(base)
    capture_cli_help(base)
    capture_doctor(base)
    print(str(base))


if __name__ == "__main__":
    main()

