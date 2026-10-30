# Gap Analysis | CRASH-REBOUND-STRATEGY | 2026-10-30T01:43:44Z

## Comparison: PDF Spec vs Current Implementation

### Core Logic
| Item | PDF Spec | Implementation | Status | Notes |
|---|---|---|---|---|
| Crash trigger | 21-hour RSI < 20, coins with >=$5M vol, next hourly open entry | `detect_crash()` looks for large % drop from open or prev close (-2% default), volume spike confirmation | PARTIAL/MISMATCH | Uses price-drop based trigger, not RSI. Config has `crash_pct_drop`, `volume_spike_mult`. Tests use drop-based logic. |
| Entry timing | Buy at next hourly open | `backtest_simple` does `entry_next_bar` using next bar open when enabled | OK | Matches concept. |
| Rebound confirmation | Implied by bounce after crash | `confirm_rebound()` requires bullish candle with body in upper range of last candle | OK-ish | Heuristic; different from RSI-based trigger but works with fixtures/tests. |
| Target | +9% or 50h | Config has `target_pct=9.0`, also uses `reward_risk` fallback | OK | Matches. |
| Time exit (buy) | 50 hours max | `time_exit_max_bars` default 50 | OK | Matches. |
| Rebound short | After buy hits +9%, short same coin, close at -9% or 48h, stop at +40% | Implemented in backtest engine with `enable_rebound_short`, `rebound_short_target_pct=9.0`, `rebound_short_time_exit_bars=48`, `rebound_short_stop_pct=40.0` | OK | Matches well; tested. |
| Stop (buy) | 8x hourly range (ATR-like) below entry | ATR-based stop via `atr()` and `safety_stop_price()` with `stop_atr_mult=8.0`, `atr_period=14` | OK | Aligned conceptually. |
| Stop (short) | +40% above entry | Implemented | OK | Matches. |
| ETH hedge | Every trade hedged with ETH (vol ratio, capped 3x) | Not implemented in codebase (no hedge logic in strategy/backtest) | MISSING | Critical part of spec. |
| Position sizing by order book | Up to 1.25% of coin's 24h volume, equal-share cuts on cap breach | `position_size_shares()` uses risk % of capital; no volume-based sizing or cap/equal-share logic visible | MISSING/DIFFERENT | Code uses fixed risk% sizing; PDF uses order-book/volume-based sizing + cap management. |
| Universe filter ($5M vol) | >=$5M daily volume | Not enforced | MISSING | |
| Multiple positions/cap management | Buys+shorts capped at 120% of vault, equal-share cuts, 1 position per coin | Risk has `max_positions`, `gross_cap_pct` but no equal-share cut logic on new signals/open positions | PARTIAL | Config has caps but implementation not matching PDF's dynamic cut behavior. |
| Regime filter | Avoid downtrend? (not explicitly emphasized as RSI filter, but vault sits in USDC between crashes) | `regime_ok()` blocks if below MA/price threshold when enabled | PARTIAL | Different mechanism. |
| Slicing orders | Never >half book, slice every ~20s | Not implemented | MISSING | Execution detail. |
| Hourly funding/liquidation checks | Modeled in sim | Not present | MISSING | Backtest is simplified. |
| Look-ahead guard | No look-ahead | Tests enforce/look-ahead guards exist | OK | `backtest_simple` checks start_idx properly. |

### Data/Infrastructure
| Item | Status | Notes |
|---|---|---|
| PDF extracted | DONE | `research_state/strategy_spec.md` created |
| Fixtures | OK | Multi-symbol fixtures exist for SPY/QQQ/IWM |
| Tests | ALL PASS (58/58) | Good baseline |
| Scripts/research_state dirs exist | OK | Empty except maybe nothing |

## Prioritized Gaps (by impact)
1. **Crash trigger alignment** (HIGH) - PDF says RSI(21)<20 on coins >=$5M vol; code uses % drop. Need to understand if tests expect drop-based or if we need to support both. Tests all pass with current drop-based logic, so either (a) keep drop-based as implementation variant that satisfies tests, or (b) add RSI-based trigger. Need to be careful not to break existing tests.
2. **ETH hedging** (HIGH) - Every trade hedged with ETH (vol ratio, capped 3x). This is fundamental to strategy. Needs design/implementation.
3. **Position sizing per order book** (HIGH) - 1.25% of 24h volume, cap management with equal-share cuts. Major difference from risk% sizing.
4. **Universe/volume filters** (MED) - >=$5M daily volume filter.
5. **Execution realism** (MED) - Slicing, funding, liquidation checks (more complex).

## Recommendations
- Don't break existing passing tests. Add support for both trigger styles? Or make RSI-based trigger available via config.
- For "heavy working" per request: focus on making implementation closer to PDF spec where it affects correctness of backtest/results, but incrementally.
- Create a concrete action plan in HANDOFF.md.
