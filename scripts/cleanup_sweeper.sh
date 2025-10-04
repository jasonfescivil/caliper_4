#!/usr/bin/env bash
set -euo pipefail

# Organizes stray files at the repo root into consistent locations.
# - Dry-run by default. Use --execute to actually move files.
# - Writes a plan to logs/cleanup_<timestamp>_(plan|executed).txt

execute=false
if [[ ${1:-} == "--execute" ]]; then
  execute=true
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
timestamp="$(date +%Y%m%d_%H%M%S)"
log_dir="$repo_root/logs"
mkdir -p "$log_dir"
suffix=$([[ $execute == true ]] && echo "_executed.txt" || echo "_plan.txt")
plan_path="$log_dir/cleanup_${timestamp}${suffix}"

metadata_dir="$repo_root/data_v2/metadata"
jobs_dir="$repo_root/data_v2/jobs"
notes_legacy_dir="$repo_root/notes/archive/legacy"
tests_dir="$repo_root/archive/$timestamp/tests"
misc_dir="$repo_root/archive/$timestamp/misc"
scripts_dir="$repo_root/scripts"
logs_dir="$repo_root/logs"

mkdir -p "$metadata_dir" "$jobs_dir" "$notes_legacy_dir" "$tests_dir" "$misc_dir" "$scripts_dir" "$logs_dir"

keep_dirs=(src scripts notes docs knowledge_base data_v2 outputs archive logs .venv .mypy_cache .ruff_cache .pytest_cache .cursor .ide .github .obsidian .vscode)
keep_files=(run_caliper_v2.py pyproject.toml poetry.lock requirements.heavy.txt .gitattributes .gitignore .pre-commit-config.yaml README.md README_local_quickstart.md .env Dockerfile docker-compose.yml)

plan_entries=()
plan_move() {
  local from="$1" to="$2"
  plan_entries+=("FROM: $from -> TO: $to")
  if [[ $execute == true ]]; then
    mkdir -p "$(dirname "$to")"
    mv -f "$from" "$to" 2>/dev/null || true
  fi
}

# Files at root
shopt -s nullglob dotglob
for f in "$repo_root"/*; do
  [[ -d "$f" ]] && continue
  name="$(basename "$f")"
  # keep files
  for k in "${keep_files[@]}"; do
    [[ "$name" == "$k" ]] && continue 2
  done
  if [[ "$name" == README*.md && "$name" != README_local_quickstart.md ]]; then
    continue
  fi

  # Rules
  case "$name" in
    *.ps1|*.sh|*.bat)
      if [[ "$(dirname "$f")" != "$scripts_dir" ]]; then
        plan_move "$f" "$scripts_dir/$name"
        continue
      fi
      ;;
    *.log)
      plan_move "$f" "$logs_dir/$name"
      continue ;;
  esac

  if [[ "$name" == metadata_* || "$name" == *metadata*.csv ]]; then
    plan_move "$f" "$metadata_dir/$name"
    continue
  fi
  if [[ "$name" == jobs_*.csv || "$name" == llama-cloud-history.json || "$name" == ll_*mapping*.csv ]]; then
    plan_move "$f" "$jobs_dir/$name"
    continue
  fi
  if [[ "$name" == test_* ]]; then
    plan_move "$f" "$tests_dir/$name"
    continue
  fi
  if [[ "$name" == *.md && "$name" != README*.md ]]; then
    plan_move "$f" "$notes_legacy_dir/$name"
    continue
  fi
  # default
  plan_move "$f" "$misc_dir/$name"
done

# Directories at root
for d in "$repo_root"/*; do
  [[ -d "$d" ]] || continue
  name="$(basename "$d")"
  # keep dirs
  for k in "${keep_dirs[@]}"; do
    [[ "$name" == "$k" ]] && continue 2
  done
  if [[ "$name" =~ ^logs?$ ]]; then
    continue
  fi
  to="$misc_dir/$name"
  if [[ $execute == true ]]; then
    mv -f "$d" "$to" 2>/dev/null || true
  else
    plan_entries+=("FROM: $d -> TO: $to")
  fi
done

{
  printf '%s\n' "Cleanup Plan ($([[ $execute == true ]] && echo EXECUTE || echo DRY-RUN)) - $timestamp"
  printf '%s\n' "--------------------------------------------------------------------------------"
  for e in "${plan_entries[@]}"; do printf '%s\n' "$e"; done
} | tee "$plan_path"

echo
echo "Plan saved to: $plan_path"
if [[ $execute == true ]]; then
  echo "EXECUTED: files moved."
else
  echo "DRY-RUN: no changes made."
fi

