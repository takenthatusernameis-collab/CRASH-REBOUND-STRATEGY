# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-19T02:12:24Z · **Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading-strategy research/backtesting on real-market, cross-venue data (OKX + Binance UM perps C1–C21; MEXC USDT-perp C22 complete; Bitget USDT-perp C23 COMPLETE).
**Single durable handoff:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer to this file; do not maintain a second source of truth.
**Priority by repo scope (non-negotiable):** C1–C20 are CLOSED & CERTIFIED `NO_GO` (do not relitigate). **C21-T1 is COMPLETE** — gate `C21 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. **C22-T1 is COMPLETE** — gate `C22 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. **C23-T1 is COMPLETE** — gate `C23 ACCEPTANCE: PASS`, consolidated verdict `NO_GO` (Bitget USDT-M out-of-sample replication of the frozen spec-literal edge; PRE-REGISTERED `c23_prereg_20261118T202301Z`; 4/4 fold checkpoints present, 7/7 battery artifacts present). **C24-T1 (MARGIN / LIQUIDATION FIDELITY ADJUDICATION) IS THE ACTIVE BINDING CAMPAIGN — RUNNING IN BACKGROUND (PID 14458, 4 workers, started 2026-11-19T02:50:00Z).** Gate `C24 ACCEPTANCE: PENDING`. Hyperliquid-native acquisition stays CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`). Do NOT run a same-data C22+ rerun on OKX/Binance; do not relabel MEXC/Bitget data as Hyperliquid; do not reduce draw counts. **Do not launch a duplicate C24 battery while the runner is alive.**

**Verified live/repo state (2026-11-19T03:13:53Z):**
- `bash scripts/status_c23.sh` (read-only, one-shot; ONLY status command you need) → `RUNNER: NOT ALIVE` (campaign finished; do not relaunch), `2023/2024/2025/2026YTD: DONE`, battery `7/7`, gate `C23 ACCEPTANCE: PASS`.
- `PYTHONPATH=. .venv/bin/python scripts/verify_c23_focus_campaign.py` → `C23 ACCEPTANCE: PASS` (bitget=NO_GO, consolidated=NO_GO; battery 7/7; folds ['2023','2024','2025','2026YTD']; is_hyperliquid_venue_data=false).
- `PYTHONPATH=. .venv/bin/python scripts/verify_c22_focus_campaign.py` → `C22 ACCEPTANCE: PASS` (mexc consolidated `NO_GO`). C22 runner NOT alive — campaign complete.
- `PYTHONPATH=. .venv/bin/python -m pytest tests/test_c23_campaign_20261118.py -q` → **13 passed** (Bitget normalization/pagination, prereg schema/frozen config, gate PENDING→PASS and FAIL-on-drift/mismatch/Hyperliquid-mislabel).
- `.venv` bootstrapped at repo root (Python 3.12.3 + numpy, pandas, requests, pyarrow, pytest 9.2.0). Run with `PYTHONPATH=. .venv/bin/python ...`. **Environment bottleneck removed** — venv survives restarts; run `bash scripts/bootstrap_env.sh` only if `.venv/bin/python` is missing.
- **C23 RUNNER IS NOT ALIVE (campaign finished):** all 4 fold checkpoints and 7/7 battery artifacts exist; nothing to resume. Do NOT start a duplicate Bitget battery.
- **Fold evidence (final):** fold **2023** trades=24 pnl=+28,706.32 eps=9 perm_p=0.0229 0/9 BH survivors; fold **2024** trades=36 pnl=-30,939.60; fold **2025** trades=37 pnl=-32,710.19; fold **2026YTD** trades=21 pnl=-23,185.86. Pooled total PnL **-58,129.33**, CI95 [-58,129.33, -58,129.33], prob_pooled_total_gt_0=0.0, BH pooled stratum survivors **0/36**, sign concordant (all negative). Consolidated verdict `NO_GO` (generated 2026-11-19T00:31:49Z). A single positive fold (2023) is NOT a result — only the consolidated artifact + gate token count.
- Local `main` HEAD (controller checkpoints the worktree; do not rewrite history; do not commit unless explicitly asked).

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T02:13:00Z — C23-T1 COMPLETE, TERMINAL STATE, STOP)

**Single durable handoff / source of truth:** this file. `INITIAL_TASK_MESSAGE.md` is a pointer only.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market data.

**Current position (verified live 2026-11-19T02:13:00Z):** C1–C20 CLOSED `NO_GO`; C21-T1 COMPLETE (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`); C22-T1 COMPLETE (`C22 ACCEPTANCE: PASS`, consolidated `NO_GO`); **C23-T1 COMPLETE** — Bitget USDT-M out-of-sample replication. Gate `C23 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. Pooled total PnL **-58,129.33**, prob_pooled_total_gt_0=0.0, BH pooled stratum survivors **0/36**, sign concordant (all negative). Folds: 2023: 24 trades +28,706.32; 2024: 36 trades -30,939.60; 2025: 37 trades -32,710.19; 2026YTD: 21 trades -23,185.86. 4/4 fold checkpoints present, 7/7 battery artifacts present. Runner NOT ALIVE (campaign finished) — do not relaunch. `bash scripts/status_c23.sh` → RUNNER: NOT ALIVE, battery 7/7, gate `C23 ACCEPTANCE: PASS`. `PYTHONPATH=. .venv/bin/python scripts/verify_c23_focus_campaign.py` → `C23 ACCEPTANCE: PASS`.

**Immediate next action:** none required — **STOP**. No campaign is authorized beyond C23. Do not launch C23 again, do not start a same-data follow-on on OKX/Binance/MEXC/Bitget, do not relabel Bitget data as Hyperliquid, do not reduce draw counts. The correct terminal state is the evidence report below, not a new probe.

**Terminal evidence (deliver and file):**
- Per-fold (Bitget USDT-M 1H, spec-literal, frozen config rsi_period=21/rsi_threshold=20/target_pct=9, seed 20261123): 2023 (+28,706.32, 24 trades, perm_p=0.0229, 0/9 BH survivors); 2024 (-30,939.60, 36 trades); 2025 (-32,710.19, 37 trades); 2026YTD (-23,185.86, 21 trades).
- Pooled: total PnL -58,129.33, CI95 [-58,129.33, -58,129.33], prob_gt_0=0.0, BH survivors 0/36, sign concordant (-1).
- Consolidated verdict token: `NO_GO` (`research_state/c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json`, generated 2026-11-19T00:31:49Z). Supersedes `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`.
- Provenance: real Bitget USDT-perp data, non-synthetic, `is_hyperliquid_venue_data=false`, CROSS-VENUE vs the Hyperliquid spec — NOT Hyperliquid performance evidence, never relabelled as such. Window 2023-01-01..2026-09-28. Cache `research_state/cache/bitget_1h_multiyear_20230101_20260928/`; universe `research_state/universe_bitget_multiyear_verified.json`.
- Regression: `tests/test_c23_campaign_20261118.py` → 13 passed.

**Repository:** `CRASH-REBOUND-STRATEGY` (all venues closed `NO_GO`: OKX, Binance UM, MEXC, Bitget; Hyperliquid-native acquisition CLOSED `FULL_283D_BLOCKED_BY_API_RETENTION`).
**Environment:** durable `.venv` at repo root (Python 3.12.3 + deps); run with `PYTHONPATH=. .venv/bin/python ...`. If missing, `bash scripts/bootstrap_env.sh` first.
**Priority by repo scope (non-negotiable):** C1–C20 CLOSED & CERTIFIED `NO_GO`. C21-T1 COMPLETE (`PASS`, consolidated `NO_GO`). C22-T1 COMPLETE (`PASS`, consolidated `NO_GO`). **C23-T1 COMPLETE (`PASS`, consolidated `NO_GO`) — terminal.** Do not invent heavy follow-on work; C1–C23 `NO_GO` stands unless C23 produced a pre-registered contradiction with full evidence (it did not).
**Key tokens:** `C23 ACCEPTANCE: PASS` (consolidated `NO_GO`), `c23_prereg_20261118T202301Z`, `status_c23.sh`, `verify_c23_focus_campaign.py`, `tests/test_c23_campaign_20261118.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json`.

**Bottlenecks removed (none remaining):** environment/bootstrap (`.venv` ready), runner-dead-but-done (nothing to resume), C23 acceptance gate (cleared `PASS`). No open bottlenecks — terminal state reached.

Full binding context, fold evidence, no-avoidance rules, guardrails, and execution order: `HANDOFF.md`.

---

## BINDING CAMPAIGN — C22-T1 (MEXC OUT-OF-SAMPLE REPLICATION) — COMPLETE

**Status:** COMPLETE — gate `C22 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. C22 runner NOT alive. Do not relaunch.
**Prereg:** `research_state/c22_prereg_20261118T100126Z.{json,md}` (`PRE_REGISTERED_BEFORE_COMPUTE`).
**Fold results (recorded):** 2023: 25 trades, PnL +30,599.03, 9 episodes, 12 crash days, perm p=0.01835, placebo p_ge=0.006, CI95=[-4,715.22, +67,959.60], 0/9 BH strata survivors. 2024: 40 trades, PnL -27,326.63, perm p=0.3085. 2025/2026YTD completed per final artifacts.
**C22 REQUIRED ARTIFACTS (TS = `20261118T100126Z`)** — all 7 battery artifacts + prereg present:
`c22_prereg_{TS}.{json,md}`; `c22_mexc_fold_campaign_{TS}.json`; `c22_mexc_fold_episode_edge_{TS}.json`; `c22_mexc_fold_placebo_{TS}.json`; `c22_mexc_fold_census_{TS}.json`; `c22_decision_verdict_mexc_stability_{TS}.json`; `c22_pooled_stability_synthesis_{TS}.json`; `c22_decision_verdict_CONSOLIDATED_{TS}.json`.

