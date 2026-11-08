# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T21:50:30Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-08T21:50:30Z)
- **Status: NO BLOCKERS / NO INEFFICIENCIES BLOCKING PROGRESS.** Verified: only root `HANDOFF.md` exists as durable handoff (`scripts/controller_progress.py` is CI tooling, not a handoff). No stale `.lock` files outside `.git/`. No contradictory canonical artifacts. Working tree clean at check.
- **Gate (verified 2026-11-08T21:50:30Z):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`609 passed` in 31.41s** (0 skipped). Next session MUST re-run gate before coding. Do not proceed past a broken gate.
- **CI:** `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Env bootstrap (if deps missing):** `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Known remote branches (context, not blockers):** `origin/fix/campaign-fixture-provenance-20261030`, `origin/fix/campaign-integrity-and-exposure-accounting-20261030` — do not merge/rebase unless explicitly requested and verified.
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` fail-closed `BLOCKED...` on incomplete coverage/provenance is correct. Real 283d Hyperliquid data is unavailable in this environment; expand universe only with archived verified data + full provenance. **Never fabricate numbers/artifacts.**
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it FIRST** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`.

## REPO-NAME PRIORITY / SPEC CONTRACT (DRIVES ALL WORK)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Non-negotiables (never regress): hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (**cuts only, never top-ups**); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-08T21:50:30Z, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T21:50:30Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-08T21:50:30Z): NO BLOCKERS. Only root `HANDOFF.md` is durable (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). No stale `.lock` files. CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`). Verified gate THIS CHECK (2026-11-08T21:50:30Z): `609 passed` (31.41s, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. If deps missing: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. Intentional non-bottleneck: `scripts/fetch_hyperliquid_candles.py` fail-closed on incomplete coverage/provenance is correct; real 283d Hyperliquid data unavailable here — NEVER fabricate. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

CARRY-FORWARD EVIDENCE (locked — do not reopen without concrete failing defect):
- Priority A (2g/2b): FULLY LOCKED (forced 120% equal-share cut old+new + cross-bar settlement/reentry; portfolio reservation/occupancy releases verified in locked tests). Tests: test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py, test_portfolio_cross_bar_settlement_reentry_commission_min_cap_cut_20261108.py, etc.
- Priority B rebound-short terminals: LIQUIDATION (w/wo ETH hedge, commission_min, entry_next_bar, cap-cut), STOP (+40%, ETH hedge + commission_min + entry_next_bar), STOP with missing ETH bar (close/open absent, bar present, aligned fallback+funding), TARGET (-9%), 48h TIME-EXIT under ETH hedge + commission_min + entry_next_bar LOCKED. Missing-ETH-bar (close/open absent) on liquidation/stop/48h time-exit with funding+aligned fallback LOCKED. Same-bar liq>stop>target sequencing locked (worst-price liq wins; stop wins over target when liq off).
- 2a/e CLOSED (rebound hedge entry ETH-aligned to idx). Commission_min fill accounting locked. 8x safety stop re-anchor + ETH 336h/cap locked. Long liq sequencing locked.

HEAVY-WORK GUARANTEE (future agents cannot avoid this): this session MUST ship >=1 MATERIAL item with concrete evidence. DO NOT end idle. DO NOT substitute passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input. Material = spec-fidelity defect fix + failing-tests-first proof, OR a failing-tests-first regression lock for a real uncovered spec path with concrete expected values, OR material gated-pipeline/API/provenance guardrail hardening with proof. Re-running the gate or refreshing status alone is NOT material — find and lock/fix a real gap.

YOU MUST SHIP >=1 MATERIAL ITEM THIS SESSION. NO EXCEPTIONS.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate (mandatory first): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 609 passed). Do not proceed past a broken gate.
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A/B carry-forward above are locked — do not reopen without a concrete failing defect. Attack next (pick highest real uncovered risk):
   B-rem6 (HIGHEST if gap found): Rebound short TARGET (-9%) with missing ETH bar present but close/open absent under ETH hedge + commission_min + entry_next_bar (liq/stop/time-exit missing-bar covered; target parity may be gap — verify against existing missing-ETH-path tests e.g. test_missing_eth_hedge_funding_all_exit_paths_20261108.py / test_hedge_funding_fallback_on_missing_eth_exit.py before coding). Lock concrete expected values if uncovered.
   B-rem7: Rebound short 48h time-exit boundary/ordering — 48h counted as `(sidx - short_start_idx + 1) >= short_bars_max`; verify interaction with same-bar liq>stop>target (already locked) in any uncovered boundary case. Only lock if uncovered.
   B-rem2 (only with concrete failing case): Portfolio `apply_cap_cuts`/occupancy interaction during rebound transition in multi-symbol context — `TradeResult.max_live_coin_notional` is authoritative coin-positions cap (hedges excluded); portfolio reconciliation uses it (`scripts/run_portfolio.py`). Lock only if you find reservation/occupancy/cuts-only violation with numbers.
   C — only with real gap after honest B-rem work: missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift in untouched path. Failing-tests-first only.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
