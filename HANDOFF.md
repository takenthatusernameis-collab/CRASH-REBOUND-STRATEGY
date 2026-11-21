# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-21T02:30:48Z · **Re-verified / updated (UTC):** 2026-11-21T04:16:29Z (this session ran `status_c25.sh`, `eta_c25.sh`, `check_c25_anchor.sh`, `cancel_wakeup list`; runner **ALIVE** — python `run_c25_cost_fidelity_campaign.py --jobs 4 --resume` worker PID 3103 under parent 3098, durable shell PID 3040, 4 rotating draw workers (PIDs change per cell; `status_c25.sh` is ground truth), log `research_state/c25_run_20261121T031415Z.log`; **6/56 real cells**, ETA ~**2026-11-24T13:09:00Z**, `ANCHOR: INCOMPLETE` with no `MISMATCH`, `C25 ACCEPTANCE: PENDING`; **no wakeup existed for this session — re-armed with `schedule_wakeup delay=8h` → `wku_1fc50ce26001jgnAXtRRcJPFEr` due 2026-11-21T12:15:16Z**) · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.

**This is the single durable handoff.** `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are pointers only. `README.md` points here. Any session that writes campaign state into a second file recreates the state-drift failure this removes.

**ONE-LINE STATUS (verified 2026-11-21T04:16:29Z):** `C25-T1` cost/funding fidelity is **RUNNER ALIVE & COMPUTING** (python worker PID 3103 under parent 3098, durable shell PID 3040, 4 draw workers; `.venv/bin/python` restored via `scripts/bootstrap_env.sh` after the runner died at ~03:13Z mid-cell `cost_base/binance_um/2025` — that cell now re-runs from checkpoint). **6/56 real inference cells complete** (`cost_base/okx/2023` pnl +34,420.88; `cost_base/okx/2024` pnl +1,621.97; `cost_base/okx/2025` pnl +4,721.66; `cost_base/okx/2026YTD` pnl +5,166.77; `cost_base/binance_um/2023` pnl +165.87; `cost_base/binance_um/2024` pnl +17,202.49, boot=20000 perm=None placebo=2000). **50 remaining.** Gate `C25 ACCEPTANCE: PENDING` (58 missing cells; verdict artifacts written only after all cells complete). Anchor `ANCHOR: INCOMPLETE` (6/16 cost_base cells checked; okx EXACT 28,469.71; binance_um 2/4 INCOMPLETE, mexc/bitget 0/4 INCOMPLETE — no MISMATCH). ETA ~**2026-11-24T13:09:00Z (±30%; 4-core box, median model n=6)**. **Wakeup armed for this session (`cancel_wakeup list` non-empty): `wku_1fc541049001la8nDar6phUqCM` due 2026-11-21T12:18:50Z carrying C25 tick + resume-once + C26-on-PASS protocol.** **C28 (next focus campaign) is BUILT and gate-held** (`c28_prereg_20261121T013400Z.{json,md}`, direction c28-a; NOT launched, `C28 ACCEPTANCE: PENDING`, runner now hard-refuses until C27 PASS). **C29 is STAGED** (prereg + launcher + status + gate stubbed; not launched; blocked on C28 PASS). **DO NOT RELAUNCH. DO NOT KILL. DO NOT REORDER ARMS. DO NOT START ANY C26/C27/C28 CELL.**

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-21T04:16:29Z)

**Repository priority:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence. This repository's live priority is the C25 cost/funding-fidelity campaign; do not substitute unrelated work.

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

1. **Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.** Those two commands are ground truth. Never trust a PID or log path written in any file. Never assemble your own `ps`/`ls`/log chain.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26/C27 cell, do not add any CPU work. Run `bash scripts/check_c25_anchor.sh` (must stay `ANCHOR: INCOMPLETE` / `ANCHOR: OK`; `ANCHOR: MISMATCH` is a P0 integrity stop — record evidence, fix cause, resume once). Then **suspend with `schedule_wakeup` (8 h)** using the monitoring protocol prompt (no wakeup is currently armed for this session — `cancel_wakeup list` was empty at 2026-11-21T04:16:29Z; re-arm immediately). Do not burn turns polling.

3. **If `RUNNER: NOT ALIVE` and gate is `PENDING`:** fix the failure cause, then resume **exactly once** with `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`. Never resume twice for the same failure. Never `nohup`/`setsid` it yourself.

4. **If gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (same session):** deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`). State verbatim `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION` — never zero-fill, proxy, or retry. Then durably launch C26-T1: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; verify with `bash scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** run `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`; confirm `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha pinned) matches the probe verdict; then durably launch C27. If probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.

