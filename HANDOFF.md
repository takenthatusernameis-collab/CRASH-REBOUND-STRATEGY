# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T06:24:04Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate, do not relaunch C20). **C21-T1 is COMPLETE** — temporal/regime stability of the spec-literal crash-rebound edge across pre-specified folds on two independent real venues; gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). No further campaign work is authorized beyond C21 without new prereg + new data + explicit operator authorization; do NOT invent a same-data C22+ rerun. If no explicit user override exists, future work is verification + await direction — never planning-only loops on closed campaigns.

**Verified live/repo state (2026-11-18T06:18:49Z):** C21 runner is NOT active and none is needed — battery finished cleanly (`research_state/c21_run_20261118T061505Z.log` ends `C21 COMPLETE: per-venue=['NO_GO', 'NO_GO'] pooled=NO_GO consolidated=NO_GO`). Repo artifacts present now: **8/8 per-fold checkpoints** (`c21_ckpt_okx_2023/2024/2025/2026YTD`, `c21_ckpt_binance_um_2023/2024/2025/2026YTD`, stamp `20261117T064408Z`). **12/12 required gate artifacts** present (OKX fold bundle `NO_GO` trades=113 pnl=-54799.23; Binance UM fold bundle `NO_GO` trades=136 pnl=-70071.39; `c21_decision_verdict_okx_stability_*`, `c21_decision_verdict_binance_um_stability_*`, `c21_pooled_stability_synthesis_*` pooled=NO_GO draws=20000, `c21_decision_verdict_CONSOLIDATED_*` final=NO_GO ts=2026-11-18T06:15:08Z). `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`. No compute bottleneck (parallel strata fix committed, ~4x speedup, draw counts preserved); `_build_pooled` TypeError from an earlier run did not recur — final run completed cleanly.

> **PROGRAM STATE: C1–C20 COMPLETE, certified `NO_GO`; C21-T1 COMPLETE, gate `C21 ACCEPTANCE: PASS` (12/12 artifacts, 8/8 checkpoints), consolidated `NO_GO`. No open binding campaign.**

**Closure tokens (binding):** `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed` (Phase O timestamp `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; C20/C19/C14/C13/C6 gates = `PASS`; `scripts/probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T06:18:49Z — C21 COMPLETE; GATE PASS; NO ACTIVE RUNNER)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data).
**Environment ready NOW:** durable `.venv` at repo root (Python 3.12.3 + `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`). Run with `PYTHONPATH=. .venv/bin/python ...`. If `.venv` is missing on a fresh runner, run `bash scripts/bootstrap_env.sh` FIRST.
**Bottom line up front (verified 2026-11-18T06:18:49Z):**
- C1–C20 closure green (`NO_GO`). Do not relitigate/relaunch C20 and do not re-run pytest/gates for closure unless you changed code.
- **C21-T1 COMPLETE** — gate `C21 ACCEPTANCE: PASS`, all 12 artifacts + 8 checkpoints present, consolidated verdict `NO_GO` (OKX `NO_GO`, Binance UM `NO_GO`, pooled `NO_GO`, 72 pooled stratum tests 0 survivors). No further campaign work is authorized beyond C21 without new prereg + new data + explicit operator authorization; do NOT invent a same-data C22+ rerun.
- No runner is active and none is needed. Do not start `run_c21_cross_venue_campaign.py` or `run_c21_detached_durable.sh` — the battery finished cleanly (`research_state/c21_run_20261118T061505Z.log` ends `C21 COMPLETE: per-venue=['NO_GO', 'NO_GO'] pooled=NO_GO consolidated=NO_GO`).
- Closure checks already green this session: `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed` (Phase O `2026-11-13T23:38:47Z`).

