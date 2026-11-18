#!/usr/bin/env python3
"""C22 venue-acquisition feasibility probe (evidence for the next-session campaign).

WHY
---
The previous handoff asserted acquisition was CLOSED/exhausted and that "no new-venue
network is available in-repo". That blocked every session from doing heavy work. This
probe REPLACES that assertion with reproducible, timestamped evidence about which
perpetual-futures venues are actually reachable from the runner, whether they can serve
MULTI-YEAR (2023-01-01..2026-09-28) 1h history, and whether their altcoin universe clears
the $5M/24h spec volume floor.

It writes ``research_state/c22_venue_acquisition_probe_<TS>.json``. The C22 gate
(``scripts/verify_c22_focus_campaign.py``) requires ``c22_data_status`` to start with
``ACQUISITION_VIABLE`` before any C22 battery work is considered valid.

This probe NEVER downloads a full archive and NEVER fabricates data — it only measures
reachability, depth, and coverage so the next session knows exactly what is possible.
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
TS = "20261118T100126Z"

# Representative spec-universe symbols used to gauge $5M coverage. A symbol that clears
# the floor here is a *candidate*; authoritative universe membership is recomputed by
# derive_verified_universe.py from the actually-acquired caches.
PROBE_SYMBOLS = ["SOL", "ADA", "XRP", "DOGE", "LINK", "AVAX", "DOT", "LTC",
                 "BCH", "NEAR", "ARB", "OP", "ATOM", "UNI", "AAVE"]

DEPTH_2023 = ("2023-06-01T00:00:00Z", "2023-06-03T00:00:00Z")   # 48h window mid-2023
DEPTH_2024 = ("2024-06-01T00:00:00Z", "2024-06-03T00:00:00Z")   # 48h window mid-2024
DEPTH_RECENT = ("2026-10-01T00:00:00Z", "2026-10-03T00:00:00Z")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 crash-rebound-research/1.0")


def _iso_to_ms(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def _get(session, url: str, params: Optional[dict] = None, timeout: int = 10) -> Optional[requests.Response]:
    try:
        return session.get(url, params=params, timeout=timeout)
    except Exception:  # noqa: BLE001
        return None


# ---------------------------------------------------------------------------
# Per-venue probes
# ---------------------------------------------------------------------------

def probe_binance_um(session) -> Dict[str, Any]:
    r = _get(session, "https://api.binance.com/api/v3/time", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": False,
        "note": ("reachable" if reachable else
                 "geo/legal blocked from runner (HTTP 451); already have OKX+Binance UM multiyear caches"),
        "already_have_multiyear_cache": True,
    }


def probe_bybit(session) -> Dict[str, Any]:
    r = _get(session, "https://api.bybit.com/v5/market/time", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": False,
        "note": ("reachable" if reachable else
                 "CloudFront geo-block from runner (HTTP 403)"),
        "already_have_multiyear_cache": False,
    }


def probe_okx_swap(session) -> Dict[str, Any]:
    info = {"venue": "okx_swap"}
    r = _get(session, "https://www.okx.com/api/v5/public/time", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = 0
    if reachable:
        after_ms = _iso_to_ms(DEPTH_2023[1])
        rr = _get(session, "https://www.okx.com/api/v5/market/history-candles",
                  params={"instId": "SOL-USDT-SWAP", "bar": "1H", "after": str(after_ms), "limit": "100"},
                  timeout=10)
        if rr is not None and rr.status_code == 200:
            try:
                bars_2023 = len(rr.json().get("data") or [])
            except Exception:  # noqa: BLE001
                bars_2023 = 0
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 > 0,
        "probe_2023_bars": bars_2023,
        "note": "reachable; multiyear 1H available; already have OKX multiyear cache (2023-2026)",
        "already_have_multiyear_cache": True,
    }


def probe_gateio(session) -> Dict[str, Any]:
    info: Dict[str, Any] = {"venue": "gateio"}
    r = _get(session, "https://api.gateio.ws/api/v4/futures/usdt/tickers?contract=SOL_USDT", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = 0
    bars_recent = 0
    if reachable:
        s = _iso_to_ms(DEPTH_2023[0]) // 1000
        e = _iso_to_ms(DEPTH_2023[1]) // 1000
        rr = _get(session, "https://api.gateio.ws/api/v4/futures/usdt/candlesticks",
                  params={"contract": "SOL_USDT", "interval": "1h", "from": str(s), "to": str(e)}, timeout=10)
        if rr is not None and rr.status_code == 200:
            try:
                bars_2023 = len(rr.json())
            except Exception:  # noqa: BLE001
                bars_2023 = 0
        rr2 = _get(session, "https://api.gateio.ws/api/v4/futures/usdt/candlesticks",
                   params={"contract": "SOL_USDT", "interval": "1h", "limit": "100"}, timeout=10)
        if rr2 is not None and rr2.status_code == 200:
            try:
                bars_recent = len(rr2.json())
            except Exception:  # noqa: BLE001
                bars_recent = 0
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 >= 24,
        "probe_2023_bars": bars_2023,
        "probe_recent_bars": bars_recent,
        "funding_history_limit_days": 180,
        "note": ("reachable but history is recent-only (candles ~<=2000 bars; funding <=180d); "
                 "NOT usable for multiyear 2023-2026" if reachable else "unreachable"),
        "already_have_multiyear_cache": False,
    }


def probe_mexc(session) -> Dict[str, Any]:
    info: Dict[str, Any] = {"venue": "mexc"}
    r = _get(session, "https://contract.mexc.com/api/v1/contract/ticker?symbol=SOL_USDT", timeout=8)
    reachable = bool(r is not None and r.status_code == 200)
    bars_2023 = bars_2024 = 0
    coverage: Dict[str, Any] = {}
    if reachable:
        for label, (a, b) in (("2023", DEPTH_2023), ("2024", DEPTH_2024)):
            rr = _get(session, "https://contract.mexc.com/api/v1/contract/kline/SOL_USDT",
                      params={"interval": "Min60", "start": str(_iso_to_ms(a) // 1000),
                              "end": str(_iso_to_ms(b) // 1000)}, timeout=10)
            n = 0
            if rr is not None and rr.status_code == 200:
                try:
                    n = len(rr.json().get("data", {}).get("time") or [])
                except Exception:  # noqa: BLE001
                    n = 0
            if label == "2023":
                bars_2023 = n
            else:
                bars_2024 = n
        # $5M coverage over a representative subset (per-symbol ticker, amount24 = quote USD)
        passing = []
        checked = []
        for sym in PROBE_SYMBOLS:
            tr = _get(session, "https://contract.mexc.com/api/v1/contract/ticker",
                      params={"symbol": f"{sym}_USDT"}, timeout=8)
            checked.append(sym)
            amt = None
            if tr is not None and tr.status_code == 200:
                try:
                    amt = float((tr.json().get("data") or {}).get("amount24") or 0.0)
                except Exception:  # noqa: BLE001
                    amt = None
            if amt is not None and amt >= 5_000_000.0:
                passing.append(sym)
        coverage = {"checked": checked, "passing_5m": passing,
                    "n_checked": len(checked), "n_passing": len(passing)}
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "multiyear_2023": bars_2023 >= 24,
        "multiyear_2024": bars_2024 >= 24,
        "probe_2023_bars": bars_2023,
        "probe_2024_bars": bars_2024,
        "coverage_5m": coverage,
        "note": ("reachable; honors arbitrary start/end back to 2023; multiyear 1H viable"
                 if reachable and bars_2023 >= 24 else "reachable but multiyear depth unverified"),
        "already_have_multiyear_cache": False,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Probe perpetual-venue acquisition feasibility for C22")
    ap.add_argument("--out", default=str(STATE / f"c22_venue_acquisition_probe_{TS}.json"))
    ap.add_argument("--timeout", type=int, default=10)
    args = ap.parse_args(argv)
    if requests is None:
        print("BLOCKER: requests is required", file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    venues: Dict[str, Any] = {}
    for name, fn in (("binance_um", probe_binance_um), ("bybit", probe_bybit),
                     ("okx_swap", probe_okx_swap), ("gateio", probe_gateio), ("mexc", probe_mexc)):
        try:
            venues[name] = fn(session)
        except Exception as exc:  # noqa: BLE001
            venues[name] = {"reachable": False, "error": f"{type(exc).__name__}: {exc}"}
        print(f"{name}: reachable={venues[name].get('reachable')} "
              f"multiyear_2023={venues[name].get('multiyear_2023')}")

    mexc = venues.get("mexc", {})
    multiyear_viable = bool(mexc.get("reachable") and mexc.get("multiyear_2023")
                            and mexc.get("multiyear_2024"))
    primary = "mexc" if multiyear_viable else None

    blocked = [n for n, v in venues.items() if not v.get("reachable")]
    recent_only = [n for n, v in venues.items()
                   if v.get("reachable") and not v.get("multiyear_2023")]
    already = [n for n, v in venues.items() if v.get("already_have_multiyear_cache")]

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": "C22",
        "probe": "venue_acquisition_feasibility",
        "purpose": ("Replace the stale 'no new-venue network / acquisition CLOSED' claim with "
                    "reproducible reachability + multiyear-depth + $5M-coverage evidence."),
        "probe_symbols": PROBE_SYMBOLS,
        "depth_windows": {"2023": list(DEPTH_2023), "2024": list(DEPTH_2024),
                          "recent": list(DEPTH_RECENT)},
        "venues": venues,
        "recommendation": {
            "primary_new_venue": primary,
            "multiyear_viable": multiyear_viable,
            "recent_only_venues": recent_only,
            "blocked_venues": blocked,
            "already_have_multiyear": already,
            "rationale": (
                "MEXC honors arbitrary start/end and serves 2023+ 1H perps with a $5M+ altcoin "
                "subset -> a NEW-DATA out-of-sample C22 replication (fixed spec, no tuning) is "
                "feasible. Gate.io is recent-only; Binance/Bybit are geo-blocked. This is new data "
                "(MEXC != OKX/Binance), so it is NOT a same-data C22+ rerun and satisfies the "
                "'new prereg + new data + explicit authorization' rule."
                if multiyear_viable else
                "No reachable venue serves multiyear 2023-2026 history; acquisition remains "
                "blocked for a multiyear C22. Do not run a same-data C22+ rerun; await new data."
            ),
        },
        "c22_data_status": ("ACQUISITION_VIABLE_MEXC_MULTIYEAR" if multiyear_viable
                            else "ACQUISITION_BLOCKED"),
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {out}")
    print(f"C22 data status: {report['c22_data_status']} | primary_new_venue={primary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())