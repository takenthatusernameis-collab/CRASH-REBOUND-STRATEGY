# Consolidated Decision Verdict — C10 Final (all cross-venue, NOT Hyperliquid)

**Generated (UTC):** 2026-11-15T12:26:36Z
**Scope:** C1–C9 complete; **C10.1–C10.4 COMPLETE** (C10.2 Binance portfolio placebo finished this session).
**Supersedes for C10 additions:** cites and finalizes `research_state/decision_verdict_consolidated_20261115T064738Z.md` and `research_state/decision_verdict_consolidated_20261115T063642Z.md` (canonical C8 `NO_GO`). Do not overwrite prior canonical stems.
**Provenance:** Real OKX/Binance UM exchange data, non-synthetic. **`is_hyperliquid_venue_data=false` for all C10 artifacts — NOT Hyperliquid performance evidence.** Hyperliquid-native path externally blocked (`research_state/hyperliquid_retention_probe.json`: 3,869/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION`; `research_state/archive_intake_validation_20261115T064406Z.*`: `REJECT_NOT_EVIDENCE`, placeholder parquet).

## C10.0 gates / external-block confirmation
- `scripts/verify_next_focus_campaign.py` → **PASS** (C6 acceptance).
- `scripts/session_gate.py` → **21/21 checks passed — DONE**.
- `scripts/verify_campaign_evidence.py` → **4/4 EVIDENCE VERIFIED**.
- `scripts/probe_hyperliquid_blocker.py` / `scripts/validate_hyperliquid_archive_intake.py`: no operator archive yielding `ACCEPT_AS_EVIDENCE_CANDIDATE`; Hyperliquid-native path remains externally blocked.

## C10.1 — Cross-venue paired symbol/date agreement
- Artifacts: `research_state/cross_venue_paired_agreement_20261115T064738Z.json`, `.md`
- Pairing key `(symbol, entry_date_utc, leg)`; OKX 42 trades, Binance 42, **32 matched 1:1 pairs** (10 OKX-only, 10 Binance-only).
- **Verdict: `DIRECTION_REPLICATES_MAJORITY`** (same-sign rate **1.0000**, 32/32). Mean diff (OKX−Binance) **−454.03**, 95% bootstrap CI **[−1057.09, +11.00]** (crosses 0).
- Interpretation: trade-level direction (win/loss sign) replicates across independent venues for matched pairs; magnitudes differ and unpaired admissions differ — supports directional reproducibility, not magnitude/edge sufficiency. NOT Hyperliquid evidence.

## C10.2 — Binance UM multi-year full-portfolio placebo (COMPLETED THIS SESSION)
- Artifacts: `research_state/placebo_portfolio_binance_um_multiyear.json`, `.md` (**`generated_at_utc` 2026-11-15T12:26:21Z**; `is_hyperliquid_venue_data=false`).
- Script: `scripts/run_portfolio_placebo_binance_um_multiyear.py` (venue-parameterized; real portfolio engine; gates/sizing/cap/occupancy/hedge/fees/funding/liquidation preserved; no synthetic data). Ran `--draws 200 --seed 20261114 --jobs 4` (fork parallel; 200 draws in 7,474 s wall).
- Mode `deterministic_seeded_draws:200_choose_42_of_64`; pool 64 signal-gate events, choose_k 42 (canonical admitted).
- Canonical: 42 trades, total PnL **+21,994.06** (replay matches canonical exactly).
- Placebo: mean **18,950.05**, median **19,201.18**, p05 **−2,969.56**, p95 **40,497.29**, 95% CI **[−7,123.60, +46,117.89]**.
- **p(placebo ≥ canonical) = 0.4150**, canonical percentile (le) **0.5850**, P(placebo>0) **0.9350**.
- **Verdict: `underpowered`** — canonical PnL sits near the placebo median; no separation from the gate-passing pool. Symmetric with the OKX analogue (`placebo_portfolio_okx_multiyear`: p=0.4000).

## C10.3 — Pooled OKX+Binance dependence-aware episode meta-analysis
- Artifacts: `research_state/pooled_episode_meta_okx_binance_20261115T064738Z.json`, `.md`
- Independence: pooled across **independent venues only** (OKX 19 + Binance UM 19 = **38 pooled episode blocks**).
- By venue: OKX total +18,220.86 (9+/10−), Binance total +21,994.06 (7+/12−).
- Pooled observed total **+40,214.92**; episode-block bootstrap 95% CI **[−69,065.03, +168,946.87]**, **P(total>0)=0.74095**; sign-flip permutation p(one-sided)=**0.26955**, p(two-sided)=0.53560.
- **Verdict: `underpowered`** — pooling 38 independent venue-episodes does not rescue decision-grade inference (CI spans 0; permutation non-significant).

## Integrated verdict vs 7 stop/go criteria (C10 delta)
C10.1 adds directional replication (paired sign concordance) but not Hyperliquid evidence or magnitude certainty; C10.2 shows the Binance canonical total is not separable from a gate-passing placebo pool (p=0.4150); C10.3 confirms pooled cross-venue inference stays **underpowered** (CI includes 0, non-significant permutation). **No stop/go criterion flips to pass.** Prior C8 findings (FRAGILE_NOT_DECISION_GRADE, buy leg negative, short-leg-carried, concentrated, stress-fragile) remain binding.

| # | Criterion | Status | Evidence (unchanged from C8 unless noted) |
|---|---|---|---|
| 1 | Hyperliquid-native real-data coverage for spec window | **FAIL** | Retention probe blocks full 283d; partial chain 0 confirmed signals; no operator archive (`ACCEPT_AS_EVIDENCE_CANDIDATE` absent). |
| 2 | Dependence-aware edge excludes zero with adequate power | **FAIL (underpowered)** | OKX CI [−50.7k,+99.3k] P>0 0.665 perm 0.10; Binance CI [−57.4k,+122.1k] P>0 0.654 perm 0.185; pooled 38 eps CI [−69.1k,+168.9k] P>0 0.741 perm 0.270 (C10.3). |
| 3 | Portfolio/placebo distinguishes edge and is robust | **FAIL (underpowered/inconclusive)** | OKX p(placebo≥canon)=0.40; **Binance p(placebo≥canon)=0.4150 (C10.2)**; no decisive separation. |
| 4 | Core (buy-leg) economics positive, not dominated by short leg | **FAIL** | OKX buy −27,837 vs short +46,058; Binance buy −36,078 vs short +58,072. Buy leg negative on both venues and all 11 OKX grid variants. |
| 5 | Stability across sub-periods / not single year or episode | **FAIL** | OKX 2023/2024 negative, 2025 +42.6k; drop-2025 flips to −24.4k; drop ep14 flips to −11.3k. |
| 6 | Robust to cost/funding/entry/parameter stress | **FAIL** | OKX slippage 5× → −13.98k; spec-literal next-open → −55.06k (113 trades); RSI15 → −8.70k; buy leg negative across all 11 configs. |
| 7 | Cross-venue result transferable to Hyperliquid as validated edge | **FAIL** | Evidence is `CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID` (`is_hyperliquid_venue_data=false`); venue mechanics differ. |

**Overall:** 0/7 pass for a positive/GO claim.

## Decision
- **`NO_GO`** on claiming a validated crash-rebound edge from available evidence (unchanged, now fully C10-complete).
- Fragility is venue-universal across both independent cross-venue chains (underpowered dependence-aware inference; buy-leg negative; short-leg-carried; fragile totals). C10 adds directional replication but no magnitude/edge separation.
- **Only positive path:** ingest a verified Hyperliquid-native archive (operator-supplied) that passes `scripts/validate_hyperliquid_archive_intake.py` with `ACCEPT_AS_EVIDENCE_CANDIDATE`, then run canonical Hyperliquid campaign + C6-T3 + C7 batteries and re-evaluate all 7 criteria on Hyperliquid-native data.

## Prohibitions / caveats (binding)
- Do not relabel cross-venue (OKX/Binance) results as Hyperliquid evidence.
- Do not fabricate, synthesize, or interpolate data; do not treat placeholder parquet as evidence.
- Do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.
- Do not relax the $5M volume floor or spec-literal opt-in defaults.
- Canonical artifacts are fixed; do not overwrite without a new stem and documented reason.

## Reproduction (C10 commands)
```bash
# C10.1
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/cross_venue_paired_agreement.py --seed 20261115 --boot 10000
# C10.2 (completed; ~2.1h with 4 jobs)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py \
  --draws 200 --seed 20261114 --jobs 4 --out placebo_portfolio_binance_um_multiyear
# C10.3
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/pooled_episode_meta_okx_binance.py --seed 20261115 --boot 20000 --perm 20000
```

*End of consolidated verdict (C10 final).*