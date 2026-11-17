# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-17T11:10:06Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting; real-market, cross-venue (OKX + Binance UM) evidence chain feeding C21.
**CLOSURE CERTIFICATION RE-VERIFIED THIS SESSION (2026-11-17T11:10:06Z, live venv):** `pytest tests/ -q` = `1047 passed, 1 skipped` (26.58s). All C1–C20 gates green with literal tokens: `session_gate.py` `21/21 checks passed`, `verify_campaign_evidence.py` `EVIDENCE VERIFIED`, `C20 ACCEPTANCE: PASS` (pooled `NO_GO`), `C19 ACCEPTANCE: PASS`, `C14 ACCEPTANCE: PASS`, `C13 ACCEPTANCE: PASS`, `C6 ACCEPTANCE: PASS`. **The C1–C20 research program is COMPLETE and certified `NO_GO`; nothing in C1–C20 remains to run. Do NOT relaunch C20, do not re-run pytest/gates for closure, do not commit unless asked.**
**BINDING NEXT FOCUS CAMPAIGN `C21` PREREGISTERED (gate RED until executed):** `research_state/c21_prereg_20261117T064408Z.{json,md}` (status `PRE_REGISTERED_BEFORE_COMPUTE`) + `scripts/verify_c21_focus_campaign.py` (fail-closed: currently `C21 ACCEPTANCE: FAIL` — 13 requirements missing / 0 of 12 artifacts, enforcing all four folds, 20,000 bootstrap/permutation draws, and 2,000 placebo runs per venue as verified 2026-11-17T11:10:06Z). **The next session's primary heavy task is to execute C21 end-to-end and turn `C21 ACCEPTANCE: FAIL` → `C21 ACCEPTANCE: PASS`.** No live `finish_c20`/`run_c20`/`run_c21`/campaign/supervisor processes; no stale `research_state/.c20/supervisor.lock`.
**Single durable handoff for the next agentic session — read this before doing anything else.**
**Phase O artifact timestamp (binding, `research_state/episode_edge_okx_full.json`):** `2026-11-13T23:38:47Z` · **Session done-gate:** `scripts/session_gate.py` = `21/21 checks passed` (re-verified 2026-11-17T11:10:06Z, green).

> **PROGRAM STATE: C1–C20 COMPLETE and certified `NO_GO` (closure re-verified 2026-11-17T11:10:06Z). C20 `ACCEPTANCE: PASS` (15/15 artifacts; pooled cross-venue `NO_GO`). There is NO live supervisor/campaign process now.**
>
> **BINDING DIRECTION (no explicit operator override):** **C21-T1** tests temporal/regime stability of the spec-literal edge on the already-verified real OKX + Binance UM archives (no new acquisition; acquisition stays CLOSED). It is a NEW hypothesis, not a same-data rerun of C20. Its gate is RED by design until the heavy compute is executed.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-17T11:11:24Z — C1–C20 CLOSED `NO_GO`; EXECUTE NEW C21)

**Repository:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication on real-market data). **Priority by repo scope:** C1–C20 are complete/certified `NO_GO`; the single binding next task is **C21-T1** (cross-venue temporal walk-forward & regime-stability of the spec-literal rule) — see `research_state/c21_prereg_20261117T064408Z.md` and `scripts/verify_c21_focus_campaign.py`.

