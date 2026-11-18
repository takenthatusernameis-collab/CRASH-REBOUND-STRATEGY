#!/usr/bin/env bash
# Canonical detached launcher for the C22 MEXC out-of-sample campaign.
# Ensures C22 runs survive session/turn boundaries with a real, readable log
# and refuses to start a duplicate while a canonical runner is already alive.
# Usage: bash scripts/run_c22_detached_durable.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c22_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c22-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

if pgrep -f "run_c22_mexc_campaign.py" >/dev/null 2>&1; then
  echo "[c22-launch] canonical C22 runner already active; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "run_c22_mexc_campaign.py" | grep -v grep || true
  exit 0
fi

echo "[c22-launch] starting canonical C22 resume run -> $LOG"
PYTHONPATH=. nohup "$PY" scripts/run_c22_mexc_campaign.py --jobs 4 --resume \
  > "$LOG" 2>&1 &
echo "[c22-launch] pid=$! log=$LOG"