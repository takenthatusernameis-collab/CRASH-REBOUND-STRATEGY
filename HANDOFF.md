# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T10:11:42Z  ·  **Last session verified (UTC):** 2026-11-16T11:09:00Z  ·  **Phase O artifact (OKX full, gate ref):** `episode_edge_okx_full.json` `generated_at_utc=2026-11-13T23:38:47Z`
**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> Re-confirmed 2026-11-16T11:09Z: acquisition CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`, probe `research_state/hyperliquid_retention_probe_next_20261116T054408Z.json`: 3849 bars, earliest 2026-04-21, 2943 early bars missing; no new native archive beyond `hyperliquid_ironflow_wide_20261115T214900Z`). C19 adjudication `SPEC_LITERAL_NEXT_OPEN` final; C18 native spec-literal = 22 trades / −47,933.58 / NO_GO; consolidated C1–C19 final `NO_GO`. Gates: `session_gate.py` **21/21 PASS**, `verify_campaign_evidence.py` **EVIDENCE VERIFIED**, `verify_c19_focus_campaign.py` **C19 ACCEPTANCE: PASS**. **Active blocker (must be removed by compute): `verify_c20_focus_campaign.py` FAIL (13/15 missing).** C20 prereg exists but C20 is NOT computed.
>
> **ENV BOTTLENECK REMOVED (2026-11-16T11:09Z):** Python deps were missing system-wide (`numpy/pandas/scipy/pyarrow/requests/pytest`). A ready venv now exists at `/tmp/crs-venv` with `requirements-test.txt` installed (`numpy 2.4.4`, `pandas 3.0.2`, `scipy 1.17.1`, `pyarrow 23.0.1`, `requests 2.33.1`, `pytest 9.0.3`). **Use `/tmp/crs-venv/bin/python` (or activate it) for all C20 compute, gates, and tests in this environment.** If venv is absent in a future environment, run `bash scripts/bootstrap_env.sh /tmp/crs-venv` before anything else.
>
> **C1–C19 verdict is final and must not be relitigated.**

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T11:09:00Z — EXECUTE C20 FOCUS CAMPAIGN, MANDATORY HEAVY WORK)

**Program state: C1–C19 CLOSED (`NO_GO`, final). C20 is the ONLY binding next focus campaign and is NOT DONE.** Preregistered 2026-11-16T06:35Z (`PRE_REGISTERED_BEFORE_COMPUTE`, `entry_spec_literal_next_open=true`, seed 20261120, fixed config, no switching). Acquisition remains CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`); C20 runs on already-verified OKX + Binance UM multi-year archives only (`is_hyperliquid_venue_data=false`, never Hyperliquid performance evidence). **Planning-only, narrative-only, or inference-only churn is not progress. Significant compute is required now.**

**Verified this session (2026-11-16T11:09Z):** `session_gate.py` 21/21 PASS, `verify_campaign_evidence.py` PASS, `verify_c19_focus_campaign.py` PASS. `verify_c20_focus_campaign.py` **FAIL (13/15 missing)**. Venv ready: `/tmp/crs-venv` (deps installed). OKX campaign+census present; Binance UM + all inference/verdict artifacts missing.

**Execute immediately, in order (do not stop at planning):**
1. Re-read `HANDOFF.md`. Do **not** re-open C1–C19 acquisition, relabel cross-venue as Hyperliquid-native, relax the spec, or churn on exhausted C14 native data.
2. Ensure env: `test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh /tmp/crs-venv`
3. **Run C20 end-to-end (heavy, resume-safe):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_c20_cross_venue_campaign.py --venues okx binance_um --jobs 4 --resume
   ```
   (OKX campaign+census already exist; Binance UM compute + all per-venue inference/placebo/battery/verdicts + pooled synthesis + consolidated final must be produced. Expect long runtime — this is the intended work.)
4. **Acceptance gate (must pass before claiming done):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   → `C20 ACCEPTANCE: PASS` (all 15 requirements).
5. Hygiene (all green): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`, `... scripts/verify_campaign_evidence.py`, `... scripts/verify_c19_focus_campaign.py`. Run `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q` and record result.
6. Update `HANDOFF.md` with a new timestamped **INITIAL TASK MESSAGE** reflecting actual outcome: point to `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.{json,md}`, record verdict (`GO` / `UNDERPOWERED` / `NO_GO` with quantified power curve), list produced artifacts, and mark C20 complete with evidence **only if** acceptance passes. If compute is blocked by runtime/resources, remove that blocker (tune `--jobs`, let it run to completion, keep `--resume`) — do not substitute narrative for artifacts.

**C20 is the ongoing heavy-work obligation until `verify_c20_focus_campaign.py` passes.**

