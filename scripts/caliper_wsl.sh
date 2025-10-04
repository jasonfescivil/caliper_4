#!/usr/bin/env bash
# Caliper launcher (WSL/Linux) — WSL-ONLY canonical entrypoint
# - Enforces a single project-local venv (.venv_heavy)
# - Fails fast with clear guidance if python3-venv is missing
# - Always aligns environment to requirements.heavy.txt to prevent drift
# Usage:
#   /mnt/c/dev/caliper/scripts/caliper_wsl.sh wizard
# Recommended shell function (add to ~/.bashrc or ~/.zshrc):
#   caliper() { /mnt/c/dev/caliper/scripts/caliper_wsl.sh "$@"; }

set -euo pipefail

msg() { printf '%b\n' "$*"; }
fail() { printf '%b\n' "$*" >&2; exit 1; }

# Resolve repo root relative to this script
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# Guardrail: running from WSL (path should start with /mnt/)
case "$REPO_DIR" in
  /mnt/*) ;;
  *) msg "[!] Warning: Expected a /mnt/... path under WSL. Current: $REPO_DIR";;
esac

VENV_DIR=".venv_heavy"
PY_EXE="python3"

# Preflight: python3 and python3-venv availability
if ! command -v "$PY_EXE" >/dev/null 2>&1; then
  fail "[!] python3 not found.\n    Fix: sudo apt update && sudo apt install -y python3 python3-venv"
fi

if ! "$PY_EXE" -m venv --help >/dev/null 2>&1; then
  fail "[!] The venv module is unavailable (python3-venv missing?).\n    Fix: sudo apt update && sudo apt install -y python3-venv"
fi

# Create venv if missing
if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  msg "[+] Creating virtual environment ($VENV_DIR)..."
  "$PY_EXE" -m venv "$VENV_DIR"
fi

# Always align environment to requirements.heavy.txt (prevents drift)
msg "[+] Ensuring dependencies are aligned with requirements.heavy.txt..."
"$VENV_DIR/bin/python" -m pip install -U pip setuptools wheel
"$VENV_DIR/bin/python" -m pip install -r requirements.heavy.txt

msg "[+] Running Caliper... (args: $*)"
exec "$VENV_DIR/bin/python" run_caliper_v2.py "$@"