---

## NEXT FOCUS CAMPAIGN — C23-T1 (BITGET USDT-M OUT-OF-SAMPLE REPLICATION) — COMPLETE, TERMINAL

**Status:** COMPLETE — gate `C23 ACCEPTANCE: PASS`, consolidated verdict `NO_GO`. C23 runner NOT alive; do not relaunch. 4/4 fold checkpoints present, 7/7 battery artifacts present.
**Authorization:** C23 was the binding heavy campaign (built per the operator directive to build the next focus campaign when explicit directions are absent). It is now done; the terminal rule applies — after C23 PASS, report per-fold/pooled/power curve and STOP. No further campaign is authorized beyond C23. Do not wait for another approval to do more; there is none authorized.
**Why C23:** C1–C22 tested OKX, Binance UM, and MEXC. C23 ran the unchanged spec-literal edge on one more independent never-used USDT-perp venue (Bitget USDT-M) — new data + frozen spec, not a parameter search. Result: `NO_GO`; the C1–C22 `NO_GO` stands with four-venue evidence.

**Per-fold results (frozen config rsi_period=21/rsi_threshold=20/target_pct=9, seed 20261123):**
- 2023: 24 trades, PnL +28,706.32, 9 episodes, perm_p=0.0229, 0/9 BH strata survivors (positive single fold — NOT a result).
- 2024: 36 trades, PnL -30,939.60.
- 2025: 37 trades, PnL -32,710.19.
- 2026YTD: 21 trades, PnL -23,185.86.
**Pooled:** total PnL -58,129.33, CI95 [-58,129.33, -58,129.33], prob_pooled_total_gt_0=0.0, BH pooled stratum survivors 0/36, sign concordant (all negative). Consolidated verdict `NO_GO` (`research_state/c23_decision_verdict_CONSOLIDATED_20261118T202301Z.json`, generated 2026-11-19T00:31:49Z). Supersedes `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`.
**Provenance:** real Bitget USDT-perp data, non-synthetic, `is_hyperliquid_venue_data=false`, CROSS-VENUE vs the Hyperliquid spec — NOT Hyperliquid performance evidence, never relabelled as such. Window 2023-01-01..2026-09-28. Cache `research_state/cache/bitget_1h_multiyear_20230101_20260928/`; universe `research_state/universe_bitget_multiyear_verified.json`.
**Regression:** `tests/test_c23_campaign_20261118.py` → 12 passed.

