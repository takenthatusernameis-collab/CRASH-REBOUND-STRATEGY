#!/usr/bin/env python3
"""Fail-closed entry point for the historical Crash-Rebound campaign.

The former implementation ran three-bar SPY/QQQ/IWM fixtures plus a synthetic
ETH proxy and wrote those results to campaign_results.json while labelling the
output a 283-day Hyperliquid campaign. That is not a valid historical
backtest. The chronological, multi-asset execution engine and verified
Hyperliquid candle panel required by the specification are not available in
this runner yet.

Use the fixture helpers only for unit/integration tests. This command refuses
to create or overwrite campaign performance evidence until a verified,
chronological historical runner is implemented.
"""


def main() -> None:
    raise SystemExit(
        "REFUSED: scripts/run_campaign.py is not a valid historical campaign "
        "runner. The previous version used synthetic SPY/QQQ/IWM fixtures and "
        "a synthetic ETH proxy, evaluated at most one signal per asset, and "
        "wrote campaign_results.json. No historical performance artifact was "
        "written. A valid campaign requires verified Hyperliquid hourly "
        "candles, point-in-time eligibility and a chronological portfolio "
        "engine that processes every bar and concurrent position."
    )


if __name__ == "__main__":
    main()
