# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T19:20:23Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position:** **C22-T1 ACTIVE & RESUMED** (MEXC USDT-perp out-of-sample replication). Parent runner PID **5347** + rotating workers, log `research_state/c22_run_20261118T192115Z.log`. Folds 2023+2024 checkpointed complete; fold 2025 interrupted/resuming; fold 2026YTD not started. Gate `C22 ACCEPTANCE: PENDING` (0/7 battery artifacts, 2/4 checkpoints).

**Immediate next action:** Run the one-shot status check from `HANDOFF.md`, then monitor/resume until `C22 ACCEPTANCE: PASS`. Only after C22 PASS and no runner alive, begin **C23-T1** (Bitget USDT-M) per the binding section in `HANDOFF.md`.

**Key tokens:** `C21 ACCEPTANCE: PASS` (consolidated `NO_GO`), `C22 ACCEPTANCE: PENDING` → must reach `PASS`, `c22_prereg_20261118T100126Z`, `run_c22_detached_durable.sh`, `verify_c22_focus_campaign.py`, `C23-T1` Bitget binding campaign.

Full binding context, fold evidence, no-avoidance rules, guardrails, and C23 execution order: `HANDOFF.md`.