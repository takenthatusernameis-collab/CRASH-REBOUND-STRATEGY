# Hyperliquid-native 1h OHLCV archive (spec window)

- Window: `2025-12-20T00:00:00+00:00` .. `2026-09-28T23:00:00+00:00` (6792 hourly bars/symbol)
- Source: Ironflow Hugging Face dataset `ironflow/hyperliquid-candles-1h` (CC BY 4.0), hourly OHLCV for every Hyperliquid perp/spot, built from Ironflow's own Hyperliquid nodes; compared hour-by-hour with Hyperliquid's own candleSnapshot by the publisher.
- Native perps only (market_class=perp, no HIP-3 dex); HIP-3 and spot excluded.
- Symbols passing complete-coverage + $5M trailing-24h volume floor: 5
- Archive parquet sha256: `658ab040d947125b91517e0cb79363d8ed834f915950e81dc7617c30e3852f94`
- This is real, non-synthetic Hyperliquid market data. It is NOT the venue's own candleSnapshot endpoint and is NOT performance evidence.
