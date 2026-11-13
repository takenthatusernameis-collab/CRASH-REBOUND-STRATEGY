"""Phase E (2026-11-13): reconcile volume gate to spec.

Spec universe is point-in-time (>= $5M 24h volume at decision). The whole-window-min
manifest gate (volume_filter_ok, every bar >= $5M) is stricter than spec and blocks
otherwise-valid alt universes. Reconciliation must:
- ADD universe_membership_ok = (peak rolling-24h USD volume >= $5M) for admission
- KEEP volume_filter_ok (all-bars) and per-trade point-in-time volume filtering
- Admit universe members with peak>=5M even if some bars dip below $5M
- Exclude symbols whose peak < $5M
- Never open a trade on a sub-$5M bar (generate_signal enforces point-in-time)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_hyperliquid_candles import analyze_symbol_volume_coverage
from scripts.run_real_campaign import validate_symbol_volume_coverage
from src.data.provenance import ProvenanceError
from src.strategy.crash_rebound import generate_signal


def _candles(prices_vols, start_ms=1_700_000_000_000):
    """prices_vols: list of (close, volume_base) per hour. high/low around close."""
    out = []
    for i, (close, vol) in enumerate(prices_vols):
        out.append({
            "timestamp_ms": start_ms + i * 3_600_000,
            "open": close,
            "high": close * 1.001,
            "low": close * 0.999,
            "close": close,
            "volume": vol,
        })
    return out


class TestAnalyzeSymbolVolumeCoverageMembership:
    def test_peak_ge_5m_but_some_sub_5m_bars_sets_membership_true_filter_false(self):
        # 30 bars: most bars give 24h USD vol well above $5M, but a few bars have
        # very low base volume so their trailing-24h sum dips below $5M.
        n = 30
        # normal: close 100, vol 3000 -> bar USD 300k, 24h ~7.2M
        pv = [(100.0, 3000.0)] * n
        # make a dip window: bars 10-12 near-zero volume so trailing windows around them drop
        for i in range(10, 13):
            pv[i] = (100.0, 0.0)
        candles = _candles(pv)
        vc = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        assert vc["volume_filter_ok"] is False, "all-bars flag must remain false when any bar < $5M"
        assert vc.get("universe_membership_ok") is True, "peak>=5M means symbol is a spec universe member"
        assert float(vc.get("observed_max_24h_usd_volume", 0)) >= 5_000_000.0
        assert float(vc["observed_min_24h_usd_volume"]) < 5_000_000.0

    def test_peak_below_5m_excluded_from_membership(self):
        # consistently low: 100 * 1000 = 100k/bar, 24h ~2.4M peak
        pv = [(100.0, 1000.0)] * 30
        candles = _candles(pv)
        vc = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        assert vc["volume_filter_ok"] is False
        assert vc.get("universe_membership_ok") is False
        assert float(vc.get("observed_max_24h_usd_volume", 0)) < 5_000_000.0

    def test_all_bars_pass_means_both_ok(self):
        # every trailing-24h window >= $5M: 300k/bar => need 24 bars in window to reach 7.2M,
        # so provide enough history that every computed window has 24 bars (bars_checked windows all pass)
        pv = [(100.0, 3000.0)] * 30  # 300k/bar, 24h ~7.2M; early windows <24 bars yield <5M
        candles = _candles(pv)
        vc = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        # early bars have short trailing windows (<24 bars) so their 24h sum is <5M
        assert vc["volume_filter_ok"] is False
        assert vc.get("universe_membership_ok") is True

        # true all-bars-pass case: large enough per-bar volume that even 1-bar window >= $5M
        pv2 = [(100.0, 60000.0)] * 30  # 6M/bar
        candles2 = _candles(pv2)
        vc2 = analyze_symbol_volume_coverage(candles2, 5_000_000.0)
        assert vc2["volume_filter_ok"] is True
        assert vc2.get("universe_membership_ok") is True
        assert vc2["bars_passing"] == vc2["bars_checked"]

    def test_membership_threshold_respects_spec_floor_semantics(self):
        # membership is spec-universe (>= $5M) peak concept
        pv = [(100.0, 3000.0)] * 30
        candles = _candles(pv)
        vc = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        assert "universe_membership_ok" in vc


def _manifest(sym="SOL", *, status="ok", complete=True, volume_filter_ok=False,
              universe_membership_ok=None, observed_min=1_261_922.0, observed_max=81_077_489.0,
              observed_mean=41_113_561.0, bars_passing=6789, bars_checked=6792):
    volcov = {
        "min_daily_volume_usd": 5_000_000.0,
        "observed_min_24h_usd_volume": observed_min,
        "observed_mean_24h_usd_volume": observed_mean,
        "bars_checked": bars_checked,
        "bars_passing": bars_passing,
        "volume_filter_ok": volume_filter_ok,
    }
    if universe_membership_ok is not None:
        volcov["universe_membership_ok"] = universe_membership_ok
    if observed_max is not None:
        volcov["observed_max_24h_usd_volume"] = observed_max
    return {
        "symbols": {
            sym: {
                "status": status,
                "coverage": {"complete_for_target_window": complete,
                             "expected_hourly_bars": 6792, "observed_in_window_bars": 6792 if complete else 0},
                "volume_coverage": volcov,
            }
        }
    }


class TestValidateSymbolVolumeCoverageAdmission:
    def test_admits_universe_member_with_peak_ge_5m_even_if_some_bars_sub_5m(self):
        m = _manifest(volume_filter_ok=False, universe_membership_ok=True,
                      observed_min=1_261_922.0, observed_max=81_077_489.0)
        passing = validate_symbol_volume_coverage(m, ["SOL"], 5_000_000.0)
        assert passing == ["SOL"]

    def test_excludes_symbol_with_peak_below_5m(self):
        m = _manifest(volume_filter_ok=False, universe_membership_ok=False,
                      observed_min=1_000_000.0, observed_max=2_400_000.0)
        with pytest.raises(ProvenanceError) as ei:
            validate_symbol_volume_coverage(m, ["SOL"], 5_000_000.0)
        msg = str(ei.value).lower()
        assert "sol" in msg
        assert "universe" in msg or "peak" in msg or "membership" in msg or "volume" in msg

    def test_admits_all_bars_passing_member(self):
        m = _manifest(volume_filter_ok=True, universe_membership_ok=True,
                      observed_min=6_670_000.0, observed_max=9_000_000.0,
                      bars_passing=6792, bars_checked=6792)
        assert validate_symbol_volume_coverage(m, ["SOL"], 5_000_000.0) == ["SOL"]

    def test_missing_membership_fields_falls_back_safely(self):
        # legacy/strict manifest with no membership key but all-bars ok should still pass
        m = _manifest(volume_filter_ok=True, universe_membership_ok=None,
                      observed_min=6_000_000.0, observed_max=None,
                      bars_passing=6792, bars_checked=6792)
        # either inferred from peak/observed_min or accepted because all-bars ok
        assert validate_symbol_volume_coverage(m, ["SOL"], 5_000_000.0) == ["SOL"]


class TestPerTradePointInTimeVolumeFilterUnchanged:
    def test_no_trade_signal_on_sub_5m_bar_even_if_universe_member(self):
        """Per-trade eligibility remains point-in-time: generate_signal must reject a
        bar whose trailing 24h USD volume < $5M, regardless of universe membership."""
        # Build bars: early period establishes high peak (>=5M), but trailing 24h at
        # decision bar is entirely sub-$5M.
        n = 70
        pv = [(100.0, 3000.0)] * n  # 300k/bar, any full 24h window ~7.2M
        # zero out last 24 bars so trailing-24h at decision bar is 0 (peak remains earlier)
        for j in range(n - 24, n):
            pv[j] = (100.0, 0.0)
        candles = _candles(pv)
        i = len(candles) - 1
        # Direct point-in-time check: compute trailing 24h USD vol at decision bar
        window = candles[max(0, i - 23): i + 1]
        trailing_24h = sum(c["close"] * c["volume"] for c in window)
        assert trailing_24h < 5_000_000.0, "test setup: decision bar must be sub-$5M"

        # Per-trade strategy filter must reject this bar (point-in-time, not peak).
        # passes_universe_filter / _daily_volume_usd enforces trailing-24h >= min on last bars.
        from src.strategy.crash_rebound import passes_universe_filter
        assert passes_universe_filter(candles[: i + 1], min_daily_volume_usd=5_000_000.0) is False

        # But the symbol can still be a universe member by peak (admission) — admission
        # does NOT permit trading on this sub-threshold bar.
        vc = analyze_symbol_volume_coverage(candles, 5_000_000.0)
        assert vc.get("universe_membership_ok") is True
        assert vc.get("volume_filter_ok") is False
        m = _manifest(volume_filter_ok=False, universe_membership_ok=True,
                      observed_min=0.0, observed_max=float(vc["observed_max_24h_usd_volume"]))
        assert validate_symbol_volume_coverage(m, ["SOL"], 5_000_000.0) == ["SOL"]
        # Admission != per-bar trade permission (per-trade filter is separate).
        assert passes_universe_filter(candles[: i + 1], min_daily_volume_usd=5_000_000.0) is False
