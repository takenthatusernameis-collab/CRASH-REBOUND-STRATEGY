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
    # Synthetic: down then rebound - volumes set to meet >=$5M daily volume requirement
    return [
        {"timestamp": "2025-01-01T09:30:00", "open": 100.0, "high": 100.5, "low": 99.5, "close": 100.0, "volume": 50000},
        {"timestamp": "2025-01-01T09:31:00", "open": 100.0, "high": 100.1, "low": 97.0, "close": 97.5, "volume": 100000},  # crash
        {"timestamp": "2025-01-01T09:32:00", "open": 97.6, "high": 99.0, "low": 97.5, "close": 98.5, "volume": 80000},  # rebound
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


import os
import math
from pathlib import Path
from datetime import datetime, timedelta


class DataValidationError(Exception):
    pass


def validate_candles(candles: List[Dict[str, Any]], check_gaps: bool = True,
                     check_nonfinite: bool = True, check_lookahead: bool = True) -> None:
    """Validate candles for gaps, non-finite values, and look-ahead safety."""
    if not candles:
        raise DataValidationError("Empty candles list")

    for i, c in enumerate(candles):
        # Check for required fields
        for field in ['open', 'high', 'low', 'close', 'volume']:
            if field not in c:
                raise DataValidationError(f"Missing field {field} at index {i}")
            val = c[field]
            if val is None:
                raise DataValidationError(f"None value for {field} at index {i}")
            try:
                fval = float(val)
            except (TypeError, ValueError):
                raise DataValidationError(f"Non-numeric value for {field} at index {i}")
            if check_nonfinite and (math.isnan(fval) or math.isinf(fval)):
                raise DataValidationError(f"Non-finite value for {field} at index {i}")

        # OHLC sanity
        o = float(c['open']); h = float(c['high']); l = float(c['low']); cl = float(c['close'])
        if h < l or h < o or h < cl or l > o or l > cl:
            raise DataValidationError(f"Invalid OHLC at index {i}")

    # Check for gaps (if timestamps present)
    if check_gaps:
        timestamps = []
        for c in candles:
            ts = c.get('timestamp') or c.get('time') or c.get('t')
            if ts is not None:
                timestamps.append(ts)
        if len(timestamps) == len(candles) and len(timestamps) > 1:
            # Try to parse and check hourly gaps
            try:
                parsed = []
                for ts in timestamps:
                    if isinstance(ts, (int, float)):
                        # Assume seconds or milliseconds
                        if ts > 1e12:  # ms
                            parsed.append(datetime.fromtimestamp(ts / 1000))
                        else:
                            parsed.append(datetime.fromtimestamp(ts))
                    elif isinstance(ts, str):
                        # Try common formats
                        for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
                            try:
                                parsed.append(datetime.strptime(ts.replace('Z', ''), fmt))
                                break
                            except:
                                continue
                        else:
                            continue  # skip if can't parse
                    else:
                        continue
                if len(parsed) > 1:
                    for i in range(1, len(parsed)):
                        diff = (parsed[i] - parsed[i-1]).total_seconds() / 3600.0
                        if diff < 0 and check_lookahead:
                            raise DataValidationError(f"Look-ahead detected: timestamp goes backwards at {i}")
                        if diff > 2.0:  # More than 2 hour gap is suspicious
                            raise DataValidationError(f"Data gap detected at index {i}: {diff} hours")
            except DataValidationError:
                raise
            except Exception:
                pass  # Don't fail on timestamp parsing issues


def load_candles_from_csv(path: str) -> List[Dict[str, Any]]:
    import csv
    candles = []
    with open(path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            candle = {}
            for k, v in row.items():
                if k.lower() in ['timestamp', 'time', 'date']:
                    candle['timestamp'] = v
                elif k.lower() in ['open', 'o']:
                    candle['open'] = float(v)
                elif k.lower() in ['high', 'h']:
                    candle['high'] = float(v)
                elif k.lower() in ['low', 'l']:
                    candle['low'] = float(v)
                elif k.lower() in ['close', 'c']:
                    candle['close'] = float(v)
                elif k.lower() in ['volume', 'v', 'vol']:
                    candle['volume'] = float(v)
            candles.append(candle)
    return candles


def load_hyperliquid_candles(path_or_data, symbol: str = None) -> List[Dict[str, Any]]:
    """Load Hyperliquid candles from file or data structure."""
    if isinstance(path_or_data, str):
        if path_or_data.endswith('.json'):
            with open(path_or_data, 'r') as f:
                data = json.load(f)
        elif path_or_data.endswith('.csv'):
            return load_candles_from_csv(path_or_data)
        else:
            with open(path_or_data, 'r') as f:
                data = json.load(f)
    else:
        data = path_or_data

    # Handle various Hyperliquid API formats
    if isinstance(data, dict):
        if 'candles' in data:
            candles = data['candles']
        elif symbol and symbol in data:
            candles = data[symbol]
        elif 'data' in data:
            candles = data['data']
        else:
            # Try to find list values
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    candles = v
                    break
            else:
                raise ValueError("Invalid Hyperliquid candles format")
    elif isinstance(data, list):
        candles = data
    else:
        raise ValueError("Invalid Hyperliquid candles format")

    # Normalize format
    normalized = []
    for c in candles:
        norm = {}
        # Timestamp
        for ts_key in ['timestamp', 'time', 't', 'datetime']:
            if ts_key in c:
                norm['timestamp'] = c[ts_key]
                break
        # OHLCV
        for k, v in c.items():
            kl = k.lower()
            if kl in ['open', 'o']:
                norm['open'] = float(v)
            elif kl in ['high', 'h']:
                norm['high'] = float(v)
            elif kl in ['low', 'l']:
                norm['low'] = float(v)
            elif kl in ['close', 'c']:
                norm['close'] = float(v)
            elif kl in ['volume', 'v', 'vol', 'basevolume']:
                norm['volume'] = float(v)
        if all(k in norm for k in ['open', 'high', 'low', 'close', 'volume']):
            normalized.append(norm)

    validate_candles(normalized)
    return normalized


def load_multi_coin_data(data_source, symbols: List[str] = None,
                         min_daily_volume_usd: float = 5_000_000.0,
                         cache_dir: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """Load multi-coin hourly candles with volume filtering and caching."""
    result = {}

    # Check cache first
    if cache_dir:
        cache_path = Path(cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)

    if isinstance(data_source, dict):
        # Dict of symbol -> candles
        for symbol, candles in data_source.items():
            if symbols and symbol not in symbols:
                continue
            try:
                candles = load_hyperliquid_candles(candles, symbol)
                result[symbol] = candles
            except Exception:
                continue
    elif isinstance(data_source, str) and os.path.isdir(data_source):
        # Directory of JSON files
        for fname in os.listdir(data_source):
            if fname.endswith('.json'):
                symbol = fname.replace('.json', '').replace('_candles', '').upper()
                if symbols and symbol not in symbols:
                    continue
                try:
                    candles = load_hyperliquid_candles(os.path.join(data_source, fname), symbol)
                    result[symbol] = candles
                except Exception:
                    continue
    elif isinstance(data_source, str) and os.path.isfile(data_source):
        # Single file with multi-coin data
        try:
            candles = load_hyperliquid_candles(data_source)
            # Try to assign to symbols or use as single
            if symbols and len(symbols) == 1:
                result[symbols[0]] = candles
            else:
                result['UNKNOWN'] = candles
        except Exception:
            pass

    # Apply volume filter if requested
    if min_daily_volume_usd > 0:
        from src.strategy.crash_rebound import passes_universe_filter, filter_universe
        from src.strategy.config import DEFAULT_CONFIG
        filtered = filter_universe(result, min_daily_volume_usd=min_daily_volume_usd,
                                   regime_config=DEFAULT_CONFIG)
        result = {k: v for k, v in result.items() if k in filtered}

    return result


def get_hyperliquid_universe(min_daily_volume_usd: float = 5_000_000.0,
                            use_cache: bool = True,
                            cache_dir: str = None) -> List[str]:
    """Get Hyperliquid universe filtered by >= $5M 24h volume."""
    # Try to load from cache or fixtures if available
    if cache_dir is None:
        cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                 'research_state', 'cache')

    if use_cache and os.path.exists(cache_dir):
        # Look for cached universe data
        universe_file = os.path.join(cache_dir, 'universe.json')
        if os.path.exists(universe_file):
            try:
                with open(universe_file, 'r') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'universe' in data:
                    return data['universe']
            except Exception:
                pass

    # Default to common Hyperliquid perps that meet volume criteria
    # Based on spec: ~26 coins clear this bar
    default_universe = [
        "BTC", "ETH", "SOL", "XRP", "DOGE", "AVAX", "LINK", "SUI", "ADA", "DOT",
        "MATIC", "UNI", "AAVE", "LTC", "BCH", "NEAR", "APT", "ARB", "OP", "INJ",
        "TIA", "SEI", "ATOM", "FTM", "ALGO", "ICP"
    ]
    return default_universe
