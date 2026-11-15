# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T17:37:01Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify edge on **Hyperliquid-native** evidence with honest dependence-aware inference; where canonical strategy fails, run the next highest-signal native campaign implied by completed evidence.

**Baseline (revalidated 2026-11-15T17:01Z):** branch `main`; env `/tmp/crs-venv` ready. **C1–C10 COMPLETE, C11.0/C11.1/C11.2 DONE, C11.3 DONE (native battery + native verdict + consolidated native verdict complete).** Gates green this session: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**.

**Canonical/native verdict state:** cross-venue consolidated verdict remains **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). **Hyperliquid-native canonical RSI(21)<20 verdict is `NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7 stop/go criteria passed** (`research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; consolidated native stem `research_state/decision_verdict_consolidated_20261115T155318Z.md`). Native 283d Ironflow cache: 43 RSI<20 events / 7 signal-gate / 6 trades, total **+4,292.50** but **spot coin PnL −3,968.80**, ETH hedge +8,261.31, rebound-short 0. Episode-block bootstrap CI **[−1,143.66, +10,339.42]** (spans 0), conditional temporal permutation **p=0.0800** (3 episodes/4 crash days), exact 6-of-7 placebo **p_ge_canonical=0.7143**. Not a GO.

**Bottleneck removed this session (2026-11-15T17:01Z):** the C12 grid (`rsi_threshold` × `target_pct`) was **not runnable** — the handoff previously named a nonexistent `scripts/run_portfolio_campaign.py`, and the real runner `scripts/run_real_campaign.py` hardcoded `StrategyConfig(...)` with no grid knobs. **Fixed:** added opt-in flags `--rsi-period`, `--rsi-threshold`, `--target-pct`, `--rebound-short-target-pct`, `--rebound-short-time-exit-bars`, `--rebound-short-require-bounce-confirm`, `--entry-spec-literal-next-open` (all default `None`/off → canonical baseline byte-for-byte unchanged). Each override is recorded verbatim in the exported `config` block. **Proven runnable:** a real-engine native run `--rsi-threshold 25 --target-pct 5.0` produced 17 trades / total_pnl −3,596.44 with the overrides recorded. 91 runner-related tests pass; all three gates green.

**Remaining binding next work:** **C12 heavy native discovery battery** on the real native cache (no handoff-only sessions).

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T17:01:24Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C11.3 are COMPLETE. Canonical `RSI(21)<20` is **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered)** on Hyperliquid-native evidence (0/7 criteria; spot alpha negative; hedge-masked headline). **Do not re-litigate C11.3 or re-run cross-venue canonical campaigns/censuses/C6-T3/C7/C10 without a NEW artifact stem and a documented reason.**

**PRIMARY MISSION — C12: execute a pre-registered, real-engine Hyperliquid-native discovery/robustness battery targeting the only evidence-backed native signals, and write a native C12 verdict.** This is heavy compute on real data; a session that only edits handoff/status or reruns gates without producing C12 artifacts has failed. **The tooling bottleneck is already removed — the runner accepts the grid knobs below; a future session has no excuse to avoid running them.**

### 0) Mandatory gate + readiness (every session, record stems/verdicts)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem); API retention block expected
```
Native inputs (fixed, do not replace): cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`, canonical native campaign/census/verdict/prereg/battery stems under `research_state/*hyperliquid*20261115T155*` and `*_20251220_20260928*` as applicable. **Provenance caveat (binding in every artifact):** real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true` for this native cache but not exchange-snapshot provenance — state it explicitly.

### 1) C12.0 — Pre-register C12 (REQUIRED before compute)
Write `research_state/hyperliquid_native_c12_prereg_<TS>Z.{json,md}` (design-only, new stem) specifying: hypotheses (a) `rsi_threshold` in `[20,22,25,30]` and (b) `target_pct` in `[5.0,9.0]` / rebound-short behavior on native Hyperliquid; primary/secondary metrics (spot coin PnL, hedge PnL, rebound-short PnL, total, trade count, episode count/crash days, max DD, cost-stress); dependence-aware inference plan (episode-block bootstrap CI + conditional temporal-edge permutation where feasible; honest power/underpowered handling given 283d/3-episode native window); and explicit NO-GO/insufficient criteria (do **not** claim GO from point PnL, in-sample sensitivity without inference, or hedge-masked totals). Treat `rsi_threshold_25`/`target_pct_5` signals from C11.3 as discovery only (originating from robustness sweep), not validated edge.

### 2) C12.1 — Real-engine native parameter campaigns (REQUIRED)
Run real portfolio-engine campaigns on the native cache/universe for the pre-registered grid (at minimum `rsi_threshold∈{20,22,25,30}` × `target_pct∈{5.0,9.0}`; include canonical `20/9.0` as anchor). **Use `scripts/run_real_campaign.py` with the grid knobs added this session** (confirmed via `--help`), one run per config, with NEW stems per config:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe-file research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --rsi-threshold <20|22|25|30> --target-pct <5.0|9.0> \
  --output-prefix campaign_results_real_hyperliquid_native_c12_rsi<X>_t<Y>_<TS>Z
```
Record full leg decomposition, exit reasons, trades, and provenance/caveats. Each run's exported `config` block records the overrides, so the artifact is self-describing. No synthetic data, no fabrication. (Canonical anchor `20/9.0` already exists as `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` — do not overwrite it; reuse or re-run under a `c12_` stem only if needed for comparability.)

