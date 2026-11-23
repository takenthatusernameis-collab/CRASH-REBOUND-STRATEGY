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
  # Fresh CI job / new worktree: .venv is gitignored, so the first session of a
  # job has no venv. Bootstrap here instead of exiting, so the documented
  # one-command launch works on the first session after the predecessor gate
  # PASSes. Fixed 2026-11-21T10:30:00Z.
  echo "[c26-launch] missing venv at $PY; bootstrapping (scripts/bootstrap_env.sh)" >&2
  if ! bash "$REPO/scripts/bootstrap_env.sh"; then
    echo "[c26-launch] ERROR: bootstrap_env.sh failed; cannot start the runner." >&2
    exit 1
  fi
fi

. "$REPO/scripts/runner_alive.sh"
if runner_alive "run_c26_path_fidelity_campaign.py --jobs"; then
  echo "[c26-launch] canonical C26 runner already active; not starting a duplicate."
  runner_ps "run_c26_path_fidelity_campaign.py"
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
