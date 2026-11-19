#!/usr/bin/env bash
# Durable foreground wrapper for the C26 intrabat path & per-trade funding-fidelity campaign.
#
# This script does NOT daemonize. Launch it with the harness background-process
# tool using persistent=true so the runner survives session/turn boundaries:
#
#   background_process start command="bash scripts/run_c26_durable.sh" persistent=true
#
# It refuses to start a duplicate runner, requires the durable venv, and tees
# output to a timestamped log under research_state/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c26_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c26-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

if pgrep -f "run_c26_path_fidelity_campaign.py --jobs" >/dev/null 2>&1; then
  echo "[c26-launch] canonical C26 runner already active; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "[r]un_c26_path_fidelity_campaign.py" || true
  exit 0
fi

echo "[c26-launch] starting canonical C26 resume run -> $LOG"
export PYTHONPATH=.
# Intra-cell draw durability: permutation/placebo draws checkpoint every 500
# subsets and resume bit-identically after an environment loss (~5 min max loss)
# instead of restarting the whole ~3.2 h cell. Set C25_DRAW_RESUME=0 for a
# monolithic (non-resumable) audit run; results are identical either way.
export C25_DRAW_RESUME="${C25_DRAW_RESUME:-1}"
export C25_DRAW_CHUNK="${C25_DRAW_CHUNK:-500}"
exec "$PY" scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume 2>&1 | tee "$LOG"
