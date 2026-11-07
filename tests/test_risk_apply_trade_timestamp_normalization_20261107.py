from src.strategy.risk import RiskState


def test_apply_trade_close_preserves_live_notionals_across_timestamp_formats():
    state = RiskState(date="2025-01-01")
    state.open_position_notionals = [60000.0, 60000.0]
    state.gross_exposure = 120000.0
    state.open_positions = 2
    state.realized_pnl = -5.0
    state.daily_loss_limit_hit = True

    state.apply_trade("2025-01-01T09:32:00", 1.5, opened=False, closed=True, notional=60000.0)

    assert state.date == "2025-01-01"
    assert state.open_position_notionals == [60000.0]
    assert state.open_positions == 1
    assert abs(state.gross_exposure - 60000.0) < 1e-9
    assert abs(state.realized_pnl - (-3.5)) < 1e-9
    assert state.daily_loss_limit_hit is True


def test_apply_trade_new_day_resets_only_when_no_live_exposure():
    state = RiskState(date="2025-01-01")
    state.open_position_notionals = [60000.0]
    state.gross_exposure = 60000.0
    state.open_positions = 1
    state.realized_pnl = -12.0
    state.daily_loss_limit_hit = True

    state.apply_trade("2025-01-02T00:00:00", 0.0, opened=False, closed=False, notional=0.0)

    assert state.date == "2025-01-02"
    assert state.realized_pnl == 0.0
    assert state.daily_loss_limit_hit is False
    assert state.open_position_notionals == [60000.0]
    assert state.open_positions == 1
    assert abs(state.gross_exposure - 60000.0) < 1e-9


def test_apply_trade_new_day_clears_stale_notionals_when_flat():
    state = RiskState(date="2025-01-01")
    state.open_position_notionals = [123.0]
    state.gross_exposure = 0.0
    state.open_positions = 0

    state.apply_trade("2025-01-02", 0.0, opened=False, closed=False)

    assert state.date == "2025-01-02"
    assert state.open_position_notionals == []
