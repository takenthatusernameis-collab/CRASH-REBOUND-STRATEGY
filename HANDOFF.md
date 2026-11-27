# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session
**Generated:** 2026-11-27T01:13:38Z
**Session Context:** CRASH-REBOUND-STRATEGY repo — systematic multi-venue strategy validation
**Chain State:** C24 PASS → C25 IN FLIGHT → C26-C32 BLOCKED

---

## 🎯 IMMEDIATE PRIORITY (No-Avoidance Rule)

**C25 Cost/Funding Fidelity Campaign is IN FLIGHT and MUST COMPLETE before any downstream campaign can launch.**
The runner is ALIVE with 4 parallel jobs. Current progress: **22/40 draw chunks** for `cost_taker_funding/mexc/2023`.
**Do not spawn new campaigns. Do not edit markdown. Do not declare "no authorized work."**
The heavy-work queue is C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32. **This chain is the only authorized work.**

---

## 📊 CAMPAIGN CHAIN STATUS (Source of Truth)

| Campaign | Status | Token / Gate | Blocked On | Next Action |
|----------|--------|--------------|------------|-------------|
| **C24** Margin/Liquidation | **PASS** | `FIDELITY_ANCHOR_REPRODUCED` | — | Done (anchor for C25) |
| **C25** Cost/Funding Fidelity | **IN FLIGHT** | `C25 ACCEPTANCE: PENDING` | C24 PASS | **Monitor → wait for PASS** |
| **C26** Intrabar Path Fidelity | **PENDING** | `C26 ACCEPTANCE: PENDING` | C25 PASS | Launch `run_c26_durable.sh` |
| **C27** Next-Venue Replication | **PRE-REGISTERED** | — | C26 PASS | Wait |
| **C28** Portfolio Allocation | **PRE-REGISTERED** | — | C27 PASS | Wait |
| **C29** Temporal OOS Holdout | **PRE-REGISTERED** | — | C28 PASS | Wait |
| **C30** Execution Realism Stress | **PRE-REGISTERED** | — | C29 PASS | Wait |
| **C31** Forward-Time Holdout | **PRE-REGISTERED** | — | C30 PASS | Wait |
| **C32** Next Independent Venue | **PRE-REGISTERED** | — | C31 PASS | Wait |

**C24 Verdict:** All 4 venues (OKX, Binance UM, MEXC, Bitget) negative PnL. Pooled CI95 `[-265k, -207k]`, `prob_gt_0 = 0.0`. This is the **fidelity anchor** — it validates simulation infrastructure, not strategy profitability.

**C1-C20 Cross-Venue (OKX + Binance UM multi-year):** `NO_GO` — pooled PnL `−125,367`, bootstrap 95% CI `[-140,619, -110,115]`, `prob_pooled_total_gt_0 = 0.0`. **Closed. Do not relaunch.**

---

## 🔧 OPERATIONAL COMMANDS (Run Exactly These)

### 1. Monitor C25 Progress (run repeatedly until PASS)
```bash
bash scripts/status_c25.sh
```
**Expected PASS signal:** `C25 ACCEPTANCE: PASS` + all 4 verdict artifacts present:
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
**Both must print PASS / "EVIDENCE VERIFIED" / "21/21 checks passed" before proceeding.**

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
bash scripts/status_c28.sh  # (check script exists)

# C29, C30, C31, C32 — follow same pattern per their durable scripts
```

---

## ⚠️ BOTTLENECKS & RECOVERY

| Bottleneck | Symptom | Recovery |
|------------|---------|----------|
| C25 runner dies | `RUNNER: NOT ALIVE` in `status_c25.sh` | `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` |
| C25 stuck on funding acquisition | `pending` cells for `cost_taker_funding/mexc/*` or `bitget/*` | Check `scripts/probe_c25_funding_acquisition.py` → `scripts/fetch_funding_history.py` |
| Anchor mismatch at C26 | `C26_UNDERPOWERED` / `path anchor reference not available` | Re-run C25 verify; ensure C25 consolidated verdict exists |
| Silent data corruption | `verify_campaign_evidence.py` FAIL | **Stop. Do not proceed.** Investigate artifact mismatch. |

---

## 📋 SESSION CHECKLIST (Next Agent Must Execute)

- [ ] Run `bash scripts/status_c25.sh` — confirm runner ALIVE, draw chunks advancing
- [ ] If C25 not PASS: **wait / monitor only** — do not launch anything else
- [ ] When C25 PASS: run `verify_campaign_evidence.py` + `session_gate.py` — both must PASS
- [ ] Launch C26 via `background_process start` with `persistent=true`
- [ ] Monitor C26 to first checkpoints (`status_c26.sh` shows cells > 0/16)
- [ ] Update this HANDOFF.md with new timestamps and status before ending session

---

## 🔒 NO-AVOIDANCE CONSTRAINTS (Enforced by Verifiers)

1. **No campaign may run out of chain order.** C26 cell runs = FAIL if C25 not PASS.
2. **No synthetic/placeholder data relabeled as evidence.** `verify_campaign_evidence.py` fails closed.
3. **No verdict token claimed without full artifact chain.** `underpowered` → no decision-grade claim.
4. **No session may declare "no authorized work."** The chain C25→C32 is pre-authorized; run it.
5. **No config switching after results.** Prereg SHA256 frozen at campaign start.

---

## 📍 CURRENT RUNNER STATE (as of 2026-11-27T01:13:38Z)

```
PID 2867 (parent) + 14533-14536 (4 workers) — python run_c25_cost_fidelity_campaign.py --jobs 4 --resume
CPU: ~93% each worker | Mem: ~700MB each | Runtime: ~2h 52m
In-flight: cost_taker_funding/mexc/2023 (22/40 chunks)
All cost_base & cost_taker arms: 16/16 DONE
cost_taker_funding OKX: UNAVAILABLE_FUNDING (API retention)
cost_taker_funding Binance UM: 16/16 DONE
cost_taker_funding MEXC/Bitget: pending → in-flight
cost_stress: 0/16 pending
```

**Next session must pick up exactly here.** No re-planning. No new direction. **Execute the chain.**

---

**End of Handoff.** Next session starts at C25 monitoring → C26 launch → chain continuation.