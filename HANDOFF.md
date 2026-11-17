# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-17T20:30:00Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting; real-market, cross-venue (OKX + Binance UM) evidence chain feeding C21.
**C1–C20 CLOSED & CERTIFIED `NO_GO` (do not relitigate, do not relaunch C20).** `pytest tests/ -q` = `1047 passed, 1 skipped`; `scripts/session_gate.py` = `21/21 checks passed` (Phase O binding `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; `C20 ACCEPTANCE: PASS`, `C19 ACCEPTANCE: PASS`, `C14 ACCEPTANCE: PASS`, `C13 ACCEPTANCE: PASS`, `C6 ACCEPTANCE: PASS`; `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.
**OPEN BINDING WORK — `C21` (preregistered, gate RED):** `research_state/c21_prereg_20261117T064408Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`) + runner `scripts/run_c21_cross_venue_campaign.py` + verifier `scripts/verify_c21_focus_campaign.py`. **The single next task is C21-T1: drive the canonical C21 runner to produce all 12 required artifacts and make `verify_c21_focus_campaign.py` print `C21 ACCEPTANCE: PASS`.**

> **PROGRAM STATE: C1–C20 COMPLETE, certified `NO_GO`. C21 is the only open work; its runner is currently mid-compute with 0/12 artifacts written.**

**Phase O artifact timestamp (binding, `research_state/episode_edge_okx_full.json`):** `2026-11-13T23:38:47Z` · **Session done-gate:** `scripts/session_gate.py` = `21/21 checks passed`.

**C21 LIVE-STATE CORRECTION (2026-11-17T20:30:00Z — supersedes the earlier "PID 2803 stalled" claim):** a canonical C21 runner **IS active**: PID **5175** (`python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume`, parent bash PID 5168, reparented to init). Verified R-state, 78.8% CPU, ~26 min CPU / ~32 min wall, 635 MB RSS, no swap. Its stdout/stderr are sockets with no reader; the file `research_state/c21_run_20261117T195156Z.log` (108 bytes, OKX 2023 census only) is a **stale abandoned log — not this process's output**. Verifier currently `FAIL` with `0/12` artifacts because **the runner writes per-venue artifacts only after all four folds complete in memory** (`run_venue_folds`, `scripts/run_c21_cross_venue_campaign.py:1115-1221`). This is a **progress-durability bottleneck**, not a wedge: the process is computing, but `--resume` cannot save partial work until a whole venue finishes.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T20:30:00Z — C21 MID-COMPUTE, DO NOT DUPLICATE)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data). **Priority by repo scope:** C1–C20 are complete/certified `NO_GO`; the single binding task is **C21-T1** (cross-venue temporal walk-forward & regime-stability of the spec-literal rule). C21 is preregistered and its gate is RED. **A canonical runner may still be active — do not start a rival run.**

**Environment ready NOW:** durable `.venv` at repo root (Python 3.12.3 + `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`). Run with `PYTHONPATH=. .venv/bin/python ...`. If `.venv` is missing on a fresh runner, run `bash scripts/bootstrap_env.sh` FIRST.

**Execute in order. No planning-only stops, no liveness narration as progress, no inference-only churn, no handoff-refresh-as-progress, no relaunching C20, no committing.**

**BOTTOM LINE UP FRONT (verified 2026-11-17T20:30:00Z):**
- C1–C20 closure green (see tokens at top). **Do not re-run pytest/gates for closure** unless you changed code.
- **C21 open/blocked:** runner possibly active; `0/12` required artifacts; `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (expected until artifacts exist).
- **Do NOT blindly relaunch.** First check for a live canonical process (Step 1). Only start if none is alive.
- Final C1–C20 verdict: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` token `NO_GO`, `research_program_complete: true`.

1. **Primary task (C21-T1, heavy): drive the canonical C21 campaign to completion.**
   a. Check for a live runner:
      `ps -eo pid,etime,time,stat,cmd | grep run_c21_cross_venue_campaign.py | grep -v grep`
   b. **If a runner is alive** (e.g. `python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume`): **do not start a second one.** Monitor it via `research_state/c21_run_<UTC>.log` if that is its redirect, or by artifact count: `ls research_state/c21_*_20261117T064408Z.json | wc -l` and `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py`. Wait for it to finish writing all 12 artifacts. If it dies before artifacts exist (check `kill -0 <pid>`), go to (c).
   c. **Only if NO runner is alive:** start the canonical resume run detached so it survives this turn:
      `bash scripts/run_c21_detached_durable.sh` (this refuses to start a duplicate if one is alive, then launches `--jobs 4 --resume` with `nohup` and a real log `research_state/c21_run_<UTC>.log`).
      Then monitor that log to completion (do not use a short foreground timeout; this is a multi-hour battery).
   d. The run must produce all 12 required artifacts named in the verifier: `c21_okx_fold_campaign_20261117T064408Z.json`, `c21_binance_um_fold_campaign_...`, `..._fold_episode_edge_...` (both venues), `..._fold_placebo_...` (both), `..._fold_census_...` (both), `c21_decision_verdict_okx_stability_...`, `c21_decision_verdict_binance_um_stability_...`, `c21_pooled_stability_synthesis_...`, `c21_decision_verdict_CONSOLIDATED_...`.

