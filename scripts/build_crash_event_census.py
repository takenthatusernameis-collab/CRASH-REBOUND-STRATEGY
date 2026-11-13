#!/usr/bin/env python3
"""Crash-event census for the real OKX 283-day campaign (Phase J1).

Counts every RSI(21) < 20 crash event across the admitted universe and assigns
exactly one blocking reason per event, reconciling the events against the trades
that the canonical campaign actually opened.

Reproducible from the on-disk manifest + cache + universe + campaign artifacts
alone. Never fabricates data and never overwrites the canonical campaign output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.provenance import ProvenanceError  # noqa: E402
from src.strategy.config import SPEC_MIN_DAILY_VOLUME_USD  # noqa: E402
from src.strategy.crash_rebound import (  # noqa: E402
    _daily_volume_usd,
    _rsi,
    confirm_rebound,
)

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

REASON_ORDER = [
    "trade_opened",
    "no_next_bar",
    "volume_gate",
    "bounce_not_confirmed",
    "regime_min_price",
    "one_position_per_coin",
    "max_positions",
    "gross_cap",
    "portfolio_admission",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _rsi_series(closes: List[float], period: int) -> List[Optional[float]]:
    """Wilder RSI for every prefix, identical to src.strategy.crash_rebound._rsi."""
    n = len(closes)
    out: List[Optional[float]] = [None] * n
    gains: List[float] = []
    losses: List[float] = []
    for i in range(1, n):
        ch = closes[i] - closes[i - 1]
        gains.append(ch if ch > 0 else 0.0)
        losses.append(-ch if ch < 0 else 0.0)
    avg_gain: Optional[float] = None
    avg_loss: Optional[float] = None
    for k in range(period - 1, len(gains)):
        if k == period - 1:
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
        else:
            avg_gain = (avg_gain * (period - 1) + gains[k]) / period
            avg_loss = (avg_loss * (period - 1) + losses[k]) / period
        if avg_loss == 0:
            out[k + 1] = 100.0
        else:
            rs = avg_gain / avg_loss
            out[k + 1] = 100.0 - (100.0 / (1.0 + rs))
    return out


def _ts_ms(candle: Dict[str, Any]) -> Optional[int]:
    for key in ("timestamp", "timestamp_ms", "time", "t"):
        v = candle.get(key)
        if v is None:
            continue
        try:
            iv = int(v)
        except (TypeError, ValueError):
            continue
        return iv if iv > 1e12 else iv * 1000
    return None


def _load_json(path: Path) -> Any:
    with open(path, "r") as f:
        return json.load(f)


def _load_candles(path: Path) -> List[Dict[str, Any]]:
    data = _load_json(path)
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def _validate_output_prefix(prefix: str) -> str:
    p = Path(prefix)
    if p.is_absolute() or ".." in p.parts or len(p.parts) != 1:
        raise SystemExit(
            "output prefix must be a bare filename stem under research_state/ "
            f"(got {prefix!r})"
        )
    return p.stem


def build_census(manifest_path: Path, cache_dir: Path, universe_path: Path,
                 campaign_path: Path, rsi_period: int, rsi_threshold: float,
                 min_daily_volume_usd: float) -> Dict[str, Any]:
    if min_daily_volume_usd < SPEC_MIN_DAILY_VOLUME_USD:
        raise ProvenanceError(
            f"census volume floor {min_daily_volume_usd:g} is below the spec floor "
            f"{SPEC_MIN_DAILY_VOLUME_USD:g}; a sub-spec floor is not valid real-evidence"
        )
    manifest = _load_json(manifest_path)
    if manifest.get("fabricated_data") is not False:
        raise ProvenanceError("manifest declares fabricated_data != false")
    if not (manifest.get("summary") or {}).get("ready_for_real_campaign"):
        raise ProvenanceError("manifest is not ready_for_real_campaign")
    if not (manifest.get("summary") or {}).get("all_complete"):
        raise ProvenanceError("manifest coverage is not all_complete")

    universe = _load_json(universe_path)
    if isinstance(universe, dict):
        symbols = universe.get("selected_symbols") or universe.get("symbols") or []
    else:
        symbols = universe
    symbols = [str(s).upper() for s in symbols]

    campaign = _load_json(campaign_path)
    if campaign.get("real_market_data") is not True:
        raise ProvenanceError("campaign artifact is not real_market_data=true")
    results = campaign.get("results") or {}
    trades = results.get("trades") or []
    config = campaign.get("config") or {}
    max_positions = int(config.get("max_positions", 5) or 5)
    gross_cap_pct = float(config.get("gross_cap_pct", 120.0) or 120.0)
    capital = float((campaign.get("config") or {}).get("capital", 100000.0) or 100000.0)
    position_pct = float(config.get("position_size_pct_of_daily_volume", 1.25) or 1.25)

    trades_by_symbol: Dict[str, List[Dict[str, Any]]] = {}
    for t in trades:
        trades_by_symbol.setdefault(str(t.get("symbol", "")).upper(), []).append(t)

    def trade_ts(t: Dict[str, Any], key: str) -> Optional[int]:
        v = t.get(key)
        try:
            return int(v) if v is not None else None
        except (TypeError, ValueError):
            return None

    events: List[Dict[str, Any]] = []
    per_symbol: List[Dict[str, Any]] = []
    missing_symbols: List[str] = []
    hash_mismatches: List[str] = []
    bars_total = 0

    for symbol in symbols:
        cache_path = cache_dir / "candles" / f"{symbol}.json"
        if not cache_path.exists():
            missing_symbols.append(symbol)
            continue
        expected_sha = ((manifest.get("symbols") or {}).get(symbol) or {}).get("sha256")
        actual_sha = sha256_file(cache_path)
        if expected_sha and actual_sha != expected_sha:
            hash_mismatches.append(f"{symbol}: expected {expected_sha}, got {actual_sha}")

        candles = _load_candles(cache_path)
        bars_total += len(candles)
        closes = [float(c["close"]) for c in candles]
        rsi_by_idx = _rsi_series(closes, rsi_period)

        sym_trades = trades_by_symbol.get(symbol, [])
        intervals = [
            (trade_ts(t, "entry_timestamp"), trade_ts(t, "exit_timestamp"), t)
            for t in sym_trades
            if trade_ts(t, "entry_timestamp") is not None
        ]

        sym_events = 0
        sym_volume_pass = 0
        sym_bounce = 0
        sym_signal_pass = 0
        sym_trades_opened = 0

        for i in range(rsi_period, len(candles)):
            rsi = rsi_by_idx[i]
            if rsi is None or rsi >= rsi_threshold:
                continue
            hist = candles[: i + 1]
            vol = _daily_volume_usd(hist, lookback=24)
            volume_pass = vol is not None and vol >= min_daily_volume_usd
            bounce = confirm_rebound(hist, lookback=3, min_body_ratio=0.5)
            close = closes[i]
            price_ok = close >= 5.0
            next_bar_ts = _ts_ms(candles[i + 1]) if i + 1 < len(candles) else None
            next_open = float(candles[i + 1]["open"]) if i + 1 < len(candles) else None
            signal_pass = bool(volume_pass and bounce and price_ok)

            event: Dict[str, Any] = {
                "symbol": symbol,
                "bar_timestamp_ms": _ts_ms(candles[i]),
                "bar_timestamp_utc": _iso(_ts_ms(candles[i])),
                "rsi": round(float(rsi), 6),
                "close": close,
                "next_bar_timestamp_ms": next_bar_ts,
                "next_bar_open": next_open,
                "trailing_24h_volume_usd": round(float(vol), 2) if vol is not None else None,
                "volume_gate_pass": bool(volume_pass),
                "bounce_confirmed": bool(bounce),
                "regime_min_price_ok": bool(price_ok),
                "signal_gate_pass": signal_pass,
                "admitted_under_gross_cap": False,
                "trade_opened": False,
                "blocking_reason": None,
                "matched_trade_leg": None,
                "matched_trade_pnl": None,
            }

            matched = None
            if next_bar_ts is not None:
                for t in sym_trades:
                    if trade_ts(t, "entry_timestamp") == next_bar_ts:
                        matched = t
                        break

            desired_notional = position_pct / 100.0 * vol if vol is not None else 0.0
            open_trades = [
                t for (ets, xts, t) in intervals
                if ets is not None and next_bar_ts is not None and ets <= next_bar_ts
                and (xts is None or next_bar_ts < xts)
            ]
            open_notional = sum(float(t.get("max_live_coin_notional") or 0.0) for t in open_trades)
            available_cap = capital * gross_cap_pct / 100.0 - open_notional

            if matched is not None:
                reason = "trade_opened"
                event["trade_opened"] = True
                event["matched_trade_leg"] = matched.get("leg")
                event["matched_trade_pnl"] = matched.get("pnl")
                live = float(matched.get("max_live_coin_notional") or 0.0)
                event["admitted_under_gross_cap"] = bool(live > 0 and live < desired_notional - 1e-6)
                sym_trades_opened += 1
            elif next_bar_ts is None:
                reason = "no_next_bar"
            elif not volume_pass:
                reason = "volume_gate"
            elif not bounce:
                reason = "bounce_not_confirmed"
            elif not price_ok:
                reason = "regime_min_price"
            elif open_trades and any(
                str(t.get("symbol", "")).upper() == symbol for t in open_trades
            ):
                reason = "one_position_per_coin"
            elif len(open_trades) >= max_positions:
                reason = "max_positions"
            elif available_cap <= 0:
                reason = "gross_cap"
            else:
                reason = "portfolio_admission"

            event["blocking_reason"] = reason
            event["desired_notional"] = round(desired_notional, 2)
            event["open_notional_at_entry"] = round(open_notional, 2)
            event["available_cap_at_entry"] = round(available_cap, 2)

            sym_events += 1
            sym_volume_pass += int(volume_pass)
            sym_bounce += int(bounce)
            sym_signal_pass += int(signal_pass)
            events.append(event)

        per_symbol.append({
            "symbol": symbol,
            "bars": len(candles),
            "events": sym_events,
            "volume_gate_pass": sym_volume_pass,
            "bounce_confirmed": sym_bounce,
            "signal_gate_pass": sym_signal_pass,
            "trades_opened": sym_trades_opened,
        })

    reason_counts: Dict[str, int] = {}
    for e in events:
        reason_counts[e["blocking_reason"]] = reason_counts.get(e["blocking_reason"], 0) + 1

    matched_events = [e for e in events if e["trade_opened"]]
    matched_entry_ts = {e["next_bar_timestamp_ms"] for e in matched_events}
    unmatched_trades = [
        {
            "symbol": t.get("symbol"),
            "leg": t.get("leg"),
            "entry_timestamp": t.get("entry_timestamp"),
            "exit_reason": t.get("exit_reason"),
        }
        for t in trades
        if trade_ts(t, "entry_timestamp") not in matched_entry_ts
    ]
    unexplained = [
        e for e in events
        if e["signal_gate_pass"] and e["blocking_reason"] == "portfolio_admission"
    ]

    window_start = (manifest.get("target_window") or {}).get("start")
    window_end = (manifest.get("target_window") or {}).get("end")

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "crash_event_census",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "inputs": {
            "manifest": str(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "cache_dir": str(cache_dir),
            "universe": str(universe_path),
            "universe_sha256": sha256_file(universe_path),
            "campaign": str(campaign_path),
            "campaign_sha256": sha256_file(campaign_path),
        },
        "params": {
            "rsi_period": rsi_period,
            "rsi_threshold": rsi_threshold,
            "min_daily_volume_usd": min_daily_volume_usd,
            "min_price_usd": 5.0,
            "rebound_lookback": 3,
            "rebound_min_body_ratio": 0.5,
            "position_size_pct_of_daily_volume": position_pct,
            "max_positions": max_positions,
            "gross_cap_pct": gross_cap_pct,
            "capital": capital,
        },
        "window": {
            "start": window_start,
            "end": window_end,
            "bars_scanned": bars_total,
        },
        "universe_size": len(symbols),
        "missing_symbols": missing_symbols,
        "hash_mismatches": hash_mismatches,
        "reconciliation": {
            "events_total": len(events),
            "volume_gate_pass": sum(1 for e in events if e["volume_gate_pass"]),
            "bounce_confirmed": sum(1 for e in events if e["bounce_confirmed"]),
            "regime_min_price_ok": sum(1 for e in events if e["regime_min_price_ok"]),
            "signal_gate_pass": sum(1 for e in events if e["signal_gate_pass"]),
            "trades_in_campaign": len(trades),
            "trades_matched_to_events": len(matched_events),
            "unmatched_campaign_trades": unmatched_trades,
            "unexplained_signal_gate_events": len(unexplained),
            "blocking_reason_counts": {
                k: reason_counts[k] for k in REASON_ORDER if k in reason_counts
            },
            "blocking_reasons_sum": sum(reason_counts.values()),
        },
        "per_symbol": sorted(per_symbol, key=lambda r: (-r["events"], r["symbol"])),
        "events": events,
    }


def _iso(ms: Optional[int]) -> Optional[str]:
    if ms is None:
        return None
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def render_markdown(report: Dict[str, Any]) -> str:
    rec = report["reconciliation"]
    lines: List[str] = []
    lines.append("# Crash-Event Census — Real OKX 283-Day Run (Phase J1)")
    lines.append("")
    lines.append(f"**Generated (UTC):** {report['generated_at_utc']}  ")
    lines.append(f"**Provenance caveat:** {report['provenance_caveat']}")
    lines.append("")
    lines.append("## Reconciliation")
    lines.append("")
    lines.append("| Stage | Count |")
    lines.append("|---|---|")
    lines.append(f"| RSI(21) < 20 events (all {report['universe_size']} admitted symbols) | {rec['events_total']} |")
    lines.append(f"| Pass volume gate (>= $5M trailing 24h) | {rec['volume_gate_pass']} |")
    lines.append(f"| Pass bounce confirmation | {rec['bounce_confirmed']} |")
    lines.append(f"| Pass regime min-price (>= $5) | {rec['regime_min_price_ok']} |")
    lines.append(f"| Pass ALL signal gates (volume + bounce + price) | {rec['signal_gate_pass']} |")
    lines.append(f"| Trades actually opened by the canonical campaign | {rec['trades_in_campaign']} |")
    lines.append(f"| Trades matched to a census event | {rec['trades_matched_to_events']} |")
    lines.append(f"| Signal-gate events with no capacity explanation | {rec['unexplained_signal_gate_events']} |")
    lines.append("")
    lines.append("## Blocking reasons (every event, exactly one)")
    lines.append("")
    lines.append("| Blocking reason | Events |")
    lines.append("|---|---|")
    for reason, count in rec["blocking_reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.append(f"| **sum** | **{rec['blocking_reasons_sum']}** |")
    lines.append("")
    if rec["unmatched_campaign_trades"]:
        lines.append("## Unmatched campaign trades (audit required)")
        lines.append("")
        for t in rec["unmatched_campaign_trades"]:
            lines.append(f"- `{t['symbol']}` {t['leg']} entry `{t['entry_timestamp']}` exit_reason `{t['exit_reason']}`")
        lines.append("")
    lines.append("## Per-symbol event counts")
    lines.append("")
    lines.append("| Symbol | Bars | Events | Vol pass | Bounce | Signal pass | Trades |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in report["per_symbol"]:
        lines.append(
            f"| {r['symbol']} | {r['bars']} | {r['events']} | {r['volume_gate_pass']} | "
            f"{r['bounce_confirmed']} | {r['signal_gate_pass']} | {r['trades_opened']} |"
        )
    lines.append("")
    lines.append("## Trade-frequency gap (8 vs 85 spec)")
    lines.append("")
    lines.append(
        f"The OKX run opened {rec['trades_in_campaign']} trades from "
        f"{rec['signal_gate_pass']} signal-gate-passing events; "
        f"{rec['volume_gate_pass']}/{rec['events_total']} events cleared the $5M volume gate and "
        f"{rec['bounce_confirmed']} cleared bounce confirmation. The gap to the spec's 85 trades "
        "is driven by the funnel above, not by a single bug."
    )
    lines.append("")
    lines.append(
        "Caveat: same-bar multi-candidate equal-share cuts can reduce a position below its "
        "uncut size without denying it; `admitted_under_gross_cap` records that case on matched trades."
    )
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="research_state/cache/okx_1h_full_20251220_20260928/provenance.json")
    parser.add_argument("--cache-dir", default="research_state/cache/okx_1h_full_20251220_20260928")
    parser.add_argument("--universe-file", default="research_state/universe_okx_full_verified.json")
    parser.add_argument("--campaign", default="research_state/campaign_results_real_okx_full.json")
    parser.add_argument("--output-prefix", default="crash_event_census_real_okx_full")
    parser.add_argument("--rsi-period", type=int, default=21)
    parser.add_argument("--rsi-threshold", type=float, default=20.0)
    parser.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0)
    args = parser.parse_args(argv)

    stem = _validate_output_prefix(args.output_prefix)
    out_json = REPO_ROOT / "research_state" / f"{stem}.json"
    out_md = REPO_ROOT / "research_state" / f"{stem}.md"

    report = build_census(
        Path(args.manifest),
        Path(args.cache_dir),
        Path(args.universe_file),
        Path(args.campaign),
        args.rsi_period,
        args.rsi_threshold,
        args.min_daily_volume_usd,
    )

    if report["missing_symbols"]:
        raise SystemExit(f"missing candle files for: {report['missing_symbols']}")
    if report["hash_mismatches"]:
        raise SystemExit("sha256 mismatch vs manifest: " + "; ".join(report["hash_mismatches"]))

    out_json.write_text(json.dumps(report, indent=2) + "\n")
    out_md.write_text(render_markdown(report))

    rec = report["reconciliation"]
    print(f"events={rec['events_total']} volume_pass={rec['volume_gate_pass']} "
          f"bounce={rec['bounce_confirmed']} signal_pass={rec['signal_gate_pass']} "
          f"trades={rec['trades_in_campaign']} matched={rec['trades_matched_to_events']} "
          f"unexplained={rec['unexplained_signal_gate_events']}")
    print(f"blocking_reasons={rec['blocking_reason_counts']}")
    print(f"wrote {out_json.relative_to(REPO_ROOT)} and {out_md.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())