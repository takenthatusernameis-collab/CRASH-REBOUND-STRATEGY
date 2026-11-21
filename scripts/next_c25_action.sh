#!/usr/bin/env bash
# Session entry probe for the C25 -> C26 -> C27 heavy queue.
#
# Purpose: collapse "read the handoff, run three scripts, reason about the gate"
# into one command that prints exactly one ACTION line and, where possible, the
# exact command to run next. It never launches, never kills, never blocks, and
# never writes campaign state. It is safe to run at the top of every session.
#
# Two bottlenecks this file removes (fixed 2026-11-21T10:20Z):
#   1. It used to match "*ALIVE*" against the status line, so the string
#      "RUNNER: NOT ALIVE" was read as ALIVE and the probe told a fresh session
#      to do nothing while the runner was dead. Dead-runner detection now runs
#      first and matches the explicit NOT ALIVE token.
#   2. It used to derive pacing from scripts/eta_c25.sh, which exits 1 when the
#      durable venv is missing (every fresh CI job starts without .venv). That
#      made remaining=0 -> wake_after=0s and hid the real 48-cell backlog.
#      Remaining cells are now counted from on-disk checkpoints in pure bash, so
#      pacing and the resume decision work with or without a venv.
#
# Usage: bash scripts/next_c25_action.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261119T045500Z"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

status_line="$(bash scripts/status_c25.sh 2>/dev/null | grep -m1 '^RUNNER:')"
runner_line="${status_line#RUNNER: }"
have_venv=0
[ -x "$PY" ] && have_venv=1

if [ "$have_venv" -eq 1 ]; then
  gate_c25="$(PYTHONPATH=. "$PY" scripts/verify_c25_focus_campaign.py 2>/dev/null | grep -m1 '^C25 ACCEPTANCE:')"
  gate_c26="$(PYTHONPATH=. "$PY" scripts/verify_c26_focus_campaign.py 2>/dev/null | grep -m1 '^C26 ACCEPTANCE:')"
  anchor="$(bash scripts/check_c25_anchor.sh 2>/dev/null | grep -m1 '^ANCHOR:')"
else
  gate_c25=""
  gate_c26=""
  anchor=""
fi

# --- remaining cells, counted from checkpoints (no venv required) ------------
real_remaining=0
skipped=0
for arm in cost_base cost_taker cost_taker_funding cost_stress; do
  for v in okx binance_um mexc bitget; do
    for f in 2023 2024 2025 2026YTD; do
      ck="research_state/c25_ckpt_${arm}_${v}_${f}_${TS}.json"
      if [ -f "$ck" ]; then
        if grep -q '"unavailable_funding"' "$ck" 2>/dev/null; then
          skipped=$((skipped + 1))
        fi
      else
        # okx has no realized funding history (OKX_FUNDING_BLOCKED_BY_API_RETENTION):
        # the two funding arms are instant UNAVAILABLE_FUNDING skips, not compute.
        if [ "$v" = "okx" ] && { [ "$arm" = "cost_taker_funding" ] || [ "$arm" = "cost_stress" ]; }; then
          skipped=$((skipped + 1))
        else
          real_remaining=$((real_remaining + 1))
        fi
      fi
    done
  done
done

# In-flight draw chunks (research_state/c25_draw_ckpts/) are a finer progress
# signal than cell checkpoints: a cell mid-permutation has no cell ckpt yet.
inflight_chunks="$(ls research_state/c25_draw_ckpts/ 2>/dev/null | grep -c 'c25_partial_perm' || true)"
inflight_cell="$(ls research_state/c25_draw_ckpts/ 2>/dev/null | grep -o 'c25_partial_perm_[a-z_]*_[a-z_]*_[0-9]*' | head -1 | sed 's/^c25_partial_perm_//')"

echo "RUNNER: ${runner_line:-UNKNOWN}"
echo "GATE:   ${gate_c25:-C25 ACCEPTANCE: UNKNOWN$([ "$have_venv" -eq 1 ] || echo ' (no venv)')}"
echo "GATE:   ${gate_c26:-C26 ACCEPTANCE: UNKNOWN}"
if [ -n "$anchor" ]; then
  echo "ANCHOR: ${anchor#ANCHOR: }"
elif [ "$have_venv" -eq 1 ]; then
  echo "ANCHOR: UNKNOWN"
else
  echo "ANCHOR: UNKNOWN (no venv; bootstrap to enable the anchor check)"
fi
echo "PROGRESS: real_cells_remaining=${real_remaining} skipped_unavailable_funding=${skipped} draw_chunks_on_disk=${inflight_chunks} in_flight=${inflight_cell:-none}"

# --- pacing -------------------------------------------------------------------
# The tier is derived from ground truth (remaining cells), never from a guess.
wake_after="8h"
wake_why=">6 cells left; 4 saturated cores at ~1.6 h/cell"
if [ "$real_remaining" -eq 0 ]; then
  wake_after="0s"
  wake_why="no real cells left; act in this turn, do not suspend"
elif [ "$real_remaining" -le 2 ]; then
  wake_after="90m"
  wake_why="<=2 cells left; detect the C25 gate within ~1.5 h of PASS"
elif [ "$real_remaining" -le 6 ]; then
  wake_after="4h"
  wake_why="<=6 cells left; detect the C25 gate within ~4 h of PASS"
fi

echo "PACING: remaining=${real_remaining} draw_chunks=${inflight_chunks} wake_after=${wake_after} (${wake_why})"

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
        if [[ "$runner_line" == *"NOT ALIVE"* ]]; then
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

if [[ "$anchor" == *"MISMATCH"* ]]; then
  emit "P0_STOP_ANCHOR_MISMATCH" \
    "  bash scripts/check_c25_anchor.sh" \
    "  record evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg."
fi

# Dead runner first: "NOT ALIVE" contains the substring "ALIVE", so the old
# ordering silently swallowed every resume.
if [[ "$runner_line" == *"NOT ALIVE"* ]]; then
  if [ "$have_venv" -eq 0 ]; then
    emit "RESUME_C25" \
      "  .venv is missing (fresh CI job). run_c25_durable.sh now bootstraps it:" \
      "  background_process start command=\"bash scripts/run_c25_durable.sh\" persistent=true" \
      "  then: bash scripts/status_c25.sh"
  fi
  emit "RESUME_C25" \
    "  background_process start command=\"bash scripts/run_c25_durable.sh\" persistent=true" \
    "  then: bash scripts/status_c25.sh"
fi

if [[ "$runner_line" == *"ALIVE"* ]]; then
  emit "NONE_RUNNER_ALIVE" \
    "  Next: bash scripts/check_c25_anchor.sh" \
    "  Then (600000 ms tool timeout): bash -c 'sleep 540; bash scripts/next_c25_action.sh'" \
    "  Do not end this session before that bounded wait completes." \
    "  Do not relaunch, do not kill, do not start C26/C27, do not add CPU work."
fi

emit "RESUME_C25" \
  "  runner state unknown; re-run status_c25.sh before any launch" \
  "  background_process start command=\"bash scripts/run_c25_durable.sh\" persistent=true"