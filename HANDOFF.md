# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T11:42:50Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T11:42:50Z — BOTTLENECKS VERIFIED CLEAR + MANDATORY HEAVY CAMPAIGN (NON-NEGOTIABLE)
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks — CLEARED (re-verified 2026-11-07T11:42:50Z):** sole handoff is `HANDOFF.md` (no other `*handoff*` files). `git status` clean on `main` tracking `origin/main`. No uncommitted source drift. Non-canonical `research_state/candle_coverage_gap_report.json` remains quarantined as `.quarantined_noncanonical_tmp_20261107`; canonical is `research_state/candle_coverage_gap_report_verified_btceth_283d.json`. Python 3.12.3 with pytest/numpy/pandas/requests present.
- **Baseline (verified):** `python -m pytest tests/ -q --tb=no` → **382 passed, 11 skipped in 41.95s** (2026-11-07T11:42:50Z UTC).
- **Data/provenance boundary (enforced):** ONLY BTC/ETH 283d verified evidence exists (`research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, verified gap report). 0 trades in verified BTC/ETH campaign = truthful ground truth. Broader Hyperliquid altcoin 283d **not verified**. Never fabricate data/results, never relax provenance, never treat synthetic/quarantined/archive-mismatched artifacts as evidence.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T11:42:50Z | MANDATORY: HEDGE QTY/SIDE+FUNDING COMPLETENESS, SAME-BAR BOUNDARY CONTRACTS, REBOUND-SHORT ENTRY→HEDGE→EXIT ATOMICITY. Baseline 382 passed/11 skipped green. FAILING-TESTS-FIRST.`

**Required execution order (ship >=1 material hardened item this session):**
1. `python -m pytest tests/ -q` (must stay green baseline).
2. **Audit `src/backtest/engine.py` with spec lens:** (a) hedge qty/side/notional/funding correctness for long hedge on liquidation/stop/target/time/final and rebound hedge on liquidation/stop/target/time/final/no-break paths, including missing-ETH fallbacks and `hours_held` semantics; (b) same-bar priority/boundary behavior: liquidation checked first (worst price) — document/lock intended hourly-bar contract for ambiguous stop-vs-target on same candle if currently undefined; ensure funding/penalty/notional/timing consistent; (c) rebound-short after target: entry→hedge open→all exits must be atomic in accounting (no partial state leakage), hedge closes on every rebound-short exit, `risk_state` updates/notional handling correct, stopped buy path never triggers rebound short.
3. **Write FAILING regression tests first** that expose a real defect or lock an unproven critical contract (boundaries, missing-ETH, funding-on-missing bars, hedge consistency, atomicity). Prefer targeted tests under `tests/` with date suffix if new.
4. **Minimal fix only if tests expose a gap.** Do not refactor broadly. Preserve hourly-engine simplification boundaries.
5. `python -m pytest tests/ -q` — full suite green.
6. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[NOW] Hedge/liquidation/funding/boundary + rebound-short atomicity hardening** (engine correctness, failing-tests-first).
2. **No-lookahead & portfolio-cap residual regression watch** (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; add failing tests if any path found).
3. **$5M gating integrity regression watch** (all spec-compliant surfaces; do not conflate `backtest_simple` low-level executor behavior).
4. **Verified-data/provenance hardening** (fail-closed checksums/manifests; broaden universe only with archived verified data + full provenance).
5. **Every session gate:** `python -m pytest tests/ -q` green, ship >=1 material hardened item with evidence, update only `HANDOFF.md`.

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** Each session ships >=1 material item: spec-fidelity hardening + tests, or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening. Concrete evidence required.
- **Spec is truth:** PDF/spec authoritative. Both legs non-negotiable. ETH hedge every leg. Funding/liquidation correct on every leg. $5M gating everywhere spec-compliant. Equal-share cuts across old+new. Stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed), not volume-gated. Spec-compliant gating lives in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** Missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke)
- **Verified artifacts (canonical):** `research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`
- **Selected regressions:** `tests/test_funding_every_leg_missing_eth_audit_20261107.py`, `tests/test_rebound_short_liquidation_audit_20261107.py`, `tests/test_rebound_short_stop_funding_and_invariant_20261107.py`, `tests/test_long_leg_liquidation_hedge_completeness.py`, `tests/test_portfolio_no_lookahead_admission_sizing_gating_20261107.py`, `tests/test_volume_gating_integrity_20261107.py`, `tests/test_portfolio_reservation_overlay_cross_bar_cap_20261107.py`

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified (2026-11-07T11:42:50Z).
- [x] Baseline green (382 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [ ] **NEXT SESSION (NOW):** Execute hedge/liq/funding/boundary + rebound-short atomicity campaign (failing-tests-first). Ship >=1 material hardened item with concrete evidence. Full suite green. Update ONLY this `HANDOFF.md`.
