# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T12:03:58Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication, OKX + Binance UM perps done, MEXC next). C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE & RUNNING** — MEXC USDT-perp out-of-sample replication, PRE-REGISTERED (`c22_prereg_20261118T100126Z`), acquisition VIABLE (probe refreshed 11:03:58Z, 11/15 symbols ≥ $5M/24h), infrastructure built, **C22 RUNNER CREATED AND EXECUTING** (4 workers at ~96% CPU, fold 2023 in progress), battery PENDING (0/7 artifacts — heavy compute in progress).

**Verified (2026-11-18T12:03:58Z):** `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`; `scripts/probe_c22_venue_acquisition.py` → `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; `scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs green, MEXC cache 34 symbols + universe derived, 0/7 battery artifacts); `tests/test_c22_campaign_20261118.py` → 11 passed. **C22 RUNNER PROCESS ACTIVE** (PID 18746, 4 workers) launched 2026-11-18T12:05:00Z with `--jobs 4 --resume`. **SAME-RUN RECOVERY:** push/fetch failure RESOLVED — `git push origin main` succeeded, remote HEAD (6289d43) matches local.

**Next action (MONITOR → COMPLETE → VERIFY GATE):**
1. Check runner: `ps aux | grep run_c22_mexc_campaign` — if workers at high CPU, battery computing. If died, restart with `--resume` (checkpoints protect ≤1 fold loss).
2. Watch checkpoints: `ls -la research_state/c22_ckpt_mexc_*` — 4 folds = 4 checkpoints expected.
3. When process exits: `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → must print `C22 ACCEPTANCE: PASS` (token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; mexc verdict = consolidated; `is_hyperliquid_venue_data=false`).
4. If gate still PENDING: restart runner with `--resume` — skips completed folds via checkpoints.
5. Then stop and await explicit operator direction. Do NOT start same-data C23+ rerun without new prereg + new data + explicit authorization.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` ≠ `C22 ACCEPTANCE: PASS`, session NOT done — heavy execution (restart with `--resume` → complete folds → emit artifacts) mandatory until gate green. `PENDING` = work order, not completion.

**Expected outcome is honesty, not a GO:** given C1–C21, C22 likely `NO_GO`/`UNDERPOWERED` — a **success**. Report per-fold, per-venue, pooled numbers + power curve; never tune spec to chase GO. Full binding context/tokens: `HANDOFF.md`.

(End of file - total 15 lines)