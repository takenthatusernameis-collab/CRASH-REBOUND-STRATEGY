#!/usr/bin/env python3
"""Full-portfolio crash-rebound placebo for the exploratory spec-literal next-open
Hyperliquid path (retained PARTIAL chain).

WHY THIS EXISTS
---------------
C1 closed the exploratory spec-literal next-open adjudication: on the retained
aligned Hyperliquid chain the spec-literal entry rule (buy at next hourly open
after RSI(21)<20, bypassing ONLY the same-bar confirm_rebound gate) produced
8 generate_signal events -> 2 real-engine trades (BCH +559, BTC -3230),
total PnL -$2,671.  C1-T2 recorded the episode-aware audit as NOT_APPLICABLE
(n_episodes=2 < 10).  The missing inference artifact is a FULL-PORTFOLIO placebo
that isolates admission/cap/occupancy selection under the same gates, sizing,
120% gross cap, ETH hedge, fees, funding and liquidation as the real engine.

This script runs the REAL portfolio engine (scripts.run_portfolio.run_portfolio_simulation)
under a memoized ``generate_signal`` configured with ``entry_spec_literal_next_open=True``:

* Every RSI(21)<20 bar passing the trailing-24h >= $5M volume gate is enumerated
  from the real candles and the real ``generate_signal`` is evaluated exactly once
  per such bar (the signal-gate pool, n=11 on the retained chain).
* The memo is exact: restricting the memo to the canonical admitted events
  reproduces the exploratory campaign to the cent (2 trades, total PnL
  -2670.7567875859345). That canonical-equality check is a hard failure gate.
* For every k-of-n subset (k = canonical trade count = 2) the other signals are
  masked and the exact portfolio engine is re-run. With n=11 and k=2 there are
  C(11,2)=55 subsets, so this is an EXACT enumeration (no Monte Carlo error).

OUTPUT IS EXPLORATORY / NOT EVIDENCE:
``NOT_EVIDENCE_PLACEBO``. The retained window is a PARTIAL window with only a
handful of independent crash episodes; this placebo cannot create statistical
power the sample does not contain and is NEVER Hyperliquid performance evidence.

Outputs (new stems only; canonical artifacts are never overwritten):
* research_state/placebo_portfolio_hyperliquid_exploratory_next_open_<TS>.json
* research_state/placebo_portfolio_hyperliquid_exploratory_next_open_<TS>.md
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import _close, _volume, generate_signal as real_generate_signal  # noqa: E402
import scripts.run_portfolio as portfolio_mod  # noqa: E402
from scripts.run_hyperliquid_exploratory_next_open import rolling_volume_24h  # noqa: E402
from scripts.build_crash_event_census import _rsi_series  # noqa: E402

LABEL = "NOT_EVIDENCE_PLACEBO"
CAVEAT = (
    "Exploratory full-portfolio placebo on the retained PARTIAL aligned Hyperliquid "
    "chain; real fetched candles, non-synthetic; NOT the 283-day spec window and NOT "
    "performance evidence. Never use for validation or capital allocation. Canonical "
    "exploratory baseline is unchanged."
)
DEFAULT_CACHE = REPO / "research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z"
CANONICAL_PNL = -2670.7567875859345
CANONICAL_TRADES = 2
MAX_EXACT_COMBINATIONS = 500


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get("candles", data)
    return data


def load_cache(cache_dir: Path) -> Tuple[Dict[str, List[Dict[str, Any]]], List[str]]:
    candles_dir = cache_dir / "candles"
    if not candles_dir.exists():
        raise SystemExit(f"BLOCKER: candles dir missing: {candles_dir}")
    symbols = sorted(p.stem for p in candles_dir.glob("*.json"))
    if not symbols:
        raise SystemExit(f"BLOCKER: no symbol candle files in {candles_dir}")
    data: Dict[str, List[Dict[str, Any]]] = {}
    for sym in symbols:
        data[sym] = load_candles(candles_dir / f"{sym}.json")
    if "ETH" not in data:
        raise SystemExit("BLOCKER: retained chain has no ETH candles; ETH hedge cannot be verified.")
    return data, symbols


def build_cfg(min_daily_volume_usd: float) -> StrategyConfig:
    return StrategyConfig(
        use_rsi_trigger=True,
        enable_rebound_short=True,
        enable_eth_hedge=True,
        enable_volume_based_sizing=True,
        min_daily_volume_usd=min_daily_volume_usd,
        entry_spec_literal_next_open=True,
    )


def enumerate_signal_pool(
    data: Dict[str, List[Dict[str, Any]]], cfg: StrategyConfig
) -> Tuple[Dict[Tuple[str, int], Any], List[Dict[str, Any]]]:
    """Evaluate real generate_signal once per RSI<20, volume-passing bar.

    detect_crash (use_rsi_trigger=True) can only fire where RSI(21)<20, so the
    census of RSI<20 bars is the complete candidate set. The trailing-24h $5M
    gate is applied explicitly here so the pool matches the funnel's
    'rsi_crash_hours_passing_trailing_24h_5m_volume' stage (n=11).
    """
    memo: Dict[Tuple[str, int], Any] = {}
    rows: List[Dict[str, Any]] = []
    for sym, candles in sorted(data.items()):
        closes: List[float] = []
        for c in candles:
            close = _close(c)
            if close is None:
                raise ValueError(f"{sym}: bar without close; refusing to misalign RSI")
            closes.append(float(close))
        rsis = _rsi_series(closes, cfg.rsi_period)
        vols = rolling_volume_24h(candles)
        for i in range(len(candles)):
            rsi = rsis[i]
            if rsi is None or rsi >= cfg.rsi_threshold:
                continue
            vol = vols[i]
            if vol is None or vol < cfg.min_daily_volume_usd:
                continue
            sig = real_generate_signal(candles[: i + 1], symbol=sym, config=cfg, capital=100000.0)
            ts = candles[i].get("timestamp")
            row = {
                "symbol": sym,
                "bar_index": i,
                "bar_timestamp": ts,
                "rsi": rsi,
                "trailing_24h_volume_usd": vol,
                "signal": sig is not None,
            }
            if sig is not None:
                memo[(sym, i)] = sig
                row["signal_entry_price"] = getattr(sig, "entry_price", None)
                row["signal_size_shares"] = getattr(sig, "size_shares", None)
            rows.append(row)
    return memo, rows


def run_memo_portfolio(
    candles: Dict[str, List[Dict[str, Any]]],
    cfg: StrategyConfig,
    memo: Dict[Tuple[str, int], Any],
) -> Dict[str, Any]:
    active = {k: v for k, v in memo.items()}

    def memo_generate_signal(candles_arg, symbol="TEST", config=None, capital=100000.0,
                             risk_state=None, cache=None):
        return active.get((symbol, len(candles_arg) - 1))

    original = portfolio_mod.generate_signal
    portfolio_mod.generate_signal = memo_generate_signal
    try:
        return portfolio_mod.run_portfolio_simulation(
            candles,
            cfg,
            100000.0,
            {"ETH": candles["ETH"]},
            require_eth_hedge=True,
        )
    finally:
        portfolio_mod.generate_signal = original


def trade_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    trades = result.get("trades", [])
    return {
        "num_trades": int(result.get("num_trades", len(trades))),
        "total_pnl": float(result.get("total_pnl", 0.0) or 0.0),
        "symbols": sorted({str(t.get("symbol")) for t in trades}),
        "exit_reasons": {reason: sum(1 for t in trades if t.get("exit_reason") == reason)
                         for reason in sorted({str(t.get("exit_reason")) for t in trades})},
        "trades": [
            {
                "symbol": t.get("symbol"),
                "entry_timestamp": t.get("entry_timestamp"),
                "exit_timestamp": t.get("exit_timestamp"),
                "exit_reason": t.get("exit_reason"),
                "total_pnl": float(t.get("total_pnl", 0.0) or 0.0),
            }
            for t in trades
        ],
    }


def canonical_keys_from_rows(rows: List[Dict[str, Any]]) -> Set[Tuple[str, int]]:
    """Canonical admitted trades: rows whose signal fired at a crash day that the
    canonical exploratory run actually traded. We identify them by matching the
    canonical campaign's trade entry bars."""
    # The canonical run's trades are on 2026-05-28 and 2026-06-02. Rather than
    # hardcode, we derive candidate keys from the memo pool and let the caller
    # verify via exact replay; here we return all signal keys and rely on the
    # replay gate to pin the exact admitted subset.
    return {(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("signal")}


def quantile(sorted_vals: Sequence[float], p: float) -> float:
    if not sorted_vals:
        return float("nan")
    k = (len(sorted_vals) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_vals[int(k)])
    return float(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f))


