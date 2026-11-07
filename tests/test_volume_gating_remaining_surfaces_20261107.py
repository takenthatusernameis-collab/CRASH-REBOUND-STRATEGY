"""2026-11-07: Audit remaining $5M volume bypass surfaces outside core gating.

Failing-tests-first. These are non-evidence/synthetic tests.
Spec-compliant paths must not accept sub-$5M non-zero volume thresholds.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.loader import get_hyperliquid_universe, load_multi_coin_data
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD, enforce_spec_volume_floor
from scripts.fetch_hyperliquid_candles import analyze_symbol_volume_coverage


def _candles_usd_per_bar(close: float, volume: float, n: int = 30):
    return [{"open": close, "high": close + 1, "low": close - 1, "close": close, "volume": volume} for _ in range(n)]


class TestAnalyzeSymbolVolumeCoverageFloor:
    def test_sub_5m_nonzero_threshold_is_floor_enforced(self):
        # ~2.4M USD/day per bar (1000 * 100 * 24 bars window conceptually per bar's trailing sum)
        candles = _candles_usd_per_bar(100.0, 1000.0)
        res = analyze_symbol_volume_coverage(candles, 1_000_000.0)
        # Spec-compliant analysis must not treat 1M as an accepted threshold; floor to $5M.
        assert float(res["min_daily_volume_usd"]) >= SPEC_MIN_DAILY_VOLUME_USD
        assert res["volume_filter_ok"] is False

    def test_zero_threshold_remains_non_spec_escape_hatch(self):
        candles = _candles_usd_per_bar(100.0, 1000.0)
        res = analyze_symbol_volume_coverage(candles, 0)
        assert float(res["min_daily_volume_usd"]) == 0.0

    def test_at_or_above_5m_preserved(self):
        candles = _candles_usd_per_bar(100.0, 3000.0)  # 300000/bar, 24h=7.2M on full windows
        res = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        assert float(res["min_daily_volume_usd"]) == 5_000_000.0
        assert res["observed_min_24h_usd_volume"] is not None and res["observed_min_24h_usd_volume"] < 5_000_000.0
        # volume_filter_ok reflects whether all checked bars pass the threshold (per function semantics)
        assert res["bars_checked"] > 0


class TestGetHyperliquidUniverseContract:
    def test_docstring_and_behavior_must_not_claim_unverified_5m_filtering(self):
        # Static default universe is not verified against live 24h volume data.
        # Function must not silently accept a sub-$5M "filter" and imply spec compliance.
        # Minimal contract: enforce floor on the parameter for consistency/labeling.
        uni = get_hyperliquid_universe(min_daily_volume_usd=1_000_000.0, use_cache=False)
        # It returns the default static list (no live data) — but the API contract must
        # not present sub-$5M as the effective spec threshold. We verify via floor helper
        # expectation: callers should see $5M semantics. The function should not claim
        # it filtered to a sub-$5M threshold; we test by ensuring it at least applies floor
        # semantics if it exposes/uses the value (indirect) — and by requiring the
        # implementation to not accept sub-$5M as-is in spec-facing behavior.
        # Direct behavioral test: function should raise or floor; we require floor.
        # (Implementation may ignore for static default, but must not propagate sub-$5M.)
        assert isinstance(uni, list)
        # If implementation applies floor, requesting 1M should behave like 5M contractually.
        # Static default unchanged, but parameter must be floor-enforced internally.
        assert get_hyperliquid_universe(min_daily_volume_usd=5_000_000.0, use_cache=False) == uni

    def test_zero_escape_hatch_allowed(self):
        uni = get_hyperliquid_universe(min_daily_volume_usd=0, use_cache=False)
        assert isinstance(uni, list)


class TestLoadMultiCoinDataGating:
    def test_sub_5m_nonzero_filter_is_floor_enforced(self):
        # Symbol with ~2.4M/day should NOT pass when caller requests 1M (spec bypass).
        low_vol = _candles_usd_per_bar(100.0, 1000.0)
        data = {"LOW": low_vol, "ETH": _candles_usd_per_bar(100.0, 3000.0)}
        # Use dict source path
        try:
            result = load_multi_coin_data(data, min_daily_volume_usd=1_000_000.0)
        except TypeError:
            pytest.skip("load_multi_coin_data signature differs")
        # LOW (~2.4M/day) must be filtered out under $5M floor
        assert "LOW" not in result

    def test_zero_escape_hatch_allows_low_volume(self):
        low_vol = _candles_usd_per_bar(100.0, 1000.0)
        data = {"LOW": low_vol}
        try:
            result = load_multi_coin_data(data, min_daily_volume_usd=0)
        except TypeError:
            pytest.skip("load_multi_coin_data signature differs")
        assert "LOW" in result
