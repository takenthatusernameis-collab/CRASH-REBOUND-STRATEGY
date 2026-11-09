# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-09T01:27:24Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-09T01:27:24Z)
- **Status: NO ACTIVE PROCESS/LOCK BOTTLENECKS.** No stale `.lock` files outside `.git/`. No parallel durable handoff/todo/progress files (`scripts/controller_progress.py` and `tests/test_controller_progress_accounting.py` are code/tests, not durable handoff). CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`).
- **Canonical data gate (fail-closed, unchanged):** real 283d Hyperliquid BTC/ETH data is **UNAVAILABLE/UNVERIFIED in this environment** (verified cache/archive are flat placeholders). Canonical gap reports/provenance/runners refuse. **Never fabricate numbers/artifacts. Never cite placeholder results as spec evidence.** `guard_canonical_write()` blocks temp-source/probe optimism from clobbering the canonical report as ready; `fetch_hyperliquid_candles.py` publishes to the canonical path only when verified-clean ready.
- **Session-open gate (verified 2026-11-09T01:27:24Z):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **621 passed** in 49.19s (0 skipped). Next session MUST re-run gate before coding.
- **Env bootstrap (if deps missing):** `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it FIRST** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`.

## REPO-NAME PRIORITY / SPEC CONTRACT (DRIVES ALL WORK)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Non-negotiables (never regress): hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (**cuts only, never top-ups**); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## SHIPPED THIS SESSION (2026-11-09T01:27:24Z) — MATERIAL, FAILING-TESTS-FIRST
- **D guardrail hardening (fail-closed): `synthetic_check.is_synthetic` must be explicitly `False` to treat data as verified-clean.** A manifest with `synthetic_check` present but `is_synthetic` missing/`None` is unverified (not proven clean); it must never be marked `ready_for_real_campaign`. Probes showed `build_gap_report` + `guard_canonical_write` previously treated `is_synthetic` missing/`None` as clean-ready (bypass risk).
  - `scripts/generate_candle_coverage_gap_report.py`: `build_gap_report` completeness now requires `synth_unverified == False` (`is_synthetic is not False` => unverified/hard block) and records unverified symbols in `actual_synthetic`; `guard_canonical_write` blocks any symbol where `synthetic_check` is absent, `is_synthetic is True`, or `is_synthetic is not False` (`synthetic_check_unverified`).
  - New failing-tests-first lock: `tests/test_gap_report_synthetic_check_must_be_explicit_20261109.py` (5 tests) — build+guard block when `is_synthetic` key missing / `is_synthetic=None`; explicit `is_synthetic=False` on a verified-clean non-temp manifest still passes through ready.
  - Evidence (2026-11-09T01:27:24Z): new test first run → **4 failed, 1 passed** (0.58s). After fix: **5 passed** (0.56s). Existing gap-report tests: **9 passed** (0.90s). Full gate: **621 passed** in 49.19s (0 skipped).

## SHIPPED (CONDENSED, CARRY-FORWARD)
- **2026-11-09T00:46:57Z:** regenerated canonical gap reports fail-closed from synthetic verified provenance; `guard_canonical_write()` prevents temp-source/probe optimism clobbering canonical ready=true; `fetch_hyperliquid_candles.py` publishes canonical only when verified-clean ready. `tests/test_candle_coverage_gap_report.py::test_canonical_gap_report_write_guarded_from_temp_archive`.
- **2026-11-08T23:42:38Z (B-rem8 lock):** rebound short liq/stop on exact 48th held bar win over 48h time-exit (`tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py`, 2). No src fix.
- **2026-11-08T22:10:00Z (B-rem7 lock):** rebound short -9% target on exact 48th held bar wins over 48h time-exit (`tests/test_rebound_short_target_wins_on_48th_bar_boundary_20261108.py`). No src fix.
- **2026-11-08T21:49:23Z (B-rem5), 20:52:27Z (B-rem3+B-rem4), 20:56:00Z (target/time-exit ETH+comm_min+entry_next_bar), 19:56:08Z (stop ETH+comm_min+entry_next_bar):** rebound-short sequencing/terminals locked under ETH hedge + commission_min + `entry_next_bar` where applicable. No src fixes.
- **2026-11-08T19:54:08Z (Priority A FULLY LOCKED):** `tests/test_portfolio_forced_cap_cut_old_plus_new_admission_20261108.py`. **2026-11-08T19:28:45Z:** cross-bar settlement/reentry + commission_min cap-cut. No src fixes.
- **2026-11-08T16:40:00Z/16:18:33Z:** rebound-short liquidation locks (ETH+comm_min+cap-cut+entry_next_bar). **2026-11-08T13:02:22Z (FIX/2b):** `src/backtest/engine.py::_slippage_commission_per_share` commission_min-aware; `tests/test_engine_commission_min_fill_accounting_20261108.py` (3).
- Prior locks/fixes preserved: long liq sequencing (4), liquidation/cap-cut/rebound `entry_next_bar` max-notional (2), `entry_next_bar` target re-anchor fix, portfolio same-bar positive-PnL capacity no-leak (2), final-exit ETH aligned-fallback (4), mid-exit short-ETH-series funding (8), 8x safety stop re-anchor + ETH 336h/cap (5), missing-ETH-bar hedge funding across exit paths, RSI not nullified by non-spec downtrend, rebound-short 48h inclusive semantics, **B-rem6** missing-ETH target lock.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Data integrity (BLOCKED by environment, fail-closed):** real 283d Hyperliquid candles unavailable/unverified here; verified cache/archive are flat placeholders. Canonical gap reports/provenance/runner refuse. Never fabricate.
- **Priority A — FULLY LOCKED.** Optional residual probe: rebound-short multi-leg occupancy settlement vs same-symbol block + sibling cuts — only with a real failing case.
- **Priority B — FULLY LOCKED (B-rem1–B-rem8):** rebound-short liq/stop/target/48h time-exit locked under ETH hedge + commission_min + `entry_next_bar` (cap-cut liq where covered); missing-ETH-bar locked for liq/stop/target/48h with funding+aligned fallback; same-bar liq>stop>target locked; 48th-bar boundary locked (target/time-exit precedence cases covered).
  - **B-rem2:** portfolio `apply_cap_cuts`/occupancy interaction during rebound transition in multi-symbol context — `TradeResult.max_live_coin_notional` authoritative (hedges excluded); portfolio reconciliation uses it. Lock only with concrete failing reservation/occupancy/cuts-only violation with numbers.
- **2b engine (narrowed):** commission_min parity + core long/rebound-short terminals mostly locked; only untouched pressure/fallback combinations remain.
- **2c/d/h (lower/monitored):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift — only if real gap found.
- **D guardrail — materially hardened this session** (explicit `is_synthetic=False` required). Further D work only if a concrete bypass is found with failing-tests-first proof.

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

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-09T01:27:24Z, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-09T01:27:24Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-09T01:27:24Z): NO active process/lock bottlenecks. Only root `HANDOFF.md` durable. No stale locks. CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (3.12, `PYTHONPATH=.`). Real 283d Hyperliquid BTC/ETH data remains UNAVAILABLE/UNVERIFIED here (fail-closed) — NEVER fabricate/cite placeholder results. `guard_canonical_write()` blocks temp-source/probe optimism and requires `synthetic_check.is_synthetic===false` for verified-clean readiness; `fetch_hyperliquid_candles.py` publishes canonical only when verified-clean ready.
Verified gate THIS CHECK (2026-11-09T01:27:24Z): `621 passed` in 49.19s (0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. If deps missing: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

CARRY-FORWARD EVIDENCE (locked — do not reopen without concrete failing defect):
- Priority A (2g/2b): FULLY LOCKED (forced 120% equal-share cut old+new + cross-bar settlement/reentry; portfolio reservation/occupancy releases verified).
- Priority B rebound-short terminals: B-rem1–B-rem8 LOCKED (liq/stop/target/48h time-exit under ETH hedge + commission_min + entry_next_bar where covered; missing-ETH-bar liq/stop/target/48h with funding+aligned fallback; same-bar liq>stop>target; 48th-bar boundaries). Evidence: `tests/test_rebound_short_liq_stop_on_48th_bar_boundary_20261108.py` et al.
- 2a/e CLOSED. Commission_min fill accounting locked (`src/backtest/engine.py::_slippage_commission_per_share`, 2026-11-08). 8x safety stop re-anchor + ETH 336h/cap locked. Long liq sequencing locked.
- D guardrail hardened (2026-11-09): canonical gap-report requires explicit `synthetic_check.is_synthetic===false`; temp-source/probe optimism cannot clobber ready=true. `tests/test_gap_report_synthetic_check_must_be_explicit_20261109.py`.

HEAVY-WORK GUARANTEE (future agents cannot avoid this): this session MUST ship >=1 MATERIAL item with concrete evidence. DO NOT end idle. DO NOT substitute passive re-verification, handoff-only edits, speculative refactors, or "blocked" without a concrete missing input. Material = spec-fidelity defect fix + failing-tests-first proof, OR a failing-tests-first regression lock for a real uncovered spec path with concrete expected values, OR material gated-pipeline/API/provenance guardrail hardening with proof.

YOU MUST SHIP >=1 MATERIAL ITEM THIS SESSION. NO EXCEPTIONS.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate (mandatory first): `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 621 passed). Do not proceed past a broken gate.
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A/B carry-forward above are locked — do not reopen without a concrete failing defect. Attack next (pick highest real uncovered risk):
   B-rem2 (only with concrete failing case): Portfolio `apply_cap_cuts`/occupancy interaction during rebound transition in multi-symbol context — `TradeResult.max_live_coin_notional` authoritative (hedges excluded); portfolio reconciliation uses it. Lock only if real reservation/occupancy/cuts-only violation with numbers.
   C — only with real gap after honest B-rem2 work: missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in untouched path; anchor drift in untouched path. Failing-tests-first only.
   D-bypass hunt (material): probe `fetch_hyperliquid_candles.py`/`src/data/provenance.py`/verified-runner ingestion for any path where `synthetic_check` missing/ambiguous, temp-source, or contradictory summary can be treated as verified/ready; add failing-tests-first lock/fix.
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign,generate_candle_coverage_gap_report,fetch_hyperliquid_candles}.py`, `src/data/provenance.py`.
4) If B-rem2/C/D-bypass yield no concrete gap after evidence-backed attempts, ship another MATERIAL guardrail with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Report exact count.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence, remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```
