# Robustness / Signal-vs-Noise — Real OKX 283-Day Campaign (Phase L)

**Generated (UTC):** 2026-11-13T18:31:30.039652+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

This is the Phase L gate: it characterizes whether the 8-trade canonical result is distinguishable from luck. It does not establish future profitability. Every statistic is derived deterministically (seed=20261113, 10000 bootstrap resamples) from the canonical trade set (8 trades).

## Go / no-go conclusion: **UNDERPOWERED**

P(total PnL > 0) is 0.9633 but the bootstrap 95% CI still crosses zero [-930.66, 19,152.38]; the sample is too small to separate signal from luck at decision grade.

## Trade-level bootstrap

- Resamples: 10000 (seed 20261113), with-replacement over realized trade total_pnl
- Observed total PnL: 9,159.69
- 95% CI total PnL: [-930.66, 19,152.38]
- 95% CI total return on 100,000: [-0.9307%, 19.1524%]
- P(total PnL > 0): 0.9633
- Observed win rate: 0.5000 (95% CI [0.1250, 0.8750])
- Profit factor: observed 5.233524, 95% CI [0.802, 114.554]
- Limitation: Bootstrap over 8 realized trades cannot manufacture information that is not in the sample; the interval is wide and reflects resampling noise, not a guarantee of future performance.

## Sign-flip permutation test

- Combinations: 256 (2^8)
- Observed total: 9,159.69
- p_value (one-sided, >= observed): 0.0938 — fraction of 2^n sign-flip totals >= observed total (one-sided)
- p_value (two-sided, |total| >= |observed|): 0.1875
- Sign-flipped total range: [-13,486.91, 13,486.91]

## Concentration

| Symbol | Trades | PnL | Share |
|---|---|---|---|
| SOL | 3 | 4,667.11 | 0.5095 |
| AVAX | 1 | 3,499.37 | 0.3820 |
| BCH | 2 | 2,916.22 | 0.3184 |
| ETH | 1 | -121.63 | -0.0133 |
| LINK | 1 | -1,801.38 | -0.1967 |

- Top symbol PnL share: 0.5095
- Top trade |PnL| share of total: 0.3820
- HHI: 0.5458 (effective symbols 1.832212)

## Time split and activity

- First half PnL: 1,070.36 (4 trades, ['ETH', 'LINK', 'SOL'])
- Second half PnL: 8,089.33 (4 trades, ['AVAX', 'BCH', 'SOL'])
- Realized span: 119.50 days (0.3272 yr), 2026-01-20T22:00:00+00:00 .. 2026-05-20T10:00:00+00:00

| Month (UTC) | Trades | PnL |
|---|---|---|
| 2026-01 | 4 | 1,070.36 |
| 2026-02 | 3 | 8,161.33 |
| 2026-05 | 1 | -72.00 |

- Annualization uses the realized trade span, not the full 283-day window; there is a multi-month no-trade tail after the last exit.

## Placebo / absence check

Compare the J1 crash-event census funnel (crashes -> volume_gate_pass -> bounce_confirmed -> regime_min_price_ok -> signal_gate_pass -> trades) to the realized trade set; every signal-gate event that did not become a trade is an absence the strategy must explain.

- J1 funnel: 342 crashes → volume 187 → bounce 39 → regime 89 → signal 11 → trades 8; unexplained signal-gate events: 0
- Signal-gate events not traded: 3 of 11
- Absence blocking-reason counts: {"one_position_per_coin": 3}
- The census is the absence ledger: signal-gate events that did not become trades are recorded with their blocking reason; no unseen data is fabricated.

## Caveats

- Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
- 8 realized trades is a small sample; the bootstrap quantifies resampling uncertainty, not out-of-sample performance.
- Realized-horizon annualization only; a multi-month no-trade tail follows the last exit, so do not annualize the full 283-day window.
- This is an evidence-chain and signal-vs-noise check, not proof of future profitability.
