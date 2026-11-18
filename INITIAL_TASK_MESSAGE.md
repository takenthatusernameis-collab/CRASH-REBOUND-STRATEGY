# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T12:22:19Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication, OKX + Binance UM perps done, MEXC replication pending). C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE, PRE-REGISTERED, AND NOT RUNNING** — MEXC USDT-perp out-of-sample replication (`c22_prereg_20261118T100126Z`), acquisition VIABLE, cache/universe/runner/gate ready, but **0/7 battery artifacts and 0/4 checkpoints** at 12:22:19Z.

**Verified (2026-11-18T12:22:19Z):** `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`; `scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs green, MEXC cache 34 symbols + universe derived, 0/7 artifacts); `tests/test_c22_campaign_20261118.py` → 11 passed. No `run_c22_mexc_campaign.py` process exists; PID 18746 and the prior "RUNNING" claim are stale and superseded.

**Next action (LAUNCH → COMPLETE → VERIFY GATE):**
1. Run `bash scripts/run_c22_detached_durable.sh` from repo root. It launches `--jobs 4 --resume`, refuses duplicates, and prints a PID + `research_state/c22_run_<TS>.log`.
2. Tail the log and confirm the process/checkpoints: four folds (`2023`, `2024`, `2025`, `2026YTD`) → `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json`.
3. When `C22 COMPLETE` appears or the process exits, run `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py`; it must print `C22 ACCEPTANCE: PASS` (token ∈ {`STABLE_POSITIVE_SUBSET`, `NO_GO`, `UNDERPOWERED`}; mexc verdict = consolidated; `is_hyperliquid_venue_data=false`).
4. If gate is still PENDING and no runner is alive, immediately rerun the launcher and continue until PASS.
5. After PASS, report per-fold, per-venue, and pooled numbers plus the power curve, then await explicit operator direction. Do NOT start a same-data C23+ rerun without new prereg + new data + explicit authorization.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` ≠ `C22 ACCEPTANCE: PASS`, the session is NOT done — launch/resume the detached runner and complete the full MEXC 4-fold 20k/20k/2k battery until the gate is green. `PENDING` = work order, not completion.

**Expected outcome is honesty, not a GO:** given C1–C21, C22 likely `NO_GO`/`UNDERPOWERED` — a **success**. Report per-fold, per-venue, pooled numbers + power curve; never tune the spec to chase GO. Full binding context/tokens: `HANDOFF.md`.

(End of file - total 15 lines)