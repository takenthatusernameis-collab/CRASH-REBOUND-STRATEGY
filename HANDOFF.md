# DURABLE HANDOFF — CRASH-REBOUND-STRATEGY
**Updated (UTC):** 2026-11-11T12:23:15Z
**Single canonical durable handoff:** ONLY this root `HANDOFF.md`. Do not create/read any other handoff file (no TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff variants). `scripts/controller_progress.py`, `tests/test_controller_progress_accounting.py`, timed/session-named tests, `__pycache__`, and `_probe_*` artifacts are implementation/tests/scratch, not handoffs.

## SESSION AUDIT (2026-11-11T12:23:15Z) — BOTTLENECKS CLEARED, GATE RE-VERIFIED, NEXT CAMPAIGN LOCKED
- **Repo identity/priorities:** `CRASH-REBOUND-STRATEGY` — crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md` (hourly backtest). Never claim 20s slicing, spread/L2/order-book impact.
- **Bottlenecks checked/cleared:** only root `HANDOFF.md` exists as durable handoff (no duplicate durable TODO/NEXT/PROGRESS/STATUS/SESSION/CONTEXT handoff docs found). No `*.lock` outside `.git/`. No stale process blockers observed. `git status` clean. `research_state/.test_derive_vol_*` temp dirs may regenerate (gitignored) — not blockers. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical/partially stale — verify against code+tests before acting. Real 283d Hyperliquid BTC/ETH candles remain unavailable/unverified (fail-closed by design, environment blocker — never fabricate).
- **Campaign status (evidence):** #1 COMPLETE. #2 COMPLETE. #3 COMPLETE. **#4 ACTIVE:** last material lock shipped 2026-11-11T12:17:54Z — long TIME_EXIT with ETH hedge missing ETH bar at exit index + fallback sequencing + commission_min/cap_cut-shares + entry_next_bar + hourly funding (`tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py`, 2 tests). Remaining #4 priority: **rebound-short STOP or TARGET exit with ETH hedge missing ETH bar at exit index** + fallback sequencing to entry RAW hedge-exit accounting + commission_min/cap_cut + entry_next_bar where applicable + hourly funding on both legs; then funding accrual sign correctness on every leg/exit path; liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar on uncovered combos.
- **Gate evidence (re-verified this session 2026-11-11T12:23:15Z):** `PYTHONPATH=. python3 -m pytest -q --tb=short` → **765 passed, 12 skipped in 29.19s**. Re-run as blocking first action next session; fix FIRST if broken/regressed. Do not treat this count as fresh green without re-run.

## MATERIAL SHIPPED (LATEST, CARRY-FORWARD EVIDENCE)
- **2026-11-11T12:17:54Z (#4 progressed):** `tests/test_long_time_exit_missing_eth_exit_bar_cap_cut_commission_min_entry_next_bar_funding_20261111.py` (2 tests, traced) — long TIME_EXIT, short ETH hedge, ETH bar missing at exit idx (fallback close `hedge_exit=1999.7511050264034` from executed `hedge_entry=1975.1105026403286`, `hedge_size=0.10226`), `shares=2.0`, `entry=102.26`, `exit=98.75`, `bars_held=3`, coin `pnl=-7.026135600000011`, `hedge_pnl=-2.5136887560000054`, `total=-9.539824356000016`, `max_live=204.52`, full coin+hedge risk_state settlement, funding reconciliation vs off (`delta=-7.635600000099885e-05 = -coin_cost-hedge_component`).
- **2026-11-11T09:16:00Z (#3 COMPLETE):** 6 test files / 14 tests covering all six uncovered #3 edge cases (3-candidate max_pos=2 batch-cut, existing+2 sequential cut, heterogeneous commission_min, deterministic tie-break, cut propagation/no top-up, settlement reconciliation with no-look-ahead).
- **2026-11-11T05:29:28Z (#2 COMPLETE, #1 COMPLETE):** rebound-short liquidation ETH bar ENTIRELY ABSENT at exit index locked; 1.25% 24h-volume sizing bypass fixed/locked.
- **#4 locks through 2026-11-11:** long/rebound-short exit/missing-ETH/hedge/funding/liquidation/settlement combo locks in dated `tests/test_*202611*.py` including this long TIME_EXIT missing-ETH fallback lock.

## IMPLEMENTATION STATUS (EVIDENCE-BACKED, KEY SURFACES)
`research_state/gap_analysis.md` is historical/partially stale; verify against code+tests before acting.
- **Core/spec-compliant paths:** RSI(21)<20 crash trigger, $5M 24h volume enforcement in trigger/universe/gated paths, 1.25% 24h-volume sizing when enabled, ETH hedge sizing 336h vol-ratio capped 3x with no-look-ahead (`eth_candles[:idx+1]`), rebound short after +9% target (stop +40%, target -9%, 48h), 8x spec safety stop, 120% gross-cap equal-share cuts (cuts only), portfolio bar-by-bar no-look-ahead admission with deepest-first ordering.
- **Runners/gating:** `scripts/run_portfolio.py` per-bar gating, deepest-first sort, reservation/cap-cut overlay, batch-cut pre-cutting for rebound-short multi-candidate same-bar admissions when no existing positions and total desired>cap. `run_real_campaign.py` sets RSI+ETH hedge+volume sizing+verified gates, fail-closed provenance.
- **Fail-closed:** engine raises when `require_eth_hedge=True` and no usable hedge; provenance/verified-cache guards fail closed for real paths.

## REMAINING RISKS / HEAVY FOCUS CAMPAIGN (EVIDENCE-BACKED, MANDATORY)
- **BLOCKED by environment (fail-closed):** real 283d Hyperliquid candles unavailable/unverified here. Never fabricate.
- **#1 COMPLETE. #2 COMPLETE. #3 COMPLETE.**
- **#4 ACTIVE (PRIMARY, MANDATORY, heavy, failing-tests-first):**
  - **FIRST uncovered cell (NEXT, do now): rebound-short STOP or TARGET exit with ETH hedge missing ETH bar at exit index** + fallback sequencing to entry RAW hedge-exit accounting + commission_min/cap_cut interaction + entry_next_bar where applicable + hourly funding on BOTH legs (rebound short coin + long ETH hedge). Long TIME_EXIT missing-ETH cap_cut/commission_min/entry_next_bar/funding is locked; rebound-short liquidation-missing-ETH and long in-loop STOP/TARGET missing-ETH combos are locked in dated tests — rebound-short STOP/TARGET missing-ETH fallback remains uncovered.
  - After first uncovered case: funding accrual sign correctness on every leg/exit path (explicit reconciliation where not yet locked); liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar on uncovered combos.
  - Ship failing-tests-first regression lock (or defect fix+proof) for the first uncovered case with concrete expected values traced from engine math (fills per leg, PnL per leg, timestamps, hedge notional/side, funding, liquidation penalty, reconciliation, no look-ahead). **If #4 proven fully locked with concrete evidence, proceed to next campaign immediately — do not idle.**
- **Next campaign (if #4 fully locked):** material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs, or gated-pipeline/provenance guardrail hardening with concrete expected values.
- **No-idle rule:** if no concrete failing case after evidence-backed attempts, ship another MATERIAL guardrail (failing-tests-first regression lock with concrete expected values for an uncovered spec path). Do not end idle.

## CRITICAL CONTEXT
- **Spec truth:** `crash-rebound-strategy.pdf` → `research_state/strategy_spec.md`. Test window 2025-12-20→2026-09-28 (283d), 6792 hourly bars/symbol.
- **Core:** `src/strategy/{config,crash_rebound,risk}.py`, `src/backtest/engine.py`, `src/data/{loader,provenance,streaming_ingest}.py`, `src/metrics/campaign_metrics.py`
- **Runners/guards:** `scripts/run_portfolio.py`, `scripts/run_real_campaign.py`, `scripts/run_campaign.py`, `scripts/derive_verified_universe.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/generate_candle_coverage_gap_report.py`

## RULES (NON-NEGOTIABLE)
- **Heavy-work guardrail:** each session ships >=1 material item with concrete evidence.
- **Spec is truth:** both legs, ETH hedge every leg, funding/liquidation correct on every leg/exit path, $5M gating in all spec-compliant paths, 1.25% 24h-volume sizing in spec-compliant paths, equal-share cuts old+new, stopped buy never opens rebound short.
- **Gating boundaries:** `backtest_simple` is low-level executor (signal assumed). Spec-compliant gating in `generate_signal`/`filter_universe`/`passes_universe_filter`/gated wrappers/runners.
- **Fail-closed:** missing provenance/verification for real path → reject. Never fabricate numbers/artifacts.
- **Single handoff:** only root `HANDOFF.md`.

## INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (2026-11-11T12:23:15Z, MANDATORY, HEAVY, NON-OPTIONAL)
```text
CRASH-REBOUND-STRATEGY | 2026-11-11T12:23:15Z | INITIAL TASK (HEAVY, NON-OPTIONAL, SINGLE DURABLE HANDOFF)