7. **On `C27 ACCEPTANCE: PASS` (same session, mandatory successor — the queue never dries out):** C28 is **already BUILT** (no need to author a new prereg): direction `c28-a` (Portfolio-Level Cross-Venue Capital Allocation & Correlation Fidelity), prereg `research_state/c28_prereg_20261121T013400Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha-pinned). Verify it with `bash scripts/status_c28.sh --direction c28-a` (must show `PRE_REGISTERED_BEFORE_COMPUTE` + `C28 ACCEPTANCE: PENDING`) and `PYTHONPATH=. .venv/bin/python scripts/verify_c28_focus_campaign.py --direction c28-a`. Then durably launch: `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`. The C28 runner now **hard-refuses** (SystemExit, exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — so if you see that refusal, C27 has not actually PASSed; fix C27 first, do not force. **C28 may NOT run any cell until C27 ACCEPTANCE: PASS** (anchor = C25/C26 primary-arm venue_totals must exist). On C28 PASS, open the **next focus campaign (C29)** with a fresh `PRE_REGISTERED_BEFORE_COMPUTE` prereg (sha-pinned, anchored on the completed C24–C28 evidence). Candidate heavy directions — choose the best-powered by realized evidence, preregister, durably launch, never idle: strict temporal out-of-sample holdout on the newest never-scored window; execution-realism stress (latency, partial fills, empirical slippage distribution); signal-mechanics robustness (parameter-frozen, structure-preserving perturbations, never a frozen-signal parameter search). Each requires new data manifest + prereg + anchor verification against the prior primary arm before any inference; **never** a same-data rerun, frozen-signal parameter search, or reduced draw count (floors hold). If no new direction is viable, preregister a **new hypothesis on new data** — "no authorized work" is never acceptable while the strategy chain is incomplete.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27 → C28 → C29+` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts (20k/2k/2k/2k floors), or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker — it means the heavy battery must keep running. **C25 is the live focus campaign; C26 is the mandatory same-session successor on C25 PASS; C27 is the mandatory same-session successor on C26 PASS; C28 (direction c28-a, already built) is the mandatory same-session successor on C27 PASS; C29 is the mandatory successor on C28 PASS.** "No authorized work" is never a truthful state while any gate in this chain is PENDING or while the strategy adjudication chain is incomplete.

---

## VERIFIED LIVE STATE — 2026-11-21T04:16:29Z

Re-verify before acting; this block is stale the moment you read it. Read-only commands, in order:

```
bash scripts/status_c25.sh              # runner + per-cell + artifacts + gate  (ground truth)
bash scripts/eta_c25.sh                 # progress, per-cell cost, ETA
bash scripts/check_c25_anchor.sh        # early cost_base vs C24 d15 anchor
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
bash scripts/status_c28.sh --direction c28-a   # C28 (built, gate-held; PENDING until C27 PASS)
PYTHONPATH=. .venv/bin/python scripts/verify_c28_focus_campaign.py --direction c28-a
```

Observed at verification time (2026-11-21T04:16:29Z):

