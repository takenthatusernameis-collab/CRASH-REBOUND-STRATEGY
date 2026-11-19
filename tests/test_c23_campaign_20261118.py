"""C23 campaign tests (Bitget USDT-M out-of-sample replication infrastructure).

Covers the offline-verifiable pieces so future sessions can trust the data layer and the gate:
  * Bitget kline normalization (volume unit convention: volume == quoteVol/close)
  * Bitget backward pagination (no gaps, no duplicates, full window coverage)
  * C23 prereg schema + frozen spec-literal config
  * C23 acceptance gate transitions (PENDING -> PASS, and FAIL on drift/inconsistency)
"""

import hashlib
import json

import scripts.fetch_bitget_perp_archive as bitget
import scripts.build_c23_prereg as c23pre
import scripts.verify_c23_focus_campaign as c23gate


# ---------------------------------------------------------------------------
# Bitget normalization
# ---------------------------------------------------------------------------

def test_normalize_bitget_row_volume_convention():
    c = bitget.normalize_bitget_row(1704067200000, 100.0, 110.0, 99.0, 105.0,
                                    base_vol=200.0, quote_vol=21000.0)
    assert c is not None
    assert abs(c["volume"] - 21000.0 / 105.0) < 1e-9
    assert abs(c["close"] * c["volume"] - c["quote_volume_usd"]) < 1e-6
    assert c["timestamp"] == 1704067200000
    assert c["timestamp_ms"] == c["timestamp"]


def test_normalize_bitget_row_falls_back_to_base_volume():
    c = bitget.normalize_bitget_row(1704067200000, 100.0, 110.0, 99.0, 105.0,
                                    base_vol=500.0, quote_vol=0.0)
    assert c is not None
    assert c["volume"] == 500.0
    assert c["quote_volume_usd"] == 0.0


def test_normalize_bitget_row_rejects_bad_ohlc():
    assert bitget.normalize_bitget_row(1, 100.0, 90.0, 99.0, 105.0, 1.0, 1.0) is None  # h<l
    assert bitget.normalize_bitget_row(1, 100.0, 101.0, 102.0, 103.0, 1.0, 1.0) is None  # l>o,cl


# ---------------------------------------------------------------------------
# Bitget pagination
# ---------------------------------------------------------------------------

def _fake_full_coverage_page(base, start_ms, end_ms, session, timeout, retries=5):
    """Serve every hourly bar in [start_ms, end_ms) (simulates a fully-covered venue)."""
    rows = []
    t = start_ms
    while t < end_ms:
        rows.append({"time_ms": t, "open": 100.0, "high": 101.0, "low": 99.0,
                     "close": 100.0, "base_vol": 10.0, "quote_vol": 1000.0})
        t += 3_600_000
    return rows


def test_bitget_fetch_range_paginates_without_gaps(monkeypatch):
    monkeypatch.setattr(bitget, "bitget_page", _fake_full_coverage_page)
    start_ms = 1704067200000  # 2024-01-01T00:00:00Z
    end_ms = start_ms + 500 * 3_600_000  # 500 hours -> forces >=3 backward windows
    candles, meta = bitget.bitget_fetch_range(
        "SOL", start_ms, end_ms, session=None, timeout=1, sleep_s=0,
    )
    expected = (end_ms - start_ms) // 3_600_000 + 1
    assert len(candles) == expected
    assert candles[0]["timestamp"] == start_ms
    assert candles[-1]["timestamp"] == end_ms
    for i in range(1, len(candles)):
        assert candles[i]["timestamp"] - candles[i - 1]["timestamp"] == 3_600_000
    assert meta["venue"] == "bitget"
    assert meta["pages_fetched"] >= 3


# ---------------------------------------------------------------------------
# Prereg
# ---------------------------------------------------------------------------

def test_c23_prereg_schema_and_frozen_config():
    p = c23pre.build_prereg()
    assert p["campaign"] == "C23"
    assert p["prereg_status"] == "PRE_REGISTERED_BEFORE_COMPUTE"
    assert p["binding_task"] == "C23-T1"
    for k, v in c23gate.FROZEN_CONFIG.items():
        assert p["config"].get(k) == v, f"config drift on {k}"
    assert p["config"]["seed"] == c23pre.SEED
    assert p["provenance"]["real_market_data"] is True
    assert p["provenance"]["fabricated_data"] is False
    assert p["provenance"]["is_hyperliquid_venue_data"] is False
    assert p["provenance"]["venue"] == "bitget"
    assert [f["id"] for f in p["folds"]] == c23gate.FOLD_IDS
    assert len(p["required_artifacts"]) == len(c23gate.BATTERY_ARTIFACTS) + 2  # + prereg json/md


def test_c23_prereg_markdown_render():
    md = c23pre.render_markdown(c23pre.build_prereg())
    for needle in ("C23", "PRE_REGISTERED_BEFORE_COMPUTE", "Fixed config",
                   "Decision rules", "Guardrails", "verify_c23_focus_campaign.py"):
        assert needle in md


