"""Regression tests for the C4-T1 archive intake gate and C4-T2 power solver.

Locks the anti-avoidance behaviour:
  - the committed placeholder parquet is rejected even with the fixture opt-in;
  - a flat full-window fixture is plumbing-only (never market data/evidence);
  - a truncated fixture is rejected even with the opt-in;
  - the multi-year duration solver is monotone and actually reaches target power.
"""
from __future__ import annotations

import json

from scripts import build_multi_year_validation_protocol as proto
from scripts import validate_hyperliquid_archive_intake as intake


def test_placeholder_is_always_rejected(tmp_path):
    res = intake.validate_archive(intake.KNOWN_PLACEHOLDER, allow_synthetic_fixture=True)
    assert res["verdict"] == "REJECT_NOT_EVIDENCE"
    assert res["is_market_data"] is False
    assert res["is_evidence"] is False
    assert res["performance_evidence"] is False
    assert any(c["check"] == "placeholder_not_evidence" and c["status"] == "fail"
               for c in res["checks"])


def test_flat_fixture_is_plumbing_only(tmp_path):
    flat = intake._write_fixture(
        tmp_path, "flat", ["BTC", "ETH"],
        intake.expected_hourly_bars(intake.SPEC_START, intake.SPEC_END), flat=True)
    rejected = intake.validate_archive(flat, allow_synthetic_fixture=False)
    assert rejected["verdict"] == "REJECT_NOT_EVIDENCE"
    accepted = intake.validate_archive(flat, allow_synthetic_fixture=True)
    assert accepted["verdict"] == "ACCEPT_FIXTURE_NON_EVIDENCE"
    assert accepted["is_market_data"] is False
    assert accepted["is_evidence"] is False
    assert accepted["performance_evidence"] is False


def test_truncated_fixture_is_rejected_even_with_optin(tmp_path):
    trunc = intake._write_fixture(tmp_path, "trunc", ["BTC", "ETH"], 300, flat=False)
    res = intake.validate_archive(trunc, allow_synthetic_fixture=True)
    assert res["verdict"] == "REJECT_NOT_EVIDENCE"
    assert any(c["check"] == "window_coverage" and c["status"] == "fail"
               for c in res["checks"])


def test_selftest_expectations_hold(tmp_path):
    st = intake.run_selftest(tmp_path)
    assert st["all_expectations_met"] is True
    assert st["case_count"] >= 3


def test_power_solver_reaches_target_and_is_monotone():
    rate = 0.012355212355212355
    sol = proto.days_for_power(rate, 10, 0.80)
    assert sol["solvable"] is True
    assert sol["achieved_power_at_solution"] >= 0.80 - 1e-6
    shorter = proto.poisson_sf(10, rate * sol["required_days"] * 0.5)
    assert shorter < 0.80
    assert proto.days_for_power(rate, 10, 0.95)["required_days"] > sol["required_days"]


def test_committed_protocol_locks_no_go_with_executable_requirement():
    artifacts = sorted(proto.STATE.glob("multi_year_validation_protocol_*.json"))
    assert artifacts, "C4-T2 artifact must be on disk"
    data = json.loads(artifacts[-1].read_text())
    assert data["decision_lock"]["current_verdict"] == "NO_GO"
    assert data["power_calculation"]["required_for_80pct_power"]["required_days"] > 365
    assert data["minimum_independent_episodes"] == 10
    assert data["performance_evidence"] is False