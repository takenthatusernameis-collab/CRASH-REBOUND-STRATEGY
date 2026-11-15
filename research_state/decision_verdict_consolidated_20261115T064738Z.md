# Consolidated Decision Verdict (C10 update)

**Generated (UTC):** 2026-11-15T06:47:38Z (C10.1/C10.3 computed); **C10.2 status:** Binance portfolio placebo run started (200 draws, seed 20261114) — artifact pending at time of this write.
**Supersedes for C10 additions:** cites `research_state/decision_verdict_consolidated_20261115T063642Z.md` (canonical C8 `NO_GO`, unchanged). Do not overwrite prior canonical stem.
**Provenance:** Real OKX/Binance UM exchange data, non-synthetic. **`is_hyperliquid_venue_data=false` for all C10 artifacts — NOT Hyperliquid performance evidence.** Hyperliquid-native path externally blocked (`research_state/hyperliquid_retention_probe.json`: 3,869/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION`; `research_state/archive_intake_validation_20261115T064406Z.*`: `REJECT_NOT_EVIDENCE`, placeholder parquet).

## C10.0 gates / external-block confirmation
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py` → **PASS** (C6 acceptance).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **21/21 checks passed — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **4/4 EVIDENCE VERIFIED**.
- `probe_hyperliquid_blocker.py` / `validate_hyperliquid_archive_intake.py` (2026-11-15T06:44Z run): no operator archive yielding `ACCEPT_AS_EVIDENCE_CANDIDATE`; Hyperliquid-native path remains externally blocked.

## C10.1 — Cross-venue paired symbol/date agreement
- Artifacts: `research_state/cross_venue_paired_agreement_20261115T064738Z.json`, `.md`
- Script: `scripts/cross_venue_paired_agreement.py --seed 20261115 --boot 10000`
- Pairing key: `(symbol, entry_date_utc, leg)`; OKX 42 trades, Binance 42, **32 matched 1:1 pairs** (10 OKX-only, 10 Binance-only, 0 ambiguous).
- **Verdict: `DIRECTION_REPLICATES_MAJORITY`** (same-sign rate **1.0000**, 32/32; both-positive 15, both-nonpositive 17). Mean diff (OKX−Binance) **−454.03**, 95% bootstrap CI **[−1057.09, +11.00]** (crosses 0). Sign test on paired diffs two-sided p≈0.1102 (OKX>Bin 11, Bin>OKX 21). OKX positive rate 0.46875, Binance 0.46875.
- By leg: buy n=23 same-sign 1.0 mean diff −207.52; short n=9 same-sign 1.0 mean diff −1083.99.
- Interpretation: **trade-level direction (win/loss sign) replicates across independent venues for matched pairs**, but PnL magnitudes differ (Binance tends higher on these pairs) and unpaired admissions differ by venue — supports directional reproducibility, not magnitude/edge sufficiency. Still NOT Hyperliquid evidence.

## C10.2 — Binance multi-year portfolio placebo
- Script: `scripts/run_portfolio_placebo_binance_um_multiyear.py` (venue-parameterized; real portfolio engine; gates/sizing/cap/occupancy/hedge/fees/funding/liquidation preserved; no synthetic data).
- Command: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py --draws 200 --seed 20261114 --out placebo_portfolio_binance_um_multiyear`
- **Status at 2026-11-15T06:47:38Z:** heavy run started in-session (background pid 16747 observed running ~10+ min); **no artifact written yet** (`research_state/placebo_portfolio_binance_um_multiyear.{json,md}` absent). **This is the remaining C10.2 completion item** — next session must ensure it finishes and records the real verdict (expected underpowered/cross-venue context per OKX analogue).

## C10.3 — Pooled OKX+Binance dependence-aware episode meta-analysis
- Artifacts: `research_state/pooled_episode_meta_okx_binance_20261115T064738Z.json`, `.md`
- Script: `scripts/pooled_episode_meta_okx_binance.py --seed 20261115 --boot 20000 --perm 20000`
- Independence: pooled across **independent venues only** (OKX 19 episodes, Binance UM 19 episodes, **38 pooled blocks**); no same-venue duplicates. Common shock timing may correlate episodes, but per-trade execution/PnL paths are venue-specific (stated).
- By venue: OKX total +18,220.86 (9+/10−), Binance total +21,994.06 (7+/12−).
- Pooled observed total **+40,214.92**; episode-block bootstrap 95% CI **[−69,065.03, +168,946.87]**, mean 40,397.76, median 37,189.06, **P(total>0)=0.74095**. Sign-flip permutation: p_null_ge_canonical(one-sided)=**0.26955**, p_abs(two-sided)=**0.53560**.
- **Verdict: `underpowered`** (CI spans 0 widely; permutation not significant). Pooling 38 independent venue-episodes does **not** rescue decision-grade inference.

## Integrated verdict vs 7 stop/go criteria (C10 delta)
C10.1 adds directional replication evidence (paired sign concordance) but not Hyperliquid evidence or magnitude certainty; C10.3 confirms pooled cross-venue inference remains **underpowered** (CI includes 0, non-significant permutation). C10.2 (Binance placebo) pending artifact — symmetry gap remains until produced. **No stop/go criterion flips to pass on C10.1/C10.3 alone.** Prior C8 findings (FRAGILE_NOT_DECISION_GRADE, buy leg negative, short-leg-carried, concentrated, stress-fragile) remain binding.

**Overall verdict: `NO_GO` (unchanged).** Edge is not established as decision-grade; Hyperliquid-native validation remains the only path to a potential `GO` and is externally blocked pending a verified operator archive (`ACCEPT_AS_EVIDENCE_CANDIDATE`). Do not promote point estimates to evidence. Cross-venue results are `is_hyperliquid_venue_data=false`.

## Next required work
1. Complete C10.2: wait for/ensure `research_state/placebo_portfolio_binance_um_multiyear.{json,md}` is written with real verdict; if process died, rerun the command above.
2. Update this consolidated verdict (new stem) to include C10.2 results, then re-run gates (`verify_next_focus_campaign.py` PASS, `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4) and re-timestamp `HANDOFF.md` to reflect full C10 completion.
3. If a verified Hyperliquid operator archive lands, prefer C9-step-2 Hyperliquid-native end-to-end over further cross-venue refinement.
