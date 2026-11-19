#!/usr/bin/env bash
# One-shot, read-only C26 status probe. Never launches, never kills, never blocks.
# Usage: bash scripts/status_c26.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261119T121500Z"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "--- runner ---"
if pgrep -af "run_c26_path_fidelity_campaign.py" >/dev/null 2>&1; then
  echo "RUNNER: ALIVE"
  ps -eo pid,ppid,etime,time,stat,cmd | grep "[r]un_c26_path_fidelity_campaign.py" || true
else
  echo "RUNNER: NOT ALIVE -> launch once with: background_process start command=\"bash scripts/run_c26_durable.sh\" persistent=true"
fi

echo "--- arm/venue/fold cells (a cell is DONE only when its ckpt exists) ---"
for arm in path_base path_funding_trade path_intrabar_adverse_first path_intrabar_combined; do
  done=0
  for v in okx binance_um mexc bitget; do
    for f in 2023 2024 2025 2026YTD; do
      [ -f "research_state/c26_ckpt_${arm}_${v}_${f}_${TS}.json" ] && done=$((done + 1))
    done
  done
  echo "  ${arm}: ${done}/16"
done

echo "--- intrabat path / per-trade funding inference (all arms; 20k/20k/2k floors) ---"
for arm in path_base path_funding_trade path_intrabar_adverse_first path_intrabar_combined; do
  for v in okx binance_um mexc bitget; do
    for f in 2023 2024 2025 2026YTD; do
      p="research_state/c26_ckpt_${arm}_${v}_${f}_${TS}.json"
      if [ -f "$p" ]; then
        "$PY" - "$p" <<'EOF' 2>/dev/null || echo "    ${arm}/${v}/${f}: unreadable"
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("unavailable_funding"):
    print(f"    {d['arm']}/{d['venue']}/{d['fold']}: UNAVAILABLE_FUNDING")
else:
    ep=d.get("episode") or {}
    print(f"    {d['arm']}/{d['venue']}/{d['fold']}: boot={(ep.get('episode_block_bootstrap') or {}).get('resamples')} "
          f"perm={(ep.get('temporal_edge_permutation') or {}).get('draws')} "
          f"placebo={((d.get('placebo') or {}).get('placebo') or {}).get('runs')} "
          f"ptf={d.get('config',{}).get('per_trade_funding')} iaf={d.get('config',{}).get('intrabar_adverse_first')}")
EOF
      else
        echo "    ${arm}/${v}/${f}: pending"
      fi
    done
  done
done

echo "--- artifacts ---"
for a in c26_prereg c26_decision_verdict_path_base c26_decision_verdict_path_funding_trade \
         c26_decision_verdict_path_intrabar_adverse_first c26_decision_verdict_path_intrabar_combined \
         c26_decision_verdict_CONSOLIDATED; do
  [ -f "research_state/${a}_${TS}.json" ] && echo "  present: ${a}_${TS}.json" || echo "  missing: ${a}_${TS}.json"
done

echo "--- gate ---"
if [ -x "$PY" ] && [ -f scripts/verify_c26_focus_campaign.py ]; then
  PYTHONPATH=. "$PY" scripts/verify_c26_focus_campaign.py 2>&1 | head -8
else
  echo "  missing venv ($PY) or gate script; run: bash scripts/bootstrap_env.sh"
fi
