#!/usr/bin/env bash
# Durable foreground wrapper for the OKX realized-funding acquisition (C25 prerequisite).
#
# C25's cost_taker_funding (PRIMARY) and cost_stress arms require realized per-venue
# 8h funding history. binance_um/mexc/bitget are already cached; OKX is the missing
# venue. This wrapper acquires it so OKX is funding-available rather than
# UNAVAILABLE_FUNDING, which would otherwise weaken the C25 decision rule.
#
# Launch with the harness background-process tool using persistent=true:
#   background_process start command="bash scripts/run_c25_okx_funding_durable.sh" persistent=true
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO/research_state/okx_funding_run_${TS}.log"

if [ ! -x "$PY" ]; then
  echo "[okx-funding] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

if pgrep -f "fetch_funding_history.py --venues okx" >/dev/null 2>&1; then
  echo "[okx-funding] OKX funding acquisition already active; not starting a duplicate."
  ps -eo pid,etime,time,stat,cmd | grep "[f]etch_funding_history.py" || true
  exit 0
fi

echo "[okx-funding] starting OKX realized-funding acquisition -> $LOG"
export PYTHONPATH=.
exec "$PY" scripts/fetch_funding_history.py --venues okx --workers 8 2>&1 | tee "$LOG"