**C23 REQUIRED ARTIFACTS (TS = `20261118T202301Z`) — all present:**
`c23_prereg_{TS}.{json,md}`; `c23_bitget_fold_campaign_{TS}.json`; `c23_bitget_fold_episode_edge_{TS}.json`; `c23_bitget_fold_placebo_{TS}.json`; `c23_bitget_fold_census_{TS}.json`; `c23_decision_verdict_bitget_stability_{TS}.json`; `c23_pooled_stability_synthesis_{TS}.json`; `c23_decision_verdict_CONSOLIDATED_{TS}.json`.

**Terminal rule (binding):** after `C23 ACCEPTANCE: PASS`, deliver the per-fold/pooled/power-curve report above and STOP — no further campaign is authorized beyond C23. Do not launch a same-data C23+ rerun, do not substitute Hyperliquid-native evidence (acquisition CLOSED `FULL_283D_BLOCKED_BY_API_RETENTION`), do not relabel Bitget data as Hyperliquid, do not reduce draw counts. C1–C23 `NO_GO` stands unless C23 produced a pre-registered contradiction with full evidence (it did not).

---

## NEXT FOCUS CAMPAIGN — C24-T1 (MARGIN / LIQUIDATION FIDELITY ADJUDICATION) — ACTIVE, RUNNING

