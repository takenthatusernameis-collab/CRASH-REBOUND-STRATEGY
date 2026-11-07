# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-11-07T12:27:42Z
## SINGLE CANONICAL HANDOFF
Only this root `HANDOFF.md` is durable. Do **not** create/read any other handoff file.

## SESSION 2026-11-07T12:27:42Z — BOTTLENECK CLEARED + RISKSTATE TIMESTAMP NORMALIZATION (MATERIAL, EVIDENCED)
- **Repo-name priority:** `CRASH-REBOUND-STRATEGY` → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly engine only; **do not claim** 20s slicing / explicit spread / L2 order-book impact.
- **Non-negotiable spec contracts:** hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths and missing/incomplete bars as applicable; hourly liquidation at worst price with correct sequencing vs stop/target/time, correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.
- **Bottlenecks — CLEARED (re-verified 2026-11-07T12:27:42Z):** sole durable handoff is this root `HANDOFF.md` (no other `*handoff*` files in repo/worktree except quarantined non-handoff artifacts). `git status` clean on `main` before session edits. No active session blockers removed except a real failing baseline test exposed during verification.
- **Baseline on session start (verified):** `python -m pytest tests/ -q --tb=no` → **1 failed, 383 passed, 11 skipped**. Failure: `tests/test_crash_rebound_strategy.py::test_engine_applies_equal_share_cuts_to_existing_positions` (`open_position_notionals` became `[]` after timestamped close; expected `[60000.0]`).
- **Root cause (material accounting defect):** `RiskState.apply_trade` reset state on any string date mismatch. Engine closes pass full ISO timestamps (`YYYY-MM-DDTHH:MM:SS`) while state may hold `YYYY-MM-DD`; same-calendar-day close wiped `open_position_notionals`, causing duplicate-notional removal across equal-share-cut persisted lists (old+new both cut to 60k; close removed both 60k entries).
- **Shipped (failing-tests-first, minimal fix):**
  - Added regression `tests/test_risk_apply_trade_timestamp_normalization_20261107.py` (3 tests): timestamp-format close preserves live notionals/exposure/open positions and realized PnL/daily-halt flags on same day; new-day reset preserves live exposure if positions still open; stale notionals cleared only when flat on new day.
  - Fixed `src/strategy/risk.py::RiskState.apply_trade`: normalize to calendar day (`str(date)[:10]`), do not wipe live position accounting on format-only changes; reset daily counters on true day change, but preserve live notionals when exposure/positions remain open.
- **Verification evidence (2026-11-07T12:27:42Z UTC):**
  - `python -m pytest tests/test_crash_rebound_strategy.py -q` → **46 passed** (previously 1 failed in this module context).
  - `python -m pytest tests/test_risk_apply_trade_timestamp_normalization_20261107.py -q` → **3 passed**.
  - `python -m pytest tests/ -q --tb=no` → **387 passed, 11 skipped in 41.62s**.
- **Data/provenance boundary (unchanged, enforced):** ONLY BTC/ETH 283d verified evidence exists (`research_state/cache/hyperliquid_verified_283d_btceth/`, `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`). 0 trades in verified BTC/ETH campaign = truthful ground truth. Broader Hyperliquid altcoin 283d **not verified**. Never fabricate data/results, never relax provenance, never treat synthetic/quarantined/archive-mismatched artifacts as evidence.
- **Engine audit notes (not all shipped; targeted for next heavy work):** liquidation-first/stop/target ordering is present in long and rebound-short loops; funding applied on many leg paths; rebound-short exits close rebound hedge and apply funding in audited paths. Remaining risk: rebound-short hedge `hedge_pnl`/field attribution in `TradeResult` may not fully surface rebound-hedge component separately (probe showed `hedge_pnl`/hedge fields not reflecting rebound-hedge leg while `total_pnl` changed with funding); rebound-short is not registered as an opened notional in `risk_state` (long closed at target) — verify atomic accounting/portfolio invariants for all callers; same-bar stop-vs-target contract is currently ordered but should be explicitly locked by tests where ambiguous; rebound-short hedge missing-ETH exit fallback applies funding but attribution/contract tests can be tightened.
- **Files changed this session:** `src/strategy/risk.py`, `tests/test_risk_apply_trade_timestamp_normalization_20261107.py`, `HANDOFF.md`.

