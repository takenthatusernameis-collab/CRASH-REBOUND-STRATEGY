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
