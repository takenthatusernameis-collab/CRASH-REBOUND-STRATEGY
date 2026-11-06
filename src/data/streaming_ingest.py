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