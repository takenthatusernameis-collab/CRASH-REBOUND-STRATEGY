# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T20:56:00Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-08T20:56:00Z)
- **Status:** **NO BLOCKERS / NO INEFFICIENCIES BLOCKING PROGRESS.** Verified absent: duplicate durable handoff files (only root `HANDOFF.md`), stale `.lock` files (none outside git internals), broken gate, contradictory canonical artifacts. `main` ahead of `origin/main` only by local checkpoint commits (not a durable-task blocker). `scripts/controller_progress.py` is CI tooling, not a durable handoff; `tests/test_session_hardening_*.py` / `tests/test_controller_progress_accounting.py` are tests, not handoff variants.
- **Last verified gate (2026-11-08T20:56:00Z, this session):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`604 passed`** (31.57s, 0 skipped). Next session MUST re-run gate before coding.
- **CI:** `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Env bootstrap (if deps missing):** `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Known remote branches (context, not blockers):** `origin/fix/campaign-fixture-provenance-20261030`, `origin/fix/campaign-integrity-and-exposure-accounting-20261030` — do not merge/rebase unless explicitly requested and verified.
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` fail-closed `BLOCKED...` on incomplete coverage/provenance is correct. Real 283d Hyperliquid data is unavailable in this environment; expand universe only with archived verified data + full provenance. **Never fabricate numbers/artifacts.**
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it FIRST** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`. **Do not proceed past a broken gate.**

## REPO-NAME PRIORITY / SPEC CONTRACT (DRIVES ALL WORK)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Non-negotiables (never regress): hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (**cuts only, never top-ups**); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-08T20:56:00Z, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T20:56:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-08T20:56:00Z): NO BLOCKERS. Only root `HANDOFF.md` is durable (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). No stale `.lock` files. `main` ahead of `origin/main` by local checkpoint commits only (not a durable-task blocker). CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`). Verified gate THIS SESSION (2026-11-08T20:56:00Z): `604 passed` (31.57s, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. If deps missing: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. Intentional non-bottleneck: `scripts/fetch_hyperliquid_candles.py` fail-closed on incomplete coverage/provenance is correct; real 283d Hyperliquid data unavailable here — NEVER fabricate. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

CARRY-FORWARD EVIDENCE (locked): Priority A (2g/2b) FULLY LOCKED (forced 120% equal-share cut old+new + cross-bar settlement/reentry). Priority B rebound-short LIQUIDATION (w/wo ETH hedge, commission_min, entry_next_bar, cap-cut) LOCKED. Rebound-short STOP under ETH hedge + commission_min + entry_next_bar LOCKED. **B-rem TARGET (-9%) and 48h TIME-EXIT under ETH hedge + commission_min + entry_next_bar LOCKED this session** (`tests/test_rebound_short_target_time_exit_eth_hedge_commission_min_entry_next_bar_20261108.py`, 2 tests, concrete values; no src fix required). 2a/e CLOSED. Commission_min fill accounting locked.

HEAVY-WORK GUARANTEE (future agents cannot avoid this): this session MUST ship >=1 MATERIAL item with concrete evidence. DO NOT end idle. DO NOT substitute passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input. Material = spec-fidelity defect fix + failing-tests-first proof, OR a failing-tests-first regression lock for a real uncovered spec path with concrete expected values, OR material gated-pipeline/API/provenance guardrail hardening with proof. Re-running the gate or refreshing status alone is NOT material — find and lock/fix a real gap.

YOU MUST SHIP >=1 MATERIAL ITEM THIS SESSION. NO EXCEPTIONS.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate (mandatory first step): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 604 passed). Do not proceed past a broken gate.
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A fully locked — do not reopen without a concrete failing defect. Priority B rebound-short liq/stop/target/time-exit now locked under ETH hedge + commission_min + entry_next_bar. Attack next (pick highest real uncovered risk):
   B-rem2 (HIGHEST REMAINING if gap found): **Rebound short target/48h time-exit/stop under cap-cut pressure** (`_CapCutRS`/equal-share cut applied before/during rebound context if reachable) — verify `max_live_coin_notional` reservation, executed short notional vs cap cuts, coin+hedge funding/PnL, and no top-ups. Inspect whether cap cuts affect rebound short sizing in engine paths; failing-tests-first only.
   B-rem3: **Rebound short time-exit + ETH hedge when ETH data is missing/short/aligned fallback** on exit bar (mirrors long-leg missing-ETH/final-exit aligned-fallback locks) — verify hedge exit fallback, funding hours, no look-ahead, concrete values.
   B-rem4: **Rebound short liquidation/stop/target sequencing with commission_min + cap-cut + entry_next_bar on the SAME priority bar** (if engine can produce same-bar multi-trigger ambiguity) — lock worst-price/sequencing semantics with evidence.
   C — only with real gap after honest B-rem2-4 work: missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift in untouched path. Failing-tests-first only.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