### 3) C12.2 — Dependence-aware inference for lead configs (REQUIRED)
For the pre-registered lead candidate(s) (e.g. best spot-alpha and best rebound-short/total configs, plus canonical anchor), run episode edge / crash-event census alignment and portfolio placebo as appropriate with fixed seeds, producing NEW stems: `crash_event_census_hyperliquid_native_c12_<...>_<TS>Z.*`, `episode_edge_hyperliquid_native_c12_<...>_<TS>Z.*`, `placebo_portfolio_hyperliquid_native_c12_<...>_<TS>Z.*`. Report episodes/clustering, bootstrap CI, permutation p, placebo percentile, effective N; label `underpowered` where criteria not met. Do not substitute C11.3 numbers for new configs.

### 4) C12.3 — Native C12 verdict (REQUIRED)
Write `research_state/decision_verdict_hyperliquid_native_c12_<TS>Z.md` (and optional consolidated update `decision_verdict_consolidated_<TS>Z.md` if warranted) that: re-maps stop/go criteria for each tested hypothesis on native evidence; separates **spot coin alpha**, **ETH hedge contribution**, and **rebound-short alpha**; states whether any config clears pre-registered thresholds; explicitly preserves `NO_GO` for canonical unless re-validated under pre-registered rules; and gives a concrete next campaign only if evidence supports it. **Never flip to GO from hedge-masked totals or unpowered point estimates.**

### 5) Close (every session)
- Re-run gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**.
- Re-timestamp this handoff with exact C12 artifact stems/verdicts; keep gate-token contract intact. No second handoff/status file.

**Definition of done (C12):** prereg + real-engine native campaign grid artifacts + dependence-aware inference for lead config(s) + `decision_verdict_hyperliquid_native_c12_<TS>Z.md`, with all three gates green and this handoff re-timestamped. **Handoff-only or gate-only sessions fail C12.**

---

## Gate-token contract (DO NOT remove — machine-checked)

The handoff is parsed by `scripts/session_gate.py` (`check_handoff`) and `scripts/verify_next_focus_campaign.py`. To keep gates green this file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## What changed this session (2026-11-15T17:01Z)

- **Bottleneck removed (the important change):** C12 grid was unrunnable — prior handoff cited nonexistent `scripts/run_portfolio_campaign.py`, and `scripts/run_real_campaign.py:491` hardcoded `StrategyConfig`. Added opt-in C12 grid flags (`--rsi-period`, `--rsi-threshold`, `--target-pct`, `--rebound-short-target-pct`, `--rebound-short-time-exit-bars`, `--rebound-short-require-bounce-confirm`, `--entry-spec-literal-next-open`); defaults `None`/off preserve the canonical baseline. Grid overrides are recorded in the exported `config` block for provenance.
- **Verified:** `run_real_campaign.py --help` lists all flags; defaults parse to `None`; real native probe `--rsi-threshold 25 --target-pct 5.0` → 17 trades, total_pnl −3,596.44, overrides recorded (`rsi_threshold 25.0 target_pct 5.0 rsi_period 21`); probe artifacts cleaned. Runner-related tests **91 passed** (`test_real_campaign_pipeline`, `test_reproducibility_contract_real_okx_full`, `test_vault_fees_export_wiring`, `test_real_campaign_volume_threshold`, `test_real_campaign_synthetic_cache_rejection`, `test_real_campaign_spec_volume_cli_guardrail`, `test_rsi_trigger_not_killed_by_non_spec_ma_downtrend_filter`, `test_archive_universe_hardening`, `test_provenance_volume_observed_min_required`, `test_backtest_api_guardrails`, `test_universe_membership_vs_percode`, `test_cache_sha256_verification`, `test_verified_consumer_temp_manifest_cache_dir_pairing`, `test_repair_manifest_volume_coverage`).
- **Gates re-run and green:** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**.
- **Handoff rewritten** as single clear timestamped initial task for next session (C12) with corrected, executable runner commands. Gate-token contract preserved; no second handoff/status file.

