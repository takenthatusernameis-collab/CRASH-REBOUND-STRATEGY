#!/usr/bin/env bash
# Shared campaign-runner liveness helpers.
#
# Why not `pgrep -f`: pgrep matches the full command line of every process,
# including the caller's shell. When an agent probes with a command whose text
# contains the campaign script name, a dead runner is reported ALIVE. Observed
# 2026-11-23T05:35Z: status_c25.sh printed "RUNNER: ALIVE" with no campaign
# process alive, so next_c25_action.sh emitted NONE_RUNNER_ALIVE and the session
# would have waited instead of resuming C25.
#
# Require a real Python interpreter process instead. A shell wrapper whose argv
# merely mentions the script can never match.

# Print PIDs of real Python processes whose argv contains the given substring.
runner_pids() {
  local pat="$1"
  ps -eww -o pid=,comm=,args= 2>/dev/null \
    | awk -v pat="$pat" '$2 ~ /^python/ && index($0, pat) {print $1}'
}

# Print the matching real Python processes (pid/ppid/etime/time/stat/args).
runner_ps() {
  local pat="$1"
  ps -eww -o pid=,ppid=,etime=,time=,stat=,comm=,args= 2>/dev/null \
    | awk -v pat="$pat" '$6 ~ /^python/ && index($0, pat)'
}

# True when at least one real Python campaign process is running.
runner_alive() {
  [ -n "$(runner_pids "$1")" ]
}