2. **Gate requirements (must satisfy — do not relax):** `folds` must be `["2023","2024","2025","2026YTD"]` (or equivalent objects) in per-venue fold artifacts; episode-edge must record `episode_block_bootstrap.resamples >= 20000` and `temporal_edge_permutation.draws_evaluated >= 20000`; placebo must record `placebo.runs >= 2000`; pooled synthesis must record `pooled_venue_blocked_bootstrap.draws >= 20000`. Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` must print `C21 ACCEPTANCE: PASS` (token `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` with a power curve, plus an honest pooled verdict).

3. **Known performance facts (from this repo's own timing probes):** canonical full-universe portfolio replay is ~93s (OKX) / ~140s (Binance UM) per full-window campaign. The C21 path uses a **validated exact fast replay** (`_fast_portfolio_pnl`, fail-closed parity check `_fast_matches_canonical`) with a fork pool (`--jobs 4`) and 20,000-draw / 2,000-subset targets. **Do not reduce draw counts to make the gate pass.**

4. **Progress-durability caveat (why you may see 0/12 for a long time):** `run_venue_folds` computes all four folds per venue in memory and writes the four per-venue artifacts only at venue end. If the runner dies mid-venue, `--resume` re-does that venue from scratch. **If you must restart after a crash, prefer keeping `--jobs 4` and let it finish; do not attempt to hand-edit artifacts.** A resume-safe improvement (optional, only if you must restart anyway) is to checkpoint per-fold results; but never fabricate or rename timing/probe files into required artifacts.

5. **After C21 is green:** re-run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` (must stay `1047 passed, 1 skipped`) and `scripts/session_gate.py` (must stay `21/21 checks passed`), then update this HANDOFF with new timestamped literals (keep all tokens below). **Do not commit unless explicitly asked.**

6. **If the C21 battery is already complete on disk** (future resume): just run `verify_c21_focus_campaign.py`; if green, do not recompute — refresh this HANDOFF and stop.

7. **If operator explicitly authorizes a NEW direction beyond C21:** requires **new prereg + new data** (Hyperliquid moving-tail acquisition exhausted, earliest ~2026-04-21; no new-venue network). Preregister before compute, acquire/specify new venue/window, treat as a fresh binding campaign. **Do not invent a same-data C22+ rerun of C21.**

8. **Never:** relabel cross-venue as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21), synthetic gap-fill as verified, relax `SPEC_LITERAL_NEXT_OPEN`, fabricate `GO`/`STABLE_POSITIVE_SUBSET`, edit completed C1–C20 campaign artifacts to change results, or commit unless asked.

**Terminal state for C1–C20: closed `NO_GO`, certified green. C21 is the open binding work — complete it.**

---

## NEXT FOCUS — NO-AVOIDANCE BINDING (2026-11-17T20:30:00Z)