Repo identity/priority (MUST DRIVE ALL WORK): CRASH-REBOUND-STRATEGY → implement and harden crash→rebound execution fidelity to `crash-rebound-strategy.pdf` / `research_state/strategy_spec.md`. Hourly backtest engine only. NEVER claim 20s slicing, spread/L2/order-book impact.

BOTTLENECKS CLEARED/CHECKED (2026-11-11T12:23:15Z): only root `HANDOFF.md` is durable. No duplicate durable handoff docs. No stale `*.lock` outside `.git/`. `git status` clean. `research_state/.test_derive_vol_*` temp dirs may regenerate (gitignored) — not blockers. `research_state/gap_analysis.md` and `research_state/campaign_artifact_provenance_erratum.md` are historical — verify against code+tests. Real 283d Hyperliquid BTC/ETH data UNAVAILABLE/UNVERIFIED (fail-closed) — NEVER fabricate. If any blocker appears (duplicate handoff, stale lock, broken gate, contradictory canonical artifact), fix it FIRST with failing-tests-first evidence.

GATE (RE-VERIFIED 2026-11-11T12:23:15Z): `PYTHONPATH=. python3 -m pytest -q --tb=short` → **765 passed, 12 skipped in 29.19s**. Re-run as blocking first action next session; fix FIRST if broken/regressed. Do not treat this count as fresh green without re-run.

