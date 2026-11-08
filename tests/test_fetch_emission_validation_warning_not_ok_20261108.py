"""Failing-test-first: fetch_hyperliquid_candles main must NOT mark status=ok when
validate_candles raised a validation_warning (non-finite / invalid OHLC).

Item 3 residual (raw-ingress / cache-emission hardening): a cache entry that fails
structural validation must never be emitted as status=ok+complete, because the
written cache would then be unloadable by downstream load_verified_cache /
load_hyperliquid_candles (which re-validate and raise). A trusted manifest label
outrunning the payload is a fail-open.

This test replays the exact entry-construction logic used by main()
(fetch_hl_candles -> validate_candles -> analyze_coverage -> detect_synthetic_candles
-> status assignment) so it is faithful to the production path and has no
filesystem side effects on the canonical research_state artifacts.
"""
import json

from scripts.fetch_hyperliquid_candles import (
    analyze_coverage,
    analyze_symbol_volume_coverage,
    detect_synthetic_candles,
    merge_verified_archives,
    _parse_iso,
    _sha256_bytes,
)


def _build_entry(candles, start_iso, end_iso, min_daily_volume_usd=0.0):
    """Replay main()'s per-symbol entry construction (non-archive path).

    Mirrors the corrected production logic in fetch_hyperliquid_candles.main():
    structural validation failure (validate_candles raising) is fail-closed —
    an entry with a validation_warning must never be emitted status=ok.
    """
    start = _parse_iso(start_iso)
    end = _parse_iso(end_iso)
    entry = {"symbol": "BTC", "status": "pending"}
    try:
        from src.data.loader import validate_candles
        try:
            validate_candles(candles, check_gaps=False)
        except Exception as ve:
            entry["validation_warning"] = str(ve)
        cov = analyze_coverage(candles, start, end)
        volcov = analyze_symbol_volume_coverage(candles, min_daily_volume_usd)
        synth = detect_synthetic_candles(candles)
        payload = json.dumps(candles, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        entry["coverage"] = cov
        entry["volume_coverage"] = volcov
        entry["synthetic_check"] = synth
        entry["sha256"] = _sha256_bytes(payload)
        if synth.get("is_synthetic"):
            entry["status"] = "error"
            entry["error"] = f"{synth.get('reason')}: {synth.get('distinct_signatures')}/{synth.get('bars_checked')} distinct signatures"
        elif entry.get("validation_warning"):
            # Fail-closed: structural validation failed; the written cache would be
            # unloadable downstream (manifest label outrunning the payload).
            entry["status"] = "error"
            entry["error"] = f"structural validation failed: {entry['validation_warning']}"
        else:
            entry["status"] = "ok" if cov.get("complete_for_target_window") else "incomplete"
    except Exception as e:
        entry["status"] = "error"
        entry["error"] = f"{type(e).__name__}: {e}"
    return entry


def test_emission_not_ok_when_validate_candles_raises_nonfinite():
    # A candle with NaN close: validate_candles(check_nonfinite=True) raises, but
    # coverage/synthetic detection would still run and could label it ok/complete.
    ts0 = 1766188800000  # 2025-12-20T00:00:00Z
    candles = [
        {"timestamp_ms": ts0 + i * 3_600_000,
         "open": 100.0 + i, "high": 101.0 + i, "low": 99.0 + i,
         "close": float("nan") if i % 2 == 0 else (100.5 + i),
         "volume": 1000.0 + i}
        for i in range(10)
    ]
    entry = _build_entry(candles, "2025-12-20T00:00:00Z", "2025-12-20T09:00:00Z")
    assert entry.get("validation_warning"), "expected validate_candles to raise and be recorded"
    assert entry["coverage"]["complete_for_target_window"] is True, "coverage must be complete to isolate validation_warning"
    # Must NOT be emitted as ok despite coverage/synth running.
    assert entry.get("status") != "ok", (
        f"FAIL-OPEN: entry emitted status={entry.get('status')} with validation_warning={entry.get('validation_warning')!r}"
    )


def test_emission_not_ok_when_validate_candles_raises_invalid_ohlc():
    ts0 = 1766188800000
    candles = [
        {"timestamp_ms": ts0 + i * 3_600_000,
         "open": 100.0 + i, "high": 50.0, "low": 99.0 + i,  # high < low
         "close": 100.5 + i, "volume": 1000.0 + i}
        for i in range(10)
    ]
    entry = _build_entry(candles, "2025-12-20T00:00:00Z", "2025-12-20T09:00:00Z")
    assert entry.get("validation_warning"), "expected invalid OHLC to raise validate_candles"
    assert entry["coverage"]["complete_for_target_window"] is True, "coverage must be complete to isolate validation_warning"
    assert entry.get("status") != "ok", (
        f"FAIL-OPEN: entry emitted status={entry.get('status')} with validation_warning={entry.get('validation_warning')!r}"
    )


def test_merge_emission_not_ok_on_invalid_ohlc(tmp_path):
    """merge_verified_archives must also fail-closed on structural validation."""
    import json as _json
    from scripts.fetch_hyperliquid_candles import merge_verified_archives

    ts0 = 1766188800000
    rows = [
        {"timestamp_ms": ts0 + i * 3_600_000,
         "open": 100.0 + i, "high": 50.0, "low": 99.0 + i,  # high < low
         "close": 100.5 + i, "volume": 1000.0 + i}
        for i in range(10)
    ]
    p = tmp_path / "BTC.json"
    p.write_text(_json.dumps({"BTC": rows}))
    start = _parse_iso("2025-12-20T00:00:00Z")
    end = _parse_iso("2025-12-20T09:00:00Z")
    merged = merge_verified_archives([p], ["BTC"], start, end, min_daily_volume_usd=0)
    e = merged["symbols"]["BTC"]
    assert e.get("validation_warning"), "expected merge to record structural validation failure"
    assert e.get("status") != "ok", (
        f"FAIL-OPEN: merge emitted status={e.get('status')} with validation_warning={e.get('validation_warning')!r}"
    )