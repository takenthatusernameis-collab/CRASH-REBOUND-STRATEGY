# Hyperliquid-native Ironflow wide archive (C14-T1)

- Window: `2025-12-20T00:00:00Z` .. `2026-09-28T23:00:00Z` (6792 hourly bars/symbol)
- Source: Ironflow Hugging Face dataset `ironflow/hyperliquid-candles-1h` (CC BY 4.0), hourly OHLCV built from Ironflow's own Hyperliquid nodes; compared hour-by-hour with Hyperliquid's own candleSnapshot by the publisher.
- Native perps only (market_class=perp, dex empty); HIP-3 builder dexes and spot excluded.
- Native perp symbols in window: 198; complete-coverage symbols: 148.
- Real, non-synthetic Hyperliquid market data. NOT the venue's own candleSnapshot endpoint. NOT performance evidence.