**Bounded acquisition precondition — remains CLOSED (executed 2026-11-16T05:46Z):** `hyperliquid_retention_probe_next_20261116T054408Z.json` → `FULL_283D_BLOCKED_BY_API_RETENTION` (3849/6792 bars, earliest `2026-04-21`, 2943 missing). No new native archive. C20 uses OKX + Binance UM only (`is_hyperliquid_venue_data=false`).

---

## C1–C19 CLOSED STATE (historical context, do not relitigate)

**Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`, supersedes `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`. No validated edge claimed.

**Completed C19 work (do not relitigate):**
- **C19-T1 Adjudication: COMPLETE.** `SPEC_LITERAL_NEXT_OPEN` wins (spec text: RSI(21)<20 crash close → buy at next hourly open; no same-bar `confirm_rebound()` gate). Artifact: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`.
- **C19-T2 Native battery re-run: COMPLETE.** C18 spec-literal on Ironflow wide archive = 22 trades, −47,933.58, win rate 31.8%, max DD −52,160. NO_GO under adjudicated reading.
- **C19-T3 Dependence-aware inference + power curve: COMPLETE.** 0/7 GO criteria met; max achievable 4 episodes < 5 required.
- **C19-T4 Native verdict: COMPLETE.** `decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}` — token `NO_GO`, `is_hyperliquid_evidence=true`, `cross_venue=false`.
- **C19-T5 Consolidated final: COMPLETE.** `decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`.

**Current state (prioritized, FINAL, CLOSED 2026-11-16T05:46Z):**
1. Acquisition: CLOSED / exhausted. Live Hyperliquid `candleSnapshot` moving tail (`full_window_served=false`, earliest ~`2026-04-21`). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14. Cross-venue OKX/Binance are **not** admissible as native evidence.
2. Native evidence: underpowered / fragile. C14 = 7 trades, 3 episodes, bootstrap CI spans 0; max achievable 4 episodes < 5 GO floor.
3. C19 fork: `SPEC_LITERAL_NEXT_OPEN` wins; C18 spec-literal NO_GO decisively negative; C14 canonical same-bar demoted to non-spec sensitivity (+8,914.33 / 7 trades).
4. Cross-venue context (complete, not native): C6 OKX + Binance UM multi-year pooled 38 venue-episodes underpowered (CI spans 0). Context only, `is_hyperliquid_venue_data=false`.
5. Consolidated final: `NO_GO` for C1–C19.

---

## C20 FOCUS CAMPAIGN — MISSING ARTIFACTS (heavy work, must not be avoided)

Prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, config fixed (`entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120). **No config switching after results.**

Already present (do not regenerate unless resuming):
- `campaign_results_real_okx_multiyear_specliteral_20261116T063500Z.json` (+ `_metrics.json`)
- `crash_event_census_real_okx_multiyear_specliteral_20261116T063500Z.json`

**Missing — the next session must produce all of these:**
| # | Artifact (stem `20261116T063500Z`) | Status |
|---|---|---|
| 1 | `campaign_results_real_binance_um_multiyear_specliteral` | MISSING |
| 2 | `crash_event_census_real_binance_um_multiyear_specliteral` | MISSING |
| 3 | `episode_edge_okx_multiyear_specliteral` | MISSING |
| 4 | `episode_edge_binance_um_multiyear_specliteral` | MISSING |
| 5 | `placebo_portfolio_okx_multiyear_specliteral` | MISSING |
| 6 | `placebo_portfolio_binance_um_multiyear_specliteral` | MISSING |
| 7 | `multiyear_robustness_battery_okx_specliteral` | MISSING |
| 8 | `multiyear_robustness_battery_binance_um_specliteral` | MISSING |
| 9 | `decision_verdict_cross_venue_okx_specliteral_c20` | MISSING |
| 10 | `decision_verdict_cross_venue_binance_um_specliteral_c20` | MISSING |
| 11 | `c20_pooled_cross_venue_synthesis` | MISSING |
| 12 | `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z` | MISSING |

**C20 acceptance gate:** `scripts/verify_c20_focus_campaign.py` — fail-closed, all 15 requirements must pass (prereg + both venue campaigns + both censuses + both episode edges + both placebos + both batteries + both verdicts + pooled synthesis + consolidated final + handoff reference).

**C20 decision rules (from prereg):** GO only if pooled synthesis has episode-block bootstrap 95% CI excluding 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Otherwise verdict `UNDERPOWERED` or `NO_GO` with a quantified power curve. C20 is cross-venue (`is_hyperliquid_venue_data=false`) — never Hyperliquid performance evidence.

---

## Bottleneck removal (what this session set up)

- **C20 was preregistered but never computed — the single biggest bottleneck.** `scripts/run_c20_cross_venue_campaign.py` orchestrates the full 8-step pipeline per venue (campaign, census, episode dependence audit, conditional permutation, placebo, robustness battery, per-venue verdict, pooled synthesis + consolidated final) with `--resume` for crash recovery. OKX half is already on disk; Binance UM is the missing half.
- **Missing acceptance gate created:** `scripts/verify_c20_focus_campaign.py` (fail-closed, 15 checks) so future agents cannot mark C20 done without the full artifact set.
- **HANDOFF.md now points at C20** (`verify_c20_focus_campaign.py` referenced, C20-T1 initial task message). No acceptance gate blocks the next session.

## Guardrails (never violate)

- No cross-venue relabeling as Hyperliquid-native evidence (`is_hyperliquid_venue_data=false` for all C20 artifacts).
- No synthetic gap-fill presented as verified.
- No spec relaxation to manufacture a GO; `SPEC_LITERAL_NEXT_OPEN` is the fixed C20 reading (default `entry_spec_literal_next_open=false` in canonical baseline — opt-in only).
- No inference-only churn on exhausted C14 native data; C19 adjudicated and closed.
- No silent change to the canonical baseline; any code change is opt-in, documented, justified.
- C1–C19 `NO_GO` verdict stands unless C20 produces a new consolidated final superseding it.

## Key files

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C20 prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}`
- C20 runner: `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`)
- C20 gate: `scripts/verify_c20_focus_campaign.py` (15 requirements, fail-closed)
- C19 artifacts (reference only): `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

## Session-end requirement — C20 IN PROGRESS (2026-11-16T11:20Z, compute launched)

C1–C19 is closed (`NO_GO`). **C20 end-to-end execution has been started but is NOT complete.** The next session's only legitimate initial task remains: reach **`C20 ACCEPTANCE: PASS`** for `scripts/verify_c20_focus_campaign.py` and then update this handoff with the C20 consolidated final verdict/evidence.

**State as of 2026-11-16T11:20Z:**
- Gates: `session_gate.py` 21/21 PASS, `verify_campaign_evidence.py` PASS, `verify_c19_focus_campaign.py` PASS. `verify_c20_focus_campaign.py` **FAIL (13/15 missing)**.
- Present C20 artifacts: `campaign_results_real_okx_multiyear_specliteral_20261116T063500Z.json` (+metrics), `crash_event_census_real_okx_multiyear_specliteral_20261116T063500Z.json`. Missing: Binance UM campaign+census and all inference/placebo/battery/verdicts + pooled synthesis + consolidated final (per top-of-file list).
- Env bottleneck removed: venv `/tmp/crs-venv` ready with deps (`numpy/pandas/scipy/pyarrow/requests/pytest`). Use `/tmp/crs-venv/bin/python` for compute/gates/tests; bootstrap via `bash scripts/bootstrap_env.sh /tmp/crs-venv` if missing.
- **Heavy compute launched this session (background, may still be running):**
  - OKX: `PYTHONPATH=. /tmp/crs-venv/bin/python -u scripts/run_c20_cross_venue_campaign.py --venues okx --jobs 1 --resume` (under `timeout 900`; observed active/high CPU ~11:18Z)
  - Binance UM: `PYTHONPATH=. /tmp/crs-venv/bin/python -u scripts/run_c20_cross_venue_campaign.py --venues binance_um --jobs 1 --resume` (under `timeout 180`; observed active/high CPU ~11:18Z)
  - Log: `/tmp/c20_run.log` (cached-step resumes only so far). If processes timed out/stopped, **restart immediately** with `--resume` (remove restrictive `timeout` or raise it substantially); do not recompute from scratch unnecessarily.

**Mandatory next actions:**
1. Check for running C20 processes / produced artifacts in `research_state/*specliteral*20261116T063500Z*` and rerun `scripts/verify_c20_focus_campaign.py`.
2. If not passing, run to completion (long-running): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_c20_cross_venue_campaign.py --venues okx binance_um --jobs 4 --resume` until all C20 artifacts exist. Tune `--jobs` to available CPU/RAM; keep `--resume`.
3. Achieve `C20 ACCEPTANCE: PASS`, rerun all gates, run `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q`, then update `HANDOFF.md` with new timestamped initial task message pointing to `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.{json,md}` and the honest verdict/power curve. Do **not** re-open C1–C19, relabel cross-venue as Hyperliquid-native, or substitute narrative for artifacts.

Verification commands (use venv python):
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **21/21 checks passed** (last verified)
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **EVIDENCE VERIFIED**
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py` → **C19 ACCEPTANCE: PASS**
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py` → **C20 ACCEPTANCE: PASS** (required)
- `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q` → record actual result

Final program verdict C1–C19: **`NO_GO`**. C20 verdict pending — compute must be completed.

(End of file)
