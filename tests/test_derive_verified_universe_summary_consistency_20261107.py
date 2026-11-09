"""2026-11-07 failing-tests-first: derive_verified_universe real_market_data labeling must be
authoritative over validated symbol facts, never over a manifest summary label.

Campaign item 4 residual (summary-consumer hardening). derive_verified_universe.py reads
manifest.summary.all_complete directly to label real_market_data. A manifest whose summary
claims all_complete=true while symbol coverage facts do not prove completeness must NOT
produce real_market_data=true; derivation must fail closed (reject selection) when the
summary contradicts validated symbol facts. Archived-verified evidence only; never fabricate.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.derive_verified_universe import main as derive_main


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _varied_candles(n=30, start_ms=1_766_188_800_000):
    out = []
    for i in range(n):
        px = 100.0 + i * 0.5
        out.append({"timestamp": start_ms + i * 3_600_000, "open": px, "high": px + 1, "low": px - 1, "close": px + 0.2, "volume": 3000.0})
    return out


def _run(argv, monkeypatch):
    import scripts.derive_verified_universe as dv
    monkeypatch.setattr(sys, "argv", argv)
    try:
        return dv.main()
    except SystemExit as e:
        code = e.code
        return 1 if (code is None or isinstance(code, str)) else int(code)


def _manifest(tmp_path, candles, *, summary_all_complete, coverage_complete_flag=True,
              coverage_expected_bars=None, coverage_observed_bars=None, coverage_gap_count=0,
              symbol_status="ok", synthetic=False):
    # Repo-local fixture dir: pytest tmp_path lives under the harness _temp/kilo-tmp
    # scratch tree, which the hardened temp-path guard rejects as unverified
    # provenance evidence. Verified cache shapes must live repo-LOCAL. The caller
    # must hold the returned TemporaryDirectory alive until the derivation finishes.
    import tempfile
    td = tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[1]))
    cache_dir = Path(td.name) / "cache"
    candles_dir = cache_dir / "candles"
    candles_dir.mkdir(parents=True)
    (candles_dir / "BTC.json").write_text(json.dumps(candles))
    n = len(candles)
    first = candles[0]["timestamp"]
    last = candles[-1]["timestamp"]
    exp_bars = n if coverage_expected_bars is None else coverage_expected_bars
    obs_bars = n if coverage_observed_bars is None else coverage_observed_bars
    manifest = {
        "schema_version": 1, "source": "test", "fabricated_data": False,
        "summary": {"all_complete": summary_all_complete, "ready_for_real_campaign": summary_all_complete},
        "target_window": {"start": _iso(first), "end": _iso(last)},
        "symbols": {
            "BTC": {
                "status": symbol_status,
                "cache_path": str(candles_dir / "BTC.json"),
                "synthetic_check": {"is_synthetic": synthetic, "reason": "varied_series_ok"},
                "coverage": {
                    "complete_for_target_window": coverage_complete_flag,
                    "expected_hourly_bars": exp_bars,
                    "observed_in_window_bars": obs_bars,
                    "gap_count": coverage_gap_count,
                },
            }
        },
    }
    mp = tmp_path / "manifest.json"
    mp.write_text(json.dumps(manifest))
    return mp, cache_dir, tmp_path / "universe.json", td


class TestDeriveSummaryContradictionFailClosed:
    def test_summary_claims_complete_but_coverage_fields_do_not_prove_it(self, tmp_path, monkeypatch):
        # Manifest summary says all_complete=true and coverage flag says complete, but
        # coverage.expected_hourly_bars does not match the window -> facts do not prove
        # completeness. Current code trusts summary -> real_market_data=true (BUG).
        candles = _varied_candles()
        mp, cache_dir, out, _tmpd = _manifest(
            tmp_path, candles, summary_all_complete=True,
            coverage_complete_flag=True, coverage_expected_bars=999,
        )
        rc = _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        assert rc != 0, "derivation must fail closed when summary contradicts validated symbol facts"
        if out.exists():
            d = json.loads(out.read_text())
            assert d.get("real_market_data") is not True, d
            assert "BTC" not in (d.get("selected_symbols") or []), d

    def test_summary_claims_complete_and_facts_prove_it_still_works(self, tmp_path, monkeypatch):
        # Truthful manifest: summary + coverage facts both complete -> real_market_data true.
        candles = _varied_candles()
        mp, cache_dir, out, _tmpd = _manifest(
            tmp_path, candles, summary_all_complete=True,
            coverage_complete_flag=True, coverage_expected_bars=len(candles),
        )
        rc = _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        assert rc == 0, rc
        d = json.loads(out.read_text())
        assert d.get("real_market_data") is True, d
        assert "BTC" in (d.get("selected_symbols") or []), d

    def test_summary_all_complete_false_does_not_block_when_facts_prove_complete(self, tmp_path, monkeypatch):
        # Campaign item 4 residual (stale-pessimistic hardening): manifest summary is
        # advisory only. When validated symbol facts prove all symbols are complete,
        # non-synthetic, and coverage-consistent, stale-pessimistic summary labels must
        # NOT block derivation or prevent truthful real_market_data/selection output.
        # Optimistic contradictions (summary claims complete but facts do not prove it)
        # remain fail-closed (covered by test_summary_claims_complete_but_coverage_fields_do_not_prove_it).
        candles = _varied_candles()
        mp, cache_dir, out, _tmpd = _manifest(
            tmp_path, candles, summary_all_complete=False,
            coverage_complete_flag=True, coverage_expected_bars=len(candles),
        )
        rc = _run(["derive_verified_universe.py", "--manifest", str(mp), "--cache-dir", str(cache_dir), "--output", str(out)], monkeypatch)
        assert rc == 0, rc
        d = json.loads(out.read_text())
        assert d.get("real_market_data") is True, d
        assert "BTC" in (d.get("selected_symbols") or []), d
