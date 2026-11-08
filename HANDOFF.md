# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T12:50:22Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status (2026-11-08T12:50:22Z):** No blockers. Only root `HANDOFF.md` exists as durable handoff. No `.lock` files. CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`). Bottleneck removal rule: if you find another durable handoff/task file, stale lock, or failing gate, delete/consolidate the duplicate handoff into root `HANDOFF.md` or fix the gate **before** other work (failing-tests-first). Verified gate: `575 passed, 11 skipped` (586 collected; 11 pyarrow skips).
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` prints fail-closed `BLOCKED...` on incomplete coverage/provenance — correct by design. Real 283d Hyperliquid data unavailable in this environment; expand universe only with archived verified data + full provenance. Never fabricate numbers/artifacts.
- **Verified gate (2026-11-08T12:50:22Z):** `575 passed, 11 skipped` (586 collected; 11 pyarrow skips) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`. Core imports OK.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware path); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T12:50:22Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact — those are not implemented in this hourly engine.

Bottleneck check (done 2026-11-08T12:50:22Z): no blockers. Only root `HANDOFF.md` exists. No `.lock` files. CI runs `python -m pytest tests/ -q`. Gate: `575 passed, 11 skipped` (586 collected; 11 pyarrow skips). If you find a blocker (duplicate handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove it first with failing-tests-first evidence, then continue heavy work.

You MUST ship >=1 MATERIAL item this session. "Material" = spec-fidelity defect fix + tests, or a failing-tests-first regression lock for a real uncovered spec path, or material gated-pipeline/API/provenance guardrail hardening. NOT material: passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input.

MANDATORY HEAVY CAMPAIGN (execute in order, no skipping to easy tasks):
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 575 passed, 11 skipped).
2) Pick the highest-risk unproven spec path below and produce failing-tests-first evidence. Do not stop at audit prose.
   a) **2b MEDIUM (partially locked 2026-11-08):** liquidation worst-price + sequencing × `entry_next_bar` × cap-cut × rebound-short (slippage) locked (`tests/test_liquidation_cap_cut_rebound_entry_next_bar_max_notional_20261108.py`, 2 tests). Long same-bar stop-vs-target deterministic ordering (stop before target, liq before both) locked (`tests/test_long_same_bar_stop_target_sequencing_20261108.py`, 4 tests); short analog locked (`tests/test_rebound_short_attribution_and_risk_state_20261107.py`). Remaining: commission-min/edge rounding affecting penalty base/notional under `commission_min > 0` if spec requires per-trade minimum on liquidation fills — audit `_slippage_commission_per_share` (per-share, ignores `commission_min`) vs spec intent; failing-tests-first only on concrete gap. Also any spec-ambiguous path where intra-bar evidence would change outcome (hourly engine limitation — document, do not guess).
   b) **2g HIGH (partially locked 2026-11-08):** same-bar probe later-exit positive realized PnL/capacity-release must not leak into sibling admission (`tests/test_portfolio_same_bar_probe_positive_pnl_capacity_no_leak_20261108.py`) and loss/halt reconciliation locked (`test_portfolio_daily_loss_cross_bar_reconciliation_20261107.py`). Extend only for a concrete uncovered branch (e.g., profit-driven reservation/overlay edge under forced cap cuts with multi-symbol admissions and mixed rebound/liquidation terminals where post-probe notionals interact with pending realized exits across bars) — failing-tests-first.
   c) **2a/e:** ETH/coin bar alignment when series diverge non-trivially at rebound entry/start/final boundaries. Mid-exit short/missing ETH funding and final-exit aligned fallback locked; audit remaining rebound-start/short-ETH-series edge assumptions (rebound hedge entry uses `idx+1`/`idx` ref — verify against missing/short ETH at exact boundary) and lock gaps.
   d) **2c:** 8x spec safety stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`), stopped-buy never opens rebound short, `entry_next_bar` re-anchor — lock missing-candle-field comparison paths only if present in spec-compliant flow.
   e) **2d:** rebound short opens only after long +9% target; anchored to executed short entry (slippage/commission-aware); exits `-9%`/`48h`/`+40%`; funding on coin short + long ETH hedge on every exit — lock 48h/funding attribution under ETH-series divergence if uncovered.
   f) **2e:** ETH hedge every leg, vol-ratio `coin_vol/eth_vol` over 336h capped 3x, no look-ahead (`candles[:hedge_hist_end]`). Add engine-level lock only for a real branch gap.
   g) **2h:** target/stop anchors to executed entry; `entry_next_bar` re-anchor locked — no anchor drift for rebound/next-bar paths.
   h) Regression-only unless a concrete uncovered boundary is found: RSI(21)<20 next-hour open, deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); `avoid_downtrend` must not nullify spec-primary RSI trigger.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`. For every defect: failing test → minimal fix → pass. For verified-non-defect with insufficient lock: add regression lock with concrete expected values.