def summarize(vals: Sequence[float]) -> Dict[str, Any]:
    if not vals:
        return {}
    s = sorted(float(v) for v in vals)
    import statistics
    return {
        "n": len(s),
        "mean": statistics.fmean(s),
        "median": statistics.median(s),
        "stdev": statistics.pstdev(s) if len(s) > 1 else 0.0,
        "min": s[0],
        "max": s[-1],
        "p05": quantile(s, 0.05),
        "p25": quantile(s, 0.25),
        "p75": quantile(s, 0.75),
        "p95": quantile(s, 0.95),
    }


def find_canonical_subset(
    memo: Dict[Tuple[str, int], Any],
    candles: Dict[str, List[Dict[str, Any]]],
    cfg: StrategyConfig,
    rows: List[Dict[str, Any]],
    canonical_trade_bars: List[Tuple[str, int]],
) -> Set[Tuple[str, int]]:
    """Pin the canonical admitted keys by matching canonical trade entry bars.

    canonical_trade_bars is the set of (symbol, entry_bar_index) from the canonical
    exploratory campaign's trades, translated to the decision bar on the full series
    (the signal_index that produced the trade). We accept the memo keys that match.
    """
    keys = {(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows if r.get("signal")}
    admitted = {k for k in canonical_trade_bars if k in keys}
    if len(admitted) != CANONICAL_TRADES:
        raise SystemExit(
            f"could not pin canonical admitted subset: matched {len(admitted)} of "
            f"{CANONICAL_TRADES} expected keys {canonical_trade_bars}"
        )
    return admitted


def render_md(result: Dict[str, Any]) -> str:
    can = result["canonical"]
    pl = result["placebo"]
    s = pl["summary"]
    lines = [
        "# Full-Portfolio Crash-Rebound Placebo — Hyperliquid Exploratory Spec-Literal Next-Open",
        "",
        f"**Generated (UTC):** {result['generated_at_utc']}  ",
        f"**Mode:** {result['mode']}  ",
        f"**Label:** `{result['label']}`  ",
        f"**Provenance caveat:** {result['provenance_caveat']}",
        "",
        "## What this fixes",
        "",
        "C1 closed the exploratory spec-literal next-open adjudication (8 signals -> "
        "2 trades, total PnL -$2,671) and recorded the episode audit as NOT_APPLICABLE "
        "(n=2 < 10). This placebo runs the **real portfolio engine** on the retained "
        "PARTIAL Hyperliquid chain under the same gates, sizing, 120% gross cap, ETH "
        "hedge, fees, funding and liquidation, varying only which of the volume-passing "
        "crash-rebound signal bars are admitted. It isolates admission/cap/occupancy "
        "selection, not the temporal edge versus random event times.",
        "",
        "## Canonical baseline (must reproduce exactly)",
        "",
        f"- Trades: **{can['trades']}**, total PnL: **{can['total_pnl']:.6f}**",
        f"- Canonical campaign artifact sha256: `{can['sha256']}`",
        f"- Memoized replay: {can['replay']['num_trades']} trades, PnL {can['replay']['total_pnl']:.6f} — exact match.",
        "",
        "## Placebo design (gate-preserving)",
        "",
        f"All {result['pool']['signal_gate_events']} RSI(21)<20 bars passing the "
        "trailing-24h >= $5M volume gate are the only bars where a spec-compliant "
        "trade can open. The canonical run admitted 2 (rest blocked by ETH hedge/"
        "120% cap/ETH availability). Every 2-of-n subset is run with the other "
        "signals masked, preserving every gate and the portfolio engine. With "
        f"n={result['pool']['signal_gate_events']} and k=2 there are "
        f"C(n,2)={result['pool']['exact_combinations']} subsets, so this is an "
        "**exact enumeration**, not a Monte Carlo estimate.",
        "",
        "## Result",
        "",
        f"- Placebo runs: **{pl['runs']}**",
        f"- Placebo total PnL: mean **{s['mean']:.2f}**, median **{s['median']:.2f}**, "
        f"p05 **{s['p05']:.2f}**, p95 **{s['p95']:.2f}**, min **{s['min']:.2f}**, max **{s['max']:.2f}**",
        f"- Canonical {CANONICAL_PNL:.2f} percentile: **{pl['canonical_percentile_le']:.4f}** "
        f"(P(placebo <= canonical) = **{pl['p_le_canonical']:.4f}**, P(>=) = {pl['p_ge_canonical']:.4f})",
        f"- P(placebo total PnL > 0): **{pl['prob_total_pnl_positive']:.4f}**",
        f"- 95% placebo interval: [{pl['ci_low_pnl_2p5']:.2f}, {pl['ci_high_pnl_97p5']:.2f}]",
        f"- Trade-count distribution: {pl['trade_count_distribution']}",
        f"- Symbol frequency: {pl['symbol_frequency']}",
        "",
        "## Interpretation",
        "",
        f"The canonical exploratory {CANONICAL_PNL:.2f} result sits at percentile "
        f"{pl['canonical_percentile_le']:.4f} of the exact full-portfolio placebo "
        "distribution. With only 2 independent crash episodes traded (C1-T1), this "
        "remains **`underpowered` / not decision-grade**; the placebo cannot create "
        "statistical power the sample does not contain. **Not** validation, **not** "
        "capital-allocation evidence.",
        "",
        "## Limitations",
        "",
    ]
    for lim in result["limitations"]:
        lines.append(f"- {lim}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", default=str(DEFAULT_CACHE))
    parser.add_argument("--min-daily-volume-usd", type=float, default=5_000_000.0)
    parser.add_argument("--out", default=None,
                        help="Default: research_state/placebo_portfolio_hyperliquid_exploratory_next_open_<TS>")
    args = parser.parse_args(argv)

    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = (REPO / cache_dir).resolve()
    data, symbols = load_cache(cache_dir)
    cfg = build_cfg(args.min_daily_volume_usd)

    t0 = time.time()
    memo, rows = enumerate_signal_pool(data, cfg)
    signal_keys = sorted(k for k, v in memo.items() if v is not None)
    if len(signal_keys) < CANONICAL_TRADES:
        raise SystemExit(
            f"only {len(signal_keys)} signal-gate events; need >= {CANONICAL_TRADES}"
        )

    # Canonical trade entry bars from the recorded exploratory campaign: BCH and BTC
    # both entered at 15:00 on their crash day. With entry_next_bar=True the engine
    # enters at the bar AFTER the signal bar, so the signal (decision) bar is the one
    # immediately before the entry timestamp. We locate the bar at/before the entry
    # timestamp and step back one bar to the signal bar.
    canonical_trade_bars: List[Tuple[str, int]] = []
    for sym, entry_ts in (("BCH", "2026-05-28T15:00:00+00:00"),
                           ("BTC", "2026-06-02T15:00:00+00:00")):
        candles = data.get(sym)
        if not candles:
            raise SystemExit(f"canonical symbol {sym} missing from retained chain")
        entry_idx = None
        for i, c in enumerate(candles):
            ts = str(c.get("timestamp") or "")
            if ts[:19] == entry_ts[:19]:
                entry_idx = i
                break
        if entry_idx is None or entry_idx == 0:
            raise SystemExit(f"could not locate {sym} entry bar {entry_ts}")
        canonical_trade_bars.append((sym, entry_idx - 1))

    canon_keys = find_canonical_subset(memo, data, cfg, rows, canonical_trade_bars)

    active_symbols = sorted({s for s, _ in memo} | {"ETH"})
    candles = {s: data[s] for s in active_symbols if s in data}
    if "ETH" not in candles:
        raise SystemExit("ETH candles missing; cannot run spec-compliant hedge")

    # Hard validation: restricting to the canonical admitted events must reproduce
    # the canonical exploratory campaign exactly (same trades and PnL).
    canon_run = run_memo_portfolio(candles, cfg, {k: memo[k] for k in canon_keys})
    canon_summary = trade_summary(canon_run)
    if (canon_summary["num_trades"] != CANONICAL_TRADES
            or abs(canon_summary["total_pnl"] - CANONICAL_PNL) > 1e-6):
        raise SystemExit(
            "canonical replay mismatch: "
            f"trades={canon_summary['num_trades']} pnl={canon_summary['total_pnl']!r} "
            f"expected {CANONICAL_TRADES}/{CANONICAL_PNL!r}"
        )

    total_comb = math.comb(len(signal_keys), CANONICAL_TRADES)
    subsets = list(itertools.combinations(signal_keys, CANONICAL_TRADES)) \
        if total_comb <= MAX_EXACT_COMBINATIONS else None
    if subsets is None:
        raise SystemExit(
            f"{total_comb} combinations exceeds MAX_EXACT_COMBINATIONS={MAX_EXACT_COMBINATIONS}; "
            "add --draws sampling before running"
        )
    mode = f"exact_enumeration:{len(subsets)}_subsets"

    results: List[Dict[str, Any]] = []
    for sub in subsets:
        sub_set = set(sub)
        t1 = time.time()
        res = run_memo_portfolio(candles, cfg, {k: memo[k] for k in sub_set})
        summ = trade_summary(res)
        results.append({
            "subset": [f"{s}@{i}" for s, i in sorted(sub_set)],
            "subset_keys": [f"{s}:{i}" for s, i in sorted(sub_set)],
            "num_trades": summ["num_trades"],
            "total_pnl": summ["total_pnl"],
            "symbols": summ["symbols"],
            "exit_reasons": summ["exit_reasons"],
            "is_canonical_subset": sub_set == canon_keys,
            "wall_seconds": time.time() - t1,
        })
    results.sort(key=lambda r: (r["total_pnl"], r["num_trades"], r["subset"]))

    pnls = [r["total_pnl"] for r in results]
    summary = summarize(pnls)
    le = sum(1 for x in pnls if x <= CANONICAL_PNL)
    ge = sum(1 for x in pnls if x >= CANONICAL_PNL)
    trade_counts: Dict[str, int] = {}
    for r in results:
        trade_counts[str(r["num_trades"])] = trade_counts.get(str(r["num_trades"]), 0) + 1
    symbol_counts: Dict[str, int] = {}
    for r in results:
        for s in r["symbols"]:
            symbol_counts[s] = symbol_counts.get(s, 0) + 1
    canonical_subset_result = next((r for r in results if r["is_canonical_subset"]), None)
    if canonical_subset_result is not None:
        if (canonical_subset_result["num_trades"] != CANONICAL_TRADES
                or abs(canonical_subset_result["total_pnl"] - CANONICAL_PNL) > 1e-6):
            raise SystemExit("canonical subset did not reproduce canonical result")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = Path(args.out) if args.out else REPO / f"research_state/placebo_portfolio_hyperliquid_exploratory_next_open_{ts}"
    if not str(out).startswith(str(REPO)):
        out = REPO / out

    campaign_artifact = REPO / "research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json"
    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "run_type": "hyperliquid_full_portfolio_placebo_exploratory_spec_literal_next_open",
        "label": LABEL,
        "research_status": LABEL,
        "real_market_data": True,
        "performance_evidence": False,
        "fabricated_data": False,
        "partial_universe_not_evidence": True,
        "canonical_baseline_changed": False,
        "provenance_caveat": CAVEAT,
        "method": (
            "Exact full-portfolio placebo: every 2-of-n gate-passing RSI(21)<20 crash-rebound "
            "signal-bar subset is run through the real portfolio engine with all other signals "
            "masked. The memoized generate_signal (entry_spec_literal_next_open=True) is exact and "
            "reproduces the canonical exploratory campaign to the cent."
        ),
        "mode": mode,
        "cache_dir": str(cache_dir.relative_to(REPO)) if str(cache_dir).startswith(str(REPO)) else str(cache_dir),
        "config": {
            "use_rsi_trigger": cfg.use_rsi_trigger,
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "entry_spec_literal_next_open": cfg.entry_spec_literal_next_open,
            "enable_rebound_short": cfg.enable_rebound_short,
            "enable_eth_hedge": cfg.enable_eth_hedge,
            "enable_volume_based_sizing": cfg.enable_volume_based_sizing,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
            "gross_cap_pct": cfg.gross_cap_pct,
        },
        "canonical": {
            "trades": CANONICAL_TRADES,
            "total_pnl": CANONICAL_PNL,
            "sha256": sha256_file(campaign_artifact) if campaign_artifact.exists() else None,
            "admitted_keys": [f"{s}:{i}" for s, i in sorted(canon_keys)],
            "replay": canon_summary,
        },
        "pool": {
            "signal_gate_events": len(signal_keys),
            "choose_k": CANONICAL_TRADES,
            "exact_combinations": total_comb,
            "event_keys": [f"{s}:{i}" for s, i in signal_keys],
        },
        "placebo": {
            "runs": len(results),
            "summary": summary,
            "p_le_canonical": le / len(results) if results else None,
            "p_ge_canonical": ge / len(results) if results else None,
            "canonical_percentile_le": le / len(results) if results else None,
            "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(results) if results else None,
            "ci_low_pnl_2p5": quantile(sorted(pnls), 0.025) if pnls else None,
            "ci_high_pnl_97p5": quantile(sorted(pnls), 0.975) if pnls else None,
            "trade_count_distribution": trade_counts,
            "symbol_frequency": symbol_counts,
            "canonical_subset_result": canonical_subset_result,
        },
        "runs": results,
        "event_rows": rows,
        "verdict": "underpowered",
        "limitations": [
            "Conditions on the observed volume-passing crash-rebound signal bars on the retained PARTIAL chain; tests admission/cap/occupancy selection, not the temporal crash-rebound edge versus random event times.",
            "Only 2 independent crash episodes traded (C1-T1); the placebo cannot create statistical power the sample does not contain.",
            "Memoized generate_signal is exact for the exploratory config/data (verified by exact canonical replay) but is not a general accelerator for other configs.",
            "Retained PARTIAL window, NOT the 283-day spec window; NEVER Hyperliquid performance evidence.",
        ],
        "wall_seconds": time.time() - t0,
    }

    out_json = Path(str(out) + ".json")
    out_md = Path(str(out) + ".md")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, default=str) + "\n")
    out_md.write_text(render_md(result))

    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    print(
        f"runs={result['placebo']['runs']} "
        f"mean={result['placebo']['summary']['mean']:.2f} "
        f"median={result['placebo']['summary']['median']:.2f} "
        f"canon_pct={result['placebo']['canonical_percentile_le']:.4f} "
        f"p_le_canon={result['placebo']['p_le_canonical']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())