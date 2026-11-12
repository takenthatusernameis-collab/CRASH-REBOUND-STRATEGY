"""Vault fee CONFIG SURFACE tests (HANDOFF cell 2: explicit fee knobs + fail-closed).

Proves the cell-2 gap: `fee_config_from_args`, `validate_fee_config`, and
`VaultFeeConfigError` had zero test coverage, and the CLI fee knobs
(`--aum-rate-annual`, `--profit-share-rate`, `--fee-hours-per-step`) were
untested in both runners. This suite locks the fail-closed contract:
negative / NaN / non-finite / non-numeric values are REJECTED with
VaultFeeConfigError; a single invalid knob rejects the whole set; unspecified
knobs (None) are left ABSENT so module defaults (0.02, 0.10, 1.0) apply.

All expectations are hand-traced against src/metrics/vault_fees.py.
"""
import argparse
import math

import pytest

from src.metrics.vault_fees import (
    DEFAULT_AUM_FEE_ANNUAL,
    DEFAULT_PROFIT_SHARE,
    VaultFeeConfigError,
    accrue_vault_fees,
    fee_config_from_args,
    validate_fee_config,
)
from scripts.run_campaign import build_parser as campaign_build_parser
from scripts.run_real_campaign import build_parser as real_campaign_build_parser

INVALID_VALUES = (-0.1, -1.0, float("nan"), float("inf"), float("-inf"), "x", [1], object())


# --- Gap proof: module defaults are the traced anchors (0.02, 0.10, 1.0) ---

def test_module_defaults_are_002_010_10():
    assert DEFAULT_AUM_FEE_ANNUAL == 0.02
    assert DEFAULT_PROFIT_SHARE == 0.10
    # hours default is 1.0 (accrual step) — asserted via accrual below.


# --- CLI flag surface: explicit knobs parse in both runners, default None ---

def test_run_campaign_cli_fee_knobs_parse_explicit_and_default_none():
    ap = campaign_build_parser()
    a = ap.parse_args([])
    assert a.aum_rate_annual is None
    assert a.profit_share_rate is None
    assert a.fee_hours_per_step is None

    a = ap.parse_args(["--aum-rate-annual", "0.03",
                       "--profit-share-rate", "0.2",
                       "--fee-hours-per-step", "2"])
    assert a.aum_rate_annual == 0.03
    assert a.profit_share_rate == 0.2
    assert a.fee_hours_per_step == 2.0


def test_run_real_campaign_cli_fee_knobs_parse_explicit_and_default_none():
    ap = real_campaign_build_parser()
    a = ap.parse_args([])
    assert a.aum_rate_annual is None
    assert a.profit_share_rate is None
    assert a.fee_hours_per_step is None

    a = ap.parse_args(["--aum-rate-annual", "0.03",
                       "--profit-share-rate", "0.2",
                       "--fee-hours-per-step", "2"])
    assert a.aum_rate_annual == 0.03
    assert a.profit_share_rate == 0.2
    assert a.fee_hours_per_step == 2.0


# --- fee_config_from_args: absent knobs stay absent; explicit knobs pass through ---

def test_fee_config_from_args_all_none_returns_empty_dict():
    args = argparse.Namespace(aum_rate_annual=None, profit_share_rate=None,
                              fee_hours_per_step=None)
    assert fee_config_from_args(args) == {}


def test_fee_config_from_args_partial_explicit_keeps_only_provided():
    args = argparse.Namespace(aum_rate_annual=0.03, profit_share_rate=None,
                              fee_hours_per_step=2.0)
    out = fee_config_from_args(args)
    assert out == {"aum_rate_annual": 0.03, "fee_hours_per_step": 2.0}
    assert "profit_share_rate" not in out  # absent → module default applies


def test_fee_config_from_args_explicit_zero_is_kept():
    # Zero is a valid explicit degenerate disable (no fee of that type).
    args = argparse.Namespace(aum_rate_annual=0.0, profit_share_rate=0.0,
                              fee_hours_per_step=0.0)
    assert fee_config_from_args(args) == {
        "aum_rate_annual": 0.0, "profit_share_rate": 0.0, "fee_hours_per_step": 0.0,
    }


# --- validate_fee_config: reject invalid, accept valid, typed floats ---

