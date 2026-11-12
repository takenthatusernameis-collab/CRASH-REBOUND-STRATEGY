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
from datetime import datetime
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


def elapsed_hours_from_timestamps(timestamps: Sequence[Any],
                                  default_hours: float = 1.0) -> List[float]:
    """Derive per-step elapsed hours from ISO-8601 equity-curve timestamps.

    Fee accrual is hourly; an equity curve whose points are emitted only at trade
    exits (irregular gaps of hours/days) must be charged the TRUE elapsed hours
    between consecutive points, not a flat one-hour step (which under-charges AUM
    fees by the actual gap).

    Contract (fail-safe, no look-ahead beyond provided timestamps):
    - step 0 uses ``default_hours`` (the declared fee step, e.g. 1.0).
    - step i (i>=1) = hours between ``timestamps[i-1]`` and ``timestamps[i]``.
    - Unparseable/missing timestamp for step i -> ``default_hours``.
    - Negative delta (out-of-order/bad data) is clamped to 0.0 (never a negative
      fee time); zero hours charges no AUM fee for that step.

    Returns a list of length ``len(timestamps)`` of finite non-negative floats.
    """
    ts = list(timestamps or [])
    n = len(ts)
    if n == 0:
        return []
    dh = _finite(default_hours)
    if dh < 0.0:
        dh = 0.0
    hours: List[float] = [dh]
    prev = _parse_iso(ts[0])
    for i in range(1, n):
        cur = _parse_iso(ts[i])
        if prev is None or cur is None:
            hours.append(dh)
        else:
            delta = (cur - prev).total_seconds() / 3600.0
            hours.append(delta if delta > 0.0 else 0.0)
        prev = cur
    return hours


def _parse_iso(value: Any) -> Optional[Any]:
    """Parse an ISO-8601 timestamp to datetime; return None on missing/invalid."""
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        pass
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


# Alias for compatibility with "high-water mark" terminology in codebases
compute_high_water_mark_fee = compute_profit_share


class VaultFeeConfigError(ValueError):
    """Raised when vault fee configuration knobs are invalid (fail-closed).

    Callers (CLI runners, config constructors) must NOT silently substitute
    defaults or clamp invalid values; they must reject and surface the error.
    """


def validate_fee_config(aum_rate_annual: Any,
                        profit_share_rate: Any,
                        fee_hours_per_step: Any) -> tuple[float, float, float]:
    """Validate explicit fee config knobs; raise VaultFeeConfigError on invalid.

    Fail-closed contract: negative, NaN, non-finite, or non-numeric values are
    REJECTED (no silent substitution, no clamping to a default). Zero is permitted
    as an explicit degenerate disable (no fee of that type).

    Returns the validated (aum_rate_annual, profit_share_rate, fee_hours_per_step)
    as floats so callers can rely on typed values.
    """
    def _check(name: str, value: Any) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            raise VaultFeeConfigError(
                f"{name} must be numeric, got {value!r}"
            ) from None
        if not math.isfinite(v):
            raise VaultFeeConfigError(
                f"{name} must be a finite number, got {value!r}"
            )
        if v < 0.0:
            raise VaultFeeConfigError(
                f"{name} must be >= 0, got {v:g}"
            )
        return v

    a = _check("aum_rate_annual", aum_rate_annual)
    p = _check("profit_share_rate", profit_share_rate)
    h = _check("fee_hours_per_step", fee_hours_per_step)
    return a, p, h


def fee_config_from_args(args: Any) -> dict[str, Any]:
    """Extract validated fee config knobs from an argparse Namespace.

    Unspecified knobs (None) are left ABSENT from the returned dict so callers
    apply the module defaults (DEFAULT_AUM_FEE_ANNUAL / DEFAULT_PROFIT_SHARE / 1.0)
    unchanged. Any explicitly-provided knob is validated via validate_fee_config;
    a single invalid knob rejects the whole set (no partial substitution).

    Typical argparse attribute names: aum_rate_annual, profit_share_rate,
    fee_hours_per_step (from --aum-rate-annual, --profit-share-rate,
    --fee-hours-per-step).
    """
    kwargs: dict[str, Any] = {}
    for attr, key in (("aum_rate_annual", "aum_rate_annual"),
                      ("profit_share_rate", "profit_share_rate"),
                      ("fee_hours_per_step", "fee_hours_per_step")):
        v = getattr(args, attr, None)
        if v is not None:
            kwargs[key] = v
    if kwargs:
        validate_fee_config(
            kwargs.get("aum_rate_annual", DEFAULT_AUM_FEE_ANNUAL),
            kwargs.get("profit_share_rate", DEFAULT_PROFIT_SHARE),
            kwargs.get("fee_hours_per_step", 1.0),
        )
    return kwargs
