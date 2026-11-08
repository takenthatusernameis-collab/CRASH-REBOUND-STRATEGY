# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-08T17:58:25Z
**Single canonical handoff:** ONLY this root `HANDOFF.md` is durable. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/session variants). `__pycache__`/compiled artifacts are not evidence.

## BOTTLENECK CHECK (2026-11-08T17:58:25Z)
- **Status:** **No blockers found; bottlenecks removed/absent.** Verified: only root `HANDOFF.md` exists as durable handoff; no `.lock` files; working tree clean before this refresh; `main` tracks `origin/main`.
- **Gate (re-verified 2026-11-08T17:58:25Z):** `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` → **`599 passed`** (599 collected, 0 skipped, 32.04s).
- **CI:** `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q` (Python 3.12, `PYTHONPATH=.`).
- **Env note:** `pytest`/`pyarrow`/`numpy`/`pandas`/`requests` may not be pre-installed: `python3.12 -m pip install pytest pyarrow numpy pandas requests`.
- **Known remote branches (context, not blockers):** `origin/fix/campaign-fixture-provenance-20261030`, `origin/fix/campaign-integrity-and-exposure-accounting-20261030` — do not merge/rebase unless explicitly requested and verified.
- **Intentional non-bottleneck (do NOT "fix" by relaxing):** `scripts/fetch_hyperliquid_candles.py` fail-closed `BLOCKED...` on incomplete coverage/provenance is correct. Real 283d Hyperliquid data is unavailable in this environment; expand universe only with archived verified data + full provenance. Never fabricate numbers/artifacts.
- **Removal rule (mandatory):** if you find another durable handoff/task file, stale lock, failing gate, or contradictory canonical artifact, **remove/fix it before other work** with failing-tests-first evidence. Consolidate duplicates into root `HANDOFF.md`. Do not proceed past a broken gate.

## REPO-NAME PRIORITY / SPEC CONTRACT (MANDATORY)
**CRASH-REBOUND-STRATEGY** → fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. **Hourly engine only.** Never claim 20s slicing / explicit spread / L2 order-book impact.

