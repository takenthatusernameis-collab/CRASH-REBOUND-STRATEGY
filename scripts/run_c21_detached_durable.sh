#!/usr/bin/env bash
# Canonical detached launcher for the C21 cross-venue campaign.
# Ensures C21 runs survive session/turn boundaries with a real, readable log
# and refuses to start a duplicate while a canonical runner is already alive.
# Usage: bash scripts/run_c21_detached_durable.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c21_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c21-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

if pgrep -f "run_c21_cross_venue_campaign.py" >/dev/null 2>&1; then
  echo "[c21-launch] canonical C21 runner already active; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "run_c21_cross_venue_campaign.py" | grep -v grep || true
  exit 0
fi

echo "[c21-launch] starting canonical C21 resume run -> $LOG"
PYTHONPATH=. nohup "$PY" scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume \
  > "$LOG" 2>&1 &
echo "[c21-launch] pid=$! log=$LOG"