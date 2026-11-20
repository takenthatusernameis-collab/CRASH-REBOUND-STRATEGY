# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-20T07:35:47Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data.
**This is the single durable handoff.** `INITIAL_TASK_MESSAGE.md` and `AGENT_HANDOFF.md` are now *pointers only* (they must not carry state). `README.md` points here.

**ONE-LINE STATUS:** `C25-T1` cost/funding fidelity is **RUNNER ALIVE & COMPUTING** (PID 5536, 4 workers), **1/56 real inference cells complete** (`cost_base/okx/2023`, pnl +34,420.88), 55 pending, gate `C25 ACCEPTANCE: PENDING`, projected completion **~2026-11-28T13:44:20Z (±30%)** on this 4-core box. Anchor `INCOMPLETE` (1/16 checked, no MISMATCH). **DO NOT RELAUNCH. DO NOT KILL. DO NOT REORDER ARMS. DO NOT START ANY C26/C27 CELL.** Binding queue: `C24 → C25 (live) → C26 (BUILT, blocked on C25 PASS) → C27 (probe + prereg staged, blocked on C26 PASS)`.

**SESSION LOG — 2026-11-20T07:35:47Z (handoff refresh):** Re-verified live state at handoff read (2026-11-20T07:35:47Z): `status_c25.sh` → `RUNNER: ALIVE` (PID 5536, parent 5531, 4 workers running since ~06:21Z), `eta_c25.sh` → **1/56 real cells complete**, 55 remaining, ETA **~2026-11-28T13:46:34Z (±30%)**, `check_c25_anchor.sh` → **ANCHOR: INCOMPLETE** (1/16 cost_base cells checked; okx/2023 reproduces C24 d15 exactly — **no MISMATCH**). `verify_c25_focus_campaign.py` → `C25 ACCEPTANCE: PENDING` (63 missing cells). Runner healthy, 4 workers saturated. Checkpoint `c25_ckpt_cost_base_okx_2023_20261119T045500Z.json` persists in `research_state/`. No bottlenecks are removable mid-run — compute is the sole remaining constraint and is not fixable without a restart (see BOTTLENECK REGISTER). Scheduled next wake at 8 h per the monitoring protocol.

**Binding heavy queue (there is no idle state):** `C24-T1 (COMPLETE, PASS)` → **`C25-T1 (IN FLIGHT)`** → `C26-T1 (BUILT, blocked on C25 PASS)` → `C27-T1 (probe + prereg staged, launch blocked on C26 PASS)`.

---

## VERIFIED LIVE STATE — 2026-11-20T07:33:33Z

Re-verify before acting; this block is stale the moment you read it. Read-only commands, in order:

```
bash scripts/status_c25.sh              # runner + per-cell + artifacts + gate  (ground truth)
bash scripts/eta_c25.sh                 # progress, per-cell cost, ETA
bash scripts/check_c25_anchor.sh        # early cost_base vs C24 d15 anchor
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
```

Observed at generation time (2026-11-20T06:37:22Z):

- **C25 RUNNER: ALIVE.** Parent PID **5536** (`scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`), started **~06:21Z**, 4 draw workers, launched through the harness background-process runner (`persistent=true`) via `scripts/run_c25_durable.sh`, teeing to `research_state/c25_run_20261119T234132Z.log`. Whatever `status_c25.sh` prints is ground truth — never trust a PID written in this file.
- **Cells:** `cost_base 1/16`, `cost_taker 0/16`, `cost_taker_funding 0/16`, `cost_stress 0/16`; 1 real cell DONE (`cost_base/okx/2023`, pnl **+34,420.88**, perm_p **0.335**, placebo p_ge **0.0705**, ckpt written 21:00:41Z). `cost_base/okx/2024` in permutation since ~06:21Z (the permutation stage emits no log lines for hours — silence is normal).
- **ETA:** `eta_c25.sh` → 55 real cells left, median **3.20 h** permutation + **0.41 h** placebo per cell → **198.2 h ≈ 8.3 days → ~2026-11-28T13:46:34Z (±30%)**. The 4-core box is saturated; no mid-run acceleration, restart, or extra CPU work is permitted while the runner is alive (guardrails).
- **Anchor:** `ANCHOR: INCOMPLETE` (1/16 cost_base cells checked; okx/2023 reproduces C24 d15 exactly). `ANCHOR: MISMATCH` would be a P0 integrity stop.
- **Gate:** `C25 ACCEPTANCE: PENDING` (63 missing cells; verdict artifacts written only after all cells complete). **`C26 ACCEPTANCE: PENDING`** (blocked on C25; 64 missing cells; path-anchor reference not yet available).
- **Tests (re-verified this session):** `PYTHONPATH=. .venv/bin/python -m pytest -q` → **1095 passed, 1 skipped** in 74 s. Campaign subset `tests/test_c25_campaign.py tests/test_c26_campaign.py` → **13 passed**.
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited, 6 verdict artifacts present. **Do not relaunch.**
- `.venv` is bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`. Only run `bash scripts/bootstrap_env.sh` if `.venv/bin/python` is missing.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-20T07:32:35Z — C25 RUNNER ALIVE, 1/56 REAL CELLS, ETA ~2026-11-28T12:48:10Z ±30% — DO NOT RELAUNCH)

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.

**Current position:** C1–C20 closed `NO_GO`. C21/C22/C23-T1 complete (`PASS`), each consolidated `NO_GO`. **C24-T1 complete: `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled **+144,651.69**, CI95 [+117,408.41, +173,074.50], prob>0 = 1.0; C1–C23 `NO_GO` superseded). **C25-T1 in flight** (1/56 real cells; 8 okx funding cells are instant `UNAVAILABLE_FUNDING` skips; ETA ~2026-11-28T12:48:10Z ±30%). **C26-T1 built, not launched. C27-T1 probe + prereg staged, not launched.**

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