Non-negotiable: hourly funding on **every leg** (long coin; short ETH hedge; rebound short coin; rebound long ETH hedge) on all exits including edge/missing-data/missing-ETH/fallback/final paths; hourly liquidation at worst price with correct sequencing vs stop/target/time and correct notional/timing/penalty; **stopped buy never opens rebound short**; 8x safety stop (`use_spec_safety_stop` ratio semantics: `entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound short `-9%/48h/+40%`, anchored to executed short entry (slippage/commission-aware); ETH hedge every leg, vol-ratio over 336h capped 3x; `RSI(21)<20` next-hour open, deepest-first; `>= $5M` 24h volume in **all spec-compliant gating paths** (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only, never top-ups); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (TIMESTAMPED, MANDATORY)
```text
CRASH-REBOUND-STRATEGY | 2026-11-08T17:58:25Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (must drive all work): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, explicit spread modeling, or L2/order-book impact.

Bottleneck check (2026-11-08T17:58:25Z): NO BLOCKERS. Only root `HANDOFF.md` is durable (no TODO/NEXT/PROGRESS/session variants); no `.lock` files; `main` tracks `origin/main`. CI `.github/workflows/strategy-tests.yml` runs `python -m pytest tests/ -q`. Gate re-verified: `599 passed` (599 collected, 0 skipped) — `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`. Env may lack deps: `python3.12 -m pip install pytest pyarrow numpy pandas requests`. Intentional non-bottleneck: `scripts/fetch_hyperliquid_candles.py` fail-closed on incomplete coverage/provenance is correct; real 283d Hyperliquid data unavailable here — do not fabricate. If you find any blocker (duplicate durable handoff/task file, stale lock, broken gate, contradictory canonical artifact), remove/fix it FIRST with failing-tests-first evidence before other work.

You MUST ship >=1 MATERIAL item this session. Material = spec-fidelity defect fix + tests, OR a failing-tests-first regression lock for a real uncovered spec path, OR material gated-pipeline/API/provenance guardrail hardening with proof. NOT material: passive re-verification, handoff-only edits, speculative refactors, "blocked" without a concrete missing input, or claiming hourly-engine limitations as defects.

MANDATORY HEAVY CAMPAIGN (execute in order; do not stop at easy/passive tasks):
1) Gate: `cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY && PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no` (expect 599 passed).
2) Target highest-risk UNPROVEN path with failing-tests-first evidence (no audit-only conclusions). Priority A before B before C:
   A) **Portfolio 2g/2b boundary (highest remaining):** cross-bar pending realized-exit settlement + SAME-BAR re-admission/occupancy boundary under `commission_min` + forced 120% equal-share cap-cut + `entry_next_bar`/mixed terminals. Construct a case where a realized exit settles into capacity and another symbol is (re-)admitted/probed in the same bar, or where reservation/probe state could leak/mis-admit/mis-size after pending realized-exit reconciliation. Probe `src/backtest/engine.py` portfolio loop (pending realized, reserved notionals, probe/apply admission, occupancy, gross exposure). Lock with concrete expected values: shares/notionals/PnL/timestamps/exit reasons, `final_open_positions`, reserved/open notionals, gross exposure, realized PnL reconciliation.
   B) **Rebound hedge + cap-cut + commission_min + entry_next_bar (ETH hedge enabled, uncovered terminal):** liquidation with/without ETH hedge is locked. Find/lock a concrete uncovered rebound-short terminal path — e.g. rebound stop, rebound +40% target, rebound 48h time-exit, or a real hedge sizing/funding/notional/penalty sequencing edge — ONLY with a real failing test or a proven uncovered branch and concrete expected values. Do not duplicate locked liquidation cases.
   C) **2c/d/h (only with real gap):** missing-candle-field stop comparison in spec-compliant flow; rebound 48h/funding attribution under ETH divergence in an untouched path; anchor drift in an untouched path. Failing-tests-first only.
   (2a/e CLOSED — rebound hedge entry ETH-aligned to `idx`, locked by `tests/test_rebound_hedge_entry_eth_alignment_20261108.py` + mid/final/missing-ETH locks. Do not reopen without concrete failing defect.)
3) Core files: `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `scripts/{run_portfolio,run_real_campaign,run_campaign}.py`. For every defect: failing test → minimal fix → pass. For a verified-non-defect with insufficient lock: add a regression lock with concrete expected values (state "no src fix required; behavior verified" with evidence).
4) If A/B/C yield no concrete failing/uncovered gap after honest evidence-backed attempts, ship another MATERIAL guardrail (gated pipeline/API/provenance/coverage) with failing-tests-first proof — do not end session idle.
5) Final gate: `PYTHONPATH=. python3.12 -m pytest tests/ -q --tb=no`.
6) Update ONLY root `HANDOFF.md`: UTC timestamp, exact commands/results, files changed, shipped material item(s) + evidence (failing→passing or lock proof), remaining risks, and a new timestamped heavy initial task. No other handoff files. No unrelated commits/staging.

Spec non-negotiables (never regress): hourly funding on every leg and every exit path (coin long/short, ETH hedge short/long); hourly liquidation at worst price with correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety-stop ratio semantics (`entry*(1-8*avg(hourly high-low/prev_close over 14h))`); rebound `-9%/48h/+40%` anchored to executed short entry (slippage/commission-aware); ETH hedge every leg (336h vol ratio, cap 3x); RSI(21)<20 next open deepest-first; `$5M` 24h volume in all spec-compliant gating paths (`enforce_spec_volume_floor`; `min_daily_volume_usd=0` is non-spec fixture escape hatch only); equal-share cuts old+new across 120% gross cap (cuts only); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification for real paths.
```

