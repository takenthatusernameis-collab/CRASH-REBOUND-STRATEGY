# Durable Handoff (SINGLE SOURCE OF TRUTH)

**TIMESTAMP:** 2026-10-29T20:44:00Z
**REPO:** CRASH-REBOUND-STRATEGY
**PRIORITY:** HEAVY EXECUTION OF CRASH-REBOUND STRATEGY (diagnostics support only)

## CURRENT STATE
- **Tests:** 51/51 passing (`PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python3 -m pytest -q`). Grew 47→51 this session.
- **Active Run:** #21 (40904974141) — **IN_PROGRESS**. Job `kilo` (123688873244), step 6 `Run general-purpose Kilo agent loop` in_progress since 19:41:59Z. Steps 1-5 OK, 7-9/18 pending. Timeout 360 min (~01:42Z Oct 30). Monitor running as bgp PID 3176 (`python3 scripts/monitor_run.py 40904974141 30 360`).
- **Ledger:** 21 records in `research_state/workflow_run_diagnostics.jsonl` (runs #1-#21 captured). Last captured: run 40845157948 (success, completed 19:41:45Z). Run #21 (40904974141) NOT yet in ledger — still active.
- **Strategy:** Scaffolding + risk now wired into backtester (`src/backtest/engine.py` integrates `DailyRiskState`: pre-entry max_positions/daily-loss gate, `apply_trade` on open/close, `time_exit_max_bars`). `src/strategy/{config,crash_rebound,risk}.py`, `src/data/loader.py`, 7 test files, 51 tests. Smoke backtest in `research_state/backtest_smoke.json`. PDF present at root (`crash-rebound-strategy.pdf`, image-heavy, not yet parsed).
- **Working tree:** modified `src/backtest/engine.py` and `tests/test_crash_rebound_strategy.py` (risk wiring + 4 new tests). **Uncommitted.** Next session must commit/push regular files only (see guards).
- **Bottlenecks removed:** Generic `scripts/monitor_run.py <RUN_ID> [POLL] [TIMEOUT_MIN]` and `scripts/finalize_run.py <RUN_ID>` (no per-run hardcoded copies). Push gate: only regular files allowed (`.github/workflows` blocked by token permissions).

## BOTTLENECKS / GUARDS (MANDATORY)
- **NEVER cancel run #21** — `gh run cancel` returns 403 (insufficient scope). Do not force-push. Only push regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
- **Tool-shape guard:** `kilo_edit_tool_invalid_arguments` is known (aborts after 3 consecutive invalid edits). Always supply complete `filePath`/`oldString`/`newString`. Verify with `Read`/`grep` before re-editing. Never repeat a malformed edit 3x.
- **Tests must stay green.** Run `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python3 -m pytest -q` before ending turn.
- **PDF bottleneck:** `crash-rebound-strategy.pdf` is image-heavy/rendered; simple text extraction fails. Try `pdftotext`, `pdfinfo`/`poppler-utils`, or `pymupdf`/`fitz` OCR-like parsing. Do not get stuck — mark parameters **"Resolved (from PDF)"** vs **"Assumed (inferred)"** and keep implementing with assumptions flagged.

## IMMEDIATE INITIAL TASK (EXECUTE IN ORDER — NO IDLE-WATCHING)

**OBJECTIVE:** Push heavy strategy implementation forward while monitoring run #21. Diagnostics are support only. The repo name is the directive — execute the crash-rebound strategy heavily.

### STEP 1: ASSESS ACTIVE RUN (GATE)
```bash
gh run view 40904974141 --json status,conclusion,jobs
```
- If **completed (success/failure)**: run `python3 scripts/finalize_run.py 40904974141`, verify tests pass, commit/push `research_state/workflow_run_diagnostics.jsonl` + `research_state/handoff.md` + working tree (regular files only). Update this handoff with new timestamp/status/test count.
- If **in_progress**: do NOT cancel. Continue with Steps 2-5 in parallel. Monitor via `python3 scripts/monitor_run.py 40904974141 30 360` (PID 3176 already running).

### STEP 2: EXTRACT CONCRETE RULES FROM PDF (HEAVY)
- Parse `crash-rebound-strategy.pdf` (try `pdftotext`, `pdfinfo`, `poppler-utils`, `pymupdf`/`fitz`). Update `research_state/strategy_spec.md` with **"Resolved (from PDF)"** vs **"Assumed (inferred)"** sections.
- Resolve at minimum: crash threshold (% drop), rebound confirmation (criteria/timing), universe, entry window, exit (target/stop/time), regime/filter, position sizing/risk params.

### STEP 3: WIRE RISK CONTROLS INTO BACKTESTER (HEAVY) — PARTIALLY DONE
- `src/backtest/engine.py` now gates entry via `DailyRiskState.check_position` (max positions, daily-loss halt) and calls `apply_trade` on open/close; `time_exit_max_bars` enforced. `config.time_exit_max_bars` wired.
- Still to do: ensure per-trade RiskCheck returned by `check_position` gates size; add `stop_atr_mult`-based stop (config-driven, no magic numbers); verify `risk.py` and `config.py` `RiskState`/`DailyRiskState` are not duplicated/divergent — consolidate to one risk state.
- Add tests: position blocked at `max_positions` (done), halt after daily-loss breach (done), new day resets state (done), ATR-multiple stop.

### STEP 4: MULTI-SYMBOL BACKTEST + FIXTURES (HEAVY)
- Add fixtures for ≥3 symbols (SPY/QQQ/IWM) covering crash-then-rebound and no-trade cases in `src/data/` or tests.
- Backtest with `DEFAULT_CONFIG`, log per-symbol + aggregate PnL/R/exit reasons to `research_state/backtest_smoke.json`.
- Add test asserting aggregate metrics structure and losing fixtures produce negative PnL/stopped exits.

### STEP 5: EXPAND TESTS + HARDEN (HEAVY, MANDATORY)
- Add tests for: stopped-out (`exit_reason='stopped'`), `entry_next_bar` on/off, slippage/commission sweep. Grow test count meaningfully beyond 51.
- **Run all tests:** `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python3 -m pytest -q` — must be green.
- Update `research_state/backtest_smoke.json` with concrete multi-symbol results.

## MANDATORY END-OF-TURN
Before ending this session, **UPDATE THIS "Durable Handoff"** with:
- New timestamp (current UTC)
- Run #21 status (completed/in_progress + conclusion if done)
- Monitor state (running/stopped + bgp/PID)
- What was built/tested (files changed, test count before→after)
- Blockers (if any)
- Concrete next steps for the following agent (specific, actionable, heavy)

**RULE:** Never stop at diagnostics. Every session must produce material strategy/backtest/test progress. The repo name is the directive — execute the crash-rebound strategy heavily.
