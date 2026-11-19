#!/usr/bin/env bash
# Read-only C25 progress + ETA probe. NEVER launches, resumes, or kills anything.
#
# Why this exists: one C25 inference cell costs hours on this 4-core box
# (20k conditional-permutation portfolio replays at ~3 core-seconds each plus a
# 2k full-portfolio placebo). Sessions used to poll the log and hand-estimate
# progress, which is what produced the contradictory "0/64" vs "1/64" handoff
# states. This prints the single truth plus a self-calibrating ETA.
#
# Usage: bash scripts/eta_c25.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

"$PY" - <<'EOF'
import datetime as dt
import json
from pathlib import Path

STATE = Path("research_state")
TS = "20261119T045500Z"
ARMS = ["cost_base", "cost_taker", "cost_taker_funding", "cost_stress"]
VENUES = ["okx", "binance_um", "mexc", "bitget"]
FOLDS = ["2023", "2024", "2025", "2026YTD"]

done, skipped, missing = [], [], []
for arm in ARMS:
    for venue in VENUES:
        for fold in FOLDS:
            p = STATE / f"c25_ckpt_{arm}_{venue}_{fold}_{TS}.json"
            if not p.exists():
                missing.append((arm, venue, fold))
                continue
            ck = json.loads(p.read_text())
            if ck.get("unavailable_funding"):
                skipped.append((arm, venue, fold))
                continue
            perm = (ck.get("episode") or {}).get("temporal_edge_permutation") or {}
            done.append((arm, venue, fold, float(perm.get("wall_seconds") or 0.0),
                         int(perm.get("draws_evaluated") or 0)))

# okx funding arms can never run: UNAVAILABLE_FUNDING (retention wall). They are
# written as instant skip checkpoints, so they do not consume compute.
funding_arms = {"cost_taker_funding", "cost_stress"}
future_skips = sum(1 for a, v, f in missing if v == "okx" and a in funding_arms)
real_remaining = len(missing) - future_skips

now = dt.datetime.now(dt.timezone.utc)
print(f"UTC: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")
print(f"cells complete (real inference): {len(done)}/56    "
      f"skipped UNAVAILABLE_FUNDING: {len(skipped) + future_skips}/8    "
      f"pending: {len(missing)}")
print(f"real inference cells still to compute: {real_remaining}")

walls = sorted(w for *_, w, _ in done if w > 0)
if walls:
    med = walls[len(walls) // 2]
    # Calibration from the first completed cell: perm 11,510 s + placebo 1,458 s.
    per_cell = med * 1.127
    eta_h = real_remaining * per_cell / 3600.0
    finish = now + dt.timedelta(hours=eta_h)
    print(f"median permutation wall per completed cell: {med/3600.0:.2f} h")
    print(f"per-cell estimate (perm + placebo): {per_cell/3600.0:.2f} h")
    print(f"ETA: {eta_h:.1f} h -> ~{finish.strftime('%Y-%m-%dT%H:%M:%SZ')} "
          f"(+/- 30%; 4-core box, shared runner)")
else:
    print("ETA: unknown (no completed real cell yet; measured budget 3.6 h/cell)")

if done:
    print("last completed:", " ".join(str(x) for x in done[-3:]))
if missing:
    print("next cells:", ", ".join(f"{a}/{v}/{f}" for a, v, f in missing[:4]))
print("NOTE: one cell runs at a time; only its 20k/2k draws use 4 worker processes.")
print("NOTE: never relaunch or kill while the runner is ALIVE; see HANDOFF.md.")
EOF