1. **Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`.** Those two commands are the truth. Do not assemble your own `ps`/`ls`/log chain. Never trust a PID or log path written in any file; whatever `status_c25.sh` prints is ground truth.

2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26/C27 cell, do not add any CPU work. Do:
   - `bash scripts/check_c25_anchor.sh` → must stay `ANCHOR: OK` / `ANCHOR: INCOMPLETE`. If `ANCHOR: MISMATCH`, that is a P0 integrity stop: record the evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg.
   - then **suspend with `schedule_wakeup` (8 h)** using the exact prompt in the monitoring protocol below. Do not burn turns polling.

3. **If `RUNNER: NOT ALIVE` and the gate is `PENDING`:** fix the failure cause first, then resume **exactly once**:
   `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (its duplicate guard no-ops if a runner is already up). Never resume twice for the same failure. Never `nohup`/`setsid` it yourself — a runner started inside a turn dies with the turn.

4. **If the gate prints `C25 ACCEPTANCE: FAIL`:** fix only the failing integrity condition (prereg drift, anchor mismatch, draw floors, smoke contamination). Never force PASS.

5. **On `C25 ACCEPTANCE: PASS` (do all of this in that same session, then go to step 6):**
   a. Deliver the full arm × venue × fold cost/funding table, per-leg attribution, exit-reason decomposition, BH family, and the consolidated token (`C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`).
   b. State, verbatim, `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` and cite `research_state/c25_funding_model_disclosure_20261119T091800Z.json`. Never claim per-trade funding (that is C26).
   c. Report `okx` as `UNAVAILABLE_FUNDING` / `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Never zero-fill, proxy, or retry it.
   d. **Immediately and durably launch C26-T1:** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then verify with `bash scripts/status_c26.sh` and `scripts/verify_c26_focus_campaign.py`. Do not idle, do not claim "no authorized work", do not do a same-data parameter search.

6. **On `C26 ACCEPTANCE: PASS` (same session, mandatory successor):** run the staged stage-0 probe `PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py`; confirm the prereg `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`, sha pinned) still matches the probe verdict; then durably launch the C27 campaign. If the probe returns `ACQUISITION_BLOCKED_BY_API_RETENTION`, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or a frozen-signal parameter search.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27` is the heavy queue. No session may idle, declare "no authorized work", substitute a frozen-signal parameter search, retry closed data acquisitions, zero-fill funding, reduce draw counts, or relaunch a finished campaign (C20/C22/C23/C24 are PASS and closed). A `PENDING` gate is not a blocker: it means the heavy battery must keep running. **C25 is the live focus campaign; C26 is the mandatory same-session successor on C25 PASS; C27 is the mandatory same-session successor on C26 PASS.** "No authorized work" is never a truthful state while any gate in this chain is PENDING.

---

## MONITORING PROTOCOL FOR THE MULTI-DAY RUN (use this, never poll)

- A session must never hold a turn open for hours, never `sleep` past the ~900 s idle timeout, and never poll in a loop.
- One bounded read (`bash scripts/eta_c25.sh`), then schedule and suspend with exactly:
  `schedule_wakeup delay=8h reason="C25 tick" prompt="Run bash scripts/status_c25.sh and bash scripts/eta_c25.sh. If RUNNER NOT ALIVE and gate PENDING, fix the cause then resume exactly once with background_process start command='bash scripts/run_c25_durable.sh' persistent=true. If the gate is C25 ACCEPTANCE: PASS, execute the C25-PASS checklist and launch C26 in this same session. If check_c25_anchor.sh prints ANCHOR: MISMATCH, stop and record evidence. Otherwise update HANDOFF.md only if state materially changed and schedule the next 8h wakeup."`
- **8 h cadence is correct** at ~3.6 h/cell (≈2 cells per wake). Shorter adds nothing.
- If the checkpoint count is unchanged across **two consecutive 8 h wakes** while the runner is ALIVE, treat it as "cell in permutation" (that stage prints nothing) and keep waiting — do **not** conclude the runner is stuck and do **not** kill it.
- One wake in four should additionally run `PYTHONPATH=. .venv/bin/python -m pytest -q` (74 s) to catch wiring rot. Do not run it every wake; it competes with the 4 cores.

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

Remaining bottleneck — compute, and it is **not fixable mid-run**:

- 20k conditional-permutation portfolio replays per cell cost **11,510 s** (3.20 h) + 2k placebo replays **1,458 s** (0.41 h) = **~3.6 h/cell** on 4 saturated cores; **55 cells left ≈ 198 h → ~2026-11-28T13:46:34Z (±30%)**.
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

**Status (2026-11-20T07:35:47Z):** 1/56 real cells complete (`cost_base/okx/2023`), 55 remaining, ETA **~2026-11-28T13:46:34Z (±30%)**, anchor `INCOMPLETE` (1/16), gate `PENDING`. Runner healthy.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)

**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags `intrabar_adverse_first` / `per_trade_funding` exist with default `False` (C20–C25 baseline unchanged); campaign, durable launcher, status, gate, and `tests/test_c26_campaign.py` all present and passing. **No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Why:** C25 applies funding as one venue-mean scalar and prices every fill at next open on 1 h bars. Two gaps remain, both able to flip the sign: (a) funding applied per trade/symbol/timestamp instead of a venue mean; (b) intrabar path — when a 1 h bar touches both stop and target (or liquidation), the within-bar order decides the exit.
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 → `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k.
**Tokens:** `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`; gate `C26 ACCEPTANCE: PENDING|PASS|FAIL`.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; monitor with `scripts/status_c26.sh` + `scripts/verify_c26_focus_campaign.py`. Budget the **same ~3.6 h/cell, ~8 days → ~2026-11-28T13:46:34Z + 8 days (±30%)** (56 real cells, 8 okx funding skips).

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (STAGED, NOT LAUNCHED)

**Status:** probe + prereg written; launch blocked on `C26 ACCEPTANCE: PASS`.
**Staged artifacts:** `scripts/probe_c27_venue_acquisition.py`; `research_state/c27_prereg_20261119T215721Z.{json,md}` (`prereg_status: PRE_REGISTERED_BEFORE_COMPUTE`; Bybit primary candidate, fallback named by the probe; signal path frozen to the spec-literal values including `liquidation_maint_margin_pct=14.0`, `liquidation_buffer_pct=1.0`, `liquidation_distance_pct=15.0`).
**Mandate:** after `C26 ACCEPTANCE: PASS` (whatever the token), the same session must run the probe, confirm the prereg matches its `ACQUISITION_VIABLE_*` verdict (or record `*_BLOCKED_BY_API_RETENTION`), and durably launch the campaign. If no new venue is viable, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or frozen-signal parameter search.
**Hyperliquid-native stays CLOSED:** `FULL_283D_BLOCKED_BY_API_RETENTION`.

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
- **No idle sessions:** the binding queue is `C24 → C25 → C26 → C27`.
- Do not commit unless explicitly asked (the controller checkpoints the worktree; do not rewrite history).
- Preserve literal gate tokens verbatim: `C21/C22/C23 ACCEPTANCE: PASS`, `C24 ACCEPTANCE: PASS`, `C25 ACCEPTANCE: PENDING|PASS|FAIL`, `C26 ACCEPTANCE: PENDING|PASS|FAIL`, `FIDELITY_ANCHOR_REPRODUCED`, `COST_ANCHOR_REPRODUCED`, `PATH_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C25_UNDERPOWERED`, `C26_UNDERPOWERED`, `COST_ANCHOR_MISMATCH`, `PATH_ANCHOR_MISMATCH`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `PRE_REGISTERED_BEFORE_COMPUTE`, `MISMATCH`/`ANCHOR: OK`/`ANCHOR: INCOMPLETE` from `check_c25_anchor.sh`.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-20T07:35:47Z)

**Read this HANDOFF.md** — single durable handoff with verified live state, binding queue (`C24 → C25 → C26 → C27`), exact orders, monitoring protocol, guardrails.

Current one-line status (verified at 2026-11-20T07:35:47Z via `status_c25.sh` + `eta_c25.sh` + `check_c25_anchor.sh`): `C25-T1` cost/funding fidelity is **RUNNER ALIVE & COMPUTING** (PID 5536, 4 workers), 1/56 real inference cells complete (`cost_base/okx/2023`), 55 pending, gate `C25 ACCEPTANCE: PENDING`, ETA ~2026-11-28T13:46:34Z (±30%) on this 4-core box. Anchor `INCOMPLETE` (1/16 cost_base cells; okx/2023 reproduces C24 d15 exactly — no MISMATCH). **DO NOT RELAUNCH. DO NOT KILL. DO NOT REORDER ARMS. DO NOT START ANY C26/C27 CELL.** Binding queue: `C24 (PASS) → C25 (live) → C26 (BUILT, blocked on C25 PASS) → C27 (probe + prereg staged, blocked on C26 PASS)`.

Next focus campaign: monitor C25 to PASS, then unblock C26 path fidelity, then C27 venue acquisition. Heavy work continues; no idle sessions.

- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` + `AGENT_HANDOFF.md` (pointers), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`.
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261119T234132Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- C27: `scripts/probe_c27_venue_acquisition.py`, `research_state/c27_prereg_20261119T215721Z.{json,md}`.
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`.
