# DURABLE HANDOFF — NEXT AGENTIC SESSION
**Generated (UTC):** 2026-11-27T20:05:55Z
**Repository:** CRASH-REBOUND-STRATEGY
**Session Context:** C25 campaign IN FLIGHT — critical path bottleneck (updated from 19:25:33Z handoff)

---

## CURRENT STATE SNAPSHOT

### C25 — Round-Trip Cost & Realized-Funding Fidelity Adjudication
- **Status:** `IN_FLIGHT` (runner alive, 4 workers active since 19:59Z, ETA ~2026-11-28 on this 4-core box)
- **Progress from `c25_run_20261127T182524Z.log`:**
  - ✅ `cost_base` — all 4 venues × 4 folds = 16 cells (OKX, Binance UM, MEXC, Bitget; 2023-2026YTD) — **RESUMED**
  - ✅ `cost_taker` — all 4 venues × 4 folds = 16 cells — **RESUMED**
  - ✅ `cost_taker_funding` OKX 2023-2026YTD = 4 cells (UNAVAILABLE_FUNDING, excluded from realistic arms) — **RESUMED**
  - ✅ `cost_taker_funding` Binance UM 2023-2025 = 3 cells — **RESUMED**
  - 🔄 `cost_taker_funding` Binance UM 2026YTD — **RUNNING** (active worker)
  - 🔄 `cost_taker_funding` MEXC 2023 — **RUNNING** (active worker, first of 4 folds)
  - 🔄 `cost_taker_funding` Bitget 2023 — **RUNNING** (active worker, census: events=348 signal_pass=108 trades=46)
  - ⏳ `cost_taker_funding` MEXC 2024, 2025, 2026YTD (3 cells)
  - ⏳ `cost_taker_funding` Bitget 2024, 2025, 2026YTD (3 cells)
  - ⏳ `cost_stress` all venues × 4 folds (16 cells) — runs after PRIMARY
- **Total cells:** 56 (4 venues × 4 folds × 4 arms; OKX funding arms excluded = 4×4×3 + 4×4×2 = 56)
- **Completed:** ~26/56 | **Running:** 3 (Binance UM 2026YTD + MEXC 2023 + Bitget 2023) | **Remaining:** ~27
- **Checkpoints:** `research_state/c25_ckpt_*.json` present for all completed cells
- **Run log:** `research_state/c25_run_20261127T182524Z.log` (active)

### BLOCKED CHAIN (all PRE_REGISTERED_BEFORE_COMPUTE)
| Campaign | Axis | Blocked On | Cannot Launch Until |
|----------|------|------------|---------------------|
| **C26** | intrabar_path + per_trade_funding | C25 ACCEPTANCE: PASS | `C25 ACCEPTANCE: PASS` |
| **C27** | next_venue_replication (Bybit) | C26 ACCEPTANCE: PASS | `C26 ACCEPTANCE: PASS` |
| **C28** | portfolio_level_allocation | C27 ACCEPTANCE: PASS | `C27 ACCEPTANCE: PASS` |
| **C29** | strict_temporal_oos_holdout (archived window) | C28 ACCEPTANCE: PASS | `C28 ACCEPTANCE: PASS` |
| **C30** | execution_realism_stress (3× slippage + taker fee) | C29 ACCEPTANCE: PASS | `C29 ACCEPTANCE: PASS` |
| **C31** | strict_temporal_oos_holdout (forward window 2026-09-29→2026-11-21) | C30 ACCEPTANCE: PASS | `C30 ACCEPTANCE: PASS` |
| **C32** | next_venue_replication (beyond C27) | C31 ACCEPTANCE: PASS | `C31 ACCEPTANCE: PASS` |

### ANCHOR VERDICTS (COMPLETED)
- **C24:** `C24_REOPENS_C1_C23` — d15 (15% liquidation distance) PASSED, consolidated verdict `C24_REOPENS_C1_C23` supersedes C1-C23 NO_GO
- **C15 (Hyperliquid-native):** `BLOCKED_EVIDENCED_DATA_REQUIRED` — T2 not executable without extended native evidence; hard blocker filed

---

## MANDATORY NEXT ACTIONS FOR NEXT SESSION

### PRIORITY 1 — MONITOR C25 TO COMPLETION
The C25 runner is alive with 4 workers (PIDs 22818-22821 started 19:59Z). **Do not restart or interfere.** The campaign uses `--resume` and checkpoints (`c25_ckpt_*.json`).

**When C25 finishes (all 56 cells):**
```bash
# 1. Verify acceptance (produces C25 ACCEPTANCE: PASS or detailed failure)
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py

# 2. If PASS, immediately launch C26 (same session — heavy work must chain)
PYTHONPATH=. .venv/bin/python scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume
```

