# Agent Handoff — CRASH-REBOUND-STRATEGY — 2026-11-19T22:25:57Z

## Project Context
**Repository**: CRASH-REBOUND-STRATEGY — Multi-venue crash-rebound trading strategy validation campaign sequence (C20→C26).

## Current Campaign Status (verified via `verify_c2*_focus_campaign.py`)

| Campaign | Status | Description |
|----------|--------|-------------|
| **C23** | **PASS** | Bitget USDT-M out-of-sample replication (4 folds, 7 battery artifacts, NO_GO consolidated) |
| **C24** | **PASS** | Margin fidelity (liquidation distance sweep); d15 primary arm = 15% distance; C24_REOPENS_C1_C23 |
| **C25** | **PENDING** | **NEXT BLOCKER** — Cost/funding fidelity adjudication (64 cells × 20k/20k/2k/2k inference) |
| **C26** | **PENDING** | Blocked on C25 PASS — Intrabar path & per-trade funding fidelity |

## Immediate Next Task: **Run C25 Heavy Campaign to PASS**

### Why C25 is the critical path
- C24 proved the crash-rebound edge survives realistic liquidation distances (d15 primary arm = +144k pooled PnL on C24 primary arm)
- The remaining un-adjudicated fidelity gap is **COST**: current engine uses 5 bps slippage + near-zero commission + flat 0.01%/hr funding — materially more permissive than real venue taker fees (4.5–7 bps/side → 9–14 bps round trip) and realized 8h funding
- C25 attaches **full inference** (episode-block bootstrap 20k, conditional temporal-edge permutation 20k, full-portfolio placebo 2k, BH 2k) to pre-registered cost/funding arms
- **Must complete before C26 can start** (C26 gate explicitly blocks on C25 ACCEPTANCE: PASS)

### C25 Arm Specification (frozen in prereg `c25_prereg_20261119T045500Z.json`)
| Arm | Role | Config |
|-----|------|--------|
| `cost_base` | FIDELITY_ANCHOR | Exact current engine model — MUST reproduce C24 d15 per-venue/per-fold PnL within ±1.0 |
| `cost_taker` | — | Per-venue published taker fee (bps) per side + 5 bps slippage + $1 min commission |
| `cost_taker_funding` | **PRIMARY** | cost_taker + realized 8h funding on every leg |
| `cost_stress` | — | cost_taker_funding + 2× slippage + 5 bps borrow/financing |

### Execution Command (from repo root)
```bash
PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume
```
- 4 arms × 4 venues (OKX, Binance UM, MEXC, Bitget) × 4 folds (2023, 2024, 2025, 2026YTD) = **64 cells**
- Each cell: campaign → crash census → episode-block bootstrap (20k) → conditional permutation (20k) → placebo portfolio (2k) → robustness battery
- Estimated wall time: **several hours** (use `--resume` for fault tolerance)

### Verification After Completion
```bash
python -m scripts.verify_c25_focus_campaign
# Expected: C25 ACCEPTANCE: PASS
```

### Then Unblock C26
```bash
PYTHONPATH=. .venv/bin/python scripts/run_c26_path_fidelity_campaign.py --jobs 4 --resume
python -m scripts.verify_c26_focus_campaign
```

## Guardrails (Non-Negotiable)
- **Real market data only**: `real_market_data=true, fabricated_data=false, synthetic_data=false, is_hyperliquid_venue_data=false`
- **Signal path frozen**: RSI(21) ≤ 20, target 9%, entry next-open, liq distance 15% (maint=14, buffer=1) — drift = INVALID
- **Draw-count floors**: 20k / 20k / 2k / 2k — **not reducible**
- **No smoke artifacts**: Tests assert zero `_SMOKE.json` files in research_state
- **C25 blocked until C24 PASS**: Already satisfied (C24 PASS confirmed)

## Key Files for Next Agent
- `scripts/run_c25_cost_fidelity_campaign.py` — Heavy runner (762 lines)
- `scripts/verify_c25_focus_campaign.py` — Acceptance gate
- `research_state/c25_prereg_20261119T045500Z.json` — Pre-registered spec (frozen config, arms, folds, venues)
- `research_state/c25_prereg_20261119T045500Z.md` — Human-readable prereg

## Test Suite Health
- **1095 passed, 1 skipped** (84s) — All wiring/guardrail tests green
- CI: `.github/workflows/strategy-tests.yml` runs full suite on PR/push

---

**DO NOT START NEW CAMPAIGNS OR EXPERIMENTS.** The only valid next step is completing C25 heavy compute to PASS, then C26. This is a sequential adjudication pipeline; skipping or parallelizing breaks the pre-registration chain.