"""Deterministic vault fee accounting tests (spec: 2%/yr AUM, 10% profit above HWM).

Hand-traced expectations per HANDOFF 2026-11-12T13:54:32Z campaign cells 1-4.
"""
import math

import pytest

from src.metrics.vault_fees import (
    HOURS_PER_YEAR,
    accrue_vault_fees,
    compute_aum_fee,
    compute_profit_share,
)


def _approx(a, b, tol=1e-12):
    return abs(a - b) <= tol


# --- Cell 1: AUM fee (2%/yr) ---

def test_aum_fee_1h_24h_8760h_traced():
    eq = 100000.0
    # 1 hour: equity * 0.02 * (1/8760)
    f1 = compute_aum_fee(eq, hours=1.0)
    assert _approx(f1, eq * 0.02 * 1.0 / HOURS_PER_YEAR)
    assert _approx(f1, 2000.0 / 8760.0)

    f24 = compute_aum_fee(eq, hours=24.0)
    assert _approx(f24, eq * 0.02 * 24.0 / HOURS_PER_YEAR)
    assert f24 == pytest.approx(100000.0 * 0.02 * 24.0 / 8760.0)

    f8760 = compute_aum_fee(eq, hours=8760.0)
    assert _approx(f8760, 2000.0)
    assert f8760 == pytest.approx(eq * 0.02)


def test_aum_fee_never_charges_non_positive_equity_or_hours():
    assert compute_aum_fee(0.0, hours=1.0) == 0.0
    assert compute_aum_fee(-100.0, hours=1.0) == 0.0
    assert compute_aum_fee(100.0, hours=0.0) == 0.0
    assert compute_aum_fee(100.0, hours=-5.0) == 0.0
    assert compute_aum_fee(100.0, hours=1.0, annual_rate=0.0) == 0.0
    assert compute_aum_fee(100.0, hours=1.0, annual_rate=-0.1) == 0.0


def test_aum_fee_capped_to_equity_for_extreme_inputs():
    # absurd horizon/rate should not produce fee > equity
    assert compute_aum_fee(50.0, hours=10**9, annual_rate=1.0) == 50.0


# --- Cell 2: Profit share (10% above HWM) ---

def test_profit_share_only_on_equity_above_hwm():
    # no charge when <= HWM
    assert compute_profit_share(100.0, hwm=100.0) == 0.0
    assert compute_profit_share(99.0, hwm=100.0) == 0.0
    # 10% of excess over HWM
    assert compute_profit_share(110.0, hwm=100.0) == pytest.approx(1.0)
    assert compute_profit_share(150.0, hwm=120.0) == pytest.approx(3.0)


def test_profit_share_zero_for_non_positive_equity_or_rate():
    assert compute_profit_share(0.0, hwm=0.0) == 0.0
    assert compute_profit_share(-10.0, hwm=0.0) == 0.0
    assert compute_profit_share(110.0, hwm=100.0, share_rate=0.0) == 0.0
    assert compute_profit_share(110.0, hwm=100.0, share_rate=-1.0) == 0.0


# --- Cell 2/3 traced accrual: AUM then profit-share, HWM on net peaks ---

def test_accrual_ordering_and_hwm_traced_two_steps():
    # Step 0: gross 100000, h=1 -> AUM fee on 100000, after_aum < initial HWM(100000)
    #   so profit share 0, net=after_aum, HWM stays 100000.
    # Step 1: gross 110000, h=1 -> AUM on 110000, profit share 10% of (after_aum1 - 100000).
    series = [100000.0, 110000.0]
    res = accrue_vault_fees(series, hours_per_step=1.0)

    aum0 = 100000.0 * 0.02 / HOURS_PER_YEAR
    after0 = 100000.0 - aum0
    ps0 = 0.0  # after0 < initial HWM 100000
    net0 = after0
    hwm0 = 100000.0

    aum1 = 110000.0 * 0.02 / HOURS_PER_YEAR
    after1 = 110000.0 - aum1
    ps1 = 0.10 * (after1 - hwm0)  # > 0
    net1 = after1 - ps1
    hwm1 = max(hwm0, net1)

    assert len(res.steps) == 2
    s0, s1 = res.steps
    assert s0.aum_fee == pytest.approx(aum0)
    assert s0.equity_after_aum == pytest.approx(after0)
    assert s0.profit_share == pytest.approx(ps0)
    assert s0.equity_net == pytest.approx(net0)
    assert s0.hwm_before == pytest.approx(100000.0)
    assert s0.hwm_after == pytest.approx(hwm0)

    assert s1.aum_fee == pytest.approx(aum1)
    assert s1.equity_after_aum == pytest.approx(after1)
    assert s1.profit_share == pytest.approx(ps1)
    assert s1.equity_net == pytest.approx(net1)
    assert s1.hwm_before == pytest.approx(hwm0)
    assert s1.hwm_after == pytest.approx(hwm1)

    assert res.aum_fee_total == pytest.approx(aum0 + aum1)
    assert res.profit_share_total == pytest.approx(ps0 + ps1)
    assert res.total_fees == pytest.approx(aum0 + aum1 + ps0 + ps1)
    assert res.final_equity_gross == pytest.approx(110000.0)
    assert res.final_equity_net == pytest.approx(net1)
    assert res.final_hwm == pytest.approx(hwm1)


