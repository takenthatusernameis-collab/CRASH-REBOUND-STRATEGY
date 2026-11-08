# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T10:30:06Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks. Only root `HANDOFF.md` is the durable handoff (verified 2026-11-08T10:24:00Z; `find` maxdepth 3 hits: `HANDOFF.md`, `scripts/controller_progress.py`, and `tests/*session_hardening*`/`*controller_progress*`/`*entry_next_bar*` test files — no parallel handoff/todo/next/roadmap/progress files). CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`). `git status --short` clean at session start; this session modified only `src/backtest/engine.py`, added `tests/test_final_exit_short_eth_series_aligned_fallback_20261108.py`, and updated `HANDOFF.md`. No untracked non-ignored files beyond the new test. Do not stage unrelated files.
- **Intentional non-bottleneck:** `scripts/fetch_hyperliquid_candles.py` prints fail-closed "BLOCKED..." on incomplete coverage/provenance — correct by design. Real 283d Hyperliquid data unavailable in this environment; expand universe only with archived verified data + full provenance.
- **Verified gate (this session, 2026-11-08T10:24:00Z):** `562 passed, 11 skipped` (573 collected; 11 pyarrow skips) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`. Core imports OK.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware path); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T10:24:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified gate (2026-11-08T10:24:00Z): 562 passed, 11 skipped (573 collected; 11 pyarrow skips) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`. Core imports OK. No bottlenecks; sole durable handoff is root HANDOFF.md.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate first (expect 562 passed, 11 skipped): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2) NEXT HEAVY — spec-fidelity hardening, one material defect-fix OR one failing-tests-first regression-lock minimum (highest-risk unproven path first):
   a) Funding on EVERY leg on ALL exits: short/absent ETH series mid-exit and long/rebound FINAL-exit misaligned-ETH-bar paths now locked (2026-11-08; `tests/test_final_exit_short_eth_series_aligned_fallback_20261108.py`). Remaining risk: rebound hedge entry when ETH series shorter than rebound-start index / mixed timestamp alignment assumptions; any path selecting ETH bar by array index where coin/ETH series lengths diverge non-trivially — audit/failing-tests-first lock.
   b) Liquidation worst-price + sequencing (checked before stop/target/time each bar): correct notional/timing/penalty. Remaining risk: liquidation + `entry_next_bar` interaction (fill at next open, liq on same/next bars), liquidation with cap-cut-adjusted shares/notional, and exact penalty base when commission/slippage active — lock with failing test if spec requires a specific base.
   c) 8x spec safety stop + stopped-buy invariant: ratio semantics and `entry_next_bar` re-anchor locked. Remaining risk: legacy/non-spec ATR-offset form only if retained in a spec-compliant path; missing-candle-field stop comparison paths.
   d) Rebound short lifecycle: opens only after long +9% target; anchored to executed short entry; `-9%`/`48h`/`+40%`; funding on coin leg and long ETH hedge on every exit. Remaining risk: rebound final-exit paths now partially locked; audit 48h/funding attribution when ETH series diverges at rebound start/final boundaries.
   e) ETH hedge every leg: vol-ratio `coin_vol/eth_vol` over 336h lookback, capped 3x; engine passes `candles[:hedge_hist_end]` (no look-ahead). Add engine-level lock only if a real branch gap is found (rebound sizing with short/divergent ETH series / cap in all branches).
   f) Signal/gating (CLEARED at known boundaries — do not regress): RSI(21)<20 next-hour open, deepest-first; `$5M` 24h volume in all spec-compliant gating paths. `avoid_downtrend` must NOT nullify spec-primary RSI trigger at known boundaries (SHIPPED). Audit only if you find a concrete uncovered non-spec default in spec-compliant wiring.
   g) Portfolio/risk: equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead. `run_portfolio.py` uses `_bar_realized/_bar_daily_hit` reconciled through bar `i` for same-bar admission probes; `tests/test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py` covers daily-loss leak. Remaining risk: add a failing-tests-first lock proving a same-bar probe's later-exit **positive realized PnL / capacity release** cannot leak into a sibling admission decision (reservation overlay only; exit effects reconciled at/through `i`).
   h) Entry/anchor fidelity: target/stop anchored to executed entry; `entry_next_bar` re-anchor locked. No anchor drift for rebound short or entry_next_bar paths.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
   For every real defect: write a failing spec-fidelity test first, fix minimally, prove pass. For a verified-non-defect item with insufficient direct lock: add a failing-tests-first regression-lock test, then move on.
