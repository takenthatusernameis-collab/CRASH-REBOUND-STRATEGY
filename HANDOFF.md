# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session

**Timestamp:** 2026-11-27T12:14:19Z
**Repository:** CRASH-REBOUND-STRATEGY
**Working Directory:** /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY

---

## 🎯 IMMEDIATE NEXT TASK (Non-Negotiable)

**Complete C25 `cost_stress` arm (16 venue-fold cells) → Generate all 4 C25 arm verdicts → Generate C25 consolidated verdict → Unlock C26**

### Current Campaign Status (Sequential Chain: C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32)

| Campaign | Status | Blocking Issue |
|----------|--------|----------------|
| **C24** | ✅ ACCEPTANCE: PASS | — |
| **C25** | ⚠️ **INCOMPLETE** | Missing `cost_stress` arm (16 cells) + 2 arm verdicts + consolidated verdict |
| **C26** | 🔒 BLOCKED | Requires C25 ACCEPTANCE: PASS (consolidated verdict) |
| C27–C32 | 🔒 BLOCKED | Sequential dependency on C26 |

### C25 Completion Checklist (verify_c25_focus_campaign.py gate)

- [ ] **Prereg**: ✅ Exists (`c25_prereg_20261119T045500Z.json`, status: PRE_REGISTERED_BEFORE_COMPUTE)
- [ ] **C24 PASS**: ✅ (`c24_decision_verdict_CONSOLIDATED_20261119T013154Z.json` exists)
- [ ] **All 4 arms × 4 venues × 4 folds checkpoints**: ❌ **cost_stress arm has ZERO checkpoints** (cost_base: 16, cost_taker: 16, cost_taker_funding: 16, cost_stress: 0)
- [ ] **No signal-path/cost drift**: ✅ (frozen config validated)
- [ ] **Cost anchor (cost_base vs C24 d15)**: ✅ (COST_ANCHOR_REPRODUCED)
- [ ] **Inference floors (20k/20k/2k/2k)**: ✅ for completed arms
- [ ] **No SMOKE artifacts**: ✅
- [ ] **All 4 arm verdicts exist**: ❌ **Missing verdicts for `cost_taker_funding` and `cost_stress`**
- [ ] **Consolidated verdict exists**: ❌ **Missing `c25_decision_verdict_CONSOLIDATED_20261119T045500Z.json`**

---

## 🚀 EXECUTION COMMANDS (Run in Order)

### 1. Complete C25 cost_stress arm (heavy compute ~3-4 hours)

```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume --arms cost_stress
```

This runs 16 cells (4 venues × 4 folds) with full inference (episode-block bootstrap 20k, permutation 20k, placebo 2k). Use `--resume` for checkpoint durability.

### 2. Verify C25 ACCEPTANCE gate

```bash
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
```

**Expected output on success:** `C25 ACCEPTANCE: PASS` (with consolidated verdict token and arm pooled totals)

### 3. Launch C26 (once C25 PASS confirmed)

```bash
PYTHONPATH=. .venv/bin/python scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume
```

C26 adjudicates intrabar path sequencing + per-trade realized funding (4 arms × 4 venues × 4 folds).

---

## 🔧 KEY FILES & CONTEXTS

| File | Purpose |
|------|---------|
| `scripts/run_c25_cost_fidelity_campaign.py` | C25 runner (4 arms, frozen signal, liquidation=15%) |
| `scripts/verify_c25_focus_campaign.py` | C25 acceptance gate (authoritative PASS/PENDING/FAIL) |
| `scripts/run_c26_path_fidelity_campaign.py` | C26 runner (intrabar + per-trade funding fidelity) |
| `research_state/c25_prereg_20261119T045500Z.json` | C25 pre-registration (immutable) |
| `src/strategy/crash_rebound.py` | Core strategy (RSI<20 crash, +9% target, ETH hedge) |
| `src/backtest/engine.py` | Execution engine (fees, funding, liquidation, rebound short) |
| `src/strategy/config.py` | StrategyConfig with spec-compliant enforcement |

---

## ⚠️ HARD CONSTRAINTS (No-Avoidance Rules)

1. **No parameter searches** — Signal path frozen at C25 sentinel (RSI21<20, target=9%, entry=next-open, liquidation=15%)
2. **No draw-count reduction** — Floors: 20k bootstrap / 20k permutation / 2k placebo / 2k strata
3. **No zero-filling funding** — Venues without realized funding cache = UNAVAILABLE_FUNDING (excluded, not zeroed)
4. **No same-data reruns** — Each cell runs once; `--resume` continues from checkpoints
5. **Sequential adjudication** — C26 cannot start until C25 consolidated verdict exists
6. **Real data only** — `fabricated_data=false`, `synthetic_data=false`, `cross_venue=true`

---

## 📊 EXPECTED OUTCOMES

### C25 cost_stress arm
- Higher slippage (2×), taker fees, realized funding, +5 bps borrow
- Likely negative PnL (DESCRIPTIVE_ONLY role) — confirms cost sensitivity

### C25 consolidated verdict
- Primary arm (`cost_taker_funding`) token: `C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`
- Fidelity arm (`cost_base`) token: `COST_ANCHOR_REPRODUCED`
- Other arms: `DESCRIPTIVE_ONLY`

### C26 primary arm (`path_intrabar_combined`)
- Token: `C26_REOPENS_C1_C25` (if robust) or `C26_NO_GO_ROBUST_TO_PATH`
- Fidelity anchor (`path_base`): `PATH_ANCHOR_REPRODUCED` vs C25 primary

---

## 🛑 STOP CONDITIONS

- If `verify_c25_focus_campaign.py` returns **FAIL**: Fix drift/smoke/missing cells before proceeding
- If C25 cost_stress cells hit **UNAVAILABLE_FUNDING** for all venues: Document and proceed (arm still runs cost_taker config)
- If **any session idles** without executing heavy compute: Violates handoff no-avoidance rule

---

## 📝 NOTES FOR NEXT SESSION

- The `.venv` exists and is bootstrapped (requirements: pytest, numpy, pandas, requests, pyarrow)
- Use `background_process` with `persistent=true` for long-running campaign runs
- Checkpoint files in `research_state/` enable exact resume after environment loss
- All timestamps in UTC; `TS=20261119T045500Z` for C25, `TS=20261119T121500Z` for C26
- C24 d15 reference: `c24_decision_verdict_d15_20261119T013154Z.json` (venue_totals for cost_base anchor)

---

**This handoff is the single source of truth for the next session. Do not substitute lighter work, parameter searches, or "no authorized work" declarations. The only valid next action is completing C25 cost_stress to unblock the sequential campaign chain.**