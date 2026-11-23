#!/usr/bin/env bash
# One-shot, read-only C28 status probe. Never launches, never kills, never blocks.
# Usage: bash scripts/status_c28.sh --direction c28-a
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261121T013400Z"
DIRECTION=""

while [ $# -gt 0 ]; do
  case "$1" in
    --direction) DIRECTION="$2"; shift 2 ;;
    --direction=*) DIRECTION="${1#*=}"; shift ;;
    *) shift ;;
  esac
done

if [ -z "$DIRECTION" ]; then
  echo "ERROR: --direction <c28-a|c28-b|c28-c> is required" >&2
  exit 2
fi

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "C28 direction: $DIRECTION (ts=$TS)"

echo "--- prereg ---"
PREREG="research_state/c28_prereg_${TS}.json"
if [ -f "$PREREG" ]; then
  echo "  present: $PREREG"
  "$PY" -c "import json,sys; p=json.load(open('$PREREG')); print('  status:', p.get('prereg_status')); print('  direction:', p.get('direction')); print('  title:', p.get('title'))" 2>/dev/null || echo "  (unreadable)"
else
  echo "  missing: $PREREG  -> run: PYTHONPATH=. .venv/bin/python scripts/build_c28_prereg.py --direction $DIRECTION"
fi

echo "--- runner ---"
. "$REPO/scripts/runner_alive.sh"
if runner_alive "run_c28_campaign.py --direction ${DIRECTION}"; then
  echo "RUNNER: ALIVE"
  runner_ps "run_c28_campaign.py --direction ${DIRECTION}"
else
  echo "RUNNER: NOT ALIVE -> launch once with: background_process start command=\"bash scripts/run_c28_durable.sh --direction $DIRECTION\" persistent=true"
fi

echo "--- arm/venue/fold cells (a cell is DONE only when its ckpt exists) ---"
ARMS=$("$PY" -c "import json; p=json.load(open('research_state/c28_prereg_${TS}.json')); print(','.join(p['arms']))" 2>/dev/null || echo "")
if [ -z "$ARMS" ]; then
  echo "  (cannot enumerate arms; prereg missing or unreadable)"
else
  for arm in $(echo "$ARMS" | tr ',' ' '); do
    done=0
    total=0
    for v in okx binance_um mexc bitget; do
      for f in 2023 2024 2025 2026YTD; do
        total=$((total + 1))
        [ -f "research_state/c28_ckpt_${DIRECTION}_${arm}_${v}_${f}_${TS}.json" ] && done=$((done + 1))
      done
    done
    echo "  ${arm}: ${done}/${total}"
  done
fi

echo "--- artifacts ---"
for a in c28_prereg c28_decision_verdict_CONSOLIDATED; do
  [ -f "research_state/${a}_${TS}.json" ] && echo "  present: ${a}_${TS}.json" || echo "  missing: ${a}_${TS}.json"
done
for arm in $ARMS; do
  [ -f "research_state/c28_decision_verdict_${arm}_${TS}.json" ] && echo "  present: c28_decision_verdict_${arm}_${TS}.json" || echo "  missing: c28_decision_verdict_${arm}_${TS}.json"
done

echo "--- gate ---"
if [ -x "$PY" ] && [ -f scripts/verify_c28_focus_campaign.py ]; then
  PYTHONPATH=. "$PY" scripts/verify_c28_focus_campaign.py --direction "$DIRECTION" 2>&1 | head -12
else
  echo "  missing venv ($PY) or gate script; run: bash scripts/bootstrap_env.sh"
fi
