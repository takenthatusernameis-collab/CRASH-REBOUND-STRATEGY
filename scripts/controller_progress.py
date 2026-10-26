#!/usr/bin/env python3
"""Determine whether a Kilo session produced meaningful project progress."""

import argparse
import subprocess
import sys


def run_git(*args):
    return subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def changed_paths(base_sha, head_sha):
    output = run_git("diff", "--name-only", f"{base_sha}..{head_sha}")
    return [line for line in output.splitlines() if line.strip()]


def is_meaningful(path):
    return not (path == ".github/workflows" or path.startswith(".github/workflows/"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--verified-remote-sha", default=None)
    args = parser.parse_args()

    if args.verified_remote_sha is not None and args.head_sha != args.verified_remote_sha:
        return 1

    paths = changed_paths(args.base_sha, args.head_sha)
    meaningful = [p for p in paths if is_meaningful(p)]
    return 0 if meaningful else 1


if __name__ == "__main__":
    sys.exit(main())
