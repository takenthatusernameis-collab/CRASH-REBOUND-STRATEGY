# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T17:38:53Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK
- **Status (2026-11-08T17:38:53Z):** **No blockers found; bottlenecks removed/absent.** Verified: only root `HANDOFF.md` exists as durable handoff (no TODO/NEXT/PROGRESS/session handoff variants). No `.lock` files. Working tree clean except this HANDOFF refresh; `main` tracks `origin/main`. Known remote branches (context, not blockers): `origin/fix/campaign-fixture-provenance-20261030`, `origin/fix/campaign-integrity-and-exposure-accounting-20261030` — do not merge/rebase unless explicitly requested and verified. CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`). Last verified gate: **`599 passed`** (599 collected, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (re-verified 2026-11-08T17:38:53Z, 32.87s). Env note: `pytest`/`pyarrow` may not be pre-installed; `python3.12 -m pip install pytest pyarrow numpy pandas requests` (CI installs deps).
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it before other work** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`. Do not proceed past a broken gate.
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` fail-closed `BLOCKED...` on incomplete coverage/provenance is correct. Real 283d Hyperliquid data is unavailable in this environment; expand universe only with archived verified data + full provenance. Never fabricate numbers/artifacts.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware path); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T17:38:53Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact — not implemented.

Bottleneck check (2026-11-08T17:38:53Z): NO BLOCKERS. Only root `HANDOFF.md` is durable (no TODO/NEXT/PROGRESS/session variants); no `.lock` files; `main` tracks `origin/main`. CI: `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q`. Last verified gate: `599 passed` (599 collected, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (2026-11-08T17:38:53Z). Env may lack `pytest`/`pyarrow`: `python3.12 -m pip install pytest pyarrow numpy pandas requests` (CI installs deps). Intentional non-bottleneck: `scripts/fetch_hyperliquid_candles.py` fail-closed on incomplete coverage/provenance is correct; real 283d Hyperliquid data unavailable here — do not fabricate. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

You MUST ship >=1 MATERIAL item this session. Material = spec-fidelity defect fix + tests, OR a failing-tests-first regression lock for a real uncovered spec path, OR material gated-pipeline/API/provenance guardrail hardening with proof. NOT material: passive re-verification, handoff-only edits, speculative refactors, "blocked" without a concrete missing input, or claiming hourly-engine limitations as defects.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 599 passed).
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A before B before C:
   A) **Portfolio 2g/2b boundary (highest remaining):** cross-bar pending realized-exit settlement + SAME-BAR re-admission/occupancy boundary under `commission_min` + forced 120% equal-share cap-cut + `entry_next_bar`/mixed terminals. Construct a case where a realized exit settles into capacity and another symbol is (re-)admitted/probed in the same bar, or where reservation/probe state could leak/mis-admit/mis-size after pending realized-exit reconciliation. Probe `src/backtest/engine.py` portfolio loop (pending realized, reserved notionals, probe/apply admission, occupancy, gross exposure). Lock with concrete expected values: shares/notionals/PnL/timestamps/exit reasons, `final_open_positions`, reserved/open notionals, gross exposure, realized PnL reconciliation.
   B) **Rebound hedge + cap-cut + commission_min + entry_next_bar (ETH hedge enabled, uncovered terminal):** existing locks cover liquidation (no hedge / with ETH hedge). Find/lock a concrete uncovered rebound-short terminal path under ETH hedge enabled with cap-cut+commission_min+`entry_next_bar` — e.g. rebound stop, rebound +40% target, rebound 48h time-exit, or a real hedge sizing/funding/notional/penalty sequencing edge — ONLY with a real failing test or a proven uncovered branch and concrete expected values. Do not duplicate locked liquidation cases.
   C) **2c/d/h (only with real gap):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in an untouched path; anchor drift in an untouched path. Failing-tests-first only.
   (2a/e CLOSED — rebound hedge entry ETH-aligned to `idx`, locked by `tests/test_rebound_hedge_entry_eth_alignment_20261108.py` + mid/final/missing-ETH locks. Do not reopen without concrete failing defect.)
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`. For every defect: failing test → minimal fix → pass. For a verified-non-defect with insufficient lock: add a regression lock with concrete expected values (state "no src fix required; behavior verified" with evidence).
4) If A/B/C yield no concrete failing/uncovered gap after honest evidence-backed attempts, ship another MATERIAL guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence (failing→passing or lock proof), remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## HEAVY FOCUS CAMPAIGN (NEXT AGENT MUST EXECUTE; CANNOT AVOID)
1. **Gate:** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 599 passed; last verified 2026-11-08T17:38:53Z — install deps first if missing).
2. **Priority A (2g/2b):** portfolio cross-bar pending realized-exit settlement + same-bar re-admission/occupancy boundary under commission_min + forced 120% equal-share cap-cut (+ entry_next_bar/mixed terminals). Failing-tests-first, concrete expected values, no capacity/leak/mis-admission regressions.
3. **Priority B (2b+hedge):** uncovered rebound-short terminal under ETH hedge enabled + cap-cut + commission_min + `entry_next_bar` (stop/target/48h-time or proven sizing/funding/notional/penalty edge), not duplicating locked liquidation cases. Failing-tests-first.
4. **Priority C (2c/d/h):** missing-candle-field stop comparison, rebound 48h/funding attribution under ETH divergence (untouched path), anchor drift — only if real gap found.
5. **2a/e CLOSED:** do not reopen without failing-tests-first concrete defect.
6. **If clean after evidence-backed A–C:** ship a different MATERIAL guardrail (pipeline/API/provenance/coverage) with failing-tests-first proof. No idle/passive session.
7. **Always:** final gate + update ONLY root `HANDOFF.md` with evidence and a new timestamped heavy task.

