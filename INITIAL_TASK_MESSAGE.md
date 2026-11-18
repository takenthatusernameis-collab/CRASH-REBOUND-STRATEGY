# INITIAL TASK MESSAGE — 2026-11-18T23:25:19Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live 2026-11-18T23:25:19Z):** C1–C20 CLOSED `NO_GO`; C21 PASS (`NO_GO`); C22 PASS (`NO_GO`); **C23-T1 ACTIVE & RUNNING** (Bitget USDT-M out-of-sample replication). Runner parent PID **25897** alive with 4 rotating workers, log `research_state/c23_run_20261118T222155Z.log`. **Fold 2023 checkpoint DONE** (24 trades, PnL +28,706.32, 9 episodes, perm_p=0.0229, 0/9 BH strata survivors); **fold 2024 IN PROGRESS** (census 36 trades, -30,939.60, fast-path diff 0.00e+00, permutation/placebo phase); 2025/2026YTD pending. Battery artifacts **0/7** — gate `C23 ACCEPTANCE: PENDING`. Expected completion **2026-11-19T01:20–01:45Z** (~46 min/fold observed).

**Immediate next action (one read-only command):** `bash scripts/status_c23.sh`
- `RUNNER: ALIVE` → do not relaunch, do not kill, do not foreground-wait; schedule a wakeup ~40–45 min out and re-check. Quiet logs during the 20k permutation/2k placebo phase are normal.
- `RUNNER: NOT ALIVE` + gate PENDING → `bash scripts/run_c23_detached_durable.sh` (resume skips completed folds; if all 4 checkpoints exist it only rebuilds artifacts).
- Gate `PASS` → deliver the per-fold / pooled / power-curve report, then **STOP** (no campaign is authorized beyond C23).

**Key tokens:** `C22 ACCEPTANCE: PASS` (consolidated `NO_GO`), `C23 ACCEPTANCE: PENDING` → must reach `PASS`, `c23_prereg_20261118T202301Z`, `run_c23_detached_durable.sh`, `status_c23.sh`, `verify_c23_focus_campaign.py`, `tests/test_c23_campaign_20261118.py`.

**Priority by repo scope (non-negotiable):** C1–C20 CLOSED & CERTIFIED `NO_GO`. C21-T1 COMPLETE (`PASS`, consolidated `NO_GO`). C22-T1 COMPLETE (`PASS`, consolidated `NO_GO`). **C23-T1 is the ACTIVE BINDING CAMPAIGN** — it must run to completion and pass `C23 ACCEPTANCE: PASS`; a positive fold 2023 alone is not a result (0/9 BH strata survivors). Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`). Do NOT reduce draw counts (20k/20k/2k floors); do NOT relabel Bitget data as Hyperliquid; do NOT start a same-data rerun.

Full binding context, fold evidence, no-avoidance rules, guardrails, and execution order: `HANDOFF.md`.