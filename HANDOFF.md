# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-19T22:31:49Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data.
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` and `README.md` are pointers; never maintain a second source of truth.

**ONE-LINE STATUS:** `C25-T1` cost/funding fidelity is **RUNNER ALIVE & COMPUTING**, **1/56 real inference cells complete** (`cost_base/okx/2023`), gate `C25 ACCEPTANCE: PENDING`, projected completion **~2026-11-28T04:43Z (±30%)** on this 4-core box. **DO NOT RELAUNCH, DO NOT KILL, DO NOT REORDER ARMS.** `C26-T1` is BUILT and may not launch until `C25 ACCEPTANCE: PASS`. `C27-T1` pre-compute staged (probe + `c27_prereg`, launch blocked on `C26 ACCEPTANCE: PASS`).

**Binding heavy queue (no idle state exists):** `C24-T1 (COMPLETE, PASS)` → **`C25-T1 (IN FLIGHT)`** → `C26-T1 (BUILT, blocked on C25 PASS)` → `C27-T1 (pre-compute staged: scripts/probe_c27_venue_acquisition.py + research_state/c27_prereg_20261119T215721Z.{json,md}; launch blocked on C26 PASS)`.

---

## VERIFIED LIVE STATE — 2026-11-19T22:31:49Z (re-verify before acting; this block is stale the moment you read it)

Commands (read-only, in order):

```
bash scripts/status_c25.sh              # runner + per-cell + artifacts + gate
bash scripts/eta_c25.sh                 # progress, per-cell cost, ETA   (added this session)
bash scripts/check_c25_anchor.sh        # early cost_base vs C24 d15 anchor (added this session)
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
```

Observed at generation time:

- **C25 RUNNER: ALIVE.** Parent PID **3901** (`scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume`), started **17:24:18Z**, 4 draw workers, persistent launcher `scripts/run_c25_durable.sh`. Whatever `status_c25.sh` prints is ground truth — never trust a PID written in this file.
- **Cells:** `cost_base 1/16`, `cost_taker 0/16`, `cost_taker_funding 0/16`, `cost_stress 0/16`; 1 real cell DONE (`cost_base/okx/2023`, pnl **+34,420.88**, perm_p **0.335**, placebo p_ge **0.0705**, ckpt written 21:00:41Z). `cost_base/okx/2024` in flight.
- **Gate:** `C25 ACCEPTANCE: PENDING` (63 missing cells). **`C26 ACCEPTANCE: PENDING`** (blocked on C25; 64 missing cells).
- **Tests:** `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c24_campaign.py tests/test_c25_campaign.py tests/test_c26_campaign.py -q` → **24 passed** (re-verified 21:44Z).
- **C24:** `C24 ACCEPTANCE: PASS`, consolidated `C24_REOPENS_C1_C23`, all 80 cells done, runner exited, 6 verdict artifacts present. **Do not relaunch.**
- `.venv` is bootstrapped at repo root (Python 3.12.3). Use `PYTHONPATH=. .venv/bin/python ...`. Only run `bash scripts/bootstrap_env.sh` if `bin/python` is missing.

---

## THROUGHPUT — THE BINDING BOTTLENECK (measured, not estimated)

This host has **4 cores**, shared with the CI runner. One C25 cell is:

| stage | cost (measured) |
|---|---|
| real portfolio engine replay (canonical) | 5.1 s |
| crash census + memo build | ~3 s |
| episode-block bootstrap, 20k resamples | <1 s |
| **conditional permutation, 20k unique portfolio replays** | **11,510 s** (3.20 h) |
| placebo, 2,000 full-portfolio replays (4 workers) | 1,458 s (0.41 h) |
| **total per cell** | **~3.6 h** |

- Direct measurement in-session on the same cell/config: memoised portfolio replay **3.34 s**; 20 permutation draws with 1 worker **61.4 s → 3.07 core-s/draw**.
- **56** cells require real inference (64 cells − 8 `okx` funding-arm cells that are instant `UNAVAILABLE_FUNDING` skips). Remaining after the 1 done cell: **55 × 3.6 h ≈ 198 h ≈ 8.3 days → ~2026-11-28T04:43Z**.
- Do **not** derive ETAs from C24 wall times: the C24 d15 okx/2023 artifact records 477.65 s for 20k draws (~0.095 core-s/draw) on the host used then, ~30× faster than this box measures today. Always use `scripts/eta_c25.sh`, which self-calibrates from completed cells.
- **Do not "fix" this bottleneck mid-run.** The live process has already imported the engine, so editing `src/backtest/engine.py` or `scripts/run_portfolio.py` cannot speed it up, and a bit-identical claim cannot be proven mid-flight. Reducing draw counts is forbidden by the prereg. Any acceleration is a separate, pre-registered, anchor-verified campaign after C25/C26 — never a mid-run edit or restart.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T22:31:49Z — C25 RUNNER ALIVE, 1/56 REAL CELLS DONE, ETA ~2026-11-28, DO NOT RELAUNCH)

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`, never relabelled as Hyperliquid evidence.

