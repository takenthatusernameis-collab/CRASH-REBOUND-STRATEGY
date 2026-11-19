# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T22:35:23Z)

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.

**Current position:** C1–C20 closed `NO_GO`. C21/C22/C23-T1 complete (`PASS`), consolidated `NO_GO`. **C24-T1 complete: `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled **+144,651.69**, CI95 [+117,408.41, +173,074.50], prob>0 = 1.0, prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded). **C25-T1 in flight** (1/56 real cells). **C26-T1 built, not launched.**

**VERIFIED LIVE STATE (re-verify before acting):**
- **C25 RUNNER: ALIVE.** Parent PID **3901** (`scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`), started **17:24:18Z**, 4 draw workers, persistent launcher `scripts/run_c25_durable.sh`.
- **Cells:** `cost_base 1/16`, `cost_taker 0/16`, `cost_taker_funding 0/16`, `cost_stress 0/16`; 1 real cell DONE (`cost_base/okx/2023`, pnl **+34,420.88**, perm_p **0.335**, placebo p_ge **0.0705**, ckpt written 21:00:41Z). `cost_base/okx/2024` in flight.
- **Gate:** `C25 ACCEPTANCE: PENDING` (63 missing cells). `C26 ACCEPTANCE: PENDING` (blocked on C25).
- **Tests:** `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c24_campaign.py tests/test_c25_campaign.py tests/test_c26_campaign.py -q` → **24 passed** (re-verified).
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited, 6 verdict artifacts present. **Do not relaunch.**
- `.venv` bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`. Only run `bash scripts/bootstrap_env.sh` if `bin/python` is missing.

---

**DO EXACTLY THIS, IN ORDER — DO NOT SKIP, DO NOT REORDER, DO NOT "IMPROVE" IT:**

1. **Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.** Those two commands are the truth. Do not assemble your own `ps`/`ls`/log chain.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26 cell. If you want to make progress, do one of:
   - `bash scripts/check_c25_anchor.sh` → must eventually print `ANCHOR: OK`. If it prints `ANCHOR: MISMATCH`, that is a P0 integrity stop: record the evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg.
   - then **suspend the session with `schedule_wakeup` (6–12 h, see protocol below)** instead of burning turns polling.

3. **If `RUNNER: NOT ALIVE` and the gate is `PENDING`:** fix the failure cause first, then resume **exactly once**:
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (its duplicate guard no-ops if a runner is already up). Never resume twice for the same failure.

4. **If the gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (do all of this in that same session):**
   a. Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
   b. State, verbatim, `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cite `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Never claim per-trade funding (that is C26).
   c. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Never zero-fill, proxy, or retry it.
   d. **Immediately and durably launch C26-T1:** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then verify with `scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`. Do not idle, do not claim "no authorized work", do not do a same-data parameter search.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts, or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker: it means the heavy battery must keep running.

---

## MONITORING PROTOCOL FOR A MULTI-DAY RUN (use this instead of polling)

- A session must never hold a turn open for hours, never `sleep` past the ~900 s idle timeout, and never poll in a loop.
- Use one bounded read (`bash scripts/eta_c25.sh`), then schedule and suspend:
  `schedule_wakeup delay=8h reason="C25 tick" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume once with bash scripts/run_c25_durable.sh (persistent). If anchor shows MISMATCH, stop and record. Otherwise check the anchor, update HANDOFF.md only if the state materially changed, and schedule the next 8h wakeup."`
- 6–12 h intervals are appropriate; each cell takes ~3.6 h, so shorter intervals add nothing.
- If a checkpoint count has not changed across two consecutive 8 h wakes while the runner is ALIVE, treat it as "cell in permutation" (that stage emits no log lines) and keep waiting — do **not** conclude the runner is stuck.

---

## CAMPAIGNS (reference)

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)
**Prereg (frozen):** `research_state/c25_prereg_20261119T045500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, sha256 `b1e22b36d074eed3aa2577edccd744343d1e8673c102257b7890a554504f2b6e`.
**Arms:** `cost_base` (FIDELITY_ANCHOR), `cost_taker`, `cost_taker_funding` (**PRIMARY**), `cost_stress`. 4 venues × 4 folds × 20k/20k/2k.
**Anchor rule:** `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 → `COST_ANCHOR_REPRODUCED` else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`.
**Decision rules:** `C25_REOPENS_C1_C24` requires, under `cost_taker_funding`: pooled > 0 AND CI95 lower > 0 AND ≥1 BH survivor in the 16-test family AND ≥3/4 folds positive AND ≥3/4 venues positive. Otherwise `C25_NO_GO_ROBUST_TO_COST`.
**Funding inputs (real):** binance_um 0.0005717 %/h; mexc 0.0004581 %/h; bitget 0.0007211 %/h. `okx` → `UNAVAILABLE_FUNDING`.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)
**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags `intrabar_adverse_first` / `per_trade_funding` exist with default `False`. **No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 → `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`.

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (NOT BUILT — MANDATORY SUCCESSOR TO C26)
**Status:** definition only. After `C26 ACCEPTANCE: PASS`, same session must: (1) write and run a stage-0 acquisition probe for a never-used USDT-perp venue (Bybit primary), (2) write `c27_prereg_<TS>.{json,md}` with `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE` **before any compute**, (3) durably launch the campaign. If no new venue is viable, the only legitimate alternative is a new pre-registered hypothesis on new data — never a same-data rerun or frozen-signal parameter search.

---

## GUARDRAILS (never violate)
- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C27).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22/C23/C24/C25/C26 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cites `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code path.**
- **Status first:** `bash scripts/status_c25.sh` before any C25 action.
- **Do not kill or duplicate the persistent runner.** Long campaigns must be launched through the harness background-process tool with `persistent=true`.
- **No long foreground sleep** that hits the ~900 s idle timeout: use `schedule_wakeup` or bounded reads.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a new campaign.
- Do not commit unless explicitly asked.
- Preserve literal gate tokens.

---

## KEY FILES
- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` (this file), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`.
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261119T172418Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`.