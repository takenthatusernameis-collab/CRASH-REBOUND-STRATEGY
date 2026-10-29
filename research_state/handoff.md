# Durable Handoff (SINGLE SOURCE OF TRUTH)

**TIMESTAMP:** 2026-10-29T20:43:00Z
**REPO:** CRASH-REBOUND-STRATEGY
**PRIORITY:** HEAVY EXECUTION OF CRASH-REBOUND STRATEGY (diagnostics support only)

## CURRENT STATE
- **Tests:** 47/47 passing (`PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python3 -m pytest -q`)
- **Active Run:** #21 (40904974141) — **IN_PROGRESS**. Job `kilo` (123688873244), step 6 `Run general-purpose Kilo agent loop` in_progress since 19:41:59Z. Steps 1-5 OK, 7-9/18 pending. Timeout 360 min (~01:42Z Oct 30). Monitor running as bgp `bgp_18930588700153l0A72Z2j7jkH` (PID 3146).
- **Ledger:** 21 records in `research_state/workflow_run_diagnostics.jsonl` (runs #1-#21 captured)
- **Strategy:** Scaffolding in place (`src/strategy/{config,crash_rebound,risk}.py`, `src/data/loader.py`, `src/backtest/engine.py`, 7 test files, 47 tests). Smoke backtest in `research_state/backtest_smoke.json`. PDF present at root (`crash-rebound-strategy.pdf`).
- **Bottlenecks removed:** Generic `scripts/monitor_run.py <RUN_ID> [POLL] [TIMEOUT_MIN]` and `scripts/finalize_run.py <RUN_ID>` (no per-run hardcoded copies). Push gate: only regular files allowed (`.github/workflows` blocked by token permissions).

## BOTTLENECKS / GUARDS (MANDATORY)
- **NEVER cancel run #21** — `gh run cancel` returns 403 (insufficient scope). Do not force-push. Only push regular files (`research_state/*`, `src/*`, `tests/*`, `scripts/*`).
- **Tool-shape guard:** `kilo_edit_tool_invalid_arguments` is known (aborts after 3 consecutive invalid edits). Always supply complete `filePath`/`oldString`/`newString`. Verify with `Read`/`grep` before re-editing. Never repeat malformed edit 3x.
- **Tests must stay green.** Run `PYTHONPATH=/home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY python3 -m pytest -q` before ending turn.

## IMMEDIATE INITIAL TASK (EXECUTE IN ORDER — NO IDLE-WATCHING)

**OBJECTIVE:** Push heavy strategy implementation forward while monitoring run #21. Diagnostics are support only.

### STEP 1: ASSESS ACTIVE RUN (GATE)
```bash
gh run view 40904974141 --json status,conclusion,jobs
```
- If **completed (success/failure)**: run `python3 scripts/finalize_run.py 40904974141`, verify tests pass, commit/push `research_state/workflow_run_diagnostics.jsonl` + `research_state/handoff.md` (regular files only). Update this handoff with new timestamp/status/test count.
- If **in_progress**: do NOT cancel. Continue with Steps 2-5 in parallel. Monitor via `python3 scripts/monitor_run.py 40904974141 30 360` if needed (already running).

### STEP 2: EXTRACT CONCRETE RULES FROM PDF (HEAVY)
- PDF is image-heavy/rendered. Parse/extract what you can (try OCR-like approaches: `pdftotext`, `pdfinfo`, `poppler-utils`, or read raw streams). Update `research_state/strategy_spec.md` with **"Resolved (from PDF)"** vs **"Assumed (inferred)"** sections.
- Resolve at minimum: crash threshold (% drop), rebound confirmation (criteria/timing), universe, entry window, exit (target/stop/time), regime/filter, position sizing/risk params.

### STEP 3: WIRE RISK CONTROLS INTO BACKTESTER (HEAVY)
- Integrate `src/strategy/risk.py` (`DailyRiskState`, `check_position`, `check_daily_loss_halt`) into `src/backtest/engine.py`. Before entry: check max positions and daily-loss halt. On open/close: update risk state. Gate trades via per-trade RiskCheck.
- Add tests: position blocked at `max_positions`, halt after daily-loss breach, new day resets state.
- Keep all params from `StrategyConfig` (no magic numbers).

### STEP 4: MULTI-SYMBOL BACKTEST + FIXTURES (HEAVY)
- Add fixtures for ≥3 symbols (SPY/QQQ/IWM) covering crash-then-rebound and no-trade cases in `src/data/` or tests.
- Backtest with `DEFAULT_CONFIG`, log per-symbol + aggregate PnL/R/exit reasons to `research_state/backtest_smoke.json`.
- Add test asserting aggregate metrics structure and losing fixtures produce negative PnL/stopped exits.

### STEP 5: EXPAND TESTS + HARDEN (HEAVY, MANDATORY)
- Add tests for: stopped-out (stop hit → `exit_reason='stopped'`), entry_next_bar on/off, slippage/commission sweep. Grow test count meaningfully beyond 47.
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