**Current position:** C1–C20 closed `NO_GO`. C21/C22/C23-T1 complete (`PASS`), consolidated `NO_GO`. **C24-T1 complete: `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled **+144,651.69**, CI95 [+117,408.41, +173,074.50], prob>0 = 1.0, prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded). **C25-T1 in flight** (1/56 real cells). **C26-T1 built, not launched.**

**Do exactly this, in order — do not skip, do not reorder, do not "improve" it:**

1. Run `bash scripts/status_c25.sh` and `bash scripts/eta_c25.sh`. Those two commands are the truth. Do not assemble your own `ps`/`ls`/log chain.
2. **If `RUNNER: ALIVE`:** do not relaunch, do not kill, do not resume, do not start any C26 cell. If you want to make progress, do one of:
   - `bash scripts/check_c25_anchor.sh` → must eventually print `ANCHOR: OK`. If it prints `ANCHOR: MISMATCH`, that is a P0 integrity stop: record the evidence, stop the battery, fix the cause, resume once. Never relax floors or edit the prereg.
   - then suspend the session with `schedule_wakeup` (6–12 h, see protocol below) instead of burning turns polling.
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

## CAMPAIGNS

### C25-T1 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY (IN FLIGHT)

**Prereg (frozen):** `research_state/c25_prereg_20261119T045500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, sha256 `b1e22b36d074eed3aa2577edccd744343d1e8673c102257b7890a554504f2b6e`. Do not edit.
**Question:** the engine charges 5 bps/side slippage, `commission_per_share=0.001` (effectively free), `commission_min=1.0`, flat `funding_rate_pct_per_hour=0.01`. Real venues charge ~4.5–7 bps/side taker plus realized 8 h funding. On a 9 %-target, multi-day-hold, short/hedged strategy this is the largest remaining candidate explanation for the four-venue `NO_GO`.
**Arms (only slippage/commission/funding vary; signal path frozen; liquidation fixed at C24 primary = 15 %):**

| arm | slippage | commission | funding | role |
|---|---|---|---|---|
| `cost_base` | 5 bps | 0.001/share ($1 min) | 0.01 %/h | FIDELITY_ANCHOR |
| `cost_taker` | 5 bps | venue taker bps | 0.01 %/h | descriptive |
| `cost_taker_funding` | 5 bps | venue taker bps | realized venue mean | **PRIMARY** |
| `cost_stress` | 10 bps | venue taker bps | realized + 5 bps borrow | descriptive |

**Anchor rule:** `cost_base` must reproduce C24 d15 per-venue totals within ±1.0 (in practice it reproduces each fold exactly: okx/2023 = 34,420.88 both). Token `COST_ANCHOR_REPRODUCED`, else `COST_ANCHOR_MISMATCH` → `C25_UNDERPOWERED`.
**Funding inputs (real, never zero-filled):** binance_um 132,577 rows/32 symbols → 0.0005717 %/h; mexc 1,568 rows/8 symbols → 0.0004581 %/h; bitget 3,944 rows/33 symbols → 0.0007211 %/h. `okx` has **no** realized funding history (`GET /api/v5/public/funding-rate-history` is capped at 100 rows and a rolling 33-day window, cursor ignored) → `UNAVAILABLE_FUNDING`, artifact `research_state/c25_okx_funding_retention_probe_20261119T101402Z.json`. Funding arms run on 3 venues, satisfying the prereg availability clause.
**Decision rules:** `C25_REOPENS_C1_C24` requires, under `cost_taker_funding`: pooled > 0 AND CI95 lower > 0 AND ≥1 BH survivor in the 16-test venue×fold family AND ≥3/4 folds positive AND ≥3/4 venues positive. Otherwise `C25_NO_GO_ROBUST_TO_COST` (C1–C25 `NO_GO` robust to margin and cost). Gate tokens: `C25 ACCEPTANCE: PENDING|PASS|FAIL`.
**Scripts:** `run_c25_cost_fidelity_campaign.py`, `run_c25_durable.sh`, `status_c25.sh`, `eta_c25.sh`, `check_c25_anchor.sh`, `verify_c25_focus_campaign.py`, `build_c25_prereg.py`, `probe_c25_funding_acquisition.py`, `probe_c25_okx_funding_retention.py`, `fetch_funding_history.py`, `run_c25_okx_funding_durable.sh` (guard only), `tests/test_c25_campaign.py`.

