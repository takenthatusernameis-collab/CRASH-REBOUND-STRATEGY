#!/usr/bin/env python3
"""C3-T2 — full-window campaign dry-run readiness harness.

WHY THIS EXISTS
---------------
The only path to decision-grade evidence is an operator-supplied, verified
Hyperliquid-native 283-day archive. When it lands, the pipeline must run
immediately, with no code archaeology. This script proves the pipeline is wired
end-to-end *today* by executing the exact command sequence against a
synthetic-but-clearly-labelled dry-run fixture (repo-local temp dir), asserting
the fail-closed labels, and recording the operator command sequence with
placeholders.

It does NOT fabricate market data, does NOT relabel anything as evidence, and
never writes into the canonical artifact stems. Fixture outputs are hashed,
recorded, then deleted.

Steps
  A. Environment + runbook script/flag verification (fail-closed).
  B. Synthetic fixture: fetch -> derive universe -> real campaign (partial
     NOT_EVIDENCE mode) -> exploratory next-open -> episode clustering import.
  C. Assert every produced artifact carries performance_evidence=false /
     fabricated_data=false and a NOT_EVIDENCE-style research status.
  D. Emit research_state/full_window_dry_run_readiness_<TS>.json with the exact
     operator command sequence and per-step PASS/FAIL.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

STATE = REPO / "research_state"
SCRIPTS = REPO / "scripts"
PYTHON = sys.executable

LABEL = "NOT_EVIDENCE_DRY_RUN_READINESS"
CAVEAT = (
    "Readiness/wiring proof only. A synthetic, clearly-labelled fixture is used to "
    "prove the pipeline executes end-to-end; it is NOT market data and NOT evidence. "
    "No canonical artifact is written or overwritten. The placeholder parquet remains "
    "NEVER evidence."
)

RUNBOOK_SCRIPTS: Dict[str, List[str]] = {
    "fetch_hyperliquid_candles.py": ["--source", "--input-archive", "--symbols", "--start", "--end", "--cache-dir"],
    "derive_verified_universe.py": ["--manifest", "--cache-dir", "--output"],
    "run_real_campaign.py": ["--manifest", "--cache-dir", "--universe-file", "--output-prefix", "--apply-vault-fees"],
    "run_hyperliquid_exploratory_next_open.py": ["--cache-dir", "--manifest", "--output-prefix"],
    "run_portfolio_placebo_hyperliquid_exploratory.py": ["--cache-dir", "--out"],
    "build_crash_event_census.py": ["--manifest", "--cache-dir", "--universe-file", "--output-prefix"],
    "run_episode_edge_okx.py": ["--out", "--draws", "--seed"],
    "audit_spec_divergence_closure.py": [],
}

FIXTURE_START = "2025-01-01T00:00:00+00:00"
FIXTURE_BARS = 120


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: List[str], timeout: int = 900) -> Tuple[int, str, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO)
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO), env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def make_fixture_candles(base: float, volume: float, crash_at: int, drop: float = 0.30) -> List[Dict[str, Any]]:
    """Non-flat, varied synthetic candles (the flat-series guard must not trip)."""
    out: List[Dict[str, Any]] = []
    start_ms = 1735689600000  # 2025-01-01T00:00:00Z
    for i in range(FIXTURE_BARS):
        close = base * (1.0 + 0.0005 * i)
        if i >= crash_at:
            close = base * (1.0 + 0.0005 * crash_at) * (1.0 - drop) * (1.0 + 0.005 * (i - crash_at))
        out.append({
            "timestamp": f"2025-01-{(i // 24) + 1:02d}T{i % 24:02d}:00:00+00:00",
            "timestamp_ms": start_ms + i * 3_600_000,
            "open": close,
            "high": close * 1.01,
            "low": close * 0.99,
            "close": close,
            "volume": volume * (1.0 + 0.05 * (i % 3)),
        })
    return out


def verify_scripts() -> Tuple[bool, Dict[str, Any]]:
    checks: Dict[str, Any] = {}
    ok = True
    for script, flags in RUNBOOK_SCRIPTS.items():
        path = SCRIPTS / script
        if not path.exists():
            checks[script] = {"exists": False}
            ok = False
            continue
        source = path.read_text()
        supports_help = "argparse" in source or "ArgumentParser" in source
        if supports_help:
            rc, out, err = run([PYTHON, str(path), "--help"], timeout=120)
            text = out + err
            present = {f: (f in text) for f in flags} if flags else {}
            script_ok = rc == 0 and all(present.values())
            detail = {"help_exit": rc, "flags_present": present}
        else:
            # Some audit scripts have no CLI; executing --help would run their
            # main() and create a side-effect artifact. Verify existence/hash only.
            present = {f: False for f in flags} if flags else {}
            script_ok = not flags
            detail = {"help_exit": None, "flags_present": present,
                      "note": "no CLI; existence/hash check only"}
        checks[script] = {
            "exists": True,
            "sha256": sha256_file(path),
            **detail,
            "ok": script_ok,
        }
        ok = ok and script_ok
    return ok, checks


def assert_not_evidence(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text())
    facts = {
        "artifact": str(path.relative_to(REPO)),
        "sha256": sha256_file(path),
        "performance_evidence": data.get("performance_evidence"),
        "fabricated_data": data.get("fabricated_data"),
        "research_status": data.get("research_status") or data.get("label"),
    }
    facts["ok"] = (
        facts["performance_evidence"] is False
        and facts["fabricated_data"] is False
        and facts["research_status"] is not None
    )
    return facts


def main() -> int:
    ts_compact = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    ts_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    steps: List[Dict[str, Any]] = []
    overall = True

    def record(name: str, ok: bool, detail: Dict[str, Any]) -> None:
        nonlocal overall
        overall = overall and ok
        steps.append({"step": name, "ok": bool(ok), **detail})

    # --- A. environment + runbook scripts ---
    rc, out, err = run([PYTHON, "-c", "import pytest,numpy,pandas,requests,pyarrow;print('env_ok')"], timeout=120)
    record("env", rc == 0 and "env_ok" in out, {"exit": rc, "stdout_tail": out.strip()[-200:]})

    scripts_ok, script_checks = verify_scripts()
    record("runbook_scripts_and_flags", scripts_ok, {"scripts": script_checks})

    # --- B. synthetic fixture pipeline ---
    td = tempfile.TemporaryDirectory(dir=str(REPO), prefix=".dryrun_fixture_")
    root = Path(td.name)
    produced: List[Path] = []
    try:
        archive = root / "archive"
        archive.mkdir(parents=True)
        fixture = {
            "AAA": make_fixture_candles(100.0, 100_000.0, 40),
            "BBB": make_fixture_candles(50.0, 100_000.0, 55),
            "ETH": make_fixture_candles(2000.0, 5_000.0, 70),
        }
        for sym, candles in fixture.items():
            (archive / f"{sym}.json").write_text(json.dumps(candles))
        cache = root / "cache"
        uni = root / "universe.json"
        end = f"2025-01-{(FIXTURE_BARS - 1) // 24 + 1:02d}T{(FIXTURE_BARS - 1) % 24:02d}:00:00+00:00"

        rc, out, err = run([
            PYTHON, str(SCRIPTS / "fetch_hyperliquid_candles.py"),
            "--source", "archive", "--input-archive", str(archive),
            "--symbols", "AAA", "BBB", "ETH",
            "--start", FIXTURE_START, "--end", end,
            "--cache-dir", str(cache), "--allow-partial",
        ])
        manifest = cache / "provenance.json"
        record("fixture_fetch_provenance", rc == 0 and manifest.exists(),
               {"exit": rc, "manifest": str(manifest.relative_to(REPO)) if manifest.exists() else None,
                "stderr_tail": err.strip()[-300:]})

        rc, out, err = run([
            PYTHON, str(SCRIPTS / "derive_verified_universe.py"),
            "--manifest", str(manifest), "--cache-dir", str(cache), "--output", str(uni),
        ])
        universe_ok = rc == 0 and uni.exists()
        if universe_ok:
            u = json.loads(uni.read_text())
            universe_ok = bool(u.get("selected_symbols"))
        record("fixture_derive_universe", universe_ok, {"exit": rc, "stderr_tail": err.strip()[-300:]})

        campaign_prefix = f"dryrun_fixture_campaign_{ts_compact}"
        rc, out, err = run([
            PYTHON, str(SCRIPTS / "run_real_campaign.py"),
            "--manifest", str(manifest), "--cache-dir", str(cache),
            "--universe-file", str(uni),
            "--output-prefix", campaign_prefix,
            "--allow-partial-not-evidence",
            "--window-start", FIXTURE_START, "--window-end", end,
        ])
        campaign_json = STATE / f"{campaign_prefix}.json"
        produced.append(campaign_json)
        record("fixture_campaign_partial_not_evidence",
               rc == 0 and campaign_json.exists(),
               {"exit": rc, "stdout_tail": out.strip()[-300:], "stderr_tail": err.strip()[-300:]})

        expl_prefix = f"dryrun_fixture_exploratory_{ts_compact}"
        expl_out = root / "out"
        expl_out.mkdir(parents=True, exist_ok=True)
        latest = STATE / "hyperliquid_exploratory_next_open_latest.json"
        latest_before = sha256_file(latest) if latest.exists() else None
        rc, out, err = run([
            PYTHON, str(SCRIPTS / "run_hyperliquid_exploratory_next_open.py"),
            "--cache-dir", str(cache),
            "--out-dir", str(expl_out),
            "--output-prefix", expl_prefix, "--skip-funnel",
        ])
        expl_json = expl_out / f"{expl_prefix}.json"
        produced.append(expl_json)
        latest_after = sha256_file(latest) if latest.exists() else None
        record("fixture_exploratory_next_open", rc == 0 and expl_json.exists(),
               {"exit": rc, "stdout_tail": out.strip()[-300:], "stderr_tail": err.strip()[-300:]})
        record("fixture_canonical_latest_untouched", latest_before is not None and latest_before == latest_after,
               {"sha256_before": latest_before, "sha256_after": latest_after})

        # Episode-aware audit wiring: clustering must import and run on fixture events.
        try:
            from scripts.run_episode_edge_okx import cluster_episodes  # noqa: WPS433
            times = {("AAA", 40): "2025-01-02T16:00:00Z", ("BBB", 55): "2025-01-03T07:00:00Z"}
            episodes = cluster_episodes([("AAA", 40), ("BBB", 55)], times, 98.0)
            ep_ok = len(episodes) >= 1 and "episode_id" in episodes[0]
            ep_detail = {"episodes": len(episodes)}
        except Exception as exc:  # noqa: BLE001
            ep_ok, ep_detail = False, {"error": f"{type(exc).__name__}: {exc}"}
        record("episode_audit_wiring", ep_ok, ep_detail)

        # --- C. labels ---
        label_facts = []
        for p in produced:
            if p.exists():
                label_facts.append(assert_not_evidence(p))
        labels_ok = bool(label_facts) and all(f["ok"] for f in label_facts)
        record("fixture_artifacts_not_evidence", labels_ok, {"artifacts": label_facts})

        fixture_pipeline_ok = all(s["ok"] for s in steps if s["step"].startswith("fixture") or s["step"] == "episode_audit_wiring")
    finally:
        # Recorded-then-removed: fixture outputs never persist as artifacts.
        for p in produced:
            for cand in (p, Path(str(p) + ".csv"), Path(str(p).replace(".json", "_metrics.json")),
                         Path(str(p).replace(".json", "_metrics.csv"))):
                if cand.exists():
                    cand.unlink()
        shutil.rmtree(root, ignore_errors=True)

    fixture_pipeline_ok = all(s["ok"] for s in steps if s["step"].startswith("fixture") or s["step"] == "episode_audit_wiring")
    record("fixture_outputs_removed", not any(STATE.glob("dryrun_fixture_*")),
           {"remaining": [p.name for p in STATE.glob("dryrun_fixture_*")]})

    operator_sequence = [
        "test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh",
        "# 1. operator: place verified archive at research_state/archives/hyperliquid_1h_full_20251220_20260928/ with SOURCE.md",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source archive "
        "--input-archive research_state/archives/hyperliquid_1h_full_20251220_20260928 "
        "--symbols <VERIFIED_SYMBOLS> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z "
        "--cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_verified_universe.py "
        "--manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json "
        "--cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 "
        "--output research_state/universe_hyperliquid_full_verified.json",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py "
        "--manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json "
        "--cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 "
        "--universe-file research_state/universe_hyperliquid_full_verified.json "
        "--output-prefix campaign_results_real_hyperliquid_full --apply-vault-fees",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_hyperliquid_exploratory.py "
        "--cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_crash_event_census.py "
        "--manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json "
        "--cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 "
        "--universe-file research_state/universe_hyperliquid_full_verified.json "
        "--campaign research_state/campaign_results_real_hyperliquid_full.json "
        "--output-prefix crash_event_census_hyperliquid_full",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py",
        "PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py",
    ]

    artifact = {
        "schema_version": 1,
        "generated_at_utc": ts_iso,
        "run_type": "full_window_dry_run_readiness",
        "label": LABEL,
        "performance_evidence": False,
        "provenance_caveat": CAVEAT,
        "fixture": {
            "kind": "synthetic_dry_run_fixture",
            "is_market_data": False,
            "is_evidence": False,
            "bars_per_symbol": FIXTURE_BARS,
            "window": [FIXTURE_START, "2025-01-05T23:00:00+00:00"],
            "symbols": ["AAA", "BBB", "ETH"],
        },
        "steps": steps,
        "operator_command_sequence": operator_sequence,
        "full_archive_present": (STATE / "archives" / "hyperliquid_1h_full_20251220_20260928").exists(),
        "pipeline_wired_end_to_end": bool(fixture_pipeline_ok and scripts_ok),
        "verdict": "READY" if (overall and fixture_pipeline_ok and scripts_ok) else "NOT_READY",
    }

    out = STATE / f"full_window_dry_run_readiness_{ts_compact}.json"
    out.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"wrote {out}")
    for s in steps:
        print(f"[{'PASS' if s['ok'] else 'FAIL'}] {s['step']}")
    print(f"pipeline_wired_end_to_end={artifact['pipeline_wired_end_to_end']} verdict={artifact['verdict']}")
    return 0 if artifact["verdict"] == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())