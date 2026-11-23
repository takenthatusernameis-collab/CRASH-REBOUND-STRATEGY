#!/usr/bin/env bash
# Durable foreground wrapper for the C27 next-venue replication campaign.
#
# C27 is the mandatory same-session successor on C26 ACCEPTANCE: PASS in the
# `C24 -> C25 -> C26 -> C27+` heavy queue. No C27 cell may run until C26
# ACCEPTANCE: PASS; this wrapper self-bootstraps the venv on fresh jobs and
# launches the canonical C27 resume run durably so it survives session/turn
# boundaries.
#
# This script does NOT daemonize. Launch it with the harness background-process
# tool using persistent=true:
#
#   background_process start command="bash scripts/run_c27_durable.sh" persistent=true
#
# It refuses to start a duplicate runner, requires the durable venv, and tees
# output to a timestamped log under research_state/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c27_run_${TS}.log"

if [ ! -x "$PY" ]; then
  # Fresh CI job / new worktree: .venv is gitignored, so the first session of a
  # job has no venv. Bootstrap here instead of exiting, so the documented
  # one-command launch works on the first session after the predecessor gate
  # PASSes.
  echo "[c27-launch] missing venv at $PY; bootstrapping (scripts/bootstrap_env.sh)" >&2
  if ! bash "$REPO/scripts/bootstrap_env.sh"; then
    echo "[c27-launch] ERROR: bootstrap_env.sh failed; cannot start the runner." >&2
    exit 1
  fi
fi

. "$REPO/scripts/runner_alive.sh"
if runner_alive "run_c27_campaign.py --jobs"; then
  echo "[c27-launch] canonical C27 runner already active; not starting a duplicate."
  runner_ps "run_c27_campaign.py"
  exit 0
fi

echo "[c27-launch] starting canonical C27 resume run -> $LOG"
export PYTHONPATH=.
# Intra-cell draw durability: permutation/placebo draws checkpoint every 500
# subsets and resume bit-identically after an environment loss (~5 min max loss)
# instead of restarting the whole ~3.2 h cell. Set C25_DRAW_RESUME=0 for a
# monolithic (non-resumable) audit run; results are identical either way.
export C25_DRAW_RESUME="${C25_DRAW_RESUME:-1}"
export C25_DRAW_CHUNK="${C25_DRAW_CHUNK:-500}"
exec "$PY" scripts/run_c27_campaign.py --jobs 4 --resume 2>&1 | tee "$LOG"
