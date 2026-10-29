#!/usr/bin/env python3
"""One-shot finalizer for GitHub Actions run #19 (40845157948).

Run this only after run #19 has completed (status != in_progress). It:
  1. fetches the run's job metadata via `gh run view --json jobs`
  2. appends a record to research_state/workflow_run_diagnostics.jsonl
  3. runs `python3 -m pytest -q`
  4. commits the ledger + handoff and pushes regular files to origin/main
     (workflow-file changes remain blocked by the GITHUB_TOKEN scope)
"""
import json
import os
import subprocess
import sys
import time

REPO = "/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY"
RUN_ID = "40845157948"
LEDGER = os.path.join(REPO, "research_state", "workflow_run_diagnostics.jsonl")
HANDOFF = os.path.join(REPO, "research_state", "handoff.md")


def run_cmd(cmd):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)


def fetch_run():
    r = run_cmd(["gh", "run", "view", RUN_ID, "--json", "status,conclusion,jobs"])
    if r.returncode != 0:
        print(f"gh run view failed: {r.stderr}", file=sys.stderr)
        return None
    return json.loads(r.stdout)


def append_record(run, jobs):
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
        "html_url": f"https://github.com/takenthatusernameis-collab/CRASH-REBOUND-STRATEGY/actions/runs/{RUN_ID}",
        "jobs_total": len(jobs),
        "log_capture_status": "not_scanned",
        "potential_errors": [],
        "run_attempt": 1,
        "run_completed_at": jobs[0].get("completedAt") if jobs and jobs[0].get("completedAt") not in (None, "0001-01-01T00:00:00Z") else None,
        "run_id": int(RUN_ID),
        "run_started_at": jobs[0].get("startedAt") if jobs else None,
        "schema_version": 1,
        "status": jobs[0].get("status") if jobs else None,
        "workflow_id": 396326025,
        "workflow_name": "Kilo General Agent Loop",
        "workflow_path": ".github/workflows/main.yml",
    }

    with open(LEDGER, "a") as f:
        f.write(json.dumps(record) + "\n")

    with open(os.path.join(REPO, "research_state", f"run_{RUN_ID}_jobs.json"), "w") as f:
        json.dump(jobs_info, f, indent=2)

    print(f"Appended run #{RUN_ID} record to ledger: conclusion={record['conclusion']} status={record['status']} (flush=True)")


def run_tests():
    r = run_cmd(["python3", "-m", "pytest", "-q"])
    print(r.stdout, flush=True)
    print(r.stderr, file=sys.stderr, flush=True)
    return r.returncode == 0


def git_commit_and_push():
    run_cmd(["git", "add", "--", "research_state/workflow_run_diagnostics.jsonl", "research_state/handoff.md"])
    diff = run_cmd(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        print("No changes to commit.")
        return True
    r = run_cmd(["git", "commit", "-m", "chore: capture completed workflow run diagnostics and handoff"])
    if r.returncode != 0:
        print(f"commit failed: {r.stderr}", file=sys.stderr)
        return False
    p = run_cmd(["git", "push", "origin", "main"])
    return p.returncode == 0


def main():
    data = fetch_run()
    if not data:
        sys.exit(1)

    status = data.get("status")
    conclusion = data.get("conclusion")
    jobs = data.get("jobs", [])
    print(f"run #{RUN_ID}: status={status} conclusion={conclusion}", flush=True)

    if status == "in_progress":
        print("Run still in_progress; nothing to do.", flush=True)
        sys.exit(2)

    append_record(data, jobs)
    ok = run_tests()
    print(f"tests: {'pass' if ok else 'fail'}", flush=True)
    if not ok:
        print("Tests failed; investigate/fix before committing.", flush=True)
        sys.exit(1)

    if git_commit_and_push():
        print("Ledger + handoff committed and pushed to origin/main.", flush=True)
    else:
        print("Commit/push failed; manual step required.", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()