**Environment ready NOW (bottleneck removed this session):** the durable `.venv` (repo root, Python 3.12.3, `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`) was bootstrapped this session via `scripts/bootstrap_env.sh`. Run gates with `PYTHONPATH=. .venv/bin/python ...`. If `.venv` is ever missing on a fresh runner, run `bash scripts/bootstrap_env.sh` FIRST (documented #1 avoidable time sink) — do not hand-roll a `/tmp` venv.

**Execute in order. No planning-only stops, no liveness narration as progress, no inference-only churn, no handoff-refresh-as-progress, no relaunching C20.**

**BOTTOM LINE UP FRONT (certified 2026-11-17T11:10:06Z):**
- `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` → `1047 passed, 1 skipped`.
- `scripts/session_gate.py` → `21/21 checks passed` (Phase O binding `2026-11-13T23:38:47Z`).
- `scripts/verify_campaign_evidence.py` → `EVIDENCE VERIFIED`.
- `scripts/verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS` (15/15 artifacts; pooled cross-venue `NO_GO`).
- `scripts/verify_c19_focus_campaign.py` → `C19 ACCEPTANCE: PASS`; `scripts/verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS`; `scripts/verify_c13_focus_campaign.py` → `C13 ACCEPTANCE: PASS`; `scripts/verify_next_focus_campaign.py` → `C6 ACCEPTANCE: PASS`.
- **C21 (next):** `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (13 requirements missing, 0/12 artifacts) **by design** — RED until the C21 battery is executed. Turning this green is the next session's heavy task.
- Final verdict (C1–C20): `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` token `NO_GO`, `research_program_complete: true`.

1. **Primary task (C21-T1):** execute the full C21 campaign end-to-end — preregistered folds {2023, 2024, 2025, 2026YTD} × {OKX, Binance UM}, per venue-fold episode-block bootstrap (20,000 draws), permutation p (20,000), portfolio placebo (2,000 subsets), census, BH-corrected stratum tests, pooled venue-blocked synthesis, per-venue + consolidated verdict, with a power curve. Produce every artifact in `c21_prereg_20261117T064408Z.json` → `required_artifacts`. Reuse C20 machinery (`scripts/run_c20_cross_venue_campaign.py`, `scripts/run_multiyear_robustness_battery.py`, `scripts/run_portfolio_placebo_*`) but do NOT edit C20 artifacts. `folds` must be `["2023","2024","2025","2026YTD"]` (or equivalent objects) in per-venue fold artifacts; episode-edge must record `episode_block_bootstrap.resamples >= 20000` and `temporal_edge_permutation.draws_evaluated >= 20000`; placebo must record `placebo.runs >= 2000`; pooled synthesis must record `pooled_venue_blocked_bootstrap.draws >= 20000`. Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py` must print `C21 ACCEPTANCE: PASS`.
2. **After C21 is green:** re-run `PYTHONPATH=. .venv/bin/python -m pytest tests/ -q` (must stay `1047 passed, 1 skipped`) and `scripts/session_gate.py` (must stay `21/21 checks passed`), then update this HANDOFF with new timestamped literals (keep all tokens below).
3. **If the C21 battery is already complete on disk** (future resume): just run `verify_c21_focus_campaign.py`; if green, do not recompute — refresh this HANDOFF and stop.
4. **If operator explicitly authorizes a NEW direction beyond C21:** this requires **new prereg + new data** (Hyperliquid moving-tail acquisition exhausted, earliest ~2026-04-21; no new-venue network). Preregister before compute (`research_state/c2x_prereg_*.{json,md}`, status `PRE_REGISTERED_BEFORE_COMPUTE`), acquire/specify new venue/window, and treat as a fresh binding campaign. **Do not invent a same-data C22+ rerun of C21.**
5. **Never:** relabel cross-venue as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21), synthetic gap-fill as verified, relax `SPEC_LITERAL_NEXT_OPEN`, fabricate `GO`/`STABLE_POSITIVE_SUBSET`, edit completed C1–C20 campaign artifacts to change results, or commit unless asked.

**Terminal state for C1–C20: closed `NO_GO`, certified green. C21 is the open binding work.**

---

## NEXT FOCUS — NO-AVOIDANCE BINDING (2026-11-17T11:10:06Z)

