#!/usr/bin/env python
"""C25 prerequisite probe: is OKX realized funding history reachable for 2023-01-01..2026-09-28?

GET https://www.okx.com/api/v5/public/funding-rate-history caps at 100 rows per
request and (verified 2026-11-19) returns only a rolling ~1 month window no matter
which cursor (before/after) is supplied. Deep history is therefore not reachable,
so okx is recorded UNAVAILABLE_FUNDING for C25 rather than zero-filled or proxied.

Writes research_state/c25_okx_funding_retention_probe_<TS>.json and prints a single
decision token:
  OKX_FUNDING_BLOCKED_BY_API_RETENTION  -> do not attempt the multiyear fetch
  OKX_FUNDING_HISTORY_REACHABLE         -> the deep fetch is viable after all
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"

API = ("https://www.okx.com/api/v5/public/funding-rate-history"
       "?instId=BTC-USDT-SWAP&limit=100")
PROBE_CURSORS_MS = [
    1704067200000,  # 2024-01-01
    1735689600000,  # 2025-01-01
    1767225600000,  # 2026-01-01
]
MIN_EXPECTED_SPAN_DAYS = 180


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_rows(cursor_ms: int, timeout: float = 20.0) -> list[dict]:
    sys.path.insert(0, str(REPO / "scripts"))
    import fetch_funding_history as ffh  # shares the venue-approved HTTP client

    url = f"{API}&before={cursor_ms}"
    payload = ffh._get_json(url, timeout=int(timeout), retries=2)
    if str(payload.get("code")) != "0":
        raise RuntimeError(f"OKX error code={payload.get('code')} msg={payload.get('msg')}")
    return payload.get("data") or []


def build_report(observations: list[dict]) -> dict:
    spans = [o["span_days"] for o in observations if o.get("rows")]
    widest = max(spans) if spans else 0.0
    newest = max((o["newest_ms"] for o in observations if o.get("rows")), default=None)
    oldest = min((o["oldest_ms"] for o in observations if o.get("rows")), default=None)
    reachable = widest >= MIN_EXPECTED_SPAN_DAYS
    token = (
        "OKX_FUNDING_HISTORY_REACHABLE" if reachable
        else "OKX_FUNDING_BLOCKED_BY_API_RETENTION"
    )
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "campaign": "C25",
        "kind": "funding_acquisition_retention_probe",
        "venue": "okx",
        "endpoint": API,
        "requested_window": {"start": "2023-01-01", "end": "2026-09-28"},
        "per_request_row_cap": 100,
        "min_expected_span_days": MIN_EXPECTED_SPAN_DAYS,
        "observations": observations,
        "widest_span_days": round(widest, 2),
        "reachable_oldest_utc": _iso(oldest) if oldest else None,
        "reachable_newest_utc": _iso(newest) if newest else None,
        "decision_token": token,
        "venue_status": "UNAVAILABLE_FUNDING" if not reachable else "FUNDING_ACQUIRED",
        "action": (
            "Do not run a multiyear OKX funding fetch; record UNAVAILABLE_FUNDING and "
            "evaluate C25 cost_taker_funding / cost_stress on binance_um, mexc and bitget "
            "only (>=3 venues), per the C25 prereg availability clause."
            if not reachable else
            "Run scripts/fetch_funding_history.py --venues okx --workers 8."
        ),
        "filled_zero_or_proxied": False,
        "provenance": {
            "real_market_data": True,
            "fabricated_data": False,
            "synthetic_data": False,
            "is_hyperliquid_venue_data": False,
        },
    }


def main() -> int:
    observations = []
    for cursor in PROBE_CURSORS_MS:
        entry: dict = {"cursor_ms": cursor, "cursor_utc": _iso(cursor)}
        try:
            recs = fetch_rows(cursor)
            ts = sorted(int(r["fundingTime"]) for r in recs)
            entry.update({
                "rows": len(ts),
                "rows_returned_after_cursor": sum(1 for t in ts if t > cursor),
                "oldest_ms": ts[0] if ts else None,
                "newest_ms": ts[-1] if ts else None,
                "span_days": round((ts[-1] - ts[0]) / 86_400_000.0, 2) if ts else 0.0,
            })
        except Exception as exc:  # network/auth failure is itself a blocker
            entry.update({"rows": 0, "error": f"{type(exc).__name__}: {exc}", "span_days": 0.0})
        observations.append(entry)

    report = build_report(observations)
    STATE.mkdir(parents=True, exist_ok=True)
    ts_tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = STATE / f"c25_okx_funding_retention_probe_{ts_tag}.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in (
        "widest_span_days", "reachable_oldest_utc", "reachable_newest_utc", "decision_token")}))
    print(f"wrote {out.relative_to(REPO)}")
    print(report["decision_token"])
    return 0 if report["decision_token"] == "OKX_FUNDING_HISTORY_REACHABLE" else 2


if __name__ == "__main__":
    sys.exit(main())
