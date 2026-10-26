import subprocess
import os
import tempfile

def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)

def setup_repo():
    d = tempfile.mkdtemp()
    git(d, "init", "-q")
    git(d, "config", "user.email", "t@t.com")
    git(d, "config", "user.name", "t")
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("hello\n")
    git(d, "add", "README.md")
    git(d, "commit", "-q", "-m", "init")
    base = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    return d, base

def run_script(d, base, head, remote=None):
    cmd = ["python3", os.path.join(os.getcwd(), "scripts", "controller_progress.py"),
           "--base-sha", base, "--head-sha", head]
    if remote is not None:
        cmd += ["--verified-remote-sha", remote]
    return subprocess.run(cmd, cwd=d, capture_output=True)

def test_meaningful_change_returns_zero():
    d, base = setup_repo()
    with open(os.path.join(d, "src.py"), "w") as f:
        f.write("x=1\n")
    git(d, "add", "src.py")
    git(d, "commit", "-q", "-m", "change")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    r = run_script(d, base, head)
    assert r.returncode == 0

def test_workflow_only_change_returns_nonzero():
    d, base = setup_repo()
    os.makedirs(os.path.join(d, ".github", "workflows"), exist_ok=True)
    with open(os.path.join(d, ".github", "workflows", "x.yml"), "w") as f:
        f.write("name: x\n")
    git(d, "add", ".github/workflows/x.yml")
    git(d, "commit", "-q", "-m", "wf")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    r = run_script(d, base, head)
    assert r.returncode != 0

def test_no_change_returns_nonzero():
    d, base = setup_repo()
    r = run_script(d, base, base)
    assert r.returncode != 0

def test_verified_remote_mismatch_returns_nonzero():
    d, base = setup_repo()
    with open(os.path.join(d, "src.py"), "w") as f:
        f.write("x=1\n")
    git(d, "add", "src.py")
    git(d, "commit", "-q", "-m", "change")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    r = run_script(d, base, head, remote="deadbeef")
    assert r.returncode != 0

def test_verified_remote_match_returns_zero():
    d, base = setup_repo()
    with open(os.path.join(d, "src.py"), "w") as f:
        f.write("x=1\n")
    git(d, "add", "src.py")
    git(d, "commit", "-q", "-m", "change")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()
    r = run_script(d, base, head, remote=head)
    assert r.returncode == 0