### C26-T1 — INTRABAR PATH & PER-TRADE FUNDING FIDELITY (BUILT, NOT LAUNCHED)

**Status:** BUILT. Prereg `c26_prereg_20261119T121500Z` (`PRE_REGISTERED_BEFORE_COMPUTE`); engine flags `intrabar_adverse_first` / `per_trade_funding` exist with default `False` (C20–C25 baseline unchanged); campaign, durable launcher, status, gate and `tests/test_c26_campaign.py` all present and passing. **No C26 cell may run until `C25 ACCEPTANCE: PASS`.**
**Why:** C25 applies funding as one venue-mean scalar and prices every fill at next open on 1 h bars. Two gaps remain, both able to flip the sign: (a) funding applied per trade/symbol/timestamp instead of a venue mean; (b) intrabar path — when a 1 h bar touches both stop and target (or liquidation), the within-bar order decides the exit.
**Arms:** `path_base` (FIDELITY_ANCHOR, must reproduce C25 `cost_taker_funding` within ±1.0 → `PATH_ANCHOR_REPRODUCED`), `path_funding_trade`, `path_intrabar_adverse_first`, `path_intrabar_combined` (**PRIMARY**). 4 venues × 4 folds × 20k/20k/2k. Tokens `C26_REOPENS_C1_C25` / `C26_NO_GO_ROBUST_TO_PATH`.
**Launch (only after C25 PASS):** `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`; monitor with `scripts/status_c26.sh` + `scripts/verify_c26_focus_campaign.py`. Expect the **same ~3.6 h/cell, ~8 days** budget: 56 real cells, 8 okx funding skips.

### C27-T1 — NEXT INDEPENDENT USDT-PERP VENUE REPLICATION (NOT BUILT — MANDATORY SUCCESSOR TO C26)

**Status:** definition only. It is the pre-authorized successor so no future session can claim there is no work after C26.
**Mandate:** after `C26 ACCEPTANCE: PASS` (whatever the token), the same session must (1) write and run a stage-0 acquisition probe in the C22/C23 style for a **never-used** USDT-perp venue (Bybit is the primary candidate; if its archive/API retention fails, the probe must name the next candidate and return an explicit `ACQUISITION_VIABLE_*` or `*_BLOCKED_BY_API_RETENTION` token), (2) write `c27_prereg_<TS>.{json,md}` with `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE` **before any compute**, and (3) durably launch the campaign. If no new venue is viable, the only legitimate alternative is a **new pre-registered hypothesis on new data** — never a same-data rerun or a frozen-signal parameter search.
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
- **C22-T1 — MEXC OOS replication (`20261118T100126Z`):** `PASS`, consolidated `NO_GO`. 2023: 25 trades, +30,599.03, perm p=0.01835, placebo p_ge=0.006, CI95 [−4,715.22, +67,959.60]; 2024: 40 trades, −27,326.63, perm p=0.3085; 2025/2026YTD per final artifacts. A single positive fold is not a result.
- **C23-T1 — Bitget OOS replication (`20261118T202301Z`):** `PASS`, consolidated `NO_GO`. 2023 +28,706.32 (24 trades, perm_p 0.0229, 0/9 BH) · 2024 −30,939.60 (36) · 2025 −32,710.19 (37) · 2026YTD −23,185.86 (21). Pooled **−58,129.33**, CI95 [−58,129.33, −58,129.33], prob>0 = 0.0, BH survivors 0/36. `tests/test_c23_campaign_20261118.py` → 13 passed.
- **C20 cross-venue reference (spec-literal, full multiyear):** OKX 113 trades, −55,057.45; Binance UM 136 trades, −70,309.57 → pooled `NO_GO`. Use to sanity-check any new-venue result: a wildly divergent sign is a red flag, not a discovery.
- **C1–C21 closed** `NO_GO`; C1–C23 `NO_GO` is **superseded** by C24. C14 native is underpowered (7 trades / 3 episodes).
- **Closed data acquisitions:** Hyperliquid-native `FULL_283D_BLOCKED_BY_API_RETENTION`; OKX realized funding `OKX_FUNDING_BLOCKED_BY_API_RETENTION`. Do not retry either.

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-19T22:31:49Z)