LOCKED (keep ALL anchors green): Priority A/B, B-rem1–B-rem8, 2a/e, 2b engine 6 cross-leg cells, commission_min parity, completing-probe reservation cut propagation, mixed-target batch-cut equal-share, all reservation/max_live/cap-cut locks (incl. 4-candidate mixed-terminal max_live inflation), cap-cut no-top-up, engine missing-candle fail-closed stop/target, verified-consumer temp/manifest cache pairing, D guardrails/provenance/archive/publish guards, spec-compliant ETH-hedge fail-closed in gated paths, all long/rebound-short exit/missing-ETH/hedge/funding/liquidation/settlement locks through 2026-11-11, 1.25% 24h-volume sizing enforcement, $5M 24h volume floor enforcement across all gated surfaces, RSI-trigger deepest-first admission in portfolio/gated path — FULLY LOCKED. Known interpretation: actual `max_live_coin_notional` can exceed entry-notional cap at pressure points/across rebound leg while reservations record entry-notional cap — do NOT "fix" without concrete failing defect preserving all anchors.

#1 COMPLETE. #2 COMPLETE. #3 COMPLETE. #4 ACTIVE.

#4 PRIMARY MATERIAL TARGET (MANDATORY, attempt first now — heavy, failing-tests-first):
FIRST uncovered cell (do now): **rebound-short STOP or TARGET exit with ETH hedge missing ETH bar at exit index** + fallback sequencing to entry RAW hedge-exit accounting + commission_min/cap_cut interaction + entry_next_bar where applicable + hourly funding on BOTH legs (rebound short coin + long ETH hedge).
  - Build deterministic hand-traced fixture from an established rebound-short scenario (long target hit → rebound short opens with long ETH hedge). At rebound-short STOP or TARGET exit bar, make ETH candle missing/unusable.
  - Trace and lock concrete expected values from engine math: coin short entry/exit fills and pnl, hedge close fallback path/raw+slippage+commission_min and hedge pnl, hourly funding on rebound short coin and long ETH hedge for held hours, liquidation not breached, reservation/risk_state settlement, trades/rebound attribution, reconciliation, timestamps, hedge notional/side. No look-ahead.
  - Long TIME_EXIT missing-ETH cap_cut/commission_min/entry_next_bar/funding is locked; rebound-short liquidation-missing-ETH and long in-loop STOP/TARGET missing-ETH combos are locked — do not duplicate those cells.
  - Ship failing-tests-first regression lock (or defect fix+proof) with concrete expected values.

After first uncovered case: funding accrual sign correctness on every leg/exit path where not yet explicitly locked; liquidation worst-price sequencing/notional/timing/penalty under cap_cut+commission_min+entry_next_bar on uncovered combos.
**If #4 proven fully locked with concrete evidence, proceed to next campaign immediately — do not idle.**

NEXT CAMPAIGN (if #4 fully locked): material guardrail hardening with failing-tests-first proof — cross-leg reconciliation/settlement lock for every terminal path (stop/target/time_exit/liquidation/final_exit) on both legs, OR gated-pipeline/provenance guardrail hardening with concrete expected values.

HEAVY-WORK GUARANTEE (ENFORCED): ship >=1 MATERIAL item with concrete evidence this session. Material = spec-fidelity defect fix + failing-tests-first proof, OR failing-tests-first regression lock for an uncovered spec path with concrete expected values traced from engine math, OR material gated-pipeline/provenance guardrail hardening with proof. NO IDLE. No passive re-verification, no handoff-only edits without bottleneck/gate evidence, no speculative refactors.

FINAL GATE: `PYTHONPATH=. python3 -m pytest -q --tb=short` (expect >=765 passed, 12 skipped unless legitimately changed by material work). Report exact count.
UPDATE ONLY root `HANDOFF.md`: timestamp, exact commands/results, files changed, shipped material item(s)+concrete evidence, remaining risks, new timestamped heavy initial task. No other handoff files.

SPEC NON-NEGOTIABLES (never regress): hourly funding on every leg/exit; hourly liquidation worst price correct sequencing/notional/timing/penalty; stopped buy never opens rebound short; 8x safety stop; rebound `-9%/48h/+40%` anchored to executed short entry; ETH hedge every leg (336h vol ratio cap 3x), hedge sizing uses `eth_candles[:idx+1]`, entry aligned (no look-ahead); RSI(21)<20 next open deepest-first in spec path; `$5M` 24h volume in all spec-compliant gating paths; 1.25% 24h-volume sizing in spec-compliant path; equal-share cuts old+new across 120% gross cap (cuts only, never top-up); one position/coin; strict no-look-ahead. Fail-closed on missing provenance/verification and on missing/insufficient required ETH hedge in spec-compliant paths.
```
