#!/usr/bin/env bash
# One-shot, read-only C24 status probe. Never launches, never kills, never blocks.
# Usage: bash scripts/status_c24.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
TS="20261119T013154Z"

echo "UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

echo "--- runner ---"
if pgrep -af "run_c24_margin_fidelity_campaign.py" >/dev/null 2>&1; then
  echo "RUNNER: ALIVE"
  ps -eo pid,ppid,etime,time,stat,cmd | grep "[r]un_c24_margin_fidelity_campaign.py" || true
else
  echo "RUNNER: NOT ALIVE -> resume with: PYTHONPATH=. .venv/bin/python scripts/run_c24_margin_fidelity_campaign.py --jobs 4 --resume"
fi

echo "--- arm/venue/fold cells (a cell is DONE only when its ckpt exists) ---"
for arm in base_6 d10 d15 d30 noliq; do
  done=0
  for v in okx binance_um mexc bitget; do
    for f in 2023 2024 2025 2026YTD; do
      [ -f "research_state/c24_ckpt_${arm}_${v}_${f}_${TS}.json" ] && done=$((done + 1))
    done
  done
  echo "  ${arm}: ${done}/16"
done

echo "--- d15 inference (primary arm; 20k/20k/2k floors) ---"
for v in okx binance_um mexc bitget; do
  for f in 2023 2024 2025 2026YTD; do
    p="research_state/c24_ckpt_d15_${v}_${f}_${TS}.json"
    if [ -f "$p" ]; then
      "$PY" - "$p" <<'EOF' 2>/dev/null || echo "    ${v}/${f}: unreadable"
import json,sys
d=json.load(open(sys.argv[1]))
ep=d.get("episode") or {}
boot=(ep.get("episode_block_bootstrap") or {})
perm=(ep.get("temporal_edge_permutation") or {})
print(f"    {d['venue']}/{d['fold']}: pnl={round((d.get('campaign_artifact') or {}).get('results',{}).get('total_pnl',float('nan')),2)} "
      f"boot={boot.get('resamples')} perm={perm.get('draws_evaluated')} "
      f"perm_p={ep.get('perm_p')} "
      f"placebo={((d.get('placebo') or {}).get('placebo') or {}).get('runs')} "
      f"placebo_p_ge={(((d.get('placebo') or {}).get('placebo') or {}).get('p_ge_canonical'))}")
EOF
    else
      echo "    ${v}/${f}: pending"
    fi
  done
done

echo "--- artifacts ---"
for a in c24_prereg c24_liquidation_fidelity_probe c24_decision_verdict_base_6 \
         c24_decision_verdict_d15 c24_decision_verdict_d10 c24_decision_verdict_d30 \
         c24_decision_verdict_noliq c24_decision_verdict_CONSOLIDATED; do
  [ -f "research_state/${a}_${TS}.json" ] && echo "  present: ${a}_${TS}.json" || echo "  missing: ${a}_${TS}.json"
done

echo "--- gate ---"
if [ -x "$PY" ] && [ -f scripts/verify_c24_focus_campaign.py ]; then
  PYTHONPATH=. "$PY" scripts/verify_c24_focus_campaign.py 2>&1 | head -6
else
  echo "  missing venv ($PY) or gate script; run: bash scripts/bootstrap_env.sh"
fi