Future agents **cannot avoid heavy work**: the binding next campaign is **C21-T1**, whose gate `scripts/verify_c21_focus_campaign.py` is **RED until the full battery is executed**. Accepted progress is therefore **only**:
- **C21 executed end-to-end:** all `c21_*_20261117T064408Z` artifacts produced (per-venue fold campaign + episode edge + placebo + census, per-venue verdict, pooled stability synthesis, consolidated final), with `C21 ACCEPTANCE: PASS` (token `STABLE_POSITIVE_SUBSET`, `NO_GO`, or `UNDERPOWERED` with a power curve) and an honest pooled verdict.
- **Plus closure stays green:** `pytest tests/ -q` = `1047 passed, 1 skipped` and `session_gate.py` = `21/21 checks passed` with literal Phase O timestamp `2026-11-13T23:38:47Z`.
- **Plus** `verify_campaign_evidence.py` = `EVIDENCE VERIFIED`, `verify_c20_focus_campaign.py` = `C20 ACCEPTANCE: PASS`, `verify_c19_focus_campaign.py` = `C19 ACCEPTANCE: PASS`, `verify_c14_focus_campaign.py` = `C14 ACCEPTANCE: PASS`, `verify_c13_focus_campaign.py` = `C13 ACCEPTANCE: PASS`, `verify_next_focus_campaign.py` = `C6 ACCEPTANCE: PASS`, `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION`.

Not progress: reading, planning, rewriting this file, refreshing timestamps, "monitoring" an already-exited supervisor, relaunching C20, or inventing a same-data C22+ rerun. **Do NOT relaunch `scripts/finish_c20_detached_durable.sh`. Do NOT commit unless explicitly asked.**

## LIVE STATE VERIFIED (2026-11-17T11:10:06Z)

