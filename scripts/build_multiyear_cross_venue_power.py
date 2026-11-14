#!/usr/bin/env python3
"""C6-T2 — multi-year cross-venue power reassessment from the crash census.

Reads the real OKX multi-year crash census and computes the dependence-aware
episode structure (98h single-linkage, the spec's own holding horizon) for:
  - all RSI(21) < 20 crash events
  - volume-gate-passing events
  - signal-gate-passing events

It then checks the C4-T2 binding power floor (>= 10 independent crash episodes
plus >= 10 distinct crash days) and writes a machine-checkable JSON/MD artifact.

This is CROSS-VENUE evidence only.  It is never Hyperliquid performance
evidence and never a substitute for the operator archive.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
EPISODE_LINK_HOURS = 98.0
POWER_EPISODE_FLOOR = 10
POWER_DAY_FLOOR = 10
MIN_DAYS_FOR_80P = 1013.2


def parse_utc(text: str) -> dt.datetime:
    return dt.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


def cluster_episodes(events: List[Dict[str, Any]], link_hours: float = EPISODE_LINK_HOURS):
    parsed = sorted(((parse_utc(str(e["bar_timestamp_utc"])), e) for e in events), key=lambda x: x[0])
    episodes: List[List[Dict[str, Any]]] = []
    current: List[Dict[str, Any]] = []
    anchor = None
    for moment, event in parsed:
        if anchor is None or (moment - anchor).total_seconds() / 3600.0 <= link_hours:
            current.append(event)
            if anchor is None:
                anchor = moment
        else:
            episodes.append(current)
            current = [event]
            anchor = moment
    if current:
        episodes.append(current)
    return episodes


def summarize(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    episodes = cluster_episodes(events)
    days = sorted({str(e["bar_timestamp_utc"])[:10] for e in events})
    sizes = sorted((len(e) for e in episodes), reverse=True)
    return {
        "events": len(events),
        "episodes": len(episodes),
        "distinct_crash_days": len(days),
        "first_event_utc": min((str(e["bar_timestamp_utc"]) for e in events), default=None),
        "last_event_utc": max((str(e["bar_timestamp_utc"]) for e in events), default=None),
        "largest_episode_events": sizes[0] if sizes else 0,
        "largest_episode_share": (sizes[0] / len(events)) if events and sizes else 0.0,
        "episode_size_histogram": {str(k): sizes.count(k) for k in sorted(set(sizes))},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Multi-year cross-venue power reassessment (C6-T2)")
    ap.add_argument("--census", default="research_state/crash_event_census_real_okx_multiyear.json")
    ap.add_argument("--out", default="research_state/multiyear_cross_venue_power")
    args = ap.parse_args(argv)

    census_path = REPO_ROOT / args.census
    if not census_path.exists():
        print(f"BLOCKER: census not found: {census_path}", file=sys.stderr)
        return 2
    census = json.loads(census_path.read_text())
    events = census.get("events") or []
    if not events:
        print("BLOCKER: census has no events", file=sys.stderr)
        return 2

    by_all = summarize(events)
    by_volume = summarize([e for e in events if e.get("volume_gate_pass")])
    by_signal = summarize([e for e in events if e.get("signal_gate_pass")])

    window = census.get("window") or {}
    days_observed = None
    try:
        days_observed = (parse_utc(window["end"]) - parse_utc(window["start"])).total_seconds() / 86400.0
    except Exception:
        pass

    powered = (
        by_signal["episodes"] >= POWER_EPISODE_FLOOR
        and by_signal["distinct_crash_days"] >= POWER_DAY_FLOOR
    )
    verdict = (
        "CROSS_VENUE_POWERED_OBSERVED"
        if powered
        else "CROSS_VENUE_UNDERPOWERED_OBSERVED"
    )

    payload = {
        "schema_version": 1,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_type": "multiyear_cross_venue_power_reassessment",
        "provenance_caveat": (
            "Real OKX exchange data, non-synthetic; CROSS-VENUE. NOT Hyperliquid performance evidence."
        ),
        "inputs": {
            "census": str(census_path.relative_to(REPO_ROOT)),
            "census_sha256": __import__("hashlib").sha256(census_path.read_bytes()).hexdigest(),
            "census_generated_at_utc": census.get("generated_at_utc"),
            "universe_size": census.get("universe_size"),
            "window": window,
        },
        "method": {
            "episode_link_hours": EPISODE_LINK_HOURS,
            "episode_rule": "single-linkage on crash-bar time; spec holding horizon",
            "power_floor_episodes": POWER_EPISODE_FLOOR,
            "power_floor_distinct_days": POWER_DAY_FLOOR,
            "min_days_for_80pct_power": MIN_DAYS_FOR_80P,
        },
        "observed": {
            "all_events": by_all,
            "volume_gate_pass": by_volume,
            "signal_gate_pass": by_signal,
            "days_observed": days_observed,
        },
        "checks": {
            "signal_episodes_ge_10": by_signal["episodes"] >= POWER_EPISODE_FLOOR,
            "signal_distinct_days_ge_10": by_signal["distinct_crash_days"] >= POWER_DAY_FLOOR,
            "days_observed_ge_1013": (days_observed or 0) >= MIN_DAYS_FOR_80P,
            "largest_episode_share_below_0.5": by_signal["largest_episode_share"] < 0.5,
        },
        "verdict": verdict,
        "is_hyperliquid_evidence": False,
        "cross_venue": True,
    }
    payload["powered"] = powered

    out_json = REPO_ROOT / f"{args.out}.json"
    out_md = REPO_ROOT / f"{args.out}.md"
    out_json.write_text(json.dumps(payload, indent=2) + "\n")

    lines = [
        f"# Multi-Year Cross-Venue Power Reassessment (C6-T2)",
        "",
        f"**Generated (UTC):** {payload['generated_at_utc']}",
        f"**Verdict:** `{verdict}`",
        "**Venue basis:** OKX public REST v5 history-candles. **NOT Hyperliquid evidence.**",
        "",
        "## Observed",
        "",
        "| Slice | Events | Episodes | Distinct crash days | Largest episode share |",
        "|---|---:|---:|---:|---:|",
        f"| All RSI<20 | {by_all['events']} | {by_all['episodes']} | {by_all['distinct_crash_days']} | {by_all['largest_episode_share']:.3f} |",
        f"| Volume-gate pass | {by_volume['events']} | {by_volume['episodes']} | {by_volume['distinct_crash_days']} | {by_volume['largest_episode_share']:.3f} |",
        f"| Signal-gate pass | {by_signal['events']} | {by_signal['episodes']} | {by_signal['distinct_crash_days']} | {by_signal['largest_episode_share']:.3f} |",
        "",
        "## Power-floor checks",
        "",
        f"- Signal-gate episodes >= {POWER_EPISODE_FLOOR}: **{payload['checks']['signal_episodes_ge_10']}** ({by_signal['episodes']})",
        f"- Signal-gate distinct crash days >= {POWER_DAY_FLOOR}: **{payload['checks']['signal_distinct_days_ge_10']}** ({by_signal['distinct_crash_days']})",
        f"- Observed days >= {MIN_DAYS_FOR_80P}: **{payload['checks']['days_observed_ge_1013']}** ({days_observed})",
        f"- Largest episode share < 0.5: **{payload['checks']['largest_episode_share_below_0.5']}** ({by_signal['largest_episode_share']:.3f})",
        "",
        "This artifact removes the *sample-size* bottleneck for the cross-venue track. It does "
        "not promote OKX to Hyperliquid evidence and does not by itself establish profitability; "
        "the campaign PnL, episode-block bootstrap, crash-day permutation and portfolio placebo "
        "must still be run on this multi-year cache.",
        "",
    ]
    out_md.write_text("\n".join(lines) + "\n")
    print(f"verdict: {verdict}")
    print(
        f"signal events={by_signal['events']} episodes={by_signal['episodes']} "
        f"days={by_signal['distinct_crash_days']} largest_share={by_signal['largest_episode_share']:.3f}"
    )
    print(f"wrote {out_json.relative_to(REPO_ROOT)} and {out_md.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())