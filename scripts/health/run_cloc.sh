#!/usr/bin/env bash
set -euo pipefail

REPOS_DIR="${1:?usage: run_cloc.sh <repos_dir>}"

# Conservative excludes: caches, build outputs, virtualenvs, node_modules, etc.
EXCLUDES=".git,.venv,venv,node_modules,dist,build,__pycache__,.mypy_cache,.pytest_cache,.ruff_cache,.tox,.nox,.cache,site-packages"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
OUT_DIR="$ROOT_DIR/.health/cloc_json"

mkdir -p "$OUT_DIR"

cd "$REPOS_DIR"
for d in */ ; do
  [ -d "${d}/.git" ] || continue
  repo="${d%/}"
  echo "cloc: $repo"
  cloc "$repo" \
    --exclude-dir="$EXCLUDES" \
    --json --quiet \
    --out "$OUT_DIR/${repo}.json"
done
