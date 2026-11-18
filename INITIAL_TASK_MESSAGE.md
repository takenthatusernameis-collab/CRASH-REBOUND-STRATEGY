# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T06:25:11Z — C21 COMPLETE; GATE PASS; NO ACTIVE RUNNER)

**Authoritative durable handoff:** `HANDOFF.md` (single source of truth). This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication (OKX + Binance UM). C1–C20 CLOSED & CERTIFIED `NO_GO`. **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). No relabeling, no C20 relaunch, no same-data C22+, no draw-count reduction.

**Verified snapshot (2026-11-18T06:22:58Z):**
- C21 gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → **`C21 ACCEPTANCE: PASS`** (12/12 artifacts, 8/8 checkpoints, pooled=NO_GO, ts=2026-11-18T06:15:08Z).
- Closure: `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed`.
- No runner active; none needed (`research_state/c21_run_20261118T061505Z.log` ends `C21 COMPLETE`).

**Immediate next action (verification only, no campaign work):**
1. Confirm gate → `C21 ACCEPTANCE: PASS`.
2. Confirm artifacts: `ls research_state/c21_ckpt_* | wc -l` → 8; `ls research_state/c21_*_20261117T064408Z.json | grep -v prereg | grep -v ckpt | wc -l` → 12.
3. Await explicit operator direction for anything beyond C21 (new prereg + new data required). Do not plan, rewrite, or relaunch campaigns without authorization. Do not commit unless explicitly asked.

Full binding spec, guardrails, acceptance tokens, file map: `HANDOFF.md`.