- **C25 RUNNER: ALIVE (re-verified 2026-11-21T04:16:29Z).** `bash scripts/status_c25.sh` prints `RUNNER: ALIVE`: python `scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume` worker PID **3103** under parent **3098**, durable shell PID **3040**, 4 draw workers (PIDs rotate per cell — `status_c25.sh` is ground truth), launched through the harness background-process runner (`persistent=true`, id `bgp_1fc18ec62001OS15zZ5B7pjpf0`), teeing to `research_state/c25_run_20261121T031415Z.log`. The runner previously died ~03:13Z mid-cell `cost_base/binance_um/2025` due to missing `.venv/bin/python` (fixed with `bash scripts/bootstrap_env.sh`); it now resumes from checkpoint and `.venv/bin/python` is present again. Whatever `status_c25.sh` prints is ground truth — never trust a PID written in this file.
- **Cells:** `cost_base 6/16` (okx/2023 pnl +34,420.88; okx/2024 pnl +1,621.97; okx/2025 pnl +4,721.66; okx/2026YTD pnl +5,166.77; binance_um/2023 pnl +165.87; binance_um/2024 pnl +17,202.49, boot=20000 perm=None placebo=2000), `cost_taker 0/16`, `cost_taker_funding 0/16`, `cost_stress 0/16`; 6 real cells DONE, 50 remaining, 8 okx funding skips (`UNAVAILABLE_FUNDING`). Next cells: `cost_base/binance_um/2025`, `cost_base/binance_um/2026YTD`, `cost_base/mexc/2023`, `cost_base/mexc/2024`.
- **ETA:** `eta_c25.sh` → 50 real cells left, median **1.44 h** permutation per cell → **80.9 h ≈ 3.4 days → ~2026-11-24T13:09:00Z (±30%)**. The 4-core box is saturated; no mid-run acceleration, restart, or extra CPU work is permitted while the runner is alive (guardrails).
- **Anchor:** `ANCHOR: INCOMPLETE` (6/16 cost_base cells checked; okx EXACT 28,469.71; binance_um/mexc/bitget INCOMPLETE). `ANCHOR: MISMATCH` would be a P0 integrity stop.
- **Gate:** `C25 ACCEPTANCE: PENDING` (58 missing cells; verdict artifacts written only after all cells complete). **`C26 ACCEPTANCE: PENDING`** (blocked on C25; 64 missing cells; path-anchor reference not yet available). **`C28 ACCEPTANCE: PENDING`** (direction c28-a; 32 missing cells; blocked on C27; runner now hard-refuses until `c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists).
- **C28 is BUILT, not launched:** prereg `research_state/c28_prereg_20261121T013400Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c28-a`); `scripts/{build_c28_prereg,run_c28_campaign,verify_c28_focus_campaign}.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `tests/test_c28_campaign.py` (8 passed). Arms: `alloc_base` (FIDELITY_ANCHOR) + `alloc_correlation` (PRIMARY); 4 venues × 4 folds × 20k/20k/2k. Launch command (only after C27 PASS): `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`. The C28 runner now **hard-refuses** (SystemExit, exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists — so if you see that refusal, C27 has not actually PASSed; fix C27 first, do not force. **C28 may NOT run any cell until C27 ACCEPTANCE: PASS** (anchor = C25/C26 primary-arm venue_totals must exist).
- **C29 is STAGED, not launched:** prereg `research_state/c29_prereg_20261121T031907Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`, direction `c29-a`); `scripts/{build_c29_prereg,run_c29_campaign,verify_c29_focus_campaign}.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `tests/test_c29_campaign.py`. Direction `c29-a` = **strict temporal out-of-sample holdout on the newest never-scored window** (the most heavily powered candidate by realized evidence: C24–C28 leave 2026YTD partially scored and no holdout on the most recent window). Launch command (only after C28 PASS): `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`. The C29 runner hard-refuses unless `research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists. **C29 may NOT run any cell until C28 ACCEPTANCE: PASS.** On C29 PASS, open C30 with a fresh prereg anchored on C24–C29 evidence.
- **Tests (last verified 2026-11-21T03:14:30Z; not re-run this session to avoid competing for cores):** Campaign subset `tests/test_c25_campaign.py tests/test_c26_campaign.py tests/test_c28_campaign.py tests/test_c29_campaign.py` → **29 passed** in ~0.5 s. (Full `pytest -q` last green 2026-11-20T17:37:22Z → 1100 passed, 1 skipped; do not re-run every wake — it competes with the 4 cores.)
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited, 6 verdict artifacts present. **Do not relaunch.**
- `.venv` is bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`. Only run `bash scripts/bootstrap_env.sh` if `.venv/bin/python` is missing.

---

## MONITORING PROTOCOL FOR THE MULTI-DAY RUN (use this, never poll)

- A session must never hold a turn open for hours, never `sleep` past the ~900 s idle timeout, and never poll in a loop.
- One bounded read (`bash scripts/eta_c25.sh`), then schedule and suspend with exactly:
  `schedule_wakeup delay=8h reason="C25 tick" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume exactly once with background_process start command='bash scripts/run_c25_durable.sh' persistent=true. If the gate is C25 ACCEPTANCE: PASS, execute the C25-PASS checklist and launch C26 in this same session. If check_c25_anchor.sh prints ANCHOR: MISMATCH, stop and record evidence. Otherwise update HANDOFF.md only if state materially changed and schedule the next 8h wakeup."`
- **8 h cadence is correct** at ~3.6 h/cell (≈2 cells per wake). Shorter adds nothing.
- If the checkpoint count is unchanged across **two consecutive 8 h wakes** while the runner is ALIVE, treat it as "cell in permutation" (that stage prints nothing) and keep waiting — do **not** conclude the runner is stuck and do **not** kill it.
- One wake in four should additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (74 s) to catch wiring rot. Do not run it every wake; it competes with the 4 cores.
- **Continuity guarantee:** no wakeup is currently armed for this session (`cancel_wakeup list` empty at 2026-11-21T04:14:07Z). **Wakeups are session-scoped:** every new agent session must run `cancel_wakeup list`; if empty, re-arm immediately with the exact `schedule_wakeup` above. The queue does not stall on a human remembering to poll.

---

## BOTTLENECK REGISTER (what is removed, what remains, what is forbidden)

Removed already (do not re-add):

1. **State drift across duplicate handoffs — removed 2026-11-19T22:40Z.** `HANDOFF.md` is the only state-bearing file; `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers. Any future session that writes campaign state into a second file is creating the exact failure this note removes.
2. **Multi-day monitoring blindness — removed.** `scripts/eta_c25.sh` self-calibrates from completed checkpoints; sessions no longer guess from log tails or mistake the silent permutation stage for a hang.
3. **Late anchor detection — removed.** `scripts/check_c25_anchor.sh` compares every `cost_base` cell and venue total against C24 d15 the moment a checkpoint lands, instead of after ~6 days of compute.
4. **Same-session C25→C26 transition — hard-coded in step 5d.** Previously the gap between "C25 PASS" and "C26 launched" could idle for a whole wake (8 h) or a human cycle. Now it is a same-session obligation with the exact command.
5. **Queue-dryness — removed.** C26 is built and launch-ready behind the C25 gate; C27 is staged (probe + prereg) behind the C26 gate, so "no authorized work" is never a truthful state.
6. **Stale PID/log state drift in INITIAL TASK MESSAGE — removed 2026-11-19T23:43:01Z.** The INITIAL TASK MESSAGE previously cited a dead runner PID 3901 / log `c25_run_20261119T172418Z.log` while the SESSION LOG recorded runner PID 3258 / log `c25_run_20261119T234132Z.log`. The VERIFIED LIVE STATE block now reads one verified state (PID 3258, log `234132Z.log`, started 23:41:32Z); future sessions cannot relaunch a ghost or confuse the live runner.
7. **INITIAL_TASK_MESSAGE.md carried duplicate state — removed 2026-11-20T01:53:10Z.** `INITIAL_TASK_MESSAGE.md` is now a pointer-only file (one line pointing to `HANDOFF.md`). It no longer carries campaign state, ETA, PID, or gate values. Any future session that writes campaign state into `INITIAL_TASK_MESSAGE.md` or `AGENT_HANDOFF.md` recreates the exact state-drift failure this removes.
8. **Handoff bloat from repetitive session logs — removed 2026-11-21T00:27:46Z.** The prior `HANDOFF.md` had accumulated ~12 near-identical "re-verify" session-log entries with stale timestamps and two competing INITIAL TASK MESSAGE sections, creating ambiguity about which state was current. This version consolidates to a single clean handoff with the latest verified state at the top, the single binding INITIAL TASK MESSAGE, and the full guardrails/protocol/campaign record preserved.
9. **Handoff vs repository drift on C28 — removed 2026-11-21T02:35:05Z.** The C28 campaign (prereg `c28_prereg_20261121T013400Z`, scripts, tests) already existed on disk (built 2026-11-21T01:36Z) but `HANDOFF.md` still described C28 as "not yet created" / "standing next focus campaign," so a future agent reading the handoff would either rebuild C28 or be confused. HANDOFF.md now records C28 as BUILT + gate-held with its exact artifacts, arms, tokens, and launch command, and adds `status_c28.sh`/`verify_c28_focus_campaign.py` to the read-only verification block.
10. **C28 gate documented but not enforced — removed 2026-11-21T02:35:05Z.** `scripts/run_c28_campaign.py` printed a warning when C27 had not PASSed but then continued into ~8 days of heavy compute on pre-anchor, invalid evidence. It now raises `SystemExit` (exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists, matching the documented "no C28 cell may run until C27 ACCEPTANCE: PASS" guardrail. Tests unaffected (8 passed).

11. **Missing 8h monitoring wakeup in a new session — removed 2026-11-21T04:16:29Z.** `cancel_wakeup list` was empty in this session even though the prior handoff claimed a wakeup was armed; wakeups do not automatically carry into a new session. Re-armed with `schedule_wakeup delay=8h` (reason "C25 cost-fidelity multi-day run: monitor progress, resume-once if dead, launch C26 on PASS") → `wku_1fc50ce26001jgnAXtRRcJPFEr` due 2026-11-21T12:15:16Z, carrying the full C25 tick + resume-once + C26-on-PASS protocol prompt. **No future session may start without confirming a wakeup is armed** (`cancel_wakeup list` must be non-empty); if missing, re-arm immediately with the MONITORING PROTOCOL prompt.

12. **Runner death from missing `.venv` — removed 2026-11-21T03:14:30Z.** At 03:13:33Z `status_c25.sh` printed `RUNNER: NOT ALIVE`; the C25 runner had died mid-cell `cost_base/binance_um/2025` because `.venv/bin/python` was missing (ephemeral venv wiped between sessions). Fix: `bash scripts/bootstrap_env.sh` (durable default at `$ROOT/.venv`, gitignored, survives restarts), then resume exactly once with `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`. Runner is now ALIVE (python PID 3103, parent 3098, durable shell 3040), 6/56 cells complete, resuming from checkpoint. Never `nohup`/`setsid` a runner yourself; never relaunch while ALIVE.

13. **Duplicate wakeup entries in the bottleneck register — removed 2026-11-21T03:25:06Z.** Items 11 and 13 previously repeated the same missing-wakeup note with different stale IDs. Item 11 is now the single authoritative entry; this item is retained only as the removal record so future sessions do not reintroduce duplicate monitoring state.

Remaining bottleneck — compute, and it is **not fixable mid-run**:

- 20k conditional-permutation portfolio replays per cell cost **11,510 s** (3.20 h) + 2k placebo replays **1,458 s** (0.41 h) = **~3.6 h/cell** on 4 saturated cores; **50 cells left; `eta_c25.sh` self-calibrates to 80.9 h (n=6) → ~2026-11-24T12:17:35Z (±30%)**.
- The live process has already imported the engine, so editing `src/backtest/engine.py`, `scripts/run_portfolio.py`, or `scripts/run_c20_cross_venue_campaign.py` **cannot** speed it up; a restart would gamble the campaign and a bit-identical claim cannot be proven mid-flight.
- Draw floors (20k/20k/2k/2k) are prereg-bound and **must not be reduced**. Running C25 and C26 concurrently is forbidden (sequential adjudication chain) and would only split 4 cores.
- Any acceleration is a **separate, pre-registered, anchor-verified campaign after C25/C26** — never a mid-run edit, restart, or "quick fix". Do not add competing CPU work (extra tests, probes, notebooks) while the runner is alive.

---

## CAMPAIGNS

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)

**Prereg (frozen):** `research_state/c25_prereg_20261119T045500Z.{json,md}` — `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, generated `2026-11-19T04:55:00Z`. Do not edit; any drift ⇒ `C25 ACCEPTANCE: FAIL`.
**Question:** the engine charges 5 bps/side slippage, `commission_per_share=0.001` (effectively free), `commission_min=1.0`, flat `funding_rate_pct_per_hour=0.01`. Real venues charge ~4.5–7 bps/side taker plus realized 8 h funding. On a 9 %-target, multi-day-hold, short/hedged strategy this is the largest remaining candidate explanation for the four-venue `NO_GO`.
**Arms (only slippage/commission/funding vary; signal path frozen; liquidation fixed at C24 primary d15 = 15 %):**

| arm | slippage | commission | funding | role |
|---|---|---|---|---|
| `cost_base` | 5 bps | 0.001/share ($1 min) | 0.01 %/h | FIDELITY_ANCHOR |
| `cost_taker` | 5 bps | venue taker bps | 0.01 %/h | descriptive |
| `cost_taker_funding` | 5 bps | venue taker bps | realized venue mean | **PRIMARY** |
| `cost_stress` | 10 bps | venue taker bps | realized + 5 bps borrow | descriptive |

**Anchor rule:** `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 (it reproduces each fold exactly so far: okx/2023 = 34,420.88) → `COST_ANCHOR_REPRODUCED`, else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`.
**Funding inputs (real, never zero-filled):** binance_um 132,577 rows / 32 symbols → 0.0005717 %/h; mexc 1,568 rows / 8 symbols → 0.0004581 %/h; bitget 3,944 rows / 33 symbols → 0.0007211 %/h. `okx` has **no** realized funding history (`GET /api/v5/public/funding-rate-history` capped at 100 rows / rolling 33-day window, cursor ignored) → `UNAVAILABLE_FUNDING`; artifact `research_state/c25_okx_funding_retention_probe_20261119T101402Z.json`. Funding arms therefore run on 3 venues, satisfying the prereg availability clause.
**Decision rules:** `C25_REOPENS_C1_C24` requires, under `cost_taker_funding`: pooled > 0 AND CI95 lower > 0 AND ≥1 BH survivor in the 16-test venue×fold family AND ≥3/4 folds positive AND ≥3/4 venues positive. Otherwise `C25_NO_GO_ROBUST_TO_COST`. Gate tokens: `C25 ACCEPTANCE: PENDING|PASS|FAIL`.
**Scripts:** `run_c25_cost_fidelity_campaign.py`, `run_c25_durable.sh`, `status_c25.sh`, `eta_c25.sh`, `check_c25_anchor.sh`, `verify_c25_focus_campaign.py`, `build_c25_prereg.py`, `probe_c25_funding_acquisition.py`, `probe_c25_okx_funding_retention.py`, `fetch_funding_history.py`, `run_c25_okx_funding_durable.sh` (guard only), `tests/test_c25_campaign.py`.
**Status (2026-11-21T03:25:06Z):** 6/56 real cells complete (`cost_base/okx/2023` pnl +34,420.88; `cost_base/okx/2024` pnl +1,621.97; `cost_base/okx/2025` pnl +4,721.66; `cost_base/okx/2026YTD` pnl +5,166.77; `cost_base/binance_um/2023` pnl +165.87; `cost_base/binance_um/2024` pnl +17,202.49), 50 remaining, ETA **~2026-11-24T12:17:35Z (±30%)**, anchor `INCOMPLETE` (6/16; okx EXACT, others INCOMPLETE), gate `PENDING`. Runner healthy.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)