## SHIPPED (CONDENSED)
- **2026-11-08T16:40:00Z (MATERIAL regression lock / 2g/2b ii, ETH hedge enabled):** Added `tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py` (1). Locks rebound-short liquidation with `enable_eth_hedge=True` under commission_min+cap-cut+`entry_next_bar`: rebound hedge entry aligned to `idx` (no look-ahead), commission_min on fills, executed-short notional penalty base, `max_live_coin_notional` reservation, hedge funding/PnL sequencing, coin+hedge attribution. No src fix required; concrete values locked. Gate `599 passed`.
- **2026-11-08T16:18:33Z (MATERIAL regression lock / 2b engine cross-leg, rebound-short liquidation):** Added `tests/test_rebound_short_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` (1). Locks cap-cut+commission_min+`entry_next_bar` long→target→rebound-short liquidation (penalty base `short_entry*shares`, max_live_coin_notional). No src fix required. Gate `599 passed`.
- **2026-11-08T15:55:19Z (MATERIAL regression lock / 2g+2b cross-path, portfolio):** Added `tests/test_portfolio_commission_min_cap_cut_mixed_terminals_reservation_20261108.py` (1). Same-bar multi-symbol admissions under forced cap cuts with commission_min+mixed terminals across bars; reservation/pending realized exits; concrete `total_pnl=6937.131744186048`, final state zeroed/reconciled. Gate `597 passed` at ship time.
- **2026-11-08T15:06:30Z (MATERIAL regression lock / 2b narrowed):** Added `tests/test_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` (3). Long liquidation worst-price/sequencing under `entry_next_bar`+cap-cut+`commission_min`. Gate `596 passed`.
- **2026-11-08T15:03:59Z (handoff refresh):** `578 passed, 11 skipped`.
- **2026-11-08T14:23:15Z (handoff refresh):** `578 passed, 11 skipped`.
- **2026-11-08T13:02:22Z (MATERIAL spec-fidelity/fee-accounting defect fix / 2b):** `src/backtest/engine.py::_slippage_commission_per_share` made `commission_min`-aware (`max(commission_per_share, commission_min/shares)` when `shares>0`). Applied across fill sites. `tests/test_engine_commission_min_fill_accounting_20261108.py` (3) failing→passing. Gate `578 passed, 11 skipped`.
- **2026-11-08T12:19:08Z:** long liq→stop→target sequencing lock (4). `575 passed, 11 skipped`.
- **2026-11-08T11:59:47Z:** liquidation/cap-cut/rebound `entry_next_bar` max-notional lock (2). `571 passed, 11 skipped`.
- **2026-11-08T11:48:59Z:** failing `entry_next_bar`+slippage target re-anchor fix. `569 passed, 11 skipped`.
- **2026-11-08T10:45:47Z:** portfolio same-bar probe positive-PnL capacity no-leak lock (2).
- **2026-11-08T10:24:00Z:** final-exit ETH aligned-fallback fixed/locked (4).
- **2026-11-08T10:15:30Z:** mid-exit short-ETH-series funding all exit paths locked (8).
- **2026-11-08T09:25:16Z:** 8x spec safety stop `entry_next_bar` re-anchor + ETH hedge 336h window/cap locks (5).
- **2026-11-08T09:15:40Z:** missing-ETH-bar hedge funding all-exit-path coverage (4).
- **2026-11-08T09:00:31Z:** RSI trigger no-op removed at universe-gating boundary (+6).
- **2026-11-08T07:13:10Z:** RSI<20 trigger not nullified by non-spec `avoid_downtrend` (+5).
- **2026-11-08T07:01:32Z / 06:15:00Z:** rebound-short 48h max-hold/funding inclusive semantics; `entry_next_bar` target/stop re-anchor to executed entry.
- **Earlier 2026-11-08/07:** provenance/raw-ingress fail-closed hardening, synthetic-check/sha256 emission, structural validation fail-closed, final-bar exit occupancy release.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED PRIORITY)
- **Priority A — 2g/2b portfolio boundary (UNPROVEN):** cross-bar pending realized-exit settlement + same-bar re-admission/occupancy boundary under `commission_min` + forced 120% equal-share cap-cut. Existing locks cover mixed terminals across bars and positive-PnL capacity-release probe, but a targeted same-bar post-settlement re-admission/probe/reservation reconciliation case may still expose a leak or mis-admission. Evidence required: failing test or concrete uncovered branch + expected values.
- **Priority B — 2b+hedge uncovered terminal (PARTIALLY LOCKED):** rebound-short liquidation with/without ETH hedge under cap-cut+commission_min+`entry_next_bar` is locked. Remaining risk: rebound short **stop / +40% target / 48h time-exit** under ETH hedge enabled + cap-cut + commission_min + `entry_next_bar`, where hedge sizing/funding/notional/penalty/reservation sequencing could diverge. Lock only with failing-tests-first + concrete values.
- **2b engine (NARROWED):** `commission_min` parity locked; long liquidation+cap-cut+commission_min+`entry_next_bar` locked. Only concrete uncovered rebound-short/hedge interactions remain.
- **2a/e CLOSED:** rebound hedge entry ETH-aligned to `idx` (`engine.py`), locked by `tests/test_rebound_hedge_entry_eth_alignment_20261108.py` plus mid/final/missing-ETH locks. Do not reopen without failing-tests-first concrete defect.
- **2c/d/h (LOWER/MONITORED):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence (untouched path); anchor drift — only if real gap found.
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
