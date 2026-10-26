"""Tests for serializing non-finite floating-point results.

The diagnostics pipeline writes JSONL records that must survive
json.dumps with allow_nan=False. Non-finite floats (NaN, inf, -inf) raise
ValueError under that flag, so callers must coerce them to sentinel strings
before serialization. These tests pin that contract down.
"""

import json
import math

import pytest

NONFINITE_SENTINELS = {
    math.nan: "NaN",
    math.inf: "Infinity",
    -math.inf: "-Infinity",
}


def serialize_result(value):
    """Mirror the serialization guard used by the diagnostics collector."""
    if isinstance(value, float) and not math.isfinite(value):
        value = NONFINITE_SENTINELS[value]
    return json.dumps({"result": value}, allow_nan=False, sort_keys=True)


def test_finite_float_serializes():
    out = json.loads(serialize_result(3.14))
    assert out == {"result": 3.14}


def test_integer_serializes():
    out = json.loads(serialize_result(42))
    assert out == {"result": 42}


def test_nan_serializes_to_sentinel():
    out = json.loads(serialize_result(math.nan))
    assert out == {"result": "NaN"}


def test_positive_infinity_serializes_to_sentinel():
    out = json.loads(serialize_result(math.inf))
    assert out == {"result": "Infinity"}


def test_negative_infinity_serializes_to_sentinel():
    out = json.loads(serialize_result(-math.inf))
    assert out == {"result": "-Infinity"}


def test_raw_nan_raises_without_guard():
    with pytest.raises(ValueError):
        json.dumps({"result": math.nan}, allow_nan=False)


def test_raw_infinity_raises_without_guard():
    with pytest.raises(ValueError):
        json.dumps({"result": math.inf}, allow_nan=False)


def test_mixed_record_serializes():
    record = {"loss": math.nan, "score": 0.95, "epochs": 5}
    guarded = {
        k: (NONFINITE_SENTINELS[v] if isinstance(v, float) and not math.isfinite(v) else v)
        for k, v in record.items()
    }
    out = json.loads(json.dumps(guarded, allow_nan=False, sort_keys=True))
    assert out == {"epochs": 5, "loss": "NaN", "score": 0.95}