**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags `intrabar_adverse_first` / `per_trade_funding` exist with default `False` (C20–C25 baseline unchanged); campaign, durable launcher, status, gate, and `tests/test_c26_campaign.py` all present and passing. **No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Why:** C25 applies funding as one venue-mean scalar and prices every fill at next open on 1 h bars. Two gaps remain, both able to flip the sign: (a) funding applied per trade/symbol/timestamp instead of a venue mean; (b) intrabar path — when a 1 h bar touches both stop and target (or liquidation), the within-bar order decides the exit.
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 → `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`; gate `C26 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; monitor with `scripts/status_c26.sh` + `scripts/verify_c26_focus_campaign.py`. Budget the **same ~3.6 h/cell, ~8 days → ~2026-11-25T12:01:37Z + 8 days (±30%)** (56 real cells, 8 okx funding skips).

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (STAGED, NOT LAUNCHED)

**Status:** probe + prereg written; launch blocked on `C26 ACCEPTANCE: PASS`.
**Staged artifacts:** `scripts/probe_c27_venue_acquisition.py`; `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`; Bybit primary candidate, fallback named by the probe; signal path frozen to the spec-literal values including `liquidation_maint_margin_pct=14.0`, `liquidation_buffer_pct=1.0`, `liquidation_distance_pct=15.0`).
**Mandate:** after `C26 ACCEPTANCE: PASS` (whatever the token), the same session must run the probe, confirm the prereg matches its `ACQUISITION_VIABLE_*` verdict (or record `*_BLOCKED_BY_API_RETENTION`), and durably launch the campaign. If no new venue is viable, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.
**Hyperliquid-native stays CLOSED:** `FULL_283D_BLOCKED_BY_API_RETENTION`.
**C27 is not the end of the queue.** On `C27 ACCEPTANCE: PASS` the same session opens **C28** (direction `c28-a`, already built — see C28 campaign section below). The heavy-work queue does not terminate at C27.

### C28-T1 — PORTFOLIO-LEVEL CROSS-VENUE CAPITAL ALLOCATION & CORRELATION FIDELITY (BUILT, GATE-HELD, NOT LAUNCHED)

**Status:** BUILT. Prereg `research_state/c28_prereg_20261121T013400Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c28-a`); `scripts/{build_c28_prereg,run_c28_campaign,verify_c28_focus_campaign}.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `tests/test_c28_campaign.py` (8 passed) all present. **No C28 cell may run until `C27 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c27_decision_verdict_CONSOLIDATED_20261119T215721Z.json` exists.
**Why:** C25/C26 adjudicate cost/funding and intrabar-path fidelity per venue on 4 venues × 4 folds. C28-A asks the portfolio-level successor question: does the pooled GO survive cross-venue capital constraints and venue return correlation when all viable venues share a fixed gross budget? Allocation weights vary; signal, cost, funding, liquidation frozen at C25/C26 primary.
**Arms:** `alloc_base` (FIDELITY_ANCHOR, must reproduce the prior primary-arm per-venue/per-fold PnL within ±1.0 → `ALLOC_ANCHOR_REPRODUCED`), `alloc_correlation` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C28_REOPENS_C1_C27` / `C28_NO_GO_ROBUST_TO_AXIS`; gate `C28 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C27 PASS):** `background_process start command="bash scripts/run_c28_durable.sh --direction c28-a" persistent=true`; monitor with `scripts/status_c28.sh --direction c28-a` + `scripts/verify_c28_focus_campaign.py --direction c28-a`.