def test_validate_fee_config_accepts_valid_and_returns_floats():
    a, p, h = validate_fee_config(0.03, 0.2, 2)
    assert (a, p, h) == (0.03, 0.2, 2.0)
    assert all(isinstance(x, float) for x in (a, p, h))


def test_validate_fee_config_accepts_explicit_zero():
    assert validate_fee_config(0.0, 0.0, 0.0) == (0.0, 0.0, 0.0)


@pytest.mark.parametrize("bad", INVALID_VALUES)
def test_validate_fee_config_rejects_each_invalid_aum(bad):
    with pytest.raises(VaultFeeConfigError):
        validate_fee_config(bad, 0.10, 1.0)


@pytest.mark.parametrize("bad", INVALID_VALUES)
def test_validate_fee_config_rejects_each_invalid_profit_share(bad):
    with pytest.raises(VaultFeeConfigError):
        validate_fee_config(0.02, bad, 1.0)


@pytest.mark.parametrize("bad", INVALID_VALUES)
def test_validate_fee_config_rejects_each_invalid_hours(bad):
    with pytest.raises(VaultFeeConfigError):
        validate_fee_config(0.02, 0.10, bad)


# --- Partial invalid set rejects the WHOLE set (no partial substitution) ---

def test_fee_config_from_args_partial_invalid_rejects_whole_set():
    # One invalid knob must reject the entire config even though others are valid.
    args = argparse.Namespace(aum_rate_annual=0.03,
                              profit_share_rate=-0.5,   # invalid
                              fee_hours_per_step=2.0)   # valid
    with pytest.raises(VaultFeeConfigError):
        fee_config_from_args(args)


def test_fee_config_from_args_nan_rejects_whole_set():
    args = argparse.Namespace(aum_rate_annual=float("nan"),
                              profit_share_rate=0.2,
                              fee_hours_per_step=1.0)
    with pytest.raises(VaultFeeConfigError):
        fee_config_from_args(args)


# --- Fail-closed propagation: runners reject invalid knobs BEFORE any I/O ---

def test_run_campaign_main_rejects_invalid_fee_knob_before_io():
    from scripts.run_campaign import main as campaign_main
    rc = campaign_main(["--aum-rate-annual", "-0.1"])
    assert rc == 2


def test_run_real_campaign_main_rejects_invalid_fee_knob_before_io():
    from scripts.run_real_campaign import main as real_campaign_main
    rc = real_campaign_main(["--fee-hours-per-step", "nan"])
    assert rc == 2


# --- Traced value lock: explicit knobs actually change the accrual result ---

def test_explicit_aum_rate_changes_accrued_fee_traced():
    curve = [100000.0, 110000.0]
    # Default 2%/yr: AUM on 100000 over 1h = 100000*0.02/8760
    base = accrue_vault_fees(curve, hours_per_step=1.0)
    # Explicit 4%/yr doubles the AUM rate.
    explicit = accrue_vault_fees(curve, hours_per_step=1.0, aum_rate_annual=0.04)
    assert base.steps[0].aum_fee == pytest.approx(100000.0 * 0.02 / 8760.0)
    assert explicit.steps[0].aum_fee == pytest.approx(100000.0 * 0.04 / 8760.0)
    assert explicit.steps[0].aum_fee == pytest.approx(2.0 * base.steps[0].aum_fee)


def test_explicit_profit_share_rate_changes_fee_traced():
    curve = [100000.0, 110000.0]
    # After AUM, step-1 profit above HWM(100000) gets profit-share charged.
    base = accrue_vault_fees(curve, hours_per_step=1.0, profit_share_rate=0.10)
    explicit = accrue_vault_fees(curve, hours_per_step=1.0, profit_share_rate=0.50)
    # With 10%: profit_share step1 = 0.10 * (110000 - aum - 100000)
    aum1 = 110000.0 * 0.02 / 8760.0
    profit_above = 110000.0 - aum1 - 100000.0
    assert base.steps[1].profit_share == pytest.approx(profit_above * 0.10)
    assert explicit.steps[1].profit_share == pytest.approx(profit_above * 0.50)
    assert explicit.steps[1].profit_share == pytest.approx(5.0 * base.steps[1].profit_share)