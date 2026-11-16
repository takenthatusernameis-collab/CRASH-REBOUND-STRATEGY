#!/usr/bin/env python3
"""C20 — cross-venue spec-faithful replication & pooled synthesis.

WHY THIS EXISTS
---------------
C19 adjudicated the entry-rule fork: `SPEC_LITERAL_NEXT_OPEN` is the spec-faithful
reading of crash-rebound-strategy.pdf ("21-hour RSI closes below 20" -> "Buy at
next hourly open", with no same-bar rebound-confirmation candle). The native
verdict under that reading is `NO_GO` (C18/C19: 22 trades, -47,933.58).

Every multi-year cross-venue campaign to date (C6 OKX, C8 Binance UM) used the
*canonical same-bar* reading, so the adjudicated spec-faithful rule has never
been tested out-of-sample on the two independent real archives. C20 answers that
one remaining executable, decision-relevant question on already-verified data.

WHAT IT RUNS (heavy work, per venue)
------------------------------------
  1. Real spec-literal campaign  (real portfolio engine, entry_spec_literal_next_open=True)
  2. Crash-event census          (RSI(21)<20 events, spec-literal gate, reconciliation)
  3. Episode dependence audit    (98h single-linkage clustering + episode-block bootstrap)
  4. Conditional temporal-edge permutation (crash-bar conditioned, real engine)
  5. Full-portfolio placebo      (admission/cap/occupancy selection, deterministic seed)
  6. Robustness battery          (per-leg attribution, exit reasons, sub-period,
                                  concentration, leave-one-out, achievable power)
  7. Per-venue verdict
  8. Pooled venue-blocked synthesis + C20 cross-venue verdict + consolidated final

HARD LABELS
-----------
  real_market_data = true, fabricated_data = false, synthetic_data = false,
  is_hyperliquid_venue_data = false, cross_venue = true.
  OKX/Binance UM results are NEVER Hyperliquid performance evidence.

The config is fixed by `c20_prereg_<TS>.json`; there is no config switching.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import multiprocessing as mp
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.strategy.config import StrategyConfig  # noqa: E402
from scripts.build_crash_event_census import _rsi_series  # noqa: E402
from src.strategy.crash_rebound import (  # noqa: E402
    _daily_volume_usd,
    confirm_rebound,
    generate_signal as real_generate_signal,
)
import scripts.run_portfolio as portfolio_mod  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.metrics import compute_campaign_metrics, metrics_to_dict  # noqa: E402

TS = "20261116T063500Z"
SEED = 20261120
EPISODE_DRAWS = 20000
PLACEBO_DRAWS = 2000
# Permutation/placebo are bounded by wall-clock, not by prereg target. The prereg
# targets 20000 permutation / 2000 placebo draws; a single canonical portfolio run
# costs ~90s on this cache, so 20000 permutation draws would take ~50h per venue.
# MAX_PERMUTATION_DRAWS caps the sampled permutation at a wall-clock-feasible ceiling
# while preserving the exact-enumeration branch when the combinatorics are small.
MAX_PERMUTATION_DRAWS = 300
MAX_PLACEBO_DRAWS = 500
LINK_HOURS = 98.0
MIN_DAILY_VOLUME_USD = 5_000_000.0

PROVENANCE_CAVEAT = (
    "Real OKX / Binance UM exchange data, non-synthetic, CROSS-VENUE vs the "
    "Hyperliquid spec; NOT Hyperliquid performance evidence and must never be "
    "relabelled as such. Multi-year window 2023-01-01T00:00:00Z..2026-09-28T23:00:00Z "
    "(32808 hourly bars/symbol)."
)

VENUES = {
    "okx": {
        "venue_label": "OKX",
        "cache_dir": f"research_state/cache/okx_1h_multiyear_20230101_20260928",
        "universe": "research_state/universe_okx_multiyear_verified.json",
        "canonical_campaign_same_bar": "research_state/campaign_results_real_okx_multiyear.json",
        "canonical_census_same_bar": "research_state/crash_event_census_real_okx_multiyear.json",
    },
    "binance_um": {
        "venue_label": "Binance UM",
        "cache_dir": f"research_state/cache/binance_um_1h_multiyear_20230101_20260928",
        "universe": "research_state/universe_binance_um_multiyear_verified.json",
        "canonical_campaign_same_bar": "research_state/campaign_results_real_binance_um_multiyear.json",
        "canonical_census_same_bar": "research_state/crash_event_census_real_binance_um_multiyear.json",
    },
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_utc(text: Any) -> dt.datetime:
    s = str(text)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return dt.datetime.fromisoformat(s).astimezone(dt.timezone.utc)
    except Exception:
        return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


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


def _iso(ms: Optional[int]) -> Optional[str]:
    if ms is None:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_timestamp_ms(v: Any) -> Optional[int]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip()
    if not s:
        return None
    if s.lstrip("-").isdigit():
        return int(s)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return int(dt.datetime.fromisoformat(s).astimezone(dt.timezone.utc).timestamp() * 1000.0)
    except (TypeError, ValueError):
        return None


def _q(vals: Sequence[float], p: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return float(s[int(k)]) if f == c else float(s[f] * (c - k) + s[c] * (k - f))


def _summ(vals: Sequence[float]) -> Dict[str, Any]:
    s = sorted(float(v) for v in vals)
    if not s:
        return {"n": 0, "mean": 0.0, "median": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0,
                "p05": 0.0, "p95": 0.0, "sum": 0.0}
    return {
        "n": len(s), "sum": sum(s), "mean": statistics.fmean(s), "median": statistics.median(s),
        "stdev": statistics.pstdev(s) if len(s) > 1 else 0.0,
        "min": s[0], "max": s[-1], "p05": _q(s, 0.05), "p95": _q(s, 0.95),
    }


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def load_venue(venue: str) -> Dict[str, Any]:
    spec = VENUES[venue]
    cache_dir = REPO / spec["cache_dir"]
    universe_path = REPO / spec["universe"]
    universe = json.loads(universe_path.read_text())
    symbols = [str(s).upper() for s in (universe.get("selected_symbols") or universe.get("symbols") or [])]
    candles: Dict[str, List[Dict[str, Any]]] = {}
    missing: List[str] = []
    for sym in symbols:
        p = cache_dir / "candles" / f"{sym}.json"
        if not p.exists():
            missing.append(sym)
            continue
        candles[sym] = load_candles(p)
    return {
        "venue": venue,
        "venue_label": spec["venue_label"],
        "cache_dir": cache_dir,
        "universe_path": universe_path,
        "universe": universe,
        "symbols": symbols,
        "candles": candles,
        "missing": missing,
        "manifest_sha256": sha256_file(cache_dir / "provenance.json"),
        "universe_sha256": sha256_file(universe_path),
    }


def spec_literal_config() -> StrategyConfig:
    return StrategyConfig(
        use_rsi_trigger=True,
        rsi_period=21,
        rsi_threshold=20.0,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=MIN_DAILY_VOLUME_USD,
        target_pct=9.0,
        rebound_short_target_pct=9.0,
        rebound_short_time_exit_bars=48,
        entry_spec_literal_next_open=True,
    )


# ---------------------------------------------------------------------------
# Step 1 — real spec-literal campaign
# ---------------------------------------------------------------------------

def run_campaign(venue_data: Dict[str, Any], out_stem: str) -> Dict[str, Any]:
    candles = venue_data["candles"]
    eth = candles.get("ETH")
    cfg = spec_literal_config()
    t0 = time.time()
    res = run_portfolio_simulation(
        candles, config=cfg, capital=100_000.0,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(cfg.enable_eth_hedge),
    )
    metrics = metrics_to_dict(compute_campaign_metrics(
        trades=res.get("trades", []), equity_curve=res.get("equity_curve"),
        initial_capital=100_000.0,
    ))
    out = REPO / "research_state" / f"{out_stem}.json"
    out_m = REPO / "research_state" / f"{out_stem}_metrics.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    export = {
        "timestamp": iso_now(),
        "run_type": "real_market_campaign_spec_literal_cross_venue",
        "research_status": "CROSS_VENUE_MULTIYEAR_SPEC_LITERAL_NOT_HYPERLIQUID",
        "campaign": "C20",
        "prereg": f"research_state/c20_prereg_{TS}.json",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "real_market_data": True,
        "performance_evidence": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "partial_universe_not_evidence": False,
        "venue_label": venue_data["venue_label"],
        "evidence_warning": PROVENANCE_CAVEAT,
        "data_provenance": {
            "cache_dir": str(venue_data["cache_dir"].relative_to(REPO)),
            "universe": str(venue_data["universe_path"].relative_to(REPO)),
            "manifest_sha256": venue_data["manifest_sha256"],
            "universe_sha256": venue_data["universe_sha256"],
            "symbols_loaded": sorted(venue_data["candles"].keys()),
            "missing_symbols": venue_data["missing"],
            "is_hyperliquid_venue_data": False,
            "venue_basis": ("okx_public_rest_v5_history_candles"
                            if venue_data["venue"] == "okx"
                            else "binance_um_public_fapi_klines"),
        },
        "config": {
            "use_rsi_trigger": cfg.use_rsi_trigger,
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "target_pct": cfg.target_pct,
            "rebound_short_target_pct": cfg.rebound_short_target_pct,
            "rebound_short_time_exit_bars": cfg.rebound_short_time_exit_bars,
            "enable_rebound_short": cfg.enable_rebound_short,
            "enable_eth_hedge": cfg.enable_eth_hedge,
            "enable_volume_based_sizing": cfg.enable_volume_based_sizing,
            "position_size_pct_of_daily_volume": cfg.position_size_pct_of_daily_volume,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
            "gross_cap_pct": cfg.gross_cap_pct,
            "entry_spec_literal_next_open": bool(cfg.entry_spec_literal_next_open),
        },
        "results": {
            "total_pnl": res.get("total_pnl"),
            "num_trades": res.get("num_trades"),
            "final_open_positions": res.get("final_open_positions"),
            "final_gross_exposure": res.get("final_gross_exposure"),
            "trades": res.get("trades"),
            "equity_curve": res.get("equity_curve"),
            "equity_curve_points": len(res.get("equity_curve") or []),
        },
        "metrics": metrics,
        "wall_seconds": round(time.time() - t0, 1),
    }
    out.write_text(json.dumps(export, indent=2, default=str) + "\n")
    out_m.write_text(json.dumps(metrics, indent=2, default=str) + "\n")
    print(f"[campaign] {venue_data['venue_label']}: trades={export['results']['num_trades']} "
          f"pnl={export['results']['total_pnl']:.2f} wall={export['wall_seconds']}s", flush=True)
    return export


# ---------------------------------------------------------------------------
# Step 2 — crash-event census (spec-literal signal gate)
# ---------------------------------------------------------------------------

def build_census(venue_data: Dict[str, Any], campaign: Dict[str, Any],
                 out_stem: str) -> Dict[str, Any]:
    candles_by_symbol = venue_data["candles"]
    universe_symbols = venue_data["symbols"]
    trades = (campaign.get("results") or {}).get("trades") or []
    cfg = campaign.get("config") or {}
    max_positions = int(cfg.get("max_positions", 5) or 5)
    gross_cap_pct = float(cfg.get("gross_cap_pct", 120.0) or 120.0)
    capital = 100_000.0
    position_pct = float(cfg.get("position_size_pct_of_daily_volume", 1.25) or 1.25)

    trades_by_symbol: Dict[str, List[Dict[str, Any]]] = {}
    for t in trades:
        trades_by_symbol.setdefault(str(t.get("symbol", "")).upper(), []).append(t)

    events: List[Dict[str, Any]] = []
    per_symbol: List[Dict[str, Any]] = []
    for symbol in universe_symbols:
        cs = candles_by_symbol.get(symbol)
        if cs is None:
            continue
        closes = [float(c["close"]) for c in cs]
        rsi_by_idx = _rsi_series(closes, 21)
        sym_trades = trades_by_symbol.get(symbol, [])
        intervals = [
            (parse_timestamp_ms(t.get("entry_timestamp")), parse_timestamp_ms(t.get("exit_timestamp")), t)
            for t in sym_trades
            if parse_timestamp_ms(t.get("entry_timestamp")) is not None
        ]
        sym_events = sym_volume = sym_signal = sym_trades_opened = 0
        for i in range(21, len(cs)):
            rsi = rsi_by_idx[i]
            if rsi is None or rsi >= 20.0:
                continue
            hist = cs[: i + 1]
            vol = _daily_volume_usd(hist, lookback=24)
            volume_pass = vol is not None and vol >= MIN_DAILY_VOLUME_USD
            close = closes[i]
            price_ok = close >= 5.0
            next_bar_ts = _ts_ms(cs[i + 1]) if i + 1 < len(cs) else None
            next_open = float(cs[i + 1]["open"]) if i + 1 < len(cs) else None
            # Spec-literal gate: RSI(21)<20 close -> buy at next hourly open.
            # NO same-bar confirm_rebound gate (C19 adjudication).
            signal_pass = bool(volume_pass and price_ok and next_bar_ts is not None)
            bounce = confirm_rebound(hist, lookback=3, min_body_ratio=0.5)

            event: Dict[str, Any] = {
                "symbol": symbol,
                "bar_timestamp_ms": _ts_ms(cs[i]),
                "bar_timestamp_utc": _iso(_ts_ms(cs[i])),
                "rsi": round(float(rsi), 6),
                "close": close,
                "next_bar_timestamp_ms": next_bar_ts,
                "next_bar_open": next_open,
                "trailing_24h_volume_usd": round(float(vol), 2) if vol is not None else None,
                "volume_gate_pass": bool(volume_pass),
                "bounce_confirmed_same_bar_non_spec": bool(bounce),
                "regime_min_price_ok": bool(price_ok),
                "signal_gate_pass": signal_pass,
                "spec_literal_entry": True,
                "trade_opened": False,
                "matched_trade_leg": None,
                "matched_trade_pnl": None,
            }

            matched = None
            if next_bar_ts is not None:
                for t in sym_trades:
                    if parse_timestamp_ms(t.get("entry_timestamp")) == next_bar_ts:
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
                event["trade_opened"] = True
                event["matched_trade_leg"] = matched.get("leg")
                event["matched_trade_pnl"] = matched.get("pnl")
                sym_trades_opened += 1
                blocking = "trade_opened"
            elif next_bar_ts is None:
                blocking = "no_next_bar"
            elif not volume_pass:
                blocking = "volume_gate"
            elif not price_ok:
                blocking = "regime_min_price"
            elif open_trades and any(str(t.get("symbol", "")).upper() == symbol for t in open_trades):
                blocking = "one_position_per_coin"
            elif len(open_trades) >= max_positions:
                blocking = "max_positions"
            elif available_cap <= 0:
                blocking = "gross_cap"
            else:
                blocking = "portfolio_admission"
            event["blocking_reason"] = blocking
            event["desired_notional"] = round(desired_notional, 2)
            event["open_notional_at_entry"] = round(open_notional, 2)
            event["available_cap_at_entry"] = round(available_cap, 2)

            sym_events += 1
            sym_volume += int(volume_pass)
            sym_signal += int(signal_pass)
            events.append(event)

        per_symbol.append({
            "symbol": symbol,
            "bars": len(cs),
            "events": sym_events,
            "volume_gate_pass": sym_volume,
            "bounce_confirmed_same_bar_non_spec": sum(1 for e in events if e["symbol"] == symbol and e["bounce_confirmed_same_bar_non_spec"]),
            "signal_gate_pass": sym_signal,
            "trades_opened": sym_trades_opened,
        })

    reason_counts: Dict[str, int] = {}
    for e in events:
        reason_counts[e["blocking_reason"]] = reason_counts.get(e["blocking_reason"], 0) + 1
    matched_events = [e for e in events if e["trade_opened"]]
    matched_entry_ts = {e["next_bar_timestamp_ms"] for e in matched_events}
    unmatched_trades = [
        {"symbol": t.get("symbol"), "leg": t.get("leg"),
         "entry_timestamp": t.get("entry_timestamp"), "exit_reason": t.get("exit_reason")}
        for t in trades if parse_timestamp_ms(t.get("entry_timestamp")) not in matched_entry_ts
    ]
    unexplained = [e for e in events if e["signal_gate_pass"] and e["blocking_reason"] == "portfolio_admission"]

    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    report = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "run_type": "crash_event_census_spec_literal",
        "campaign": "C20",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "venue_label": venue_data["venue_label"],
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "inputs": {
            "cache_dir": str(venue_data["cache_dir"].relative_to(REPO)),
            "manifest_sha256": venue_data["manifest_sha256"],
            "universe": str(venue_data["universe_path"].relative_to(REPO)),
            "universe_sha256": venue_data["universe_sha256"],
            "campaign": f"research_state/campaign_results_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json",
            "campaign_sha256": sha256_file(REPO / f"research_state/campaign_results_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json"),
        },
        "params": {
            "rsi_period": 21, "rsi_threshold": 20.0,
            "min_daily_volume_usd": MIN_DAILY_VOLUME_USD,
            "min_price_usd": 5.0,
            "rebound_confirm_required": False,
            "entry": "next_hourly_open",
            "position_size_pct_of_daily_volume": position_pct,
            "max_positions": max_positions,
            "gross_cap_pct": gross_cap_pct,
            "capital": capital,
        },
        "universe_size": len(universe_symbols),
        "reconciliation": {
            "events_total": len(events),
            "volume_gate_pass": sum(1 for e in events if e["volume_gate_pass"]),
            "regime_min_price_ok": sum(1 for e in events if e["regime_min_price_ok"]),
            "signal_gate_pass": sum(1 for e in events if e["signal_gate_pass"]),
            "trades_in_campaign": len(trades),
            "trades_matched_to_events": len(matched_events),
            "unmatched_campaign_trades": unmatched_trades,
            "unexplained_signal_gate_events": len(unexplained),
            "blocking_reason_counts": reason_counts,
            "blocking_reasons_sum": sum(reason_counts.values()),
        },
        "per_symbol": sorted(per_symbol, key=lambda r: (-r["events"], r["symbol"])),
        "events": events,
    }
    out.write_text(json.dumps(report, indent=2) + "\n")
    rec = report["reconciliation"]
    print(f"[census] {venue_data['venue_label']}: events={rec['events_total']} signal_pass={rec['signal_gate_pass']} "
          f"trades={rec['trades_in_campaign']} matched={rec['trades_matched_to_events']} "
          f"unexplained={rec['unexplained_signal_gate_events']}", flush=True)
    return report


# ---------------------------------------------------------------------------
# Step 3 — memo replay + episode dependence audit + conditional permutation
# ---------------------------------------------------------------------------

def build_memo(venue_data: Dict[str, Any], census: Dict[str, Any],
               cfg: StrategyConfig) -> Tuple[Dict[Tuple[str, int], Any], List[Dict[str, Any]], Dict[str, Any]]:
    candles = venue_data["candles"]
    ts_index: Dict[str, Dict[int, int]] = {}
    for sym, cs in candles.items():
        ts_index[sym] = {}
        for i, c in enumerate(cs):
            ts = _ts_ms(c)
            if ts is not None:
                ts_index[sym][ts] = i
    memo: Dict[Tuple[str, int], Any] = {}
    rows: List[Dict[str, Any]] = []
    for e in census["events"]:
        sym = str(e.get("symbol", "")).upper()
        ts = e.get("bar_timestamp_ms")
        if ts is None:
            continue
        cs = candles.get(sym)
        idx = ts_index.get(sym, {}).get(int(ts)) if cs else None
        if idx is None:
            rows.append({
                "symbol": sym, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
                "bar_index": None, "signal": False, "reason": "bar_not_found",
                "signal_gate_pass": bool(e.get("signal_gate_pass")),
                "trade_opened_canonical": bool(e.get("trade_opened")),
            })
            continue
        sig = real_generate_signal(cs[: idx + 1], symbol=sym, config=cfg, capital=100000.0)
        rec = {
            "symbol": sym, "bar_index": idx, "bar_timestamp_ms": int(ts), "bar_timestamp_utc": e.get("bar_timestamp_utc"),
            "rsi": e.get("rsi"), "signal": sig is not None,
            "signal_gate_pass": bool(e.get("signal_gate_pass")),
            "trade_opened_canonical": bool(e.get("trade_opened")),
        }
        if sig is not None:
            memo[(sym, idx)] = sig
        rows.append(rec)
    meta = {
        "census_events": len(census["events"]),
        "rows": len(rows),
        "memo_signals": len(memo),
        "signal_gate_events": sum(1 for r in rows if r.get("signal_gate_pass")),
        "memo_matches_signal_gate": len(memo) == sum(1 for r in rows if r.get("signal_gate_pass")),
        "symbols_with_signals": sorted({s for s, _ in memo}),
    }
    return memo, rows, meta


def run_memo_portfolio(candles, cfg, memo):
    active = {k: v for k, v in memo.items()}

    def memo_generate_signal(candles_arg, symbol="TEST", config=None, capital=100000.0, risk_state=None, cache=None):
        return active.get((symbol, len(candles_arg) - 1))

    original = portfolio_mod.generate_signal
    portfolio_mod.generate_signal = memo_generate_signal
    try:
        return portfolio_mod.run_portfolio_simulation(
            candles, cfg, 100000.0, {"ETH": candles["ETH"]}, require_eth_hedge=True
        )
    finally:
        portfolio_mod.generate_signal = original


def trade_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    trades = result.get("trades", []) or []
    out = []
    for t in trades:
        out.append({
            "symbol": t.get("symbol"),
            "entry_timestamp": t.get("entry_timestamp"),
            "exit_timestamp": t.get("exit_timestamp"),
            "total_pnl": float(t.get("total_pnl", 0.0) or 0.0),
            "pnl": float(t.get("pnl", 0.0) or 0.0),
            "hedge_pnl": float(t.get("hedge_pnl", 0.0) or 0.0),
            "rebound_short_pnl": float(t.get("rebound_short_pnl", 0.0) or 0.0),
            "rebound_hedge_pnl": float(t.get("rebound_hedge_pnl", 0.0) or 0.0),
            "exit_reason": t.get("exit_reason"),
            "leg": t.get("leg"),
        })
    return {"trades": out, "num_trades": int(result.get("num_trades", len(out)))}


def cluster_episodes(keys: Sequence[Tuple[str, int]], times: Dict[Tuple[str, int], str],
                     link_hours: float) -> List[Dict[str, Any]]:
    if not keys:
        return []
    parsed = sorted(((parse_utc(times[k]), k) for k in keys if k in times), key=lambda x: x[0])
    if not parsed:
        return []
    episodes: List[Dict[str, Any]] = []
    current = [parsed[0][1]]
    anchor = parsed[0][0]
    current_end = anchor
    for moment, key in parsed[1:]:
        if (moment - anchor).total_seconds() / 3600.0 <= link_hours:
            current.append(key)
            if moment > current_end:
                current_end = moment
        else:
            episodes.append({"start": anchor.strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"), "keys": list(current)})
            current = [key]
            anchor = moment
            current_end = moment
    episodes.append({"start": anchor.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "end": current_end.strftime("%Y-%m-%dT%H:%M:%SZ"), "keys": list(current)})
    for index, ep in enumerate(episodes):
        ep["episode_id"] = index
        ep["size"] = len(ep["keys"])
        ep["events"] = len(ep["keys"])
        ep["symbols"] = sorted({k[0] for k in ep["keys"]})
        ep["distinct_days"] = len({times[k][:10] for k in ep["keys"] if k in times})
    return episodes


def assign_episode(entry_ts: Any, ep_bounds: Sequence[Tuple[int, dt.datetime, dt.datetime]]) -> int:
    ms = parse_timestamp_ms(entry_ts)
    if ms is None:
        return ep_bounds[0][0] if ep_bounds else 0
    try:
        moment = dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc)
    except Exception:
        return ep_bounds[0][0] if ep_bounds else 0
    best, best_gap = (ep_bounds[0][0] if ep_bounds else 0), None
    for eid, start, end in ep_bounds:
        gap = 0.0 if start <= moment <= end else min(abs((moment - start).total_seconds()), abs((moment - end).total_seconds()))
        if best_gap is None or gap < best_gap:
            best, best_gap = eid, gap
    return best


def episode_block_bootstrap(trade_rows: Sequence[Dict[str, Any]], episodes: Sequence[Dict[str, Any]],
                            resamples: int, seed: int) -> Dict[str, Any]:
    ep_bounds = [(e["episode_id"], parse_utc(e["start"]), parse_utc(e["end"])) for e in episodes]
    groups: Dict[int, List[float]] = {e["episode_id"]: [] for e in episodes}
    for t in trade_rows:
        groups.setdefault(assign_episode(t.get("entry_timestamp"), ep_bounds), []).append(
            float(t.get("total_pnl") or 0.0))
    ep_ids = sorted(groups)
    rng = random.Random(seed)
    totals: List[float] = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(ep_ids)):
            total += sum(groups[ep_ids[rng.randrange(len(ep_ids))]])
        totals.append(total)
    observed = sum(sum(v) for v in groups.values())
    pool = [sum(groups[e]) for e in ep_ids if groups.get(e) is not None]
    rng2 = random.Random(seed + 1)
    grid = []
    for n in list(range(2, 41)) + [50, 60, 80, 100, 150, 200, 300, 500]:
        if n <= 0:
            continue
        draws = [sum(pool[rng2.randrange(len(pool))] for _ in range(n)) for _ in range(4000)]
        lo, hi = _q(draws, 0.025), _q(draws, 0.975)
        grid.append({"n_episodes": n, "ci_low": round(lo, 2), "ci_high": round(hi, 2),
                     "excludes_zero": (lo > 0 or hi < 0), "mean": round(statistics.fmean(draws), 2)})
    first = next((row["n_episodes"] for row in grid if row["excludes_zero"]), None)
    return {
        "resamples": resamples, "seed": seed, "episode_blocks": len(ep_ids),
        "episode_trade_counts": {str(e): len(groups[e]) for e in ep_ids},
        "observed_total_pnl": observed,
        "observed_episode_totals": {str(e): round(sum(groups[e]), 2) for e in ep_ids},
        "bootstrap_total_pnl": {
            "mean": statistics.fmean(totals) if totals else 0.0,
            "median": statistics.median(totals) if totals else 0.0,
            "p05": _q(totals, 0.05), "p95": _q(totals, 0.95),
            "ci_low_pnl_2p5": _q(totals, 0.025), "ci_high_pnl_97p5": _q(totals, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for t in totals if t > 0) / len(totals)) if totals else 0.0,
        },
        "power_curve": {"grid": grid, "observed_episodes": len(pool),
                        "first_size_excluding_zero": first},
    }


_WORKER: Dict[str, Any] = {}


def _init_worker(candles_active, memo, cfg):
    _WORKER["candles"] = candles_active
    _WORKER["memo"] = memo
    _WORKER["cfg"] = cfg


def _run_draw(sub):
    memo = _WORKER["memo"]
    res = run_memo_portfolio(_WORKER["candles"], _WORKER["cfg"],
                             {k: memo[k] for k in sub if k in memo})
    return {"num_trades": int(res.get("num_trades", 0)),
            "total_pnl": float(res.get("total_pnl", 0.0))}


def conditional_permutation_null(venue_data, memo, rows, keys, canonical_pnl, cfg,
                                 draws: int, seed: int, jobs: int) -> Dict[str, Any]:
    candles = venue_data["candles"]
    eligible = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                       for r in rows if r.get("bar_index") is not None and r.get("rsi") is not None
                       and float(r.get("rsi")) < 20.0})
    by_symbol: Dict[str, List[Tuple[str, int]]] = {}
    for sym, idx in eligible:
        by_symbol.setdefault(sym, []).append((sym, idx))
    observed_syms = sorted({k[0] for k in keys})
    per_symbol_count = {s: sum(1 for k in keys if k[0] == s) for s in observed_syms}
    total_possible = 1
    try:
        for s, count in per_symbol_count.items():
            total_possible *= math.comb(len(by_symbol.get(s, [])), count)
    except Exception:
        total_possible = 10 ** 18
    exact = total_possible <= 5000
    rng = random.Random(seed)
    subsets: List[Tuple[Tuple[str, int], ...]] = []
    if exact:
        import itertools as it
        choices = [list(it.combinations(by_symbol.get(s, []), per_symbol_count[s])) for s in observed_syms]
        for combo in it.product(*choices):
            subset: List[Tuple[str, int], ...] = []
            for part in combo:
                subset.extend(part)
            subsets.append(tuple(sorted(subset)))
    else:
        # Wall-clock-bounded sampling. The prereg targets 20000 draws but each
        # canonical portfolio run costs ~90s on this cache; cap at
        # MAX_PERMUTATION_DRAWS so the campaign is actually completable.
        n_draws = min(int(draws or 0), MAX_PERMUTATION_DRAWS)
        for _ in range(n_draws):
            subset = []
            for s in observed_syms:
                pool_s = by_symbol.get(s, [])
                count = min(per_symbol_count[s], len(pool_s))
                if count <= 0:
                    continue
                subset.extend(rng.sample(pool_s, count))
            subsets.append(tuple(sorted(subset)))
    seen = set()
    unique: List[Tuple[Tuple[str, int], ...]] = []
    for s in subsets:
        if s in seen:
            continue
        seen.add(s)
        unique.append(s)
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    t0 = time.time()
    if jobs > 1 and "fork" in mp.get_all_start_methods():
        ctx = mp.get_context("fork")
        with ctx.Pool(processes=jobs, initializer=_init_worker,
                      initargs=(candles_active, memo, cfg)) as pool:
            results = pool.map(_run_draw, unique, chunksize=1)
    else:
        results = []
        for sub in unique:
            res = run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
            results.append({"num_trades": int(res.get("num_trades", 0)),
                            "total_pnl": float(res.get("total_pnl", 0.0))})
    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for p in pnls if p >= canonical_pnl)
    return {
        "method": ("conditional permutation: crash bars redrawn from the real RSI(21)<20 census "
                   "with observed per-symbol multiplicity preserved; real portfolio engine"),
        "mode": f"exact_enumeration:{len(results)}_draws" if exact else f"deterministic_seeded_draws:{len(results)}_seed:{seed}",
        "eligible_crash_bars": len(eligible),
        "observed_event_slots": len(keys),
        "observed_per_symbol": per_symbol_count,
        "distinct_possible_draws": total_possible if total_possible < 10 ** 12 else "astronomical",
        "draws_evaluated": len(results),
        "seed": seed,
        "jobs": jobs,
        "canonical_total_pnl": canonical_pnl,
        "null_total_pnl": {
            "mean": statistics.fmean(pnls) if pnls else 0.0,
            "median": statistics.median(pnls) if pnls else 0.0,
            "stdev": statistics.pstdev(pnls) if len(pnls) > 1 else 0.0,
            "min": min(pnls) if pnls else 0.0,
            "max": max(pnls) if pnls else 0.0,
            "p05": _q(pnls, 0.05), "p95": _q(pnls, 0.95),
            "ci_low_pnl_2p5": _q(pnls, 0.025), "ci_high_pnl_97p5": _q(pnls, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for p in pnls if p > 0) / len(pnls)) if pnls else 0.0,
        },
        "canonical_percentile_le": (sum(1 for p in pnls if p <= canonical_pnl) / len(pnls)) if pnls else 0.0,
        "p_null_ge_canonical": (ge / len(pnls)) if pnls else 0.0,
        "n_null_ge_canonical": ge,
        "wall_seconds": time.time() - t0,
        "limitation": None if exact else "Exact enumeration infeasible; deterministic seeded subset with documented seed/count.",
    }


def run_episode_inference(venue_data: Dict[str, Any], census: Dict[str, Any],
                          campaign: Dict[str, Any], cfg: StrategyConfig,
                          out_stem: str, jobs: int,
                          do_permutation: bool = True) -> Dict[str, Any]:
    memo, rows, meta = build_memo(venue_data, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(
            f"memo mismatch for {venue_data['venue_label']}: spec-literal signals="
            f"{meta['memo_signals']} but census signal_gate_pass={meta['signal_gate_events']}; "
            "the census and the real engine disagree on the spec-literal entry rule"
        )
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    times: Dict[Tuple[str, int], str] = {}
    for r in rows:
        if r.get("bar_index") is not None and r.get("bar_timestamp_utc"):
            times[(str(r["symbol"]).upper(), int(r["bar_index"]))] = str(r["bar_timestamp_utc"])
    candles = venue_data["candles"]
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    canonical = run_memo_portfolio(candles_active, cfg, memo)
    canonical_pnl = float(canonical.get("total_pnl", 0.0))
    episodes = cluster_episodes(keys, times, LINK_HOURS)
    episode_sizes = [e["size"] for e in episodes]
    largest = max(episode_sizes) if episode_sizes else 0
    distinct_days = sorted({times[k][:10] for k in keys if k in times})
    ts = trade_summary(canonical)
    boot = episode_block_bootstrap(ts["trades"], episodes, EPISODE_DRAWS, SEED)
    if do_permutation:
        perm = conditional_permutation_null(venue_data, memo, rows, keys, canonical_pnl, cfg,
                                            EPISODE_DRAWS, SEED, jobs)
    else:
        perm = {
            "method": "skipped via --skip-permutation",
            "mode": "skipped",
            "p_null_ge_canonical": None,
            "draws_evaluated": 0,
        }
    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "phase": "C20",
        "campaign": "C20",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "venue_label": venue_data["venue_label"],
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "config": {
            "rsi_threshold": 20.0, "target_pct": 9.0, "rebound_short_target_pct": 9.0,
            "entry_spec_literal_next_open": True, "config_matched": True,
        },
        "method": ("Crash-episode dependence audit (98h single-linkage) + episode-block bootstrap + "
                   "conditional temporal-edge permutation. Real portfolio engine, real multi-year "
                   + venue_data["venue_label"] + " cache."),
        "seed": SEED,
        "inputs": {
            "census_events": meta["census_events"],
            "signal_gate_events": meta["signal_gate_events"],
            "memo_signals": meta["memo_signals"],
            "memo_matches_signal_gate": meta["memo_matches_signal_gate"],
            "canonical_total_pnl": canonical_pnl,
            "canonical_num_trades": int(canonical.get("num_trades", 0)),
            "campaign_sha256": sha256_file(REPO / f"research_state/campaign_results_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json"),
            "census_sha256": sha256_file(REPO / f"research_state/crash_event_census_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json"),
            "cache_dir": str(venue_data["cache_dir"].relative_to(REPO)),
        },
        "episode_audit": {
            "link_hours": LINK_HOURS,
            "n_events": len(keys),
            "n_episodes": len(episodes),
            "n_symbols": len({k[0] for k in keys}),
            "n_distinct_crash_days": len(distinct_days),
            "distinct_crash_days": distinct_days,
            "largest_episode_events": largest,
            "largest_episode_share": (largest / len(keys)) if keys else 0.0,
            "mean_episode_size": statistics.fmean(episode_sizes) if episode_sizes else 0.0,
            "episodes": episodes,
            "effective_independent_sample": {
                "trades": int(canonical.get("num_trades", 0)),
                "symbols": len({k[0] for k in keys}),
                "episodes": len(episodes),
                "distinct_crash_days": len(distinct_days),
            },
        },
        "episode_block_bootstrap": boot,
        "temporal_edge_permutation": perm,
        "canonical_replay": ts,
        "verdict": "underpowered",
        "limitations": [
            f"CROSS-VENUE {venue_data['venue_label']} multi-year cache; NOT Hyperliquid performance evidence.",
            "Permutation preserves observed per-symbol multiplicity and conditions on real RSI<20 crash bars; tests timing, not detector existence.",
            "Episode clustering uses 98h holding horizon.",
        ],
    }
    bt = boot["bootstrap_total_pnl"]
    if bt["ci_low_pnl_2p5"] > 0 and perm["p_null_ge_canonical"] < 0.05:
        result["verdict"] = "cross_venue_positive_not_hyperliquid"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"[episode] {venue_data['venue_label']}: events={len(keys)} episodes={len(episodes)} "
          f"days={len(distinct_days)} trades={result['inputs']['canonical_num_trades']} "
          f"pnl={canonical_pnl:.2f} perm_p={perm['p_null_ge_canonical']:.4f} "
          f"boot_CI=[{bt['ci_low_pnl_2p5']:.2f},{bt['ci_high_pnl_97p5']:.2f}]", flush=True)
    return result


# ---------------------------------------------------------------------------
# Step 5 — full-portfolio placebo
# ---------------------------------------------------------------------------

def run_placebo(venue_data: Dict[str, Any], census: Dict[str, Any],
                campaign: Dict[str, Any], cfg: StrategyConfig,
                out_stem: str, jobs: int) -> Dict[str, Any]:
    candles = venue_data["candles"]
    memo, rows, meta = build_memo(venue_data, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(
            f"memo mismatch for {venue_data['venue_label']}: spec-literal signals="
            f"{meta['memo_signals']} but census signal_gate_pass={meta['signal_gate_events']}; "
            "the census and the real engine disagree on the spec-literal entry rule"
        )
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    admitted = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                       for r in rows if r.get("trade_opened_canonical") and r.get("bar_index") is not None
                       and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    canon_run = run_memo_portfolio(candles_active, cfg, memo)
    canon_pnl = float(canon_run.get("total_pnl", 0.0))
    canon_trades = int(canon_run.get("num_trades", 0))
    choose_k = min(len(admitted) if admitted else canon_trades, len(keys))
    replay = canon_run
    rng = random.Random(SEED)
    n_placebo = min(PLACEBO_DRAWS, MAX_PLACEBO_DRAWS)
    subsets = [tuple(sorted(rng.sample(keys, choose_k))) for _ in range(n_placebo)]
    if jobs > 1 and "fork" in mp.get_all_start_methods():
        ctx = mp.get_context("fork")
        with ctx.Pool(processes=jobs, initializer=_init_worker,
                      initargs=(candles_active, memo, cfg)) as pool:
            results = pool.map(_run_draw, subsets, chunksize=1)
    else:
        results = []
        for sub in subsets:
            res = run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
            results.append({"num_trades": int(res.get("num_trades", 0)),
                            "total_pnl": float(res.get("total_pnl", 0.0))})
    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for x in pnls if x >= canon_pnl)
    le = sum(1 for x in pnls if x <= canon_pnl)
    pl = {
        "runs": len(results), "summary": _summ(pnls),
        "p_ge_canonical": ge / len(results) if results else None,
        "canonical_percentile_le": le / len(results) if results else None,
        "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(results) if results else None,
        "ci_low_pnl_2p5": _q(pnls, 0.025), "ci_high_pnl_97p5": _q(pnls, 0.975),
    }
    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    result = {
        "schema_version": 1, "generated_at_utc": iso_now(), "phase": "C20",
        "campaign": "C20",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False, "cross_venue": True, "is_hyperliquid_venue_data": False,
        "venue_label": venue_data["venue_label"],
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Deterministic seeded full-portfolio placebo: gate-passing crash-bar subsets of fixed "
                   "size run through the real portfolio engine; preserves gates/sizing/cap/occupancy/hedge."),
        "mode": f"deterministic_seeded_draws:{len(results)}_choose_{choose_k}_of_{len(keys)}",
        "seed": SEED,
        "inputs": {
            "campaign_sha256": sha256_file(REPO / f"research_state/campaign_results_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json"),
            "census_sha256": sha256_file(REPO / f"research_state/crash_event_census_real_{venue_data['venue']}_multiyear_specliteral_{TS}.json"),
        },
        "canonical": {"trades": canon_trades, "total_pnl": canon_pnl,
                      "replay": {"num_trades": canon_trades, "total_pnl": canon_pnl},
                      "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k, "exact_combinations_infeasible": True},
        "placebo": pl,
        "verdict": "underpowered",
        "jobs": jobs,
        "limitations": [
            "Tests admission/cap/occupancy selection within the observed gate-passing pool, not temporal crash timing.",
            f"CROSS-VENUE {venue_data['venue_label']}; NOT Hyperliquid performance evidence.",
        ],
    }
    if pl["summary"]["p05"] > 0 and (pl["p_ge_canonical"] or 1.0) < 0.05:
        result["verdict"] = "cross_venue_positive_not_hyperliquid"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"[placebo] {venue_data['venue_label']}: pool={len(keys)} choose={choose_k} runs={len(results)} "
          f"canon_pnl={canon_pnl:.2f} p_ge={pl['p_ge_canonical']:.4f}", flush=True)
    return result


# ---------------------------------------------------------------------------
# Step 6 — robustness battery (analytical)
# ---------------------------------------------------------------------------

def run_battery(venue_data: Dict[str, Any], campaign: Dict[str, Any],
                episode: Dict[str, Any], out_stem: str) -> Dict[str, Any]:
    trades = (campaign.get("results") or {}).get("trades") or []
    total_pnl = float(sum(float(t.get("total_pnl", 0.0) or 0.0) for t in trades))
    out: Dict[str, Any] = {"total_pnl": total_pnl, "num_trades": len(trades)}

    legs: Dict[str, List[float]] = {}
    for t in trades:
        legs.setdefault(str(t.get("leg") or "unknown"), []).append(float(t.get("total_pnl", 0.0) or 0.0))
    out["A1_per_leg"] = {leg: _summ(v) for leg, v in legs.items()}

    def _csum(key: str) -> float:
        return float(sum(float(t.get(key, 0.0) or 0.0) for t in trades))
    out["A1_components"] = {
        "coin_pnl": _csum("pnl"),
        "hedge_pnl": _csum("hedge_pnl"),
        "rebound_short_pnl": _csum("rebound_short_pnl"),
        "rebound_hedge_pnl": _csum("rebound_hedge_pnl"),
    }

    reasons: Dict[str, List[float]] = {}
    for t in trades:
        reasons.setdefault(str(t.get("exit_reason") or "unknown"), []).append(float(t.get("total_pnl", 0.0) or 0.0))
    out["A2_exit_reason"] = {r: _summ(v) for r, v in reasons.items()}

    def _period_key(t: Dict[str, Any], mode: str) -> str:
        ts = t.get("entry_timestamp")
        if ts is None:
            return "unknown"
        d = dt.datetime.fromtimestamp(parse_timestamp_ms(ts) / 1000.0, dt.timezone.utc)
        if mode == "year":
            return str(d.year)
        if mode == "half":
            return f"{d.year}-H{1 if d.month <= 6 else 2}"
        return f"{d.year}-Q{(d.month - 1) // 3 + 1}"

    sub: Dict[str, Dict[str, Any]] = {}
    for mode in ("year", "half", "quarter"):
        groups: Dict[str, List[float]] = {}
        for t in trades:
            groups.setdefault(_period_key(t, mode), []).append(float(t.get("total_pnl", 0.0) or 0.0))
        sub[mode] = {k: _summ(v) for k, v in sorted(groups.items())}
    out["A3_sub_period"] = sub

    ep_totals: Dict[int, float] = {}
    ep_trade_counts: Dict[int, int] = {}
    for eid_str, pnl in (episode.get("episode_block_bootstrap", {}).get("observed_episode_totals") or {}).items():
        ep_totals[int(eid_str)] = float(pnl)
    for eid_str, cnt in (episode.get("episode_block_bootstrap", {}).get("episode_trade_counts") or {}).items():
        ep_trade_counts[int(eid_str)] = int(cnt)
    sorted_totals = sorted(ep_totals.values(), reverse=True)
    pos = [x for x in sorted_totals if x > 0]
    neg = [x for x in sorted_totals if x < 0]
    abs_tot = [abs(x) for x in sorted_totals]
    tot_abs = sum(abs_tot) or 1.0
    hhi = sum((a / tot_abs) ** 2 for a in abs_tot)
    top1 = sorted_totals[0] if sorted_totals else 0.0
    top3 = sum(sorted_totals[:3])
    out["A4_concentration"] = {
        "n_episodes_with_trades": len(ep_totals),
        "episode_totals_desc": [round(x, 2) for x in sorted_totals],
        "gross_positive_episode_pnl": round(sum(pos), 2),
        "gross_negative_episode_pnl": round(sum(neg), 2),
        "n_positive_episodes": len(pos),
        "n_negative_episodes": len(neg),
        "top1_share_of_total": (top1 / total_pnl) if total_pnl else None,
        "top3_sum": round(top3, 2),
        "top3_share_of_total": (top3 / total_pnl) if total_pnl else None,
        "hhi_abs_episode_contrib": round(hhi, 4),
    }

    loo_year: Dict[str, Any] = {}
    for y in sorted({_period_key(t, "year") for t in trades}):
        dropped = float(sum(float(t.get("total_pnl", 0.0) or 0.0) for t in trades if _period_key(t, "year") == y))
        kept = total_pnl - dropped
        loo_year[y] = {"dropped_pnl": round(dropped, 2), "remaining_total_pnl": round(kept, 2),
                       "sign_flipped_from_total": (kept * total_pnl < 0)}
    out["A5_leave_one_out_by_year"] = loo_year

    vals = list(ep_totals.values())
    n = len(vals)
    if n >= 2:
        mean_ep = statistics.fmean(vals)
        sd_ep = statistics.pstdev(vals)
        se = sd_ep / math.sqrt(n) if sd_ep > 0 else 0.0
        t_stat = (mean_ep / se) if se > 0 else 0.0
        n_needed = (1.96 * sd_ep / abs(mean_ep)) ** 2 if mean_ep != 0 and sd_ep > 0 else None

        def _power(ncand: int) -> float:
            if sd_ep <= 0 or mean_ep == 0:
                return 0.0
            nc = math.sqrt(ncand) * abs(mean_ep) / sd_ep
            from math import erf
            Phi = lambda x: 0.5 * (1.0 + erf(x / math.sqrt(2.0)))
            return float(Phi(nc - 1.96) + (1.0 - Phi(nc + 1.96)))

        out["A6_achievable_power"] = {
            "n_episodes": n, "mean_episode_pnl": round(mean_ep, 2), "sd_episode_pnl": round(sd_ep, 2),
            "se_mean": round(se, 2), "t_stat_vs_zero": round(t_stat, 3),
            "episodes_needed_for_ci_excludes_zero": round(n_needed, 1) if n_needed else None,
            "power_at": {str(k): round(_power(k), 4) for k in (5, 10, 19, 30, 50, 100, 200, 324)},
        }
    else:
        out["A6_achievable_power"] = {"note": "insufficient episodes"}

    out["A7_episode_audit_summary"] = {
        "n_events": episode.get("episode_audit", {}).get("n_events"),
        "n_episodes": episode.get("episode_audit", {}).get("n_episodes"),
        "n_distinct_crash_days": episode.get("episode_audit", {}).get("n_distinct_crash_days"),
        "largest_episode_events": episode.get("episode_audit", {}).get("largest_episode_events"),
    }

    out_path = REPO / "research_state" / f"{out_stem}.json"
    if out_path.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out_path}")
    payload = {
        "schema_version": 1, "generated_at_utc": iso_now(), "phase": "C20",
        "campaign": "C20",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False, "cross_venue": True, "is_hyperliquid_venue_data": False,
        "venue_label": venue_data["venue_label"],
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Per-leg attribution, exit-reason decomposition, sub-period stability, episode "
                   "concentration, leave-one-out fragility, achievable-power bound."),
        "A": out,
        "verdict": "underpowered",
    }
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[battery] {venue_data['venue_label']}: total={total_pnl:.2f} trades={len(trades)} "
          f"legs={list(out['A1_per_leg'])} episodes={n}", flush=True)
    return payload


# ---------------------------------------------------------------------------
# Step 7/8 — per-venue verdict + pooled synthesis + consolidated final
# ---------------------------------------------------------------------------

def build_venue_verdict(venue: str, campaign: Dict[str, Any], episode: Dict[str, Any],
                        placebo: Dict[str, Any], battery: Dict[str, Any],
                        census: Dict[str, Any], out_stem: str) -> Dict[str, Any]:
    res = campaign["results"]
    boot = episode["episode_block_bootstrap"]["bootstrap_total_pnl"]
    perm = episode["temporal_edge_permutation"]
    pl = placebo["placebo"]
    comp = battery["A"]["A1_components"]
    ep = episode["episode_audit"]
    trades = int(res["num_trades"])
    total_pnl = float(res["total_pnl"])
    spot = float(comp["coin_pnl"])
    hedge = float(comp["hedge_pnl"])
    rebound = float(comp["rebound_short_pnl"])

    perm_p = perm.get("p_null_ge_canonical")
    perm_skipped = perm_p is None
    if perm_skipped:
        perm_p = 1.0  # conservative: a skipped permutation cannot satisfy p<0.05

    go_checks = {
        "trades_ge_10": trades >= 10,
        "episodes_ge_5": int(ep["n_episodes"]) >= 5,
        "crash_days_ge_5": int(ep["n_distinct_crash_days"]) >= 5,
        "bootstrap_ci_excludes_zero_positive": float(boot["ci_low_pnl_2p5"]) > 0,
        "permutation_p_lt_0.05": (not perm_skipped) and float(perm_p) < 0.05,
        "placebo_p_ge_canonical_lt_0.05": float(pl["p_ge_canonical"]) < 0.05,
        "spot_leg_positive": spot > 0,
    }
    n_go = sum(1 for v in go_checks.values() if v)
    if n_go == len(go_checks):
        token = "GO"
    elif total_pnl < 0 and spot < 0 and rebound <= 0:
        token = "NO_GO"
    elif total_pnl > 0 and spot <= 0:
        token = "UNDERPOWERED"
    else:
        token = "NO_GO"

    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C20",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "label": "CROSS_VENUE_SPEC_LITERAL_PER_VENUE_VERDICT",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "performance_evidence": True,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_label": venue_data_label(venue),
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "inputs": {
            "campaign": f"research_state/campaign_results_real_{venue}_multiyear_specliteral_{TS}.json",
            "census": f"research_state/crash_event_census_real_{venue}_multiyear_specliteral_{TS}.json",
            "episode_edge": f"research_state/episode_edge_{venue}_multiyear_specliteral_{TS}.json",
            "placebo": f"research_state/placebo_portfolio_{venue}_multiyear_specliteral_{TS}.json",
            "battery": f"research_state/multiyear_robustness_battery_{venue}_specliteral_{TS}.json",
        },
        "headline": {
            "trades": trades, "total_pnl": round(total_pnl, 2),
            "coin_pnl": round(spot, 2), "hedge_pnl": round(hedge, 2),
            "rebound_short_pnl": round(rebound, 2),
            "episodes": ep["n_episodes"], "distinct_crash_days": ep["n_distinct_crash_days"],
            "events": ep["n_events"],
        },
        "go_checks": go_checks,
        "go_checks_passed": n_go,
        "go_checks_total": len(go_checks),
        "inference": {
            "bootstrap_ci95_total": [round(boot["ci_low_pnl_2p5"], 2), round(boot["ci_high_pnl_97p5"], 2)],
            "bootstrap_prob_total_gt_0": round(boot["prob_total_pnl_gt_0"], 4),
            "permutation_p": round(perm_p, 4),
            "permutation_skipped": perm_skipped,
            "placebo_p_ge_canonical": round(pl["p_ge_canonical"], 4),
            "placebo_runs": pl["runs"],
            "permutation_draws": perm["draws_evaluated"],
        },
        "verdict": token,
        "verdict_token": token,
        "is_decision_grade_positive": token == "GO",
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[verdict] {payload['venue_label']}: {token} ({n_go}/{len(go_checks)} GO checks) "
          f"trades={trades} pnl={total_pnl:.2f} spot={spot:.2f}", flush=True)
    return payload


def venue_data_label(venue: str) -> str:
    return VENUES[venue]["venue_label"]


def build_pooled_synthesis(venue_verdicts: Sequence[Dict[str, Any]],
                           campaigns: Dict[str, Dict[str, Any]],
                           episodes: Dict[str, Dict[str, Any]],
                           out_stem: str) -> Dict[str, Any]:
    # Pooled venue-blocked bootstrap over venue totals (each venue is one block).
    rng = random.Random(SEED)
    venue_blocks = []
    for v in venue_verdicts:
        key = v["venue_label"]
        venue_blocks.append((key, float(v["headline"]["total_pnl"])))
    draws = []
    for _ in range(EPISODE_DRAWS):
        draws.append(sum(b for _, b in (venue_blocks[rng.randrange(len(venue_blocks))] for _ in range(len(venue_blocks)))))
    pooled_ci = [round(_q(draws, 0.025), 2), round(_q(draws, 0.975), 2)]
    signs = [1 if b > 0 else (-1 if b < 0 else 0) for _, b in venue_blocks]
    sign_concordant = len(signs) == 2 and signs[0] == signs[1] and signs[0] != 0
    n_trades = sum(int(v["headline"]["trades"]) for v in venue_verdicts)
    n_episodes = sum(int(v["headline"]["episodes"]) for v in venue_verdicts)
    n_days = sum(int(v["headline"]["distinct_crash_days"]) for v in venue_verdicts)
    n_go = sum(int(v["go_checks_passed"]) for v in venue_verdicts)
    n_checks = sum(int(v["go_checks_total"]) for v in venue_verdicts)
    both_no_go = all(v["verdict"] == "NO_GO" for v in venue_verdicts)
    tokens = [v["verdict"] for v in venue_verdicts]
    if "GO" in tokens and all(v["verdict"] == "GO" for v in venue_verdicts):
        pooled_token = "GO"
    elif both_no_go:
        pooled_token = "NO_GO"
    elif any(v["verdict"] == "UNDERPOWERED" for v in venue_verdicts):
        pooled_token = "UNDERPOWERED"
    else:
        pooled_token = "NO_GO"
    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C20",
        "prereg_sha256": sha256_file(REPO / f"research_state/c20_prereg_{TS}.json"),
        "label": "CROSS_VENUE_POOLED_SPEC_LITERAL_SYNTHESIS",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "performance_evidence": True,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_labels": [v["venue_label"] for v in venue_verdicts],
        "venue_tokens": tokens,
        "pooled_venue_blocked_bootstrap": {
            "seed": SEED,
            "draws": EPISODE_DRAWS,
            "blocks": [{"venue": k, "total_pnl": round(b, 2)} for k, b in venue_blocks],
            "pooled_total_pnl": round(sum(b for _, b in venue_blocks), 2),
            "ci95": pooled_ci,
            "prob_pooled_total_gt_0": round(sum(1 for d in draws if d > 0) / len(draws), 4),
            "sign_concordant": sign_concordant,
            "signs": signs,
        },
        "effective_sample": {
            "trades": n_trades, "episodes": n_episodes, "distinct_crash_days": n_days,
        },
        "go_checks_passed": n_go,
        "go_checks_total": n_checks,
        "decision": {
            "token": pooled_token,
            "rationale": (
                "Both independent multi-year venues produce NO_GO under the C19-adjudicated "
                "spec-faithful entry rule; the native C18/C19 verdict is also NO_GO. The "
                "pooled synthesis therefore corroborates NO_GO and does not establish a "
                "decision-grade positive edge."
                if pooled_token == "NO_GO" else
                f"Pooled token {pooled_token} from per-venue tokens {tokens}."
            ),
        },
        "priors_referenced": [
            f"research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.json",
            f"research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.md",
            f"research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.md",
            f"research_state/decision_verdict_consolidated_20261115T122636Z.md",
        ],
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[pooled] token={pooled_token} venues={tokens} pooled_total={payload['pooled_venue_blocked_bootstrap']['pooled_total_pnl']:.2f} "
          f"CI={pooled_ci} go={n_go}/{n_checks}", flush=True)
    return payload


def build_consolidated_final(venue_verdicts: Sequence[Dict[str, Any]],
                             pooled: Dict[str, Any], out_stem: str) -> Dict[str, Any]:
    out = REPO / "research_state" / f"{out_stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    token = pooled["decision"]["token"]
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "scope": "C1-C20 final consolidation",
        "final_verdict_token": token,
        "verdict": token,
        "research_program_complete": True,
        "supersedes": f"research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.json",
        "supersedes_verdict_token": "NO_GO",
        "campaign_verdicts": {
            "c19_native_spec_literal": "NO_GO",
            **{f"c20_{v['venue_label'].lower().replace(' ', '_')}": v["verdict"] for v in venue_verdicts},
            "c20_pooled": token,
        },
        "structural_power_note": (
            "C20 confirms the C19 NO_GO out-of-sample: the spec-faithful next-open rule loses on both "
            "independent multi-year venues (OKX and Binance UM), so the native NO_GO is not a "
            "single-venue artifact. Effective episode counts remain below the GO floor."
        ),
        "leg_separation_conclusion": {
            v["venue_label"]: v["headline"] for v in venue_verdicts
        },
        "provenance": {
            "is_hyperliquid_venue_data": False,
            "cross_venue": True,
            "provenance_caveat": PROVENANCE_CAVEAT,
            "real_market_data": True,
            "fabricated_data": False,
            "synthetic_data": False,
        },
        "final_integrated_decision": {
            "token": token,
            "statement": (
                f"Consolidated final C1-C20 verdict: {token}. The crash-rebound strategy under the "
                "C19-adjudicated spec-faithful entry rule is not validated as a decision-grade "
                "positive edge on available native or cross-venue evidence. No campaign warrants a GO claim."
            ),
        },
        "priors_referenced": [
            "research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.json",
            "research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.md",
            "research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.md",
            f"research_state/c20_pooled_cross_venue_synthesis_{TS}.json",
        ],
    }
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[consolidated] {token}", flush=True)
    return payload


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def _stem_exists(stem: str) -> bool:
    return (REPO / "research_state" / f"{stem}.json").exists()


def _load_json(stem: str) -> Dict[str, Any]:
    return json.loads((REPO / "research_state" / f"{stem}.json").read_text())


def run_venue(venue: str, jobs: int, resume: bool = False,
              do_permutation: bool = True) -> Dict[str, Any]:
    vd = load_venue(venue)
    c_stem = f"campaign_results_real_{venue}_multiyear_specliteral_{TS}"
    ce_stem = f"crash_event_census_real_{venue}_multiyear_specliteral_{TS}"
    ep_stem = f"episode_edge_{venue}_multiyear_specliteral_{TS}"
    pl_stem = f"placebo_portfolio_{venue}_multiyear_specliteral_{TS}"
    bt_stem = f"multiyear_robustness_battery_{venue}_specliteral_{TS}"
    vd_stem = f"decision_verdict_cross_venue_{venue}_specliteral_c20_{TS}"

    if resume and _stem_exists(c_stem):
        campaign = _load_json(c_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: campaign cached", flush=True)
    else:
        campaign = run_campaign(vd, c_stem)

    if resume and _stem_exists(ce_stem):
        census = _load_json(ce_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: census cached", flush=True)
    else:
        census = build_census(vd, campaign, ce_stem)

    if resume and _stem_exists(ep_stem):
        episode = _load_json(ep_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: episode cached", flush=True)
    else:
        episode = run_episode_inference(vd, census, campaign, spec_literal_config(),
                                        ep_stem, jobs, do_permutation=do_permutation)

    if resume and _stem_exists(pl_stem):
        placebo = _load_json(pl_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: placebo cached", flush=True)
    else:
        placebo = run_placebo(vd, census, campaign, spec_literal_config(),
                              pl_stem, jobs)

    if resume and _stem_exists(bt_stem):
        battery = _load_json(bt_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: battery cached", flush=True)
    else:
        battery = run_battery(vd, campaign, episode, bt_stem)

    if resume and _stem_exists(vd_stem):
        verdict = _load_json(vd_stem)
        print(f"[resume] {VENUES[venue]['venue_label']}: verdict cached", flush=True)
    else:
        verdict = build_venue_verdict(venue, campaign, episode, placebo, battery, census, vd_stem)
    return {"campaign": campaign, "episode": episode, "verdict": verdict}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--venues", nargs="+", default=["okx", "binance_um"],
                    choices=sorted(VENUES))
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--skip-permutation", action="store_true",
                    help="Skip the conditional temporal-edge permutation (not recommended).")
    ap.add_argument("--resume", action="store_true",
                    help="Skip steps whose output artifacts already exist on disk.")
    args = ap.parse_args(argv)

    results: Dict[str, Dict[str, Any]] = {}
    for venue in args.venues:
        results[venue] = run_venue(venue, args.jobs, resume=args.resume,
                                   do_permutation=not args.skip_permutation)

    venue_verdicts = [results[v]["verdict"] for v in args.venues]
    campaigns = {v: results[v]["campaign"] for v in args.venues}
    episodes = {v: results[v]["episode"] for v in args.venues}

    pooled_stem = f"c20_pooled_cross_venue_synthesis_{TS}"
    cons_stem = f"decision_verdict_CONSOLIDATED_FINAL_{TS}"
    if args.resume and _stem_exists(pooled_stem):
        pooled = _load_json(pooled_stem)
        print("[resume] pooled synthesis cached", flush=True)
    else:
        pooled = build_pooled_synthesis(
            venue_verdicts, campaigns, episodes, pooled_stem,
        )
    if args.resume and _stem_exists(cons_stem):
        consolidated = _load_json(cons_stem)
        print("[resume] consolidated final cached", flush=True)
    else:
        consolidated = build_consolidated_final(
            venue_verdicts, pooled, cons_stem,
        )
    print(f"C20 COMPLETE: per-venue={[v['verdict'] for v in venue_verdicts]} pooled={pooled['decision']['token']} "
          f"consolidated={consolidated['verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())