"""Spec-fidelity documentation/regression: hourly engine execution simplifications are explicit.

Per crash-rebound-strategy.pdf / research_state/strategy_spec.md:
- "Large orders in slices: never send > half resting on order book near price in one go, next slice ~20s later"
- "Hourly simulation with fees, spread, order-book impact, hourly funding on every leg, hourly liquidation check at worst price of each hour"

This repo's backtest is an hourly bar simulation. 20-second order slicing and a live L2
order book are NOT simulated. That limitation MUST remain explicit in config/artifact
semantics and must not be silently claimed as reproduced. Non-evidence, deterministic.
"""
from src.data.loader import make_fixture_crash_rebound_multi
from src.strategy.config import StrategyConfig, DEFAULT_CONFIG
from scripts.run_campaign import build_campaign_export
from scripts.run_portfolio import run_portfolio_simulation


def _execution_fields(cfg):
    return {
        "execution_model": cfg.execution_model,
        "order_slicing_simulated": cfg.order_slicing_simulated,
        "order_book_impact_model": cfg.order_book_impact_model,
        "spread_bps_assumed": cfg.spread_bps_assumed,
        "slippage_pct": cfg.slippage_pct,
        "funding_rate_pct_per_hour": cfg.funding_rate_pct_per_hour,
        "enable_liquidation_checks": cfg.enable_liquidation_checks,
    }


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


def test_fixture_campaign_artifact_surfaces_execution_simplifications():
    fixtures = make_fixture_crash_rebound_multi()
    config = StrategyConfig(use_rsi_trigger=False, enable_rebound_short=False,
                            enable_eth_hedge=False, enable_volume_based_sizing=False)
    results = run_portfolio_simulation(fixtures, config=config, capital=100000.0)
    export = build_campaign_export(results, config, fixtures, "2026-11-06T00:00:00Z", metrics={})
    realism = export.get("execution_realism") or {}
    assert realism.get("order_slicing_simulated") is False
    assert realism.get("execution_model") == "hourly_bar_simplified"
    assert "20" in (realism.get("limitation_note") or "") or "slicing" in (realism.get("limitation_note") or "").lower()
    # config snapshot in artifacts must also carry the explicit flags
    ecfg = export.get("config") or {}
    assert ecfg.get("order_slicing_simulated") is False
    assert ecfg.get("execution_model") == "hourly_bar_simplified"
