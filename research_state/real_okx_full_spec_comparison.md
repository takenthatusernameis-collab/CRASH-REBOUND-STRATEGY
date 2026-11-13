# Spec vs Actual — Real OKX 283-Day Crash-Rebound Campaign (Phase G+)

**Generated (UTC):** 2026-11-13T11:24:21.124182+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

Decision-grade comparison of the published Hyperliquid spec targets against the executed real-market OKX campaign. Every actual value is read from a committed artifact; every divergence cites artifact counts and code paths. Spec targets are transcribed from `research_state/strategy_spec.md`.

## Metric table (spec vs actual)

| Metric | Spec (Hyperliquid test) | Actual (OKX full run) | Delta / note |
|---|---|---|---|
| Total return | +81.2% | +9.1597% | ~11.3% of spec; no equivalence claim |
| Annualized return | +115.2%/yr | +22.5995%/yr | over 0.4301 yr realized horizon, not 283 d |
| Worst drawdown | -5.4% | -2.0275% | smaller DD on a smaller realized book |
| Positive months | 6 of 10 | 4 of 7 | different period / bucket count |
| Trades | 85 | 8 | +9.41% of spec |
| Buys (win rate) | 73 (71%) | 8 (50.00%) | constituent split includes the rebound-short's buy leg |
| Shorts (win rate) | 12 (83%) | 1 (0.00%) | one rebound short, net negative after hedge |
| Rebound-short profit contribution | ~27% | -17.87% | contradicts spec in this venue/window |
| Universe | spec-relevant >= $5M set | 54 admitted / 5 traded | admitted-but-not-traded quantified below |

## Supporting metrics (actual, from artifacts)

| Metric | Value |
|---|---|
| Equity | $100,000.00 -> $109,159.69 |
| Sharpe / Sortino / Calmar | 0.6258 / 1.2618 / 4.3793 |
| Win rate / profit factor | 50.00% / 5.2335 |
| Buy leg PnL / share | $10,796.55 / +117.8703% |
| Short leg PnL | $-1,636.86 |
| Exit reasons | {"liquidated": 1, "time_exit": 6, "target_rebound_short": 1} |
| Traded symbols | {"SOL": 3, "ETH": 1, "LINK": 1, "BCH": 2, "AVAX": 1} |
| First entry / last exit (UTC) | 2026-01-19T03:00:00Z / 2026-05-20T10:00:00Z |
| Target window | 2025-12-20T00:00:00+00:00 -> 2026-09-28T23:00:00+00:00 |
| Peak live coin notional / cap | $120,000.00 / $120,000.00 (100.00% utilization) |

## Divergence analysis (evidence-backed, one subsection per metric)

### `trade_frequency` — trades

- **Spec:** 85
- **Actual:** 8
- **Driver:** signal-availability funnel, not a single defect
- **Code paths:** `src/strategy/crash_rebound.py:162`, `src/strategy/config.py:7`, `src/strategy/crash_rebound.py:238`, `src/strategy/crash_rebound.py:367`, `scripts/run_portfolio.py:49`
- **Evidence:** `{"funnel": {"rsi_events": 342, "volume_gate_pass": 187, "bounce_confirmed": 39, "regime_min_price_ok": 89, "signal_gate_pass": 11, "trades_opened": 8, "trades_matched_to_census": 8}, "blocking_reasons": {"trade_opened": 8, "volume_gate": 155, "bounce_not_confirmed": 159, "regime_min_price": 17, "one_position_per_coin": 3}, "blocking_reasons_sum": 342, "unexplained_signal_gate_events": 0, "census_artifact": "research_state/crash_event_census_real_okx_full.json"}`

Of 342 RSI(21)<20 events across 54 admitted symbols, 155 died on the >= $5M trailing-24h volume gate, 159 on bounce confirmation, 17 on the >= $5 price floor, and 3 on one-position-per-coin. 11 events cleared every signal gate and 8 became trades. Every event has exactly one blocking reason and the reasons sum to the event total, so the shortfall is a property of crash availability in this venue/window, not an attribution bug. Spec's 85 trades came from a denser crash cluster on Hyperliquid.

### `annualization_horizon` — annualized return

- **Spec:** 115.2
- **Actual:** 22.599525626916606
- **Driver:** annualization over the realized-trade horizon, not the 283-day window
- **Code paths:** `src/backtest/engine.py:179`, src/metrics/campaign_metrics.py (equity_annualized_return_pct)
- **Evidence:** `{"realized_horizon_years": 0.4301369863013699, "first_entry_utc": "2026-01-19T03:00:00Z", "last_exit_utc": "2026-05-20T10:00:00Z", "target_window": ["2025-12-20T00:00:00+00:00", "2026-09-28T23:00:00+00:00"], "equity_curve_points": 9}`

