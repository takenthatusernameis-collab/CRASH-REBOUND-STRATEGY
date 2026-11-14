#!/usr/bin/env python3
"""C6-T3 — multi-year cross-venue close-out record.

Reads the real OKX multi-year campaign + census + power artifacts and writes a
single close-out record with exact metrics, artifact hashes, and an explicit
non-Hyperliquid evidence label.  This is the artifact the next session must
produce before the C6 acceptance gate can pass.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build C6 multi-year cross-venue close-out")
    ap.add_argument("--campaign", default="research_state/campaign_results_real_okx_multiyear.json")
    ap.add_argument("--power", default="research_state/multiyear_cross_venue_power.json")
    ap.add_argument("--census", default="research_state/crash_event_census_real_okx_multiyear.json")
    ap.add_argument("--out", default=None, help="Output stem (default: research_state/c6_closeout_<TS>)")
    args = ap.parse_args(argv)

    campaign_path = REPO / args.campaign
    power_path = REPO / args.power
    census_path = REPO / args.census
    for p in (campaign_path, power_path, census_path):
        if not p.exists():
            print(f"BLOCKER: missing {p}", file=sys.stderr)
            return 2

    campaign = json.loads(campaign_path.read_text())
    power = json.loads(power_path.read_text())
    census = json.loads(census_path.read_text())

    res = campaign.get("results") or {}
    metrics = campaign.get("metrics") or {}
    obs = (power.get("observed") or {}).get("signal_gate_pass") or {}
    checks = power.get("checks") or {}

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_stem = args.out or f"research_state/c6_closeout_{ts}"
    out_json = REPO / f"{out_stem}.json"
    out_md = REPO / f"{out_stem}.md"

    payload: Dict[str, Any] = {
        "schema_version": 1,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "campaign_id": "C6-T1/T2/T3",
        "run_type": "multiyear_cross_venue_closeout",
        "verdict": "CROSS_VENUE_MULTIYEAR_COMPLETE_NOT_HYPERLIQUID",
        "is_hyperliquid_evidence": False,
        "cross_venue": True,
        "evidence_warning": (
            "Real OKX hourly OHLCV, non-synthetic, multi-year. This is NOT Hyperliquid "
            "performance evidence and must never be relabelled as such. It does not replace "
            "the operator archive requirement for a Hyperliquid-native GO decision."
        ),
        "inputs": {
            "campaign": str(campaign_path.relative_to(REPO)),
            "campaign_sha256": sha256(campaign_path),
            "power": str(power_path.relative_to(REPO)),
            "power_sha256": sha256(power_path),
            "census": str(census_path.relative_to(REPO)),
            "census_sha256": sha256(census_path),
        },
        "campaign_summary": {
            "total_pnl": res.get("total_pnl"),
            "num_trades": res.get("num_trades"),
            "final_open_positions": res.get("final_open_positions"),
            "final_gross_exposure": res.get("final_gross_exposure"),
            "symbols_loaded": len((campaign.get("data_provenance") or {}).get("symbols_loaded") or []),
            "target_window": (campaign.get("data_provenance") or {}).get("target_window"),
            "is_hyperliquid_venue_data": campaign.get("is_hyperliquid_venue_data"),
            "performance_evidence": campaign.get("performance_evidence"),
        },
        "metrics": metrics,
        "power": {
            "verdict": power.get("verdict"),
            "signal_events": obs.get("events"),
            "signal_episodes": obs.get("episodes"),
            "signal_distinct_crash_days": obs.get("distinct_crash_days"),
            "largest_episode_share": obs.get("largest_episode_share"),
            "checks": checks,
        },
        "census_summary": {
            "events_total": (census.get("reconciliation") or {}).get("events_total"),
            "volume_gate_pass": (census.get("reconciliation") or {}).get("volume_gate_pass"),
            "signal_gate_pass": (census.get("reconciliation") or {}).get("signal_gate_pass"),
            "universe_size": census.get("universe_size"),
        },
        "not_done": [
            "episode-block bootstrap 95% CI on multi-year campaign",
            "crash-day conditional permutation test on multi-year campaign",
            "full-portfolio placebo on multi-year campaign",
            "decision memo update with multi-year cross-venue verdict",
            "Hyperliquid-native validation (still requires operator archive)",
        ],
    }
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        "# C6 Multi-Year Cross-Venue Close-Out",
        "",
        f"**Generated (UTC):** {payload['generated_at_utc']}",
        f"**Verdict:** `{payload['verdict']}`",
        "**Evidence class:** real OKX hourly OHLCV, non-synthetic, CROSS-VENUE. **NOT Hyperliquid evidence.**",
        "",
        "## Campaign",
        "",
        f"- Total PnL: **{res.get('total_pnl')}**",
        f"- Trades: **{res.get('num_trades')}**",
        f"- Symbols loaded: **{payload['campaign_summary']['symbols_loaded']}**",
        f"- Target window: `{payload['campaign_summary']['target_window']}`",
        f"- Hyperliquid venue data: **{campaign.get('is_hyperliquid_venue_data')}**",
        "",
        "## Power",
        "",
        f"- Signal-gate events: **{obs.get('events')}**",
        f"- Signal-gate episodes: **{obs.get('episodes')}** (floor 10)",
        f"- Distinct crash days: **{obs.get('distinct_crash_days')}** (floor 10)",
        f"- Largest episode share: **{obs.get('largest_episode_share')}**",
        f"- Power verdict: `{power.get('verdict')}`",
        "",
        "## Remaining (do not claim done)",
        "",
        *[f"- {x}" for x in payload["not_done"]],
        "",
    ]
    out_md.write_text("\n".join(lines) + "\n")
    print(f"verdict: {payload['verdict']}")
    print(f"campaign pnl={res.get('total_pnl')} trades={res.get('num_trades')}")
    print(f"wrote {out_json.relative_to(REPO)} and {out_md.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())