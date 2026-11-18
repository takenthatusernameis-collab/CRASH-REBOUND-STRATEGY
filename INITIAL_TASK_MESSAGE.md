# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T00:03:17Z — C21 INCOMPLETE; DO NOT DUPLICATE)

**Authoritative durable handoff:** `HANDOFF.md` (single source of truth). This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication (OKX + Binance UM). C1–C20 CLOSED & CERTIFIED `NO_GO`. **Only open binding work: C21-T1** (temporal/regime stability across prereg folds/strata). No avoidable relabeling to new campaigns without new prereg+data+authorization.

**Verified snapshot (2026-11-17T23:59:50Z, from repo):**
- C21 artifacts present (stamp `20261117T064408Z`): **5/8 checkpoints** (`c21_ckpt_okx_2023/2024/2025/2026YTD`, `c21_ckpt_binance_um_2023`). **5/12 gate artifacts**: `c21_okx_fold_{census,episode_edge,placebo,campaign}_...json`, `c21_decision_verdict_okx_stability_...json` (OKX NO_GO, survivors=0, trades=113, pnl=-54799.23).
- Missing (gate RED): Binance UM folds 2024/2025/2026YTD artifacts, `c21_binance_um_stability_verdict_...`, `c21_pooled_stability_synthesis_...`, `c21_decision_verdict_CONSOLIDATED_...`.
- Expected gate now: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` until all 12 + verdicts + synthesis + consolidated exist.

**Immediate next action (do this, in order):**
1. **Check runner:** `ps -eo pid,ppid,etime,time,stat,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep`. If any live C21 runner is present (R/S with children), **do not start another**; monitor to completion (see commands in `HANDOFF.md`).
2. If **no** live runner: `bash scripts/run_c21_detached_durable.sh` (run from a shell command line that does **not** contain that script name string), then monitor logs/checkpoints/artifacts to `C21 ACCEPTANCE: PASS`.
3. On `PASS`: run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py`; update `HANDOFF.md` timestamp/tokens if needed. **Do not reduce draw counts, hand-fabricate artifacts, or commit unless explicitly asked.**

Full binding details, guardrails, file map: `HANDOFF.md`.
