"""Campaign performance metrics for the crash-rebound strategy.

Computes a full metrics suite from a portfolio simulation result, robust to
empty / no-trade runs. All rate-style metrics are expressed as decimals
(e.g. 0.05 == 5%) unless otherwise noted.
"""

from src.metrics.campaign_metrics import (
    compute_campaign_metrics,
    compute_metrics_from_trades,
    metrics_to_dict,
    metrics_to_csv_rows,
)

__all__ = [
    "compute_campaign_metrics",
    "compute_metrics_from_trades",
    "metrics_to_dict",
    "metrics_to_csv_rows",
]