# INITIAL TASK MESSAGE — 2026-11-18T20:21:30Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live at 2026-11-18T20:21Z):** **C22-T1 ACTIVE & RESUMED** (MEXC USDT-perp out-of-sample replication). All 4 fold checkpoints now present (2023, 2024, 2025, 2026YTD). Gate `C22 ACCEPTANCE: PENDING` (1/7 battery artifacts). Runner relaunched parent PID **12059**, log `research_state/c22_run_20261118T202130Z.log`. Bottleneck removed: fixed `trades_matched` → `trades_matched_to_events` KeyError in `run_c22_mexc_campaign.py:1250` that blocked artifact build. Folds complete; runner rebuilding 7 battery artifacts. C23-T1 (Bitget) prepared, binding after C22 PASS.

**Immediate next action:** Run the one-shot status check from `HANDOFF.md`, then monitor/resume until `C22 ACCEPTANCE: PASS`. Only after C22 PASS and no runner alive, begin **C23-T1** (Bitget USDT-M) per the binding section in `HANDOFF.md`.

**Key tokens:** `C21 ACCEPTANCE: PASS` (consolidated `NO_GO`), `C22 ACCEPTANCE: PENDING` → must reach `PASS`, `c22_prereg_20261118T100126Z`, `run_c22_detached_durable.sh`, `verify_c22_focus_campaign.py`, `C23-T1` Bitget binding campaign.

**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate). C21-T1 is COMPLETE. **C22-T1 is the ACTIVE BINDING CAMPAIGN** — must run to completion and pass `C22 ACCEPTANCE: PASS`. **C23-T1 is the PREPARED NEXT FOCUS CAMPAIGN** — Bitget USDT-M, binding after C22 PASS. Hyperliquid-native acquisition stays CLOSED. Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC/Bitget data as Hyperliquid; do not reduce draw counts.

Full binding context, fold evidence, no-avoidance rules, guardrails, and C23 execution order: `HANDOFF.md`.