Future agents **cannot avoid heavy work**: the binding next campaign is **C21-T1**, whose gate `scripts/verify_c21_focus_campaign.py` is **RED until the full battery is executed**. A runner that has produced 0/12 artifacts is not accepted progress. Accepted progress is **only**:
- **C21 executed end-to-end:** all `c21_*_20261117T064408Z` artifacts produced (per-venue fold campaign + episode edge + placebo + census, per-venue verdict, pooled stability synthesis, consolidated final), with `C21 ACCEPTANCE: PASS` (token `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` with a power curve) and an honest pooled verdict.
- **Plus closure stays green:** `pytest tests/ -q` = `1047 passed, 1 skipped` and `session_gate.py` = `21/21 checks passed` with literal Phase O timestamp `2026-11-13T23:38:47Z`.
- **Plus** `verify_campaign_evidence.py` = `EVIDENCE VERIFIED`, `verify_c20_focus_campaign.py` = `C20 ACCEPTANCE: PASS`, `verify_c19_focus_campaign.py` = `C19 ACCEPTANCE: PASS`, `verify_c14_focus_campaign.py` = `C14 ACCEPTANCE: PASS`, `verify_c13_focus_campaign.py` = `C13 ACCEPTANCE: PASS`, `verify_next_focus_campaign.py` = `C6 ACCEPTANCE: PASS`, `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

Not progress: reading, planning, rewriting this file, refreshing timestamps, "monitoring" without artifact changes, relaunching C20, or inventing a same-data C22+ rerun. **Do NOT relaunch `scripts/finish_c20_detached_durable.sh`. Do NOT commit unless explicitly asked.**

## LIVE STATE VERIFIED (2026-11-17T20:30:00Z)

- **Host capacity:** `nproc=4`; load ~2.0; 16 GB RAM, ~13.7 GB available; no swap in use.
- **Venv:** `.venv/bin/python` Python 3.12.3 bootstrapped via `scripts/bootstrap_env.sh`.
- **Processes:** canonical C21 runner **PID 5175** active (`--jobs 4 --resume`), parent bash 5168 reparented to init; R-state, 78.8% CPU, ~26 min CPU / ~32 min wall, 635 MB RSS. No `finish_c20`/`run_c20`/supervisor processes.
- **C20:** PASS, terminal (15/15 artifacts). C1–C20 consolidated `NO_GO`, `research_program_complete: true` in `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`.
- **C21 (open, binding, blocked):** prereg `research_state/c21_prereg_20261117T064408Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), runner `scripts/run_c21_cross_venue_campaign.py`, verifier → `C21 ACCEPTANCE: FAIL` (13 requirements missing; 0/12 required artifacts on disk). `research_state/timing_okx.json`, `timing_binance_um.json`, `timing_c21_census.json`, `zz_timing_c21_census.json` are prior timing probes — **not C21 evidence; do not rename/copy into required C21 artifacts.**
- **Certification:** `pytest` `1047 passed, 1 skipped`; `session_gate.py` `21/21 checks passed`; `verify_campaign_evidence.py` `EVIDENCE VERIFIED`; `verify_c20_focus_campaign.py` `C20 ACCEPTANCE: PASS`; `verify_c19_focus_campaign.py` `C19 ACCEPTANCE: PASS`; `verify_c14_focus_campaign.py` `C14 ACCEPTANCE: PASS`; `verify_c13_focus_campaign.py` `C13 ACCEPTANCE: PASS`; `verify_next_focus_campaign.py` `C6 ACCEPTANCE: PASS`; `probe_hyperliquid_blocker.py` `FULL_283D_BLOCKED_BY_API_RETENTION`; `verify_c21_focus_campaign.py` `C21 ACCEPTANCE: FAIL` (expected while C21 incomplete).

## BOTTLENECKS REMOVED / TO UNBLOCK

1. **Deps/env bottleneck REMOVED:** `.venv` bootstrapped (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
2. **"Not running" bottleneck REMOVED:** canonical C21 is active with `--jobs 4 --resume`; **do not launch a duplicate** while it is alive.
3. **"Do nothing" paralysis removed:** C21-T1 preregistered and gate RED — heavy execution is mandatory.
4. **No C20/stale-lock blockers:** no `finish_c20`/`run_c20` processes, no supervisor lock observed.
5. **Current blocker (progress durability):** the runner writes artifacts only at venue end; `--resume` cannot save partial folds. If the runner is alive, let it finish. If it dies, restart with `--jobs 4 --resume` and let it complete; never hand-fabricate artifacts.
6. **Compute-performance gotcha:** C20 caps (`MAX_PERMUTATION_DRAWS=300`/`MAX_PLACEBO_DRAWS=500`) and ~90–140s replay cost mean naive 20k/2k draws are prohibitive; C21 satisfies prereg draw counts via a **validated exact fast replay + fork pool** while preserving full-universe canonical parity with C20. Do not reduce draw counts.
7. **Acquisition CLOSED:** Hyperliquid moving tail exhausted (earliest ~2026-04-21; `FULL_283D_BLOCKED_BY_API_RETENTION`); no new-venue network. C21 uses already-verified OKX + Binance UM multi-year archives only.

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
- No inference-only churn on exhausted C14 native data; C1–C20 closed.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate C21 campaign while the canonical runner is active; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C22+ rerun of C21.** New direction beyond C21 needs new prereg + new data + explicit operator authorization.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results.
- No silent change to canonical baseline. C1–C20 `NO_GO` stands.
- **Do not commit unless explicitly asked.**
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C21 (open, binding): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, stale log `research_state/c21_run_20261117T195156Z.log` (ignore), planned `research_state/c21_*_20261117T064408Z.json`, `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`