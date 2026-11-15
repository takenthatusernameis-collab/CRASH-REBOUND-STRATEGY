#!/usr/bin/env python3
"""Build a Hyperliquid-native 1h archive for the spec window from the public
Ironflow Hugging Face dataset (CC BY 4.0), derived from Hyperliquid node fills.

Source: https://huggingface.co/datasets/ironflow/hyperliquid-candles-1h
Coverage: 2025-05-25 .. 2026-10-31, one parquet per UTC month.
This script NEVER fabricates: it only re-aggregates real Hyperliquid OHLCV rows
and selects symbols with complete, gap-free hourly coverage over the spec window.
"""
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"
DL = REPO / "scratch" / "ironflow_dl"
BASE = "https://huggingface.co/datasets/ironflow/hyperliquid-candles-1h/resolve/main/data"
MONTHS = ["2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
          "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
START = pd.Timestamp("2025-12-20T00:00:00Z")
END = pd.Timestamp("2026-09-28T23:00:00Z")
EXPECTED = int((END - START).total_seconds() // 3600) + 1
MIN_VOL = 5_000_000.0


def download(m):
    out = DL / f"{m}.parquet"
    if out.exists() and out.stat().st_size > 1000:
        return out
    import urllib.request
    url = f"{BASE}/{m}.parquet"
    print(f"downloading {url}", flush=True)
    urllib.request.urlretrieve(url, out)
    return out


def min_roll24(close, vol):
    roll = 0.0
    best = None
    for i in range(len(close)):
        roll += vol[i] * close[i]
        if i >= 24:
            roll -= vol[i - 24] * close[i - 24]
        if i >= 23:
            best = roll if best is None else min(best, roll)
    return best


def main():
    DL.mkdir(parents=True, exist_ok=True)
    frames = []
    for m in MONTHS:
        p = download(m)
        df = pd.read_parquet(p, columns=["timestamp", "coin", "dex", "market_class",
                                         "open", "high", "low", "close", "volume"])
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    # native perps only: perp class, no HIP-3 dex prefix
    native = df[(df.market_class == "perp") & (df.dex.fillna("") == "")].copy()
    native["timestamp"] = pd.to_datetime(native["timestamp"], utc=True)
    native = native[(native.timestamp >= START) & (native.timestamp <= END)]
    native["timestamp_ms"] = (native["timestamp"].to_numpy(dtype="datetime64[ns]").astype("int64") // 1_000_000)

    kept = []
    report = {}
    for coin, g in native.groupby("coin"):
        g = g.sort_values("timestamp")
        ts = g["timestamp"].tolist()
        ok_cov = (len(g) == EXPECTED and ts[0] == START and ts[-1] == END
                  and all((b - a).total_seconds() == 3600 for a, b in zip(ts, ts[1:])))
        close = g["close"].to_numpy(dtype=float)
        vol = g["volume"].to_numpy(dtype=float)
        mv = min_roll24(close, vol) if len(g) >= 24 else None
        vol_ok = mv is not None and mv >= MIN_VOL
        report[coin] = {"bars": len(g), "coverage_ok": bool(ok_cov),
                        "min_roll24_usd": None if mv is None else round(mv, 2),
                        "volume_ok": bool(vol_ok)}
        if ok_cov and vol_ok:
            kept.append(g[["coin", "timestamp_ms", "open", "high", "low", "close", "volume"]]
                        .rename(columns={"coin": "symbol"}))

    if not kept:
        print("NO SYMBOLS PASSED; aborting")
        print(json.dumps(report, indent=1))
        return 1
    out = pd.concat(kept, ignore_index=True).sort_values(["symbol", "timestamp_ms"])
    out = out[["symbol", "timestamp_ms", "open", "high", "low", "close", "volume"]]
    archive_dir = STATE / "archives" / "hyperliquid_ironflow_1h_20251220_20260928"
    archive_dir.mkdir(parents=True, exist_ok=True)
    pq = archive_dir / "hyperliquid_native_1h_20251220_20260928.parquet"
    out.to_parquet(pq, index=False)
    sha = hashlib.sha256(pq.read_bytes()).hexdigest()

    complete = sorted([c for c, r in report.items() if r["coverage_ok"]])
    passing = sorted([c for c in kept for c in [c.symbol.iloc[0]]])
    src = archive_dir / "SOURCE.md"
    src.write_text(
        "# Hyperliquid-native 1h OHLCV archive (spec window)\n\n"
        f"- Window: `{START.isoformat()}` .. `{END.isoformat()}` ({EXPECTED} hourly bars/symbol)\n"
        "- Source: Ironflow Hugging Face dataset `ironflow/hyperliquid-candles-1h` "
        "(CC BY 4.0), hourly OHLCV for every Hyperliquid perp/spot, built from "
        "Ironflow's own Hyperliquid nodes; compared hour-by-hour with Hyperliquid's "
        "own candleSnapshot by the publisher.\n"
        "- Native perps only (market_class=perp, no HIP-3 dex); HIP-3 and spot excluded.\n"
        f"- Symbols passing complete-coverage + $5M trailing-24h volume floor: {len(passing)}\n"
        f"- Archive parquet sha256: `{sha}`\n"
        "- This is real, non-synthetic Hyperliquid market data. It is NOT the venue's own "
        "candleSnapshot endpoint and is NOT performance evidence.\n"
    )
    (archive_dir / f"{pq.name}.README.json").write_text(json.dumps(
        {"sha256": sha, "source": "ironflow_huggingface_hyperliquid-candles-1h",
         "license": "CC-BY-4.0", "window": {"start": START.isoformat(), "end": END.isoformat()},
         "expected_hourly_bars": EXPECTED, "symbols": passing,
         "coverage_complete_symbols": complete}, indent=2) + "\n")
    print(f"wrote {pq} sha256={sha}")
    print(f"symbols kept ({len(passing)}): {passing}")
    print(f"coverage-complete symbols ({len(complete)}): {complete}")
    print("per-symbol:")
    for c in sorted(report):
        r = report[c]
        print(f"  {c}: bars={r['bars']} cov={r['coverage_ok']} min24={r['min_roll24_usd']} vol={r['volume_ok']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())