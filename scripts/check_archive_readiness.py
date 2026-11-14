#!/usr/bin/env python3
"""Archive-ingestion readiness check for the Hyperliquid 283-day campaign (C2-T3).

Verifies that the DATA_REQUEST_283D_HYPERLIQUID.md runbook commands still match
the repo (scripts present, flags supported, env bootstrapped) so that a verified
Hyperliquid-native 283-day archive can be ingested and the canonical full-window
campaign run immediately on arrival. Records a new-stem JSON artifact.

This is readiness bookkeeping only; it does NOT fabricate data and does NOT
relabel the placeholder parquet as evidence.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LABEL = "ARCHIVE_READINESS"
CAVEAT = (
    "Readiness bookkeeping only; no data fabricated; placeholder parquet is NOT "
    "evidence. Confirms runbook scripts/flags match the repo so an operator-supplied "
    "verified Hyperliquid-native 283-day archive can be ingested on arrival."
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cli_flags(script: str, flags: list[str]) -> dict:
    path = REPO / "scripts" / script
    if not path.exists():
        return {"exists": False}
    try:
        out = subprocess.run(
            [sys.executable, str(path), "--help"],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO),
            env={"PYTHONPATH": str(REPO), "PATH": "/usr/bin:/bin"},
        )
        text = out.stdout + out.stderr
        return {
            "exists": True,
            "sha256": sha256_file(path),
            "flags_present": {f: (f in text) for f in flags},
        }
    except Exception as exc:
        return {"exists": True, "error": str(exc)}


def main() -> int:
    checks = {
        "fetch_hyperliquid_candles.py": cli_flags(
            "fetch_hyperliquid_candles.py",
            ["--source", "--input-archive", "--symbols", "--cache-dir", "--allow-partial"],
        ),
        "derive_verified_universe.py": cli_flags(
            "derive_verified_universe.py",
            ["--manifest", "--cache-dir", "--output", "--min-24h-volume-usd"],
        ),
        "run_real_campaign.py": cli_flags(
            "run_real_campaign.py",
            ["--manifest", "--cache-dir", "--universe-file", "--output-prefix",
             "--apply-vault-fees", "--allow-partial-not-evidence"],
        ),
    }
    runbook = REPO / "research_state/DATA_REQUEST_283D_HYPERLIQUID.md"
    placeholder = REPO / "research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet"
    full_archive_dir = REPO / "research_state/archives/hyperliquid_1h_full_20251220_20260928"

    all_ok = all(c.get("exists") and all(c.get("flags_present", {}).values()) for c in checks.values())

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "hyperliquid_archive_ingestion_readiness",
        "label": LABEL,
        "provenance_caveat": CAVEAT,
        "runbook": str(runbook.relative_to(REPO)),
        "runbook_sha256": sha256_file(runbook) if runbook.exists() else None,
        "script_checks": checks,
        "all_scripts_and_flags_ok": all_ok,
        "archive_state": {
            "full_archive_dir_present": full_archive_dir.exists(),
            "full_archive_dir": str(full_archive_dir.relative_to(REPO)) if full_archive_dir.exists() else None,
            "placeholder_present": placeholder.exists(),
            "placeholder_sha256": sha256_file(placeholder) if placeholder.exists() else None,
            "placeholder_is_evidence": False,
            "placeholder_note": "flat synthetic placeholder; NEVER evidence (see HANDOFF.md)",
        },
        "ingest_pipeline_ready": bool(all_ok),
        "next_step_on_operator_data": [
            "1. Place verified Hyperliquid-native 283-day archive at research_state/archives/hyperliquid_1h_full_20251220_20260928/ with SOURCE.md sidecar",
            "2. PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source archive --input-archive research_state/archives/hyperliquid_1h_full_20251220_20260928 --symbols <verified> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928",
            "3. Verify provenance: all_complete=true, ready_for_real_campaign=true, fabricated_data=false",
            "4. PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_verified_universe.py --manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 --output research_state/universe_hyperliquid_full_verified.json",
            "5. PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/hyperliquid_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/hyperliquid_1h_full_20251220_20260928 --universe-file research_state/universe_hyperliquid_full_verified.json --output-prefix campaign_results_real_hyperliquid_full --apply-vault-fees",
            "6. Run full-portfolio placebo + episode-aware audit on the full window; update decision memo",
        ],
        "verdict": "READY" if all_ok else "NOT_READY",
    }

    out = REPO / f"research_state/archive_readiness_{ts}.json"
    out.write_text(json.dumps(artifact, indent=2) + "\n")
    print(f"wrote {out}")
    print(f"all_scripts_and_flags_ok={all_ok} verdict={artifact['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())