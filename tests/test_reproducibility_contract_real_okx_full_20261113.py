from __future__ import annotations

import json
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / 'research_state/cache/okx_1h_full_20251220_20260928/provenance.json'
CACHE_DIR = REPO_ROOT / 'research_state/cache/okx_1h_full_20251220_20260928'
UNIVERSE = REPO_ROOT / 'research_state/universe_okx_full_verified.json'
CANONICAL = REPO_ROOT / 'research_state/campaign_results_real_okx_full.json'
OUT_PREFIX = 'reproducibility_check_real_okx_full'


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.skipif(
    not (MANIFEST.exists() and CACHE_DIR.exists() and UNIVERSE.exists() and CANONICAL.exists()),
    reason='canonical OKX on-disk artifacts required for reproducibility contract',
)
def test_reproducibility_contract_real_okx_full():
    out_json = REPO_ROOT / 'research_state' / f'{OUT_PREFIX}.json'
    out_metrics_json = REPO_ROOT / 'research_state' / f'{OUT_PREFIX}_metrics.json'
    out_metrics_csv = REPO_ROOT / 'research_state' / f'{OUT_PREFIX}_metrics.csv'
    produced = [out_json, out_metrics_json, out_metrics_csv]
    # clean only our own rerun files if present from a prior failed run
    for p in produced:
        if p.exists():
            p.unlink()

    canon_sha_before = _sha256(CANONICAL)
    canon_metrics = REPO_ROOT / 'research_state/campaign_results_real_okx_full_metrics.json'
    canon_metrics_sha_before = _sha256(canon_metrics) if canon_metrics.exists() else None

    env = os.environ.copy()
    env['PYTHONPATH'] = '.'
    cmd = [
        sys.executable, 'scripts/run_real_campaign.py',
        '--manifest', str(MANIFEST.relative_to(REPO_ROOT)),
        '--cache-dir', str(CACHE_DIR.relative_to(REPO_ROOT)),
        '--universe-file', str(UNIVERSE.relative_to(REPO_ROOT)),
        '--output-prefix', OUT_PREFIX,
        '--apply-vault-fees',
    ]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True)
    try:
        assert proc.returncode == 0, f'repro run failed rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}'
        assert out_json.exists(), 'reproducibility run did not produce campaign JSON'

        canon = json.loads(CANONICAL.read_text())
        rerun = json.loads(out_json.read_text())

        # Volatile fields: top-level timestamp and any derived volatile fields must not block equivalence.
        # Contract: reproduced results.trades and results.total_pnl from committed on-disk inputs.
        assert rerun.get('results', {}).get('trades') == canon.get('results', {}).get('trades'), (
            'results.trades differ from canonical artifact'
        )
        assert rerun.get('results', {}).get('total_pnl') == canon.get('results', {}).get('total_pnl'), (
            'results.total_pnl differs from canonical artifact'
        )
        assert rerun.get('results', {}).get('num_trades') == canon.get('results', {}).get('num_trades')
        assert rerun.get('run_type') == 'real_market_campaign'
        assert rerun.get('real_market_data') is True
        assert rerun.get('performance_evidence') is True
        assert rerun.get('fabricated_data') is False

        # Gate integrity: volume filter/gating contract must remain enabled and spec-compliant in output.
        cfg = rerun.get('config') or {}
        assert cfg.get('min_daily_volume_usd', 0) >= 5_000_000
        assert cfg.get('enable_volume_based_sizing') is True or 'min_daily_volume_usd' in cfg

        # Canonical artifacts must be untouched by a rerun to a distinct prefix.
        assert _sha256(CANONICAL) == canon_sha_before, 'canonical campaign artifact was modified'
        if canon_metrics.exists() and canon_metrics_sha_before is not None:
            assert _sha256(canon_metrics) == canon_metrics_sha_before, 'canonical metrics artifact was modified'
    finally:
        # delete only our own rerun files
        for p in produced:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass
