"""C22 campaign tests (MEXC out-of-sample replication infrastructure).

Covers the offline-verifiable pieces of the C22 campaign so future sessions can trust the
data layer and the gate:
  * MEXC kline normalization (volume unit convention: close*volume == quote USD)
  * MEXC forward pagination (no gaps, no duplicates, full window coverage)
  * C22 prereg schema + frozen spec-literal config
  * C22 acceptance gate transitions (PENDING -> PASS, and FAIL on drift/inconsistency)
"""

import json

import scripts.fetch_mexc_perp_archive as mexc
import scripts.build_c22_prereg as c22pre
import scripts.verify_c22_focus_campaign as c22gate


# ---------------------------------------------------------------------------
# MEXC normalization
# ---------------------------------------------------------------------------

def test_normalize_mexc_row_volume_convention():
    # amount (quote USD) / close = base-coin-equivalent volume; close*volume == amount.
    c = mexc.normalize_mexc_row(
        time_s=1704067200, o=100.0, h=110.0, l=99.0, c=105.0,
        vol=12345.0, amount=21000.0,
    )
    assert c is not None
    assert abs(c["volume"] - 21000.0 / 105.0) < 1e-9
    assert abs(c["close"] * c["volume"] - c["quote_volume_usd"]) < 1e-6
    assert c["timestamp"] == 1704067200 * 1000
    assert c["timestamp_ms"] == c["timestamp"]


def test_normalize_mexc_row_falls_back_to_contracts_when_amount_missing():
    c = mexc.normalize_mexc_row(1704067200, 100.0, 110.0, 99.0, 105.0, vol=500.0, amount=0.0)
    assert c is not None
    assert c["volume"] == 500.0  # amount<=0 -> raw contracts


def test_normalize_mexc_row_rejects_bad_ohlc():
    assert mexc.normalize_mexc_row(1704067200, 100.0, 90.0, 99.0, 105.0, 1.0, 1.0) is None  # h<l
    assert mexc.normalize_mexc_row(1704067200, 100.0, 101.0, 102.0, 103.0, 1.0, 1.0) is None  # l>o,cl


# ---------------------------------------------------------------------------
# MEXC pagination
# ---------------------------------------------------------------------------

def _fake_full_coverage_page(symbol, start_s, end_s, session, timeout, retries=4):
    """Serve every hourly bar in [start_s, end_s] (simulates a fully-covered venue)."""
    rows = []
    t = start_s
    while t <= end_s:
        rows.append({"time": t, "open": 100.0, "high": 101.0, "low": 99.0,
                     "close": 100.0, "vol": 10.0, "amount": 1000.0})
        t += 3600
    return rows


def test_mexc_fetch_range_paginates_without_gaps(monkeypatch):
    monkeypatch.setattr(mexc, "mexc_kline_page", _fake_full_coverage_page)
    start_ms = 1704067200000  # 2024-01-01T00:00:00Z
    end_ms = start_ms + 5000 * 3600000  # 5000 hours (forces >1 window at 1500h)
    candles, meta = mexc.mexc_fetch_range(
        "SOL", start_ms, end_ms, session=None, timeout=1,
        window_hours=1500, sleep_s=0,
    )
    expected = (end_ms - start_ms) // 3600000 + 1
    assert len(candles) == expected
    # sorted + contiguous (no gaps, no dupes)
    for i in range(1, len(candles)):
        assert candles[i]["timestamp"] - candles[i - 1]["timestamp"] == 3600000
    assert candles[0]["timestamp"] == start_ms
    assert candles[-1]["timestamp"] == end_ms
    assert meta["venue"] == "mexc"
    assert meta["pages_fetched"] >= 3


# ---------------------------------------------------------------------------
# Prereg
# ---------------------------------------------------------------------------

def test_c22_prereg_schema_and_frozen_config():
    p = c22pre.build_prereg()
    assert p["campaign"] == "C22"
    assert p["prereg_status"] == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert p["binding_task"] == "C22-T1"
    # frozen spec-literal config
    for k, v in c22gate.FROZEN_CONFIG.items():
        assert p["config"].get(k) == v, f"config drift on {k}"
    assert p["config"]["seed"] == c22pre.SEED
    # provenance: real, cross-venue, never Hyperliquid
    assert p["provenance"]["real_market_data"] is True
    assert p["provenance"]["fabricated_data"] is False
    assert p["provenance"]["is_hyperliquid_venue_data"] is False
    assert p["provenance"]["venue"] == "mexc"
    # folds + required artifacts
    assert [f["id"] for f in p["folds"]] == ["2023", "2024", "2025", "2026YTD"]
    assert len(p["required_artifacts"]) == len(c22gate.BATTERY_ARTIFACTS) + 2  # + prereg json/md


