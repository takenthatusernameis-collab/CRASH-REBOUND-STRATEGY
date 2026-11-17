# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-17T20:27:48Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting; real-market, cross-venue (OKX + Binance UM) evidence chain feeding C21.
**CLOSURE CERTIFICATION RE-VERIFIED (live venv, 2026-11-17T11:10:06Z):** `pytest tests/ -q` = `1047 passed, 1 skipped` (26.58s). All C1–C20 gates green with literal tokens: `session_gate.py` `21/21 checks passed`, `verify_campaign_evidence.py` `EVIDENCE VERIFIED`, `C20 ACCEPTANCE: PASS` (pooled `NO_GO`), `C19 ACCEPTANCE: PASS`, `C14 ACCEPTANCE: PASS`, `C13 ACCEPTANCE: PASS`, `C6 ACCEPTANCE: PASS`. **The C1–C20 research program is COMPLETE and certified `NO_GO`; nothing in C1–C20 remains to run. Do NOT relaunch C20, do not re-run pytest/gates for closure, do not commit unless asked.**
**BINDING NEXT FOCUS CAMPAIGN `C21` PREREGISTERED (gate RED until executed):** `research_state/c21_prereg_20261117T064408Z.{json,md}` (status `PRE_REGISTERED_BEFORE_COMPUTE`) + canonical runner `scripts/run_c21_cross_venue_campaign.py` + verifier `scripts/verify_c21_focus_campaign.py`. **Verified 2026-11-17T19:56:30Z (this session):** the previous C21 launch is stalled and is an execution bottleneck: PID 2803 is gone, `research_state/c21_run_20261117T195156Z.log` has advanced only through the OKX 2023 census, and 0/12 required C21 artifacts exist. The next session must not narrate or restart C20; it must resume C21 with `--jobs 4 --resume`, preserve every existing artifact, and drive the verifier to `C21 ACCEPTANCE: PASS`. **The next session's primary heavy task is to remove the stalled-run bottleneck by resuming C21 end-to-end and validating all 12 required artifacts.**

> **PROGRAM STATE: C1–C20 COMPLETE and certified `NO_GO`. C21 is the open binding work; its prior runner is inactive before artifact creation.**

**Phase O artifact timestamp (binding, `research_state/episode_edge_okx_full.json`):** `2026-11-13T23:38:47Z` · **Session done-gate:** `scripts/session_gate.py` = `21/21 checks passed` (re-verified 2026-11-17T19:56:30Z, green).

**C21 BLOCKER (2026-11-17T20:27:48Z):** the prior C21 runner is inactive before artifact creation; the next session must resume C21 with `--jobs 4 --resume` and obtain all 12 required artifacts and `C21 ACCEPTANCE: PASS`. Do not treat the stale PID/log as active progress.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T20:27:48Z — C21 STALLED, RESUME REQUIRED)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data). **Priority by repo scope:** C1–C20 are complete/certified `NO_GO`; the single binding next task is **C21-T1** (cross-venue temporal walk-forward & regime-stability of the spec-literal rule). C21 is preregistered and its gate is RED. The prior run (`PID 2803`, log `research_state/c21_run_20261117T195156Z.log`) is not active and produced only:

```text
[C21] OKX fold 2023: symbols=34
[census] OKX: events=345 signal_pass=95 trades=21 matched=21 unexplained=32
```

The previous handoff's "running" claim is stale and must not be repeated.

**Environment ready NOW (bottleneck removed):** durable `.venv` is present at repo root (Python 3.12.3, `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`) via `scripts/bootstrap_env.sh`. Run with `PYTHONPATH=. .venv/bin/python ...`. If `.venv` is missing on a fresh runner, run `bash scripts/bootstrap_env.sh` FIRST.

**Execute in order. No planning-only stops, no liveness narration as progress, no inference-only churn, no handoff-refresh-as-progress, no relaunching C20.**

**BOTTOM LINE UP FRONT (verified 2026-11-17T19:56:30Z):**
- Closure (re-verified 2026-11-17T11:10:06Z): `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` → `1047 passed, 1 skipped`; `scripts/session_gate.py` → `21/21 checks passed` (Phase O binding `2026-11-13T23:38:47Z`); `scripts/verify_campaign_evidence.py` → `EVIDENCE VERIFIED`; `scripts/verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS`; `scripts/verify_c19_focus_campaign.py` → `C19 ACCEPTANCE: PASS`; `scripts/verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS`; `scripts/verify_c13_focus_campaign.py` → `C13 ACCEPTANCE: PASS`; `scripts/verify_next_focus_campaign.py` → `C6 ACCEPTANCE: PASS`.
- **C21 (open, blocked):** no `run_c21_cross_venue_campaign.py` process is active; `research_state/c21_run_20261117T195156Z.log` is only 108 bytes; the verifier reports 13 missing requirements and `0/12` required artifacts. **Resume C21, do not start a duplicate campaign.** The canonical command is `PYTHONPATH=. .venv/bin/python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume > research_state/c21_run_<UTC>.log 2>&1 &`.
- **Bottleneck to clear first:** the prior C21 process has exited before writing any required artifact. Use `--resume` so completed work is reused; do not delete or rename existing `c21_*_20261117T064408Z.*` artifacts. If another canonical C21 process is active, inspect its PID/log and let it finish rather than launching a rival run.
- Final verdict (C1–C20): `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` token `NO_GO`, `research_program_complete: true`.

