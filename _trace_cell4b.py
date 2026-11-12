"""Scratch: verify the portfolio equity_curve leading timestamp defect."""
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict
from src.metrics.vault_fees import accrue_vault_fees, elapsed_hours_from_timestamps, HOURS_PER_YEAR
from scripts.run_portfolio import run_portfolio_simulation
from src.strategy.config import StrategyConfig


def _series_with_mid_crash_rebound():
    candles = []
    for i in range(60):
        ts = f"2026-01-01T{i%24:02d}:00:00Z"
        if i == 10:
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 88, "close": 90, "volume": 500})
        elif i == 11:
            candles.append({"timestamp": ts, "open": 90, "high": 97, "low": 89, "close": 96, "volume": 400})
        else:
            candles.append({"timestamp": ts, "open": 100, "high": 101, "low": 99, "close": 100, "volume": 200})
    return candles


if __name__ == "__main__":
    candles = _series_with_mid_crash_rebound()
    cfg = StrategyConfig(
        use_rsi_trigger=False, enable_eth_hedge=False, min_daily_volume_usd=0,
        crash_lookback=2, entry_next_bar=False, time_exit_max_bars=50,
    )
    res = run_portfolio_simulation({"X": candles}, config=cfg, capital=100000)
    curve = res["equity_curve"]
    print("equity_curve points:", len(curve))
    print("first point:", curve[0])
    print("last point:", curve[-1])
    ts = [p.get("timestamp") for p in curve]
    print("derived hours:", elapsed_hours_from_timestamps(ts, default_hours=1.0))
    flat = metrics_to_dict(compute_campaign_metrics(
        trades=res["trades"], equity_curve=curve, initial_capital=100000.0,
        apply_vault_fees=True, fee_hours_per_step=1.0))
    elapsed = metrics_to_dict(compute_campaign_metrics(
        trades=res["trades"], equity_curve=curve, initial_capital=100000.0,
        apply_vault_fees=True, fee_hours_per_step=1.0, fee_use_timestamp_hours=True))
    print("flat aum_fee_total:", flat["aum_fee_total"])
    print("elapsed aum_fee_total:", elapsed["aum_fee_total"])
    print("ratio:", elapsed["aum_fee_total"] / flat["aum_fee_total"] if flat["aum_fee_total"] else None)