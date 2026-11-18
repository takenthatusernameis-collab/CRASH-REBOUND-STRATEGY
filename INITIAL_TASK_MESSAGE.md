# INITIAL TASK MESSAGE — 2026-11-18T22:24:48Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY`.

**Current position (verified live 2026-11-18T22:24:48Z):** C1–C20 CLOSED `NO_GO`; C21 PASS (`NO_GO`); C22 PASS (`NO_GO`); **C23-T1 ACTIVE & RUNNING** (Bitget USDT-M). Runner parent PID **25897**, log `research_state/c23_run_20261118T222155Z.log`. Gate `C23 ACCEPTANCE: PENDING`.

**Immediate next action:** monitor/resume until `C23 ACCEPTANCE: PASS` per HANDOFF.md. Do not reduce draws; do not relabel Bitget data as Hyperliquid.

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live at 2026-11-18T22:24Z):** **C23-T1 ACTIVE & RUNNING** (Bitget USDT-M out-of-sample replication). C22-T1 **COMPLETE** with `C22 ACCEPTANCE: PASS` (mexc=NO_GO, consolidated=NO_GO). All 4 C22 fold checkpoints present. C23 prerequisites all GREEN: prereg `c23_prereg_20261118T202301Z`, probe `c23_venue_acquisition_probe_20261118T202301Z` (`ACQUISITION_VIABLE_BITGET_MULTIYEAR`), cache 34 symbols (33 complete), universe `universe_bitget_multiyear_verified.json` (33 selected, real_market_data=true). **C23 runner launched** parent PID **25897**, log `research_state/c23_run_20261118T222155Z.log` (fold 2023 in progress). **Battery artifacts: 0/7 present** — gate `C23 ACCEPTANCE: PENDING`.

**Immediate next action:** Run the one-shot status check from `HANDOFF.md` (adapted for C23), then monitor/resume until `C23 ACCEPTANCE: PASS`. Expected ~1.5 h/fold × 4 folds = ~6 hours total.

**Key tokens:** `C22 ACCEPTANCE: PASS` (consolidated `NO_GO`), `C23 ACCEPTANCE: PENDING` → must reach `PASS`, `c23_prereg_20261118T202301Z`, `run_c23_detached_durable.sh`, `verify_c23_focus_campaign.py`.

**Priority by repo scope (non-negotiable):** C1–C20 CLOSED & CERTIFIED `NO_GO`. C21-T1 COMPLETE (`PASS`, consolidated `NO_GO`). C22-T1 COMPLETE (`PASS`, consolidated `NO_GO`). **C23-T1 is the ACTIVE BINDING CAMPAIGN** — must run to completion and pass `C23 ACCEPTANCE: PASS`. Hyperliquid-native acquisition stays CLOSED. Do NOT reduce draw counts; do NOT relabel Bitget data as Hyperliquid.

Full binding context, fold evidence, no-avoidance rules, guardrails, and execution order: `HANDOFF.md`.