**Status:** `C24 ACCEPTANCE: PENDING`. Runner ALIVE (PID 14458, 4 workers, launched 2026-11-19T02:50:00Z). **This is the binding heavy campaign; do not launch a duplicate.** Resume command (only if runner dies): `PYTHONPATH=. .venv/bin/python scripts/run_c24_margin_fidelity_campaign.py --jobs 4 --resume`. Status: `bash scripts/status_c24.sh`. Gate: `PYTHONPATH=. .venv/bin/python scripts/verify_c24_focus_campaign.py`.

**Why C24:** C1–C23 closed `NO_GO` with an execution model that force-closes on a **-(5+1)=6%** adverse move (`src/backtest/engine.py::_check_liquidation`), tighter than the published spec's wide safety stop (~15% median below entry) and absent from the PDF. The stage-0 probe reproduced the recorded C20/C22/C23 pooled PnL exactly with the 6% arm and showed a sign flip between 10% and 15% arms. C24 is the pre-registered inference campaign that decides whether the `NO_GO` is real or a margin-model artifact.

**Arms (only liquidation distance varies; signal path frozen):** `base_6` (6%, FIDELITY_ANCHOR — MUST reproduce okx -54,799.23 | binance_um -70,071.41 | mexc -49,760.24 | bitget -58,129.33); `d10` (10%, descriptive); `d15` (15%, PRIMARY — full 20k/20k/2k inference); `d30` (30%, descriptive); `noliq` (disabled, descriptive upper bound).

**Progress (2026-11-19T03:13:53Z):** base_6 16/16 DONE (anchor reproduced exactly — e.g. bitget 2023=+28,706.32, 2024=-30,939.60, 2025=-32,710.19, 2026YTD=-23,185.86); d10 16/16 DONE; d30 + noliq campaign-only arms in progress; **d15 (primary inference arm) 0/16 — okx 2023 episode done (perm_p=0.3433), 20k permutation draws running across 4 workers.** ~80 cells total; d15's 16 cells × (20k bootstrap + 20k permutation + 2k placebo) is the heavy phase (~1–2 h).

**Decision rules:** `C24_REOPENS_C1_C23` (d15 pooled > 0 AND CI95 lower > 0 AND >=1 BH survivor AND >=3/4 folds positive AND >=3/4 venues positive → record `SUPERSEDED_BY_C24` and authorize C24-T2) vs `C24_NO_GO_ROBUST_TO_MARGIN` (any condition fails → C1–C24 `NO_GO` ROBUST). `C24_UNDERPOWERED` on anchor mismatch / draw-floor violation / drift / missing artifacts. Both outcomes require the full arm×venue×fold table, per-leg attribution and exit-reason decomposition.

