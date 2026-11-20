#!/usr/bin/env bash
# Read-only decision probe for the C25 -> C26 -> C27 heavy queue.
#
# Purpose: collapse "read the handoff, run three scripts, reason about the gate"
# into one command that prints exactly one ACTION line and, where possible, the
# exact command to run next. It never launches, never kills, never blocks, and
# never writes state.
#
# Usage: bash scripts/next_c25_action.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

runner_line="$(bash scripts/status_c25.sh 2>/dev/null | sed -n 's/^--- runner ---$//p;' >/dev/null; bash scripts/status_c25.sh 2>/dev/null | grep -m1 '^RUNNER:')"
gate_c25="$(PYTHONPATH=. "$PY" scripts/verify_c25_focus_campaign.py 2>/dev/null | grep -m1 '^C25 ACCEPTANCE:')"
gate_c26="$(PYTHONPATH=. "$PY" scripts/verify_c26_focus_campaign.py 2>/dev/null | grep -m1 '^C26 ACCEPTANCE:')"
anchor="$(bash scripts/check_c25_anchor.sh 2>/dev/null | grep -m1 '^ANCHOR:')"

echo "RUNNER: ${runner_line#RUNNER: }"
echo "GATE:   ${gate_c25:-C25 ACCEPTANCE: UNKNOWN}"
echo "GATE:   ${gate_c26:-C26 ACCEPTANCE: UNKNOWN}"
echo "ANCHOR: ${anchor#ANCHOR: }"

emit() {
  echo "ACTION: $1"
  shift
  for line in "$@"; do echo "$line"; done
  exit 0
}

case "$gate_c25" in
  *"ACCEPTANCE: PASS"*)
    case "$gate_c26" in
      *"ACCEPTANCE: PASS"*)
        emit "PROBE_AND_LAUNCH_C27" \
          "  1. PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py" \
          "  2. confirm the prereg research_state/c27_prereg_20261119T215721Z.{json,md} still matches the probe verdict" \
          "  3. then launch the C27 campaign (see HANDOFF.md step 6)"
        ;;
      *"ACCEPTANCE: FAIL"*)
        emit "FIX_C26_INTEGRITY" \
          "  PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py" \
          "  fix only the failing integrity condition; never force PASS (HANDOFF.md step 4)"
        ;;
      *)
        if [[ "${runner_line:-}" == *"NOT ALIVE"* ]]; then
          emit "LAUNCH_C26" \
            "  background_process start command=\"bash scripts/run_c26_durable.sh\" persistent=true" \
            "  then: bash scripts/status_c26.sh"
        else
          emit "NONE_C26_RUNNER_ALIVE" \
            "  Do not relaunch, do not kill, do not start C27. Checkpoint progress is the only state."
        fi
        ;;
    esac
    ;;
  *"ACCEPTANCE: FAIL"*)
    emit "FIX_C25_INTEGRITY" \
      "  PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py" \
      "  fix only the failing integrity condition; never force PASS (HANDOFF.md step 4)"
    ;;
esac

if [[ "${anchor:-}" == *"MISMATCH"* ]]; then
  emit "P0_STOP_ANCHOR_MISMATCH" \
    "  bash scripts/check_c25_anchor.sh" \
    "  record evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg."
fi

if [[ "${runner_line:-}" == *"ALIVE"* ]]; then
  emit "NONE_RUNNER_ALIVE" \
    "  Do not relaunch, do not kill, do not start C26/C27, do not add CPU work." \
    "  Update HANDOFF.md only if the cell count or ETA materially changed, then end the turn."
fi

emit "RESUME_C25" \
  "  background_process start command=\"bash scripts/run_c25_durable.sh\" persistent=true" \
  "  then: bash scripts/status_c25.sh"
