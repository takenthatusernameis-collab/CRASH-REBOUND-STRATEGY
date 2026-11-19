# INITIAL TASK MESSAGE — 2026-11-19T02:12:24Z (TERMINAL STATE — STOP)

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here. This file is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live 2026-11-19T02:12:24Z):** C1–C20 CLOSED `NO_GO`; C21-T1 COMPLETE (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`); C22-T1 COMPLETE (`C22 ACCEPTANCE: PASS`, consolidated `NO_GO`); **C23-T1 COMPLETE** — Bitget USDT-M out-of-sample replication. Gate `C23 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. Pooled total PnL **-58,129.33**, prob_pooled_total_gt_0=0.0, BH pooled stratum survivors **0/36**, sign concordant (all negative). Folds: 2023: 24 trades +28,706.32; 2024: 36 trades -30,939.60; 2025: 37 trades -32,710.19; 2026YTD: 21 trades -23,185.86. 4/4 fold checkpoints present, 7/7 battery artifacts present. Runner NOT ALIVE (campaign finished) — do not relaunch. `scripts/status_c23.sh` → RUNNER: NOT ALIVE, battery 7/7, gate `C23 ACCEPTANCE: PASS`. `tests/test_c23_campaign_20261118.py` → 13 passed.

**Immediate next action:** none required — **STOP**. No campaign is authorized beyond C23. Do not launch C23 again, do not start a same-data follow-on on OKX/Binance/MEXC, do not relabel Bitget data as Hyperliquid, do not reduce draw counts. The correct terminal state is the evidence report in `HANDOFF.md`, not a new probe.

**Terminal evidence (file and do not relitigate):** per-fold numbers above; pooled PnL -58,129.33 (CI95 [-58,129.33, -58,129.33]); consolidated verdict token `NO_GO` (`research_state/c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json`, generated 2026-11-19T00:31:49Z); provenance `is_hyperliquid_venue_data=false`, real Bitget USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; `tests/test_c23_campaign_20261118.py` → 13 passed.

**Key tokens:** `C23 ACCEPTANCE: PASS` (consolidated `NO_GO`), `c23_prereg_20261118T202301Z`, `status_c23.sh`, `verify_c23_focus_campaign.py`, `tests/test_c23_campaign_20261118.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json`.

Full binding context, fold evidence, no-avoidance rules, guardrails, and execution order: `HANDOFF.md`.