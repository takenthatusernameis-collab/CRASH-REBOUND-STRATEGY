#!/usr/bin/env bash
# Read-only EARLY cost-anchor check for C25. NEVER launches, resumes, or kills.
#
# Why this exists: the frozen C25 fidelity arm cost_base MUST reproduce the C24
# d15 primary arm exactly (same engine, same liquidation distance, same cost
# model). Without an early check, a mismatch would only surface in the final
# acceptance gate after the other three arms have burned ~6 days of compute on a
# 4-core box. This checks the moment each cost_base cell lands, so a broken
# anchor can be caught after the first 16 cells (or sooner) instead of at the end.
#
# Usage: bash scripts/check_c25_anchor.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

"$PY" - <<'EOF'
import json
from pathlib import Path

STATE = Path("research_state")
C25_TS = "20261119T045500Z"
C24_TS = "20261119T013154Z"
VENUES = ["okx", "binance_um", "mexc", "bitget"]
FOLDS = ["2023", "2024", "2025", "2026YTD"]
TOL = 1.0  # must match verify_c25_focus_campaign.py

ref = json.loads((STATE / f"c24_decision_verdict_d15_{C24_TS}.json").read_text())
ref_totals = ref["venue_totals"]

print("C25 EARLY COST ANCHOR (cost_base vs C24 d15 primary)")
status = "OK"
done_cells = 0
for venue in VENUES:
    observed = 0.0
    expected = float(ref_totals[venue])
    missing = []
    mismatched = []
    for fold in FOLDS:
        p25 = STATE / f"c25_ckpt_cost_base_{venue}_{fold}_{C25_TS}.json"
        p24 = STATE / f"c24_ckpt_d15_{venue}_{fold}_{C24_TS}.json"
        if not p25.exists():
            missing.append(fold)
            continue
        ck = json.loads(p25.read_text())
        if ck.get("unavailable_funding"):
            missing.append(fold)
            continue
        pnl25 = float(ck["campaign_artifact"]["results"]["total_pnl"])
        observed += pnl25
        done_cells += 1
        pnl24 = float(json.loads(p24.read_text())["campaign_artifact"]["results"]["total_pnl"])
        if abs(pnl25 - pnl24) > 1e-6:
            mismatched.append(f"{fold}: {pnl25:.2f} != {pnl24:.2f}")
    if missing:
        state = f"INCOMPLETE ({len(missing)} folds: {','.join(missing)})"
        status = "INCOMPLETE" if status == "OK" else status
    elif mismatched:
        state = "MISMATCH " + " | ".join(mismatched)
        status = "MISMATCH"
    elif abs(observed - expected) > TOL:
        state = f"MISMATCH venue total {observed:.2f} != {expected:.2f}"
        status = "MISMATCH"
    else:
        state = f"EXACT {observed:.2f}"
    print(f"  {venue:<11} {state}")

print(f"cells checked: {done_cells}/16")
if status == "OK":
    print("ANCHOR: OK -> cost_base reproduces C24 d15 exactly; C25 is safe to continue.")
elif status == "MISMATCH":
    print("ANCHOR: MISMATCH -> C25 will be UNDERPOWERED. Do NOT let the remaining")
    print("        arms burn compute. Record the evidence, fix the cause, resume once.")
    print("        Never relax the draw floors or edit the prereg to force PASS.")
else:
    print("ANCHOR: INCOMPLETE -> keep the runner alive; re-run this after each cell.")
EOF
