"""Boundary audit: no portfolio/report/loader path labels verified universe optimistically.

Campaign item 3/4 residual (HANDOFF.md 2026-11-07): confirm no remaining
portfolio/report/loader boundary labels verified universe optimistically
without provenance/manifest intent checks.

Failing-tests-first regression guardrails. Each assertion encodes a boundary
property that must not regress: selection/volume gating is computed from
verified data + provenance floor enforcement only; manifest status/complete
and volume-filter flags are never treated as optimistic volume evidence by
non-gated consumers.
"""
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.loader import get_hyperliquid_universe
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict
from scripts.derive_verified_universe import main as derive_main, max_rolling_24h_quote_volume
from scripts.run_campaign import build_campaign_export
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD, StrategyConfig
from src.strategy.crash_rebound import filter_universe


def _candles(close: float = 100.0, volume: float = 3000.0, n: int = 30):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [
        {"timestamp_ms": int((base + timedelta(hours=i)).timestamp() * 1000),
         "timestamp": (base + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "open": close + i * 0.01, "high": close + i * 0.01 + 1, "low": close + i * 0.01 - 1,
         "close": close + i * 0.01, "volume": volume}
        for i in range(n)
    ]


class TestDeriveVerifiedUniverseReaderNoOptimisticVolumeLabel:
    """derive_verified_universe.py reader path: selection is computed-volume from
    verified caches only; manifest status/complete are informational; never
    volume-optimistic labeling."""

    def test_selection_is_computed_volume_not_manifest_status(self):
        vol = max_rolling_24h_quote_volume(_candles(volume=3000.0, n=30))
        assert float(vol["max_rolling_24h_quote_volume_usd_proxy"]) >= SPEC_MIN_DAILY_VOLUME_USD
        assert vol["passes_5m_any_24h_window"] is True

    def test_output_never_claims_performance_evidence_from_manifest(self, tmp_path, monkeypatch):
        # Manifest claims all_complete=true but carries NO volume_coverage: the
        # reader must not derive volume/performance evidence from manifest status.
        cache_dir = tmp_path / "cache" / "hyperliquid"
        (cache_dir / "candles").mkdir(parents=True)
        candles = _candles(volume=3000.0, n=30)
        (cache_dir / "candles" / "BTC.json").write_text(json.dumps(candles))
        manifest = {
            "generated_at_utc": "2026-11-07T00:00:00Z",
            "fabricated_data": False,
            "real_market_data_intended": True,
            "target_window": {"start": "2025-12-20T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
            "summary": {"all_complete": True, "ready_for_real_campaign": True},
            "symbols": {
                "BTC": {
                    "status": "ok",
                    "cache_path": str(cache_dir / "candles" / "BTC.json"),
                    # no volume_coverage: reader must not treat status/complete as volume evidence
                    "coverage": {
                        "complete_for_target_window": True,
                        "expected_hourly_bars": 2,
                        "observed_in_window_bars": 2,
                        "gap_count": 0,
                    },
                }
            },
        }
        mp = tmp_path / "manifest.json"
        mp.write_text(json.dumps(manifest))
        out = tmp_path / "universe.json"

        monkeypatch.setattr(sys, "argv", [
            "derive_verified_universe.py",
            "--manifest", str(mp),
            "--cache-dir", str(cache_dir),
            "--output", str(out),
            "--min-24h-volume-usd", "5000000",
        ])
        with pytest.raises(SystemExit):
            derive_main()


class TestPortfolioRunnerNoProvenanceConsumption:
    """run_portfolio.run_portfolio_simulation is fixture-driven; accepts no
    manifest/provenance/volume fields; consumes no volume_filter_ok/observed-min/intent."""

    def test_runner_accepts_no_manifest_or_provenance_fields(self):
        import inspect
        sig = inspect.signature(run_portfolio_simulation)
        assert set(sig.parameters) <= {"candles_by_symbol", "config", "capital", "eth_candles"}, sig.parameters
        fixtures = {"BTC": _candles(volume=3000.0, n=30), "ETH": _candles(volume=3000.0, n=30)}
        config = StrategyConfig(use_rsi_trigger=False, enable_rebound_short=True)
        res = run_portfolio_simulation(fixtures, config=config, capital=100000.0,
                                       eth_candles={"ETH": _candles(volume=3000.0, n=30)})
        assert "total_pnl" in res and "trades" in res
        # No provenance/manifest/volume fields leak into the result shape.
        for t in res["trades"]:
            assert "volume_filter_ok" not in t
            assert "observed_min_24h_usd_volume" not in t


class TestCampaignMetricsNoProvenanceConsumption:
    """src.metrics.campaign_metrics computes from trades/equity_curve only;
    no provenance/manifest/volume consumption."""

    def test_metrics_ignore_provenance_volume_kwargs(self):
        trades = [
            {"exit_timestamp": "2026-01-01T00:00:00Z", "total_pnl": 100.0, "pnl": 100.0,
             "symbol": "BTC", "side": "long"},
            {"exit_timestamp": "2026-01-02T00:00:00Z", "total_pnl": -50.0, "pnl": -50.0,
             "symbol": "BTC", "side": "long"},
        ]
        m = metrics_to_dict(compute_campaign_metrics(trades=trades,
                                                     volume_filter_ok=True,
                                                     min_daily_volume_usd=1.0,
                                                     manifest={"symbols": {}}))
        assert m["win_rate"] == 0.5
        assert "volume_filter_ok" not in m and "min_daily_volume_usd" not in m
        assert "manifest" not in m


class TestRunCampaignFixtureExplicitlyNonEvidence:
    """run_campaign.build_campaign_export is explicitly synthetic smoke output:
    fabricated_data=True, real_market_data=False, performance_evidence=False."""

    def test_build_export_never_claims_evidence(self):
        config = StrategyConfig(min_daily_volume_usd=5_000_000.0)
        fixtures = {"BTC": _candles(volume=3000.0, n=30)}
        results = {"total_pnl": 0.0, "num_trades": 0, "trades": [], "equity_curve": [],
                   "final_open_positions": 0, "final_gross_exposure": 0.0}
        export = build_campaign_export(results, config, fixtures, "2026-11-07T00:00:00Z")
        assert export["data_provenance"]["fabricated_data"] is True
        assert export["data_provenance"]["real_market_data"] is False
        assert export["data_provenance"]["performance_evidence"] is False
        assert export["research_status"] == "SMOKE_TEST_ONLY"


class TestLoaderGetHyperliquidUniverseNonVerified:
    """loader.get_hyperliquid_universe is a static default list, not a verified
    live >= $5M universe filter; must not be treated as spec-compliant gating."""

    def test_static_default_universe_not_live_verified(self):
        uni = get_hyperliquid_universe(min_daily_volume_usd=1_000_000.0, use_cache=False)
        assert isinstance(uni, list) and len(uni) > 0
        assert get_hyperliquid_universe(min_daily_volume_usd=5_000_000.0, use_cache=False) == uni
        assert get_hyperliquid_universe(min_daily_volume_usd=0, use_cache=False) == uni


class TestFilterUniverseFloorEnforced:
    """Core gating filter_universe floors sub-$5M nonzero thresholds."""

    def test_sub_5m_nonzero_threshold_floored(self):
        low = _candles(volume=1000.0, n=30)  # ~2.4M/day
        data = {"LOW": low, "ETH": _candles(volume=3000.0, n=30)}
        passed = filter_universe(data, min_daily_volume_usd=1_000_000.0)
        assert "LOW" not in passed
        assert "ETH" in passed