### C29-T1 — STRICT TEMPORAL OUT-OF-SAMPLE HOLDOUT ON THE NEWEST NEVER-SCORED WINDOW (STAGED, NOT LAUNCHED)

**Status:** STAGED. Prereg `research_state/c29_prereg_20261121T031907Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, direction `c29-a`); `scripts/{build_c29_prereg,run_c29_campaign,verify_c29_focus_campaign}.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `tests/test_c29_campaign.py` all present. **No C29 cell may run until `C28 ACCEPTANCE: PASS`.** The runner hard-refuses (SystemExit, exit 1) unless `research_state/c28_decision_verdict_CONSOLIDATED_20261121T013400Z.json` exists.
**Why:** C24–C28 adjudicate margin/liquidation, cost/funding, intrabar path, next-venue replication, and portfolio-level allocation — all on the same multiyear 2023–2026YTD window. No direction has yet scored a strict temporal holdout on the newest never-scored window, which is the most heavily powered candidate by realized evidence for re-opening the C1–C28 NO_GO chain.
**Direction `c29-a` (holdout):** signal path frozen at C25/C26 primary; cost/funding/liquidation frozen at C25 primary; 4 venues × 4 folds × 20k/20k/2k. One fold is held out as the strictest temporal OOS test (the most recent never-scored window); the remaining 3 folds train/anchor. The PRIMARY arm tests whether the pooled GO survives on truly unseen data.
**Arms:** `holdout_base` (FIDELITY_ANCHOR, must reproduce C25/C26 primary-arm per-venue/per-fold PnL within ±1.0 → `HOLDOUT_ANCHOR_REPRODUCED`), `holdout_primary` (**PRIMARY**, strict OOS on the held-out newest window).
**Tokens:** `C29_REOPENS_C1_C28` / `C29_NO_GO_ROBUST_TO_HOLDOUT`; gate `C29 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C28 PASS):** `background_process start command="bash scripts/run_c29_durable.sh --direction c29-a" persistent=true`; monitor with `scripts/status_c29.sh --direction c29-a` + `PYTHONPATH=. .venv/bin/python scripts/verify_c29_focus_campaign.py --direction c29-a`.
**Budget:** same ~3.6 h/cell, ~8 days on 4 saturated cores (56 real cells, 8 okx funding skips). C29 opens the holdout frontier; C30 is the standing successor on C29 PASS.

---

## C24-T1 — MARGIN / LIQUIDATION FIDELITY ADJUDICATION (COMPLETE, CLOSED)

`C24 ACCEPTANCE: PASS`; consolidated `C24_REOPENS_C1_C23`; all 80 cells done; runner exited; 6 verdict artifacts (`c24_decision_verdict_{base_6,d10,d15,d30,noliq,CONSOLIDATED}_20261119T013154Z.json`); prereg `c24_prereg_20261119T013154Z` (sha256 `3c0d0b12e139ed2ed264e44964c23639110b2c5a4c0b79ade99ec1f69af30dcb`). **Do not relaunch.**
Anchor: the 6 % forced-liquidation arm reproduced C20/C22/C23 exactly (okx −54,799.23 | binance_um −70,071.41 | mexc −49,760.24 | bitget −58,129.33) → `FIDELITY_ANCHOR_REPRODUCED`.
Arm pooled totals: `base_6` −232,760.19 · `d10` −61,002.11 · **`d15` +144,651.69 (PRIMARY)** · `d30` +417,169.70 · `noliq` +539,745.52.
d15 venue totals: okx 28,469.71 · binance_um 47,613.33 · mexc 38,334.16 · bitget 30,234.49.
d15 per-cell PnL / perm_p / placebo p_ge (20k/20k/2k):
okx 2023 34,420.88 / 0.335 / 0.0675 · okx 2024 −23,054.83 / 0.6149 / 0.923 · okx 2025 5,538.89 / 0.53815 / 0.699 · okx 2026YTD 11,564.77 / 0.5756 / 0.3595 ·
binance_um 2023 38,752.19 / 0.4906 / 0.0635 · 2024 −15,387.90 / 0.71625 / 0.7845 · 2025 18,273.31 / 0.4923 / 0.662 · 2026YTD 5,975.73 / 1.0 / 0.4115 ·
mexc 2023 34,300.42 / 0.06135 / 0.0915 · 2024 −15,455.09 / 0.79765 / 0.7775 · 2025 15,567.16 / 0.4654 / 0.64 · 2026YTD 3,921.67 / 1.0 / 0.4065 ·
bitget 2023 35,797.29 / 0.1283 / 0.047 · 2024 −29,720.46 / 0.6564 / 0.9665 · 2025 21,116.87 / 0.2552 / 0.647 · 2026YTD 3,040.79 / 0.75 / 0.422.
**No d15 cell has perm_p < 0.01; one placebo p_ge = 0.047 (bitget/2023) ≤ 0.05 — watch item, not a verdict.** The verdict is the prereg rule over all 16 cells, never a partial read.

---

## CLOSED CAMPAIGN RECORD (history — do not relitigate)

- **C21-T1 (`20261117T064408Z`):** `PASS`, consolidated `NO_GO`.
- **C22-T1 — MEXC OOS replication (`20261118T100126Z`):** `PASS`, consolidated `NO_GO`. 2023: 25 trades, +30,599.03, perm p=0.01835, placebo p_ge=0.006, CI95 [−4,715.22, +67,959.60]; 2024: 40 trades, −27,326.63, perm p=0.3085. A single positive fold is not a result.
- **C23-T1 — Bitget OOS replication (`20261118T202301Z`):** `PASS`, consolidated `NO_GO`. 2023 +28,706.32 (24 trades, perm_p 0.0229, 0/9 BH) · 2024 −30,939.60 · 2025 −32,710.19 · 2026YTD −23,185.86. Pooled **−58,129.33**, prob>0 = 0.0, BH survivors 0/36.
- **C20 cross-venue reference (spec-literal, full multiyear):** OKX 113 trades, −55,057.45; Binance UM 136 trades, −70,309.57 → pooled `NO_GO`. Use as a sanity check on any new-venue result: a wildly divergent sign is a red flag, not a discovery.
- **C1–C21 closed** `NO_GO`; C1–C23 `NO_GO` is **superseded** by C24. C14 native is underpowered (7 trades / 3 episodes).
- **Closed data acquisitions:** Hyperliquid-native `FULL_283D_BLOCKED_BY_API_RETENTION`; OKX realized funding `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Do not retry either.