- **Host capacity:** `nproc=4`. No live `finish_c20`/`run_c20`/`run_c21`/campaign/supervisor processes (verified). No stale `research_state/.c20/supervisor.lock`.
- **Venv (this session):** `scripts/bootstrap_env.sh` completed → `.venv/bin/python` Python 3.12.3 with `pytest`/`numpy`/`pandas`/`requests`/`pyarrow`. Gate commands run green (see BOTTOM LINE UP FRONT).
- **C20:** PASS, terminal. `research_state/.c20/supervisor_status.json` = `state: PASS`, `artifacts: 15`, `updated_at_utc: 2026-11-17T05:39:45Z`.
- **C21 (open, binding):** prereg present `research_state/c21_prereg_20261117T064408Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`). Gate `scripts/verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (13 requirements missing; 0/12 output artifacts) — **expected RED until heavy compute is executed**. No canonical C21 runner/output exists. `research_state/timing_okx.json`, `timing_binance_um.json`, `timing_c21_census.json`, `zz_timing_c21_census.json` are prior **C20** timing probes — not C21 evidence; do not rename/copy into required C21 artifacts.
- **Artifacts:** 15/15 `research_state/*_20261116T063500Z.json` present. C20 closure artifacts tracked/clean; only this handoff update (and any local verifier changes) are uncommitted.
- **Consolidated final (C1–C20):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json` — token `NO_GO`, `research_program_complete: true` (pooled total PnL `-125,367.02`, bootstrap 95% CI `[-140,619.14, -110,114.9]`, `prob_pooled_total_gt_0=0.0`, go checks `6/14`, effective sample trades=249, episodes=67, distinct_crash_days=98).
- **Per-venue (both `NO_GO`):** OKX trades=113, total_pnl=-55,057.45 (coin -197,767.56, hedge +140,841.80, rebound_short -38,420.09), episodes=31, crash_days=45. Binance UM trades=136, total_pnl=-70,309.57 (coin -214,779.38, hedge +135,812.12, rebound_short -38,036.67), episodes=36, crash_days=53.
- **Certification (re-verified):** `pytest tests/ -q` → `1047 passed, 1 skipped`; `session_gate.py` → `21/21 checks passed`; `verify_campaign_evidence.py` → `EVIDENCE VERIFIED`; `verify_c20_focus_campaign.py` → `C20 ACCEPTANCE: PASS`; `verify_c19_focus_campaign.py` → `C19 ACCEPTANCE: PASS`; `verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS`; `verify_c13_focus_campaign.py` → `C13 ACCEPTANCE: PASS`; `verify_next_focus_campaign.py` → `C6 ACCEPTANCE: PASS`; `probe_hyperliquid_blocker.py` → `FULL_283D_BLOCKED_BY_API_RETENTION`; `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: FAIL` (expected).

## BOTTLENECKS REMOVED / UNBLOCKED (2026-11-17T11:10:06Z)

1. **"Do nothing" paralysis removed:** C1–C20 closed `NO_GO` but binding next campaign **C21-T1** is preregistered and its gate is RED until executed — heavy work is mandatory, not optional.
2. **Deps venv bottleneck REMOVED this session:** `.venv` was absent (documented #1 avoidable time sink) and is now bootstrapped at the repo root via `scripts/bootstrap_env.sh`; gates run green immediately. A fresh runner without `.venv` must run the bootstrap script first.
3. **No live/stale process blockers:** no `finish_c20`/`run_c20`/`run_c21` processes running; no stale supervisor lock; no duplicate/rival campaigns; no foreground campaign in this turn.
4. **Execution gap is the work:** `scripts/verify_c21_focus_campaign.py` fails with 13 missing requirements (0/12 artifacts). Bottleneck is unexecuted heavy compute, not environment contention.
5. **C20-permutation cap gotcha (MUST address before run):** `scripts/run_c20_cross_venue_campaign.py:75-76` sets `MAX_PERMUTATION_DRAWS = 300` and `MAX_PLACEBO_DRAWS = 500`, while C21 requires 20,000 permutations and 2,000 placebos per venue-fold. A canonical portfolio replay costs ~90s, so naive draws would take ~50h/venue. Build a fold-aware C21 runner that satisfies the full draw counts efficiently (e.g., memoized/vectorized permutation replay, reduced per-draw cost, or checkpoint+resume with `jobs=4`), verify its full-universe canonical replay matches C20, benchmark one fold, then run with checkpoint/resume. The strengthened C21 gate rejects reduced-draw or missing-fold artifacts.
6. **Acquisition bottleneck stays CLOSED, honestly:** Hyperliquid moving-tail acquisition exhausted (earliest ~2026-04-21; `FULL_283D_BLOCKED_BY_API_RETENTION`); new-venue network blocked. C21 must use already-verified OKX + Binance UM multi-year archives — no fabrication, no synthetic gap-fill, no cross-venue relabeling.

## C21 SPEC & DECISION RULES (prereg `c21_prereg_20261117T064408Z`, PRE_REGISTERED_BEFORE_COMPUTE) — OPEN

- **C21-T1 binding task:** quantify temporal/regime stability of the spec-literal crash-rebound edge on two independent real venues, with pre-specified BH multiplicity correction and an honest pooled verdict (`STABLE_POSITIVE_SUBSET` / `NO_GO` / `UNDERPOWERED`).
- **Config fixed (no switching):** `entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, rebound short 9%/48h, ETH hedge on, $5M volume gate, gross cap 120%, seed 20261121.
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
- **Do not relaunch `scripts/finish_c20_detached_durable.sh` — C20 is PASS.** No rival/duplicate campaign; no foreground campaign in an agent turn; no short `timeout`.
- **Do not invent a same-data C22+ rerun of C21.** New direction beyond C21 needs new prereg + new data + explicit operator authorization.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py` to change results.
- No silent change to canonical baseline. C1–C20 `NO_GO` stands.
- **Do not commit unless explicitly asked.**
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`
- C21 (open, binding): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/verify_c21_focus_campaign.py`, planned `research_state/c21_*_20261117T064408Z.json`, `research_state/c21_decision_verdict_CONSOLIDATED_20261117T064408Z.{json,md}`
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`, cap `MAX_PERMUTATION_DRAWS=300`/`MAX_PLACEBO_DRAWS=500`), `scripts/finish_c20_detached_durable.sh`, `scripts/verify_c20_focus_campaign.py`
- C19 ref: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.*`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.*`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.*`
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6)
- Env: `scripts/bootstrap_env.sh` (durable default `.venv`; run first on a fresh runner)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`