import random

from src.strategy.crash_rebound import _rsi


def _series(n, seed=7):
    rng = random.Random(seed)
    price = 100.0
    rows = []
    for _ in range(n):
        price *= 1.0 + rng.uniform(-0.03, 0.03)
        rows.append({"close": price})
    return rows


def test_incremental_rsi_matches_uncached_prefixes():
    rows = _series(300)
    cache = {}
    for n in range(1, len(rows) + 1):
        inc = _rsi(rows[:n], period=21, cache=cache)
        unc = _rsi(rows[:n], period=21, cache=None)
        assert inc == unc


def test_incremental_rsi_skips_missing_closes_like_full_recompute():
    rows = _series(200)
    rows[40]["close"] = None
    rows[41]["close"] = None
    rows[120]["close"] = None
    cache = {}
    for n in range(1, len(rows) + 1):
        assert _rsi(rows[:n], period=21, cache=cache) == _rsi(rows[:n], period=21, cache=None)


def test_rsi_non_consecutive_prefix_falls_back_to_full_recompute():
    rows = _series(300)
    cache = {}
    assert _rsi(rows[:100], period=21, cache=cache) == _rsi(rows[:100], period=21, cache=None)
    # Jump forward: the incremental state cannot be extended, so it must recompute.
    assert _rsi(rows[:200], period=21, cache=cache) == _rsi(rows[:200], period=21, cache=None)