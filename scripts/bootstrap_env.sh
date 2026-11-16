#!/usr/bin/env bash
# Bootstrap a local test environment for CRASH-REBOUND-STRATEGY.
# The runner image ships without pytest/numpy/pandas/requests/pyarrow; this is the
# documented single biggest avoidable time sink. Run this first, then the test suite.
#
# DURABLE DEFAULT: the venv now lives at "$ROOT/.venv" (gitignored, survives /tmp
# wipes and agent restarts) instead of the ephemeral "/tmp/crs-venv". On runner
# images /tmp is wiped between sessions, which used to force a full ~5-10 min pip
# rebuild after every restart — the single largest avoidable bottleneck. Pass an
# explicit path as $1 to override (e.g. for a scratch venv).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${1:-$ROOT/.venv}"

if [ -x "$VENV/bin/python" ] && "$VENV/bin/python" -c "import numpy,pandas,pyarrow,requests,pytest" >/dev/null 2>&1; then
  echo "venv already ready: $VENV"
  echo "tests: PYTHONPATH=. $VENV/bin/python -m pytest -q -rs"
  exit 0
fi

python3 -m venv "$VENV"
"$VENV/bin/pip" install --disable-pip-version-check -q -r "$ROOT/requirements-test.txt"

echo "venv ready: $VENV"
echo "tests: PYTHONPATH=. $VENV/bin/python -m pytest -q -rs"