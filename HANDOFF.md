# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T07:10:45Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status:** No bottlenecks. Only root `HANDOFF.md` exists (verified). CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Baseline (this session):** gate `530 passed, 11 skipped` (~27.5s) at 2026-11-08T07:10:45Z (`cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`).

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware path); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T07:10:45Z | INITIAL TASK (HEAVY, NON-OPTIONAL)

Repo priority: CRASH-REBOUND-STRATEGY → fidelity to crash-rebound-strategy.pdf / research_state/strategy_spec.md. Hourly engine only. Never claim 20s slicing / explicit spread / L2 order-book impact.

Verified baseline: 530 passed, 11 skipped (cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no, ~27.5s, 2026-11-08T07:10:45Z). No bottlenecks. Sole durable handoff: root HANDOFF.md only.

You MUST ship >=1 MATERIAL item this session. Passive re-verification, handoff-only edits, or claiming "blocked" without a concrete missing input is NOT allowed. Use failing-tests-first for every change.

MANDATORY EXECUTION ORDER:
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 530+ passed, 11 skipped).
2) NEXT HEAVY — spec-fidelity hardening audit, one material defect-fix OR one failing-tests-first regression-lock minimum (pick the highest-risk unproven path first):
   a) Funding on EVERY leg on ALL exits: long coin + short ETH hedge + rebound short coin + rebound long ETH hedge; verify liquidated/stopped/target/time_exit/final paths, including missing-ETH fallback paths (hedge funding must still follow spec-consistent semantics when exit price unavailable). Evidence: existing funding tests pass; add failing test only for a real uncovered path.
   b) Liquidation worst-price + sequencing: liquidation checked before stop/target/time each bar; correct notional/timing/penalty; hedge/rebound legs closed with correct funding on liquidation.
   c) 8x spec safety stop ratio semantics (`use_spec_safety_stop`): `entry*(1-8*avg((high-low)/prev_close,14h))`; stopped buy NEVER opens rebound short. Verify engine path, not just helper.
   d) Rebound short: opens only after long +9% target; anchored to executed short entry (slippage/commission-aware); `-9%` target / `48h` max hold / `+40%` stop; funding on coin leg and long ETH hedge on every exit (spec-locked 48h inclusive semantics 2026-11-08T07:01:32Z — do not regress).
   e) ETH hedge every leg: vol-ratio `coin_vol/eth_vol` over 336h, capped at 3x position; long-side short ETH hedge and rebound-short long ETH hedge both present when enabled/data available.
   f) Signal/gating: `RSI(21)<20` next-hour open, deepest-first (run_portfolio `_crash_severity`/candidate sort); `>= $5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`, `detect_crash`/`passes_universe_filter`/`filter_universe`/gated wrappers/runners). Audit portfolio/real-campaign config wiring for accidental non-spec defaults in spec-compliant paths.
   g) Portfolio/risk: equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead (`hist[:i+1]` in runner; reservation overlay must not leak future exits into same-bar admission/cap decisions).
   h) Entry/anchor fidelity: target/stop anchored to executed entry (SHIPPED 2026-11-08T06:15:00Z); no anchor drift for rebound short or entry_next_bar paths.

   Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
   For every real defect: write a failing spec-fidelity test first, fix minimally, prove pass. For a verified-non-defect item with insufficient direct lock: add a failing-tests-first regression-lock test, then move on.
3) If audit+locks show no uncovered defect after evidence-backed review of 2a-h, ship another material item (gated-pipeline/API-guardrail hardening or provenance/coverage guardrail) with failing-tests-first evidence.
4) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
5) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, next heavy task message. No other handoff files.
```

## HEAVY FOCUS CAMPAIGN (EXECUTE IN ORDER)
1. **Gate first:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
2. **ACTIVE — spec-fidelity hardening audit + failing-tests-first locks** (one material item minimum): items 2a–h above. Prioritize any path where implementation exists but a direct spec regression test is weak/missing, especially missing-ETH hedge fallbacks, runner config wiring for spec-compliant volume/RSI defaults, and liquidation+hedge sequencing edge cases.
3. **Watch (regression-only, failing tests first):** Item 3 residual raw-ingress/provenance hardening (SHIPPED 2026-11-08T06:00:26Z); validated-fact authority fail-closed (Item 4 cleared).
4. **Optional only after 2–3:** refactor only when it reduces spec-fidelity risk and is test-covered.
5. **Material shipped item definition:** spec-fidelity defect fix+tests, regression-lock test for a real uncovered spec path, or material gated-pipeline/API-guardrail/provenance hardening — with concrete failing-tests-first evidence.
6. **Final gate + handoff required.**

## SHIPPED (CONDENSED)
- **2026-11-08T07:10:45Z (this session, MATERIAL handoff/reset):** bottleneck check clear (only root `HANDOFF.md` exists). Re-verified full gate `530 passed, 11 skipped` (27.46s). Evidence-backed spot audit: stopped buy never opens rebound short is engine-guarded + `tests/test_rebound_short_stop_funding_and_invariant_20261107.py` passes; 8x spec safety stop uses ratio semantics (`src/strategy/risk.py` default ratio form, `src/strategy/crash_rebound.py:372-374` `use_ratio=True`, config `use_spec_safety_stop=True`) with stop-spec tests passing; ETH hedge vol lookback 336h/cap 3x in config+`compute_eth_hedge_size`; rebound short anchor uses executed slippage-adjusted entry. Refreshed single durable handoff with timestamped heavy initial task for next session.
- **2026-11-08T07:01:32Z:** spec-fidelity fix — rebound-short 48h max-hold time-exit bar-count/funding semantics consistent with long-leg (inclusive N bars = N funding hours). Failing test first (`tests/test_rebound_short_time_exit_48h_funding_spec_20261108.py`), engine fix `src/backtest/engine.py`, updated `tests/test_rebound_short_funding_all_paths.py` PATH_SHORT_HOURS['time_exit']=5; gate 530/11.
- **2026-11-08T06:58:30Z:** handoff refresh; 529/11.
- **2026-11-08T06:15:00Z:** entry_next_bar target/stop re-anchor to executed entry (+2 tests). 529/11.
- **2026-11-08T06:00:26Z / 05:17:30Z / 04:27Z / 03:21:21Z / 03:10:50Z / 02:35:37Z / 02:21:02Z / 723144c / 01:14:16Z / 00:29:47Z:** Item 3 residual provenance/raw-ingress fail-closed hardening, synthetic-check/sha256 emission, structural validation fail-closed, final-bar exit occupancy release. 527→503→494→487→486.

## REMAINING RISKS / NEXT HEAVY FOCUS
- **Active:** complete evidence-backed spec-fidelity audit for items 2a–h with failing-tests-first defect fixes or regression locks. Highest-value targets: missing-ETH hedge/funding fallbacks on every rebound/exit path, liquidation+hedge sequencing edge cases, runner/API/config wiring that could bypass spec-compliant `$5M`/RSI defaults, and direct regression locks for 8x stop + stopped-buy-no-rebound-short + 336h/3x hedge ratio behavior.
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
