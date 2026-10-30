from __future__ import annotations

import json

from scripts.run_campaign import build_campaign_export
from src.strategy.config import StrategyConfig


def test_campaign_export_cannot_be_mistaken_for_historical_performance():
    fixtures = {
        "BTC": [{"timestamp": "2026-01-01T00:00:00", "close": 100.0}],
        "ETH": [
            {"timestamp": "2026-01-01T00:00:00", "close": 50.0},
            {"timestamp": "2026-01-01T01:00:00", "close": 51.0},
        ],
    }
    results = {
        "total_pnl": 12.5,
        "num_trades": 1,
        "final_open_positions": 0,
        "final_gross_exposure": 0.0,
        "trades": [{"symbol": "BTC", "total_pnl": 12.5}],
    }
    config = StrategyConfig()

    artifact = build_campaign_export(
        results, config, fixtures, "2026-10-30T00:00:00"
    )

    assert artifact["run_type"] == "fixture_smoke_test"
    assert artifact["research_status"] == "SMOKE_TEST_ONLY"
    assert artifact["data_provenance"]["kind"] == "synthetic_fixture"
    assert artifact["data_provenance"]["real_market_data"] is False
    assert artifact["data_provenance"]["fabricated_data"] is True
    assert artifact["data_provenance"]["performance_evidence"] is False
    assert artifact["data_provenance"]["target_historical_window"]["status"] == "NOT_RUN"
    assert artifact["data_provenance"]["target_historical_window"]["days"] == 283
    assert artifact["symbols"] == ["BTC", "ETH"]
    assert artifact["candle_counts_by_symbol"] == {"BTC": 1, "ETH": 2}
    assert artifact["config"]["use_rsi_trigger"] is True
    assert artifact["config"]["enable_volume_based_sizing"] is True

    # The exported artifact must remain machine-serializable without
    # losing or changing its explicit provenance declaration.
    encoded = json.dumps(artifact)
    decoded = json.loads(encoded)
    assert decoded["data_provenance"] == artifact["data_provenance"]


def test_campaign_export_preserves_fixture_trade_payload_without_relabeling_as_market_data():
    fixtures = {"SPY": [{"timestamp": "2026-01-01T00:00:00", "close": 100.0}]}
    results = {
        "total_pnl": -2.0,
        "num_trades": 1,
        "final_open_positions": 0,
        "final_gross_exposure": 0.0,
        "trades": [{"symbol": "SPY", "total_pnl": -2.0}],
    }

    artifact = build_campaign_export(results, StrategyConfig(), fixtures, "fixture-run")

    assert artifact["results"] == results
    assert artifact["data_provenance"]["performance_evidence"] is False