---

## GUARDRAILS (never violate)

- No cross-venue relabelling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20–C27).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22/C23/C24/C25/C26 configs frozen to their preregs.
- **No funding fabrication:** `okx` funding does not exist beyond a 33-day window (`OKX_FUNDING_BLOCKED_BY_API_RETENTION`) — report `UNAVAILABLE_FUNDING`, never zero-fill, never proxy from another venue, never cache the 1-month tail as multiyear.
- **Funding model honesty:** C25 reports `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cites `research_state/c25_funding_model_disclosure_20261119T091800Z.json`; per-trade funding is C26 only.
- **Do not reduce draw counts** (20k/20k/2k/2k floors). **Do not edit a live campaign's prereg or code path.**
- **Status first:** `bash scripts/status_c25.sh` before any C25 action; the durable runner's real PID is whatever it prints.
- **Do not kill or duplicate the persistent runner.** Long campaigns must be launched through the harness background-process tool with `persistent=true` (a campaign started inside a turn dies with the turn — that already cost two C24 runs).
- **No long foreground sleep** that hits the ~900 s idle timeout: use `schedule_wakeup` or bounded reads.
- No same-data rerun of a closed campaign. Only new data + new prereg + explicit authorization justifies a new campaign.
- Do not edit completed artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent baseline change. C1–C23 `NO_GO` is superseded by C24; it stands until a later pre-registered campaign contradicts it with full evidence.
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27 → C28 → C29 → C30+`. C28 (direction c28-a) is built and gate-held behind C27; C29 (direction c29-a) is staged and gate-held behind C28; C30 is the standing successor on C29 PASS.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim: `C21/C22/C23 ACCEPTANCE: PASS`, `C24 ACCEPTANCE: PASS`, `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`, `FIDELITY_ANCHOR_REPRODUCED`, `COST_ANCHOR_REPRODUCED`, `PATH_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C25_UNDERPOWERED`, `C26_UNDERPOWERED`, `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, `MISMATCH`/`ANCHOR: OK`/`ANCHOR: INCOMPLETE` from `check_c25_anchor.sh`.

---

## QUICK REFERENCE — PATHS

- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` + `AGENT_HANDOFF.md` (pointers), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`.
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261121T031415Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- C27: `scripts/probe_c27_venue_acquisition.py`, `research_state/c27_prereg_20261119T215721Z.{json,md}`.
- C28 (BUILT, direction c28-a): `scripts/build_c28_prereg.py`, `scripts/run_c28_campaign.py`, `scripts/run_c28_durable.sh`, `scripts/status_c28.sh`, `scripts/verify_c28_focus_campaign.py`, `tests/test_c28_campaign.py`, `research_state/c28_prereg_20261121T013400Z.{json,md}`.
- C29 (STAGED, direction c29-a): `scripts/build_c29_prereg.py`, `scripts/run_c29_campaign.py`, `scripts/run_c29_durable.sh`, `scripts/status_c29.sh`, `scripts/verify_c29_focus_campaign.py`, `tests/test_c29_campaign.py`, `research_state/c29_prereg_20261121T031907Z.{json,md}`. Holdout direction: strict temporal OOS on the newest never-scored window. Launch only after C28 PASS.
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`.
