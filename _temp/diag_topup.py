"""Diagnostic: engine cap-cut with 3 positions — does a new admission get topped up
beyond its requested size when equal-share cut exceeds the request?"""
from src.strategy.config import StrategyConfig
from src.strategy.risk import RiskState


def cfg():
    return StrategyConfig(
        use_rsi_trigger=False, enable_rebound_short=False, enable_eth_hedge=False,
        entry_next_bar=False, min_daily_volume_usd=0, slippage_pct=0.0,
        commission_per_share=0.0, commission_min=0.0, funding_rate_pct_per_hour=0.0,
        avoid_downtrend=False, gross_cap_pct=120.0, max_positions=10,
        time_exit_max_bars=200, max_daily_loss_pct=100.0,
    )


def main():
    capital = 10000.0
    # Two existing positions already cut to 6000 each (X, A).
    risk_state = RiskState(date="")
    risk_state.open_position_notionals = [6000.0, 6000.0]
    risk_state.gross_exposure = 12000.0
    risk_state.open_positions = 2

    # B requests only 1500 notional (15 shares @100).
    notional = 1500.0
    cap_value = capital * 120.0 / 100.0  # 12000
    total_exposure = risk_state.gross_exposure + notional  # 13500 > 12000
    print("total_exposure:", total_exposure, "cap:", cap_value)
    all_notionals = list(risk_state.open_position_notionals) + [notional]  # [6000, 6000, 1500]
    cuts = risk_state.apply_cap_cuts(capital, cfg(), all_notionals)
    print("all_notionals:", all_notionals)
    print("cuts (equal share = 12000/3 = 4000 each):", cuts)
    new_notional_cut = cuts[-1]
    print("B's cut notional:", new_notional_cut, "-> shares @100 =", new_notional_cut / 100.0)
    print("B REQUESTED 1500 notional (15 shares). Got:", new_notional_cut)
    if new_notional_cut > notional:
        print("DEFECT: new position TOPPED UP from", notional, "to", new_notional_cut,
              "(equal-share cut exceeds request — violates 'cuts only, never top-ups')")


if __name__ == "__main__":
    main()