from __future__ import annotations

from pathlib import Path

from scripts.build_crash_event_census import (
    REASON_ORDER,
    _rsi_series,
    build_census,
    parse_timestamp_ms,
)
from src.strategy.crash_rebound import _rsi

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"


def test_rsi_series_matches_reference_rsi() -> None:
    closes = [10.0, 10.5, 10.2, 9.8, 9.1, 8.4, 8.0, 8.6, 9.4, 10.1, 10.8, 11.2]
    series = _rsi_series(closes, period=5)
    for i in range(len(closes)):
        reference = _rsi(
            [{"close": c} for c in closes[: i + 1]],
            period=5,
        )
        assert series[i] == reference, f"prefix {i}: {series[i]} != {reference}"


def _census():
    return build_census(
        STATE / "cache/okx_1h_full_20251220_20260928/provenance.json",
        STATE / "cache/okx_1h_full_20251220_20260928",
        STATE / "universe_okx_full_verified.json",
        STATE / "campaign_results_real_okx_full.json",
        21,
        20.0,
        5_000_000.0,
    )


def test_census_reconciles_every_event_to_exactly_one_reason() -> None:
    report = _census()
    rec = report["reconciliation"]

    assert report["missing_symbols"] == []
    assert report["hash_mismatches"] == []
    assert report["universe_size"] == 54

    events = report["events"]
    assert len(events) == rec["events_total"]
    assert rec["blocking_reasons_sum"] == rec["events_total"]

    for event in events:
        assert event["blocking_reason"] in REASON_ORDER
        assert event["rsi"] < report["params"]["rsi_threshold"]
        assert event["bar_timestamp_ms"] is not None

    counts = rec["blocking_reason_counts"]
    for reason, count in counts.items():
        assert reason in REASON_ORDER
        assert count == sum(1 for e in events if e["blocking_reason"] == reason)


def test_census_matches_every_campaign_trade_without_unexplained_drops() -> None:
    report = _census()
    rec = report["reconciliation"]

    assert rec["trades_in_campaign"] == 8
    assert rec["trades_matched_to_events"] == 8
    assert rec["unmatched_campaign_trades"] == []
    assert rec["unexplained_signal_gate_events"] == 0
    assert rec["signal_gate_pass"] >= rec["trades_matched_to_events"]


def test_census_baseline_funnel_is_locked() -> None:
    report = _census()
    rec = report["reconciliation"]

    assert rec["events_total"] == 342
    assert rec["volume_gate_pass"] == 187
    assert rec["bounce_confirmed"] == 39
    assert rec["signal_gate_pass"] == 11
    assert rec["blocking_reason_counts"] == {
        "volume_gate": 155,
        "bounce_not_confirmed": 159,
        "regime_min_price": 17,
        "one_position_per_coin": 3,
        "trade_opened": 8,
    }


def test_parse_timestamp_ms_supports_epoch_and_iso8601() -> None:
    assert parse_timestamp_ms(1768791600000) == 1768791600000
    assert parse_timestamp_ms("1768791600000") == 1768791600000
    assert parse_timestamp_ms("2026-01-19T04:00:00+00:00") == 1768795200000
    assert parse_timestamp_ms("2026-01-19T04:00:00Z") == 1768795200000
    assert parse_timestamp_ms(None) is None
    assert parse_timestamp_ms("not_a_ts") is None


def test_census_native_hyperliquid_reconciles_all_six_trades() -> None:
    report = build_census(
        STATE / "cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json",
        STATE / "cache/hyperliquid_ironflow_native_20251220_20260928",
        STATE / "universe_hyperliquid_ironflow_native_20251220_20260928.json",
        STATE / "campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json",
        21,
        20.0,
        5_000_000.0,
    )
    rec = report["reconciliation"]
    assert report["missing_symbols"] == []
    assert report["hash_mismatches"] == []
    assert rec["events_total"] == 43
    assert rec["signal_gate_pass"] == 7
    assert rec["trades_in_campaign"] == 6
    assert rec["trades_matched_to_events"] == 6
    assert rec["unmatched_campaign_trades"] == []
    assert rec["unexplained_signal_gate_events"] == 0
    assert rec["blocking_reason_counts"] == {
        "bounce_not_confirmed": 36,
        "one_position_per_coin": 1,
        "trade_opened": 6,
    }


def test_census_rejects_sub_spec_volume_floor() -> None:
    import pytest

    from src.data.provenance import ProvenanceError

    with pytest.raises(ProvenanceError):
        build_census(
            STATE / "cache/okx_1h_full_20251220_20260928/provenance.json",
            STATE / "cache/okx_1h_full_20251220_20260928",
            STATE / "universe_okx_full_verified.json",
            STATE / "campaign_results_real_okx_full.json",
            21,
            20.0,
            0.0,
        )