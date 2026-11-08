# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T07:01:32Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks. Only root HANDOFF.md exists. CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Baseline (this session):** gate `530 passed, 11 skipped` (~27.2s) at 2026-11-08T07:01:32Z (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`). Entry baseline `529 passed, 11 skipped`; +1 from failing-tests-first rebound-short 48h time-exit/funding spec test.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics); rebound short `-9%/48h/+40%`; ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T07:01:32Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline: 530 passed, 11 skipped (PYTHONPATH=. python3 -m pytest tests/ -q --tb=no, ~27.2s, 2026-11-08T07:01:32Z). No bottlenecks. Sole durable handoff: root HANDOFF.md only.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 530+ passed, 11 skipped).
2) NEXT HEAVY — spec-fidelity engine hardening audit + failing-tests-first test coverage (crash-rebound-strategy.pdf / research_state/strategy_spec.md), one material item minimum:
    a) Hourly funding on EVERY leg (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on ALL exits incl. edge/missing-data/missing-ETH/fallback paths. Verify each exit path (liquidated/stopped/target/time_exit/final) deducts/credits funding on both coin leg and ETH hedge leg.
    b) Hourly liquidation at worst price: correct sequencing (liquidation checked before stop/target/time each bar); correct notional/timing/penalty on all exit paths.
    c) 8x safety stop (`use_spec_safety_stop` ratio semantics: entry*(1-8*range_ratio)); stopped buy never opens rebound short (rebound short only on +9% target hit).
    d) Rebound short `-9%` target / `48h` max hold / `+40%` stop; ETH hedge every leg; vol-ratio over 336h capped 3x. (48h time-exit bar-count/funding semantics spec-locked 2026-11-08T07:01:32Z — do not regress.)
    e) `RSI(21)<20` next-hour open, deepest-first crash first (run_portfolio.py `_crash_severity`/candidate sort); `>= $5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`).
    f) Equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead (hist[:i+1] only in runner).
    g) Target/stop anchored to executed entry (SHIPPED 2026-11-08T06:15:00Z); rebound short enters at executed long exit — verify no anchor drift.
    Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/run_portfolio.py`.
    Anchor every change with a failing spec-fidelity test first; prove the fix with the test passing.
3) If (2) audit finds no real defect for an item after evidence-backed review, add a failing-tests-first regression-lock test for that spec item, then move to next item.
4) If all items a-g are test-locked with no defects, ship another material item (gated-pipeline/API-guardrail hardening) with failing-tests-first evidence.
5) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **ACTIVE — spec-fidelity engine hardening audit + test-lock coverage** (failing-tests-first, one material item minimum): hourly funding/liquidation/stops/rebound/hedge/volume-gating/cap/no-look-ahead per spec (INITIAL TASK step 2). Goal: every spec item a-g locked with failing-then-passing/regression tests.
3. **Item 3 residual (SHIPPED 2026-11-08T06:00:26Z):** verified-data/provenance/raw-ingress hardening complete. Fix regressions only with failing tests.
4. **Item 4 watch (cleared):** validated-fact authority fail-closed. Fix regressions only with failing tests.
5. **Optional only after 2–3:** refactor only when it reduces spec-fidelity risk and is test-covered.
6. **Material shipped item definition:** spec-fidelity hardening+tests (incl. regression-lock tests), or verified-data/provenance hardening, or material gated-pipeline/API-guardrail hardening — with concrete failing-tests-first evidence.
7. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T07:01:32Z (this session, MATERIAL):** spec-fidelity fix — rebound-short 48h max-hold time-exit bar-count/funding semantics made consistent with long-leg 50h semantics (hourly funding on every leg; "48 hours at latest").
  - **Failing-tests-first:** new `tests/test_rebound_short_time_exit_48h_funding_spec_20261108.py` (1 test) failed pre-fix: `short pnl 5.341 != expected 5.232 (funding_benefit=5.232 for 48h)` — engine charged 49h-equivalent funding while holding 49 bars due to off-by-one condition (`(sidx-short_start_idx) >= 48` with `hours = sidx-short_start_idx+1`).
  - **Fix:** `src/backtest/engine.py` rebound-short time-exit path: condition changed to `(sidx - short_start_idx + 1) >= short_bars_max` so N-bar max hold = N funding hours (inclusive), matching long-leg `(idx - start_idx + 1) >= config.time_exit_max_bars`.
  - **Evidence:** new test PASSED post-fix. Updated `tests/test_rebound_short_funding_all_paths.py` time_exit expectation `PATH_SHORT_HOURS['time_exit']=5` to match spec-consistent inclusive counting for `reb_time=5` (was 6); that test now passes and still validates funding on every exit path.
  - **Commands:** `PYTHONPATH=. python3 -m pytest tests/test_rebound_short_time_exit_48h_funding_spec_20261108.py -v` (pre-fix FAIL, post-fix PASS); `PYTHONPATH=. python3 -m pytest tests/test_rebound_short_funding_all_paths.py tests/test_rebound_short_stop_funding_and_invariant_20261107.py tests/test_rebound_short_attribution_and_risk_state_20261107.py tests/test_rebound_short_liquidation_audit_20261107.py -q` (22 passed); final `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` → **`530 passed, 11 skipped`**.
- **2026-11-08T06:58:30Z (prior):** handoff refresh; baseline 529/11.
- **2026-11-08T06:15:00Z:** entry_next_bar target/stop re-anchor to executed entry (`src/backtest/engine.py`, +2 tests). 529/11.
- **2026-11-08T06:00:26Z:** Item 3 residual — raw-ingress fail-closed + gap-report scan never upgrades unverified. 527/11.
- **2026-11-08T05:17:30Z:** gap-report archive scan fail-closed on declared synthetic. 525/11.
- **2026-11-08T04:27Z:** raw-ingress fail-closed APIs + consumer wiring. 522/11.
- **2026-11-08T03:21:21Z:** structural-validation fail-closed at cache emission. 507/11.
- **2026-11-08T03:10:50Z:** merge_verified_archives emits payload sha256 w/ synthetic_check. 504/11.
- **2026-11-08T02:35:37Z / 02:21:02Z / 723144c / 01:14:16Z / 00:29:47Z:** fail-closed synthetic/provenance hardening + final-bar exit releases occupancy. 503→494→487→486.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Next heavy (active campaign):** continue spec-fidelity engine hardening audit + failing-tests-first test-lock coverage for remaining spec items a-g (funding/liquidation sequencing & all exit paths incl. missing-ETH edge cases; 8x stop/stopped-buy-no-rebound-short invariants; rebound short `-9%/+40%` anchors; ETH hedge vol-ratio 336h cap 3x; RSI(21)<20 next-hour open deepest-first; $5M gating everywhere; equal-share cuts across 120% cap old+new; one position/coin; strict no-look-ahead). Ship >=1 material item with failing-then-passing evidence.
- **Watch:** occupancy/lifecycle/no-lookahead/cap and validated-fact regressions — fix only with failing tests.
- **Environment constraint:** real 283d Hyperliquid candles unavailable here; expand universe only with archived verified data + full provenance. Canonical BTC/ETH placeholder remains fail-closed by design.

## CRITICAL CONTEXT
- **Spec:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke), `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`
- **Canonical artifacts:** `research_state/cache/hyperliquid_verified_283d_btceth/` (placeholder fail-closed), `research_state/universe_verified.json`, `research_state/real_campaign_verified_btceth_283d*.json`, `research_state/candle_coverage_gap_report_verified_btceth_283d.json`

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** each session ships >=1 material item with concrete evidence.
- **Spec is truth:** both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating in all spec-compliant paths, equal-share cuts across old+new, stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
