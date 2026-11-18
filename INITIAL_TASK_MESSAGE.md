# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T00:55:29Z — C21 INCOMPLETE; MONITOR/RESUME ONLY)

**Authoritative durable handoff:** `HANDOFF.md` (single source of truth). This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication (OKX + Binance UM). C1–C20 CLOSED & CERTIFIED `NO_GO`. **Only open binding work: C21-T1** (temporal/regime stability across prereg folds/strata, `c21_prereg_20261117T064408Z`). No relabeling, no C20 relaunch, no same-data C22+, no draw-count reduction.

**Verified snapshot (2026-11-18T00:55:29Z):**
- Canonical C21 runner **live**: PID 21945, `--jobs 4 --resume`, ~2h55m wall, 4 R-state child workers ~380% CPU total. **No duplicate runner.**
- Checkpoints **6/8**: `c21_ckpt_okx_{2023,2024,2025,2026YTD}`, `c21_ckpt_binance_um_{2023,2024}` (stamp `20261117T064408Z`).
- Required gate artifacts **5/12**: OKX fold bundle (`campaign/census/episode_edge/placebo`) + `c21_decision_verdict_okx_stability_20261117T064408Z.json` (`NO_GO`, survivors=0, trades=113, pnl=-54799.23).
- Progress: Binance UM 2023/2024 fold checkpoints written (log: 2023 trades=28 pnl=+34989.90; 2024 trades=43 pnl=-33586.83). **Binance UM fold 2025 in progress** (log: trades=41 pnl=-42040.50, fast-path validations active); fold 2026YTD pending, then Binance verdict + `c21_pooled_stability_synthesis_*` + `c21_decision_verdict_CONSOLIDATED_*`.
- Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → **`C21 ACCEPTANCE: FAIL`** (8 missing: `c21_binance_um_fold_{campaign,episode_edge,placebo,census}_*`, `c21_decision_verdict_binance_um_stability_*`, `c21_pooled_stability_synthesis_*`, `c21_decision_verdict_CONSOLIDATED_*`).

**Immediate next action (heavy execution only):**
1. **Confirm runner:** `ps -eo pid,ppid,etime,time,stat,pcpu,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep`. If live with child workers, **do not start another** — monitor to completion.
2. **Monitor:** `ls research_state/c21_ckpt_* | wc -l` (→8), count gate artifacts `ls research_state/c21_*_20261117T064408Z.json | grep -v prereg | grep -v ckpt | wc -l` (→12), `tail -n 50 research_state/c21_run_20261117T215941Z.log`, and rerun verifier to `C21 ACCEPTANCE: PASS`.
3. **Only if no runner alive:** `bash scripts/run_c21_detached_durable.sh` from a command line that does **not** contain that script name string, then monitor to `PASS`.
4. **On `PASS`:** `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py`; update `HANDOFF.md` timestamps/tokens. **Do not commit unless explicitly asked.**

Full binding spec, guardrails, acceptance tokens, file map: `HANDOFF.md`.
