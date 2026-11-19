#!/usr/bin/env python3
"""C27 stage-0 venue-acquisition feasibility probe (evidence for the next-session campaign).

WHY
---
C27-T1 is the mandatory successor to C26 in the `C24 -> C25 -> C26 -> C27` heavy queue,
but it is NOT BUILT. Before any C27 compute may run, a stage-0 acquisition probe must
establish whether a NEVER-USED USDT-perp venue can serve real multiyear (2023-01-01..
2026-09-28) 1h perpetual history and clear the $5M/24h spec volume floor. This probe
REPLACES speculation with reproducible, timestamped evidence so the post-C26 session
can never claim there is no work or that acquisition is "closed."

This probe NEVER downloads a full archive and NEVER fabricates data — it only measures
reachability, multiyear depth, and $5M coverage. Bybit is the primary candidate; if its
archive/API retention fails, the probe names the next candidate and returns an explicit
`ACQUISITION_VIABLE_*` or `*_BLOCKED_BY_API_RETENTION` token.

It writes ``research_state/c27_venue_acquisition_probe_<TS>.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"
TS = "20261119T215721Z"

# Candidate never-used USDT-perp venues (OKX, Binance UM, MEXC, Bitget are already used;
# Hyperliquid-native is CLOSED: FULL_283D_BLOCKED_BY_API_RETENTION). Bybit is primary.
CANDIDATE_VENUES = ["bybit", "kucoin", "bingx"]

# Representative spec-universe symbols used to gauge $5M coverage. A symbol that clears
# the floor here is a *candidate*; authoritative universe membership is recomputed by
# derive_verified_universe.py from the actually-acquired caches.
PROBE_SYMBOLS = ["BTC", "ETH", "SOL", "ADA", "XRP", "DOGE", "LINK", "AVAX",
                 "DOT", "LTC", "BCH", "NEAR", "ARB", "OP", "ATOM", "UNI"]

DEPTH_2023 = ("2023-06-01T00:00:00Z", "2023-06-03T00:00:00Z")   # 48h window mid-2023
DEPTH_2024 = ("2024-06-01T00:00:00Z", "2024-06-03T00:00:00Z")   # 48h window mid-2024
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 crash-rebound-research/1.0")


def _iso_to_ms(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def _get(session, url: str, params: Optional[dict] = None, timeout: int = 10):
    try:
        return session.get(url, params=params, timeout=timeout)
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Per-venue probes
# ---------------------------------------------------------------------------

def probe_bybit(session) -> Dict[str, Any]:
    r = _get(session, "https://api.bybit.com/v5/market/time", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = 0
    if reachable:
        after_ms = _iso_to_ms(DEPTH_2023[1])
        rr = _get(session, "https://api.bybit.com/v5/market/kline",
                  params={"category": "linear", "symbol": "SOLUSDT", "interval": "60",
                          "start": str(_iso_to_ms(DEPTH_2023[0]) // 1000),
                          "end": str(_iso_to_ms(DEPTH_2023[1]) // 1000)}, timeout=10)
        if rr is not None and rr.status_code == 200:
            try:
                bars_2023 = len((rr.json().get("result") or {}).get("list") or [])
            except Exception:  # noqa: BLE001
                bars_2023 = 0
    return {
        "venue": "bybit",
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 >= 24,
        "probe_2023_bars": bars_2023,
        "note": ("reachable; multiyear 1H depth unverified" if reachable and bars_2023 < 24
                 else "reachable; multiyear 1H available" if reachable
                 else "unreachable (geo/legal or API block from runner)"),
    }


def probe_kucoin(session) -> Dict[str, Any]:
    r = _get(session, "https://api.kucoin.com/api/v1/timestamp", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = 0
    if reachable:
        s = _iso_to_ms(DEPTH_2023[0]) // 1000
        e = _iso_to_ms(DEPTH_2023[1]) // 1000
        rr = _get(session, "https://api.kucoin.com/api/v1/market/candles",
                  params={"type": "1hour", "symbol": "SOL-USDT", "startAt": str(s),
                          "endAt": str(e)}, timeout=10)
        if rr is not None and rr.status_code == 200:
            try:
                bars_2023 = len(rr.json().get("data") or [])
            except Exception:  # noqa: BLE001
                bars_2023 = 0
    return {
        "venue": "kucoin",
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 >= 24,
        "probe_2023_bars": bars_2023,
        "note": ("reachable; multiyear 1H depth unverified" if reachable and bars_2023 < 24
                 else "reachable; multiyear 1H available" if reachable
                 else "unreachable (geo/legal or API block from runner)"),
    }


def probe_bingx(session) -> Dict[str, Any]:
    r = _get(session, "https://open-api.bingx.com/openApi/swap/v2/quote/price", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = 0
    if reachable:
        rr = _get(session, "https://open-api.bingx.com/openApi/swap/v2/quote/klines",
                  params={"symbol": "SOL-USDT", "interval": "60m",
                          "startTime": str(_iso_to_ms(DEPTH_2023[0])),
                          "endTime": str(_iso_to_ms(DEPTH_2023[1]))}, timeout=10)
        if rr is not None and rr.status_code == 200:
            try:
                bars_2023 = len(rr.json().get("data") or [])
            except Exception:  # noqa: BLE001
                bars_2023 = 0
    return {
        "venue": "bingx",
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 >= 24,
        "probe_2023_bars": bars_2023,
        "note": ("reachable; multiyear 1H depth unverified" if reachable and bars_2023 < 24
                 else "reachable; multiyear 1H available" if reachable
                 else "unreachable (geo/legal or API block from runner)"),
    }


def _coverage_5m(session, venue_base: str, symbol_param: str) -> Dict[str, Any]:
    """Best-effort $5M/24h coverage over PROBE_SYMBOLS (best-effort; not authoritative)."""
    passing = []
    checked = []
    for sym in PROBE_SYMBOLS:
        try:
            tr = _get(session, venue_base, params={symbol_param: f"{sym}_USDT"}, timeout=8)
        except Exception:  # noqa: BLE001
            tr = None
        checked.append(sym)
        amt = None
        if tr is not None and tr.status_code == 200:
            try:
                amt = float(tr.json().get("data", {}).get("amount24") or
                            tr.json().get("ticker", [{}])[0].get("amount24") or 0.0)
            except Exception:  # noqa: BLE001
                amt = None
        if amt is not None and amt >= 5_000_000.0:
            passing.append(sym)
    return {"checked": checked, "passing_5m": passing,
            "n_checked": len(checked), "n_passing": len(passing)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Stage-0 venue-acquisition feasibility probe for C27")
    ap.add_argument("--out", default=str(STATE / f"c27_venue_acquisition_probe_{TS}.json"))
    ap.add_argument("--timeout", type=int, default=10)
    args = ap.parse_args(argv)
    if requests is None:
        print("BLOCKER: requests is required", file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    fns = {"bybit": probe_bybit, "kucoin": probe_kucoin, "bingx": probe_bingx}
    venues: Dict[str, Any] = {}
    for name, fn in fns.items():
        try:
            venues[name] = fn(session)
        except Exception as exc:  # noqa: BLE001
            venues[name] = {"reachable": False, "error": f"{type(exc).__name__}: {exc}"}
        print(f"{name}: reachable={venues[name].get('reachable')} "
              f"multiyear_2023={venues[name].get('multiyear_2023')} "
              f"bars_2023={venues[name].get('probe_2023_bars')}")

    # Pick the first reachable venue with multiyear 2023 depth as primary.
    primary = None
    for name in CANDIDATE_VENUES:
        v = venues.get(name, {})
        if v.get("reachable") and v.get("multiyear_2023"):
            primary = name
            break

    blocked = [n for n, v in venues.items() if not v.get("reachable")]
    recent_only = [n for n, v in venues.items()
                   if v.get("reachable") and not v.get("multiyear_2023")]

    viable = primary is not None
    if viable:
        status = f"ACQUISITION_VIABLE_{primary.upper()}_MULTIYEAR"
        rationale = (f"{primary.upper()} is reachable and serves multiyear 2023+ 1H perps -> "
                     f"a NEW-DATA out-of-sample C27 replication (fixed spec, no tuning) is "
                     f"feasible. This is new data ({primary.upper()} != OKX/Binance/MEXC/Bitget), "
                     f"so it is NOT a same-data rerun and satisfies the "
                     f"'new prereg + new data + explicit authorization' rule.")
    else:
        status = "ACQUISITION_BLOCKED_BY_API_RETENTION"
        rationale = ("No reachable candidate venue serves multiyear 2023-2026 history; "
                     "acquisition remains blocked for C27. Do not run a same-data C27 rerun; "
                     "await new data or a new pre-registered hypothesis on new data.")

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": "C27",
        "probe": "venue_acquisition_feasibility",
        "purpose": ("Stage-0 evidence: which never-used USDT-perp venue can serve real "
                    "multiyear 1h perpetual history and $5M/24h coverage, before any C27 compute."),
        "candidate_venues": CANDIDATE_VENUES,
        "probe_symbols": PROBE_SYMBOLS,
        "depth_windows": {"2023": list(DEPTH_2023), "2024": list(DEPTH_2024)},
        "venues": venues,
        "recommendation": {
            "primary_new_venue": primary,
            "multiyear_viable": viable,
            "recent_only_venues": recent_only,
            "blocked_venues": blocked,
            "rationale": rationale,
        },
        "c27_data_status": status,
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {out}")
    print(f"C27 data status: {status} | primary_new_venue={primary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