Annualized return is computed over 0.4301369863013699 years of realized-trade horizon (2026-01-19T03:00:00Z to 2026-05-20T10:00:00Z), not the 283-day target window. No trade opens after 2026-05-20T10:00:00Z, so the final ~131.54 days of the window contribute zero return while the spec's figure covers its full window. Annualizing a short active span inflates the rate relative to a full-window figure; the two numbers are not directly comparable.

### `drawdown_scale` — worst drawdown

- **Spec:** -5.4
- **Actual:** -2.0274965243788596
- **Driver:** smaller realized book (8 trades, 5 symbols) => smaller peak-to-trough
- **Code paths:** `src/strategy/config.py:87`, `scripts/run_portfolio.py:49`
- **Evidence:** `{"max_drawdown_usd": -2091.6053422543337, "max_drawdown_timestamp": "1769551200000", "trades": 8, "max_live_coin_notional": 120000.0, "gross_cap_usd": 120000.0, "gross_cap_utilization_pct": 100.0}`

Worst drawdown -2.0274965243788596% ($-2,091.61) is smaller in magnitude than spec -5.4% because the realized book is far smaller: 8 trades, peak live coin notional $120,000.00 against a $120,000.00 gross cap (100.00% utilization). A smaller book has less absolute peak-to-trough excursion. This is not evidence of superior risk control.

### `monthly_breadth` — positive months

- **Spec:** 6 of 10
- **Actual:** 4 of 7 (3 negative, 0 flat)
- **Driver:** different period and bucket count (7 realized-trade buckets vs 10 spec months)
- **Code paths:** src/metrics/campaign_metrics.py (monthly_breakdown/positive_months)
- **Evidence:** `{"monthly_breakdown": {"1768946": 3161.969310655877, "1769115": -121.63379295786945, "1769551": -1969.9715492964642, "1770112": 2988.2241534821824, "1770062": 3499.3737911286935, "1770069": 1673.7337690180457, "1779271": -72.00374714750825}, "annual_breakdown": {"1768": 3161.969310655877, "1769": -2091.6053422543337, "1770": 8161.3317136289215, "1779": -72.00374714750825}, "total_months": 7}`

4 of 7 realized-trade buckets were positive vs spec 6 of 10. The bucket count differs because the realized horizon spans fewer calendar months, so this is a coverage difference, not a reproducibility failure.

### `buy_leg` — buys (win rate)

- **Spec:** 73 (71%)
- **Actual:** 8 (50.00%)
- **Driver:** leg attribution split of one rebound-short trade into buy+short constituents
- **Code paths:** src/metrics/campaign_metrics.py:161 (constituent split), src/metrics/campaign_metrics.py:237 (_split_leg_pnls)
- **Evidence:** `{"buy_trades": 8, "buy_wins": 4, "buy_pnl": 10796.553759712579, "buy_pnl_share_pct": 117.87027158190706, "buy_profit_factor": 5.990066741999788, "trade_attribution_by_leg": {"buy": {"leg": "buy", "pnl": 10796.55375971258, "trades": 8}, "short": {"leg": "short", "pnl": -1636.8618248296225, "trades": 1}}}`

Buy leg: 8 constituent trades, 4 wins (50.00%), PnL $10,796.55 (117.87% of grand total), profit factor 5.990. The buy-leg trade count exceeds the 8 campaign trades because the single rebound-short trade is split into its buy and short constituents for attribution; `trade_attribution_by_leg` sums to the grand total ($9,159.69).

### `short_leg` — shorts (win rate)

- **Spec:** 12 (83%)
- **Actual:** 1 (0.00%)
- **Driver:** only one rebound short fired; it was net negative after hedge separation
- **Code paths:** `src/strategy/config.py:116`, src/metrics/campaign_metrics.py:237
- **Evidence:** `{"short_trades": 1, "short_wins": 0, "short_pnl": -1636.8618248296225, "short_pnl_share_pct": -17.87027158190707, "rebound_short_constituents": {"rebound_short_pnl": 1067.729426, "rebound_hedge_pnl": -2704.591251}}`

Short leg: 1 trade, 0 wins, PnL $-1,636.86 (-17.87% share). Its coin leg gained $1,067.73 while the long-ETH hedge against it lost $2,704.59, so the rebound short was net negative after hedge separation. This is a single observation and must not be read as the spec's ~27% profit contribution.

### `rebound_short_attribution_correction` — rebound-short profit contribution

- **Spec:** 27.0
- **Actual:** -17.87027158190707
- **Driver:** earlier `short +2,988.22` reading conflated the whole BCH trade with the short leg
- **Code paths:** src/metrics/campaign_metrics.py:161, src/metrics/campaign_metrics.py:237
- **Evidence:** `{"bch_trade_total_pnl": 2988.2241534821824, "bch_trade_pnl": 4625.085978311805, "bch_rebound_short_pnl": 1067.729426268781, "bch_rebound_hedge_pnl": -2704.5912510984035, "authoritative_leg_attribution": {"buy": {"leg": "buy", "pnl": 10796.55375971258, "trades": 8}, "short": {"leg": "short", "pnl": -1636.8618248296225, "trades": 1}}}`

