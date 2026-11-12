"""Campaign performance metrics for the crash-rebound strategy.

Computes a full metrics suite from a portfolio simulation result, robust to
empty / no-trade runs. All rate-style metrics are expressed as decimals
(e.g. 0.05 == 5%) unless otherwise noted.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _trade_pnl(t: Dict[str, Any]) -> float:
    # Grand total across all legs (coin + hedge + rebound short + rebound hedge),
    # mirroring TradeResult.__init__ default semantics. Explicit `total_pnl` stays
    # authoritative (engine/runtime path). Never fall back to bare `pnl`, which
    # silently drops rebound legs and corrupts attribution/aggregation.
    if "total_pnl" in t and t["total_pnl"] is not None:
        return _finite(t["total_pnl"])
    return _finite(
        _finite(t.get("pnl", 0.0))
        + _finite(t.get("hedge_pnl", 0.0))
        + _finite(t.get("rebound_short_pnl", 0.0))
        + _finite(t.get("rebound_hedge_pnl", 0.0)),
    )


def _trade_ts(t: Dict[str, Any], *keys: str) -> Optional[str]:
    for k in keys:
        v = t.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
        # accept numeric epoch ms/seconds for deterministic provenance-aligned artifacts
        if isinstance(v, (int, float)) and math.isfinite(v):
            iv = int(v)
            # heuristic: ms if large
            if abs(iv) > 10_000_000_000:
                dt = datetime.fromtimestamp(iv / 1000.0, tz=timezone.utc)
            else:
                dt = datetime.fromtimestamp(iv, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    return None


def _parse_dt(ts: Optional[str]):
    if not ts or not isinstance(ts, str):
        return None
    s = ts.strip()
    if not s:
        return None
    try:
        # Handle ISO strings; tolerate trailing Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _week_key(ts: Optional[str]) -> str:
    dt = _parse_dt(ts)
    if dt is None:
        return (ts[:10] if isinstance(ts, str) and len(ts) >= 10 else "unknown")
    iso = dt.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def _month_key(ts: Optional[str]) -> str:
    if isinstance(ts, str) and len(ts) >= 7:
        return ts[:7]
    dt = _parse_dt(ts)
    if dt is None:
        return "unknown"
    return f"{dt.year}-{dt.month:02d}"


def compute_metrics_from_trades(trades: Optional[List[Dict[str, Any]]]):
    trades = list(trades or [])
    pnls = [_trade_pnl(t) for t in trades]
    total_pnl = sum(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    win_rate = (len(wins) / len(pnls)) if pnls else 0.0
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss else (1.0 if gross_profit > 0 else 0.0)
    if not math.isfinite(profit_factor):
        profit_factor = 0.0

    returns = pnls
    mean_r = (sum(returns) / len(returns)) if returns else 0.0
    var = (sum((r - mean_r) ** 2 for r in returns) / len(returns)) if returns else 0.0
    std = math.sqrt(var) if var > 0 else 0.0
    sharpe = (mean_r / std) if std > 0 else 0.0

    downside = [r for r in returns if r < 0]
    down_var = (sum(r ** 2 for r in downside) / len(downside)) if downside else 0.0
    down_std = math.sqrt(down_var) if down_var > 0 else 0.0
    sortino = (mean_r / down_std) if down_std > 0 else 0.0

    # Drawdown series with timestamps (cumulative PnL equity curve).
    # Prefer exit_timestamp for realized-PnL attribution; fall back deterministically.
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    max_dd_ts = None
    max_dd_series: List[Dict[str, Any]] = []
    for t in trades:
        pnl = _trade_pnl(t)
        equity = _finite(equity + pnl)
        if equity > peak:
            peak = equity
        dd = _finite(equity - peak)  # <= 0
        ts = _trade_ts(t, "exit_timestamp", "timestamp", "entry_timestamp")
        max_dd_series.append({"timestamp": ts, "equity": equity, "drawdown": dd})
        if dd < max_dd:
            max_dd = dd
            max_dd_ts = ts
    calmar = (total_pnl / abs(max_dd)) if max_dd < 0 else 0.0

    monthly: Dict[str, float] = defaultdict(float)
    weekly: Dict[str, float] = defaultdict(float)
    for t in trades:
        ts = _trade_ts(t, "exit_timestamp", "entry_timestamp", "timestamp")
        monthly[_month_key(ts)] += _trade_pnl(t)
        weekly[_week_key(ts)] += _trade_pnl(t)

    # Trade-level attribution by symbol/leg
    by_symbol: Dict[str, Dict[str, Any]] = {}
    by_leg: Dict[str, Dict[str, Any]] = {}
    for t in trades:
        sym = t.get("symbol", "unknown")
        leg = t.get("side", t.get("leg", "unknown"))
        pnl = _trade_pnl(t)
        coin_pnl = _finite(t.get("pnl", pnl))
        hedge_pnl = _finite(t.get("hedge_pnl", 0.0))
        s = by_symbol.setdefault(sym, {"symbol": sym, "pnl": 0.0, "trades": 0, "coin_pnl": 0.0, "hedge_pnl": 0.0})
        s["pnl"] += pnl
        s["coin_pnl"] += coin_pnl
        s["hedge_pnl"] += hedge_pnl
        s["trades"] += 1
        lg = by_leg.setdefault(str(leg), {"leg": str(leg), "pnl": 0.0, "trades": 0})
        lg["pnl"] += pnl
        lg["trades"] += 1
    attribution = list(by_symbol.values())
    attribution_by_leg = list(by_leg.values())

    # Per-leg breakdown: win rate, profit factor, R-multiple mean, and PnL share.
    # The PDF spec cites per-leg statistics explicitly ("73 buys (71% profitable),
    # 12 shorts (83% profitable)", "rebound short contributes ~27% of profit"), so
    # this decomposition must be machine-checkable, not just an aggregate win_rate.
    leg_breakdown = _compute_leg_breakdown(trades, total_pnl)

    exposure = {
        "total_trades": len(trades),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "total_pnl": total_pnl,
        "avg_pnl_per_trade": (total_pnl / len(trades)) if trades else 0.0,
        "winning_trades": len(wins),
        "losing_trades": len(losses),
    }

    return {
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
        "max_drawdown_timestamp": max_dd_ts,
        "max_drawdown_series": max_dd_series,
        "calmar_ratio": calmar,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "monthly_breakdown": dict(monthly),
        "weekly_breakdown": dict(weekly),
        "trade_attribution": attribution,
        "trade_attribution_by_leg": attribution_by_leg,
        "leg_breakdown": leg_breakdown,
        "exposure_metrics": exposure,
    }


def _leg_key(t: Dict[str, Any]) -> str:
    """Determine the leg of a trade for per-leg attribution.

    Prefers an explicit 'leg' field; falls back to 'side'. Unknown legs are
    bucketed under 'unknown' so attribution never silently drops a trade.
    """
    leg = t.get("leg")
    if isinstance(leg, str) and leg.strip():
        return leg.strip()
    side = t.get("side")
    if isinstance(side, str) and side.strip():
        return side.strip()
    return "unknown"


def _compute_leg_breakdown(trades: List[Dict[str, Any]], total_pnl: float) -> List[Dict[str, Any]]:
    """Per-leg win rate / profit factor / avg R-multiple / PnL share."""
    groups: Dict[str, List[float]] = {}
    r_groups: Dict[str, List[float]] = {}
    for t in trades:
        key = _leg_key(t)
        groups.setdefault(key, []).append(_trade_pnl(t))
        r = _finite(t.get("r_multiple"))
        r_groups.setdefault(key, []).append(r)

    out: List[Dict[str, Any]] = []
    for leg, pnls in groups.items():
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        gp = sum(wins)
        gl = abs(sum(losses))
        pf = (gp / gl) if gl else (1.0 if gp > 0 else 0.0)
        if not math.isfinite(pf):
            pf = 0.0
        rs = r_groups.get(leg, [])
        avg_r = (sum(rs) / len(rs)) if rs else 0.0
        if not math.isfinite(avg_r):
            avg_r = 0.0
        pnl = sum(pnls)
        share = (pnl / total_pnl * 100.0) if total_pnl else 0.0
        if not math.isfinite(share):
            share = 0.0
        out.append({
            "leg": leg,
            "trades": len(pnls),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": (len(wins) / len(pnls)) if pnls else 0.0,
            "gross_profit": gp,
            "gross_loss": gl,
            "profit_factor": pf,
            "total_pnl": pnl,
            "avg_r_multiple": avg_r,
            "pnl_share_pct": share,
        })
    out.sort(key=lambda d: d["leg"])
    return out


def _equity_series_for_fees(trades: List[Dict[str, Any]],
                            equity_curve: Optional[List[Any]] = None,
                            initial_capital: float = 100000.0):
    """Build gross equity series for vault-fee accrual.

    Prefer an explicit equity_curve when provided (ordered points with equity/value).
    Otherwise derive from cumulative trade PnL starting at initial_capital.
    """
    if equity_curve and isinstance(equity_curve, list):
        vals = []
        for pt in equity_curve:
            if not isinstance(pt, dict):
                continue
            vals.append(_finite(pt.get("equity", pt.get("value", initial_capital)), default=initial_capital))
        if vals:
            return vals
    eq = _finite(initial_capital, default=0.0)
    series = [eq]
    for t in trades:
        eq = _finite(eq + _trade_pnl(t))
        series.append(eq)
    return series


def _attach_vault_fee_metrics(m: Dict[str, Any], trades: List[Dict[str, Any]],
                              equity_curve=None, **kwargs):
    """Optionally compute and attach vault fee reconciliation metrics.

    Enabled when apply_vault_fees=True or when explicit fee config/inputs are
    provided (initial_capital with fee intent). Default behavior (no flags)
    leaves existing metrics shape unchanged.
    """
    apply_fees = bool(kwargs.get("apply_vault_fees", False))
    initial_capital = kwargs.get("initial_capital", None)
    if not apply_fees and initial_capital is None and "aum_rate_annual" not in kwargs and "profit_share_rate" not in kwargs:
        return m
    cap = _finite(initial_capital, default=100000.0)
    hours_per_step = kwargs.get("fee_hours_per_step", 1.0)
    aum_rate = kwargs.get("aum_rate_annual", None)
    ps_rate = kwargs.get("profit_share_rate", None)

    series = _equity_series_for_fees(trades, equity_curve=equity_curve, initial_capital=cap)
    # Lazy import to keep core metrics usable even if fee module missing in isolation.
    from src.metrics.vault_fees import accrue_vault_fees, DEFAULT_AUM_FEE_ANNUAL, DEFAULT_PROFIT_SHARE
    fee_kwargs = {
        "hours_per_step": hours_per_step,
        "initial_hwm": kwargs.get("fee_initial_hwm", None),
        "include_steps": bool(kwargs.get("include_fee_steps", False)),
    }
    if aum_rate is not None:
        fee_kwargs["aum_rate_annual"] = _finite(aum_rate, DEFAULT_AUM_FEE_ANNUAL)
    if ps_rate is not None:
        fee_kwargs["profit_share_rate"] = _finite(ps_rate, DEFAULT_PROFIT_SHARE)
    summary = accrue_vault_fees(series, **fee_kwargs)

    gross_total = _finite(summary.final_equity_gross - _finite(series[0], cap))
    net_total = gross_total - _finite(summary.total_fees)
    fee_block = {
        "aum_fee_total": _finite(summary.aum_fee_total),
        "profit_share_total": _finite(summary.profit_share_total),
        "vault_fee_total": _finite(summary.total_fees),
        "gross_total_pnl": gross_total,
        "net_total_pnl": net_total,
        "gross_final_equity": _finite(summary.final_equity_gross),
        "net_final_equity": _finite(summary.final_equity_net),
        "vault_hwm_final": _finite(summary.final_hwm),
        "fee_hours_per_step": hours_per_step,
        "fee_time_base_hours_per_year": 8760.0,
    }
    if fee_kwargs.get("include_steps"):
        fee_block["vault_fee_steps"] = [s.as_dict() for s in summary.steps]
    m.update(fee_block)
    return m


def compute_campaign_metrics(result=None, trades=None, equity_curve=None, **kwargs):
    """Compute campaign metrics from a portfolio result dict, trade list, or kwargs.

    Accepts flexible inputs for compatibility:
    - trades=[...]
    - result={'trades': [...], ...}
    - equity_curve=[...] (if provided without trades, returns empty-trade-safe metrics
      with drawdown computed from equity curve when possible)

    Vault fee reconciliation (spec: 2%/yr AUM + 10% profit above HWM): opt-in via
    apply_vault_fees=True (or by passing fee-related kwargs with initial_capital).
    When enabled, attaches gross/net PnL & equity and fee components without
    altering existing trade-based aggregates (no double counting).
    """
    if trades is None and isinstance(result, dict):
        trades = result.get("trades")
        if equity_curve is None:
            equity_curve = result.get("equity_curve")
        # allow result to carry fee context
        for k in ("initial_capital", "capital", "apply_vault_fees", "fee_hours_per_step",
                  "aum_rate_annual", "profit_share_rate", "fee_initial_hwm", "include_fee_steps"):
            if k in result and k not in kwargs:
                kwargs[k] = result[k]
    if trades is None and "trades" in kwargs:
        trades = kwargs.get("trades")

    trades = list(trades or [])
    m = compute_metrics_from_trades(trades)

    # If no trades but an equity curve is provided, compute drawdown series from it.
    if not trades and equity_curve and isinstance(equity_curve, list):
        peak = None
        max_dd = 0.0
        max_dd_ts = None
        series = []
        for pt in equity_curve:
            if not isinstance(pt, dict):
                continue
            eq = _finite(pt.get("equity", pt.get("value", 0.0)))
            ts = pt.get("timestamp")
            if peak is None or eq > peak:
                peak = eq
            dd = (eq - peak) if peak is not None else 0.0
            series.append({"timestamp": ts, "equity": eq, "drawdown": dd})
            if dd < max_dd:
                max_dd = dd
                max_dd_ts = ts
        if series:
            m["max_drawdown"] = max_dd
            m["max_drawdown_timestamp"] = max_dd_ts
            m["max_drawdown_series"] = series
            # Calmar remains 0 without return context

    _attach_vault_fee_metrics(m, trades, equity_curve=equity_curve, **kwargs)
    m["timestamp"] = datetime.now().isoformat()
    return m


def metrics_to_dict(metrics: Optional[Dict[str, Any]]):
    out = dict(metrics or {})

    def _sanitize(v: Any):
        if isinstance(v, float):
            return v if math.isfinite(v) else 0.0
        if isinstance(v, dict):
            return {k: _sanitize(val) for k, val in v.items()}
        if isinstance(v, list):
            return [_sanitize(x) for x in v]
        return v

    return {k: _sanitize(v) for k, v in out.items()}


def metrics_to_csv_rows(metrics: Optional[Dict[str, Any]]):
    metrics = metrics or {}
    rows = []
    for k, v in metrics.items():
        if isinstance(v, (dict, list)):
            if k == "max_drawdown_series" and isinstance(v, list):
                # Represent series length as a scalar hint; full series lives in JSON.
                rows.append({"metric": "max_drawdown_series_points", "value": len(v)})
                continue
            if k == "leg_breakdown" and isinstance(v, list):
                # Emit one row per leg so per-leg win rate / profit factor / PnL share
                # are machine-checkable in the flat CSV (full detail in JSON).
                for leg in v:
                    if not isinstance(leg, dict):
                        continue
                    name = str(leg.get("leg", "unknown"))
                    for field in ("trades", "wins", "losses", "win_rate",
                                  "gross_profit", "gross_loss", "profit_factor",
                                  "total_pnl", "avg_r_multiple", "pnl_share_pct"):
                        rows.append({"metric": f"leg_breakdown.{name}.{field}",
                                     "value": leg.get(field)})
                continue
            continue
        if isinstance(v, float) and not math.isfinite(v):
            v = 0.0
        rows.append({"metric": k, "value": v})
    # Stable ordering
    rows.sort(key=lambda r: str(r.get("metric", "")))
    return rows
