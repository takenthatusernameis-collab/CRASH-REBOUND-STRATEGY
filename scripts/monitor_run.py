#!/usr/bin/env python3
"""Generic monitor for a GitHub Actions run until completion.

Usage: python3 scripts/monitor_run.py <RUN_ID> [POLL_INTERVAL_SECONDS] [JOB_TIMEOUT_MIN]

On completion:
  - fetch job metadata via `gh run view --json jobs`
  - append a record to research_state/workflow_run_diagnostics.jsonl
  - run `python3 -m pytest -q`
  - log that commit/push of ledger + handoff is required (manual step)
"""
import json
import os
import subprocess
import sys
import time

REPO = "/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY"
LEDGER = os.path.join(REPO, "research_state", "workflow_run_diagnostics.jsonl")
DEFAULT_POLL_INTERVAL = 30
DEFAULT_JOB_TIMEOUT_MIN = 360


def run_cmd(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def fetch_run(run_id):
    r = run_cmd(["gh", "run", "view", run_id, "--json", "jobs"])
    if r.returncode != 0:
        print(f"gh run view failed: {r.stderr}", file=sys.stderr)
        return None
    return json.loads(r.stdout)


def append_record(run_id, run, jobs):
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    jobs_info = []
    for job in jobs:
        jobs_info.append({
            "databaseId": job.get("databaseId"),
            "name": job.get("name"),
            "status": job.get("status"),
            "conclusion": job.get("conclusion"),
            "startedAt": job.get("startedAt"),
            "completedAt": job.get("completedAt"),
        })

    record = {
        "actor": "takenthatusernameis-collab",
        "branch": "main",
        "capture_attempts": 1,
        "capture_status": "complete",
        "captured_at_utc": now,
        "conclusion": jobs[0].get("conclusion") if jobs else None,
        "created_at": run.get("created_at") if run else None,
        "event": "schedule",
        "head_sha": run.get("head_sha") if run else None,
        "html_url": f"https://github.com/takenthatusernameis-collab/CRASH-REBOUND-STRATEGY/actions/runs/{run_id}",
        "jobs_total": len(jobs),
        "log_capture_status": "not_scanned",
        "potential_errors": [],
        "run_attempt": 1,
        "run_completed_at": jobs[0].get("completedAt") if jobs and jobs[0].get("completedAt") not in (None, "0001-01-01T00:00:00Z") else None,
        "run_id": int(run_id),
        "run_started_at": jobs[0].get("startedAt") if jobs else None,
        "schema_version": 1,
        "status": jobs[0].get("status") if jobs else None,
        "workflow_id": 396326025,
        "workflow_name": "Kilo General Agent Loop",
        "workflow_path": ".github/workflows/main.yml",
    }

    with open(LEDGER, "a") as f:
        f.write(json.dumps(record) + "\n")

    with open(os.path.join(REPO, "research_state", f"run_{run_id}_jobs.json"), "w") as f:
        json.dump(jobs_info, f, indent=2)

    print(f"Appended run #{run_id} record to ledger: conclusion={record['conclusion']} status={record['status']} (flush=True)")


def run_tests():
    r = run_cmd(["python3", "-m", "pytest", "-q"])
    print(r.stdout, flush=True)
    print(r.stderr, file=sys.stderr, flush=True)
    return r.returncode == 0


def main():
    if len(sys.argv) < 2:
        print("usage: monitor_run.py <RUN_ID> [POLL_INTERVAL] [JOB_TIMEOUT_MIN]", file=sys.stderr)
        sys.exit(2)

    run_id = sys.argv[1]
    poll_interval = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_POLL_INTERVAL
    job_timeout_min = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_JOB_TIMEOUT_MIN

    deadline = time.time() + job_timeout_min * 60
    print(f"Monitoring run #{run_id} (poll {poll_interval}s, job timeout {job_timeout_min} min) [started]", flush=True)

    while time.time() < deadline:
        data = fetch_run(run_id)
        if not data:
            time.sleep(poll_interval)
            continue

        jobs = data.get("jobs", [])
        job = jobs[0] if jobs else {}
        status = job.get("status")
        conclusion = job.get("conclusion")

        print(f"run #{run_id}: status={status} conclusion={conclusion}", flush=True)

        if status != "in_progress":
            append_record(run_id, data, jobs)
            ok = run_tests()
            print(f"tests: {'pass' if ok else 'fail'}", flush=True)
            if ok:
                print("MANUAL STEP REQUIRED: commit research_state/ledger + handoff and push regular files (contents: write). Workflow changes blocked by token scope.", flush=True)
            else:
                print("Tests failed; investigate/fix before committing.", flush=True)
            return

        time.sleep(poll_interval)

    print(f"run #{run_id}: no completion observed before {job_timeout_min}-minute job timeout; stall noted. Do not cancel/force-push/escalate without explicit user direction.", flush=True)


if __name__ == "__main__":
    main()