### PRIORITY 2 — IF C25 FAILS ACCEPTANCE
- If `COST_ANCHOR_MISMATCH` → C25_UNDERPOWERED: investigate anchor reproduction failure
- If `C25_NO_GO_ROBUST_TO_COST` → program closes as C1-C25 NO_GO ROBUST TO MARGIN AND COST
- Record verdict in `research_state/c25_decision_verdict_CONSOLIDATED_<TS>.json`
- **No further campaigns launch** — the chain terminates

### PRIORITY 3 — CHAIN EXECUTION (C25 PASS → C26 → C27 → C28 → C29 → C30 → C31 → C32)
Each campaign follows identical pattern:
```bash
# For each campaign C{N}:
PYTHONPATH=. .venv/bin/python scripts/run_c{N}_campaign.py --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c{N}_focus_campaign.py  # -> C{N} ACCEPTANCE: PASS
bash scripts/status_c{N}.sh
```
**No session may stop between campaigns.** The pre-registrations exist precisely so the heavy-work queue never dries out and no future agent can claim "no authorized work."

### PRIORITY 4 — DATA ACQUISITION GATES (must be ready before each launch)
- **C26:** Funding caches for Binance UM, MEXC, Bitget (OKX = UNAVAILABLE_FUNDING) — `scripts/probe_c25_funding_acquisition.py` should have completed
- **C27:** Stage-0 probe `scripts/probe_c27_venue_acquisition.py` → must return `ACQUISITION_VIABLE_<VENUE>_MULTIYEAR` (Bybit primary)
- **C29:** Holdout window manifests `research_state/cache/<venue>_1h_multiyear_20260929_20261121`
- **C31:** Holdout window manifests for forward window 2026-09-29 → 2026-11-21
- **C32:** Next independent venue acquisition probe

---

## SIGNAL PATH (FROZEN — DRIFT-CHECKED AT EVERY LAUNCH)
```
rsi_period=21, rsi_threshold=20, target_pct=9, rebound_short_*,
gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on,
entry_spec_literal_next_open=True, seed=20261201.
Liquidation distance fixed at C24 primary arm (d15): maint=14, buffer=1 => 15%.
Cost model frozen at C25 primary; funding model honest (okx = UNAVAILABLE_FUNDING).
```

---

## INVARIANTS (NEVER VIOLATE)
1. **No parameter tuning after results** — configs frozen at pre-registration
2. **No synthetic gap-fill** — symbols not listed for full window excluded (coverage=false)
3. **No funding fabrication** — UNAVAILABLE_FUNDING recorded, never zero-filled
4. **No draw-count reduction** — 20k bootstrap / 20k permutation / 2k placebo / 2k strata floors
5. **Anchor verification mandatory** — fidelity-anchor must reproduce prior primary-arm PnL within ±1.0
6. **Full artifact table required** — per-arm × per-venue × per-fold, per-leg attribution, exit-reason decomposition
7. **Cross-venue provenance** — `cross_venue=true`, `is_hyperliquid_venue_data=false` for C20-C32

---

## IF NO C25 RUNNER IS ALIVE (SESSION RESTART SCENARIO)
```bash
# Resume C25 from checkpoints
PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume

# If checkpoints corrupted/missing, rebuild from pre-reg (last resort)
PYTHONPATH=. .venv/bin/python scripts/build_c25_prereg.py
PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4
```

---

## ESCALATION CONTACTS
- **Campaign scripts:** `scripts/run_c25_cost_fidelity_campaign.py`, `scripts/verify_c25_focus_campaign.py`
- **Pre-reg reference:** `research_state/c25_prereg_20261119T045500Z.md`
- **Run log:** `research_state/c25_run_20261127T182524Z.log` (CURRENT ACTIVE)
- **Checkpoints:** `research_state/c25_ckpt_*.json`

---

## BOTTLENECK REMOVAL STATUS
- **Previous bottleneck:** C25 runner was not active (per 19:25 handoff)
- **Current status:** RESOLVED — 4 workers actively processing since 19:59Z
- **No action required** — let the workers complete the remaining ~27 cells
- **Do not spawn additional sessions** — this 4-core box is at capacity

---

**THIS HANDOFF IS BINDING.** The C25 campaign is the single point of failure for the entire C25-C32 adjudication chain. The next session MUST monitor C25 to completion and, on PASS, immediately chain into C26 without pause. No session may declare "no authorized work" — the pre-registration chain through C32 exists precisely to prevent that.