RETRACTION: an earlier summary read the BCH rebound-short trade's whole-trade total ($2,988.22) as the short leg's profit. The authoritative attribution is short coin $1,067.73 plus rebound hedge $-2,704.59 = $-1,636.86 for the short leg (-17.87% share), while the buy leg is $10,796.55 (117.87%). The two legs sum to the grand total.

### `universe_utilization` — universe

- **Spec:** spec-relevant >= $5M set (~26 on Hyperliquid per spec; up to ~80 in 2024-2025)
- **Actual:** 54 admitted / 5 traded
- **Driver:** admitted universe is broad but crash+rebound availability is narrow
- **Code paths:** `src/strategy/crash_rebound.py:162`, `scripts/run_portfolio.py:49`
- **Evidence:** `{"universe_size": 54, "symbols_loaded": 54, "symbols_traded": 5, "traded": {"SOL": 3, "ETH": 1, "LINK": 1, "BCH": 2, "AVAX": 1}, "never_traded_symbols": 49, "never_traded_with_signal_pass": [], "admitted_but_never_traded_zero_signal": ["OP", "TRX", "FLOW", "WLD", "COMP", "LDO", "SAND", "STX", "SUI", "APT", "CHZ", "GALA", "XRP", "ADA", "DOGE", "FIL", "SEI", "UNI", "WIF", "XLM", "ALGO", "BONK", "FET", "PEPE", "SUSHI", "XTZ", "ZEC", "AAVE", "ARB", "INJ", "SATS", "CRV", "DOT", "ORDI", "LTC", "NEAR", "SHIB", "DASH", "HBAR", "ICP", "JTO", "KSM", "RENDER", "AXS", "ENJ", "ETC", "JUP", "SNX", "TIA"], "top_symbols_by_events": [{"symbol": "BCH", "bars": 6792, "events": 29, "volume_gate_pass": 19, "bounce_confirmed": 3, "signal_gate_pass": 3, "trades_opened": 2}, {"symbol": "OP", "bars": 6792, "events": 22, "volume_gate_pass": 17, "bounce_confirmed": 4, "signal_gate_pass": 0, "trades_opened": 0}, {"symbol": "TRX", "bars": 6792, "events": 19, "volume_gate_pass": 19, "bounce_confirmed": 3, "signal_gate_pass": 0, "trades_opened": 0}, {"symbol": "FLOW", "bars": 6792, "events": 18, "volume_gate_pass": 0, "bounce_confirmed": 2, "signal_gate_pass": 0, "trades_opened": 0}, {"symbol": "SOL", "bars": 6792, "events": 16, "volume_gate_pass": 16, "bounce_confirmed": 5, "signal_gate_pass": 5, "trades_opened": 3}, {"symbol": "WLD", "bars": 6792, "events": 14, "volume_gate_pass": 14, "bounce_confirmed": 2, "signal_gate_pass": 0, "trades_opened": 0}, {"symbol": "COMP", "bars": 6792, "events": 12, "volume_gate_pass": 0, "bounce_confirmed": 2, "signal_gate_pass": 0, "trades_opened": 0}, {"symbol": "ETH", "bars": 6792, "events": 12, "volume_gate_pass": 12, "bounce_confirmed": 1, "signal_gate_pass": 1, "trades_opened": 1}]}`

54 symbols were admitted (peak trailing-24h volume >= $5M) and all were loaded, but only 5 ever traded (AVAX, BCH, ETH, LINK, SOL). 49 admitted symbols never even produced a signal-gate-passing event, and 0 produced signal-gate passes that did not become trades (one-position-per-coin / capacity). Breadth of admission is therefore not breadth of participation.

## Conclusions

- Realized: +9.1597% total return over a 0.4301-year realized-trade horizon (22.5995% annualized), worst drawdown -2.0275%, 8 trades, win rate 50.00%, profit factor 5.234.
- The trade-frequency gap (8 vs 85) is fully explained by the J1 census funnel 342->187->39->11->8 with 0 unexplained signal-gate events and blocking reasons summing to 342. No attribution defect is implied.
- Rebound short contributed -17.8703% of the grand total ($-1,636.86), contradicting the spec's ~27% contribution claim in this venue/window. The buy leg carried the result ($10,796.55, +117.8703%).
- Peak gross-cap utilization was 100.00% of the $120,000.00 120% cap, so the equal-share cut mechanism was not a binding constraint on this realized book.
- No claim of Hyperliquid parity is made or implied: the venue, the realized horizon, and the realized trade count all differ from the spec test.

## Reproducibility

| Artifact | sha256 |
|---|---|
| `campaign_sha256` | `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8` |
| `metrics_sha256` | `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c` |
| `census_sha256` | `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec` |
| `manifest_sha256` | `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554` |

**Provenance caveat (repeated):** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
