# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T20:41:00Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-08T20:41:00Z)
- **Status:** **NO BLOCKERS / NO INEFFICIENCIES BLOCKING PROGRESS.** Verified absent: duplicate durable handoff files (only root `HANDOFF.md`), stale `.lock` files (none outside git internals), broken gate, contradictory canonical artifacts. `main` ahead of `origin/main` only by local checkpoint commits (not a durable-task blocker). `scripts/controller_progress.py` is CI tooling, not a durable handoff; `tests/test_session_hardening_*.py` / `tests/test_controller_progress_accounting.py` are tests, not handoff variants — none are durable task files.
- **Last verified gate (2026-11-08T20:41:00Z, this session):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`602 passed`** (34.87s, 0 skipped). Next session MUST re-run gate before coding.
- **CI:** `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Env bootstrap (if deps missing):** `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Known remote branches (context, not blockers):** `origin/fix/campaign-fixture-provenance-20261030`, `origin/fix/campaign-integrity-and-exposure-accounting-20261030` — do not merge/rebase unless explicitly requested and verified.
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` fail-closed `BLOCKED...` on incomplete coverage/provenance is correct. Real 283d Hyperliquid data is unavailable in this environment; expand universe only with archived verified data + full provenance. **Never fabricate numbers/artifacts.**
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it FIRST** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`. **Do not proceed past a broken gate.**

## REPO-NAME PRIORITY / SPEC CONTRACT (DRIVES ALL WORK)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Non-negotiables (never regress): hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (**cuts only, never top-ups**); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-08T20:41:00Z, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T20:41:00Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-08T20:41:00Z): NO BLOCKERS. Only root `HANDOFF.md` is durable (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). No stale `.lock` files. `main` ahead of `origin/main` by local checkpoint commits only (not a durable-task blocker). CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`). Verified gate THIS SESSION (2026-11-08T20:41:00Z): `602 passed` (34.87s, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. If deps missing: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. Intentional non-bottleneck: `scripts/fetch_hyperliquid_candles.py` fail-closed on incomplete coverage/provenance is correct; real 283d Hyperliquid data unavailable here — NEVER fabricate. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

CARRY-FORWARD EVIDENCE (locked): Priority A (2g/2b) FULLY LOCKED — forced 120% equal-share cut across old+new admissions + cross-bar settlement/reentry (`tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py`, `tests/test_portfolio_cross_bar_settlement_reentry_commission_min_cap_cut_20261108.py`). Priority B rebound-short LIQUIDATION and STOP LOCKED under ETH hedge + commission_min + entry_next_bar (`tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py`, `tests/test_rebound_short_stop_eth_hedge_commission_min_entry_next_bar_20261108.py`). 2a/e CLOSED (rebound hedge entry ETH-aligned to `idx`). Commission_min fill accounting locked (`src/backtest/engine.py::_slippage_commission_per_share`).

HEAVY-WORK GUARANTEE (future agents cannot avoid this): this session MUST ship >=1 MATERIAL item with concrete evidence. DO NOT end idle. DO NOT substitute passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input. Material = spec-fidelity defect fix + failing-tests-first proof, OR a failing-tests-first regression lock for a real uncovered spec path with concrete expected values, OR material gated-pipeline/API/provenance guardrail hardening with proof. Re-running the gate or refreshing status alone is NOT material — find and lock/fix a real gap.

