# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T23:03:24Z — C21 MID-COMPUTE, DO NOT DUPLICATE)

**Authoritative durable handoff:** `HANDOFF.md` — this file is a pointer only; do not maintain a second source of truth.

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data (OKX + Binance UM).
**State:** C1–C20 CLOSED & CERTIFIED `NO_GO` (pytest `1047 passed, 1 skipped`; session_gate `21/21 checks passed`; verify_campaign_evidence `EVIDENCE VERIFIED`). C21-T1 is the **only** open binding work.

**BOTTOM LINE UP FRONT (verified 2026-11-17T23:03:24Z):**
- Canonical C21 runner **ACTIVE**: PID 21945 (`python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume`), ppid 1 (detached), 4 workers R-state all ~90–95% CPU, ~1 hr wall, system load avg ~6.0; OKX fold 2023 complete (`1/8` checkpoints) and OKX fold 2024 computing. **0/12 required artifacts**. `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (expected until complete).
- **DO NOT START A SECOND RUNNER** — the live process is computing on all 4 cores.
- **Binding no-avoidance campaign:** C21-T1 is the sole open campaign. Continue heavy execution until `C21 ACCEPTANCE: PASS`; no planning-only, artifact-free monitoring, draw-count reduction, or C22+ relabeling is accepted.
- **Bottleneck removed (prior session):** strata permutations now 4-way pooled + fail-closed fast-path validation; all 20k/20k/2k draws preserved (~4x faster, ~5–6 hr ETA). No new bottleneck observed — runner is compute-bound and progressing on all 4 cores.

**Next action:** monitor the live runner to `C21 ACCEPTANCE: PASS` (per-fold checkpoints `research_state/c21_ckpt_*`, artifacts `research_state/c21_*_20261117T064408Z.json`, log `research_state/c21_run_20261117T215941Z.log`). If no runner is alive, run `bash scripts/run_c21_detached_durable.sh` (invoke from a command line that does not itself contain the script name). Then run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` (`1047 passed, 1 skipped`) and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py` (`21/21 checks passed`). **Do not reduce draw counts, fabricate artifacts, relabel cross-venue, or commit unless explicitly asked.**

Full state, C21 spec, guardrails, and file map: `HANDOFF.md`.

(End of file - total 15 lines)