# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T23:51:43Z — C21 MID-COMPUTE, DO NOT DUPLICATE)

**Authoritative durable handoff:** `HANDOFF.md` — this file is a pointer only; do not maintain a second source of truth. Read `HANDOFF.md` for the full binding state, C21 spec, guardrails, file map, and the execute-in-order steps.

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data (OKX + Binance UM).
**State:** C1–C20 CLOSED & CERTIFIED `NO_GO`. C21-T1 is the **only** open binding work.

**BOTTOM LINE UP FRONT (verified 2026-11-17T23:51:43Z):**
- Canonical C21 runner **ACTIVE**: PID 21945 (`python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume`), ppid 1 (detached), ~1h52m wall, 4 workers R-state ~94–95% CPU each. **4/8** per-fold checkpoints — all OKX folds complete; **OKX verdict: NO_GO** (survivors=0, trades=113, pnl=-54799.23). **Binance UM fold 2023 computing** (census events=342 trades=28 pnl=+34989.9036, fast-path validated). **5/12** artifacts present; `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` — 8 requirements missing.
- **DO NOT START A SECOND RUNNER** — the live process is computing on all 4 cores.
- **Binding no-avoidance campaign:** C21-T1 is the sole open campaign. Continue heavy execution until `C21 ACCEPTANCE: PASS`; no planning-only, artifact-free monitoring, draw-count reduction, or C22+ relabeling is accepted.

**Next action:** monitor the live runner to `C21 ACCEPTANCE: PASS` (per-fold checkpoints `research_state/c21_ckpt_*`, artifacts `research_state/c21_*_20261117T064408Z.json`, log `research_state/c21_run_20261117T215941Z.log`). If no runner is alive, run `bash scripts/run_c21_detached_durable.sh` (invoke from a command line that does not itself contain the script name). Then run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py`. **Do not reduce draw counts, fabricate artifacts, relabel cross-venue, or commit unless explicitly asked.**

Full state, C21 spec, guardrails, and file map: `HANDOFF.md`.
