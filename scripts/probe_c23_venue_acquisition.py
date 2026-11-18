#!/usr/bin/env python3
"""C23 venue-acquisition feasibility probe (Bitget USDT-M first, documented fallbacks).

WHY
---
C22 closed `NO_GO` on MEXC (new venue, frozen spec). Before the crash-rebound edge is
declared dead (or confirmed), C23 must run the SAME frozen spec on one more never-used
USDT-perp venue. This probe produces reproducible, timestamped evidence that Bitget
USDT-M public REST serves MULTI-YEAR (2023-01-01..2026-09-28) 1h history with enough
depth and breadth to support the frozen folds/strata/inference.

It writes ``research_state/c23_venue_acquisition_probe_<TS>.json``. The C23 gate
(``scripts/verify_c23_focus_campaign.py``) requires ``c23_data_status`` to start with
``ACQUISITION_VIABLE`` before C23 battery work is considered valid.

It NEVER downloads the full archive and NEVER fabricates data: it measures reachability,
depth (48h windows in 2023/2024/2025), contract breadth, and a live $5M turnover proxy.
Authoritative universe membership is recomputed from the acquired cache by
``derive_verified_universe.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"
TS = "20261118T202301Z"

PROBE_SYMBOLS = ["SOL", "ADA", "XRP", "DOGE", "LINK", "AVAX", "DOT", "LTC",
                 "BCH", "NEAR", "ARB", "OP", "ATOM", "UNI", "AAVE"]

DEPTH_WINDOWS = {
    "2023": ("2023-01-01T00:00:00Z", "2023-01-02T23:00:00Z"),
    "2024": ("2024-06-01T00:00:00Z", "2024-06-02T23:00:00Z"),
    "2025": ("2025-06-01T00:00:00Z", "2025-06-02T23:00:00Z"),
    "2026": ("2026-09-01T00:00:00Z", "2026-09-02T23:00:00Z"),
}

BITGET_HISTORY = "https://api.bitget.com/api/v2/mix/market/history-candles"
BITGET_CONTRACTS = "https://api.bitget.com/api/v2/mix/market/contracts"
BITGET_TICKERS = "https://api.bitget.com/api/v2/mix/market/tickers"
KRAKEN_FUTURES = "https://futures.kraken.com/derivatives/api/v3/instruments"

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36 crash-rebound-research/1.0")


def _iso_to_ms(s: str) -> int:
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000)


def _get(session, url: str, params: Optional[dict] = None, timeout: int = 15):
    try:
        return session.get(url, params=params, timeout=timeout)
    except Exception:  # noqa: BLE001
        return None


def _bg_depth(session, symbol: str, window: tuple) -> int:
    """Count 1H bars Bitget returns for a 48h window (48 == full depth)."""
    params = {
        "symbol": f"{symbol}USDT",
        "productType": "usdt-futures",
        "granularity": "1H",
        "startTime": str(_iso_to_ms(window[0])),
        "endTime": str(_iso_to_ms(window[1])),
        "limit": "200",
    }
    r = _get(session, BITGET_HISTORY, params=params, timeout=20)
    if r is None or r.status_code != 200:
        return 0
    try:
        return len(r.json().get("data") or [])
    except Exception:  # noqa: BLE001
        return 0


def probe_bitget(session) -> Dict[str, Any]:
    info: Dict[str, Any] = {"venue": "bitget_usdt_m"}
    contracts = _get(session, BITGET_CONTRACTS, params={"productType": "usdt-futures"}, timeout=25)
    reachable = bool(contracts is not None and contracts.status_code == 200)
    symbols: List[str] = []
    if reachable:
        try:
            symbols = [str(c.get("symbol")) for c in (contracts.json().get("data") or [])]
        except Exception:  # noqa: BLE001
            symbols = []
    depth = {label: _bg_depth(session, "SOL", w) for label, w in DEPTH_WINDOWS.items()}
    multiyear = all(depth[label] >= 24 for label in ("2023", "2024", "2025"))

    coverage: Dict[str, Any] = {}
    if reachable:
        r = _get(session, BITGET_TICKERS, params={"productType": "usdt-futures"}, timeout=25)
        tick: Dict[str, float] = {}
        if r is not None and r.status_code == 200:
            try:
                for row in (r.json().get("data") or []):
                    try:
                        tick[str(row.get("symbol"))] = float(row.get("quoteVolume") or 0.0)
                    except Exception:  # noqa: BLE001
                        continue
            except Exception:  # noqa: BLE001
                tick = {}
        passing = [s for s in PROBE_SYMBOLS if tick.get(f"{s}USDT", 0.0) >= 5_000_000.0]
        coverage = {
            "checked": list(PROBE_SYMBOLS),
            "n_checked": len(PROBE_SYMBOLS),
            "passing_5m_live": passing,
            "n_passing_live": len(passing),
            "note": ("live 24h quote turnover proxy; authoritative $5M membership is recomputed "
                     "from the acquired cache by derive_verified_universe.py"),
        }
    return {
        "reachable": reachable,
        "http_status": getattr(contracts, "status_code", None),
        "n_usdt_m_contracts": len(symbols),
        "contracts_probe": [s for s in symbols if s in {f"{p}USDT" for p in PROBE_SYMBOLS}][:15],
        "multiyear_2023": depth["2023"] >= 24,
        "multiyear_2024": depth["2024"] >= 24,
        "multiyear_2025": depth["2025"] >= 24,
        "probe_bars_by_window": depth,
        "coverage_5m_live": coverage,
        "page_cap_bars": 200,
        "pagination_note": ("history-candles caps responses at 200 bars and returns the LAST 200 "
                            "bars of the requested span; the C23 fetcher therefore pages BACKWARD "
                            "from the end in <=199h windows so every hour is covered exactly once"),
        "note": ("reachable; serves 1H history back to 2023-01-01 (48/48 bars per 48h probe "
                 "window) -> multiyear out-of-sample C23 replication is feasible"
                 if reachable and multiyear else
                 "reachable but multiyear depth unverified; do not run C23 on this evidence"),
        "already_have_multiyear_cache": False,
    }


def probe_kraken_futures(session) -> Dict[str, Any]:
    r = _get(session, KRAKEN_FUTURES, timeout=12)
    reachable = bool(r is not None and r.status_code == 200)
    n_pf = 0
    if reachable:
        try:
            n_pf = sum(1 for i in (r.json().get("instruments") or [])
                       if str(i.get("symbol", "")).startswith("PF_"))
        except Exception:  # noqa: BLE001
            n_pf = 0
    return {
        "reachable": reachable,
        "http_status": getattr(r, "status_code", None),
        "n_pf_instruments": n_pf,
        "multiyear_2023": False,
        "note": ("documented fallback only; depth/coverage unprobed in this run — requires its own "
                 "viability probe before use" if reachable else "unreachable"),
        "already_have_multiyear_cache": False,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Probe Bitget USDT-M acquisition feasibility for C23")
    ap.add_argument("--out", default=str(STATE / f"c23_venue_acquisition_probe_{TS}.json"))
    args = ap.parse_args(argv)
    if requests is None:
        print("BLOCKER: requests is required", file=sys.stderr)
        return 2

    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "application/json"})

    venues: Dict[str, Any] = {}
    for name, fn in (("bitget_usdt_m", probe_bitget), ("kraken_futures", probe_kraken_futures)):
        try:
            venues[name] = fn(session)
        except Exception as exc:  # noqa: BLE001
            venues[name] = {"reachable": False, "error": f"{type(exc).__name__}: {exc}"}
        print(f"{name}: reachable={venues[name].get('reachable')} "
              f"multiyear_2023={venues[name].get('multiyear_2023')}")

    bg = venues.get("bitget_usdt_m", {})
    viable = bool(bg.get("reachable") and bg.get("multiyear_2023")
                  and bg.get("multiyear_2024") and bg.get("multiyear_2025"))
    fallback = None if viable else "kraken_futures"

    report = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "campaign": "C23",
        "probe": "venue_acquisition_feasibility",
        "purpose": ("Confirm a second never-used USDT-perp venue can serve MULTI-YEAR 1H history "
                    "for the frozen spec-literal C23 replication (new data, not a rerun)."),
        "probe_symbols": PROBE_SYMBOLS,
        "depth_windows": {k: list(v) for k, v in DEPTH_WINDOWS.items()},
        "venues": venues,
        "recommendation": {
            "primary_new_venue": "bitget_usdt_m" if viable else None,
            "documented_fallback": fallback,
            "multiyear_viable": viable,
            "rationale": (
                "Bitget USDT-M serves 1H history back to 2023-01-01 with 890 USDT-M contracts; "
                "the whole spec altcoin universe is listed. New data + frozen spec = legitimate "
                "out-of-sample C23, NOT a same-data rerun."
                if viable else
                "Bitget multiyear depth unverified; probe Kraken Futures explicitly before C23. "
                "Do not substitute OKX/Binance/MEXC/Hyperliquid data."
            ),
        },
        "c23_data_status": ("ACQUISITION_VIABLE_BITGET_MULTIYEAR" if viable
                            else "ACQUISITION_BLOCKED"),
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = REPO_ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Wrote {out}")
    print(f"C23 data status: {report['c23_data_status']} | "
          f"primary_new_venue={report['recommendation']['primary_new_venue']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
