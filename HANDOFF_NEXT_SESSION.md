# DURABLE HANDOFF — NEXT AGENTIC WORK SESSION
**Timestamp:** 2026-11-27T05:09:02Z
**Repository:** CRASH-REBOUND-STRATEGY
**Session Context:** Heavy compute queue C24→C25→C26→C27→C28→C29→C30→C31→C32+

---

## 🎯 CURRENT STATE: C25 IN FLIGHT (ACTIVE BOTTLENECK)

### What's Running RIGHT NOW
- **Campaign:** C25 Cost/Funding Fidelity Adjudication
- **Runner:** `run_c25_cost_fidelity_campaign.py --jobs 4 --resume` (4 parallel workers)
- **Log:** `research_state/c25_run_20261126T235730Z.log`
- **Progress:** 41/64 cells complete → **23 cells remaining**
- **Current Cell:** `cost_taker_funding mexc 2024` (PRIMARY arm)
- **Remaining:** `cost_taker_funding` arm for `mexc` (2024, 2025, 2026YTD) + `bitget` (2023, 2024, 2025, 2026YTD)

### Acceptance Gate Status
```bash
C25 ACCEPTANCE: PENDING
  PENDING: 23 missing (arm, venue, fold) cells
  PENDING: missing verdict artifacts
  next: PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume
```

---

## ⛓️ BLOCKED CHAIN (NO CELL MAY RUN UNTIL PREDECESSOR PASS)
```
C25 IN FLIGHT (23 cells)
    ↓ blocks
C26 Intrabar-Path Fidelity (prereg exists, 0 cells)
    ↓ blocks
C27 Next-Venue Replication: Bybit (prereg exists, 0 cells)
    ↓ blocks
C28 Portfolio-Level Allocation (prereg exists, 0 cells)
    ↓ blocks
C29 Strict Temporal OOS Holdout on Archived Window (prereg exists, 0 cells)
    ↓ blocks
C30 Execution-Realism Stress (prereg exists, 0 cells)
    ↓ blocks
C31 Forward-Time Holdout on Newest Never-Scored Window (prereg exists, 0 cells)
    ↓ blocks
C32 NEXT FOCUS CAMPAIGN: Next Independent USDT-Perp Venue Replication Beyond C27
    (prereg EXISTS: c32_prereg_20261121T061508Z.json/.md)
    Direction c32-a = next_venue_replication
```

---

## 🚀 IMMEDIATE NEXT SESSION TASK LIST

### PRIORITY 1: MONITOR C25 TO COMPLETION (NON-NEGOTIABLE)
```bash
# Check current status
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py

# Tail the live log
tail -f research_state/c25_run_20261126T235730Z.log

# When verify prints PASS, C25 verdict artifacts will exist:
#   c25_cost_base_decision_verdict_20261119T045500Z.json
#   c25_cost_taker_decision_verdict_20261119T045500Z.json
#   c25_cost_taker_funding_decision_verdict_20261119T045500Z.json
#   c25_cost_stress_decision_verdict_20261119T045500Z.json
#   c25_decision_verdict_CONSOLIDATED_20261119T045500Z.json
```

### PRIORITY 2: SEQUENTIALLY UNBLOCK THE CHAIN (ONE CAMPAIGN PER SESSION MINIMUM)
**Each campaign requires: `run_campaign.py --jobs 4 --resume` → `verify_cXX_focus_campaign.py` → `status_cXX.sh`**

| Campaign | Script | Prereg | Est. Cells | Est. Time |
|----------|--------|--------|------------|-----------|
| C26 | `run_c26_path_fidelity_campaign.py` | c26_prereg_20261119T121500Z | 64 | ~3-4h |
| C27 | `run_c27_campaign.py` | c27_prereg_20261119T215721Z | 64 | ~3-4h |
| C28 | `run_c28_campaign.py` | c28_prereg_20261121T013400Z | 64 | ~3-4h |
| C29 | `run_c29_campaign.py` | c29_prereg_20261121T031907Z | 64 | ~3-4h |
| C30 | `run_c30_campaign.py` | c30_prereg_20261121T051754Z | 64 | ~3-4h |
| C31 | `run_c31_campaign.py` | c31_prereg_20261121T052233Z | 64 | ~3-4h |
| **C32** | `run_c32_campaign.py` | **c32_prereg_20261121T061508Z** | **64** | **~3-4h** |

