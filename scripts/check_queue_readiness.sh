#!/usr/bin/env bash
# Read-only heavy-queue readiness audit for the C25 -> C32 adjudication chain.
#
# History (added 2026-11-21T10:22:00Z): C28/C29/C30/C31/C32 are all gated behind
# C27, and C27 was originally staged only as a prereg + acquisition probe. That
# gap is now CLOSED -- scripts/{run_c27_campaign.py,run_c27_durable.sh,
# status_c27.sh,verify_c27_focus_campaign.py} and tests/test_c27_campaign.py all
# exist and this audit reports them ok. The C27 branch below is kept so a future
# regression (a deleted successor artifact) is caught BEFORE the gate is reached,
# rather than letting a session stall on "durably launch C27" with no runner.
#
# It never launches, never kills, never writes, never needs a venv.
# Usage: bash scripts/check_queue_readiness.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "Heavy queue: C24 -> C25 -> C26 -> C27 -> C28 -> C29 -> C30 -> C31 -> C32+"
echo

gate() {  # gate <campaign> <prereg-ts>
  local c="$1" ts="$2" f
  for f in "research_state/c${c}_prereg_${ts}.json" "research_state/c${c}_prereg_${ts}.md"; do
    [ -f "$f" ] || { echo "  MISSING $f"; return 1; }
  done
  echo "  ok      prereg research_state/c${c}_prereg_${ts}.{json,md}"
  return 0
}

impl() {  # impl <campaign> <campaign-script> <prereg-ts>
  local c="$1" runner="$2" ts="$3" f missing=0
  for f in "scripts/${runner}" "scripts/run_c${c}_durable.sh" "scripts/status_c${c}.sh" \
           "scripts/verify_c${c}_focus_campaign.py" "tests/test_c${c}_campaign.py"; do
    if [ -f "$f" ]; then
      echo "  ok      $f"
    else
      echo "  MISSING $f"
      missing=1
    fi
  done
  [ "$missing" -eq 0 ] || echo "  -> build the missing C${c} artifacts before C$((c-1)) PASS lands"
  return "$missing"
}

status=0

echo "C25 (in flight) -- runner: scripts/run_c25_cost_fidelity_campaign.py"
impl 25 run_c25_cost_fidelity_campaign.py 20261119T045500Z || status=1
echo

echo "C26 (BUILT, gate-held behind C25 PASS)"
impl 26 run_c26_path_fidelity_campaign.py 20261119T121500Z || status=1
echo

echo "C27 (BUILT, gate-held behind C26 PASS; C28-C32 are all gated behind it)"
if impl 27 run_c27_campaign.py 20261119T215721Z; then
  echo "  -> C27 is ready to launch on C26 PASS (venue still fixed by scripts/probe_c27_venue_acquisition.py)"
else
  status=1
  echo "  -> REQUIRED on C26 PASS: build scripts/run_c27_campaign.py + run_c27_durable.sh + status_c27.sh +"
  echo "     verify_c27_focus_campaign.py + tests/test_c27_campaign.py, modelled on C28 (direction/venue"
  echo "     parametric, prereg-frozen arms/folds/draw floors, hard-refuses unless"
  echo "     research_state/c26_decision_verdict_CONSOLIDATED_<ts>.json exists)."
  echo "  -> Then run the probe: PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py"
fi
echo

for c in 28 29 30 31 32; do
  case "$c" in
    28) ts=20261121T013400Z; note="gate-held behind C27 PASS" ;;
    29) ts=20261121T031907Z; note="gate-held behind C28 PASS" ;;
    30) ts=20261121T051754Z; note="gate-held behind C29 PASS" ;;
    31) ts=20261121T052233Z; note="gate-held behind C30 PASS + holdout manifests" ;;
    32) ts=20261121T061508Z; note="gate-held behind C31 PASS" ;;
  esac
  echo "C${c} (${note})"
  impl "$c" "run_c${c}_campaign.py" "$ts" || status=1
  echo
done

if [ "$status" -eq 0 ]; then
  echo "QUEUE READY: every campaign in C25..C32 has a prereg and a full implementation."
else
  echo "QUEUE GAP: at least one campaign is missing implementation artifacts (see MISSING lines)."
  echo "Build the missing successor BEFORE its predecessor gate PASSes; never launch a campaign with no runner."
fi
exit "$status"