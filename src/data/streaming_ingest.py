"""Streaming, large-archive/parquet-safe candle ingest with incremental checksums.

Track-4(d) hardening: read candle archives row-by-row (bounded memory) instead of
loading whole files into RAM, so multi-GB parquet/NDJSON/CSV archives are safe to
ingest. Computes per-file and per-symbol sha256 incrementally. Never fabricates
data; never claims performance evidence. Deterministic.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple

try:
    import pyarrow  # type: ignore
    import pyarrow.parquet as _pq  # type: ignore
except Exception:  # pragma: no cover
    pyarrow = None  # type: ignore
    _pq = None  # type: ignore


# Columns we accept (case-insensitive) when mapping raw rows to normalized candles.
_TS_KEYS = ("timestamp", "time", "date", "t", "datetime", "ts")
_OHLCV_MAP = {
    "open": "open", "o": "open",
    "high": "high", "h": "high",
    "low": "low", "l": "low",
    "close": "close", "c": "close",
    "volume": "volume", "v": "volume", "vol": "volume", "basevolume": "volume",
    "quotevolume": "volume_usd",
}
_SYMBOL_KEYS = ("symbol", "coin", "s", "sym", "ticker")


def _sha256_streaming() -> Tuple[Callable[[bytes], None], Callable[[], str]]:
    h = hashlib.sha256()

    def feed(b: bytes) -> None:
        if b:
            h.update(b)

    def digest() -> str:
        return h.hexdigest()

    return feed, digest


def _normalize_row(r: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Map a raw row dict to a normalized candle dict (streaming-safe, no full-file load)."""
    if not isinstance(r, dict):
        return None
    out: Dict[str, Any] = {}
    # timestamp
    for k in _TS_KEYS:
        if k in r and r[k] not in (None, ""):
            out["timestamp"] = r[k]
            break
    if "timestamp_ms" in r and r["timestamp_ms"] not in (None, ""):
        out["timestamp_ms"] = r["timestamp_ms"]
    elif "timestamp" in out:
        t = out["timestamp"]
        if isinstance(t, (int, float)):
            it = int(t)
            out["timestamp_ms"] = it if it > 10 ** 12 else it * 1000
    # OHLCV
    for k, v in r.items():
        kl = str(k).lower()
        if kl in _OHLCV_MAP:
            try:
                out[_OHLCV_MAP[kl]] = float(v)
            except (TypeError, ValueError):
                continue
    need = ("open", "high", "low", "close", "volume")
    if all(k in out for k in need):
        return out
    return None


def iter_jsonl_rows(path: Path) -> Iterator[Dict[str, Any]]:
    """Yield parsed JSON rows from a JSONL/NDJSON file, one line at a time."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                yield obj


def iter_csv_rows(path: Path) -> Iterator[Dict[str, Any]]:
    """Yield CSV rows as dicts, one row at a time (streaming)."""
    import csv
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row is None:
                continue
            yield {k: v for k, v in row.items() if k is not None}


def iter_parquet_batches(path: Path, batch_size: int = 65536) -> Iterator[Any]:
    """Yield record batches from a Parquet file without loading it all into memory."""
    if _pq is None:
        raise RuntimeError("pyarrow not installed; cannot stream parquet")
    pth = Path(path)
    pf = _pq.ParquetFile(str(pth))
    for batch in pf.iter_batches(batch_size=batch_size):
        yield batch


def sha256_file_streaming(path: Path, chunk_size: int = 1 << 20) -> str:
    """Incremental sha256 of a file (bounded memory)."""
    feed, digest = _sha256_streaming()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            feed(b)
    return digest()


def sha256_bytes(b: bytes) -> str:
    feed, digest = _sha256_streaming()
    feed(b)
    return digest()


def stream_normalize(path: Path, symbol: str) -> Iterator[Dict[str, Any]]:
    """Stream-normalize rows for a symbol from JSONL/CSV/Parquet (row-by-row)."""
    suffix = Path(path).suffix.lower()
    if suffix in (".ndjson", ".jsonl"):
        for r in iter_jsonl_rows(Path(path)):
            sym = None
            for k in _SYMBOL_KEYS:
                if k in r:
                    sym = str(r[k]).strip().upper()
                    break
            if sym and sym != symbol.upper():
                continue
            nc = _normalize_row(r)
            if nc:
                yield nc
    elif suffix == ".csv":
        for r in iter_csv_rows(Path(path)):
            sym = None
            for k in _SYMBOL_KEYS:
                if k in r:
                    sym = str(r[k]).strip().upper()
                    break
            if sym and sym != symbol.upper():
                continue
            nc = _normalize_row(r)
            if nc:
                yield nc
    elif suffix == ".parquet":
        for batch in iter_parquet_batches(Path(path)):
            for r in batch.to_pylist():
                sym = None
                for k in _SYMBOL_KEYS:
                    if k in r:
                        sym = str(r[k]).strip().upper()
                        break
                if sym and sym != symbol.upper():
                    continue
                nc = _normalize_row(r)
                if nc:
                    yield nc
    else:
        raise ValueError(f"Unsupported streaming format: {suffix}")