## SHIPPED (CONDENSED)
- **2026-11-08T16:40:00Z (lock / 2g/2b ii):** `tests/test_rebound_short_liquidation_eth_hedge_commission_min_cap_cut_entry_next_bar_20261108.py` — rebound-short liquidation w/ ETH hedge, commission_min+cap-cut+`entry_next_bar`; no src fix.
- **2026-11-08T16:18:33Z (lock / 2b):** `tests/test_rebound_short_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` — rebound-short liquidation, cap-cut+commission_min+`entry_next_bar`; no src fix.
- **2026-11-08T15:55:19Z (lock / 2g+2b):** `tests/test_portfolio_commission_min_cap_cut_mixed_terminals_reservation_20261108.py` — same-bar multi-symbol forced cap cuts, commission_min, mixed terminals, reservation/reconciliation.
- **2026-11-08T15:06:30Z (lock / 2b):** `tests/test_liquidation_commission_min_cap_cut_entry_next_bar_20261108.py` (3) — long liquidation worst-price/sequencing under `entry_next_bar`+cap-cut+`commission_min`.
- **2026-11-08T13:02:22Z (FIX / 2b):** `src/backtest/engine.py::_slippage_commission_per_share` made `commission_min`-aware; `tests/test_engine_commission_min_fill_accounting_20261108.py` (3) failing→passing.
- **2026-11-08T12:19:08Z:** long liq→stop→target sequencing lock (4).
- **2026-11-08T11:59:47Z:** liquidation/cap-cut/rebound `entry_next_bar` max-notional lock (2).
- **2026-11-08T11:48:59Z:** `entry_next_bar`+slippage target re-anchor fix.
- **2026-11-08T10:45:47Z:** portfolio same-bar probe positive-PnL capacity no-leak lock (2).
- **2026-11-08T10:24:00Z:** final-exit ETH aligned-fallback fixed/locked (4).
- **2026-11-08T10:15:30Z:** mid-exit short-ETH-series funding all exit paths locked (8).
- **2026-11-08T09:25:16Z:** 8x spec safety stop `entry_next_bar` re-anchor + ETH hedge 336h window/cap locks (5).
- **2026-11-08T09:15:40Z / 09:00:31Z / 07:13:10Z:** missing-ETH-bar hedge funding coverage; RSI trigger not nullified by non-spec downtrend filter.
- **2026-11-08T07:01:32Z / 06:15:00Z:** rebound-short 48h max-hold/funding inclusive semantics; `entry_next_bar` target/stop re-anchor to executed entry.

## REMAINING RISKS / NEXT HEAVY FOCUS (EVIDENCE-BACKED)
- **Priority A — 2g/2b portfolio boundary (UNPROVEN):** cross-bar pending realized-exit settlement + same-bar re-admission/occupancy boundary under `commission_min` + forced 120% equal-share cap-cut. Existing locks cover mixed terminals across bars and positive-PnL capacity-release probe, but a targeted same-bar post-settlement re-admission/probe/reservation reconciliation case may still expose leak/mis-admission. Evidence required.
- **Priority B — 2b+hedge uncovered terminal (PARTIALLY LOCKED):** rebound-short liquidation w/ and w/o ETH hedge under cap-cut+commission_min+`entry_next_bar` locked. Remaining: rebound short **stop / +40% target / 48h time-exit** under ETH hedge enabled + cap-cut + commission_min + `entry_next_bar` (hedge sizing/funding/notional/penalty/reservation sequencing). Failing-tests-first + concrete values only.
- **2b engine (NARROWED):** `commission_min` parity locked; long liquidation+cap-cut+commission_min+`entry_next_bar` locked. Only concrete uncovered rebound-short/hedge interactions remain.
- **2a/e CLOSED:** rebound hedge entry ETH-aligned to `idx`; locked. Do not reopen without failing-tests-first concrete defect.
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
