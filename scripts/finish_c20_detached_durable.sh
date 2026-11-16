#!/usr/bin/env bash
# C20 detached finisher (durable edition) — drives the C20 cross-venue spec-literal
# campaign to the acceptance gate WITHOUT requiring a live agent session.
#
# WHY THIS FILE EXISTS (bottleneck removed):
#   The original `finish_c20_detached.sh` kept its single-instance lock, log,
#   status file, and venv under /tmp. On runner images /tmp is wiped between
#   sessions, so a restart could (a) lose the lock and launch a SECOND concurrent
#   CPU-heavy supervisor, corrupting artifacts, and (b) force a full ~5-10 min pip
#   rebuild. This variant stores lock/log/status under the durable repo dir
#   (`research_state/.c20/`) and uses the durable repo venv (`.venv`), while still
#   honoring /tmp paths for backward compatibility with the in-flight attempt 1
#   (which holds /tmp/c20_supervisor.lock). See HANDOFF.md.
#
# WHY detached: one full C20 run costs ~4-5 h at --jobs 4. An agent session cannot
# stay alive that long, and a bare `timeout 900 python ...` guarantees a mid-artifact
# kill. This supervisor re-launches with --resume until verify_c20_focus_campaign.py
# prints PASS, then exits 0. Completed artifacts are cached, so a kill costs at most
# the single in-flight artifact.
#
# USAGE (detached, survives session end):
#   setsid nohup bash scripts/finish_c20_detached.sh >/dev/null 2>&1 &
#
# STATUS / LOG (durable):
#   tail -f research_state/.c20/supervisor.log
#   cat research_state/.c20/supervisor_status.json
#
# ENV KNOBS:
#   CRS_PYTHON=...            venv python (default: <repo>/.venv/bin/python)
#   C20_MAX_ATTEMPTS=40       max resume attempts before giving up
#   C20_JOBS=4                worker processes (do NOT exceed nproc)
#   C20_SUPERVISOR_STATE_DIR  durable state dir (default: <repo>/research_state/.c20)
#   C20_SUPERVISOR_EPHMERAL   if set, force legacy /tmp paths (escape hatch)
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 1

# Durable state dir. Prefer repo-local (survives /tmp wipes); fall back to /tmp only
# if the repo dir is somehow unwritable.
if [ -z "${C20_SUPERVISOR_EPHMERAL:-}" ]; then
  STATE_DIR="${C20_SUPERVISOR_STATE_DIR:-$REPO/research_state/.c20}"
  mkdir -p "$STATE_DIR" 2>/dev/null || STATE_DIR="/tmp"
else
  STATE_DIR="/tmp"
fi
# If we fell back to /tmp, namespace the files so we never collide with legacy ones.
if [ "$STATE_DIR" = "/tmp" ]; then
  LOG="/tmp/c20_supervisor_durable.log"
  STATUS="/tmp/c20_supervisor_durable_status.json"
  LOCK="/tmp/c20_supervisor_durable.lock"
else
  LOG="$STATE_DIR/supervisor.log"
  STATUS="$STATE_DIR/supervisor_status.json"
  LOCK="$STATE_DIR/supervisor.lock"
fi

PY="${CRS_PYTHON:-$REPO/.venv/bin/python}"
MAX_ATTEMPTS="${C20_MAX_ATTEMPTS:-40}"
JOBS="${C20_JOBS:-4}"

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
    "log": None,
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

log "supervisor start pid=$$ repo=$REPO python=$PY jobs=$JOBS max_attempts=$MAX_ATTEMPTS state_dir=$STATE_DIR"

if [ ! -x "$PY" ]; then
  log "python missing at $PY; bootstrapping durable venv"
  bash scripts/bootstrap_env.sh "$REPO/.venv" >>"$LOG" 2>&1 || {
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

  # The campaign script only prints when an artifact lands, so a healthy heavy run
  # can look "silent" for hours. Write IN_FLIGHT_HEAVY_COMPUTE while alive so a
  # future agent does not mistake silence for a stall. A true stall is still
  # detected by the no-new-artifact counter below.
  PYTHONPATH=. "$PY" -u scripts/run_c20_cross_venue_campaign.py \
    --venues okx binance_um --jobs "$JOBS" --resume >>"$LOG" 2>&1 &
  campaign_pid=$!
  (
    while kill -0 "$campaign_pid" 2>/dev/null; do
      sleep 60
      if ! kill -0 "$campaign_pid" 2>/dev/null; then
        break
      fi
      write_status "IN_FLIGHT_HEAVY_COMPUTE" "$attempt" \
        "campaign running; no new log line is EXPECTED until an artifact lands; artifacts=$before; poll ps for CPU time advancement"
    done
  ) &
  watchdog_pid=$!
  wait "$campaign_pid"
  run_rc=$?
  kill "$watchdog_pid" 2>/dev/null
  wait "$watchdog_pid" 2>/dev/null

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