## INITIAL TASK MESSAGE (TIMESTAMPED, SINGLE, NEXT AGENTIC SESSION) — EXECUTE HEAVY WORK NOW
`CRASH-REBOUND-STRATEGY | 2026-11-07T12:27:42Z | MANDATORY: REBOUND-SHORT HEDGE FUNDING/ATTRIBUTION + ATOMIC RISK/TRADE-LOG CONTRACTS, EXPLICIT SAME-BAR BOUNDARY TESTS. Baseline 387 passed/11 skipped green. FAILING-TESTS-FIRST.`

**Required execution order (ship >=1 material hardened item this session):**
1. `python -m pytest tests/ -q --tb=no` (must stay green baseline: 387 passed, 11 skipped expected absent environment drift).
2. **Audit `src/backtest/engine.py` rebound-short/hedge contracts:** (a) confirm rebound-short entry→hedge open→all exits are atomic in accounting (no partial state leakage); document whether rebound short should affect `risk_state` notional/open-position semantics and make explicit via failing tests + minimal fix if needed; (b) fix/lock rebound-hedge PnL/funding attribution in `TradeResult` (`hedge_pnl`/hedge fields/trades) so every leg’s funding and price PnL is auditable and consistent with `total_pnl`; (c) missing-ETH exit fallback for rebound hedge must preserve funding/notional/timing correctness with explicit regression.
3. **Add explicit same-bar boundary regressions** (hourly worst-price contract): liquidation before stop before target for long; liquidation before stop before target for rebound short (already partially covered — extend/lock intended contract where still ambiguous).
4. **Write FAILING regression tests first** that expose a real defect or lock an unproven critical contract. Minimal fix only if tests expose a gap. Do not refactor broadly.
5. `python -m pytest tests/ -q --tb=no` — full suite green.
6. **Update ONLY this root `HANDOFF.md`** with UTC timestamp, exact commands/results, files changed, shipped material item(s), remaining risks, and next heavy task. No other handoff files.

## HEAVY FOCUS CAMPAIGN (MUST EXECUTE IN ORDER; FUTURE AGENTS MAY NOT AVOID)
1. **[NOW] Rebound-short hedge funding/attribution + atomic risk/trade-log contracts; same-bar boundary lock** (engine correctness, failing-tests-first).
2. **No-lookahead & portfolio-cap residual regression watch** (admission/sizing/gating/history/cap cuts equal-share old+new, no top-ups; timestamp/day normalization consistent across portfolio + engine).
3. **$5M gating integrity regression watch** (all spec-compliant surfaces; do not conflate `backtest_simple` low-level executor behavior).
4. **Verified-data/provenance hardening** (fail-closed checksums/manifests; broaden universe only with archived verified data + full provenance).
5. **Every session gate:** `python -m pytest tests/ -q --tb=no` green, ship >=1 material hardened item with evidence, update only `HANDOFF.md`.

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

## SUCCESS CRITERIA
- [x] Bottlenecks cleared & re-verified (2026-11-07T12:27:42Z).
- [x] Baseline green and improved (387 passed, 11 skipped).
- [x] 283d BTC/ETH verified/provenanced; real campaign truthful (0 trades).
- [x] Material item shipped with evidence: RiskState timestamp-normalized daily accounting preserves live cap-cut/notional state (failing test fixed + 3 regressions added).
- [ ] **NEXT SESSION (NOW):** Rebound-short hedge funding/attribution + atomic risk/trade-log contracts + explicit same-bar boundary tests (failing-tests-first). Ship >=1 material hardened item with concrete evidence. Full suite green. Update ONLY this `HANDOFF.md`.