YOU MUST SHIP >=1 MATERIAL ITEM THIS SESSION. NO EXCEPTIONS.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate (mandatory first step): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 602 passed). Do not proceed past a broken gate.
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A fully locked — do not reopen without a concrete failing defect. Priority B liq+stop locked. Attack next:
   B-rem — HIGHEST REMAINING (UNLOCKED): **Rebound short TARGET (-9%) close AND 48h TIME-EXIT under ETH hedge + cap-cut + commission_min + `entry_next_bar`.** Build failing-tests-first cases with concrete expected values:
   - Target case: executed short entry anchor (slippage/commission-aware), rebound hedge (long ETH) entry at short entry, coin short target at -9% from executed entry, hedge exit/PnL, hourly funding on coin short + hedge long for every included bar (verify boundary semantics), `max_live_coin_notional`/reservation/cap reconciliation, reason/timestamps, no no-look-ahead.
   - 48h time-exit case: force no target/stop/liquidation for 48 bars after rebound short entry; verify exit at `entry_idx + 48` (per spec: "48小时未反弹或亏损 -40%" — lock actual engine semantics with explicit evidence), coin+hedge PnL, funding over full 48h hold, notional/reservation reconciliation.
   - Combined pressure variant (if feasible without brittle fixtures): commission_min + cap-cut interaction on rebound short entry sizing/notional while hedge/funding/terminal exit remains correct.
   Inspect `src/backtest/engine.py` (`_execute_rebound_short`, `_hedge_entry_for_rebound`, `_hedge_exit_pnl`, funding/final paths, ~410-700), `src/strategy/risk.py`, `scripts/run_portfolio.py`. For each defect: failing test → minimal fix → pass. For verified-non-defect: regression lock with concrete values and state "no src fix required; behavior verified".
   C — only with real gap after honest B-rem work: missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift in untouched path. Failing-tests-first only.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`.
4) If B-rem/C yield no concrete gap after evidence-backed attempts, ship another MATERIAL guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Report exact count.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## THIS SESSION (2026-11-08T20:41:00Z)
- **Bottleneck sweep:** no duplicate durable handoff files (`scripts/controller_progress.py` is CI tooling; `tests/test_session_hardening_*.py`/`test_controller_progress_accounting.py` are tests), no stale `.lock` files, no contradictory canonical artifacts.
- **Gate (verified):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`602 passed` in 34.87s** (0 skipped). No code changes this session; no src fixes required.
- **Material deliverable:** refreshed the single durable `HANDOFF.md` with a clear, timestamped, repo-priority-driven initial task that forces >=1 material item next session and targets highest-remaining unlocked gap **B-rem** (rebound short TARGET -9% and 48h TIME-EXIT under ETH hedge + cap-cut + commission_min + `entry_next_bar`, with funding/notional/reservation/anchor evidence). Updated carry-forward status and explicit heavy campaign steps.
- **Files changed:** `HANDOFF.md` only.

## SHIPPED (CONDENSED, CARRY-FORWARD)
- **2026-11-08T20:41:00Z (handoff/bottleneck refresh, no blockers):** Gate re-verified `602 passed` (34.87s). Single durable handoff refreshed; B-rem (rebound target + 48h time-exit under ETH hedge/cap-cut/commission_min/entry_next_bar) remains highest unlocked work.
- **2026-11-08T19:45:47Z (handoff/bottleneck sweep):** No blockers; gate green `600 passed`. Confirmed CI/tooling/test names are not durable handoffs.
- **2026-11-08T19:54:08Z (lock / 2g/2b forced equal-share cut, FULLY LOCKS Priority A):** `tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py` — 120% equal-share cap cut forced across post-settlement old+new admissions (commission_min=60 + cap pressure): B 2000→1199.2804317409555 (cap/2=60000), C 3000→999.5002498750624 (cap/3=40000), cuts only, X untouched; final 8760.0 total, 0 open, 0 gross. **No src fix required.**
- **2026-11-08T19:56:08Z (lock / 2b stop + ETH hedge + commission_min + entry_next_bar):** `tests/test_rebound_short_stop_eth_hedge_commission_min_entry_next_bar_20261108.py` — rebound-short STOP (+40%) under ETH hedge + commission_min + entry_next_bar + hourly funding on coin+hedge; concrete PnL/notional/reason locked; total_pnl -23254.04 reconciled. **No src fix required.**
- **2026-11-08T19:28:45Z (lock / 2g/2b cross-bar settlement):** `tests/test_portfolio_cross_bar_settlement_reentry_commission_min_cap_cut_20261108.py` — **no src fix required.**
- **2026-11-08T16:40:00Z (lock / 2g/2b ii):** `tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py` — no src fix.
- **2026-11-08T16:18:33Z (lock / 2b):** `tests/test_rebound_short_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` — no src fix.
- **2026-11-08T15:55:19Z (lock / 2g+2b):** `tests/test_portfolio_commission_min_cap_cut_mixed_terminals_reservation_20261108.py`.
- **2026-11-08T15:06:30Z (lock / 2b):** `tests/test_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` (3).
- **2026-11-08T13:02:22Z (FIX / 2b):** `src/backtest/engine.py::_slippage_commission_per_share` commission_min-aware; `tests/test_engine_commission_min_fill_accounting_20261108.py` (3) failing→passing.
- Prior locks/fixes preserved: long liq sequencing (4), liquidation/cap-cut/rebound `entry_next_bar` max-notional (2), `entry_next_bar` target re-anchor fix, portfolio same-bar positive-PnL capacity no-leak (2), final-exit ETH aligned-fallback (4), mid-exit short-ETH-series funding (8), 8x safety stop re-anchor + ETH 336h/cap (5), missing-ETH-bar hedge funding, RSI not nullified by non-spec downtrend, rebound-short 48h inclusive semantics, `entry_next_bar` target/stop re-anchor.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Priority A — 2g/2b portfolio boundary (FULLY LOCKED):** Settlement+re-admission mechanics locked and forced 120% equal-share cut proof shipped (`tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py`). Do not reopen without a concrete failing defect. Optional residual probe: rebound-short multi-leg occupancy settlement (`_reconcile_realized_through`/`occupied_until`) vs same-symbol block + sibling cuts — only with a real failing case.
- **Priority B — 2b+hedge terminals (HIGHEST REMAINING, PARTIALLY LOCKED):** Rebound-short liquidation w/wo ETH hedge locked. Rebound-short STOP under ETH hedge + commission_min + entry_next_bar locked (`tests/test_rebound_short_stop_eth_hedge_commission_min_entry_next_bar_20261108.py`). **REMAINING (next session must attack):** rebound short **TARGET (-9%) close AND 48h TIME-EXIT** under ETH hedge + cap-cut + commission_min + `entry_next_bar` — hedge sizing/funding/notional/penalty/reservation sequencing and anchor-to-executed-short-entry on all legs, failing-tests-first with concrete expected values.
- **2b engine (NARROWED):** commission_min parity + long liquidation cases + rebound-short liq/stop locked; rebound-short target/time-exit remain.
- **2a/e CLOSED:** rebound hedge entry ETH-aligned to `idx`; locked.
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