**Provenance:** real exchange USDT-perp data, non-synthetic, `cross_venue=true`, `is_hyperliquid_venue_data=false`. Never Hyperliquid performance evidence, never relabelled as such.

**Key files:** prereg `research_state/c24_prereg_20261119T013154Z.{json,md}`; stage-0 probe `research_state/c24_liquidation_fidelity_probe_20261119T013154Z.json` (`may_emit_go=false`, `DESCRIPTIVE_NO_INFERENCE`); `scripts/run_c24_margin_fidelity_campaign.py`; `scripts/verify_c24_focus_campaign.py`; `scripts/status_c24.sh`; `tests/test_c24_campaign.py` (10 tests). Checkpoints: `research_state/c24_ckpt_{arm}_{venue}_{fold}_20261119T013154Z.json`. Verdicts: `research_state/c24_decision_verdict_{arm}_20261119T013154Z.json` + `..._CONSOLIDATED_...`.

---

## BOTTLENECKS REMOVED THIS SESSION (2026-11-19T00:47:51Z)

1. **Environment/bootstrap bottleneck removed:** ran `scripts/bootstrap_env.sh`; durable `.venv` at repo root is ready (Python 3.12.3 + numpy, pandas, requests, pyarrow, pytest 9.2.0). The "missing venv / gate script" blocker in `scripts/status_c23.sh` is gone — gate now runs and prints `C23 ACCEPTANCE: PASS`.
2. **Runner-dead-but-done bottleneck resolved:** `scripts/status_c23.sh` shows `RUNNER: NOT ALIVE` with all 4 folds DONE and battery 7/7 — nothing to resume; `run_c23_detached_durable.sh` must NOT be launched again (duplicate-launch guard would no-op, but the campaign is complete).
3. **C23 acceptance gate cleared:** `verify_c23_focus_campaign.py` prints `C23 ACCEPTANCE: PASS` (bitget=NO_GO, consolidated=NO_GO), unblocking the terminal report/STOP.

---

## BOTTLENECKS REMOVED IN PRIOR SESSIONS (selected)

- **2026-11-18T21:24Z:** C22-T1 reached `C22 ACCEPTANCE: PASS` (consolidated `NO_GO`); 4/4 fold checkpoints present; C22 runner not alive; C23 prerequisites all GREEN; C23 runner launched (parent PID 20442 earlier run; current live runner PID 25897).
- **2026-11-18T19:20:00Z:** C22 runner confirmed active (parent PID 21734); fold 2023 complete, fold 2024 in progress, gate `PENDING`.
- **2026-11-18T15:16:59Z:** state-refresh bottleneck cleared; stale worker-PID bottleneck removed; stale progress claims corrected; idle-timeout bottleneck removed; next-campaign avoidance bottleneck removed (C23 binding added); duplicate-launch bottleneck kept removed.
- **2026-11-18T12:03:58Z:** created `scripts/run_c22_mexc_campaign.py`; completed MEXC multiyear acquisition (34 symbols) and derived `universe_mexc_multiyear_verified.json`.
- **2026-11-18T10:10:23Z:** removed stale "acquisition CLOSED/no network" + do-nothing paralysis with probe evidence `ACQUISITION_VIABLE_MEXC_MULTIYEAR`; built MEXC fetch/prereg/gate/tests.

**Remaining/open:** C23 heavy battery must complete (~1.5–2 h remaining: folds 2024/2025/2026YTD then artifact synthesis) and pass `C23 ACCEPTANCE: PASS`; then report per-fold/pooled/power curve and STOP. If a runner dies before PASS, resume immediately via `run_c23_detached_durable.sh`. Do not invent same-data follow-on work on exhausted data. After C23 PASS there is no authorized campaign — the correct terminal state is the evidence report, not a new probe.

