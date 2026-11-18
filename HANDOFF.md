# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-18T07:32:06Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate, do not relaunch C20). **C21-T1 is COMPLETE** — temporal/regime stability of the spec-literal crash-rebound edge across pre-specified folds on two independent real venues; gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (2026-11-18T06:15:08Z). No further campaign work is authorized beyond C21 without **new prereg + new data + explicit operator authorization**; do NOT invent, preregister, or run a same-data C22+ rerun/variant. If no explicit user override exists, future work is verification + await direction — never planning-only loops on closed campaigns.

**Verified live/repo state (2026-11-18T07:32:06Z):** `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (pooled=`NO_GO`, consolidated final=`NO_GO`, ts=2026-11-18T06:15:08Z). No C21/C22 runner active; none needed. **8/8** per-fold checkpoints present (`c21_ckpt_okx_2023/2024/2025/2026YTD`, `c21_ckpt_binance_um_2023/2024/2025/2026YTD`, stamp `20261117T064408Z`) and **12/12** required gate artifacts present (OKX `NO_GO` trades=113 pnl=-54799.23; Binance UM `NO_GO` trades=136 pnl=-70071.39; `c21_decision_verdict_okx_stability_*`, `c21_decision_verdict_binance_um_stability_*`, `c21_pooled_stability_synthesis_*` pooled=NO_GO draws=20000; `c21_decision_verdict_CONSOLIDATED_*`). No C22 prereg/script/artifacts exist in-repo; `INITIAL_TASK_MESSAGE.md` pointer reconciled to this handoff (removed stale C22 claim). Working tree was clean at HEAD `67984e9` before this handoff update.

> **PROGRAM STATE: C1–C20 COMPLETE, certified `NO_GO`; C21-T1 COMPLETE, gate `C21 ACCEPTANCE: PASS` (12/12 artifacts, 8/8 checkpoints), consolidated `NO_GO`. No open binding campaign. No new data available (Hyperliquid `FULL_283D_BLOCKED_BY_API_RETENTION`); acquisition CLOSED/exhausted.**

**Closure tokens (binding):** `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed` (Phase O timestamp `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; C20/C19/C14/C13/C6 gates = `PASS`; `scripts/probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-18T07:32:06Z — C21 COMPLETE; GATE PASS; NO CAMPAIGN AUTHORIZED; AWAIT EXPLICIT DIRECTION)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data, OKX + Binance UM).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first.
**Verified (2026-11-18T07:32:06Z):** C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** — `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (consolidated `NO_GO`, 12/12 required artifacts, 8/8 checkpoints, stamp `20261117T064408Z`, final ts `2026-11-18T06:15:08Z`). No C21/C22 runner active. **No C22 prereg, script, or artifacts exist** — C22 is not authorized.
**Binding constraint:** acquisition CLOSED/exhausted (`probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`, earliest ~2026-04-21). All preregistered campaigns through C21 are closed `NO_GO`. **Do NOT invent, preregister, or run a same-data C22+ rerun/variant.** Any work beyond C21 requires **new prereg + new data + explicit operator authorization** (and must preserve closure tokens: `session_gate.py` `21/21 checks passed` `2026-11-13T23:38:47Z`, `verify_campaign_evidence.py` `EVIDENCE VERIFIED`, C20/C19/C14/C13/C6 gates `PASS`, `C19-T1`, `C14` `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`).

**Immediate next action (verification only, then stop):**
1. Confirm `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS` (tokens `STABLE_POSITIVE_SUBSET`/`NO_GO`/`UNDERPOWERED`; current `NO_GO`).
2. Confirm 8 checkpoints, 12 required artifacts, and no `run_c21`/`run_c22` process active.
3. **Await explicit operator direction.** Do not plan, rewrite, relaunch, or manufacture campaign work without authorization and new data/prereg.

**No-avoidance rule:** if `verify_c21_focus_campaign.py` ever prints anything other than `C21 ACCEPTANCE: PASS`, the session is not done — heavy execution to restore a green gate on the existing C21 battery is mandatory. While PASS, do not manufacture further work on the same data.
---

## BINDING CAMPAIGN — C21-T1 (SATISFIED 2026-11-18T06:15:08Z)

C21 terminal state achieved: **`C21 ACCEPTANCE: PASS`** (consolidated `NO_GO`, 12/12 artifacts, 8/8 checkpoints) produced by the canonical runner. Accepted tokens: `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED`. This section is historical/binding for gate semantics.

**Not progress (ever):** reading, planning, rewriting handoff without authorization, "monitoring" without artifact changes, relaunching C20, inventing a same-data C22+ rerun, or reducing draw counts.

**No-avoidance rule:** if `scripts/verify_c21_focus_campaign.py` ever regresses to `C21 ACCEPTANCE: FAIL`, the session is not done — heavy execution to restore a green gate on the existing C21 battery is mandatory until PASS. With PASS green, do not manufacture further work on the same data; await explicit direction + new prereg + new data for anything beyond C21.

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

1. **Serial strata permutations REMOVED:** 4-way pool; ~4x faster; all 20k draws preserved (committed).
2. **Unvalidated parallel draws REMOVED:** `_fast_parallel_draws` is fail-closed (validates once in-parent; falls back to canonical on failure).
3. **Deps/env REMOVED:** `.venv` bootstrapped (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
4. **Duplicate-runner risk REMOVED:** no C21 runner active; `scripts/run_c21_detached_durable.sh` refuses duplicates via `pgrep` (caveat: invoke from a command line not containing the script name). Do not start a runner.
5. **Stale PID/log references REMOVED:** prior in-progress notes (PID 21945 / in-flight fold state) are obsolete; C21 completed cleanly (log `research_state/c21_run_20261118T061505Z.log`, 12/12 artifacts, 8/8 checkpoints).
6. **"Do nothing" paralysis REMOVED:** C21-T1 executed to completion; gate is `C21 ACCEPTANCE: PASS` (consolidated `NO_GO`).
7. **Progress durability (historical):** per-fold checkpoints `research_state/c21_ckpt_*` written; `--resume` supported. Not needed now (complete).
8. **Progress visibility (historical):** log/fork-pool behavior noted; irrelevant while no runner is active.
9. **Compute-performance:** validated exact fast replay with 4-fork pool preserved 20k/20k/2k draws. **Do not reduce draw counts** in any future authorized campaign.
10. **Acquisition CLOSED (blocking for new campaigns):** Hyperliquid moving tail exhausted (earliest ~2026-04-21; `FULL_283D_BLOCKED_BY_API_RETENTION`); no new-venue network available in-repo. No heavy follow-on campaign is possible without new data + new prereg + explicit operator authorization. This is the binding constraint — do not invent a same-data C22+ rerun.

---

## C21 SPEC & DECISION RULES (prereg `c21_prereg_20261117T064408Z`, PRE_REGISTERED_BEFORE_COMPUTE) — COMPLETE (`NO_GO`)

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
- C21 (complete, `NO_GO`, gate PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, final log `research_state/c21_run_20261118T061505Z.log`, per-fold checkpoints `research_state/c21_ckpt_*` (8), artifacts `research_state/c21_*_20261117T064408Z.json` (12 excl. prereg), `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`