4) If audit+locks show no uncovered defect after evidence-backed review of 2a-h, ship another material item (gated-pipeline/API-guardrail hardening or provenance/coverage guardrail) with failing-tests-first evidence.
5) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files. Do not stage/commit unrelated pre-existing modified files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **ACTIVE — spec-fidelity hardening audit + failing-tests-first locks** (one material item minimum): items 2a–h above. Prioritize: **(2b)** liquidation + `entry_next_bar` interaction and cap-cut-adjusted shares/penalty-base correctness; **(2g)** same-bar probe future-exit *positive* realized PnL/capacity-release must not leak into sibling admission (`test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py` covers loss/halt — add positive/capacity lock if needed); **(2a/e)** remaining ETH-bar alignment assumptions when coin/ETH series diverge non-trivially (mid paths + final-exit aligned fallback now locked). **(2e)** engine-level hedge cap/no-look-ahead only if a real branch gap found.
3. **Watch (regression-only, failing tests first):** Item 3 residual raw-ingress/provenance hardening (SHIPPED 06:00:26Z); validated-fact authority fail-closed (Item 4 cleared); RSI `avoid_downtrend` nullification at known boundaries (SHIPPED 07:13:10Z, 09:00:31Z); short/missing ETH hedge funding on all exits (SHIPPED 09:15:40Z, 10:15:30Z); final-exit short ETH series misaligned `eth_candles[-1]` (SHIPPED+FIXED 2026-11-08T10:24:00Z).
4. **Optional only after 2–3:** refactor only when it reduces spec-fidelity risk and is test-covered.
5. **Material shipped item definition:** spec-fidelity defect fix+tests, regression-lock test for a real uncovered spec path, or material gated-pipeline/API-guardrail/provenance hardening — with concrete failing-tests-first evidence.
6. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T10:24:00Z (MATERIAL spec-fidelity defect fix + regression locks / 2a):** Failing-tests-first: long and rebound final-exit (end of coin series) used `eth_candles[-1]` unconditionally for ETH hedge exit/funding accounting, selecting a misaligned ETH bar when ETH series was shorter than the coin exit index (probe: coin bar 19, ETH bar 7 returned `hedge_exit=9999` instead of aligned fallback). Fixed in `src/backtest/engine.py` to require `final_coin_idx < len(eth_candles)` (aligned bar) else fall back to hedge entry for exit-price accounting while still applying funding (`_apply_funding_pnl`, hourly funding on every leg). Added `tests/test_final_exit_short_eth_series_aligned_fallback_20261108.py` (4 tests: long/rebound misaligned fallback + funding delta; long/rebound aligned bar correctness). Full gate 562 passed, 11 skipped (+4).
- **2026-11-08T10:15:30Z (MATERIAL regression-lock / spec-fidelity audit 2a):** Mid-exit short-ETH-series (`idx >= len(eth_candles)`) funding on all exit paths locked (`tests/test_eth_short_series_hedge_funding_all_exits_20261108.py`, 8). No engine defect. Gate 558/11.
- **2026-11-08T09:25:16Z (MATERIAL regression-lock / spec-fidelity audit 2c,2e coverage):** Engine-level 8x spec safety stop `entry_next_bar` re-anchor + signal->engine invariant; ETH hedge 336h window/cap locks at sizing (`tests/test_engine_spec_safety_stop_hedge_ratio_locks_20261108.py`, 5). Gate 550/11.
- **2026-11-08T09:15:40Z (MATERIAL regression-lock / 2a):** Missing-ETH-bar hedge funding all-exit-path coverage extended (`tests/test_missing_eth_hedge_funding_all_exit_paths_20261108.py`, 4). Gate 545/11.
- **2026-11-08T09:00:31Z (MATERIAL spec-fidelity defect fix):** RSI trigger no-op removed at universe-gating boundary (`filter_universe`/`passes_universe_filter` default `skip_downtrend_filter` in RSI-trigger mode). Gate 541/11 (+6).
- **2026-11-08T07:13:10Z (MATERIAL spec-fidelity defect fix):** RSI<20 trigger not nullified by non-spec `avoid_downtrend` in `generate_signal`/`regime_ok`. Gate 535/11 (+5).
- **2026-11-08T07:01:32Z:** rebound-short 48h max-hold/funding inclusive semantics aligned. Gate 530/11.
- **2026-11-08T06:15:00Z:** `entry_next_bar` target/stop re-anchor to executed entry. Gate 529/11 (+2).
- **2026-11-08T06:00:26Z / 05:17:30Z / 04:27Z / 03:21:21Z / 03:10:50Z / 02:35:37Z / 02:21:02Z / 723144c / 01:14:16Z / 00:29:47Z:** Item 3 residual provenance/raw-ingress fail-closed hardening, synthetic-check/sha256 emission, structural validation fail-closed, final-bar exit occupancy release. 527→503→494→487→486.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Active:** complete evidence-backed spec-fidelity audit for items 2a–h with failing-tests-first defect fixes or regression locks. Highest-value targets: **(2b)** liquidation + `entry_next_bar` interaction and cap-cut-adjusted shares/penalty-base correctness; **(2g)** same-bar probe future-exit positive realized PnL/capacity-release must not leak into sibling admission (add failing-tests-first lock if not already implied); **(2a/e)** ETH bar alignment when coin/ETH series diverge non-trivially at rebound/entry boundaries (final-exit aligned fallback now fixed/locked). **(2e)** engine-level hedge cap/no-look-ahead only if a real branch gap found.
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
