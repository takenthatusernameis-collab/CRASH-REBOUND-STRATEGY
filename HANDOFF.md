# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-16T02:42:51Z — **C15 COMPLETE (evidenced hard blocker, gate PASS); C16 IS THE ACTIVE HEAVY CAMPAIGN — DO SUBSTANTIVE WORK.** "Closed state / do nothing substantive" remains **REMOVED**. This is the single durable handoff and the **initial task message** for the next agentic work session.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap). **Priority:** decision-grade crash-rebound verdict on **Hyperliquid-native** evidence with honest dependence-aware inference. Cross-venue OKX/Binance remain `is_hyperliquid_venue_data=false` and must NOT be relabeled as Hyperliquid.

**Current bottleneck (resolved — C15 executed):** no verified Hyperliquid-native hourly archive ≥2023-01-01 is reachable (public API moving tail from ~2026-04-21; Ironflow `ironflow/hyperliquid-candles-1h` starts 2025-05-25, already exhausted as C14 widest archive). C15 T1 acquisition attempted with command-level evidence; T3 evidenced hard blocker filed. Resolution requires an **operator-supplied verified Hyperliquid-native archive** (≥2023-01-01 target, n≥4+ independent episodes) or a refreshed evidenced hard blocker — never a bare "closed/no work", never a handoff-only stop.

**Priors (do not relitigate/rewrite):** FINAL consolidated **`NO_GO`** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`; cross-venue C10 `NO_GO` (0/7, `is_hyperliquid_venue_data=false`) `research_state/decision_verdict_consolidated_20261115T122636Z.md`; native C11.3 `NO_GO/FRAGILE_NOT_DECISION_GRADE` `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; C12 `NO_DECISION_GRADE_GO` `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`; C13 `UNDERPOWERED` `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`; C14 `UNDERPOWERED` `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.md`; C15 `BLOCKED_EVIDENCED_DATA_REQUIRED` `research_state/c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.md`.

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-16T02:42:51Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`). Do substantive research work now — a handoff-only stop is not acceptable.** C15 is **COMPLETE**: T1 acquisition attempted with full command/network evidence (HF `ironflow/hyperliquid-candles-1h` probe: rows 3,641,742, range 2025-05-25T14:00:00Z..2026-10-31T23:00:00Z, covers spec window but cannot reach ≥2023-01-01; live API retention probe: full_window_served=false, 3849/6792 bars, earliest 2026-04-21T15:00:00Z, moving tail). C15 gate `verify_c15_focus_campaign.py` prints `C15 ACCEPTANCE: PASS` (verdict `BLOCKED_EVIDENCED_DATA_REQUIRED`). C14 remains `UNDERPOWERED` — 3 effective episodes / 4 crash days / 7 trades; bootstrap 95% CI [−1144,+17547] spans zero (first CI exclusion n=4, archive max 4); permutation p=0.03595; placebo p=0.4444. Consolidated final verdict C1–C13 remains `NO_GO`. **Do not relabel cross-venue as Hyperliquid, do not fabricate data, do not relax $5M/spec defaults, do not edit canonical C1–C14 or C15 artifacts.**

### C16 — Operator archive ingest + full C16 battery to decision-grade power (ACTIVE, HEAVY, MACHINE-GATED)

**Goal:** reach n>=4+ independent crash episodes (CI-excluding-zero feasible) on verified Hyperliquid-native data via operator-supplied archive ≥2023-01-01, execute the full battery + C16 acceptance gate, or produce a refreshed evidenced hard blocker. Execute in order; do not skip T1.

**Bottleneck removal already done:** venv bootstrapped at `/tmp/crs-venv` (`bash scripts/bootstrap_env.sh`), `session_gate.py` **21/21 checks passed**, `verify_c14_focus_campaign.py` **C14 ACCEPTANCE: PASS**, `verify_c15_focus_campaign.py` **C15 ACCEPTANCE: PASS**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**.

**T1 — Data acquisition (REQUIRED FIRST, heavy):**
1. Poll/re-attempt acquisition of an operator-supplied verified Hyperliquid-native hourly OHLCV archive extending to **≥2023-01-01** (target multiyear parity for episode-count parity with cross-venue) via `scripts/fetch_hyperliquid_candles.py` and/or `scripts/acquire_exchange_archive.py`. Record exact commands, stdout/stderr, HTTP/DNS/network evidence to a timestamped `research_state/c16_acquisition_attempt_<UTC>.{json,md}` (or equivalent) — no bare claims.
2. **If reachable/acquired:** build extended archive (parquet, per-file SHA256, non-synthetic attestation/SOURCE.md) → intake validate with `scripts/validate_hyperliquid_archive_intake.py` (record stem) → derive/confirm universe at $5M gate (`scripts/build_c14_universe_scope.py` or C16 equivalent; spec defaults unchanged) → prepare cache/provenance. Keep `is_hyperliquid_venue_data=true` only for native artifacts.
3. **If not acquirable:** record evidenced hard blocker (command + HTTP + DNS + reachability) and a concrete `data_request_stem` requesting additional Hyperliquid-native episodes/windows; proceed to T3 outcome.

**T2 — Full battery + verdict (ONLY if T1 yields usable extended native evidence):** run the full C14-aligned battery on the extended native universe (no spec relaxation): crash-event census → spec-canonical campaign (rsi20/t9) → episode-edge (20000 draws, recorded seed) → placebo (exact/enumerated as applicable) → decision verdict (GO / UNDERPOWERED / NO_GO with power curve) → acceptance gate (implement/run `verify_c16_focus_campaign.py` or documented equivalent) that must print `C16 ACCEPTANCE: PASS`. Pre-registered GO criteria: CI95 excludes zero + permutation p<0.05 + placebo p_ge_canonical<0.05 + spot leg > 0.

**T3 — Blocked-but-evidenced outcome (ONLY if no extended native data possible):** refresh command/HTTP/DNS evidence + `data_request_stem` (update `research_state/c16_data_request_stem_<UTC>.md`) + updated verdict/status artifacts proving C14-underpowered gap cannot be closed with available native data. A bare "closed/no work" is forbidden.

### Required gates/commands (run and report)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # must be 21/21 checks passed
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py    # must remain C14 ACCEPTANCE: PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c15_focus_campaign.py    # must remain C15 ACCEPTANCE: PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # read-only; record stem for T1/T3
```
If C16 artifacts are produced, also run the C16 acceptance gate and include its `C16 ACCEPTANCE: PASS/FAIL` line.

