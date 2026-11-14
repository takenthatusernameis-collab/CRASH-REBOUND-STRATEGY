"""Tests for the reproducible Hyperliquid retention probe (anti-avoidance).

The blocker claim ("the public API cannot serve the full 283-day window") must be
reproducible from code, not asserted in prose. These tests lock the probe's
contract:
  - every count is derived from the API response, never hardcoded;
  - a full-window response flips the verdict (so a real full dataset cannot be
    blocked by a stale artifact);
  - a transient error is not silently recorded as a permanent block;
  - the written artifact carries the machine-checkable fields the gate reads.
"""
from __future__ import annotations

import json

import pytest

from scripts import probe_hyperliquid_blocker as probe


class _FakeResp:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _bars(n, start_ms=1_766_188_800_000, step_ms=3_600_000):
    return [{"t": start_ms + i * step_ms} for i in range(n)]


def _patch_url(monkeypatch, meta, candle_map, *, fail=None):
    """Patch http_json so no real network is touched.

    meta: metaAndAssetCtxs payload. candle_map: {symbol: bars or Exception}.
    fail: optional set of symbols whose requests always raise.
    """
    fail = fail or set()

    def fake_http_json(url, payload=None, timeout=30, retries=3):
        if payload is None:
            raise AssertionError("unexpected meta request")
        if payload.get("type") == "metaAndAssetCtxs":
            return meta
        req = payload["req"]
        sym = req["coin"]
        if sym in fail:
            raise RuntimeError(f"simulated outage for {sym}")
        return candle_map[sym]

    monkeypatch.setattr(probe, "http_json", fake_http_json)


def _meta(names_volumes):
    universe = [{"name": n} for n, _ in names_volumes]
    ctxs = [{"dayNtlVlm": str(v)} for _, v in names_volumes]
    return [{"universe": universe}, ctxs]


def test_blocked_window_records_missing_bars(monkeypatch):
    meta = _meta([("BTC", 9e9), ("ETH", 2e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900), "ETH": _bars(3900)})
    report = probe.build_probe(probe.HL_INFO_URL)
    summary = report["probe_summary"]
    assert summary["full_window_served"] is False
    assert summary["expected_hourly_bars"] == 6792
    assert summary["max_bars_returned"] == 3900
    assert summary["missing_early_bars_vs_expected"] == 6792 - 3900
    assert "BLOCKED" in report["verdict"]


def test_full_window_flips_verdict(monkeypatch):
    """If the API ever serves the whole window, the artifact must stop claiming a block."""
    meta = _meta([("BTC", 9e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(6792)})
    report = probe.build_probe(probe.HL_INFO_URL)
    assert report["probe_summary"]["full_window_served"] is True
    assert report["probe_summary"]["missing_early_bars_vs_expected"] == 0
    assert "SERVED" in report["verdict"]
    assert "run_real_campaign.py" in report["next_action"]


def test_volume_gate_filters_universe(monkeypatch):
    meta = _meta([("BTC", 9e9), ("TINY", 1_000.0), ("MID", 6e6)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900), "MID": _bars(3900)})
    report = probe.build_probe(probe.HL_INFO_URL)
    assert report["universe"]["perps_total"] == 3
    assert report["universe"]["perps_passing_volume_gate"] == 2
    probed = {r["symbol"] for r in report["per_symbol"]}
    assert probed == {"BTC", "MID"}


def test_transient_error_is_not_a_block(monkeypatch):
    """A symbol that errors must not be counted as evidence the window is blocked."""
    meta = _meta([("BTC", 9e9), ("ETH", 9e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900), "ETH": _bars(3900)},
               fail={"ETH"})
    report = probe.build_probe(probe.HL_INFO_URL)
    # BTC alone still shows a partial window; ETH is recorded as error, not "served".
    assert report["probe_summary"]["symbols_empty_or_error"] == ["ETH"]
    eth = next(r for r in report["per_symbol"] if r["symbol"] == "ETH")
    assert eth["status"] == "error"


def test_symbol_filter_and_limit(monkeypatch):
    meta = _meta([("BTC", 9e9), ("ETH", 9e9), ("SOL", 9e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900), "ETH": _bars(3900),
                                   "SOL": _bars(3900)})
    report = probe.build_probe(probe.HL_INFO_URL, symbols=["BTC"])
    assert [r["symbol"] for r in report["per_symbol"]] == ["BTC"]
    report2 = probe.build_probe(probe.HL_INFO_URL, limit=1)
    assert report2["universe"]["probed"] == 1


def test_written_artifact_has_gate_fields(tmp_path, monkeypatch):
    meta = _meta([("BTC", 9e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900)})
    out = tmp_path / "probe.json"
    report = probe.build_probe(probe.HL_INFO_URL)
    out.write_text(json.dumps(report))
    data = json.loads(out.read_text())
    for key in ("generated_at_utc", "probe_summary", "verdict", "target_window", "per_symbol"):
        assert key in data
    assert data["probe_summary"]["full_window_served"] is False


def test_requested_symbol_absent_from_universe_is_recorded(monkeypatch):
    meta = _meta([("BTC", 9e9)])
    _patch_url(monkeypatch, meta, {"BTC": _bars(3900)})
    report = probe.build_probe(probe.HL_INFO_URL, symbols=["BTC", "MATIC", "FTM"])
    assert report["universe"]["requested_not_in_live_universe"] == ["FTM", "MATIC"]


def test_expected_hourly_bars_is_inclusive():
    import datetime as dt
    start = probe.parse_utc(probe.SPEC_START)
    end = probe.parse_utc(probe.SPEC_END)
    assert probe.expected_hourly_bars(start, end) == 6792