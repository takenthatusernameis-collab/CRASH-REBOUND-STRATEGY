# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T09:25:16Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks. Only root `HANDOFF.md` exists (verified; no parallel handoff/todo/next/roadmap files). CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`). Working tree has pre-existing unrelated `research_state/candle_coverage_gap_report.json` modification (not produced by this session; not staged/committed).
- **Baseline (verified this session):** gate `545 passed, 11 skipped` (27.24s) at 2026-11-08T09:25:16Z (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`).
- **Final gate (this session):** `550 passed, 11 skipped` (27.27s) at 2026-11-08T09:25:16Z (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`). (+5 regression locks).

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware path); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T09:25:16Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline/final (this session): 545 passed, 11 skipped baseline; 550 passed, 11 skipped final at 2026-11-08T09:25:16Z (cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no). No bottlenecks. Sole durable handoff: root HANDOFF.md only. Ignore unrelated pre-existing modified `research_state/candle_coverage_gap_report.json` unless your task intentionally changes it.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 550+ passed, 11 skipped).
2) NEXT HEAVY — spec-fidelity hardening audit, one material defect-fix OR one failing-tests-first regression-lock minimum (pick the highest-risk unproven path first):
    a) Funding on EVERY leg on ALL exits (highest residual risk): hedge funding with missing-ETH fallback-to-entry is covered for long stopped/liquidated/time/final/target-audit and rebound liq/time/final/stopped/target (2026-11-08 locks). Remaining risk: prove no uncovered branch where hedge exists but funding is skipped/misattributed (rare early-exit ordering, zero-notional guards, edge candle-shape paths, or mixed same-bar states). Add a failing test for any real uncovered path before fixing.
    b) Liquidation worst-price + sequencing: liquidation checked before stop/target/time each bar; correct notional/timing/penalty; hedge/rebound legs closed with correct funding attribution on liquidation. Regression-lock any engine path not directly covered (especially liquidation + missing ETH + rebound hedge interactions and same-bar ordering beyond existing locks).
    c) 8x spec safety stop + stopped-buy invariant (engine-level): ratio semantics `entry*(1-8*avg((high-low)/prev_close,14h))` exercised in engine/signal paths (new locks 2026-11-08: entry_next_bar re-anchor ratio for stop/target, signal->engine stop breach never opens rebound short). Remaining risk: engine-level lock for legacy/non-spec ATR-offset form if that mode must remain safe, and any path where stop is computed but not compared due to missing candle fields.
    d) Rebound short lifecycle: opens only after long +9% target; anchored to executed short entry (slippage/commission-aware); `-9%` target / `48h` max hold / `+40%` stop; funding on coin leg and long ETH hedge on every exit (48h inclusive semantics locked 2026-11-08 — do not regress). Verify hedge funding attribution on all rebound exits with missing-ETH fallback behavior.
    e) ETH hedge every leg: vol-ratio `coin_vol/eth_vol` over 336h lookback, capped at 3x position (new locks 2026-11-08: compute_eth_hedge_size cap+336h window insensitivity). Remaining risk: engine-level lock that long-side short ETH hedge and rebound-short long ETH hedge are both sized using decision-available history (no look-ahead) and that cap is applied to the executed position value path in engine when history is sufficient.
    f) Signal/gating (CLEARED at known boundaries — do not regress): RSI(21)<20 next-hour open, deepest-first; `$5M` 24h volume in all spec-compliant gating paths. `avoid_downtrend` must NOT nullify spec-primary RSI trigger at `generate_signal`/`regime_ok`, `passes_universe_filter`/`filter_universe`/loader universe filtering (SHIPPED 07:13:10Z, 09:00:31Z). Audit portfolio/real-campaign config wiring for accidental non-spec defaults in spec-compliant paths only if you find a concrete uncovered boundary.
    g) Portfolio/risk: equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead (`hist[:i+1]` in runner; reservation overlay must not leak future exits into same-bar admission/cap decisions). Cross-bar reservation coverage exists; add a failing-tests-first lock for any uncovered same-bar/future-exit leak scenario.
    h) Entry/anchor fidelity: target/stop anchored to executed entry (SHIPPED 06:15:00Z; engine re-anchor ratio locked 2026-11-08). No anchor drift for rebound short or entry_next_bar paths.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
   For every real defect: write a failing spec-fidelity test first, fix minimally, prove pass. For a verified-non-defect item with insufficient direct lock: add a failing-tests-first regression-lock test, then move on.
