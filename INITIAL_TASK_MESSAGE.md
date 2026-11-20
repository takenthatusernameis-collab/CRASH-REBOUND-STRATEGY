# Initial Task Message — CRASH-REBOUND-STRATEGY (2026-11-20T22:30:36Z)

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.
**Single durable handoff:** `HANDOFF.md`. `AGENT_HANDOFF.md` is a pointer only.

**Live status (verified 2026-11-20T22:30:36Z via `bash scripts/status_c25.sh` + `bash scripts/eta_c25.sh` + `bash scripts/check_c25_anchor.sh`):**

- `C25-T1` cost/funding fidelity: **RUNNER ALIVE & COMPUTING** (PID 3391, parent 3386, 4 workers R-state, resumed ~21:24Z, elapsed 01:06:14)
- Cells: **5/56 real complete** (`cost_base/okx/2023` pnl +34,420.88; `cost_base/okx/2024` pnl +1,621.97; `cost_base/okx/2025` pnl +4,721.66; `cost_base/okx/2026YTD` pnl +5,166.77; `cost_base/binance_um/2023` pnl +165.87), **51 pending**, 8 okx funding skips (`UNAVAILABLE_FUNDING`)
- Gate: `C25 ACCEPTANCE: PENDING` (59 missing cells); Anchor: `ANCHOR: INCOMPLETE` (5/16 cost_base checked: okx EXACT 28,469.71, binance_um/mexc/bitget INCOMPLETE, **no MISMATCH**)
- ETA: **~2026-11-24T01:53:43Z (±30%)**; 4-core box saturated; in-flight cell `cost_base/binance_um/2024` elapsed 1.13 h; next cells: cost_base/binance_um/2024, cost_base/binance_um/2025, cost_base/binance_um/2026YTD, cost_base/mexc/2023
- `C26-T1` path/funding fidelity: **BUILT, blocked on C25 PASS** (`C26 ACCEPTANCE: PENDING`, 64 missing cells, no path anchor)
- `C27-T1` venue replication: **STAGED, blocked on C26 PASS** (probe + prereg written, launch gated)
- Binding queue: `C24 (PASS) → C25 (live) → C26 (BUILT, blocked on C25 PASS) → C27 (probe + prereg staged, blocked on C26 PASS)`
- Tests: **1100 passed, 1 skipped** (46.1 s — do not rerun pytest while runner is alive; it competes for 4 saturated cores)

---

## DO EXACTLY THIS, IN ORDER — DO NOT SKIP, REORDER, OR "IMPROVE":

### 1. Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`
Those two commands are ground truth. Never trust a PID or log path written in any file. Never assemble your own `ps`/`ls`/log chain.

### 2. If `RUNNER: ALIVE`:
- Do not relaunch, do not kill, do not resume, do not start any C26/C27 cell, do not add any CPU work.
- Run `bash scripts/check_c25_anchor.sh` (must stay `ANCHOR: INCOMPLETE` / `ANCHOR: OK`; **`ANCHOR: MISMATCH` is a P0 integrity stop — record evidence, fix cause, resume once**).
- Then **suspend with `schedule_wakeup` (8 h)** using the monitoring protocol prompt below. Do not burn turns polling.

### 3. If `RUNNER: NOT ALIVE` and gate is `PENDING`:
- Fix the failure cause, then resume **exactly once** with:
  `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`
- Never resume twice for the same failure. Never `nohup`/`setsid` it yourself.

### 4. If gate prints `C25 ACCEPTANCE: FAIL`:
- Fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

### 5. On `C25 ACCEPTANCE: PASS` (same session):
- Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
- State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`.
- Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry.
- Then durably launch C26-T1: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; verify with `bash scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`.

### 6. On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):
- Run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`
- Confirm `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha pinned) matches the probe verdict
- Then durably launch C27. If probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.

---

## NO-AVOIDANCE RULE (BINDING):
`C24 → C25 → C26 → C27` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts (20k/2k/2k/2k floors), or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker — it means the heavy battery must keep running. **C25 is the live focus campaign; C26 is the mandatory same-session successor on C25 PASS; C27 is the mandatory same-session successor on C26 PASS.** "No authorized work" is never a truthful state while any gate in this chain is PENDING.

---

## BOTTLENECK REGISTER (CURRENT):
The only remaining bottleneck is **compute** (20k/20k/2k draw floors, prereg-bound, not reducible; 51 cells × ~3.6 h/cell ≈ 184 h on saturated 4 cores). It is **not fixable mid-run** — restarting gambles the campaign and a bit-identical claim cannot be proven mid-flight. C26/C27 are legitimately blocked on the C25 gate by the sequential adjudication chain; that is by design, **not an inefficiency to workaround**. No competing CPU work (extra tests, probes, notebooks) may run while the C25 runner is alive. No removable bottleneck exists — progress continues only by letting C25 run to its gate.

---

## MONITORING PROTOCOL (USE THIS, NEVER POLL):
One bounded read (`bash scripts/eta_c25.sh`), then suspend with exactly:

```
schedule_wakeup delay=8h reason="C25 tick" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume exactly once with background_process start command='bash scripts/run_c25_durable.sh' persistent=true. If the gate is C25 ACCEPTANCE: PASS, execute the C25-PASS checklist and launch C26 in this same session. If check_c25_anchor.sh prints ANCHOR: MISMATCH, stop and record evidence. Otherwise update HANDOFF.md only if state materially changed and schedule the next 8h wakeup."
```

- 8 h cadence is correct at ~3.6 h/cell (≈2 cells per wake). Shorter adds nothing.
- If checkpoint count is unchanged across **two consecutive 8 h wakes** while runner is ALIVE, treat as "cell in permutation" (prints nothing) and keep waiting — do **not** conclude stuck and do **not** kill.
- One wake in four should additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (74 s) to catch wiring rot. Do not run it every wake; it competes with the 4 cores.

---

## KEY FILES:
- Handoff/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261120T212421Z.log`
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`
- C27: `scripts/probe_c27_venue_acquisition.py`, `research_state/c27_prereg_20261119T215721Z.{json,md}`
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`
