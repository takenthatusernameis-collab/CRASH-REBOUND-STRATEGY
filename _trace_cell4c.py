"""Scratch: design a 2-trade fixture with a multi-day gap to trace exact values."""
from src.metrics.campaign_metrics import compute_campaign_metrics, metrics_to_dict
from src.metrics.vault_fees import accrue_vault_fees, elapsed_hours_from_timestamps, HOURS_PER_YEAR


if __name__ == "__main__":
    trades = [
        {"exit_timestamp": "2026-01-01T03:00:00Z", "total_pnl": 1000.0, "pnl": 1000.0, "symbol": "A", "side": "long"},
        {"exit_timestamp": "2026-01-03T03:00:00Z", "total_pnl": -500.0, "pnl": -500.0, "symbol": "B", "side": "long"},
    ]
    curve = [
        {"timestamp": "2026-01-01T02:00:00Z", "equity": 100000.0, "pnl": 0.0},
        {"timestamp": "2026-01-01T03:00:00Z", "equity": 101000.0, "pnl": 1000.0},
        {"timestamp": "2026-01-03T03:00:00Z", "equity": 100500.0, "pnl": -500.0},
    ]
    print("hours:", elapsed_hours_from_timestamps([p["timestamp"] for p in curve], default_hours=1.0))
    flat = metrics_to_dict(compute_campaign_metrics(
        trades=trades, equity_curve=curve, initial_capital=100000.0,
        apply_vault_fees=True, fee_hours_per_step=1.0))
    elapsed = metrics_to_dict(compute_campaign_metrics(
        trades=trades, equity_curve=curve, initial_capital=100000.0,
        apply_vault_fees=True, fee_hours_per_step=1.0, fee_use_timestamp_hours=True))
    print("flat aum:", flat["aum_fee_total"], "profit_share:", flat["profit_share_total"], "total:", flat["vault_fee_total"])
    print("elapsed aum:", elapsed["aum_fee_total"], "profit_share:", elapsed["profit_share_total"], "total:", elapsed["vault_fee_total"])
    print("ratio:", elapsed["aum_fee_total"] / flat["aum_fee_total"])
    # hand-trace elapsed:
    # step0: eq 100000, h=1.0 -> aum = 100000*0.02*1/8760 = 0.22831050228310503
    # after_aum0 = 99999.77168949772; hwm0 = 100000 (initial = first gross)
    # ps0 = 0 (after_aum0 < hwm0); net0 = after_aum0; hwm stays 100000
    # step1: eq 101000, h=1.0 -> aum = 101000*0.02*1/8760 = 0.23059360730593608
    # after_aum1 = 100999.76940639269; ps1 = 0.10 * max(0, after_aum1 - 100000) = 0.10*999.7694063926927 = 99.97694063926927
    # net1 = 100899.79246575342; hwm1 = max(100000, 100899.79) = 100899.79246575342
    # step2: eq 100500, h=48.0 -> aum = 100500*0.02*48/8760 = 10.990867579908677
    # after_aum2 = 99989.00913242009; ps2 = 0 (after_aum2 < hwm1); net2 = after_aum2
    # total aum = 0.22831050228310503 + 0.23059360730593608 + 10.990867579908677 = 11.449771689497718
    # total ps = 99.97694063926927
    print("hand-trace aum expected: 11.449771689497718")
    print("hand-trace ps expected: 99.97694063926927")