# ---------------------------------------------------------------------------
# Acceptance gate transitions
# ---------------------------------------------------------------------------

def _write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _seed_prereq(state):
    _write(state / f"c23_prereg_{c23gate.TS}.json", c23pre.build_prereg())
    (state / f"c23_prereg_{c23gate.TS}.md").write_text("# prereg\n")
    _write(state / f"c23_venue_acquisition_probe_{c23gate.TS}.json",
           {"c23_data_status": "ACQUISITION_VIABLE_BITGET_MULTIYEAR"})


def _seed_battery(state, bitget_token="NO_GO", consolidated_token="NO_GO"):
    prov = {"is_hyperliquid_venue_data": False, "fabricated_data": False, "synthetic_data": False}
    pre_sha = hashlib.sha256((state / f"c23_prereg_{c23gate.TS}.json").read_bytes()).hexdigest()
    _write(state / f"c23_bitget_fold_campaign_{c23gate.TS}.json",
           {"campaign": "C23", "folds": [{"id": f} for f in c23gate.FOLD_IDS]})
    _write(state / f"c23_bitget_fold_episode_edge_{c23gate.TS}.json", {"campaign": "C23"})
    _write(state / f"c23_bitget_fold_placebo_{c23gate.TS}.json", {"campaign": "C23"})
    _write(state / f"c23_bitget_fold_census_{c23gate.TS}.json", {"campaign": "C23"})
    _write(state / f"c23_decision_verdict_bitget_stability_{c23gate.TS}.json",
           {"campaign": "C23", "verdict": bitget_token, "provenance": prov})
    _write(state / f"c23_pooled_stability_synthesis_{c23gate.TS}.json",
           {"campaign": "C23", "token": bitget_token, "provenance": prov})
    _write(state / f"c23_decision_verdict_CONSOLIDATED_{c23gate.TS}.json",
           {"campaign": "C23", "final_verdict_token": consolidated_token,
            "provenance": prov, "prereg_sha256": pre_sha})


def test_gate_pending_when_battery_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    token, checks = c23gate.evaluate()
    assert token == "PENDING"
    assert checks["battery_present"] == 0
    assert len(checks["pending_missing"]) == len(c23gate.BATTERY_ARTIFACTS)


def test_gate_fail_on_config_drift(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    pre = c23pre.build_prereg()
    pre["config"]["rsi_threshold"] = 10.0
    _write(tmp_path / f"c23_prereg_{c23gate.TS}.json", pre)
    (tmp_path / f"c23_prereg_{c23gate.TS}.md").write_text("# prereg\n")
    _write(tmp_path / f"c23_venue_acquisition_probe_{c23gate.TS}.json",
           {"c23_data_status": "ACQUISITION_VIABLE_BITGET_MULTIYEAR"})
    token, checks = c23gate.evaluate()
    assert token == "FAIL"
    assert any("drift" in r for r in checks["fail_reasons"])


def test_gate_fail_when_acquisition_not_viable(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _write(tmp_path / f"c23_venue_acquisition_probe_{c23gate.TS}.json",
           {"c23_data_status": "ACQUISITION_BLOCKED"})
    token, _ = c23gate.evaluate()
    assert token == "FAIL"


def test_gate_pass_when_battery_complete(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _seed_battery(tmp_path)
    token, checks = c23gate.evaluate()
    assert token == "PASS", checks
    assert checks["battery_present"] == len(c23gate.BATTERY_ARTIFACTS)


def test_gate_fail_on_mismatched_verdicts(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _seed_battery(tmp_path, bitget_token="NO_GO", consolidated_token="STABLE_POSITIVE_SUBSET")
    token, checks = c23gate.evaluate()
    assert token == "FAIL"
    assert any("!=" in p for p in checks["consistency_problems"])


def test_gate_fail_when_hyperliquid_mislabel(tmp_path, monkeypatch):
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _seed_battery(tmp_path)
    _write(tmp_path / f"c23_decision_verdict_CONSOLIDATED_{c23gate.TS}.json",
           {"campaign": "C23", "final_verdict_token": "NO_GO",
            "provenance": {"is_hyperliquid_venue_data": True}})
    token, checks = c23gate.evaluate()
    assert token == "FAIL"
    assert any("Hyperliquid" in p for p in checks["consistency_problems"])


def test_gate_accepts_runner_nested_pooled_token(tmp_path, monkeypatch):
    """Real runner artifacts nest the pooled token as {"decision": {"token": ...}}."""
    monkeypatch.setattr(c23gate, "STATE", tmp_path)
    _seed_prereq(tmp_path)
    _seed_battery(tmp_path)
    prov = {"is_hyperliquid_venue_data": False, "fabricated_data": False, "synthetic_data": False}
    _write(tmp_path / f"c23_pooled_stability_synthesis_{c23gate.TS}.json",
           {"campaign": "C23", "venue_tokens": ["NO_GO"], "provenance": prov,
            "decision": {"token": "NO_GO", "rationale": "nested"}})
    token, checks = c23gate.evaluate()
    assert token == "PASS", checks
