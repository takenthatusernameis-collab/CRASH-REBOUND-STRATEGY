#!/usr/bin/env bash
# One-shot, read-only C27 status probe. Never launches, never kills, never blocks.
# Usage: bash scripts/status_c27.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261119T215721Z"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "C27 campaign: next independent USDT-perp venue replication (venue: kucoin) (ts=$TS)"

echo "--- prereg ---"
PREREG="research_state/c27_prereg_${TS}.json"
if [ -f "$PREREG" ]; then
  echo "  present: $PREREG"
  "$PY" -c "import json,sys; p=json.load(open('$PREREG')); print('  status:', p.get('prereg_status')); print('  campaign:', p.get('campaign')); print('  title:', p.get('title'))" 2>/dev/null || echo "  (unreadable)"
else
  echo "  missing: $PREREG  -> run: PYTHONPATH=. .venv/bin/python scripts/build_c27_prereg.py"
fi

echo "--- acquisition probe ---"
PROBE="research_state/c27_venue_acquisition_probe_${TS}.json"
if [ -f "$PROBE" ]; then
  echo "  present: $PROBE"
  "$PY" -c "import json,sys; p=json.load(open('$PROBE')); print('  status:', p.get('c27_data_status')); print('  primary:', p.get('recommendation',{}).get('primary_new_venue'))" 2>/dev/null || echo "  (unreadable)"
else
  echo "  missing: $PROBE  -> run: PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py"
fi

echo "--- gate dependency (C26 must PASS before any C27 cell) ---"
C26_CONSOLIDATED="research_state/c26_decision_verdict_CONSOLIDATED_20261119T121500Z.json"
if [ -f "$C26_CONSOLIDATED" ]; then
  echo "  present: $C26_CONSOLIDATED  (C26 ACCEPTANCE: PASS — C27 cells may run)"
else
  echo "  missing: $C26_CONSOLIDATED  (C26 ACCEPTANCE: PENDING — no C27 cell may run yet)"
fi

echo "--- runner ---"
if pgrep -af "run_c27_campaign.py --jobs" >/dev/null 2>&1; then
  echo "RUNNER: ALIVE"
  ps -eo pid,ppid,etime,time,stat,cmd | grep "[r]un_c27_campaign.py --jobs" || true
else
  echo "RUNNER: NOT ALIVE -> launch once with: background_process start command=\"bash scripts/run_c27_durable.sh\" persistent=true"
fi

echo "--- arm/venue/fold cells (a cell is DONE only when its ckpt exists) ---"
ARMS=$("$PY" -c "import json; p=json.load(open('research_state/c27_prereg_${TS}.json')); print(','.join(p.get('arms', {}).keys()))" 2>/dev/null || echo "path_base,cost_taker_funding,path_intrabar_combined")
if [ -z "$ARMS" ]; then
  echo "  (cannot enumerate arms; prereg missing or unreadable)"
else
  for arm in $(echo "$ARMS" | tr ',' ' '); do
    done=0
    total=0
    for v in kucoin; do
      for f in 2023 2024 2025 2026YTD; do
        total=$((total + 1))
        [ -f "research_state/c27_ckpt_${arm}_${v}_${f}_${TS}.json" ] && done=$((done + 1))
      done
    done
    echo "  ${arm}: ${done}/${total}"
  done
fi

echo "--- artifacts ---"
for a in c27_prereg c27_decision_verdict_CONSOLIDATED; do
  [ -f "research_state/${a}_${TS}.json" ] && echo "  present: ${a}_${TS}.json" || echo "  missing: ${a}_${TS}.json"
done
for arm in $ARMS; do
  [ -f "research_state/c27_decision_verdict_${arm}_${TS}.json" ] && echo "  present: c27_decision_verdict_${arm}_${TS}.json" || echo "  missing: c27_decision_verdict_${arm}_${TS}.json"
done

echo "--- gate ---"
if [ -x "$PY" ] && [ -f scripts/verify_c27_focus_campaign.py ]; then
  PYTHONPATH=. "$PY" scripts/verify_c27_focus_campaign.py 2>&1 | head -12
else
  echo "  missing venv ($PY) or gate script; run: bash scripts/bootstrap_env.sh"
fi