1. **Primary task (C21-T1, heavy):** resume the canonical C21 campaign. First run `ps -ef | grep run_c21_cross_venue_campaign.py | grep -v grep`, then start only if absent: `PYTHONPATH=. .venv/bin/python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume > research_state/c21_run_<UTC>.log 2>&1 &`. Monitor the log to completion; do not use a short foreground timeout. The runner must produce all four folds for both venues and all 12 required artifacts in `c21_prereg_20261117T064408Z.json`.
2. **Gate requirements (must satisfy):** `folds` must be `["2023","2024","2025","2026YTD"]` (or equivalent objects) in per-venue fold artifacts; episode-edge must record `episode_block_bootstrap.resamples >= 20000` and `temporal_edge_permutation.draws_evaluated >= 20000`; placebo must record `placebo.runs >= 2000`; pooled synthesis must record `pooled_venue_blocked_bootstrap.draws >= 20000`. Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` must print `C21 ACCEPTANCE: PASS`.
3. **Performance/correctness gotcha:** `scripts/run_c20_cross_venue_campaign.py` caps draws at `MAX_PERMUTATION_DRAWS=300`/`MAX_PLACEBO_DRAWS=500` and canonical portfolio replay is expensive (~90s order-of-magnitude). The C21 path uses memoized/vectorized replay and checkpoint+resume with `jobs=4` while preserving full-universe canonical replay parity with C20. Do not reduce draw counts to make the gate pass.
4. **After C21 is green:** re-run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` (must stay `1047 passed, 1 skipped`) and `scripts/session_gate.py` (must stay `21/21 checks passed`), then update this HANDOFF with new timestamped literals (keep all tokens below).
5. **If the C21 battery is already complete on disk** (future resume): just run `verify_c21_focus_campaign.py`; if green, do not recompute — refresh this HANDOFF and stop.
6. **If operator explicitly authorizes a NEW direction beyond C21:** requires **new prereg + new data** (Hyperliquid moving-tail acquisition exhausted, earliest ~2026-04-21; no new-venue network). Preregister before compute, acquire/specify new venue/window, treat as a fresh binding campaign. **Do not invent a same-data C22+ rerun of C21.**
7. **Never:** relabel cross-venue as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21), synthetic gap-fill as verified, relax `SPEC_LITERAL_NEXT_OPEN`, fabricate `GO`/`STABLE_POSITIVE_SUBSET`, edit completed C1–C20 campaign artifacts to change results, or commit unless asked.

**Terminal state for C1–C20: closed `NO_GO`, certified green. C21 is the open binding work — resume and complete it.**

---

## NEXT FOCUS — NO-AVOIDANCE BINDING (2026-11-17T20:27:48Z)