1. **Handoff state contradiction removed (top bottleneck for sessions).** The title said "1/64 cells complete" while the body said "0/64" and the header said "0/64 cells in flight". Verified live: exactly **1** real cell is complete (`cost_base/okx/2023`, ckpt 21:00:41Z) and exactly **one** cell runs at a time (`cost_base/okx/2024` in permutation). This file now carries that single truth plus the exact commands that produced it.
2. **Multi-day monitoring blindness removed.** Added `scripts/eta_c25.sh` (read-only): it counts real vs `UNAVAILABLE_FUNDING` cells and self-calibrates the per-cell cost from completed checkpoints (currently 3.60 h → ETA ~2026-11-28). Sessions no longer have to guess from log tails, and no longer mistake the silent permutation stage for a hung runner.
3. **Six-day waste risk removed.** Added `scripts/check_c25_anchor.sh` (read-only): it compares each `cost_base` cell against the C24 d15 cell and each venue total against the C24 anchor the moment a checkpoint lands. Previously an anchor mismatch could only be detected by the final gate, after the other arms had burned ~6 days of compute.
4. **Queue-dryness removed.** C26-T1 remains fully built and launch-ready behind `C25 ACCEPTANCE: PASS`; **C27-T1 (new-venue OOS replication)** is now defined with a mandatory probe-first, prereg-first rule, so the queue `C25 → C26 → C27` cannot run dry and "no authorized work" is never a valid state.
5. **Residual bottleneck documented, not "fixed" mid-run.** The binding constraint is compute: 3.07 core-s per permutation replay × 20k draws × 56 cells on 4 cores. The live process has already imported the engine, so mid-run code edits cannot help, draw floors cannot be reduced, and a restart would gamble the campaign. The correct handling is to let it run, monitor with 6–12 h wakeups, and measure — all of which is now encoded above.
6. **Session-ambiguity bottleneck removed (2026-11-19T22:31:49Z).** Verified live C25 state (runner ALIVE, PID 3901, 1/56 real cells, ETA ~2026-11-28T04:43Z) and refreshed `INITIAL_TASK_MESSAGE.md` + this file's "INITIAL TASK MESSAGE — NEXT SESSION" block with a single timestamped, ordered task list. C27-T1 remains fully staged (probe `scripts/probe_c27_venue_acquisition.py` + prereg `research_state/c27_prereg_20261119T215721Z.{json,md}`, `PRE_REGISTERED_BEFORE_COMPUTE`, launch blocked on `C26 ACCEPTANCE: PASS`) so the `C25 → C26 → C27` queue cannot run dry and no future session can truthfully claim "no authorized work."

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
- Preserve literal gate tokens (additional, for reports/history): `C21 ACCEPTANCE: PASS`, `C22 ACCEPTANCE: PASS`, `C23 ACCEPTANCE: PASS`, `C24_UNDERPOWERED`, `C26_UNDERPOWERED`, `PATH_ANCHOR_MISMATCH`, `SUPERSEDED_BY_C24`, `DESCRIPTIVE_NO_INFERENCE`, `c24_liquidation_fidelity_probe_20261119T013154Z.json`, `c24_prereg_20261119T013154Z.{json,md}`, `c24_ckpt_{arm}_{venue}_{fold}_20261119T013154Z.json`, `c25_ckpt_{arm}_{venue}_{fold}`, `c25_prereg`, `c25_funding_model_disclosure`, `c25_decision_verdict_{arm}`, `c25_decision_verdict_CONSOLIDATED`, `c22_prereg_{TS}.{json,md}`, `c22_mexc_fold_campaign_{TS}.json`, `c22_mexc_fold_episode_edge_{TS}.json`, `c22_mexc_fold_placebo_{TS}.json`, `c22_mexc_fold_census_{TS}.json`, `c22_decision_verdict_mexc_stability_{TS}.json`, `c22_pooled_stability_synthesis_{TS}.json`, `c22_decision_verdict_CONSOLIDATED_{TS}.json`, `c23_prereg_{TS}.{json,md}`, `c23_bitget_fold_campaign_{TS}.json`, `c23_bitget_fold_episode_edge_{TS}.json`, `c23_bitget_fold_placebo_{TS}.json`, `c23_bitget_fold_census_{TS}.json`, `c23_decision_verdict_bitget_stability_{TS}.json`, `c23_pooled_stability_synthesis_{TS}.json`, `c23_decision_verdict_CONSOLIDATED_{TS}.json`, `scripts/run_c22_mexc_campaign.py`, `scripts/run_c24_margin_fidelity_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/probe_hyperliquid_blocker.py`, `research_state/timing_okx.json`, `research_state/timing_binance_um.json`, `research_state/cache/binance_um_funding_20230101_20260928`, `research_state/cache/mexc_funding_20230101_20260928`, `research_state/cache/bitget_funding_20230101_20260928`, `research_state/cache/bitget_1h_multiyear_20230101_20260928/`, `research_state/universe_bitget_multiyear_verified.json`, `universe_mexc_multiyear_verified.json`, `spec_rebound_confirmation_adjudication_20261116T054000Z`, `20261116T063500Z`, `2026-08-19T16:00Z`, `2026-09-21T16:00Z`, `slippage_pct=0.0005`, `rsi_period=21`, `rsi_threshold=20`, `target_pct=9`, `gross_cap_pct=120`, `total_pnl=-55057.45`... (line truncated to 2000 chars)
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `C23-T1`, `verify_c23_focus_campaign.py`, `fetch_bitget_perp_archive.py`, `probe_c23_venue_acquisition.py`, `status_c23.sh`, `tests/test_c23_campaign_20261118.py`, `C24-T1`, `c24_prereg_20261119T013154Z`, `status_c24.sh`, `verify_c24_focus_campaign.py`, `run_c24_durable.sh`, `tests/test_c24_campaign.py`, `FIDELITY_ANCHOR_REPRODUCED`, `C24_REOPENS_C1_C23`, `C24_NO_GO_ROBUST_TO_MARGIN`, `C25-T1`, `C25_REOPENS_C1_C24`, `C25_NO_GO_ROBUST_TO_COST`, `COST_ANCHOR_REPRODUCED`, `UNAVAILABLE_FUNDING`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`, `probe_c25_okx_funding_retention.py`, `c25_funding_model_disclosure_20261119T091800Z`, `VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY`, `C26-T1`, `PATH_ANCHOR_REPRODUCED`, `C26_REOPENS_C1_C25`, `C26_NO_GO_ROBUST_TO_PATH`, `C27-T1`.

---

## KEY FILES

- Handoff/state: `HANDOFF.md` (single durable handoff), `INITIAL_TASK_MESSAGE.md` (pointer), `README.md`, `research_state/strategy_spec.md`.
- C25 ops: `scripts/status_c25.sh`, `scripts/eta_c25.sh`, `scripts/check_c25_anchor.sh`, `scripts/run_c25_durable.sh`, `scripts/verify_c25_focus_campaign.py`.
- C25 artifacts: `research_state/c25_prereg_20261119T045500Z.json`, `research_state/c25_ckpt_{arm}_{venue}_{fold}_20261119T045500Z.json`, `research_state/c25_decision_verdict_{arm,CONSOLIDATED}_20261119T045500Z.json`, run log `research_state/c25_run_20261119T172418Z.log`.
- C26: `scripts/run_c26_path_fidelity_campaign.py`, `scripts/run_c26_durable.sh`, `scripts/status_c26.sh`, `scripts/verify_c26_focus_campaign.py`, `tests/test_c26_campaign.py`, `research_state/c26_prereg_20261119T121500Z.{json,md}`.
- Engine: `src/backtest/engine.py`, `src/strategy/config.py`, `scripts/run_portfolio.py`.