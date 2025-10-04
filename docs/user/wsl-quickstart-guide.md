# Caliper v2 WSL Quickstart Guide

This guide provides a reliable way to run Caliper v2 using Windows Subsystem for Linux (WSL) to avoid environment drift issues.

What this gives you
- One canonical venv at /mnt/c/dev/caliper/.venv_heavy
- Pinned dependencies via requirements.heavy.txt (LlamaIndex 0.12.52 + 0.4.x split packages)
- A single launcher that always aligns the environment on every run

Prerequisites (WSL Ubuntu)
- Repo is located at /mnt/c/dev/caliper
- python3 and python3-venv installed

Install prerequisites if needed:
sudo apt update && sudo apt install -y python3 python3-venv

Add a convenience command (recommended)
- Add this to your ~/.bashrc (or ~/.zshrc), then reload your shell:
echo 'caliper() { /mnt/c/dev/caliper/scripts/caliper_wsl.sh "$@"; }' >> ~/.bashrc
source ~/.bashrc

Now you can run:
- caliper doctor
- caliper wizard
- caliper ingest ...
- caliper query ...

Use the launcher directly (if you don’t want a shell function)
- /mnt/c/dev/caliper/scripts/caliper_wsl.sh wizard
- /mnt/c/dev/caliper/scripts/caliper_wsl.sh doctor

First-time setup and ingest (required before query)
1) Ensure your .env exists and contains necessary API keys (copy the example first):
   cp /mnt/c/dev/caliper/.env.example /mnt/c/dev/caliper/.env
   # then edit .env to add OPENAI_API_KEY and any other keys you use

2) Do one ingest with persistence so indexes exist:
   caliper ingest knowledge_base --index all_docs_enhanced --persist

3) Query:
   caliper query "What are the CFR Part 503 pathogen requirements?" --index all_docs_enhanced --search-mode hybrid

Notes about dependencies and drift
- The WSL launcher scripts/caliper_wsl.sh will:
  - Create .venv_heavy if missing
  - Always run pip install -r requirements.heavy.txt to keep the environment aligned
- If you ever need a clean reset:
  rm -rf /mnt/c/dev/caliper/.venv_heavy
  caliper doctor  # this will recreate venv and reinstall

Troubleshooting
- python3 or venv missing:
  sudo apt update && sudo apt install -y python3 python3-venv

- Missing OpenAI key (for default embeddings):
  Set OPENAI_API_KEY in /mnt/c/dev/caliper/.env
  Or run with --embed-provider local for offline smoke tests

- Persisted index not found:
  Run an ingest with --persist once before using query/agent

- Running from Windows accidentally:
  caliper.bat now exits immediately with a deprecation message. Always run from WSL.

Why WSL-only
- Prevents divergence between Windows and WSL environments
- Ensures consistent Python interpreter and package paths
- Eliminates PATH/launcher differences that caused unpredictable behavior

That’s it. After the shell function is added, use caliper from any new WSL terminal.