def test_hwm_updates_only_on_new_net_peaks_and_no_double_charge():
    # rise -> drawdown -> rise above previous net peak: profit share only on excess above prior HWM
    series = [100000.0, 120000.0, 110000.0, 130000.0]
    res = accrue_vault_fees(series, hours_per_step=0.0)  # isolate profit share (no AUM)
    # step0: net 100k, hwm 100k, ps 0
    # step1: net 120k, ps 10%*(20k)=2000, net 118k, hwm 118k
    # step2: net 110k <= 118k -> ps 0, hwm 118k
    # step3: net 130k, ps 10%*(130k-118k)=1200, net 128800, hwm 128800
    assert res.steps[0].profit_share == pytest.approx(0.0)
    assert res.steps[0].hwm_after == pytest.approx(100000.0)
    assert res.steps[1].profit_share == pytest.approx(2000.0)
    assert res.steps[1].equity_net == pytest.approx(118000.0)
    assert res.steps[1].hwm_after == pytest.approx(118000.0)
    assert res.steps[2].profit_share == pytest.approx(0.0)
    assert res.steps[2].hwm_after == pytest.approx(118000.0)
    assert res.steps[3].profit_share == pytest.approx(1200.0)
    assert res.steps[3].equity_net == pytest.approx(128800.0)
    assert res.steps[3].hwm_after == pytest.approx(128800.0)
    assert res.profit_share_total == pytest.approx(3200.0)


# --- Cell 4: edge cases ---

def test_empty_zero_equity_campaign():
    r = accrue_vault_fees([], hours_per_step=1.0)
    assert r.total_fees == 0.0
    assert r.final_equity_net == 0.0
    assert r.steps == []

    r2 = accrue_vault_fees([0.0, 0.0], hours_per_step=1.0)
    assert r2.total_fees == 0.0
    assert r2.final_equity_net == 0.0
    assert all(s.profit_share == 0.0 and s.aum_fee == 0.0 for s in r2.steps)


def test_single_bar_accrual():
    r = accrue_vault_fees([50000.0], hours_per_step=24.0)
    expected_aum = 50000.0 * 0.02 * 24.0 / HOURS_PER_YEAR
    assert len(r.steps) == 1
    assert r.steps[0].aum_fee == pytest.approx(expected_aum)
    assert r.steps[0].profit_share == pytest.approx(0.0)
    assert r.final_equity_net == pytest.approx(50000.0 - expected_aum)


def test_loss_only_path_never_charges_profit_share():
    series = [100000.0, 95000.0, 90000.0, 85000.0]
    r = accrue_vault_fees(series, hours_per_step=0.0)
    assert r.profit_share_total == 0.0
    assert all(s.profit_share == 0.0 for s in r.steps)
    assert r.final_hwm == pytest.approx(100000.0)


def test_exact_hwm_equality_boundary_no_profit_share():
    r = accrue_vault_fees([100000.0, 100000.0], hours_per_step=0.0)
    assert r.steps[1].profit_share == pytest.approx(0.0)
    assert r.steps[1].hwm_after == pytest.approx(100000.0)


def test_non_finite_inputs_fail_safe():
    assert compute_aum_fee(float('nan')) == 0.0
    assert compute_aum_fee(100.0, hours=float('inf')) == 0.0
    assert compute_profit_share(float('nan'), hwm=100.0) == 0.0
    assert compute_profit_share(120.0, hwm=float('nan')) == pytest.approx(12.0)  # nan hwm -> treated as 0
    r = accrue_vault_fees([float('nan'), 100.0], hours_per_step=1.0)
    assert math.isfinite(r.total_fees)
    assert all(math.isfinite(s.equity_net) for s in r.steps)


def test_custom_initial_hwm():
    # starting below provided HWM: no profit share until exceeding that HWM
    r = accrue_vault_fees([100000.0, 105000.0], hours_per_step=0.0, initial_hwm=110000.0)
    assert r.steps[0].profit_share == 0.0
    assert r.steps[1].profit_share == 0.0
    assert r.final_hwm == pytest.approx(110000.0)