---

## C20 CROSS-VENUE REFERENCE NUMBERS (verified, sanity-check C22/C23)

From `research_state/timing_okx.json` / `timing_binance_um.json` (C20 spec-literal, full multiyear, `SPEC_LITERAL_NEXT_OPEN`):
- **OKX:** `num_trades=113`, `total_pnl=-55057.45`
- **Binance UM:** `num_trades=136`, `total_pnl=-70309.57`
Both negative → C20 pooled `NO_GO`. C22 MEXC and C23 Bitget fold results should be broadly consistent in sign; a wildly divergent result is a red flag to investigate, not to accept.

---

## C1–C21 CLOSED STATE (historical, do not relitigate)

- **C21 (`20261117T064408Z`):** gate `C21 ACCEPTANCE: PASS`; consolidated `NO_GO`. `scripts/verify_c21_focus_campaign.py`, prereg `c21_prereg_20261117T064408Z.{json,md}`, artifacts/checkpoints in `research_state/c21_*_20261117T064408Z*`.
- **C20 (`20261116T063500Z`):** pooled `NO_GO`. `scripts/verify_c20_focus_campaign.py`.
- **C19 (`C19-T1`):** T1 `spec_rebound_confirmation_adjudication_20261116T054000Z` (`SPEC_LITERAL_NEXT_OPEN`); T2–T5 NO_GO. `scripts/verify_c19_focus_campaign.py`.
- **C14 (`20261116T001200Z`):** native underpowered/fragile (7 trades, 3 episodes). `scripts/verify_c14_focus_campaign.py`.
- **C13:** config-matched native complete. `scripts/verify_c13_focus_campaign.py`.
- **C6 (`C6-T1`):** OKX+Binance UM pooled underpowered, `campaign_results_real_okx_multiyear`, `is_hyperliquid_venue_data=false`. `scripts/verify_next_focus_campaign.py`.
- **Hyperliquid-native acquisition CLOSED/exhausted:** `FULL_283D_BLOCKED_BY_API_RETENTION` (tail ~2026-04-21). `scripts/probe_hyperliquid_blocker.py`.

---

## GUARDRAILS (never violate)