Future agents **cannot avoid heavy work**: the binding next campaign is **C21-T1**, whose gate `scripts/verify_c21_focus_campaign.py` is **RED until the full battery is executed**. The prior runner stalled before artifacts existed; that is not progress. Accepted progress is therefore **only**:
- **C21 executed end-to-end:** all `c21_*_20261117T064408Z` artifacts produced (per-venue fold campaign + episode edge + placebo + census, per-venue verdict, pooled stability synthesis, consolidated final), with `C21 ACCEPTANCE: PASS` (token `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` with a power curve) and an honest pooled verdict.
- **Plus closure stays green:** `pytest tests/ -q` = `1047 passed, 1 skipped` and `session_gate.py` = `21/21 checks passed` with literal Phase O timestamp `2026-11-13T23:38:47Z`.
- **Plus** `verify_campaign_evidence.py` = `EVIDENCE VERIFIED`, `verify_c20_focus_campaign.py` = `C20 ACCEPTANCE: PASS`, `verify_c19_focus_campaign.py` = `C19 ACCEPTANCE: PASS`, `verify_c14_focus_campaign.py` = `C14 ACCEPTANCE: PASS`, `verify_c13_focus_campaign.py` = `C13 ACCEPTANCE: PASS`, `verify_next_focus_campaign.py` = `C6 ACCEPTANCE: PASS`, `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

Not progress: reading, planning, rewriting this file, refreshing timestamps, "monitoring" without artifact changes, relaunching C20, or inventing a same-data C22+ rerun. **Do NOT relaunch `scripts/finish_c20_detached_durable.sh`. Do NOT commit unless explicitly asked.**

## LIVE STATE VERIFIED (2026-11-17T19:56:30Z)

- **Host capacity:** `nproc=4`.
- **Venv:** `.venv/bin/python` Python 3.12.3 bootstrapped with required deps via `scripts/bootstrap_env.sh`.
- **Processes:** No `run_c21_cross_venue_campaign.py` process is active. Prior log: `research_state/c21_run_20261117T195156Z.log` (108 bytes; OKX 2023 census only). No `finish_c20`/`run_c20`/supervisor processes observed.
- **C20:** PASS, terminal (15/15 artifacts). C1–C20 consolidated `NO_GO`, `research_program_complete: true` in `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`.
- **C21 (open, binding, blocked):** prereg `research_state/c21_prereg_20261117T064408Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`), runner `scripts/run_c21_cross_venue_campaign.py`, verifier `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (13 requirements missing; 0/12 required artifacts on disk). `research_state/timing_okx.json`, `timing_binance_um.json`, `timing_c21_census.json`, `zz_timing_c21_census.json` are prior timing probes — not C21 evidence; do not rename/copy into required C21 artifacts.
- **Certification (re-verified 2026-11-17T11:10:06Z):** `pytest tests/ -q` → `1047 passed, 1 skipped`; `session_gate.py` → `21/21 checks passed`; `verify_campaign_evidence.py` → `EVIDENCE VERIFIED`; `verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS`; `verify_c19_focus_campaign.py` → `C19 ACCEPTANCE: PASS`; `verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS`; `verify_c13_focus_campaign.py` → `C13 ACCEPTANCE: PASS`; `verify_next_focus_campaign.py` → `C6 ACCEPTANCE: PASS`; `probe_hyperliquid_blocker.py` → `FULL_283D_BLOCKED_BY_API_RETENTION`; `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (expected while C21 is incomplete).

## BOTTLENECKS REMOVED / TO UNBLOCK

1. **Deps/env bottleneck REMOVED:** `.venv` bootstrapped via `scripts/bootstrap_env.sh` (Python 3.12.3 + deps). Fresh runner: `bash scripts/bootstrap_env.sh`.
2. **"Not running" bottleneck REMOVED:** canonical C21 should be resumed with `--jobs 4 --resume`; no duplicate run while a canonical runner is active.
3. **"Do nothing" paralysis removed:** C21-T1 preregistered and gate RED — heavy execution is mandatory.
4. **No C20/stale-lock blockers:** no `finish_c20`/`run_c20` processes, no supervisor lock observed.
5. **Current blocker (execution):** the prior C21 runner exited before artifact creation. Resume it and require all 12 artifacts plus `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`.
6. **Compute-performance gotcha:** C20 draw caps (`MAX_PERMUTATION_DRAWS=300`/`MAX_PLACEBO_DRAWS=500`) and ~90s replay cost mean naive 20k/2k draws are prohibitive; C21 path satisfies prereg draw counts efficiently (memoize/vectorize/checkpoint) with `--jobs 4` and still passes the strengthened verifier.
7. **Acquisition CLOSED:** Hyperliquid moving-tail exhausted (earliest ~2026-04-21; `FULL_283D_BLOCKED_BY_API_RETENTION`); no new-venue network. C21 uses already-verified OKX + Binance UM multi-year archives only.

## C21 SPEC & DECISION RULES (prereg `c21_prereg_20261117T064408Z`, PRE_REGISTERED_BEFORE_COMPUTE) — OPEN

- **C21-T1:** quantify temporal/regime stability of the spec-literal crash-rebound edge on two independent real venues, with pre-specified BH multiplicity correction and an honest pooled verdict (`STABLE_POSITIVE_SUBSET` / `NO_GO` / `UNDERPOWERED`).
- **Config fixed:** `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, rebound short 9%/48h, ETH hedge on, $5M volume gate, gross cap 120%, seed 20261121.
- **Folds (pre-specified):** 2023, 2024, 2025, 2026YTD (2026-01-01..2026-09-28). **Strata (pre-specified):** `crash_severity` (RSI 0–10/10–15/15–20), `btc_trend` (down/flat/up 7d), `funding_regime` (neg/neu/pos). No post-hoc invention.
- **Inference:** per venue-fold 20,000-draw episode-block bootstrap CI95 (spot/hedge/rebound/total), 20,000-draw permutation p, 2,000-subset portfolio placebo, BH correction (α=0.05) across 8 venue-fold tests + separate stratum family, pooled venue-blocked bootstrap + cross-venue sign concordance. Power floor: ≥10 trades / ≥5 episodes / ≥5 distinct crash days else `UNDERPOWERED` + power curve.
- **Decision rule:** `STABLE_POSITIVE_SUBSET` only if a pre-specified stratum survives BH with bootstrap CI excluding 0 & positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, N≥floor, AND same-direction effect in the other venue (or flagged single-venue exploratory). Otherwise `NO_GO` or `UNDERPOWERED`.
- **C21 is cross-venue** (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence.

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
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate campaign while canonical C21 is active; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C22+ rerun of C21.** New direction beyond C21 needs new prereg + new data + explicit operator authorization.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results.
- No silent change to canonical baseline. C1–C20 `NO_GO` stands.
- **Do not commit unless explicitly asked.**
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C21 (open, binding): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, prior stalled log `research_state/c21_run_20261117T195156Z.log`, planned `research_state/c21_*_20261117T064408Z.json`, `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`
