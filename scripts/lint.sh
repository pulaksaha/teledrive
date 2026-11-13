#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$ROOT_DIR/services/core/.venv/bin/python"
export npm_config_logs_dir="${TMPDIR:-/tmp}/pulakdrive-npm-logs"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Required command not found: %s\n' "$1" >&2
    exit 1
  fi
}

require_command npm
if [[ ! -x "$PYTHON_BIN" ]]; then
  printf 'Python virtual environment not found at %s\n' "$PYTHON_BIN" >&2
  printf 'Create it and install the pinned requirements before linting.\n' >&2
  exit 1
fi

printf '=== Linting PulakDrive ===\n'
printf 'Repository root: %s\n\n' "$ROOT_DIR"

printf '%s\n' '--> [1/3] Running Ruff'
(
  cd "$ROOT_DIR/services/core"
  "$PYTHON_BIN" -m ruff check .
)

printf '\n%s\n' '--> [2/3] Installing pinned web dependencies and typechecking'
(
  cd "$ROOT_DIR/apps/web"
  npm ci --no-audit --no-fund
  npm run typecheck
)

printf '\n%s\n' '--> [3/3] Running ESLint'
(
  cd "$ROOT_DIR/apps/web"
  npm run lint
)

printf '\n=== All PulakDrive lint checks passed ===\n'
