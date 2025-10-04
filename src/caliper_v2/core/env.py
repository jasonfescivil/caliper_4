from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple


def _manual_parse_env_file(path: Path) -> Tuple[int, int]:
    """
    Minimal .env parser for fallback when python-dotenv isn't installed.
    Returns (set_count, skip_count).
    """
    set_count = 0
    skip_count = 0
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0, 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            skip_count += 1
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if not key:
            skip_count += 1
            continue
        # Do not override existing unless explicitly requested later
        if key not in os.environ:
            os.environ[key] = val
            set_count += 1
    return set_count, skip_count


def _guess_repo_root(start: Optional[Path] = None) -> Optional[Path]:
    """
    Ascend from start (or this file) looking for a marker of repo root (.git, pyproject.toml, or .env).
    """
    cur = (start or Path(__file__).resolve()).parent
    for _ in range(8):
        if (cur / ".git").exists() or (cur / "pyproject.toml").exists() or (cur / ".env").exists():
            return cur
        cur = cur.parent
        if cur == cur.parent:
            break
    return None


def _windows_default_env_path() -> Optional[Path]:
    """
    Provide a pragmatic Windows fallback for local dev environments.
    """
    try:
        p = Path("C:\\repos\\caliper_3\\.env")
        return p if p.exists() else None
    except Exception:
        return None


def load_env(explicit_path: Optional[str | Path] = None, override: bool = True) -> bool:
    """
    Load environment from .env, robustly:
      1) CALIPER_DOTENV_PATH if set
      2) explicit_path argument if provided
      3) python-dotenv find_dotenv (from CWD)
      4) repo root guess (relative to this file)
      5) Windows fallback C:\\repos\\caliper_3\\.env

    If python-dotenv is not available, falls back to a minimal manual parser.
    Returns True if any .env was loaded.
    """
    # Highest-priority explicit env var
    env_var_path = os.getenv("CALIPER_DOTENV_PATH")
    candidates: list[Path] = []
    if env_var_path:
        candidates.append(Path(env_var_path))
    if explicit_path:
        candidates.append(Path(explicit_path))

    # Try python-dotenv first, capturing the discovered path if possible
    dotenv_loaded = False
    try:
        from dotenv import load_dotenv, find_dotenv  # type: ignore

        # Use python-dotenv's search from CWD
        discovered = find_dotenv(usecwd=True)
        if discovered:
            candidates.append(Path(discovered))

        # Also consider repo-root guess
        repo_root = _guess_repo_root()
        if repo_root and (repo_root / ".env").exists():
            candidates.append(repo_root / ".env")

        # Windows conventional fallback
        win_fallback = _windows_default_env_path()
        if win_fallback:
            candidates.append(win_fallback)

        # Deduplicate while preserving order
        seen = set()
        ordered_candidates: list[Path] = []
        for c in candidates:
            try:
                p = c.resolve()
            except Exception:
                continue
            if p in seen:
                continue
            seen.add(p)
            ordered_candidates.append(p)

        for c in ordered_candidates:
            if c.exists():
                if load_dotenv(dotenv_path=str(c), override=override):
                    dotenv_loaded = True
                    break
    except Exception:
        # python-dotenv missing or failed; fall back to manual parser with our best guesses
        repo_root = _guess_repo_root()
        if repo_root and (repo_root / ".env").exists():
            candidates.append(repo_root / ".env")
        win_fallback = _windows_default_env_path()
        if win_fallback:
            candidates.append(win_fallback)

        for c in candidates:
            if c and isinstance(c, Path) and c.exists():
                set_count, _ = _manual_parse_env_file(c)
                if set_count > 0:
                    dotenv_loaded = True
                    break

    return dotenv_loaded


def require_env(keys: Iterable[str]) -> None:
    """
    Ensure required environment variables are present; raise a helpful error otherwise.
    """
    missing = [k for k in keys if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Ensure your .env is loaded or set these in the environment."
        )
