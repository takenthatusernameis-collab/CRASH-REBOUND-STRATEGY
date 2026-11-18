#!/usr/bin/env bash
# Canonical detached launcher for the C23 Bitget USDT-M out-of-sample campaign.
# Ensures C23 runs survive session/turn boundaries with a real, readable log
# and refuses to start a duplicate while a canonical runner is already alive.
# Usage: bash scripts/run_c23_detached_durable.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c23_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c23-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

# C23 must not start while C22 is still running (CPU contention / sequencing rule).
if pgrep -f "run_c22_mexc_campaign.py" >/dev/null 2>&1; then
  echo "[c23-launch] C22 runner still active; wait for C22 ACCEPTANCE: PASS first." >&2
  exit 3
fi

if pgrep -f "run_c23_bitget_campaign.py" >/dev/null 2>&1; then
  echo "[c23-launch] canonical C23 runner already active; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "run_c23_bitget_campaign.py" | grep -v grep || true
  exit 0
fi

echo "[c23-launch] starting canonical C23 resume run -> $LOG"
PYTHONPATH=. nohup "$PY" scripts/run_c23_bitget_campaign.py --jobs 4 --resume \
  > "$LOG" 2>&1 &
echo "[c23-launch] pid=$! log=$LOG"
