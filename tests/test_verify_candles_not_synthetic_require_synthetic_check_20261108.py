"""Failing-test-first regression: verify_candles_not_synthetic require_synthetic_check semantics.

Found 2026-11-08T01:20Z: `verify_candles_not_synthetic(candles, require_synthetic_check=True)`
unconditionally raised ProvenanceError for *every* call, including when the caller
supplied a valid synthetic_check dict. A verified provenance entry carrying
`synthetic_check: {is_synthetic: False, reason: "varied_series_ok"}` was therefore
treated as unverified, even though it was the canonical case the flag was designed
to accept. The flag must accept a present, non-synthetic synthetic_check dict and
still re-check the actual candles, while failing closed on missing/declared-synthetic.

Deterministic, synthetic, non-evidence.
"""
from __future__ import annotations

import pytest

from src.data.provenance import ProvenanceError, verify_candles_not_synthetic


def _varied(n: int = 100) -> list:
    import math
    out = []
    for i in range(n):
        px = 60000.0 + 1000.0 * math.sin(i / 7.0) + i
        out.append({
            "open": px, "high": px + 50, "low": px - 50,
            "close": px + 25, "volume": float(2_000_000_000 + (i % 100) * 1_000_000),
        })
    return out


def _flat(n: int = 100) -> list:
    return [
        {"open": 60000.0, "high": 60200.0, "low": 59800.0, "close": 60000.0, "volume": 2e9}
        for _ in range(n)
    ]


def _clean_check() -> dict:
    return {"is_synthetic": False, "reason": "varied_series_ok"}


def test_require_synthetic_check_accepts_present_clean_check():
    """A verified entry with a clean synthetic_check dict must NOT raise."""
    res = verify_candles_not_synthetic(_varied(), require_synthetic_check=True,
                                       synthetic_check=_clean_check())
    assert res["is_synthetic"] is False


def test_require_synthetic_check_still_redetects_flat_candles():
    """Even with a clean synthetic_check, the actual candles are re-inspected."""
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_flat(), require_synthetic_check=True,
                                     synthetic_check=_clean_check(), raise_on_synthetic=True)


def test_require_synthetic_check_rejects_missing_check():
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_varied(), require_synthetic_check=True)


def test_require_synthetic_check_rejects_non_dict_check():
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_varied(), require_synthetic_check=True,
                                     synthetic_check="not-a-dict")


def test_require_synthetic_check_rejects_declared_synthetic_check():
    with pytest.raises(ProvenanceError):
        verify_candles_not_synthetic(_varied(), require_synthetic_check=True,
                                     synthetic_check={"is_synthetic": True, "reason": "flat"},
                                     raise_on_synthetic=True)


def test_require_synthetic_check_declared_synthetic_reported_when_not_raising():
    res = verify_candles_not_synthetic(_varied(), require_synthetic_check=True,
                                       synthetic_check={"is_synthetic": True, "reason": "flat"})
    assert res["is_synthetic"] is True
    assert res.get("source") == "provenance_manifest"


def test_backward_compat_default_unaffected():
    res = verify_candles_not_synthetic(_varied())
    assert res["is_synthetic"] is False