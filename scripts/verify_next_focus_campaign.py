#!/usr/bin/env python3
"""C6 acceptance gate — multi-year cross-venue campaign (fail-closed).

This gate is the machine-checkable acceptance test for the next focus campaign.
It refuses to pass on planning-only turns, missing artifacts, synthetic data, or
Hyperliquid mislabelling.  It reports one line per requirement and exits 0 only
when every C6-T1/T2 artifact is present and internally consistent.

It is intentionally separate from session_gate.py: the 21-check evidence-chain
gate stays green on the retained canonical state, while this gate measures the
new multi-year cross-venue work.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"

ARCHIVE = STATE / "archives" / "okx_1h_multiyear_20230101_20260928" / "SOURCE.json"
CACHE = STATE / "cache" / "okx_1h_multiyear_20230101_20260928" / "provenance.json"
UNIVERSE = STATE / "universe_okx_multiyear_verified.json"
CENSUS = STATE / "crash_event_census_real_okx_multiyear.json"
POWER = STATE / "multiyear_cross_venue_power.json"
CAMPAIGN = STATE / "campaign_results_real_okx_multiyear.json"
HANDOFF = REPO / "HANDOFF.md"

EXPECTED_SYMBOLS = 34
EXPECTED_BARS = 32808
EXPECTED_START = "2023-01-01T00:00:00Z"
EXPECTED_END = "2026-09-28T23:00:00Z"


def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""))
    return ok


def main() -> int:
    results: List[Tuple[str, bool, str]] = []

    # 1. Archive provenance
    if ARCHIVE.exists():
        a = _load(ARCHIVE)
        syms = a.get("symbols") or {}
        complete = sum(1 for v in syms.values() if v.get("status") == "ok")
        results.append((
            "archive_34_complete",
            complete == EXPECTED_SYMBOLS and a.get("fabricated_data") is False
            and a.get("is_hyperliquid_venue_data") is False,
            f"{complete}/{EXPECTED_SYMBOLS} complete; fabricated={a.get('fabricated_data')}; hl={a.get('is_hyperliquid_venue_data')}",
        ))
    else:
        results.append(("archive_34_complete", False, f"missing {ARCHIVE}"))

    # 2. Cache manifest
    if CACHE.exists():
        m = _load(CACHE)
        syms = m.get("symbols") or {}
        complete = sum(
            1 for v in syms.values()
            if v.get("status") == "ok"
            and (v.get("coverage") or {}).get("complete_for_target_window") is True
        )
        tw = m.get("target_window") or {}
        results.append((
            "cache_34_complete_32808",
            complete == EXPECTED_SYMBOLS
            and tw.get("expected_hourly_bars") == EXPECTED_BARS
            and m.get("fabricated_data") is False,
            f"{complete}/{EXPECTED_SYMBOLS} complete; expected_bars={tw.get('expected_hourly_bars')}; fabricated={m.get('fabricated_data')}",
        ))
    else:
        results.append(("cache_34_complete_32808", False, f"missing {CACHE}"))

    # 3. Universe
    if UNIVERSE.exists():
        u = _load(UNIVERSE)
        syms = u.get("selected_symbols") or u.get("symbols") or []
        results.append(("universe_34", len(syms) == EXPECTED_SYMBOLS, f"{len(syms)} symbols"))
    else:
        results.append(("universe_34", False, f"missing {UNIVERSE}"))

    # 4. Census
    if CENSUS.exists():
        c = _load(CENSUS)
        ev = c.get("events") or []
        sig = [e for e in ev if e.get("signal_gate_pass")]
        vol = [e for e in ev if e.get("volume_gate_pass")]
        results.append((
            "census_events_and_signal_gate",
            len(ev) > 0 and len(vol) > 0 and len(sig) > 0,
            f"events={len(ev)} volume_pass={len(vol)} signal_pass={len(sig)}",
        ))
    else:
        results.append(("census_events_and_signal_gate", False, f"missing {CENSUS}"))

    # 5. Power artifact
    if POWER.exists():
        p = _load(POWER)
        obs = (p.get("observed") or {}).get("signal_gate_pass") or {}
        checks = p.get("checks") or {}
        results.append((
            "power_signal_episodes_ge_10",
            p.get("verdict") == "CROSS_VENUE_POWERED_OBSERVED"
            and checks.get("signal_episodes_ge_10") is True
            and checks.get("signal_distinct_days_ge_10") is True,
            f"verdict={p.get('verdict')} episodes={obs.get('episodes')} days={obs.get('distinct_crash_days')}",
        ))
    else:
        results.append(("power_signal_episodes_ge_10", False, f"missing {POWER}"))

    # 6. Campaign artifact
    if CAMPAIGN.exists():
        r = _load(CAMPAIGN)
        res = r.get("results") or {}
        prov = r.get("data_provenance") or {}
        results.append((
            "campaign_cross_venue_real",
            r.get("cross_venue") is True
            and r.get("is_hyperliquid_venue_data") is False
            and r.get("performance_evidence") is True
            and r.get("fabricated_data") is False
            and res.get("num_trades") is not None
            and prov.get("expected_hourly_bars") == EXPECTED_BARS,
            f"trades={res.get('num_trades')} pnl={res.get('total_pnl')} symbols={len(prov.get('symbols_loaded') or [])}",
        ))
    else:
        results.append(("campaign_cross_venue_real", False, f"missing {CAMPAIGN}"))

    # 7. Handoff references C6 and the campaign stem
    if HANDOFF.exists():
        text = HANDOFF.read_text()
        results.append((
            "handoff_references_c6",
            "C6-T1" in text and "campaign_results_real_okx_multiyear" in text,
            f"{len(text)} bytes",
        ))
    else:
        results.append(("handoff_references_c6", False, "missing HANDOFF.md"))

    ok = all(v[1] for v in results)
    print()
    if ok:
        print("C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete")
        return 0
    failed = [v[0] for v in results if not v[1]]
    print(f"C6 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())