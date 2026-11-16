# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T11:37:30Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE BINDING NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C20 is preregistered and its heavy compute is **already running detached** (`scripts/finish_c20_detached.sh`, SID `22315`). It is **NOT complete** (4/15 artifacts). Your job is to drive it to `C20 ACCEPTANCE: PASS`, not to re-plan it. This handoff supersedes all prior handoff text.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T11:37:30Z — FINISH C20, MANDATORY HEAVY WORK)

**Repository:** `CRASH-REBOUND-STRATEGY`.
**Inferred priority from the repo name + state:** this repo exists to decide whether the crash-rebound strategy is a real edge. C1–C19 adjudicated the entry rule (`SPEC_LITERAL_NEXT_OPEN`: RSI(21)<20 crash close → buy at next hourly open, no same-bar confirmation gate) and returned `NO_GO` on Hyperliquid-native data. The single remaining decision-relevant question is whether that `NO_GO` replicates out-of-sample on the two independent real cross-venue archives (OKX + Binance UM). That is **C20**, and it is the only binding next focus campaign. Everything else is closed or inadmissible.

**Do this, in order. Do not stop at planning, narrative, or inference-only churn.**

1. **Read this file fully.** Do not re-open C1–C19, do not relabel cross-venue results as Hyperliquid-native evidence, do not relax the spec, and do not substitute narrative for artifacts.
2. **Check the detached C20 worker first — do not start a second one.**
   ```bash
   ps -eo pid,sid,etime,pcpu,cmd | grep -E "finish_c20|run_c20" | grep -v grep
   tail -n 30 /tmp/c20_supervisor.log
   cat /tmp/c20_supervisor_status.json 2>/dev/null
   ```
   - If `finish_c20_detached.sh` **is** alive: **do nothing to it.** It re-launches the campaign with `--resume` after every failure and stops only on PASS. Poll it; do not race it with a manual run (a manual run duplicates 4 CPU-heavy workers and can corrupt an in-flight artifact).
   - If it is **gone without PASS**, relaunch exactly this (detached, no timeout):
     ```bash
     setsid nohup bash scripts/finish_c20_detached.sh >/dev/null 2>&1 < /dev/null &
     ```
3. **Acceptance gate — the only accepted terminal state:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c20_focus_campaign.py
   ```
   → required output `C20 ACCEPTANCE: PASS` (all 15 requirements). Baseline now: **FAIL, 12 requirements missing** (see state table). A bare "OKX done", "prereg only", or "narrative complete" is **not** an accepted terminal state.
4. **While it runs, do useful non-racing work only:** read `research_state/c20_prereg_20261116T063500Z.md` so you can state the GO/UNDERPOWERED/NO_GO decision rule from memory, and pre-check that the evidence gates are green (step 5). Do **not** launch another compute campaign, do not re-fetch archives, do not re-run C1–C19, and do not edit `scripts/run_c20_cross_venue_campaign.py`.
5. **Hygiene gates (all must be green before you claim done):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py             # 21/21 PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py  # EVIDENCE VERIFIED
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c19_focus_campaign.py # C19 ACCEPTANCE: PASS
   PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest tests/ -q                 # 1047 passed, 1 skipped
   ```
6. **When (and only when) the gate prints PASS, update this HANDOFF.md** with a new timestamped **INITIAL TASK MESSAGE** that records: the verdict token from `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, the per-venue and pooled numbers (trades, total PnL, spot/hedge/rebound legs, bootstrap CI, permutation p, placebo p), the full artifact list, and the explicit statement that C20 is closed. If the supervisor stalls or exhausts attempts, record the actual blocker and the exact log path — do not fake artifacts and do not downgrade the gate.

**C20 remains the heavy-work obligation until `verify_c20_focus_campaign.py` prints PASS.**

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-16T11:37Z)

1. **The 4–5 h compute was session-bound and therefore doomed.** The prior run (PID 21177) was a child of a dead agent session's shell and had been launched under `timeout 900` in an earlier session. No agent session can stay alive for a ~4–5 h run (this harness idles out in 15 min), so the run could never reach PASS on its own. **Fix:** killed the session-bound run (only the in-flight OKX episode artifact was lost; `--resume` kept the 4 completed artifacts) and replaced it with `scripts/finish_c20_detached.sh`, a detached, lock-guarded, auto-resume supervisor:
   - Running now as **PID 22315, SID 22315, PPID 1** (fully detached, survives this session and this harness), 4 workers at ~95% CPU.
   - It reruns `run_c20_cross_venue_campaign.py --venues okx binance_um --jobs 4 --resume` then `verify_c20_focus_campaign.py`, up to 40 attempts, and exits 0 only on PASS.
   - Stall protection: two consecutive attempts with no new artifact → stops and writes `STALLED` instead of spinning.
   - Logs: `/tmp/c20_supervisor.log`; machine-readable state: `/tmp/c20_supervisor_status.json`; single-instance lock: `/tmp/c20_supervisor.lock` (`flock`).
   - **If the container restarts**, `/tmp` state is lost but the durable artifacts in `research_state/` are not; just relaunch with the command in step 2.
2. **Doomed invocation pattern documented so it is not repeated:** never use a short `timeout`, never `--jobs 1` on this 4-vCPU box, and never launch the campaign in the foreground of an agent turn. Use the supervisor.
3. **Stale environment claim corrected:** the venv has **no `scipy`** and does not need it (nothing in the repo imports it). Do not install it. Bootstrap only if `/tmp/crs-venv/bin/python` is missing: `bash scripts/bootstrap_env.sh /tmp/crs-venv`.
4. **Acceptance is fail-closed and already enforced** by `scripts/verify_c20_focus_campaign.py` (15 checks). The supervisor cannot declare success; only the gate can.

---

## C20 CURRENT STATE (as of 2026-11-16T11:37:30Z)

Prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, config fixed (`entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120). **No config switching after results.**

