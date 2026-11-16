#!/usr/bin/env bash
# C20 detached finisher — drives the C20 cross-venue spec-literal campaign to the
# acceptance gate WITHOUT requiring a live agent session.
#
# WHY: one full C20 run costs ~4-5 h at --jobs 4 (300 permutation + 500 placebo
# draws per venue at ~38 s/draw). An agent session cannot stay alive that long, and
# a bare `timeout 900 python ...` guarantees a mid-artifact kill. This supervisor
# re-launches the campaign with --resume until `verify_c20_focus_campaign.py`
# prints PASS, then exits 0. Every attempt caches completed artifacts, so a kill
# costs at most the single in-flight artifact.
#
# USAGE (detached, survives session end):
#   setsid nohup bash scripts/finish_c20_detached.sh >/dev/null 2>&1 &
#
# STATUS:
#   tail -f /tmp/c20_supervisor.log
#   cat /tmp/c20_supervisor_status.json
#
# ENV KNOBS:
#   CRS_PYTHON=/path/to/python   C20_MAX_ATTEMPTS=40   C20_JOBS=4
#   C20_SUPERVISOR_LOG=/tmp/c20_supervisor.log
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 1

PY="${CRS_PYTHON:-/tmp/crs-venv/bin/python}"
LOG="${C20_SUPERVISOR_LOG:-/tmp/c20_supervisor.log}"
STATUS="/tmp/c20_supervisor_status.json"
MAX_ATTEMPTS="${C20_MAX_ATTEMPTS:-40}"
JOBS="${C20_JOBS:-4}"
LOCK="/tmp/c20_supervisor.lock"

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }

log() { echo "[$(ts)] $*" | tee -a "$LOG"; }

write_status() {
  # $1=state $2=attempt $3=detail
  python3 - "$STATUS" "$1" "$2" "$3" <<'PY' 2>/dev/null || true
import json, sys, datetime
path, state, attempt, detail = sys.argv[1:5]
json.dump({
    "state": state,
    "attempt": int(attempt),
    "detail": detail,
    "updated_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "pid": None,
    "log": "/tmp/c20_supervisor.log",
    "gate": "PYTHONPATH=. python scripts/verify_c20_focus_campaign.py",
}, open(path, "w"), indent=2)
PY
}

artifact_count() {
  ls research_state/*_20261116T063500Z.json 2>/dev/null | wc -l
}

# Single-instance lock: never run two supervisors against the same artifact set.
exec 9>"$LOCK"
if ! flock -n 9; then
  log "another supervisor holds $LOCK; exiting"
  exit 0
fi

log "supervisor start pid=$$ repo=$REPO python=$PY jobs=$JOBS max_attempts=$MAX_ATTEMPTS"

if [ ! -x "$PY" ]; then
  log "python missing at $PY; bootstrapping venv"
  bash scripts/bootstrap_env.sh /tmp/crs-venv >>"$LOG" 2>&1 || {
    log "bootstrap failed; cannot continue"
    write_status "blocked_bootstrap" 0 "venv bootstrap failed"
    exit 1
  }
fi

prev_count=-1
stall=0

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  before=$(artifact_count)
  log "attempt $attempt/$MAX_ATTEMPTS start (artifacts=$before)"

  PYTHONPATH=. "$PY" -u scripts/run_c20_cross_venue_campaign.py \
    --venues okx binance_um --jobs "$JOBS" --resume >>"$LOG" 2>&1
  run_rc=$?

  if PYTHONPATH=. "$PY" scripts/verify_c20_focus_campaign.py >>"$LOG" 2>&1; then
    after=$(artifact_count)
    log "C20 ACCEPTANCE: PASS (artifacts=$after, attempts=$attempt, run_rc=$run_rc)"
    write_status "PASS" "$attempt" "verify_c20_focus_campaign.py PASS after $attempt attempt(s); artifacts=$after"
    exit 0
  fi

  after=$(artifact_count)
  log "attempt $attempt finished rc=$run_rc artifacts=$before->$after; gate still FAIL"

  if [ "$after" -le "$before" ]; then
    stall=$((stall + 1))
    log "no new artifact produced (stall=$stall)"
    if [ "$stall" -ge 2 ]; then
      log "STALLED: two consecutive attempts produced no artifact; stopping instead of spinning"
      write_status "STALLED" "$attempt" "no new artifact in 2 attempts; inspect $LOG"
      exit 2
    fi
  else
    stall=0
  fi

  write_status "RUNNING" "$attempt" "artifacts=$after; gate FAIL; will retry"
  sleep 30
done

log "exhausted $MAX_ATTEMPTS attempts without PASS"
write_status "EXHAUSTED" "$MAX_ATTEMPTS" "gate still FAIL after max attempts"
exit 1