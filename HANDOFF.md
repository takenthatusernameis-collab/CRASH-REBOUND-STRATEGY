# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session
**Generated:** 2026-11-27T01:20:35Z
**Repo:** CRASH-REBOUND-STRATEGY — systematic multi-venue strategy validation (crash-rebound strategy research and backtesting)

---

# BINDING INITIAL TASK MESSAGE (timestamped 2026-11-27T01:20:35Z)

**C25 Cost/Funding Fidelity Campaign is IN FLIGHT and MUST COMPLETE before any downstream campaign can launch. No exceptions. No new campaigns. No "no authorized work" declarations.**

1. Run `bash scripts/status_c25.sh` repeatedly until `C25 ACCEPTANCE: PASS` + all 5 verdict artifacts present. Bounded wait ~8h (runner ALIVE, 4 saturated cores, ~1.6 h/cell). Do not end this session before the bounded wait completes if monitoring.
2. When C25 PASS: run `PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py` — both must PASS.
3. Launch C26 via `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then monitor `bash scripts/status_c26.sh`.
4. Continue the chain C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32 sequentially; same durable-script pattern per campaign.

This is the single durable handoff and the binding timestamped initial task message for the next agentic session. Re-derive all runner/gate/progress/pacing state with `bash scripts/next_c25_action.sh`; do not use stale values from any pointer file.

---

## 📊 CAMPAIGN CHAIN STATUS (Source of Truth)

| Campaign | Status | Token / Gate | Blocked On | Next Action |
|----------|--------|--------------|------------|-------------|
| **C24** Margin/Liquidation | **PASS** | `FIDELITY_ANCHOR_REPRODUCED` | — | Done (anchor for C25) |
| **C25** Cost/Funding Fidelity | **IN FLIGHT** | `C25 ACCEPTANCE: PENDING` | C24 PASS | **Monitor → wait for PASS (~8h bounded)** |
| **C26** Intrabar Path Fidelity | **PENDING** | `C26 ACCEPTANCE: PENDING` | C25 PASS | Launch `run_c26_durable.sh` |
| **C27** Next-Venue Replication | **PRE-REGISTERED** | — | C26 PASS | Wait |
| **C28** Portfolio Allocation | **PRE-REGISTERED** | — | C27 PASS | Wait |
| **C29** Temporal OOS Holdout | **PRE-REGISTERED** | — | C28 PASS | Wait |
| **C30** Execution Realism Stress | **PRE-REGISTERED** | — | C29 PASS | Wait |
| **C31** Forward-Time Holdout | **PRE-REGISTERED** | — | C30 PASS | Wait |
| **C32** Next Independent Venue | **PRE-REGISTERED** | — | C31 PASS | Wait |

**C24 Verdict:** All 4 venues (OKX, Binance UM, MEXC, Bitget) negative PnL. Pooled CI95 `[-265k, -207k]`, `prob_gt_0 = 0.0`. Fidelity anchor — validates simulation infrastructure, not strategy profitability.

**C1-C20 Cross-Venue (OKX + Binance UM multi-year):** `NO_GO` — pooled PnL `−125,367`, bootstrap 95% CI `[-140,619, -110,115]`, `prob_pooled_total_gt_0 = 0.0`. **Closed. Do not relaunch.**

---

## 🔧 OPERATIONAL COMMANDS (Run Exactly These)

### 1. Monitor C25 Progress (run repeatedly until PASS)
```bash
bash scripts/status_c25.sh
```
**Expected PASS signal:** `C25 ACCEPTANCE: PASS` + verdict artifacts:
- `c25_decision_verdict_cost_base_20261119T045500Z.json`
- `c25_decision_verdict_cost_taker_20261119T045500Z.json`
- `c25_decision_verdict_cost_taker_funding_20261119T045500Z.json`
- `c25_decision_verdict_cost_stress_20261119T045500Z.json`
- `c25_decision_verdict_CONSOLIDATED_20261119T045500Z.json`

### 2. Verify Evidence Chain (anti-avoidance gate)
```bash
PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. .venv/bin/python scripts/session_gate.py
```
Both must print PASS / "EVIDENCE VERIFIED" / "21/21 checks passed" before proceeding.

### 3. Launch C26 (ONLY after C25 PASS confirmed)
```bash
background_process start command="bash scripts/run_c26_durable.sh" persistent=true
```
Then monitor: `bash scripts/status_c26.sh`

### 4. Subsequent Campaigns (sequential, same pattern)
```bash
# C27
background_process start command="bash scripts/run_c27_durable.sh" persistent=true
bash scripts/status_c27.sh
# C28
background_process start command="bash scripts/run_c28_durable.sh" persistent=true
bash scripts/status_c28.sh
# C29, C30, C31, C32 — same pattern per their durable scripts
```

---

## ⚠️ BOTTLENECKS & RECOVERY (remove to keep heavy work moving)

| Bottleneck | Symptom | Recovery |
|------------|---------|----------|
| C25 runner dies | `RUNNER: NOT ALIVE` in `status_c25.sh` | `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` |
| C25 slow / pacing | ~8h remaining, 20 real cells left, 4 saturated cores | Wait bounded ~8h; do not add CPU work, do not relaunch, do not kill |
| Funding unavailable (skipped) | `UNAVAILABLE_FUNDING` (OKX cost_taker_funding all years) | Skip — already excluded; 8 skipped_unavailable_funding cells |
| Anchor mismatch at C26 | `C26_UNDERPOWERED` / path anchor reference not available | Re-run C25 verify; ensure C25 consolidated verdict exists |
| Silent data corruption | `verify_campaign_evidence.py` FAIL | **Stop. Do not proceed.** Investigate artifact mismatch. |

---

## 📋 SESSION CHECKLIST (Next Agent Must Execute)

- [ ] Run `bash scripts/status_c25.sh` — confirm runner ALIVE, draw chunks advancing toward 40/40
- [ ] If C25 not PASS: **wait / monitor only** — do not launch anything else, do not start C26/C27
- [ ] When C25 PASS: run `verify_campaign_evidence.py` + `session_gate.py` — both must PASS
- [ ] Launch C26 via `background_process start` with `persistent=true`
- [ ] Monitor C26 to first checkpoints (`status_c26.sh` shows cells > 0/16)
- [ ] Update this HANDOFF.md with new timestamps and status before ending session

---

## 🔒 NO-AVOIDANCE CONSTRAINTS (Enforced by Verifiers — Future Agents Cannot Avoid Heavy Work)

1. **No campaign may run out of chain order.** C26 cell runs = FAIL if C25 not PASS.
2. **No synthetic/placeholder data relabeled as evidence.** `verify_campaign_evidence.py` fails closed.
3. **No verdict token claimed without full artifact chain.** `underpowered` → no decision-grade claim.
4. **No session may declare "no authorized work."** The chain C25→C32 is pre-authorized; run it.
5. **No config switching after results.** Prereg SHA256 frozen at campaign start.
6. **HANDOFF.md is the only durable state file.** Pointer files (`AGENT_HANDOFF.md`, `INITIAL_TASK_MESSAGE.md`) contain no campaign state; do not edit them except via this handoff refresh.

---

## 📍 CURRENT RUNNER STATE (as of 2026-11-27T01:20:35Z)

```
PID 2867 (parent) + 20398-20410 (4 workers) — python run_c25_cost_fidelity_campaign.py --jobs 4 --resume
CPU: ~88-90% each worker | Mem: ~700MB each | Runtime: ~1h 33m
In-flight: cost_taker_funding/mexc/2023 (24/40 draw chunks on disk)
All cost_base & cost_taker arms: 16/16 DONE
cost_taker_funding OKX: UNAVAILABLE_FUNDING (API retention — skipped)
cost_taker_funding Binance UM: 16/16 DONE
cost_taker_funding MEXC/Bitget: 8/16 (in-flight)
cost_stress: 0/16 pending
real_cells_remaining=20 | skipped_unavailable_funding=8 | pacing ~8h remaining at ~1.6 h/cell on 4 saturated cores
ANCHOR: OK — cost_base reproduces C24 d15 exactly (16/16 cells exact match). C25 is safe to continue.
GATE: C25 ACCEPTANCE: PENDING | C26 ACCEPTANCE: PENDING
```

**Next session picks up exactly here.** No re-planning. No new direction. **Execute the chain.** Re-derive pacing with `bash scripts/next_c25_action.sh`.

---

**End of Handoff.** Next session starts at C25 monitoring → C26 launch → chain continuation.
