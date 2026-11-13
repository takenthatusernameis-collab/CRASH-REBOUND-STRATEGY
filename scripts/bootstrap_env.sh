#!/usr/bin/env bash
# Bootstrap a local test environment for CRASH-REBOUND-STRATEGY.
# The runner image ships without pytest/numpy/pandas/requests/pyarrow; this is the
# documented single biggest avoidable time sink. Run this first, then the test suite.
set -euo pipefail

VENV="${1:-/tmp/crs-venv}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m venv "$VENV"
"$VENV/bin/pip" install --disable-pip-version-check -q -r "$ROOT/requirements-test.txt"

echo "venv ready: $VENV"
echo "tests: PYTHONPATH=. $VENV/bin/python -m pytest -q -rs"