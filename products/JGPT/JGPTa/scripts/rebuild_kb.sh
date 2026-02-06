#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV_DIR="$REPO_ROOT/.venv"
PYTHON_BIN="python3"

API_BASE="${API_BASE:-http://localhost:8000}"
HEALTH_URL="$API_BASE/health"
INGEST_KB_URL="$API_BASE/ingest/kb"
INGEST_WEB_URL="$API_BASE/ingest/web"

DO_DISTILL="${DO_DISTILL:-1}"
DISTILL_DOMAIN="${DISTILL_DOMAIN:-all}"

DO_WEB="${DO_WEB:-0}"
WEB_FORCE="${WEB_FORCE:-0}"
WEB_MAX_PAGES="${WEB_MAX_PAGES:-0}"

WAIT_SECONDS=90
SLEEP_STEP=2

say() { echo -e "\n==> $*"; }

ensure_venv() {
  if [[ ! -d "$VENV_DIR" ]]; then
    say "Creating Python virtual environment (.venv)"
    $PYTHON_BIN -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"

  if [[ -f "scripts/requirements.txt" ]]; then
    say "Installing Python dependencies (if needed)"
    pip install --quiet --upgrade pip
    pip install --quiet -r scripts/requirements.txt
  fi
}

wait_for_health() {
  say "Waiting for API health..."
  local elapsed=0
  until curl -fsS "$HEALTH_URL" >/dev/null; do
    sleep "$SLEEP_STEP"
    elapsed=$((elapsed + SLEEP_STEP))
    if (( elapsed > WAIT_SECONDS )); then
      echo "API did not become healthy in time" >&2
      exit 1
    fi
  done
  echo "API is healthy ✅"
}

ensure_venv
wait_for_health

if [[ "$DO_DISTILL" == "1" ]]; then
  say "Running KB distillation (domain=$DISTILL_DOMAIN)"
  python scripts/kb_distill.py --domain "$DISTILL_DOMAIN"
else
  say "Skipping KB distillation"
fi

say "Ingesting KB"
curl -fsS -X POST "$INGEST_KB_URL" >/dev/null
echo "KB ingest complete ✅"

if [[ "$DO_WEB" == "1" ]]; then
  qs="force=$WEB_FORCE"
  if [[ "$WEB_MAX_PAGES" != "0" ]]; then
    qs="$qs&max_pages=$WEB_MAX_PAGES"
  fi
  say "Running web ingest"
  curl -fsS -X POST "$INGEST_WEB_URL?$qs" >/dev/null
  echo "Web ingest complete ✅"
fi

say "Rebuild finished 🎉"
