# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T11:25:09Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 is preregistered, partially computed, and **NOT complete**. The remaining work is heavy compute, not planning. This handoff supersedes all prior handoff text.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T11:25:09Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY`. **Inferred priority from repo name + state:** the crash-rebound strategy has been adjudicated under the spec-faithful entry rule and the native verdict is `NO_GO`; the one remaining decision-relevant question is whether that `NO_GO` replicates out-of-sample on the two independent real cross-venue archives. That is **C20**, and it is the only binding next focus campaign.

**Do this, in order. Do not stop at planning, narrative, or inference-only churn.**

**Verified this session (2026-11-16T11:25Z):** `session_gate.py` **21/21 checks passed**; `verify_campaign_evidence.py` **EVIDENCE VERIFIED**; `verify_c19_focus_campaign.py` **C19 ACCEPTANCE: PASS**; `verify_c20_focus_campaign.py` **FAIL (12 requirements missing)**. Phase O artifact `episode_edge_okx_full.json` `generated_at_utc=2026-11-13T23:38:47Z`. The blocker probe is `probe_hyperliquid_blocker.py` (status: blocked, 3849/6792 bars) and the binding evidence gate is `verify_campaign_evidence.py`.

1. **Read this file fully.** Do not re-open C1–C19, do not relabel cross-venue results as Hyperliquid-native evidence, do not relax the spec, and do not substitute narrative for artifacts.
2. **Ensure the environment.** C20 needs only `numpy/pandas/pyarrow/requests/pytest`; **`scipy` is NOT installed and NOT required** (the runner imports cleanly without it; the repo has no scipy dependency). Use:
   ```bash
   test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh /tmp/crs-venv
   ```
3. **Finish the C20 compute (long-running, resume-safe, no restrictive timeout):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python -u scripts/run_c20_cross_venue_campaign.py \
     --venues okx binance_um --jobs 4 --resume
   ```
   - A detached run was launched this session (see "Bottlenecks removed" below). **Check whether it is still alive first**; if not, rerun the exact command above. `--resume` caches every completed artifact, so a killed run loses only the single in-flight artifact.
   - **Never wrap this in a short `timeout`** (the prior session used `timeout 900`, which guaranteed failure). **Do not use `--jobs 1`** on this 4-vCPU box.
   - Expected runtime at `--jobs 4` (measured this session): `build_memo` ≈ 5 s, one memo portfolio replay ≈ 38 s. So ≈ 300 permutation draws ≈ 47 min/venue and ≈ 500 placebo draws ≈ 79 min/venue; **full both-venue run ≈ 4–5 h**. Run it detached and poll; do not block a single turn on it.
4. **Acceptance gate — must pass before claiming done:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   → required output `C20 ACCEPTANCE: PASS` (all 15 requirements). Current baseline: **FAIL, 12 requirements missing** (see state table).
5. **Hygiene gates (all must be green):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py            # 21/21 PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py # EVIDENCE VERIFIED
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q
   ```
6. **Update this HANDOFF.md** with a new timestamped **INITIAL TASK MESSAGE** that reflects the actual outcome: point to `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.{json,md}`, record the verdict (`GO` / `UNDERPOWERED` / `NO_GO` with the quantified power curve), list produced artifacts, and mark C20 complete **only if** `verify_c20_focus_campaign.py` prints PASS. If compute is blocked, remove the blocker (tune `--jobs`, keep `--resume`, run detached) — do not fake artifacts.

**C20 remains the heavy-work obligation until `verify_c20_focus_campaign.py` passes.**

---

## C20 CURRENT STATE (as of 2026-11-16T11:25:09Z)

Prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, config fixed (`entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120). **No config switching after results.**

| # | Artifact (stem `20261116T063500Z`) | Status |
|---|---|---|
| 1 | `c20_prereg` | PRESENT |
| 2 | `campaign_results_real_okx_multiyear_specliteral` (+`_metrics`) | PRESENT — 113 trades, −55,057.45 |
| 3 | `campaign_results_real_binance_um_multiyear_specliteral` (+`_metrics`) | PRESENT — 136 trades, −70,309.57 |
| 4 | `crash_event_census_real_okx_multiyear_specliteral` | PRESENT — 1182 events, 369 signal-pass, 113 matched |
| 5 | `crash_event_census_real_binance_um_multiyear_specliteral` | **MISSING** |
| 6 | `episode_edge_okx_multiyear_specliteral` | **MISSING** |
| 7 | `episode_edge_binance_um_multiyear_specliteral` | **MISSING** |
| 8 | `placebo_portfolio_okx_multiyear_specliteral` | **MISSING** |
| 9 | `placebo_portfolio_binance_um_multiyear_specliteral` | **MISSING** |
| 10 | `multiyear_robustness_battery_okx_specliteral` | **MISSING** |
| 11 | `multiyear_robustness_battery_binance_um_specliteral` | **MISSING** |
| 12 | `decision_verdict_cross_venue_okx_specliteral_c20` | **MISSING** |
| 13 | `decision_verdict_cross_venue_binance_um_specliteral_c20` | **MISSING** |
| 14 | `c20_pooled_cross_venue_synthesis` | **MISSING** |
| 15 | `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z` | **MISSING** |

Gate baseline: `verify_c20_focus_campaign.py` → **FAIL, 12 requirements missing** (`c20_artifacts_present`, `binance_um_census_computed`, both episode edges, both placebos, both batteries, both verdicts, pooled synthesis, consolidated final).

**C20 decision rules (from prereg):** GO only if pooled synthesis has episode-block bootstrap 95% CI excluding 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Otherwise verdict `UNDERPOWERED` or `NO_GO` with a quantified power curve. C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence. Note: both venue campaigns are already negative (OKX −55,057; Binance UM −70,310), so the likely token is `NO_GO`/`UNDERPOWERED`, but the next session must compute it, not assume it.

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-16T11:25Z)

1. **Doomed compute killed and relaunched correctly.** The prior session left `run_c20_cross_venue_campaign.py --venues okx --jobs 1` under `timeout 900`. Measured cost is ≈38 s per memo portfolio draw; 300 permutation + 500 placebo draws ≈ 12 h at one job, so a 900 s timeout could never finish and would be killed mid-artifact. Killed PID 20246/20248 and relaunched detached with **all 4 CPUs and no timeout**:
   - Background process id `bgp_1e419a5e1001rx9WiYJDyypzGf`, PID 21121, **persistent** (survives this session), log `/tmp/c20_run.log`.
   - Confirmed healthy: 4 worker processes at ~97% CPU.
   - If it is gone when you read this, rerun the command in step 3 above.
2. **Stale environment claim corrected.** The prior handoff said the venv contained `scipy`; it does not. Verified `scipy` is not used by the runner or the repo and is not required. Do not waste time installing it.
3. **Resume semantics documented.** The runner caches each completed artifact (campaign, census, episode, placebo, battery, verdict, pooled, consolidated). A killed run loses only the in-flight artifact; always rerun with `--resume`.
4. **Acceptance gate is fail-closed and already in place:** `scripts/verify_c20_focus_campaign.py` (15 checks). A bare "OKX done" or "prereg only" is not an accepted terminal state; both venues end-to-end are required.

---

## C1–C19 CLOSED STATE (historical context, do not relitigate)

**Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`. No validated edge claimed.

- **C19-T1 Adjudication: COMPLETE.** `SPEC_LITERAL_NEXT_OPEN` wins (spec text: RSI(21)<20 crash close → buy at next hourly open; no same-bar `confirm_rebound()` gate). Artifact: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`.
- **C19-T2 Native battery re-run: COMPLETE.** C18 spec-literal on Ironflow wide archive = 22 trades, −47,933.58, win rate 31.8%, max DD −52,160. NO_GO under adjudicated reading.
- **C19-T3 Dependence-aware inference + power curve: COMPLETE.** 0/7 GO criteria met; max achievable 4 episodes < 5 required.
- **C19-T4 Native verdict: COMPLETE.** `decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}` — token `NO_GO`, `is_hyperliquid_evidence=true`, `cross_venue=false`.
- **C19-T5 Consolidated final: COMPLETE.** `decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`.
- **Acquisition: CLOSED / exhausted.** Live Hyperliquid `candleSnapshot` moving tail (`full_window_served=false`, earliest ~`2026-04-21`; probe `hyperliquid_retention_probe_next_20261116T054408Z.json`: 3849/6792 bars, 2943 missing). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14. Cross-venue OKX/Binance are **not** admissible as native evidence.
- **Native evidence: underpowered / fragile.** C14 = 7 trades, 3 episodes, bootstrap CI spans 0; max achievable 4 episodes < 5 GO floor.
- **Cross-venue context (complete, not native):** C6 OKX + Binance UM multi-year pooled 38 venue-episodes underpowered (CI spans 0). Context only, `is_hyperliquid_venue_data=false`.

---

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native evidence (`is_hyperliquid_venue_data=false` for all C20 artifacts).
- No synthetic gap-fill presented as verified.
- No spec relaxation to manufacture a GO; `SPEC_LITERAL_NEXT_OPEN` is the fixed C20 reading.
- No inference-only churn on exhausted C14 native data; C19 adjudicated and closed.
- No silent change to the canonical baseline; any code change is opt-in, documented, justified.
- C1–C19 `NO_GO` stands unless C20 produces a new consolidated final superseding it.
- Do not commit unless explicitly asked; the durable handoff is this file.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C20 prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}`
- C20 runner: `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`)
- C20 gate: `scripts/verify_c20_focus_campaign.py` (15 requirements, fail-closed)
- C19 artifacts (reference only): `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- Env bootstrap: `scripts/bootstrap_env.sh` (venv at `/tmp/crs-venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

(End of file)