## Verified state (as of 2026-11-15T17:01Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | `scripts/bootstrap_env.sh` / venv present |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` (17:01Z) |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` (17:01Z) |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` (17:01Z) |
| **C12 tooling** | **UNBLOCKED — grid knobs in `run_real_campaign.py`** | `--rsi-threshold`/`--target-pct` etc.; defaults `None`; overrides recorded in `config` export |
| Cross-venue consolidated verdict | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| **C11.1 native archive/cache** | `ACCEPT_AS_EVIDENCE_CANDIDATE`; 5 symbols × 6792 bars; node-derived Ironflow HF (CC BY 4.0) | `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json` |
| **C11.3 native campaign/census** | 6 trades, +4,292.50; 43 events / 7 signal-gate / 6 trades | `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, `crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.{json,md}` |
| **C11.3 episode edge** | 3 episodes / 4 crash days; bootstrap CI [−1,143.66,+10,339.42]; perm p=0.0800; **underpowered** | `episode_edge_hyperliquid_native_20261115T155318Z.{json,md}` |
| **C11.3 placebo** | exact 7_choose_6, p_ge_canonical=0.7143; **underpowered** | `placebo_portfolio_hyperliquid_native_20261115T155625Z.{json,md}` |
| **C11.3 robustness** | spot −3,968.80 / hedge +8,261.31 / rebound 0; 5x slippage −891.35; **FRAGILE_NOT_DECISION_GRADE** | `multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.{json,md}` |
| **Native verdict** | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** | `decision_verdict_hyperliquid_native_20261115T155318Z.md` |
| **Native consolidated verdict** | present (C11.3) | `decision_verdict_consolidated_20261115T155318Z.md` |
| API retention probe (C11.0 baseline) | 3861/6792 bars; `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` (expected) | `hyperliquid_retention_probe.json` |

## Bottlenecks (current)

1. **C12 native discovery battery — NOT YET RUN (PRIMARY).** Pre-reg + real-engine grid + dependence-aware inference + native C12 verdict required on Ironflow native cache. **Tooling is now unblocked** (grid flags in `run_real_campaign.py`); the only remaining work is execution. Do not stop at handoff/gates.
2. **Statistical power — structural.** 283d native window yielded 3 episodes/4 crash days/6 canonical trades; any discovery config must report honest power/underpowered status (bootstrap/permutation/placebo/effective N), not point-PnL claims.
3. **Canonical strategy economics — falsified on native sample.** RSI(21)<20 spot coin alpha negative (−3,968.80), headline masked by ETH hedge (+8,261.31); rebound-short inactive at 9% target. C12 must separate legs and avoid hedge-masked GO claims.
4. **Live Hyperliquid API 1h retention — external, expected (non-blocking).** Full-window evidence comes from accepted Ironflow archive, not API.
5. **Cross-venue evidence — exhausted/CLOSED.** OKX/Binance remain `is_hyperliquid_venue_data=false`; do not rerun without new stem + reason.

Removed/in force (do not revert): native archive acquired+accepted, C11.3 complete, RSI incremental cache, epoch-timestamp fix, placebo fork-parallel `--jobs`, retention-decay no-re-fetch rule, **C12 grid knobs in `run_real_campaign.py`**.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Cross-venue multi-year/canonical artifacts under `research_state/` (`campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**).
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, `crash_event_census_hyperliquid_ironflow_native_20261115T155226Z.*`, `episode_edge_hyperliquid_native_20261115T155318Z.*`, `placebo_portfolio_hyperliquid_native_20261115T155625Z.*`, `multiyear_robustness_battery_hyperliquid_native_20261115T155522Z.*`, `decision_verdict_hyperliquid_native_20261115T155318Z.md`, `decision_verdict_consolidated_20261115T155318Z.md`, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only

# C12 (next): prereg + real-engine native grid via run_real_campaign.py knobs +
# episode edge / placebo for lead configs + native C12 verdict — see INITIAL TASK MESSAGE.
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe-file research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --rsi-threshold 25 --target-pct 5.0 \
  --output-prefix campaign_results_real_hyperliquid_native_c12_rsi25_t5_<TS>Z
```

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite or only gate reruns.** C12 requires prereg + compute artifacts + native C12 verdict.
- **Do not claim the C12 grid is blocked.** `scripts/run_real_campaign.py` accepts `--rsi-threshold`/`--target-pct` (etc.) as of 2026-11-15T17:01Z; run it. The old `scripts/run_portfolio_campaign.py` reference is removed — it never existed.
- **Do not claim GO from hedge-masked totals, point PnL, or discovery-only sensitivity** (`rsi_threshold_25`/`target_pct_5` findings are hypothesis-generating until pre-registered and dependence-tested).
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` for OKX/Binance.
- **Do not misrepresent native archive provenance.** Node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`; record caveat in every native artifact.
- **Do not fabricate/synthesize data.** No synthetic candles/archives/results.
- **Do not relax `volume_filter_ok` / trailing-24h ≥ $5M gate or spec-literal opt-in defaults.**
- **Do not re-run canonical campaigns/censuses/C6-T3/C7/C10/C11.3 without a new artifact stem and documented reason.**
- **Do not revert RSI incremental cache, epoch-timestamp fix, placebo fork-parallel runner, or the new C12 grid knobs.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

(End of file)