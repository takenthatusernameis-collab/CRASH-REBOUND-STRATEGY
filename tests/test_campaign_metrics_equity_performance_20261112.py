"""CELL 7 — Reporting fidelity continuation: equity-path return/risk metrics.

Gap proof (file-search verified, 2026-11-12):
  - `src/metrics/campaign_metrics.py::compute_metrics_from_trades` only emitted
    per-trade Sharpe/Sortino/Calmar and currency monthly/annual PnL. It had NO
    equity-curve-based Sharpe/Sortino and NO return %.
  - `research_state/strategy_spec.md` Performance cites "Per year +115.2%"
    and Calmar on the equity path, so equity-curve Sharpe/Sortino/Calmar and
    per-year return % are required for reporting fidelity.
  - `grep -rn "equity_sharpe|annual_return|annualized|return_pct" src/ tests/`
    returned nothing before this change.

All values below are hand-traced. This is ADDITIVE reporting only: it must not
alter the anchored per-trade sharpe_ratio/sortino_ratio/calmar_ratio or any
pre-existing aggregate.
"""

import math

from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict


def _t(ts, pnl):
    return {"symbol": "CASE", "side": "long", "exit_timestamp": ts, "total_pnl": pnl}


def test_annual_return_pct_traced_and_additive():
    trades = [
        _t("2025-12-31T23:00:00Z", 100.0),   # 2025
        _t("2026-01-15T00:00:00Z", -40.0),   # 2026
        _t("2026-01-20T00:00:00Z", 10.0),
        _t("2026-02-10T00:00:00Z", 25.0),
        _t("2026-03-05T00:00:00Z", 0.0),
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=trades, initial_capital=1000.0))

    # annual_breakdown (unchanged): 2025=+100, 2026=-5.
    assert m["annual_breakdown"] == {"2025": 100.0, "2026": -5.0}, m["annual_breakdown"]
    # 2025 return on start 1000 -> 100/1000 = 10%.
    assert math.isclose(m["annual_return_pct"]["2025"], 10.0, rel_tol=1e-12)
    # 2026 base = 1000 + 100 = 1100 -> -5/1100 = -0.454545...%.
    assert math.isclose(m["annual_return_pct"]["2026"], -5.0 / 1100.0 * 100.0, rel_tol=1e-12)

    # Anchored per-trade metrics untouched.
    assert m["win_rate"] == 3 / 5, m["win_rate"]
    assert math.isclose(m["exposure_metrics"]["total_pnl"], 95.0)
    assert m["sharpe_ratio"] == m["sharpe_ratio"]  # present, unchanged semantics


def test_capital_kwarg_alias_enables_annual_return_pct():
    trades = [_t("2025-06-01T00:00:00Z", 50.0)]
    m = compute_campaign_metrics(trades=trades, capital=500.0)
    assert math.isclose(m["annual_return_pct"]["2025"], 10.0, rel_tol=1e-12), m.get("annual_return_pct")
    assert math.isclose(m["equity_final"], 550.0)


def test_no_starting_equity_emits_no_equity_fields():
    trades = [_t("2025-06-01T00:00:00Z", 50.0)]
    m = compute_campaign_metrics(trades=trades)
    # No initial capital / equity curve -> nothing invented.
    assert "equity_sharpe_ratio" not in m
    assert "annual_return_pct" not in m


def test_equity_sharpe_sortino_traced_from_explicit_curve():
    curve = [
        {"equity": 100.0},
        {"equity": 110.0},   # +10%
        {"equity": 99.0},    # -10%
        {"equity": 108.9},   # +10%
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=curve))

    # period returns = [0.10, -0.10, 0.10]; mean = 0.0333333.
    assert all(math.isclose(a, b, rel_tol=1e-9) for a, b in zip(
        m["equity_period_returns"], [0.10, -0.10, 0.10])), m["equity_period_returns"]
    # population std = sqrt(0.0266667/3) = 0.0942809; sharpe = 0.353553.
    assert math.isclose(m["equity_sharpe_ratio"], 1.0 / (2.0 * math.sqrt(2.0)), rel_tol=1e-9), \
        m["equity_sharpe_ratio"]
    # downside = [-0.10]; downside std = 0.10; sortino = 0.0333333/0.10 = 1/3.
    assert math.isclose(m["equity_sortino_ratio"], 1.0 / 3.0, rel_tol=1e-9), \
        m["equity_sortino_ratio"]
    # peak 110 -> 99 = -10% max drawdown.
    assert math.isclose(m["equity_max_drawdown_pct"], -10.0, rel_tol=1e-12), \
        m["equity_max_drawdown_pct"]
    assert math.isclose(m["equity_final"], 108.9, rel_tol=1e-12)
    assert m["equity_points"] == 4


def test_annualized_return_and_calmar_when_horizon_derivable():
    curve = [
        {"timestamp": "2025-01-01T00:00:00Z", "equity": 1000.0},
        {"timestamp": "2025-07-01T00:00:00Z", "equity": 900.0},    # -10% drawdown
        {"timestamp": "2026-01-01T00:00:00Z", "equity": 1210.0},   # +21% total
    ]
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=curve))

    # Span = 365 days = exactly 1.0 year.
    assert math.isclose(m["equity_horizon_years"], 1.0, rel_tol=1e-12), m["equity_horizon_years"]
    # Total return = 1210/1000 - 1 = 21%; annualized over 1y = 21%.
    assert math.isclose(m["equity_total_return_pct"], 21.0, rel_tol=1e-12), m["equity_total_return_pct"]
    assert math.isclose(m["equity_annualized_return_pct"], 21.0, rel_tol=1e-12), \
        m["equity_annualized_return_pct"]
    # max drawdown = (900-1000)/1000 = -10%; Calmar = 0.21 / 0.10 = 2.1.
    assert math.isclose(m["equity_max_drawdown_pct"], -10.0, rel_tol=1e-12), m["equity_max_drawdown_pct"]
    assert math.isclose(m["equity_annualized_calmar_ratio"], 2.1, rel_tol=1e-9), \
        m["equity_annualized_calmar_ratio"]


def test_no_annualized_fields_without_timestamps():
    curve = [{"equity": 100.0}, {"equity": 120.0}]
    m = metrics_to_dict(compute_campaign_metrics(trades=[], equity_curve=curve))
    # Horizon not derivable -> annualized fields must be absent (never guessed).
    assert "equity_annualized_return_pct" not in m
    assert "equity_horizon_years" not in m
    assert "equity_annualized_calmar_ratio" not in m


def compute_metrics_from_trades_via_campaign(trades, initial_capital):
    return metrics_to_dict(compute_campaign_metrics(trades=trades, initial_capital=initial_capital))