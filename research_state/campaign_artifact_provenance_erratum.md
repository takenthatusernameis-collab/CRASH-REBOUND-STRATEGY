# Campaign artifact provenance note — 30 October 2026

The committed `research_state/campaign_results.json` predates this correction. It records a three-trade SPY/QQQ/IWM result with `use_rsi_trigger=false` and does not contain a verified 283-day Hyperliquid market-data sample. It must not be interpreted as the specified historical campaign or as evidence for the PDF's reported performance.

The current `scripts/run_campaign.py` runner is explicitly a synthetic fixture smoke test. Its export now declares:

- `run_type=fixture_smoke_test`
- `research_status=SMOKE_TEST_ONLY`
- `real_market_data=false`
- `performance_evidence=false`
- the target 2025-12-20 through 2026-09-28 (283-day) window as `NOT_RUN`

The current default `StrategyConfig` has RSI(21)<20 enabled and volume-based sizing enabled. The fixture runner explicitly enables those controls as well. Its three-candle fixtures are not long enough to satisfy the 22-close RSI warmup, so a lack of entries is expected and is not a strategy failure or a historical result.

No replacement historical dataset is claimed. The actual 283-day Hyperliquid campaign remains NOT RUN pending verifiable, sufficiently complete hourly market data and independently documented data provenance.
