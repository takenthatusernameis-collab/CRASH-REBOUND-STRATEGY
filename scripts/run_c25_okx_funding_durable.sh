#!/usr/bin/env bash
# GUARDED durable wrapper for OKX realized-funding acquisition (C25 prerequisite).
#
# VERIFIED 2026-11-19T10:14Z: GET /api/v5/public/funding-rate-history caps at 100
# rows and serves only a rolling ~33-day window regardless of the before cursor
# (reachable: 2026-08-19..2026-09-21). The C25 window is 2023-01-01..2026-09-28,
# so the deep multiyear fetch is NOT possible. okx is recorded UNAVAILABLE_FUNDING
# (never zero-filled) and C25 evaluates cost_taker_funding / cost_stress on
# binance_um + mexc + bitget, per the prereg availability clause.
#
# This wrapper therefore probes retention first and only fetches if the probe ever
# reports OKX_FUNDING_HISTORY_REACHABLE. Do not bypass the guard by calling
# fetch_funding_history.py --venues okx directly; it silently produces a partial
# ~1 month cache that cannot support the multiyear inference.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"

if [ ! -x "$PY" ]; then
  echo "[okx-funding] ERROR: missing venv at $PY; run: bash scripts/bootstrap_env.sh" >&2
  exit 1
fi

export PYTHONPATH=.
set +e
PROBE_OUT="$("$PY" scripts/probe_c25_okx_funding_retention.py 2>&1)"
PROBE_RC=$?
set -e
echo "$PROBE_OUT"

if ! grep -q "OKX_FUNDING_HISTORY_REACHABLE" <<<"$PROBE_OUT"; then
  echo "[okx-funding] OKX_FUNDING_BLOCKED_BY_API_RETENTION -> okx stays UNAVAILABLE_FUNDING; nothing to launch."
  exit 0
fi

echo "[okx-funding] deep history reachable; starting acquisition"
exec "$PY" scripts/fetch_funding_history.py --venues okx --workers 8