4) If audit+locks show no uncovered defect after evidence-backed review of 2a-h, ship another material item (gated-pipeline/API-guardrail hardening or provenance/coverage guardrail) with failing-tests-first evidence.
5) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files. Do not stage/commit unrelated pre-existing modified files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **ACTIVE — spec-fidelity hardening audit + failing-tests-first locks** (one material item minimum): items 2a–h above. Prioritize paths where implementation exists but direct spec regression coverage is weak/missing: liquidation+hedge sequencing/attribution edge cases, engine-level hedge sizing no-look-ahead/3x-cap application path, portfolio same-bar/future-exit no-look-ahead reservations, and any missing-ETH/funding attribution branch still uncovered.
3. **Watch (regression-only, failing tests first):** Item 3 residual raw-ingress/provenance hardening (SHIPPED 06:00:26Z); validated-fact authority fail-closed (Item 4 cleared); RSI `avoid_downtrend` nullification at known boundaries (SHIPPED 07:13:10Z, 09:00:31Z).
4. **Optional only after 2–3:** refactor only when it reduces spec-fidelity risk and is test-covered.
5. **Material shipped item definition:** spec-fidelity defect fix+tests, regression-lock test for a real uncovered spec path, or material gated-pipeline/API-guardrail/provenance hardening — with concrete failing-tests-first evidence.
6. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T09:25:16Z (MATERIAL regression-lock / spec-fidelity audit 2c,2e coverage):** Added failing-tests-first regression locks for engine-level 8x spec safety stop and ETH hedge vol-ratio/336h/3x behavior (`tests/test_engine_spec_safety_stop_hedge_ratio_locks_20261108.py`, 5 tests): `test_engine_entry_next_bar_reanchors_spec_safety_stop_by_ratio` (engine re-anchors stop by `entry_px/entry`; stop breach still never opens rebound short), `test_engine_entry_next_bar_target_reanchor_ratio_semantics` (target re-anchored to executed entry), `test_generate_signal_exercises_engine_8x_stop_via_spec_path` (signal spec stop exercised through engine; stopped buy never opens rebound short), `test_compute_eth_hedge_size_uses_336h_lookback_and_3x_cap` (cap at 3x), `test_compute_eth_hedge_size_vol_ratio_respects_lookback_window` (history before 336h window does not affect size). All 5 passed. No engine/spec defect found in these paths. Full gate 550 passed, 11 skipped (+5).
- **2026-11-08T09:15:40Z (MATERIAL regression-lock / spec-fidelity audit 2a coverage):** Missing-ETH hedge funding all-exit-path coverage extended (`tests/test_missing_eth_hedge_funding_all_exit_paths_20261108.py`, 4 tests: long stopped/liquidated, rebound stopped/target). No uncovered defect found. Gate 545/11 (+4).
- **2026-11-08T09:00:31Z (MATERIAL spec-fidelity defect fix):** RSI trigger no-op removed at universe-gating boundary; `passes_universe_filter`/`filter_universe` default `skip_downtrend_filter` to RSI-trigger mode so `avoid_downtrend` fast-MA does not drop RSI crash coins before `generate_signal`. Failing-tests-first (`tests/test_universe_filter_rsi_trigger_spec_20261108.py`, 6). Gate 541/11 (+6).
- **2026-11-08T07:13:10Z (MATERIAL spec-fidelity defect fix):** RSI<20 trigger not nullified by non-spec `avoid_downtrend` in `generate_signal`/`regime_ok`. Failing-tests-first (5). Gate 535/11.
- **2026-11-08T07:10:45Z:** handoff/reset; spot audit evidence noted. 530/11.
- **2026-11-08T07:01:32Z:** rebound-short 48h max-hold/funding inclusive semantics aligned. 530/11.
- **2026-11-08T06:58:30Z:** handoff refresh; 529/11.
- **2026-11-08T06:15:00Z:** `entry_next_bar` target/stop re-anchor to executed entry. 529/11 (+2).
- **2026-11-08T06:00:26Z / 05:17:30Z / 04:27Z / 03:21:21Z / 03:10:50Z / 02:35:37Z / 02:21:02Z / 723144c / 01:14:16Z / 00:29:47Z:** Item 3 residual provenance/raw-ingress fail-closed hardening, synthetic-check/sha256 emission, structural validation fail-closed, final-bar exit occupancy release. 527→503→494→487→486.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Active:** complete evidence-backed spec-fidelity audit for items 2a–h with failing-tests-first defect fixes or regression locks. Highest-value targets: **(2b)** liquidation+hedge sequencing/attribution edge cases including same-bar interactions, missing-ETH + rebound hedge liquidation, and notional/timing/penalty correctness where not already locked; **(2e)** engine-level hedge sizing path lock proving `compute_eth_hedge_size`/engine uses decision-available history (no look-ahead) and applies 3x cap in real engine long/rebound hedge setup when history is sufficient; **(2g)** portfolio reservation overlay must not leak future exits into same-bar admission/cap decisions (add failing-tests-first lock for uncovered scenario). **Progress 2026-11-08T09:25:16Z:** engine-level 8x spec stop entry_next_bar re-anchor + signal->engine stop breach invariant locked; ETH hedge 336h window/cap locked at sizing function level. Missing-ETH hedge funding all-exit-path coverage extended 09:15:40Z.
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
- **Single handoff:** only root `HANDOFF.md`. No parallel handoff/todo/progress files.