4) If B-rem/C yield no concrete gap after evidence-backed attempts, ship another MATERIAL guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Report exact count.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## SHIPPED (CONDENSED, CARRY-FORWARD)
- **2026-11-08T21:49:23Z (lock / B-rem5):** `tests/test_rebound_short_stop_missing_eth_commission_min_entry_next_bar_20261108.py` (1) — rebound short STOP with missing ETH close/open at exit bar (bar present), aligned fallback + funding on coin short & hedge long, +40% stop anchored to executed short entry, `commission_min`, `entry_next_bar`. No src fix. Gate `609 passed`.
- **2026-11-08T20:52:27Z (lock / B-rem3+B-rem4):** `tests/test_rebound_short_sequencing_missing_eth_commission_min_entry_next_bar_20261108.py` (4) — rebound-short liquidation & 48h time-exit missing-ETH-bar (close/open absent) with funding+aligned fallback; same-bar liq>stop>target sequencing. No src fix.
- **2026-11-08T20:56:00Z (lock / B-rem TARGET + 48h TIME-EXIT):** `tests/test_rebound_short_target_time_exit_eth_hedge_commission_min_entry_next_bar_20261108.py` (2). No src fix.
- **2026-11-08T19:56:08Z (lock / rebound short STOP, ETH hedge + commission_min + entry_next_bar):** `tests/test_rebound_short_stop_eth_hedge_commission_min_entry_next_bar_20261108.py`. No src fix.
- **2026-11-08T19:54:08Z (lock / Priority A 2g/2b):** `tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py` — **FULLY LOCKS Priority A**. No src fix.
- **2026-11-08T19:28:45Z (lock / 2g/2b cross-bar settlement):** `tests/test_portfolio_cross_bar_settlement_reentry_commission_min_cap_cut_20261108.py`.
- **2026-11-08T16:40:00Z (lock / rebound short liquidation, ETH hedge + commission_min + cap-cut + entry_next_bar):** `tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py`.
- **2026-11-08T16:18:33Z (lock / rebound short liquidation, commission_min + cap-cut + entry_next_bar):** `tests/test_rebound_short_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py`.
- **2026-11-08T13:02:22Z (FIX / 2b):** `src/backtest/engine.py::_slippage_commission_per_share` commission_min-aware; `tests/test_engine_commission_min_fill_accounting_20261108.py` (3).
- Prior locks/fixes preserved: long liq sequencing (4), liquidation/cap-cut/rebound `entry_next_bar` max-notional (2), `entry_next_bar` target re-anchor fix, portfolio same-bar positive-PnL capacity no-leak (2), final-exit ETH aligned-fallback (4, incl rebound final-exit short ETH series), mid-exit short-ETH-series funding (8, incl rebound exits), 8x safety stop re-anchor + ETH 336h/cap (5), missing-ETH-bar hedge funding across exit paths (see locked tests), RSI not nullified by non-spec downtrend, rebound-short 48h inclusive semantics, `entry_next_bar` target/stop re-anchor.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Priority A — FULLY LOCKED.** Optional residual probe: rebound-short multi-leg occupancy settlement vs same-symbol block + sibling cuts — only with a real failing case.
- **Priority B — narrowed:** rebound-short liq/stop/target/48h time-exit locked under ETH hedge + commission_min + `entry_next_bar` (cap-cut variant locked for liq). Missing-ETH-bar (close/open absent, bar present) locked for liq/stop/48h time-exit with funding+aligned fallback. Same-bar liq>stop>target sequencing locked.
  - **B-rem6 (highest next probe):** rebound-short TARGET (-9%) with missing ETH bar present/close-open absent (liq/stop/time-exit missing-bar done — verify target parity gap before coding).
  - **B-rem7:** 48h time-exit boundary/ordering edge only if uncovered (`(sidx - short_start_idx + 1) >= short_bars_max`; liq>stop>target precedence locked).
  - **B-rem2:** portfolio occupancy/cap-cut during rebound transition — only with concrete failing case (inspection found none).
- **2b engine (narrowed):** commission_min parity + core long/rebound-short terminals mostly locked; only untouched pressure/fallback combinations remain.
- **2c/d/h (lower/monitored):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding under ETH divergence in untouched path; anchor drift — only if real gap found.
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