4) If 2a-h are evidence-backed clean, ship another material guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task message. No other handoff files. Do not stage/commit unrelated files.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long), hourly liquidation at worst price with correct sequencing/notional/timing/penalty, stopped buy never opens rebound short, 8x safety-stop ratio semantics, rebound `-9%/48h/+40%` anchored to executed short entry, ETH hedge every leg (336h vol ratio, cap 3x), RSI(21)<20 next open deepest-first, `$5M` 24h volume in spec-compliant gating, equal-share cuts old+new across 120% gross cap (cuts only), one position/coin, strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## HEAVY FOCUS CAMPAIGN (NEXT AGENT MUST EXECUTE; CANNOT AVOID)
1. **Gate:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3 -m pytest tests/ -q --tb=no` (expect 575/11).
2. **2b (if real gap):** `commission_min > 0` liquidation/exit fill accounting vs spec (engine `_slippage_commission_per_share` is per-share, ignores `commission_min`) — failing-tests-first only if spec requires it; do not invent behavior.
3. **2g (if real gap):** probe positive-exit/capacity no-leak under forced cap cuts + multi-symbol + mixed rebound/liquidation terminals with pending realized exits across bars — failing-tests-first.
4. **2a/e:** rebound hedge entry ETH alignment at `idx+1`/`idx` boundary when ETH series short/missing; mid-exit/final-exit partially locked.
5. **2c/d/h:** missing-candle-field stop comparison; rebound 48h/funding attribution under ETH divergence; anchor drift in untouched path — only if real gap found.
6. **If clean after evidence-backed 2–5:** ship a different material guardrail (pipeline/API/provenance/coverage) with failing-tests-first proof.
7. **Always:** final gate + update ONLY root `HANDOFF.md` with evidence and a new timestamped heavy task.

## SHIPPED (CONDENSED)
- **2026-11-08T12:19:08Z (MATERIAL regression lock / 2b long sequencing):** Added `tests/test_long_same_bar_stop_target_sequencing_20261108.py` (4 tests). Locks long-leg deterministic hourly-bar sequencing when liquidation is not triggered: stop checked before target on same-bar dual breach (`stopped`, exit at `stop_px`); sanity stop-only/target-only; and liquidation precedence when liq/stop/target all breach (`liquidated` at worst/low). Complements short same-bar stop-before-target locks and existing `test_long_liquidation_vs_stop_ordering.py`. New tests `4 passed`; related sequencing set `15 passed`; full gate `575 passed, 11 skipped`. No engine/spec logic changed.
- **2026-11-08T11:59:47Z (MATERIAL regression lock / 2b):** Added `tests/test_liquidation_cap_cut_rebound_entry_next_bar_max_notional_20261108.py` (2 tests). Locks liquidation worst-price + sequencing × `entry_next_bar` × cap-cut-adjusted shares/notional × rebound short (slippage). `max_live_coin_notional`/penalty/reservation reconcile. Full gate `571 passed, 11 skipped`.
- **2026-11-08T11:48:59Z (MATERIAL failing-tests-first bottleneck removal / 2b):** Fixed failing test expectation for `entry_next_bar`+slippage target re-anchor. Gate: `569 passed, 11 skipped`.
- **2026-11-08T10:45:47Z (MATERIAL regression-lock / 2g):** Added `tests/test_portfolio_same_bar_probe_positive_pnl_capacity_no_leak_20261108.py` (2 tests).
- **2026-11-08T10:32:04Z (handoff/bottleneck consolidation only, non-material):** refreshed root `HANDOFF.md`. No engine/spec logic changed.
- **2026-11-08T10:24:00Z (MATERIAL spec-fidelity defect fix + regression locks / 2a):** final-exit ETH aligned-fallback fixed. `tests/test_final_exit_short_eth_series_aligned_fallback_20261108.py` (4).
- **2026-11-08T10:15:30Z (MATERIAL regression-lock / 2a):** mid-exit short-ETH-series funding all exit paths locked (8).
- **2026-11-08T09:25:16Z (MATERIAL regression-lock / 2c,2e):** engine-level 8x spec safety stop `entry_next_bar` re-anchor + ETH hedge 336h window/cap locks (5).
- **2026-11-08T09:15:40Z (MATERIAL regression-lock / 2a):** missing-ETH-bar hedge funding all-exit-path coverage (4).
- **2026-11-08T09:00:31Z (MATERIAL spec-fidelity defect fix):** RSI trigger no-op removed at universe-gating boundary. Gate 541/11 (+6).
- **2026-11-08T07:13:10Z (MATERIAL spec-fidelity defect fix):** RSI<20 trigger not nullified by non-spec `avoid_downtrend`. Gate 535/11 (+5).
- **2026-11-08T07:01:32Z:** rebound-short 48h max-hold/funding inclusive semantics aligned. Gate 530/11.
- **2026-11-08T06:15:00Z:** `entry_next_bar` target/stop re-anchor to executed entry. Gate 529/11 (+2).
- **Earlier 2026-11-08/07:** Item 3 residual provenance/raw-ingress fail-closed hardening, synthetic-check/sha256 emission, structural validation fail-closed, final-bar exit occupancy release.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED PRIORITY)
- **2b (MEDIUM, partially locked):** cap-cut+entry_next_bar+rebound-short-liq+max_live_coin_notional/reservation interaction locked; long/short same-bar stop-vs-target deterministic ordering locked (liq→stop→target). Remaining: `commission_min > 0` fill accounting is per-share in `_slippage_commission_per_share` (ignores `commission_min` pass branch) — verify spec intent; failing-tests-first only if a real gap. Hourly-bar intra-path ambiguity is an engine limitation; do not claim sub-hour execution.
- **2g (HIGH, partially locked):** positive-PnL/capacity-release probe no-leak and daily-loss/halt cross-bar reconciliation locked. Extend only for a concrete uncovered cap-cut/reservation branch with mixed terminals/pending exits.
- **2a/e (MEDIUM):** remaining ETH/coin series divergence assumptions at rebound boundaries/start (mid-exit short/missing ETH and final-exit aligned fallback locked). Rebound hedge entry ref `idx+1`/`idx` at boundary with short/missing ETH series is an audit target.
- **2c/d/h (LOWER/MONITORED):** missing-candle-field stop comparison paths; rebound 48h/funding attribution under ETH divergence; anchor drift in any untouched path.
- **Environment constraint:** real 283d Hyperliquid candles unavailable here; expand universe only with archived verified data + full provenance. Canonical BTC/ETH placeholder remains fail-closed by design.

## CRITICAL CONTEXT
- **Spec truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py` (verified gate), `scripts/run_campaign.py` (fixture smoke), `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** each session ships >=1 material item with concrete evidence.
- **Spec is truth:** both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating in all spec-compliant paths, equal-share cuts old+new, stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
- **Single handoff:** only root `HANDOFF.md`. No parallel handoff/todo/progress files.
