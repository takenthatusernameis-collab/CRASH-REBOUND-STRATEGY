# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-09T02:36:39Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-09T02:36:39Z)
- **Status: NO ACTIVE PROCESS/LOCK BOTTLENECKS.** No stale `.lock` files outside `.git/`. No parallel durable handoff/todo/progress files (`scripts/controller_progress.py` and `tests/test_controller_progress_accounting.py` are code/tests, not durable handoff). CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`).
- **Canonical data gate (fail-closed, unchanged):** real 283d Hyperliquid BTC/ETH data is **UNAVAILABLE/UNVERIFIED in this environment** (verified cache/archive are flat placeholders). Canonical gap reports/provenance/runners refuse. **Never fabricate numbers/artifacts. Never cite placeholder results as spec evidence.** `guard_canonical_write()` blocks temp-source/probe optimism from clobbering the canonical report as ready; `fetch_hyperliquid_candles.py` publishes to the canonical path only when verified-clean ready.
- **Session-open gate (verified 2026-11-09T02:36:39Z):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **628 passed** in 54.47s (0 skipped). Next session MUST re-run gate before coding.
- **Env bootstrap (if deps missing):** `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it FIRST** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`.

## SHIPPED THIS SESSION (2026-11-09T02:36:39Z) — B-rem2 LOCKED + PORTFOLIO RESERVATION PROPAGATION FIX
- **B-rem2 test fixture fixed + passing:** `tests/test_portfolio_same_bar_rebound_short_admission_reservation_20261109.py` had `signal_index=0` but the portfolio scanner starts at `warmup=5` (`crash_lookback=5`), so the signal never fired ("A did not trade"). Fixed `signal_index=25` and fake generator trigger at `idx==25`. Both tests pass: same-bar multi-admission where A's rebound short opens at +9% target correctly reserves `max_live_coin_notional` (10900) so sibling B is cut (not uncut 15 shares).
- **Portfolio reservation propagation fix (material):** `scripts/run_portfolio.py:275` positional mapping `len(post_notionals) == len(existing_syms) + 1` failed when a rebound short opens alongside existing positions — the rebound short adds a second `open_position_notionals` entry for the same symbol (n+2 entries), so the `+1` check was False and existing positions were NOT updated to their post-cut notional. Changed to `>=` and reserved the new symbol at `executed_notional` (`max_live_coin_notional`) instead of `post_notionals[-1]`. This ensures existing positions get post-cut notionals propagated into the reservation overlay when a probe transitions to rebound short on the same decision bar. Added `test_existing_position_cut_when_rebound_short_opens_same_bar` (X at 10000, A triggers cap cuts + rebound short, B cut correctly).
- Gate: **628 passed** in 54.47s (0 skipped), up from 626.

## REPO-NAME PRIORITY / SPEC CONTRACT (DRIVES ALL WORK)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Non-negotiables (never regress): hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (**cuts only, never top-ups**); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## SHIPPED (CONDENSED, CARRY-FORWARD)
- **2026-11-09T02:36:39Z (B-rem2 lock + reservation fix, THIS SESSION):** B-rem2 test fixture fixed (signal_index=25), portfolio reservation propagation fix (`>=` operator, executed_notional), new test `test_existing_position_cut_when_rebound_short_opens_same_bar`. Gate 628 passed.
- **2026-11-09T01:45:00Z (D-bypass hunt):** `guard_canonical_write` hardened to scan `input_archives` (plural) as well as `input_archive` (singular) for temp-source provenance. `tests/test_guard_canonical_write_input_archives_temp_bypass_20261109.py` (5).
- **2026-11-09T01:27:24Z (D guardrail):** `synthetic_check.is_synthetic` must be explicitly `False` for verified-clean readiness. `tests/test_gap_report_synthetic_check_must_be_explicit_20261109.py` (5).
- **2026-11-09T00:46:57Z:** canonical gap reports fail-closed; `guard_canonical_write()` prevents temp-source/probe optimism clobbering ready=true.
- **2026-11-08T23:42:38Z (B-rem8 lock):** rebound short liq/stop on exact 48th held bar win over 48h time-exit (2 tests).
- **2026-11-08T22:10:00Z (B-rem7 lock):** rebound short -9% target on exact 48th held bar wins over 48h time-exit.
- **2026-11-08T19:54:08Z (Priority A FULLY LOCKED):** forced 120% equal-share cut old+new + cross-bar settlement/reentry.
- **2026-11-08T13:02:22Z (FIX/2b):** `src/backtest/engine.py::_slippage_commission_per_share` commission_min-aware (3 tests).
- Prior locks preserved: long liq sequencing, liquidation/cap-cut/rebound entry_next_bar, entry_next_bar target re-anchor, same-bar positive-PnL capacity no-leak, final-exit ETH aligned-fallback, missing-ETH hedge funding, 8x safety stop re-anchor + ETH 336h/cap, missing-ETH-bar hedge funding, RSI not nullified by downtrend filter, rebound-short 48h inclusive semantics, B-rem6 missing-ETH target lock.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Data integrity (BLOCKED by environment, fail-closed):** real 283d Hyperliquid candles unavailable/unverified here; verified cache/archive are flat placeholders. Canonical gap reports/provenance/runner refuse. Never fabricate.
- **Priority A — FULLY LOCKED.** Optional residual probe only with a real failing case.
- **Priority B — FULLY LOCKED (B-rem1–B-rem8 incl. B-rem2):** rebound-short liq/stop/target/48h time-exit locked under ETH hedge + commission_min + entry_next_bar; missing-ETH-bar locked; same-bar liq>stop>target locked; 48th-bar boundaries locked; same-bar multi-admission with rebound-short max_live reservation locked. Do not reopen without a concrete failing defect.
- **2b engine (narrowed):** commission_min parity locked; only untouched pressure/fallback combinations remain. Probe: liquidation+rebound+cap-cut+commission_min combinations not yet covered by failing-tests-first evidence.
- **2c/d/h (lower/monitored):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift — only if real gap found.
- **D guardrail — hardened.** Residual surfaces to probe next: `report.probe_evidence.source` vs `manifest.source` divergence; `archive_scan`/`verified_archives_found` path in `build_gap_report` (already fail-closed — scanned files never become verified). Add failing-tests-first lock/fix for any real escape.

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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-09T02:36:39Z, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-09T02:36:39Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-09T02:36:39Z): NO active process/lock bottlenecks. Only root `HANDOFF.md` durable. No stale locks outside `.git/`. CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`). Real 283d Hyperliquid BTC/ETH data remains UNAVAILABLE/UNVERIFIED here (fail-closed) — NEVER fabricate/cite placeholder results. `guard_canonical_write()` blocks temp-source/probe optimism and requires `synthetic_check.is_synthetic===false` for verified-clean readiness; `fetch_hyperliquid_candles.py` publishes canonical only when verified-clean ready.
Verified gate THIS CHECK (2026-11-09T02:36:39Z): `628 passed` in 54.47s (0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. If deps missing: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

CARRY-FORWARD EVIDENCE (locked — do not reopen without concrete failing defect):
- Priority A (2g/2b): FULLY LOCKED (forced 120% equal-share cut old+new + cross-bar settlement/reentry; portfolio reservation/occupancy releases verified).
- Priority B rebound-short terminals: B-rem1–B-rem8 LOCKED including B-rem2 (same-bar multi-admission with rebound-short max_live_coin_notional reservation; portfolio reservation propagation fix in `scripts/run_portfolio.py:275` — `>=` operator, `executed_notional`). Evidence: `tests/test_portfolio_same_bar_rebound_short_admission_reservation_20261109.py` (2 tests), `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` et al.
- 2a/e CLOSED. Commission_min fill accounting locked (`src/backtest/engine.py::_slippage_commission_per_share`, 2026-11-08). 8x safety stop re-anchor + ETH 336h/cap locked. Long liq sequencing locked.
- D guardrail hardened: canonical gap-report requires explicit `synthetic_check.is_synthetic===false`; temp-source/probe optimism cannot clobber ready=true; `guard_canonical_write` scans both `input_archive` and `input_archives` (plural). `tests/test_guard_canonical_write_input_archives_temp_bypass_20261109.py`, `tests/test_gap_report_synthetic_check_must_be_explicit_20261109.py`.

HEAVY-WORK GUARANTEE (future agents cannot avoid this): this session MUST ship >=1 MATERIAL item with concrete evidence. DO NOT end idle. DO NOT substitute passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input. Material = spec-fidelity defect fix + failing-tests-first proof, OR a failing-tests-first regression lock for a real uncovered spec path with concrete expected values, OR material gated-pipeline/API/provenance guardrail hardening with proof.

YOU MUST SHIP >=1 MATERIAL ITEM THIS SESSION. NO EXCEPTIONS.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate (mandatory first): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 628 passed). Do not proceed past a broken gate.
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A/B carry-forward above are locked — do not reopen without a concrete failing defect. Attack next (pick highest real uncovered risk):
   2b engine untouched combinations (CONCRETE FAILING CASE REQUIRED): liquidation + rebound short + cap-cut + commission_min combinations not yet covered by failing-tests-first evidence. Key files: `src/backtest/engine.py` (liquidation lines 126-150, rebound short lines 411-605, commission_min lines 98-103), `scripts/run_portfolio.py` (reservation overlay lines 250-282). Write a failing test demonstrating a concrete violation (e.g., commission_min parity on rebound-short liquidation exit, or cap-cut miscalculation when liquidation and rebound short interact on the same bar) with concrete expected values. If no concrete failing case exists after evidence-backed attempts, ship another MATERIAL guardrail with failing-tests-first proof — do not end session idle.
   D-bypass hunt (material): probe `fetch_hyperliquid_candles.py`/`src/data/provenance.py`/verified-runner ingestion for any path where `synthetic_check` missing/ambiguous, temp-source, or contradictory summary can be treated as verified/ready; especially residual surfaces `report.probe_evidence.source` vs `manifest.source` divergence and the `archive_scan`/`verified_archives_found` path in `build_gap_report` (already fail-closed — scanned files never become verified). Add failing-tests-first lock/fix for any real escape.
   C — only with real gap after honest 2b/D work: missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift in untouched path. Failing-tests-first only.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign,generate_candle_coverage_gap_report,fetch_hyperliquid_candles}.py`, `src/data/provenance.py`.
4) If 2b/D-bypass/C yield no concrete gap after evidence-backed attempts, ship another MATERIAL guardrail with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Report exact count.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```