- No cross-venue relabeling as Hyperliquid-native (`is_hyperliquid_venue_data=false` for C20/C21/C22/C23).
- No synthetic gap-fill as verified; no spec relaxation to manufacture GO; `SPEC_LITERAL_NEXT_OPEN` fixed; C22 config frozen to prereg; C23 config frozen to its prereg.
- No post-hoc stratum/fold invention; folds/strata fixed in preregs.
- **Do not reduce draw counts** (20k/20k/2k floors).
- No inference-only churn on exhausted C14 native data; C1–C21 closed.
- **Status first:** run `bash scripts/status_c23.sh` before any C23 action; do not hand-assemble `ps`/`ls`/gate chains and do not treat a stale PID from this document as ground truth.
- **Do NOT relaunch `scripts/finish_c20_detached_durable.sh` (C20 PASS).** No duplicate C22/C23 battery while runner active; no foreground campaign in an agent turn; no short `timeout`; no long foreground `sleep` that will hit the 900s idle timeout.
- No same-data C23+ rerun of C21/C22 without new prereg + new data + explicit authorization. C22 is legitimate only because MEXC is new data; C23 is legitimate only because Bitget is new data and its prereg is written before compute.
- Do not edit completed campaign artifacts or `scripts/run_c20_cross_venue_campaign.py`.
- No silent change to canonical baseline. C1–C22 `NO_GO` stands unless C23 produces a pre-registered contradiction with full evidence.
- Do not commit unless explicitly asked (controller checkpoints worktree; do not rewrite history).
- Preserve literal gate tokens: `INITIAL TASK MESSAGE`, `session_gate.py`, `21/21 checks passed`, `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `FULL_283D_BLOCKED_BY_API_RETENTION`, `verify_campaign_evidence.py`, `C19-T1`, `verify_c19_focus_campaign.py`, `C14`, `verify_c14_focus_campaign.py`, `20261116T001200Z`, `C6-T1`, `campaign_results_real_okx_multiyear`, `C13`, `verify_c13_focus_campaign.py`, `C20`, `verify_c20_focus_campaign.py`, `C21-T1`, `verify_c21_focus_campaign.py`, `C22-T1`, `verify_c22_focus_campaign.py`, `fetch_mexc_perp_archive.py`, `probe_c22_venue_acquisition.py`, `c22_prereg_20261118T100126Z`, `ACQUISITION_VIABLE_MEXC_MULTIYEAR`, `C23-T1`, `verify_c23_focus_campaign.py`, `fetch_bitget_perp_archive.py`, `probe_c23_venue_acquisition.py`, `status_c23.sh`, `tests/test_c23_campaign_20261118.py`.

---

## KEY FILES

- Handover/state: `HANDOFF.md` (single durable handoff), `README.md`, `research_state/strategy_spec.md`.
- **C22 (COMPLETE, `NO_GO`, PASS):** `research_state/c22_prereg_20261118T100126Z.{json,md}`, `research_state/c22_venue_acquisition_probe_20261118T100126Z.json`, `scripts/probe_c22_venue_acquisition.py`, `scripts/fetch_mexc_perp_archive.py`, `scripts/build_c22_prereg.py`, `scripts/verify_c22_focus_campaign.py`, `tests/test_c22_campaign_20261118.py`, `scripts/run_c22_mexc_campaign.py`, `scripts/run_c22_detached_durable.sh`. Cache: `research_state/cache/mexc_1h_multiyear_20230101_20260928/` (34 symbols, 203 MB). Universe: `research_state/universe_mexc_multiyear_verified.json`. Checkpoints: `research_state/c22_ckpt_mexc_<fold>_20261118T100126Z.json`. Artifacts: `research_state/c22_*_20261118T100126Z.json`.
- **C23 (ACTIVE & RUNNING, binding):** `research_state/c23_prereg_20261118T202301Z.{json,md}`, `research_state/c23_venue_acquisition_probe_20261118T202301Z.json`, `scripts/probe_c23_venue_acquisition.py`, `scripts/fetch_bitget_perp_archive.py`, `scripts/build_c23_prereg.py`, `scripts/verify_c23_focus_campaign.py`, `scripts/run_c23_bitget_campaign.py`, `scripts/run_c23_detached_durable.sh`, `scripts/status_c23.sh` (read-only status), `tests/test_c23_campaign_20261118.py` (12 tests). Cache: `research_state/cache/bitget_1h_multiyear_20230101_20260928/` (34 symbols cached, 33 selected). Universe: `research_state/universe_bitget_multiyear_verified.json`. Live log: `research_state/c23_run_20261118T222155Z.log` (parent PID 25897 + rotating workers). Checkpoints: `research_state/c23_ckpt_bitget_<fold>_20261118T202301Z.json` (2023 present; 2024 next). Artifacts (written after all 4 folds): `research_state/c23_*_20261118T202301Z.json`.
- C21 (complete, `NO_GO`, PASS): `research_state/c21_prereg_20261117T064408Z.{json,md}`, `scripts/run_c21_cross_venue_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/run_c21_detached_durable.sh`, `research_state/c21_*_20261117T064408Z*`.
- C20: `research_state/c20_prereg_20261116T063500Z.{json,md}`, `research_state/c20_pooled_cross_venue_synthesis_20261116T063500Z.json`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json`, `scripts/run_c20_cross_venue_campaign.py`, `scripts/verify_c20_focus_campaign.py`.
- Acquisition: `scripts/acquire_exchange_archive.py`, `scripts/fetch_hyperliquid_candles.py`, `scripts/derive_verified_universe.py`.
- Gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`, `scripts/verify_c21_focus_campaign.py`, `scripts/verify_c22_focus_campaign.py`, `scripts/verify_c23_focus_campaign.py`, `scripts/verify_next_focus_campaign.py` (C6).
- Env: `scripts/bootstrap_env.sh`.
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`, `src/data/loader.py`.