| # | Artifact (stem `20261116T063500Z`) | Status |
|---|---|---|
| 1 | `c20_prereg` | PRESENT |
| 2 | `campaign_results_real_okx_multiyear_specliteral` (+`_metrics`) | PRESENT — 113 trades, −55,057.45 |
| 3 | `campaign_results_real_binance_um_multiyear_specliteral` (+`_metrics`) | PRESENT — 136 trades, −70,309.57 |
| 4 | `crash_event_census_real_okx_multiyear_specliteral` | PRESENT — 1182 events, 369 signal-pass, 113 matched |
| 5 | `crash_event_census_real_binance_um_multiyear_specliteral` | PENDING (supervisor) |
| 6 | `episode_edge_okx_multiyear_specliteral` | PENDING (in flight now: 300 permutation draws) |
| 7 | `episode_edge_binance_um_multiyear_specliteral` | PENDING |
| 8 | `placebo_portfolio_okx_multiyear_specliteral` | PENDING (500 placebo draws) |
| 9 | `placebo_portfolio_binance_um_multiyear_specliteral` | PENDING |
| 10 | `multiyear_robustness_battery_okx_specliteral` | PENDING |
| 11 | `multiyear_robustness_battery_binance_um_specliteral` | PENDING |
| 12 | `decision_verdict_cross_venue_okx_specliteral_c20` | PENDING |
| 13 | `decision_verdict_cross_venue_binance_um_specliteral_c20` | PENDING |
| 14 | `c20_pooled_cross_venue_synthesis` | PENDING |
| 15 | `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z` | PENDING |

**Verified this session (2026-11-16T11:37Z):** `session_gate.py` **21/21 checks passed**; `verify_campaign_evidence.py` **EVIDENCE VERIFIED**; `verify_c19_focus_campaign.py` **C19 ACCEPTANCE: PASS**; `verify_c20_focus_campaign.py` **FAIL (12 requirements missing)**; `pytest tests/ -q` **1047 passed, 1 skipped** (416 s). Phase O artifact `episode_edge_okx_full.json` `generated_at_utc=2026-11-13T23:38:47Z`. The native acquisition blocker probe is `probe_hyperliquid_blocker.py` (status: blocked, 3849/6792 bars); the binding evidence gate is `verify_campaign_evidence.py`. Artifacts present: 4/15. Gate baseline failure list: `c20_artifacts_present`, `binance_um_census_computed`, both episode edges, both placebos, both batteries, both verdicts, `c20_pooled_synthesis_computed`, `c20_consolidated_final_computed`.

**Measured cost / ETA (from this repo, `--jobs 4`):** one memo portfolio draw ≈ 38 s. Per venue: 300 permutation + 500 placebo draws ≈ 47 min + 79 min. Both venues end-to-end ≈ **4–5 h**, so expect PASS around **2026-11-16T16:00Z** if nothing is killed. Do not block a single turn on it; poll the supervisor log.

**C20 decision rules (from prereg):** GO only if the pooled synthesis has an episode-block bootstrap 95% CI excluding 0 with a positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Otherwise the token is `UNDERPOWERED` or `NO_GO` with a quantified power curve. C20 is cross-venue (`is_hyperliquid_venue_data=false`) — **never** Hyperliquid performance evidence. Note: both venue campaigns are already negative (OKX −55,057; Binance UM −70,310), so the likely token is `NO_GO`/`UNDERPOWERED`, but the next session must compute it, not assume it.

---

## C1–C19 CLOSED STATE (historical context, do not relitigate)

**Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`. No validated edge claimed.

- **C19-T1 Adjudication: COMPLETE.** `SPEC_LITERAL_NEXT_OPEN` wins (spec text: RSI(21)<20 crash close → buy at next hourly open; no same-bar `confirm_rebound()` gate). Artifact: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`.
- **C19-T2 Native battery re-run: COMPLETE.** C18 spec-literal on Ironflow wide archive = 22 trades, −47,933.58, win rate 31.8%, max DD −52,160. NO_GO under the adjudicated reading.
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
- No second concurrent campaign run while the supervisor holds `/tmp/c20_supervisor.lock`; no foreground campaign in an agent turn; no short `timeout`.
- No silent change to the canonical baseline or to `scripts/run_c20_cross_venue_campaign.py`; any code change is opt-in, documented, justified.
- C1–C19 `NO_GO` stands unless C20 produces a new consolidated final superseding it.
- Do not commit unless explicitly asked; the durable handoff is this file.

## KEY FILES

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C20 prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}`
- C20 runner: `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`)
- C20 detached finisher: `scripts/finish_c20_detached.sh` (log `/tmp/c20_supervisor.log`, state `/tmp/c20_supervisor_status.json`, lock `/tmp/c20_supervisor.lock`)
- C20 gate: `scripts/verify_c20_focus_campaign.py` (15 requirements, fail-closed)
- C19 artifacts (reference only): `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- Env bootstrap: `scripts/bootstrap_env.sh` (venv at `/tmp/crs-venv`)
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

(End of file)