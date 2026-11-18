#!/usr/bin/env bash
# One-shot, read-only C23 status probe. Never launches, never kills, never blocks.
# Usage: bash scripts/status_c23.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261118T202301Z"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "--- runner (parent PID persists; Pool workers rotate every permutation batch) ---"
if pgrep -af "run_c23_bitget_campaign.py" >/dev/null 2>&1; then
  echo "RUNNER: ALIVE"
  ps -eo pid,ppid,etime,time,stat,cmd | grep "[r]un_c23_bitget_campaign.py" || true
else
  echo "RUNNER: NOT ALIVE -> resume with: bash scripts/run_c23_detached_durable.sh"
fi

echo "--- fold checkpoints (a fold is DONE only when its ckpt file exists) ---"
for f in 2023 2024 2025 2026YTD; do
  p="research_state/c23_ckpt_bitget_${f}_${TS}.json"
  if [ -f "$p" ]; then
    echo "  $f: DONE   $p"
  else
    echo "  $f: pending"
  fi
done

echo "--- newest run log ---"
LOG="$(ls -1t research_state/c23_run_*.log 2>/dev/null | head -1 || true)"
if [ -n "${LOG:-}" ]; then
  echo "  $LOG (mtime $(date -u -r "$LOG" +%Y-%m-%dT%H:%M:%SZ))"
  tail -2 "$LOG" | sed 's/^/  | /'
else
  echo "  none"
fi

echo "--- battery artifacts ---"
n=0
for a in c23_bitget_fold_campaign c23_bitget_fold_episode_edge c23_bitget_fold_placebo \
         c23_bitget_fold_census c23_decision_verdict_bitget_stability \
         c23_pooled_stability_synthesis c23_decision_verdict_CONSOLIDATED; do
  if [ -f "research_state/${a}_${TS}.json" ]; then n=$((n + 1)); fi
done
echo "  present: ${n}/7 (battery artifacts are written only after ALL 4 folds finish)"

echo "--- gate ---"
if [ -x "$PY" ] && [ -f scripts/verify_c23_focus_campaign.py ]; then
  PYTHONPATH=. "$PY" scripts/verify_c23_focus_campaign.py 2>&1 | tail -1
else
  echo "  missing venv ($PY) or gate script; run: bash scripts/bootstrap_env.sh"
fi
