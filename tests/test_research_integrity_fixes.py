"""Regression tests for daily risk state and campaign evidence integrity."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.backtest.engine import backtest_simple
from src.strategy.config import StrategyConfig
from src.strategy.risk import RiskState


def test_daily_risk_reset_preserves_open_positions_across_midnight() -> None:
    state = RiskState(
        date="2025-01-01",
        realized_pnl=-50.0,
        open_positions=1,
        gross_exposure=1_000.0,
        open_position_notionals=[1_000.0],
    )

    state.apply_trade(
        "2025-01-02T00:00:00Z",
        0.0,
        opened=True,
        closed=False,
        notional=500.0,
    )

    assert state.date == "2025-01-02"
    assert state.realized_pnl == 0.0
    assert state.open_positions == 2
    assert state.open_position_notionals == [1_000.0, 500.0]
    assert state.gross_exposure == pytest.approx(1_500.0)


def test_daily_loss_accumulates_across_intraday_timestamps() -> None:
    state = RiskState()

    state.apply_trade(
        "2025-01-02T09:00:00Z", -10.0, opened=False, closed=False
    )
    state.apply_trade(
        "2025-01-02T10:00:00Z", -5.0, opened=False, closed=False
    )

    assert state.date == "2025-01-02"
    assert state.realized_pnl == pytest.approx(-15.0)


def test_close_after_day_rollover_reconciles_the_correct_open_notional() -> None:
    state = RiskState(
        date="2025-01-01",
        open_positions=1,
        gross_exposure=1_000.0,
        open_position_notionals=[1_000.0],
    )

    state.apply_trade(
        "2025-01-02T01:00:00Z",
        -12.0,
        opened=False,
        closed=True,
        notional=1_000.0,
    )

    assert state.open_positions == 0
    assert state.open_position_notionals == []
    assert state.gross_exposure == pytest.approx(0.0)


def test_final_backtest_time_exit_releases_position_notional() -> None:
    candles = [
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1_000.0,
        },
        {
            "timestamp": "2025-01-01T01:00:00Z",
            "open": 100.0,
            "high": 102.0,
            "low": 99.0,
            "close": 101.0,
            "volume": 1_000.0,
        },
    ]
    signal = SimpleNamespace(
        entry_price=100.0,
        stop_price=90.0,
        target_price=150.0,
        risk_per_share=10.0,
        size_shares=10.0,
        signal_index=0,
    )
    config = StrategyConfig(
        entry_next_bar=False,
        time_exit_max_bars=10,
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=False,
        avoid_downtrend=False,
        regime_min_price=0.0,
        enable_liquidation_checks=False,
    )
    state = RiskState()

    result = backtest_simple(
        candles,
        signal,
        config=config,
        capital=100_000.0,
        risk_state=state,
    )

    assert result.exit_reason == "time_exit"
    assert state.open_positions == 0
    assert state.open_position_notionals == []
    assert state.gross_exposure == pytest.approx(0.0)


def test_campaign_entry_point_refuses_to_publish_fixture_performance() -> None:
    from scripts import run_campaign

    with pytest.raises(SystemExit, match="not a valid historical campaign runner"):
        run_campaign.main()


def test_rebound_short_exposure_is_opened_and_closed() -> None:
    candles = [
        {
            "timestamp": "2025-01-01T00:00:00Z",
            "open": 100.0,
            "high": 160.0,
            "low": 99.0,
            "close": 150.0,
            "volume": 1_000.0,
        },
        {
            "timestamp": "2025-01-01T01:00:00Z",
            "open": 150.0,
            "high": 152.0,
            "low": 140.0,
            "close": 145.0,
            "volume": 1_000.0,
        },
    ]
    signal = SimpleNamespace(
        entry_price=100.0,
        stop_price=90.0,
        target_price=150.0,
        risk_per_share=10.0,
        size_shares=10.0,
        signal_index=0,
    )
    config = StrategyConfig(
        entry_next_bar=False,
        time_exit_max_bars=10,
        use_rsi_trigger=False,
        min_daily_volume_usd=0.0,
        enable_eth_hedge=False,
        enable_rebound_short=True,
        rebound_short_time_exit_bars=1,
        avoid_downtrend=False,
        regime_min_price=0.0,
        enable_liquidation_checks=False,
    )
    state = RiskState()

    result = backtest_simple(
        candles,
        signal,
        config=config,
        capital=100_000.0,
        risk_state=state,
    )

    assert result.exit_reason == "target_rebound_short"
    assert any(trade["side"] == "short" for trade in result.trades or [])
    assert state.open_positions == 0
    assert state.open_position_notionals == []
    assert state.gross_exposure == pytest.approx(0.0)