### Acceptance contract (done-marker)
Complete iff (A) `C16 ACCEPTANCE: PASS` + verdict `GO` with pre-registered criteria met; or (B) `C16 ACCEPTANCE: PASS` + verdict `UNDERPOWERED`/`NO_GO` with full battery executed on widest available/extended native universe and a power curve + explicit data request for additional episodes/windows; or (C) refreshed evidenced hard blocker (no acquirable extended verified native archive) with command/HTTP/DNS evidence + `data_request_stem` — **never** a bare "closed/no work".


## Gate-token contract (DO NOT remove — machine-checked)

This file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `verify_c13_focus_campaign.py` (C13 acceptance gate)
- `verify_c14_focus_campaign.py` (C14 acceptance gate)
- `verify_c15_focus_campaign.py` (C15 acceptance gate)
- `verify_c16_focus_campaign.py` (C16 acceptance gate)
- `C13` (C13 campaign token) and `C14` (C14 campaign token) and `C15` (C15 campaign token) and `C16` (C16 active campaign token)
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## Verified state (as of 2026-11-16T02:42:51Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` (C16 active initial task message) | repo root |
| Session gate | **21/21 checks passed** | `scripts/session_gate.py` (confirmed 2026-11-16T02:42Z) |
| C14 acceptance gate | **PASS** | `scripts/verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS` |
| C15 acceptance gate | **PASS** | `scripts/verify_c15_focus_campaign.py` → `C15 ACCEPTANCE: PASS` (verdict BLOCKED_EVIDENCED_DATA_REQUIRED) |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (re-run at session end) | `scripts/verify_campaign_evidence.py` |
| C14 verdict | **UNDERPOWERED** (3 eps / 4 days / 7 trades, CI spans zero n=3, first exclusion n=4, max 4) | `decision_verdict_hyperliquid_native_c14_20261116T001200Z.{md,json}` |
| C15 verdict | **BLOCKED_EVIDENCED_DATA_REQUIRED** (T1 executed, T3 hard blocker + data request stem) | `c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}` |
| C14 key artifacts | intake/universe/campaign/census/episode-edge/placebo complete | `archive_intake_validation_20261116T001129Z.json`, `universe_hyperliquid_ironflow_wide_20261115T225100Z.json`, `campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json`, `crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json`, `episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json`, `placebo_portfolio_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C15 key artifacts | acquisition attempt + verdict + data request stem | `c15_acquisition_attempt_20261116T024001Z.{md,json}`, `c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}`, `c15_data_request_stem_20261116T024001Z.md` |
| Hyperliquid blocker probe (fresh) | **FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1** — 235 perps/26 passing/26 probed, 6792 expected, 3849 returned, 2943 missing, earliest 2026-04-21T15:00:00Z, full_window_served=false (moving tail) | `research_state/hyperliquid_retention_probe.json` (2026-11-16T02:29:56Z run) |
| C16 next campaign | **ACTIVE — NOT YET EXECUTED** (T1 acquisition/evidenced blocker required) | `HANDOFF.md` → NEXT SESSION START HERE (T1→T2 battery/verdict/gate, or T3 evidenced hard blocker+data_request) |
| Venv bootstrap | `/tmp/crs-venv` ready | `scripts/bootstrap_env.sh` (bottleneck removed) |

**Key C14 numbers:** N=7 trades / 3 episodes / 4 symbols / 4 crash days; bootstrap 95% CI [−1144, +17547]; permutation p=0.03595; placebo p=0.4444. **C16 target:** n>=4+ independent episodes via native window extension (≥2023-01-01 parity) to reach CI-excluding-zero (GO), or refreshed evidenced hard blocker if no more native data.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Priors/final: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{md,json}`, `decision_verdict_consolidated_20261115T122636Z.md`, C11.3/C12/C13/C14/C15 verdict+evidence stems, C6/C7/C10 stems, `campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**.
- Native priors: `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, C14 ironflow-wide archive/cache/universe + validation/campaign/census/edge/placebo/verdict stems `*_20261116T001129Z*` / `*_20261116T001200Z*`.
- C15 artifacts: `c15_acquisition_attempt_20261116T024001Z.{md,json}`, `c15_decision_verdict_hyperliquid_native_c15_20261116T024001Z.{md,json}`, `c15_data_request_stem_20261116T024001Z.md`.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Hard prohibitions
- No GO claim without pre-registered criteria met (CI95 excludes zero + permutation p<0.05 + placebo p_ge_canonical<0.05 + spot leg > 0). No relabeling cross-venue as Hyperliquid. No fabrication/synthesis. No spec relaxation ($5M gate / RSI / spec defaults). No churn/avoidance or handoff-only stop. No bare "closed/no work" (C16 requires T1 attempt + T2 battery or T3 evidenced blocker+data_request). Single durable handoff only. Preserve gate-token contract tokens. Do not edit canonical C1–C15 artifacts.