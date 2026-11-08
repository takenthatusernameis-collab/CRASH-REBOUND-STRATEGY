"""Spec-fidelity: rebound short max hold is 48 hours (48 bars) with matching
hourly funding on every leg, consistent with the long-leg 50h semantics.

Spec (crash-rebound-strategy.pdf / strategy_spec.md):
- "close short at -9% (profit target) OR after 48 hours at latest"
- "Short held up to 48 hours"
- "hourly funding on every leg"

The time-exit bar count and funding hours must be consistent: a 48-bar max hold
charges 48 hours of funding (same +1-inclusive counting as the long leg's 50h).
"""
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import Signal
from src.backtest.engine import backtest_simple


def _candles(n, o=100.0, h=101.0, l=99.0, c=100.0):
    return [{'timestamp': f'2025-01-01T{i:02d}:00:00Z',
             'open': o, 'high': h, 'low': l, 'close': c, 'volume': 1_000_000}
            for i in range(n)]


def _eth(n, price=2000.0):
    return [{'timestamp': f'2025-01-01T{i:02d}:00:00Z',
             'open': price, 'high': price * 1.001, 'low': price * 0.999,
             'close': price, 'volume': 1_000_000}
            for i in range(n)]


def _base_config(**overrides):
    defaults = dict(
        entry_next_bar=False,
        use_spec_safety_stop=False,
        enable_rebound_short=True,
        rebound_short_target_pct=9.0,
        rebound_short_stop_pct=40.0,
        rebound_short_time_exit_bars=48,
        enable_eth_hedge=False,
        funding_rate_pct_per_hour=0.01,  # 1bp/hr for clear arithmetic
        slippage_pct=0.0,
        commission_per_share=0.0,
        commission_min=0.0,
        time_exit_max_bars=200,
    )
    defaults.update(overrides)
    return StrategyConfig(**defaults)


def _signal(entry=100.0, stop=90.0, target=109.0, shares=10.0):
    return Signal(symbol='TEST', side='long', reason='crash_then_rebound',
                  entry_price=entry, stop_price=stop, target_price=target,
                  risk_per_share=entry - stop, timestamp='t0', size_shares=shares,
                  signal_index=0)


def test_rebound_short_time_exit_at_48_bars_charges_48h_funding():
    """48h max hold => time exit on 48th bar held, funding charged for 48 hours.

    Setup: long hits target on bar 5 (idx=5, bars_held=6 from start_idx=0).
    Rebound short enters at bar 5 close area, starts at short_start_idx=5.
    With flat candles (no stop/target hit), time exit fires at 48 bars.
    Funding = entry * shares * rate * 48 hours.
    """
    rate = 0.01  # %/hr
    shares = 10.0
    entry = 100.0
    target = 109.0  # +9%
    n = 120
    candles = _candles(n, o=100.0, h=101.0, l=99.0, c=100.0)
    # Long target hit at bar 5
    candles[5] = {'timestamp': '2025-01-01T05:00:00Z',
                  'open': 108.0, 'high': 110.0, 'low': 107.0, 'close': 109.0, 'volume': 1e6}
    # Flat after: short entry ~109 (target exit), no short stop (>=152.6) or target (<=99.19)
    for i in range(6, n):
        candles[i] = {'timestamp': f'2025-01-01T{i:02d}:00:00Z',
                      'open': 109.0, 'high': 112.0, 'low': 106.0, 'close': 109.0, 'volume': 1e6}

    cfg = _base_config(funding_rate_pct_per_hour=rate, enable_eth_hedge=False)
    sig = _signal(entry=entry, target=target, shares=shares)
    res = backtest_simple(candles, sig, config=cfg)

    short_leg = next((t for t in (res.trades or []) if t.get('side') == 'short'), None)
    assert short_leg is not None, f"expected rebound short leg, trades={res.trades}"
    assert short_leg['reason'] == 'time_exit', f"expected time_exit, got {short_leg}"

    short_entry = short_leg['entry']  # executed short entry (with 0 slippage = target exit px context)
    # 48 hours of funding on the short coin leg: notional * (rate/100) * 48
    expected_funding = abs(short_entry * shares) * (rate / 100.0) * 48
    # Short PnL at flat exit (close=109 => exit ~109) minus funding
    raw_short_pnl = (short_entry - short_leg['exit']) * shares
    expected_short_pnl = raw_short_pnl - (-expected_funding)  # short receives funding? _apply_funding_pnl returns -amt for short => pnl -= (-amt) => pnl += amt
    # Wait: _apply_funding_pnl returns -funding_amt for short (benefit), and engine does pnl -= funding => pnl -= (-amt) = pnl + amt.
    # So expected benefit = expected_funding added.
    expected_short_pnl = raw_short_pnl + expected_funding
    assert abs(short_leg['pnl'] - expected_short_pnl) < 1e-6, (
        f"short pnl {short_leg['pnl']} != expected {expected_short_pnl} "
        f"(raw={raw_short_pnl}, funding_benefit={expected_funding}, entry={short_entry}, exit={short_leg['exit']})"
    )
