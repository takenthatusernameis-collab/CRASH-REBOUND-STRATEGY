"""Campaign performance metrics for the crash-rebound strategy.

Computes a full metrics suite from a portfolio simulation result, robust to
empty / no-trade runs. All rate-style metrics are expressed as decimals
(e.g. 0.05 == 5%) unless otherwise noted.
"""

import math
from datetime import datetime


def compute_metrics_from_trades(trades):
    trades = trades or []
    pnls = [t.get("pnl", t.get("total_pnl", 0.0)) for t in trades]
    total_pnl = sum(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    win_rate = (len(wins) / len(pnls)) if pnls else 0.0
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss else (float("inf") if gross_profit > 0 else 0.0)
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
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    max_dd_ts = None
    for t in trades:
        equity += t.get("pnl", t.get("total_pnl", 0.0))
        if equity > peak:
            peak = equity
        dd = equity - peak
        if dd < max_dd:
            max_dd = dd
            max_dd_ts = t.get("exit_timestamp") or t.get("timestamp")
    calmar = (total_pnl / abs(max_dd)) if max_dd != 0 else 0.0
    monthly = {}
    weekly = {}
    for t in trades:
        ts = t.get("exit_timestamp") or t.get("entry_timestamp") or t.get("timestamp")
        key_m = (ts[:7] if isinstance(ts, str) and len(ts) >= 7 else "unknown")
        key_w = (ts[:10] if isinstance(ts, str) and len(ts) >= 10 else "unknown")
        monthly[key_m] = monthly.get(key_m, 0.0) + t.get("pnl", t.get("total_pnl", 0.0))
        weekly[key_w] = weekly.get(key_w, 0.0) + t.get("pnl", t.get("total_pnl", 0.0))
    attribution = []
    by_symbol = {}
    for t in trades:
        sym = t.get("symbol", "unknown")
        by_symbol.setdefault(sym, {"symbol": sym, "pnl": 0.0, "trades": 0})
        by_symbol[sym]["pnl"] += t.get("pnl", t.get("total_pnl", 0.0))
        by_symbol[sym]["trades"] += 1
    attribution = list(by_symbol.values())
    exposure = {
        "total_trades": len(trades),
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "total_pnl": total_pnl,
    }
    return {
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown": max_dd,
        "max_drawdown_timestamp": max_dd_ts,
        "calmar_ratio": calmar,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "monthly_breakdown": monthly,
        "weekly_breakdown": weekly,
        "trade_attribution": attribution,
        "exposure_metrics": exposure,
    }


def compute_campaign_metrics(result=None, trades=None, **kwargs):
    if trades is None and isinstance(result, dict):
        trades = result.get("trades", [])
    if trades is None:
        trades = []
    m = compute_metrics_from_trades(trades)
    m["timestamp"] = datetime.now().isoformat()
    return m


def metrics_to_dict(metrics):
    out = dict(metrics or {})
    for k, v in list(out.items()):
        if isinstance(v, float) and not math.isfinite(v):
            out[k] = 0.0
    return out


def metrics_to_csv_rows(metrics):
    metrics = metrics or {}
    rows = []
    for k, v in metrics.items():
        if isinstance(v, (dict, list)):
            continue
        rows.append({"metric": k, "value": v})
    return rows
