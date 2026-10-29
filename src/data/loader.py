import json
from typing import List, Dict, Any


def load_candles_from_json(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        data = json.load(f)
    if isinstance(data, dict) and 'candles' in data:
        return data['candles']
    if isinstance(data, list):
        return data
    raise ValueError("Invalid candles format")


def make_fixture_crash_rebound() -> List[Dict[str, Any]]:
    # Synthetic: down then rebound
    return [
        {"timestamp": "2025-01-01T09:30:00", "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 1000},
        {"timestamp": "2025-01-01T09:31:00", "open": 100.0, "high": 100.1, "low": 97.0, "close": 97.5, "volume": 5000},  # crash
        {"timestamp": "2025-01-01T09:32:00", "open": 97.6, "high": 99.0, "low": 97.5, "close": 98.5, "volume": 3000},  # rebound
    ]


def make_fixture_crash_rebound_multi() -> List[Dict[str, Any]]:
    """Multi-symbol style fixtures for SPY/QQQ/IWM style symbols."""
    # Return dict keyed by symbol for convenience
    fixtures = {}
    # SPY-like: clean crash then rebound
    fixtures['SPY'] = [
        {"timestamp": "2025-01-02T09:30:00", "open": 500.0, "high": 500.5, "low": 499.5, "close": 500.0, "volume": 10000},
        {"timestamp": "2025-01-02T09:31:00", "open": 500.0, "high": 500.1, "low": 485.0, "close": 487.5, "volume": 50000},  # crash
        {"timestamp": "2025-01-02T09:32:00", "open": 488.0, "high": 497.0, "low": 487.5, "close": 496.0, "volume": 30000},  # rebound
    ]
    # QQQ-like: deeper crash
    fixtures['QQQ'] = [
        {"timestamp": "2025-01-03T09:30:00", "open": 400.0, "high": 400.5, "low": 399.5, "close": 400.0, "volume": 8000},
        {"timestamp": "2025-01-03T09:31:00", "open": 400.0, "high": 400.1, "low": 380.0, "close": 382.0, "volume": 60000},
        {"timestamp": "2025-01-03T09:32:00", "open": 383.0, "high": 395.0, "low": 382.5, "close": 394.0, "volume": 40000},
    ]
    # IWM-like: smaller move
    fixtures['IWM'] = [
        {"timestamp": "2025-01-04T09:30:00", "open": 200.0, "high": 200.5, "low": 199.5, "close": 200.0, "volume": 5000},
        {"timestamp": "2025-01-04T09:31:00", "open": 200.0, "high": 200.1, "low": 193.0, "close": 194.5, "volume": 40000},
        {"timestamp": "2025-01-04T09:32:00", "open": 195.0, "high": 198.5, "low": 194.5, "close": 198.0, "volume": 25000},
    ]
    # No-trade case
    fixtures['NO_TRADE'] = [
        {"timestamp": "2025-01-05T09:30:00", "open": 150.0, "high": 151.0, "low": 149.0, "close": 150.5, "volume": 2000},
        {"timestamp": "2025-01-05T09:31:00", "open": 150.5, "high": 151.5, "low": 150.0, "close": 151.0, "volume": 2000},
    ]
    return fixtures
