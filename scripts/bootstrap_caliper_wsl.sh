#!/usr/bin/env bash
set -euo pipefail

# Caliper WSL bootstrap
# - Creates a local venv with full deps under /mnt/c/dev/caliper/.venv_heavy
# - Adds a 'caliper' shell function to ~/.bashrc for one-command usage

REPO="/mnt/c/dev/caliper"
VENV_DIR="$REPO/.venv_heavy"
PY=${PYTHON_BIN:-python3}

if [ ! -d "$REPO" ]; then
  echo "[!] Repo not found at $REPO. Edit this script to point to your repo path and re-run." 1>&2
  exit 1
fi

mkdir -p "$REPO"

if [ ! -x "$(command -v $PY)" ]; then
  echo "[!] python3 not found on PATH. Install Python 3 in WSL (e.g., sudo apt-get install python3 python3-venv python3-pip)." 1>&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[+] Creating venv at $VENV_DIR"
  $PY -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install -U pip setuptools wheel
  echo "[+] Installing dependencies (this may take a few minutes)..."
  "$VENV_DIR/bin/python" -m pip install \
    typer==0.15.* loguru==0.7.* python-dotenv==1.* pydantic==2.10.* pydantic-settings==2.7.* \
    tiktoken==0.8.* faiss-cpu==1.8.* cohere==5.* pypdf==5.* nest-asyncio==1.6.* \
    "llama-index==0.12.*" \
    "llama-index-llms-openai==0.2.*" "llama-index-llms-anthropic==0.2.*" "llama-index-llms-gemini==0.2.*" "llama-index-llms-vertex==0.2.*" "llama-index-llms-openai-like==0.2.*" \
    anthropic==0.40.* google-cloud-aiplatform==1.38.* google-auth==2.23.* \
    "llama-index-embeddings-openai==0.2.*" "llama-index-embeddings-cohere==0.2.*" "llama-index-embeddings-huggingface==0.2.*" \
    "llama-index-retrievers-bm25==0.2.*" \
    "llama-index-postprocessor-cohere-rerank==0.2.*" \
    "llama-parse==0.5.*"
fi

BASHRC="$HOME/.bashrc"
FN_NAME="caliper"
FN_BODY=$(cat <<'EOF'
function caliper() {
  local REPO="/mnt/c/dev/caliper"
  local VENV_DIR="$REPO/.venv_heavy"
  if [ ! -d "$VENV_DIR" ]; then
    echo "[!] venv missing at $VENV_DIR. Run scripts/bootstrap_caliper_wsl.sh" 1>&2
    return 1
  fi
  ( cd "$REPO" && \
    . "$VENV_DIR/bin/activate" && \
    python run_caliper_v2.py "$@" )
}
EOF
)

if ! grep -q "^function $FN_NAME" "$BASHRC" 2>/dev/null; then
  echo "" >> "$BASHRC"
  echo "# added by Caliper WSL bootstrap on $(date -Iseconds)" >> "$BASHRC"
  echo "$FN_BODY" >> "$BASHRC"
  echo "[+] Added '$FN_NAME' function to $BASHRC"
else
  echo "[=] '$FN_NAME' already present in $BASHRC"
fi

echo "\nDone. Open a new WSL shell (or 'source ~/.bashrc'), then run: caliper wizard"
