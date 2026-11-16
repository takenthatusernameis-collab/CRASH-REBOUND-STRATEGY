# HANDOFF — CRASH-REBOUND-STRATEGY
**Generated (UTC):** 2026-11-16T02:45:10Z
**Project:** CRASH-REBOUND-STRATEGY — Crash-rebound trading strategy research & backtesting
**Status:** HARD BLOCKER — Verified Hyperliquid-native data acquisition required for decision-grade inference

---

## CONTEXT SUMMARY

This repository implements the "Crash Rebound Strategy" per `crash-rebound-strategy.pdf` (see `research_state/strategy_spec.md`):
- **Universe:** Hyperliquid perpetuals with ≥$5M 24h volume (~26-80 coins)
- **Trigger:** 21h RSI < 20 → buy at next hourly open
- **Sizing:** 1.25% of coin's 24h USD volume; 120% gross cap with equal-share cuts
- **Hedge:** Every trade hedged with ETH (coin_vol/ETH_vol ratio, capped 3x)
- **Exits:** +9% target / 50h time exit / 8× hourly-range safety stop
- **Rebound short:** If buy hits +9%, short same coin (−9% target / 48h / 40% stop); only after hard bounce

The codebase is **spec-compliant and complete**: `src/strategy/` (config, risk, signal generation), `src/backtest/engine.py` (hourly simulation with fees, funding, liquidation), `src/data/` (verified loaders with provenance).

---

## CAMPAIGN HISTORY (C1–C15)

| Campaign | Verdict | Key Evidence |
|----------|---------|--------------|
| C1–C13 (Consolidated) | **NO_GO** | `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` |
| C11.3 | NO_GO / FRAGILE_NOT_DECISION_GRADE | 1 episode only |
| C12 | NO_DECISION_GRADE_GO | Underpowered |
| C13 | UNDERPOWERED | 10 episodes / 5 symbols / 283d |
| **C14** | **UNDERPOWERED** | **3 episodes / 4 crash days / 7 trades** on widest native archive (197 perps, 113 @ $5M, 283d). Bootstrap 95% CI [−1,144, +17,547] spans zero; first CI exclusion at n=4; max achievable from archive = 4. Permutation p=0.03595; placebo p=0.4444. |
| **C15** | **BLOCKED_EVIDENCED_DATA_REQUIRED** | T1: Ironflow HF probe (2025-05-25..2026-10-31) — same source as C14, cannot reach ≥2023-01-01. T2: Hyperliquid public API (candleSnapshot) — moving retention tail only (earliest 2026-04-21). **No verified Hyperliquid-native multiyear archive acquirable.** |

**Gate verification:** All gates pass (`session_gate.py`: 21/21, `verify_c14_focus_campaign.py`: PASS, `verify_campaign_evidence.py`: 4/4).

---

## THE BOTTLENECK (HARD BLOCKER)

**No verified Hyperliquid-native hourly OHLCV archive exists that extends history to ≥2023-01-01.**

- **Ironflow `ironflow/hyperliquid-candles-1h` (HuggingFace):** Only native-perps dataset found. Range: **2025-05-25T14:00:00Z .. 2026-10-31T23:00:00Z** (3.6M rows). Covers C14's 283-day spec window but **cannot reach ≥2023-01-01**. Already fully ingested.
- **Hyperliquid public API (`candleSnapshot`):** Moving retention tail only. Earliest served: **2026-04-21T15:00:00Z** (3,849/6,792 bars). Cannot supply multiyear history.
- **Cross-venue data (OKX, Binance, etc.):** Explicitly excluded — prior C10 cross-venue campaign produced `NO_GO` (0/7, `is_hyperliquid_venue_data=false`). The spec and all campaigns require **native Hyperliquid perps only** (`is_hyperliquid_venue_data=true`).

**Power curve is quantified:** C14 needs **n≥4 independent episodes** for CI excluding zero. Observed: **n=3**. Archive max: **n=4** (one additional distinct crash day). To reach decision-grade inference, we need **≥1 additional independent crash episode** from a verified native source extending the window or adding symbols.

---

## REQUIRED NEXT WORK (DATA ACQUISITION CAMPAIGN)

**Objective:** Acquire a **verified Hyperliquid-native** hourly OHLCV archive that either:
1. Extends history to **≥2023-01-01** (multiyear parity), OR
2. Provides **≥1 additional independent crash episode** beyond C14's 3 (target n≥4) under unchanged spec defaults.

**Acceptance criteria for any candidate archive:**
- Native Hyperliquid perpetuals only (no HIP-3 DEX / spot unless explicitly scoped and labeled)
- Hourly bars, complete gap-free coverage for the claimed window
- Per-symbol/per-file SHA256 + non-synthetic attestation + SOURCE/provenance manifest
- Passes `scripts/validate_hyperliquid_archive_intake.py`
- Derives universe at $5M rolling-24h gate (`spec_compliant_volume_threshold=true`) without relaxing RSI/spec defaults
- **Must not be relabeled cross-venue data** — `is_hyperliquid_venue_data=true` only for native artifacts

**Explicit data request stem:** `research_state/c15_data_request_stem_20261116T024001Z.md`

---

## WHAT FUTURE AGENTS MUST DO (NON-NEGOTIABLE)

1. **DO NOT** run inference campaigns (C16, C17, etc.) on the existing C14 archive — it is exhausted (max 4 episodes, need 4+ for CI exclusion).
2. **DO NOT** relax spec defaults (RSI<20, $5M volume, 1.25% sizing, 50h/48h exits, ETH hedge) to manufacture episodes — that invalidates the spec-compliant evidence chain.
3. **DO NOT** use cross-venue data (OKX, Binance, etc.) and label it Hyperliquid-native — C10 already proved this path fails (`NO_GO`, 0/7).
4. **MUST** focus entirely on **verified Hyperliquid-native data acquisition** from sources such as:
   - Hyperliquid institutional/historical data programs
   - Verified node operators with full-history archives
   - Data vendors with Hyperliquid-native perps coverage ≥2023-01-01
   - Any other source that can provide **provenance-attested, non-synthetic, native perps hourly OHLCV** with SHA256 verification
5. **MUST** document every acquisition attempt with command-level evidence (as C15 did) in `research_state/c15_acquisition_attempt_20261116T024001Z.md` style.
6. **ONLY** after a verified extended archive is acquired and passes intake validation should a new campaign (C16) be pre-registered and executed.

---

## KEY FILES FOR CONTINUATION

| File | Purpose |
|------|---------|
| `research_state/c15_data_request_stem_20261116T024001Z.md` | Exact data requirements |
| `research_state/c15_acquisition_attempt_20261116T024001Z.md` | Template for documenting acquisition attempts |
| `scripts/validate_hyperliquid_archive_intake.py` | Archive validation gate |
| `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` | C14 census — shows where episodes come from |
| `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json` | Power curve: n=4 first CI exclusion |
| `src/strategy/config.py` | Spec defaults (enforced via `enforce_spec_volume_floor`, `enforce_spec_position_size_pct`) |

---

## BOTTOM LINE

**The strategy implementation is complete and spec-compliant. The evidence chain is rigorous. The only blocker is data.** Without a verified Hyperliquid-native archive extending to ≥2023-01-01 (or adding ≥1 independent crash episode), **no further decision-grade work is possible**. Every future session must attack the data acquisition problem until it is resolved.