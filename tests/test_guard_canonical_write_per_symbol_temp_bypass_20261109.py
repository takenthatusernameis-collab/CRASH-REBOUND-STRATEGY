"""Fail-closed: guard_canonical_write must reject temp/unverified per-symbol provenance paths.

2026-11-09 D-bypass hunt (failing-tests-first). guard_canonical_write scans
archive keys on probe/manifest containers but not per-symbol provenance path
fields. A manifest can have clean symbol coverage/synthetic facts while carrying
temp per-symbol source/cache metadata (cache_path, source_path, source_paths,
archive_path/input_archive nested under symbol or symbol.source/provenance).
Such a manifest must not clobber the canonical gap report as ready.
"""
from __future__ import annotations

from scripts.generate_candle_coverage_gap_report import build_gap_report, guard_canonical_write
from src.data.provenance import TARGET_START, TARGET_END, expected_hourly_bars

EXP = expected_hourly_bars(TARGET_START, TARGET_END)
TEMP = "/home/runner/work/_temp/kilo-tmp/fake.parquet"
CLEAN = "/mnt/data/verified/clean.parquet"


def _clean(extra=None):
    d = {
        "status": "ok",
        "synthetic_check": {"is_synthetic": False},
        "coverage": {
            "expected_hourly_bars": EXP,
            "observed_in_window_bars": EXP,
            "complete_for_target_window": True,
            "gap_count": 0,
        },
    }
    if extra:
        d.update(extra)
    return d


def _manifest(symbols_extra=None):
    symbols_extra = symbols_extra or {}
    symbols = {"BTC": _clean(symbols_extra.get("BTC")), "ETH": _clean(symbols_extra.get("ETH"))}
    return {
        "generated_at_utc": "2026-11-09T00:00:00Z",
        "fabricated_data": False,
        "target_window": {"start": TARGET_START, "end": TARGET_END, "expected_hourly_bars": EXP},
        "source": {"kind": "archive", "input_archive": CLEAN},
        "summary": {"all_complete": True, "ready_for_real_campaign": True,
                    "complete_symbols": ["BTC", "ETH"], "symbols_requested": 2},
        "symbols": symbols,
    }


def _assert_blocked(report):
    assert report["ready_for_real_campaign"] is False
    assert report["blocked"] is True
    assert report["item_6c_blocked"] is True
    assert "provenance not verified-clean" in report["blocker"]["reason"]


def _guard(manifest):
    report = build_gap_report(manifest=manifest, probe_evidence=None, generated_at_utc="2026-11-09T00:01:00Z")
    # build_gap_report reasons from coverage facts; the guard must still block temp per-symbol provenance.
    assert report["ready_for_real_campaign"] is True
    return guard_canonical_write(dict(report), manifest)


def test_blocks_temp_cache_path_on_symbol():
    _assert_blocked(_guard(_manifest({"BTC": {"cache_path": "/tmp/fake_cache/BTC.json"}})))


def test_blocks_temp_source_path_on_symbol():
    _assert_blocked(_guard(_manifest({"BTC": {"source_path": TEMP}})))


def test_blocks_temp_source_paths_list_on_symbol():
    _assert_blocked(_guard(_manifest({"ETH": {"source_paths": [CLEAN, "/tmp/other.parquet"]}})))


def test_blocks_temp_archive_path_nested_under_symbol_source():
    _assert_blocked(_guard(_manifest({"BTC": {"source": {"input_archive": TEMP}}})))


def test_blocks_temp_input_archives_nested_under_symbol_provenance():
    _assert_blocked(_guard(_manifest({"BTC": {"provenance": {"input_archives": [TEMP]}}})))


def test_allows_clean_or_repo_relative_per_symbol_paths():
    m = _manifest({
        "BTC": {"cache_path": "research_state/cache/hyperliquid/candles/BTC.json",
                "source_path": CLEAN, "source": {"input_archive": CLEAN}},
        "ETH": {"source_paths": [CLEAN], "provenance": {"input_archives": [CLEAN]}},
    })
    guarded = _guard(m)
    assert guarded["ready_for_real_campaign"] is True
    assert guarded["blocked"] is False
