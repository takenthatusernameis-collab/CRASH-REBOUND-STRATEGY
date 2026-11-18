# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T13:42:27Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication, OKX + Binance UM perps done, MEXC replication in progress). C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`). **C22-T1 ACTIVE, PRE-REGISTERED, RUNNING (durable)** — MEXC USDT-perp out-of-sample replication (`c22_prereg_20261118T100126Z`), acquisition/cache/universe ready, heavy 4-fold 20k/20k/2k battery in progress; gate still `PENDING`.

**Verified live (2026-11-18T13:42:27Z):** `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`; `scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PENDING` (prereqs green, 0/7 battery artifacts, 0/4 checkpoints; timestamped artifacts present: `c22_prereg_20261118T100126Z.json`, `c22_venue_acquisition_probe_20261118T100126Z.json`). **Runner alive:** PID **21734** (+workers **27728–27731**, R, etime ~01:16) running `scripts/run_c22_mexc_campaign.py --jobs 4 --resume`; log `research_state/c22_run_20261118T122533Z.log` (fold 2023 in progress: census=325 events, 110 signal_pass, 25 trades, PnL=+30,599; fast-path validated). No duplicate runner; do not relaunch on log silence.

**Runtime expectation (measured):** 20,000-draw episode-block permutation dominates per-fold cost (C21 reference 130–746s/fold; C22 single-venue ~1–4h total). Fold 2023 has been in its episode permutation well over an hour with no checkpoint yet — EXPECTED. First checkpoint `c22_ckpt_mexc_2023_20261118T100126Z.json` appears only after the full fold completes.

**Next action (MONITOR/RESUME → COMPLETE → VERIFY GATE):**
1. `ps -eo pid,etime,time,stat,cmd | grep '[r]un_c22_mexc_campaign.py'` — if alive, monitor only (no duplicate). Tail `research_state/c22_run_20261118T122533Z.log`; watch checkpoints `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json` (`2023`,`2024`,`2025`,`2026YTD`).
2. If no runner is alive and gate is `PENDING`, immediately run `bash scripts/run_c22_detached_durable.sh` (`--resume`, duplicate-guarded) and continue until completion.
3. When complete / `C22 COMPLETE` logged / 7 battery artifacts present: run `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` — must print `C22 ACCEPTANCE: PASS` (token ∈ {`STABLE_POSITIVE_SUBSET`,`NO_GO`,`UNDERPOWERED`}; mexc verdict = consolidated; `is_hyperliquid_venue_data=false`).
4. After PASS, report per-fold, per-venue, and pooled numbers plus the power curve, then await explicit operator direction. No same-data C23+ without new prereg + new data + explicit authorization.

**No-avoidance rule (binding):** if `verify_c22_focus_campaign.py` ≠ `C22 ACCEPTANCE: PASS`, the session is NOT done — keep a runner active and drive the full MEXC 4-fold 20k/20k/2k battery to completion until gate is green. `PENDING` = work order, not completion. Monitoring a live runner is acceptable; abandoning a non-PASS state is not.

**Expected outcome is honesty, not a GO:** likely `NO_GO`/`UNDERPOWERED` — a **success**. Report per-fold, per-venue, pooled numbers + power curve; never tune the spec to chase GO. Full binding context/tokens: `HANDOFF.md`.