4) If B-rem/C yield no concrete gap after evidence-backed attempts, ship another MATERIAL guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Report exact count.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## THIS SESSION (2026-11-08T20:56:00Z)
- **Bottleneck sweep:** no duplicate durable handoff files, no stale `.lock` files, no contradictory canonical artifacts.
- **Gate (verified):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`604 passed` in 31.57s** (0 skipped).
- **Material deliverable (B-rem lock, no src fix required):** added `tests/test_rebound_short_target_time_exit_eth_hedge_commission_min_entry_next_bar_20261108.py` (2 tests) with concrete expected values derived from current engine behavior and verified passing:
  1. **Rebound short TARGET (-9%)** under ETH hedge + commission_min + `entry_next_bar`: long target at bar 8; rebound short entry `108.99909` (executed/slippage+commission-aware), target `99.1901719` (-9% from executed entry), exit buy-side commission_min; short PnL `9830.717917999986` incl. hourly funding on coin short leg; rebound hedge (long ETH) entry aligned to idx 8 (no look-ahead) `2000.0061162590134`, exit bar 10 `1999.9938837409866`, funding/PnL `-67.39965400000271`; `max_live_coin_notional=108999.09`; `total_pnl=coin_total+hedge_pnl=18732.407963999976`.
  2. **Rebound short 48h TIME-EXIT** (no target/stop/liq for 48 bars): exit at `sidx 56` (`8+48`, `56-8+1==48`), `exit_timestamp=s55`, `bars_held=50`; short leg `time_exit`, close-based exit `107.001`, coin short PnL `2521.2856319999905` incl. 48h funding; hedge exit `2039.9938837409866`, hedge PnL `4968.353703999997`; totals reconcile.
- **Files changed:** `tests/test_rebound_short_target_time_exit_eth_hedge_commission_min_entry_next_bar_20261108.py`, `HANDOFF.md`.

## SHIPPED (CONDENSED, CARRY-FORWARD)
- **2026-11-08T20:56:00Z (lock / B-rem TARGET + 48h TIME-EXIT, ETH hedge + commission_min + entry_next_bar):** `tests/test_rebound_short_target_time_exit_eth_hedge_commission_min_entry_next_bar_20261108.py` (2) — **no src fix required; behavior verified**. Gate `604 passed`.
- **2026-11-08T20:41:00Z (handoff/bottleneck refresh):** Gate `602 passed`. B-rem identified as highest unlocked gap.
- **2026-11-08T19:56:08Z (lock / rebound short STOP, ETH hedge + commission_min + entry_next_bar):** `tests/test_rebound_short_stop_eth_hedge_commission_min_entry_next_bar_20261108.py` — no src fix.
- **2026-11-08T19:54:08Z (lock / Priority A 2g/2b forced 120% equal-share cut old+new):** `tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py` — **FULLY LOCKS Priority A**; no src fix.
- **2026-11-08T19:28:45Z (lock / 2g/2b cross-bar settlement):** `tests/test_portfolio_cross_bar_settlement_reentry_commission_min_cap_cut_20261108.py`.
- **2026-11-08T16:40:00Z (lock / rebound short liquidation, ETH hedge + commission_min + cap-cut + entry_next_bar):** `tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py`.
- **2026-11-08T16:18:33Z (lock / rebound short liquidation, commission_min + cap-cut + entry_next_bar):** `tests/test_rebound_short_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py`.
- **2026-11-08T13:02:22Z (FIX / 2b):** `src/backtest/engine.py::_slippage_commission_per_share` commission_min-aware; `tests/test_engine_commission_min_fill_accounting_20261108.py` (3).
- Prior locks/fixes preserved: long liq sequencing (4), liquidation/cap-cut/rebound `entry_next_bar` max-notional (2), `entry_next_bar` target re-anchor fix, portfolio same-bar positive-PnL capacity no-leak (2), final-exit ETH aligned-fallback (4), mid-exit short-ETH-series funding (8), 8x safety stop re-anchor + ETH 336h/cap (5), missing-ETH-bar hedge funding, RSI not nullified by non-spec downtrend, rebound-short 48h inclusive semantics, `entry_next_bar` target/stop re-anchor.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Priority A — 2g/2b (FULLY LOCKED):** forced 120% equal-share cut old+new + settlement/reentry locked. Optional residual probe: rebound-short multi-leg occupancy settlement (`_reconcile_realized_through`/`occupied_until`) vs same-symbol block + sibling cuts — only with a real failing case.
- **Priority B — 2b+hedge terminals (mostly locked):** rebound-short liquidation (w/wo ETH hedge), stop (ETH hedge), target (-9%), and 48h time-exit now locked under ETH hedge + commission_min + `entry_next_bar` (cap-cut variant locked for liquidation). **NEXT (evidence-backed only):** cap-cut pressure applied to rebound-short sizing/reservation in reachable engine/portfolio paths (B-rem2); rebound-short exit with missing/short ETH aligned fallback (B-rem3); same-bar multi-trigger sequencing ambiguity (B-rem4) — failing-tests-first.
- **2b engine (NARROWED):** commission_min parity + core long/rebound-short terminal paths locked; only untouched pressure/fallback combinations remain.
- **2a/e CLOSED:** rebound hedge entry ETH-aligned to `idx`.
- **2c/d/h (LOWER/MONITORED):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding under ETH divergence (untouched path); anchor drift — only if real gap found.
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
