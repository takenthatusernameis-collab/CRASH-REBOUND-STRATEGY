# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T06:27:33Z — C21 COMPLETE; GATE PASS; NO ACTIVE RUNNER; NO UNCOMMITTED CHANGES)

**Authoritative durable handoff:** `HANDOFF.md` (single source of truth). This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication (OKX + Binance UM). C1–C20 CLOSED & CERTIFIED `NO_GO`. **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). No relabeling, no C20 relaunch, no same-data C22+, no draw-count reduction.

**Verified snapshot (2026-11-18T06:27:33Z):**
- C21 gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → **`C21 ACCEPTANCE: PASS`** (13/13 checks: prereg, artifacts_present 12/12, okx/binance fold campaigns trades=113 pnl=-54799.23 / trades=136 pnl=-70071.39, episode edges bootstrap=20000 permutation=20000, placebos runs=2000, censuses, per-venue verdicts token=NO_GO both, pooled synthesis draws=20000 token=NO_GO, consolidated final=NO_GO ts=2026-11-18T06:15:08Z).
- Closure: `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed` (Phase O `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; `scripts/probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION` (full_window_served=false, earliest_served=2026-04-23T19:00:00Z).
- **No active runner** (`ps` empty for `run_c21_cross_venue_campaign.py`); none needed (`research_state/c21_run_20261118T061505Z.log` ends `C21 COMPLETE`).
- **No uncommitted changes** (`git status` clean; only prior chore commits present). Do not commit unless explicitly asked.

**Immediate next action (verification only, no campaign work):**
1. Confirm gate → `C21 ACCEPTANCE: PASS`.
2. Confirm artifacts: `ls research_state/c21_ckpt_* | wc -l` → 8; `ls research_state/c21_*_20261117T064408Z.json | grep -v prereg | grep -v ckpt | wc -l` → 12.
3. Await explicit operator direction for anything beyond C21 (new prereg + new data required). Do not plan, rewrite, or relaunch campaigns without authorization. Do not commit unless explicitly asked.

Full binding spec, guardrails, acceptance tokens, file map: `HANDOFF.md`.

(End of file - total 17 lines)