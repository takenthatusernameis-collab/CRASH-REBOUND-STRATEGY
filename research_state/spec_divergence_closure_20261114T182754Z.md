# Spec Divergence Closure — 2026-11-14T18:27:54Z

**Label:** `NOT_EVIDENCE_SPEC_COMPARISON_CLOSURE` — code/spec audit only. Cross-venue OKX artifacts are NOT Hyperliquid performance evidence. No strategy behaviour changed; no campaign re-run.

**Divergences audited:** 8 of 8 (resolved 4, retained 4, gap 0, unresolved 0).

| Divergence | Metric | Spec | Actual | Status | Basis |
|---|---|---|---|---|---|
| `trade_frequency` | trades | 85 | 8 | **RESOLVED_IN_CODE** | Funnel closes exactly (blocking reasons sum to RSI events, 0 unexplained); trade count is crash-availability, not an attribution bug. |
| `annualization_horizon` | annualized return | 115.2 | 22.599525626916606 | **INTENTIONALLY_RETAINED** | Annualization is horizon-explicit and timestamp-derived; the delta vs spec is a realized-horizon difference, not a defect. Retained as-is (no full-window curve exists to annualize over). |
| `drawdown_scale` | worst drawdown | -5.4 | -2.0274965243788596 | **INTENTIONALLY_RETAINED** | Drawdown magnitude scales with realized book size; smaller DD is a coverage artefact, explicitly not evidence of superior risk control. |
| `monthly_breadth` | positive months | 6 of 10 | 4 of 7 (3 negative, 0 flat) | **INTENTIONALLY_RETAINED** | Bucket count differs because the realized horizon spans fewer calendar months; a coverage difference, not a reproducibility failure. |
| `buy_leg` | buys (win rate) | 73 (71%) | 8 (50.00%) | **RESOLVED_IN_CODE** | Constituent split is implemented and documented; buy-leg count is attribution granularity, and legs sum to the grand total. |
| `short_leg` | shorts (win rate) | 12 (83%) | 1 (0.00%) | **INTENTIONALLY_RETAINED** | n=1 observation; hedge separation explains the net-negative short. Not evidence for or against the spec's ~27% short contribution. |
| `rebound_short_attribution_correction` | rebound-short profit contribution | 27.0 | -17.87027158190707 | **RESOLVED_IN_CODE** | Authoritative attribution now separates coin leg from ETH hedge and sums to the grand total; the earlier reading is retracted in-artifact. |
| `universe_utilization` | universe | spec-relevant >= $5M set (~26 on Hyperliquid per spec; up to ~80 in 2024-2025) | 54 admitted / 5 traded | **RESOLVED_IN_CODE** | Every admitted symbol was loaded and evaluated; non-participation is fully attributed to zero signal-gate passes (no silent drop). |

## Evidence anchors

### `trade_frequency` — RESOLVED_IN_CODE

- `census_funnel={"bounce_confirmed": 39, "regime_min_price_ok": 89, "rsi_events": 342, "signal_gate_pass": 11, "trades_matched_to_census": 8, "trades_opened": 8, "volume_gate_pass": 187}`
- `blocking_reasons_sum=342`
- `unexplained_signal_gate_events=0`

### `annualization_horizon` — INTENTIONALLY_RETAINED

- `metrics: equity_annualized_return_pct derived from curve timestamps`
- `metrics: equity_horizon_years recorded alongside annualized return`
- `no fabricated 283d horizon: annualization requires >=2 curve timestamps`

### `drawdown_scale` — INTENTIONALLY_RETAINED

- `realized_max_drawdown_usd=-2091.6053422543337`
- `gross_cap_utilization_pct=100.0`
- `engine enforces gross cap + per-trade sizing (no silent change)`

### `monthly_breadth` — INTENTIONALLY_RETAINED

- `realized_month_buckets=7`
- `metrics: positive_months derived from the same monthly buckets`

### `buy_leg` — RESOLVED_IN_CODE

- `buy_trades=8`
- `trade_attribution_by_leg={"buy": {"leg": "buy", "pnl": 10796.55375971258, "trades": 8}, "short": {"leg": "short", "pnl": -1636.8618248296225, "trades": 1}}`
- `metrics: _split_leg_pnls splits rebound-short trades into buy/short constituents`

### `short_leg` — INTENTIONALLY_RETAINED

- `short_trades=1`
- `rebound_short_constituents={"rebound_hedge_pnl": -2704.591251, "rebound_short_pnl": 1067.729426}`

### `rebound_short_attribution_correction` — RESOLVED_IN_CODE

- `authoritative_leg_attribution={"buy": {"leg": "buy", "pnl": 10796.55375971258, "trades": 8}, "short": {"leg": "short", "pnl": -1636.8618248296225, "trades": 1}}`
- `metrics: rebound hedge PnL separated (rebound_hedge_pnl)`
- `metrics: _split_leg_pnls returns constituents summing to trade total`

### `universe_utilization` — RESOLVED_IN_CODE

- `universe_size=54`
- `symbols_traded=5`
- `never_traded_with_signal_pass=[]`

## Prohibition

No row here authorizes a strategy change. Any future code change must be opt-in and default-off, and must not silently alter the canonical baseline.

**Verdict:** `ALL_DIVERGENCES_ADJUDICATED`
