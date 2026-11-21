#!/usr/bin/env bash
# Durable foreground wrapper for the C32 next-focus campaign.
#
# C32 is the mandatory same-session successor on C31 ACCEPTANCE: PASS in the
# `C24 -> C25 -> C26 -> C27 -> C28 -> C29 -> C30 -> C31 -> C32+` heavy queue. No C32 cell
# may run until C31 ACCEPTANCE: PASS; this wrapper enforces nothing itself (the
# campaign runner refuses heavy compute until the gate exists) but launches the
# canonical C32 resume run durably so it survives session/turn boundaries.
#
# This script does NOT daemonize. Launch it with the harness background-process
# tool using persistent=true so the runner survives session/turn boundaries:
#
#   background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true
#
# It refuses to start a duplicate runner, requires the durable venv, and tees
# output to a timestamped log under research_state/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/c32_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[c32-launch] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

DIRECTION=""
ARGS=()
for a in "$@"; do
  case "$a" in
    --direction) DIRECTION="${2:-}"; shift 2 ;;
    --direction=*) DIRECTION="${a#*=}"; shift ;;
    *) ARGS+=("$a"); shift ;;
  esac
done

if [ -z "$DIRECTION" ]; then
  echo "[c32-launch] ERROR: --direction <c32-a> is required" >&2
  exit 1
fi

if pgrep -f "run_c32_campaign.py --direction ${DIRECTION} --jobs" >/dev/null 2>&1; then
  echo "[c32-launch] canonical C32 runner already active for ${DIRECTION}; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "[r]un_c32_campaign.py" || true
  exit 0
fi

echo "[c32-launch] starting canonical C32 resume run (${DIRECTION}) -> $LOG"
export PYTHONPATH=.
# Intra-cell draw durability: permutation/placebo draws checkpoint every 500
# subsets and resume bit-identically after an environment loss (~5 min max loss)
# instead of restarting the whole ~3.2 h cell. Set C25_DRAW_RESUME=0 for a
# monolithic (non-resumable) audit run; results are identical either way.
export C25_DRAW_RESUME="${C25_DRAW_RESUME:-1}"
export C25_DRAW_CHUNK="${C25_DRAW_CHUNK:-500}"
exec "$PY" scripts/run_c32_campaign.py --direction "${DIRECTION}" --jobs 4 --resume "${ARGS[@]+"${ARGS[@]}"}" 2>&1 | tee "$LOG"