def test_c22_prereg_markdown_render():
    md = c22pre.render_markdown(c22pre.build_prereg())
    for needle in ("C22", "PRE_REGISTERED_BEFORE_COMPUTE", "Fixed config",
                   "Decision rules", "Guardrails", "verify_c22_focus_campaign.py"):
        assert needle in md


# ---------------------------------------------------------------------------
# Acceptance gate transitions
# ---------------------------------------------------------------------------

def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _seed_prereq(state):
    pre = c22pre.build_prereg()
    _write(state / f"c22_prereg_{c22gate.TS}.json", pre)
    (state / f"c22_prereg_{c22gate.TS}.md").write_text("# prereg\n")
    _write(state / f"c22_venue_acquisition_probe_{c22gate.TS}.json",
           {"c22_data_status": "ACQUISITION_VIABLE_MEXC_MULTIYEAR"})


def test_gate_pending_when_battery_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(c22gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    token, checks = c22gate.evaluate()
    assert token == "PENDING"
    assert checks["battery_present"] == 0
    assert len(checks["pending_missing"]) == len(c22gate.BATTERY_ARTIFACTS)


def test_gate_fail_on_config_drift(tmp_path, monkeypatch):
    monkeypatch.setattr(c22gate, "STATE", tmp_path)
    pre = c22pre.build_prereg()
    pre["config"]["rsi_threshold"] = 10.0  # drift
    _write(tmp_path / f"c22_prereg_{c22gate.TS}.json", pre)
    (tmp_path / f"c22_prereg_{c22gate.TS}.md").write_text("# prereg\n")
    _write(tmp_path / f"c22_venue_acquisition_probe_{c22gate.TS}.json",
           {"c22_data_status": "ACQUISITION_VIABLE_MEXC_MULTIYEAR"})
    token, checks = c22gate.evaluate()
    assert token == "FAIL"
    assert any("drift" in r for r in checks["fail_reasons"])


def test_gate_fail_when_acquisition_not_viable(tmp_path, monkeypatch):
    monkeypatch.setattr(c22gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _write(tmp_path / f"c22_venue_acquisition_probe_{c22gate.TS}.json",
           {"c22_data_status": "ACQUISITION_BLOCKED"})
    token, checks = c22gate.evaluate()
    assert token == "FAIL"


def test_gate_pass_when_battery_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(c22gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    prov = {"is_hyperliquid_venue_data": False, "fabricated_data": False, "synthetic_data": False}
    # battery artifacts
    _write(tmp_path / f"c22_mexc_fold_campaign_{c22gate.TS}.json", {"results": {"num_trades": 12}})
    _write(tmp_path / f"c22_mexc_fold_episode_edge_{c22gate.TS}.json", {"episode_audit": {"n_episodes": 6}})
    _write(tmp_path / f"c22_mexc_fold_placebo_{c22gate.TS}.json", {"placebo": {"runs": 2000}})
    _write(tmp_path / f"c22_mexc_fold_census_{c22gate.TS}.json", {"reconciliation": {}})
    _write(tmp_path / f"c22_decision_verdict_mexc_stability_{c22gate.TS}.json",
           {"verdict": "NO_GO", "provenance": prov})
    _write(tmp_path / f"c22_pooled_stability_synthesis_{c22gate.TS}.json",
           {"token": "NO_GO", "provenance": prov})
    _write(tmp_path / f"c22_decision_verdict_CONSOLIDATED_{c22gate.TS}.json",
           {"final_verdict_token": "NO_GO", "provenance": prov})
    token, checks = c22gate.evaluate()
    assert token == "PASS", checks
    assert checks["battery_present"] == len(c22gate.BATTERY_ARTIFACTS)


def test_gate_fail_on_mismatched_verdicts(tmp_path, monkeypatch):
    monkeypatch.setattr(c22gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    prov = {"is_hyperliquid_venue_data": False}
    _write(tmp_path / f"c22_mexc_fold_campaign_{c22gate.TS}.json", {})
    _write(tmp_path / f"c22_mexc_fold_episode_edge_{c22gate.TS}.json", {})
    _write(tmp_path / f"c22_mexc_fold_placebo_{c22gate.TS}.json", {})
    _write(tmp_path / f"c22_mexc_fold_census_{c22gate.TS}.json", {})
    _write(tmp_path / f"c22_decision_verdict_mexc_stability_{c22gate.TS}.json",
           {"verdict": "NO_GO", "provenance": prov})
    _write(tmp_path / f"c22_pooled_stability_synthesis_{c22gate.TS}.json",
           {"token": "NO_GO", "provenance": prov})
    _write(tmp_path / f"c22_decision_verdict_CONSOLIDATED_{c22gate.TS}.json",
           {"final_verdict_token": "STABLE_POSITIVE_SUBSET", "provenance": prov})
    token, checks = c22gate.evaluate()
    assert token == "FAIL"
    assert any("!=" in p for p in checks["consistency_problems"])