**Immediate next action (verification only, no campaign work):**
1. **Confirm gate green:** `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → expect `C21 ACCEPTANCE: PASS` (tokens `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED`). Current token: `NO_GO`.
2. **Confirm artifacts:** `ls research_state/c21_ckpt_* | wc -l` → 8; `ls research_state/c21_*_20261117T064408Z.json | grep -v prereg | grep -v ckpt | wc -l` → 12.
3. **No active runner:** `ps -eo pid,ppid,etime,time,stat,pcpu,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep` → expect empty. Do not start a runner; none is needed.
4. **Await explicit operator direction** for any work beyond C21 (new prereg + new data required). Do not plan, rewrite, or relaunch campaigns without authorization.

**No-avoidance rule:** while `scripts/verify_c21_focus_campaign.py` prints anything other than `C21 ACCEPTANCE: PASS`, the session is not done and heavy execution is mandatory. It currently prints `PASS` — campaign execution is complete; do not manufacture further work on the same data.
---

## BINDING CAMPAIGN — C21-T1 CANNOT BE AVOIDED

The only accepted C21 terminal state is **`C21 ACCEPTANCE: PASS`** with all 12 artifacts produced by the canonical runner. Accepted tokens: `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` (with a quantified power curve and an honest pooled verdict).

**Not progress:** reading, planning, rewriting this file, refreshing timestamps, "monitoring" without artifact changes, relaunching C20, inventing a same-data C22+ rerun, or reducing draw counts. A runner with 0/12 artifacts is not accepted progress.

**No-avoidance rule:** if `scripts/verify_c21_focus_campaign.py` prints `C21 ACCEPTANCE: FAIL`, the session is not done. Heavy execution is mandatory until the gate is green.

**If the runner is progressing but slow:** it is compute-bound, not stuck. Do NOT kill a healthy 4-core runner to "restart faster." Verify liveness by child-worker CPU + checkpoint count + log, not by log silence.

---

## BOTTLENECK REMOVED THIS SESSION (2026-11-17T22:14:00Z)

**Root cause (was):** `build_strata` ran the 9 pre-specified stratum permutations per fold **serially** (`_permutation_for_keys` hard-coded `jobs=1`, each doing 20,000 draws on ONE core). With 9 bins × 20k draws × 8 venue-folds on 1 core, C21 needed **~30+ hours** and used only **1 of 4 cores** (observed ~100% single-core, load ~1.3). The intended `STRATA_PERMUTATION_DRAWS = 2000` constant existed but was never wired; the code comment claiming a 2k strata null was not implemented.

**Fix applied (draw-count preserving — NO spec relaxation):**
1. Threaded `jobs` through `build_strata(... , jobs)` → `_permutation_for_keys(..., jobs)` → `_c21_conditional_permutation_null(..., jobs)`, so every stratum permutation now runs on the **4-worker fork pool** instead of serially. **Draw counts unchanged: 20,000 per stratum bin (main episode permutation, bootstrap, placebo all still 20k/20k/2k).**
2. Made `_fast_parallel_draws` **fail-closed**: it now runs the exact `_fast_validated` canonical-vs-fast check once in the parent before any pool dispatch, and falls back to the serial (canonical) path if validation fails. Previously the pool path could dispatch unvalidated fast draws.

**Verified after fix:** process tree sustains **~373–386% CPU** (all 4 cores; 4 workers each ~95–98%) vs the prior ~100% (1 core) — a **~4x** speedup on the heavy permutation/placebo/strata phases. Fail-closed validation prints `[C21][fast-path validated] ... diff=0.00e+00`. Honest ETA is now **~5–6 hours** for the full 8-fold battery (down from ~30+ hours), fully resumable via per-fold checkpoints.

**Committed in checkpoint `5c7226d`:** the 4-way strata pooling and fail-closed fast-path validation are present in `scripts/run_c21_cross_venue_campaign.py`; no uncommitted campaign-code change remains. Do not commit handoff-only edits unless explicitly asked.

---

## BOTTLENECKS REMOVED / OPEN

1. **Serial strata permutations REMOVED (this session):** now 4-way pool; ~4x faster; all 20k draws preserved.
2. **Unvalidated parallel draws REMOVED (this session):** `_fast_parallel_draws` is fail-closed (validates once in-parent; falls back to canonical on failure).
3. **Deps/env REMOVED:** `.venv` bootstrapped (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
4. **Duplicate-runner risk REMOVED:** canonical C21 is active with `--jobs 4 --resume`; `scripts/run_c21_detached_durable.sh` refuses duplicates via `pgrep` (caveat: invoke from a command line not containing the script name).
5. **Stale PID in prior handoff REMOVED:** prior text cited PID 14019; that serial runner was stopped this session (it was mid-`build_strata` with 0 checkpoints). The live runner is PID **21945**.
6. **"Do nothing" paralysis REMOVED:** C21-T1 is preregistered and its gate is RED — heavy execution is mandatory.
7. **Progress durability:** the runner writes per-fold checkpoints `research_state/c21_ckpt_*` after each fold; `--resume` reuses them. A crash loses at most the in-flight fold. (1 checkpoint so far: OKX fold 2023; OKX fold 2024 in progress.)
8. **Progress visibility:** the log prints only at fold boundaries, on each `_fast_validated` (re)validation, and census; worker PIDs rotate as each parallel phase starts. Do not judge liveness by log silence or worker PID changes; use `ps` CPU time + child-worker count + checkpoint count + artifact count.
9. **Compute-performance:** C21 uses a validated exact fast replay (`_fast_portfolio_pnl`, fail-closed `_fast_matches_canonical`) with a 4-fork pool for 20k permutation / 2k placebo / 9×20k strata draws. **Do not reduce draw counts.**
10. **Acquisition CLOSED:** Hyperliquid moving tail exhausted (earliest ~2026-04-21; `FULL_283D_BLOCKED_BY_API_RETENTION`); no new-venue network. C21 uses already-verified OKX + Binance UM multi-year archives only.

---

## C21 SPEC & DECISION RULES (prereg `c21_prereg_20261117T064408Z`, PRE_REGISTERED_BEFORE_COMPUTE) — OPEN

- **C21-T1:** quantify temporal/regime stability of the spec-literal crash-rebound edge on two independent real venues, with pre-specified BH multiplicity correction and an honest pooled verdict (`STABLE_POSITIVE_SUBSET` / `NO_GO` / `UNDERPOWERED`).
- **Config fixed:** `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, rebound short 9%/48h, ETH hedge on, $5M volume gate, gross cap 120%, seed 20261121.
- **Folds (pre-specified):** 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28). **Strata (pre-specified):** `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos). No post-hoc invention.
- **Inference:** per venue-fold 20,000-draw episode-block bootstrap CI95 (spot/hedge/rebound/total), 20,000-draw permutation p, 2,000-subset portfolio placebo, BH correction (α=0.05) across 8 venue-fold tests + separate stratum family, pooled venue-blocked bootstrap + cross-venue sign concordance. Power floor: ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.
- **Decision rule:** `STABLE_POSITIVE_SUBSET` only if a pre-specified stratum survives BH with bootstrap CI excluding 0 & positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, N≥floor, AND same-direction effect in the other venue (or flagged single-venue exploratory). Otherwise `NO_GO` or `UNDERPOWERED`.
- **C21 is cross-venue** (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

## C20 CROSS-VENUE REFERENCE NUMBERS (verified, for sanity-checking C21 outputs)

From `research_state/timing_okx.json` / `timing_binance_um.json` (C20 spec-literal, full multi-year window, `SPEC_LITERAL_NEXT_OPEN`, wall_seconds 98.8 / 110.1):
- **OKX:** `num_trades=113`, `total_pnl=-55057.45`
- **Binance UM:** `num_trades=136`, `total_pnl=-70309.57`
- Both negative → C20 pooled `NO_GO` (`research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`). C21 fold results should be broadly consistent in sign; a wildly divergent C21 fold result is a red flag to investigate, not to accept.

## C1–C20 CLOSED STATE (historical, do not relitigate)

- **C20 (`20261116T063500Z`):** spec-literal cross-venue replication + pooled synthesis. Both venues `NO_GO`; pooled `NO_GO`. Gate: `scripts/verify_c20_focus_campaign.py`.
- **C19 (`C19-T1`):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2–T5 NO_GO consolidated. Gate: `scripts/verify_c19_focus_campaign.py`.
- **C14 (`20261116T001200Z`):** native C14 underpowered/fragile (7 trades, 3 episodes). Gate: `scripts/verify_c14_focus_campaign.py`.
- **C13:** config-matched native C13 complete. Gate: `scripts/verify_c13_focus_campaign.py`.
- **C6 (`C6-T1`):** cross-venue context OKX+Binance UM pooled underpowered, `campaign_results_real_okx_multiyear`, `is_hyperliquid_venue_data=false`. Gate: `scripts/verify_next_focus_campaign.py`.
- **Acquisition CLOSED/exhausted:** Hyperliquid moving tail (`full_window_served=false`, earliest ~2026-04-21; `hyperliquid_retention_probe_next_20261116T054408Z.json`).

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed.
- No post-hoc stratum/fold invention in C21; folds and strata fixed in prereg before compute.
- **Do not reduce draw counts.** The 20k/20k/2k floors are preserved; the this-session fix was pure parallelization + fail-closed validation, not a draw reduction.
- No inference-only churn on exhausted C14 native data; C1–C20 closed.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate C21 campaign while the canonical runner is active; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C22+ rerun of C21.** New direction beyond C21 needs new prereg + new data + explicit operator authorization.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results.
- No silent change to canonical baseline. C1–C20 `NO_GO` stands.
- **Do not commit unless explicitly asked.**
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`.

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`
- C21 (open, binding): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, active log `research_state/c21_run_20261117T215941Z.log`, per-fold checkpoints `research_state/c21_ckpt_*`, planned `research_state/c21_*_20261117T064408Z.json`, `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`