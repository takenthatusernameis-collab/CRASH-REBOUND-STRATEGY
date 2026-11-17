# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T20:51:13Z — C21 MID-COMPUTE, DO NOT DUPLICATE)

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data (OKX + Binance UM).
**State:** C1–C20 CLOSED & CERTIFIED `NO_GO` (pytest 1047 passed, session_gate 21/21, verify_campaign_evidence PASS). C21 is the **only** open binding work.

**BOTTOM LINE UP FRONT (verified 2026-11-17T20:51:13Z):**
- Canonical C21 runner **ACTIVE**: PID 5175 (`python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume`), 52 min wall, 45 min CPU, 635 MB RSS.
- **0/12 required artifacts** on disk; `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (expected).
- **DO NOT START A SECOND RUNNER** — the live process is computing. Let it finish.

---

## EXECUTE IN ORDER — NO PLANNING STOPS, NO RELAUNCH, NO COMMIT

### 1. CONFIRM RUNNER ALIVE (takes 5 sec)
```bash
ps -eo pid,etime,time,stat,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep
```
- If **PID 5175 (or similar) is RUNNING (R/S state)**: GO TO STEP 2.
- If **NO RUNNER ALIVE** (process died): GO TO STEP 3.

### 2. MONITOR EXISTING RUNNER TO COMPLETION (multi-hour battery)
```bash
# Watch artifact count climb to 12/12
watch -n 30 'ls research_state/c21_*_20261117T064408Z.json 2>/dev/null | grep -v prereg | wc -l'

# Verify gate when artifacts appear
PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py
```
**ACCEPTANCE CRITERIA:** `C21 ACCEPTANCE: PASS` (token `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` with power curve + honest pooled verdict). All 12 artifacts present with prereg-specified folds (2023,2024,2025,2026YTD), 20k bootstrap/permutation draws, 2k placebo subsets, BH correction, pooled venue-blocked bootstrap ≥20k draws.

**Do not reduce draw counts.** Do not hand-fabricate artifacts. If runner dies mid-venue, `--resume` restarts that venue from scratch — let it finish.

### 3. ONLY IF RUNNER DEAD: START CANONICAL RESUME RUN (detached, durable)
```bash
bash scripts/run_c21_detached_durable.sh
```
This script refuses to start if a runner is alive, then launches `--jobs 4 --resume` with `nohup` and a real log `research_state/c21_run_<UTC>.log`. Monitor that log to completion.

### 4. POST-C21 CLOSURE (after C21 ACCEPTANCE: PASS)
```bash
PYTHONPATH=. .venv/bin/python -m pytest tests/ -q   # must stay 1047 passed, 1 skipped
PYTHONPATH=. .venv/bin/python scripts/session_gate.py  # must stay 21/21 checks passed, Phase O timestamp 2026-11-13T23:38:47Z
```
Then update HANDOFF.md with new timestamped literals. **Do not commit unless explicitly asked.**

---

## NEVER DO
- Relitigate C1–C20, relaunch C20, invent C22+ on same data.
- Relabel cross-venue as Hyperliquid-native (`is_hyperliquid_venue_data=false` fixed).
- Relax `SPEC_LITERAL_NEXT_OPEN`, synthetic gap-fill as verified, fabricate `GO`.
- Edit completed campaign artifacts or commit without authorization.
- Treat "monitoring" without artifact changes as progress.

---

## BOTTLENECKS REMOVED
- ✅ Deps/env: `.venv` ready (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
- ✅ "Not running": canonical C21 **is active** — no duplicate launch.
- ✅ "Do nothing" paralysis: C21-T1 preregistered, gate RED — heavy execution mandatory.
- ✅ No C20/stale locks: no `finish_c20`/`run_c20` processes.
- ⚠️ **Current blocker (progress durability):** runner writes artifacts only at venue end. If alive, **let it finish**. If dead, restart with `--jobs 4 --resume` and let it complete.

**C21-T1 IS THE BINDING NEXT CAMPAIGN. THE GATE IS RED UNTIL THE FULL BATTERY EXECUTES AND VERIFIER PRINTS `C21 ACCEPTANCE: PASS`. FUTURE AGENTS CANNOT AVOID THIS HEAVY WORK.**