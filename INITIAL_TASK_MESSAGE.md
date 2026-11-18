# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T01:10:37Z — C21 INCOMPLETE; MONITOR/RESUME ONLY)

**Authoritative durable handoff:** `HANDOFF.md` (single source of truth). This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication (OKX + Binance UM). C1–C20 CLOSED & CERTIFIED `NO_GO`. **Only open binding work: C21-T1** (temporal/regime stability across prereg folds/strata, `c21_prereg_20261117T064408Z`). No relabeling, no C20 relaunch, no same-data C22+, no draw-count reduction.

**Verified snapshot (2026-11-18T01:10:37Z):**
- Canonical C21 runner **live & healthy**: PID 21945, `--jobs 4 --resume`, ~3h10m wall, 4 R-state child workers (48951–48954, ~94–95% CPU each, ~380% total). **No duplicate runner.**
- Checkpoints **6/8**: `c21_ckpt_okx_{2023,2024,2025,2026YTD}`, `c21_ckpt_binance_um_{2023,2024}` (stamp `20261117T064408Z`).
- Required gate artifacts **5/12**: OKX fold bundle (`campaign/census/episode_edge/placebo`) + `c21_decision_verdict_okx_stability_20261117T064408Z.json` (`NO_GO`, survivors=0, trades=113, pnl=-54799.23).
- Progress: OKX complete (NO_GO). Binance UM 2023 (trades=28 pnl=+34989.90, perm_p=0.6606) and 2024 (trades=43 pnl=-33586.83, perm_p=0.7127) checkpoints/log complete. **Binance UM fold 2025 in active compute** (census+fast-path: trades=41, pnl=-42040.50; fold checkpoint/summary pending while workers run permutation/placebo/strata); fold 2026YTD pending, then Binance verdict + `c21_pooled_stability_synthesis_*` + `c21_decision_verdict_CONSOLIDATED_*`.
- Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → **`C21 ACCEPTANCE: FAIL`** (8 missing: `c21_binance_um_fold_{campaign,episode_edge,placebo,census}_*`, `c21_decision_verdict_binance_um_stability_*`, `c21_pooled_stability_synthesis_*`, `c21_decision_verdict_CONSOLIDATED_*`).

**Immediate next action (heavy execution only, no planning/relitigating):**
1. **Confirm runner:** `ps -eo pid,ppid,etime,time,stat,pcpu,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep`. If live with child workers, **do not start another**.
2. **Monitor to completion (canonical signals):** `ls research_state/c21_ckpt_* | wc -l` (→8), `ls research_state/c21_*_20261117T064408Z.json | grep -v prereg | grep -v ckpt | wc -l` (→12), `tail -n 50 research_state/c21_run_20261117T215941Z.log`, and rerun `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` until **`C21 ACCEPTANCE: PASS`** (`STABLE_POSITIVE_SUBSET` / `NO_GO` / `UNDERPOWERED` with power curve). Log silence between phase prints is normal; judge by CPU + ckpt/artifact counts.
3. **Only if no runner alive:** `bash scripts/run_c21_detached_durable.sh` (invoke so command line does not literally contain the script name, per pgrep caveat), then monitor to `PASS`.
4. **On `PASS`:** `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py`; update `HANDOFF.md` with timestamped literals. **Do not kill healthy runner, do not reduce draws, do not hand-fabricate, do not relaunch C20, do not commit unless explicitly asked.**

Full binding spec, guardrails, acceptance tokens, file map: `HANDOFF.md`.
