# Consolidated Final Decision Verdict — C1–C20 — CRASH-REBOUND-STRATEGY

**Token:** `NO_GO` · **research_program_complete:** `true`
**Generated (UTC):** 2026-11-17T05:39:45Z · **Supersedes:** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.json` (also `NO_GO`)
**Source of truth (do not alter):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`

## Verdict

**NO_GO.** The crash-rebound strategy under the C19-adjudicated spec-faithful entry rule is not validated as a decision-grade positive edge on available native or cross-venue evidence. No campaign warrants a GO claim.

## Per-Venue Numbers (both `NO_GO`)

| Venue | Trades | Total PnL | Coin | Hedge | Rebound Short | Episodes | Crash Days | Events |
|---|---|---|---|---|---|---|---|---|
| OKX | 113 | **−55,057.45** | −197,767.56 | +140,841.80 | −38,420.09 | 31 | 45 | 369 |
| Binance UM | 136 | **−70,309.57** | −214,779.38 | +135,812.12 | −38,036.67 | 36 | 53 | 484 |

**Pooled total PnL:** `−125,367.02`
**Bootstrap 95% CI (episode-block):** `[-140,619.14, -110,114.9]` — excludes zero only in the negative direction; `prob_pooled_total_gt_0 = 0.0`
**Go checks:** `6/14` · **Effective sample:** `trades=249, episodes=67, distinct_crash_days=98`

## Structural Power Note

C20 confirms the C19 NO_GO out-of-sample: the spec-faithful next-open rule loses on both independent multi-year venues (OKX and Binance UM), so the native NO_GO is not a single-venue artifact. Effective episode counts remain below the GO floor.

## Provenance

- **Real-market, cross-venue** (OKX + Binance UM), non-synthetic. Multi-year window 2023-01-01T00:00:00Z..2026-09-28T23:00:00Z (32,808 hourly bars/symbol).
- **`is_hyperliquid_venue_data = false`** — this is NOT Hyperliquid performance evidence and must never be relabelled as such.
- C20 prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}`, status `PRE_REGISTERED_BEFORE_COMPUTE`. Config fixed (`entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120). No config switching after results.

## Closure Certification (verified 2026-11-17T05:42Z)

- Full `pytest tests/ -q`: **`1047 passed, 1 skipped`** — codebase green.
- Gates: `session_gate.py` `21/21 checks passed`; `verify_campaign_evidence.py` `EVIDENCE VERIFIED`; C20/C19/C13/C14/C6 all `ACCEPTANCE: PASS`; `probe_hyperliquid_blocker.py` `FULL_283D_BLOCKED_BY_API_RETENTION` (Hyperliquid acquisition exhausted, earliest served ~2026-04-21/22).

## Carry-Forward Controls

- No cross-venue relabeling as Hyperliquid-native.
- No synthetic gap-fill as verified; no spec relaxation to manufacture a GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- Do not relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.
- Do not invent a same-data C21+ campaign. A new direction requires a new prereg + new data + explicit operator authorization.