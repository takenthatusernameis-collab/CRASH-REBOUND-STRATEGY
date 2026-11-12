"""Vault fee accounting (spec: 2%/yr on assets, 10% of remaining profit).

Pure, deterministic helpers. Fees are computed per step (hourly bars by
default) against portfolio equity. This module does not mutate strategy state;
callers apply fee deductions explicitly and record components for reconciliation.

Assumptions (documented, deterministic):
- Time base: 8760 hours/year (365 * 24). Per-step AUM fee fraction =
  rate_annual * (hours_elapsed / 8760).
- AUM fee is charged on step equity (before profit-share deduction for that
  step) and is non-negative; equity never goes below zero from fees.
- Profit share is 10% of equity increase above prior high-water mark (HWM).
  HWM is tracked on post-AUM-fee equity for the step. No charge when equity <=
  HWM. HWM updates only when post-profit-share equity exceeds it (a new peak
  after fees). "Remaining profit" in spec interpreted as profit remaining above
  HWM subject to the 10% share (standard vault structure); applied after the
  AUM fee accrual for the same step so both fee types are accounted each step.
- Empty/invalid inputs are handled fail-safe (no NaN/inf propagation).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

HOURS_PER_YEAR = 8760.0
DEFAULT_AUM_FEE_ANNUAL = 0.02
DEFAULT_PROFIT_SHARE = 0.10


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _clamp_nonneg(x: float) -> float:
    return x if x > 0.0 else 0.0


@dataclass
class VaultFeeStep:
    index: int
    hours: float
    equity_gross: float
    aum_fee: float
    equity_after_aum: float
    hwm_before: float
    profit_share: float
    equity_net: float
    hwm_after: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "hours": self.hours,
            "equity_gross": self.equity_gross,
            "aum_fee": self.aum_fee,
            "equity_after_aum": self.equity_after_aum,
            "hwm_before": self.hwm_before,
            "profit_share": self.profit_share,
            "equity_net": self.equity_net,
            "hwm_after": self.hwm_after,
        }


@dataclass
class VaultFeeSummary:
    aum_fee_total: float
    profit_share_total: float
    total_fees: float
    final_equity_gross: float
    final_equity_net: float
    final_hwm: float
    steps: List[VaultFeeStep] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "aum_fee_total": self.aum_fee_total,
            "profit_share_total": self.profit_share_total,
            "total_fees": self.total_fees,
            "final_equity_gross": self.final_equity_gross,
            "final_equity_net": self.final_equity_net,
            "final_hwm": self.final_hwm,
            "steps": [s.as_dict() for s in self.steps],
        }


def compute_aum_fee(equity: float, hours: float = 1.0,
                    annual_rate: float = DEFAULT_AUM_FEE_ANNUAL) -> float:
    """2%/yr management fee on assets, accrued per step."""
    eq = _finite(equity)
    h = _finite(hours)
    rate = _finite(annual_rate)
    if eq <= 0.0 or h <= 0.0 or rate <= 0.0:
        return 0.0
    fee = eq * rate * (h / HOURS_PER_YEAR)
    fee = _clamp_nonneg(fee)
    # never exceed available equity
    if fee > eq:
        fee = eq
    return fee


def compute_profit_share(equity: float, hwm: float,
                         share_rate: float = DEFAULT_PROFIT_SHARE) -> float:
    """10% of profit above high-water mark. No charge when equity <= HWM."""
    eq = _finite(equity)
    hw = _finite(hwm)
    rate = _finite(share_rate)
    if eq <= 0.0 or rate <= 0.0:
        return 0.0
    profit_above = eq - hw
    if profit_above <= 0.0:
        return 0.0
    fee = profit_above * rate
    fee = _clamp_nonneg(fee)
    if fee > eq:
        fee = eq
    return fee


def accrue_vault_fees(equity_series: Sequence[float],
                      hours_per_step: Any = 1.0,
                      initial_hwm: Optional[float] = None,
                      aum_rate_annual: float = DEFAULT_AUM_FEE_ANNUAL,
                      profit_share_rate: float = DEFAULT_PROFIT_SHARE,
                      include_steps: bool = True) -> VaultFeeSummary:
    """Accrue vault fees over an equity series (gross equity observed each step).

    For each step i with gross equity E_i and duration h_i:
      1) aum_fee_i = AUM fee on E_i over h_i (capped to E_i)
      2) equity_after_aum_i = max(0, E_i - aum_fee_i)
      3) profit_share_i = share of (equity_after_aum_i - HWM_{i-1}) above 0
      4) equity_net_i = max(0, equity_after_aum_i - profit_share_i)
      5) HWM_i = max(HWM_{i-1}, equity_net_i)

    initial_hwm defaults to first step gross equity when series non-empty, else 0.
    This represents a standard vault: you don't charge performance fee on the
    starting capital, only on new highs achieved after fees.
    """
    if isinstance(hours_per_step, (int, float)):
        hours_list = [float(hours_per_step)] * len(equity_series)
    else:
        hours_list = list(hours_per_step)
        if len(hours_list) < len(equity_series):
            hours_list.extend([1.0] * (len(equity_series) - len(hours_list)))

    steps: List[VaultFeeStep] = []
    aum_total = 0.0
    ps_total = 0.0

    if not equity_series:
        hwm0 = _finite(initial_hwm) if initial_hwm is not None else 0.0
        return VaultFeeSummary(0.0, 0.0, 0.0, 0.0, 0.0, max(0.0, hwm0), [])

    first_gross = _finite(equity_series[0])
    if initial_hwm is None:
        hwm = max(0.0, first_gross)
    else:
        hwm = max(0.0, _finite(initial_hwm))

    final_gross = 0.0
    final_net = 0.0
    for i, eg in enumerate(equity_series):
        eq_gross = _finite(eg)
        h = _finite(hours_list[i]) if i < len(hours_list) else 1.0
        aum_fee = compute_aum_fee(eq_gross, hours=h, annual_rate=aum_rate_annual)
        eq_after_aum = max(0.0, eq_gross - aum_fee)
        ps_fee = compute_profit_share(eq_after_aum, hwm, share_rate=profit_share_rate)
        eq_net = max(0.0, eq_after_aum - ps_fee)
        hwm_after = max(hwm, eq_net)
        if not (hwm_after >= hwm):  # guard non-finite weirdness
            hwm_after = hwm

        aum_total += aum_fee
        ps_total += ps_fee
        final_gross = eq_gross
        final_net = eq_net

        if include_steps:
            steps.append(VaultFeeStep(
                index=i, hours=h, equity_gross=eq_gross, aum_fee=aum_fee,
                equity_after_aum=eq_after_aum, hwm_before=hwm, profit_share=ps_fee,
                equity_net=eq_net, hwm_after=hwm_after,
            ))
        hwm = hwm_after

    return VaultFeeSummary(
        aum_fee_total=aum_total,
        profit_share_total=ps_total,
        total_fees=aum_total + ps_total,
        final_equity_gross=final_gross,
        final_equity_net=final_net,
        final_hwm=hwm,
        steps=steps,
    )


# Alias for compatibility with "high-water mark" terminology in codebases
compute_high_water_mark_fee = compute_profit_share
