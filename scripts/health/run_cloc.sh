#!/usr/bin/env bash
set -euo pipefail

REPOS_DIR="${1:?usage: run_cloc.sh <repos_dir>}"

# Conservative excludes: caches, build outputs, virtualenvs, node_modules, etc.
EXCLUDES=".git,.venv,venv,node_modules,dist,build,__pycache__,.mypy_cache,.pytest_cache,.ruff_cache,.tox,.nox,.cache,site-packages"

mkdir -p "$GITHUB_WORKSPACE/.health/cloc_json"

cd "$REPOS_DIR"
for d in */ ; do
  [ -d "${d}/.git" ] || continue
  repo="${d%/}"
  echo "cloc: $repo"
  cloc "$repo" \
    --exclude-dir="$EXCLUDES" \
    --json --quiet \
    --out "$GITHUB_WORKSPACE/.health/cloc_json/${repo}.json"
done