**C32 is the MANDATORY same-session successor on C31 ACCEPTANCE: PASS.**
Per the HANDOFF no-avoidance rule: once C31 PASS lands, the SAME SESSION must durably launch C32.
C32-A = Next independent USDT-perp venue replication beyond C27 (Bybit).

### PRIORITY 3: DURABLE LAUNCH PATTERN (USE FOR EVERY CAMPAIGN)
```bash
# Launch durable background runner (survives session/turn boundaries)
background_process start \
  command="bash scripts/run_cXX_durable.sh --direction cXX-a" \
  persistent=true \
  description="CXX Campaign Runner"

# Monitor progress
background_process logs <id>
background_process status <id>
```

---

## 🔒 GUARDRAILS (FUTURE AGENTS CANNOT AVOID)
1. **No C26 cell runs until C25 ACCEPTANCE: PASS**
2. **No C27 cell runs until C26 ACCEPTANCE: PASS**
3. **No C28 cell runs until C27 ACCEPTANCE: PASS**
4. **No C29 cell runs until C28 ACCEPTANCE: PASS**
5. **No C30 cell runs until C29 ACCEPTANCE: PASS**
6. **No C31 cell runs until C30 ACCEPTANCE: PASS**
7. **No C32 cell runs until C31 ACCEPTANCE: PASS + C31 primary-arm anchor exists**
8. **Draw floors are NOT reducible: 20k bootstrap / 20k permutation / 2k placebo / 2k strata**
9. **No smoke/reduced-draw runs. No same-data reruns. No frozen-signal parameter searches.**
10. **Signal path FROZEN at C24/C25/C26/C31 sentinel (drift-checked every cell).**
11. **Liquidation distance FIXED at C24 primary (d15: maint=14, buffer=1 → 15%).**
12. **Cost model FROZEN at C25 primary. Funding model HONEST (okx = UNAVAILABLE_FUNDING).**
13. **C32 fidelity-anchor MUST reproduce C31 primary-arm per-venue/per-fold PnL within ±1.0.**
14. **C32 decision rules: REOPENS_C1_C31 iff ALL 5 conditions met; else NO_GO_ROBUST_TO_VENUE.**

---

## 📋 SESSION STARTUP CHECKLIST (RUN FIRST)
```bash
# 1. Verify C25 status (should be PASS or near-PASS)
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py

# 2. If C25 PASS → immediately launch C26
PYTHONPATH=. .venv/bin/python scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume

# 3. When C26 cells done → verify
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py --direction c26-a

# 4. REPEAT for C27→C28→C29→C30→C31→C32
#    EACH CAMPAIGN MUST REACH ACCEPTANCE: PASS BEFORE NEXT STARTS
```

---

## 🎯 DEFINITION OF DONE FOR THIS HANDOFF
The next session (and every subsequent session) **MUST NOT** declare "no authorized work" or "blocked" while any campaign in the chain is PENDING. The heavy-work queue **C25→C32** must be driven to completion. C32 is the terminal adjudication that either:
- **SUPERSEDED_BY_C32** (edge re-opened across all fidelity axes), OR
- **C1-C32 NO_GO ROBUST TO MARGIN, COST, PATH, ALLOCATION, HOLDOUT, EXECUTION REALISM, FORWARD-TIME HOLDOUT AND VENUE REPLICATION**

---

## 📍 KEY FILES TO REFERENCE
- `scripts/run_c25_cost_fidelity_campaign.py` — C25 runner (currently active)
- `scripts/verify_c25_focus_campaign.py` — C25 acceptance gate
- `scripts/run_c32_campaign.py` — C32 runner (final campaign)
- `scripts/verify_c32_focus_campaign.py` — C32 acceptance gate (verify after C32)
- `research_state/c32_prereg_20261121T061508Z.json` — C32 pre-registration (SHA-pinned)
- `scripts/runner_alive.sh` — Duplicate runner prevention
- `scripts/bootstrap_env.sh` — Environment bootstrap (venv)

---

**NO EXCUSES. NO AVOIDANCE. DRIVE THE QUEUE TO C32 VERDICT.**