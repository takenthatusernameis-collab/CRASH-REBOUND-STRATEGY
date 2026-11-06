"""Spec-fidelity documentation/regression: hourly engine execution simplifications are explicit.

Per crash-rebound-strategy.pdf / research_state/strategy_spec.md:
- "Large orders in slices: never send > half resting on order book near price in one go, next slice ~20s later"
- "Hourly simulation with fees, spread, order-book impact, hourly funding on every leg, hourly liquidation check at worst price of each hour"

This repo's backtest is an hourly bar simulation. 20-second order slicing and a live L2
order book are NOT simulated. That limitation MUST remain explicit in config/artifact
semantics and must not be silently claimed as reproduced. Non-evidence, deterministic.
"""
from src.strategy.config import StrategyConfig, DEFAULT_CONFIG


def test_execution_model_limitations_are_explicit():
    cfg = StrategyConfig()
    assert cfg.execution_model == "hourly_bar_simplified"
    assert cfg.order_slicing_simulated is False
    assert "slippage" in cfg.order_book_impact_model.lower()
    assert hasattr(cfg, "spread_bps_assumed")
    # defaults must remain explicit
    assert DEFAULT_CONFIG.order_slicing_simulated is False


def test_funding_and_liquidation_realism_flags_present():
    cfg = StrategyConfig()
    assert cfg.funding_rate_pct_per_hour >= 0
    assert cfg.enable_liquidation_checks is True
    assert cfg.slippage_pct >= 0
