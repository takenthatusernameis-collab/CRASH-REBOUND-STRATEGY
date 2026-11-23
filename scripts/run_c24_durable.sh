#!/usr/bin/env bash
# Durable foreground wrapper for the C24 margin/liquidation-fidelity campaign.
#
# This script does NOT daemonize. Launch it with the harness background-process
# tool using persistent=true so the runner survives session/turn boundaries:
#
#   background_process start command="bash scripts/run_c24_durable.sh" persistent=true
#
# It refuses to start a duplicate runner, requires the durable venv, and tees
# output to a timestamped log under research_state/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c24_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c24-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

. "$REPO/scripts/runner_alive.sh"
if runner_alive "run_c24_margin_fidelity_campaign.py --jobs"; then
  echo "[c24-launch] canonical C24 runner already active; not starting a duplicate."
  runner_ps "run_c24_margin_fidelity_campaign.py"
  exit 0
fi

echo "[c24-launch] starting canonical C24 resume run -> $LOG"
export PYTHONPATH=.
exec "$PY" scripts/run_c24_margin_fidelity_campaign.py --jobs 4 --resume 2>&1 | tee "$LOG"
