# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T18:20:00Z — C12 executed (prereg + real-engine native grid + censuses + dependence-aware inference + native C12 verdict). C12 not decision-grade GO; canonical remains NO_GO.
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify edge on **Hyperliquid-native** evidence with honest dependence-aware inference; where canonical/C12 fail, run the next highest-signal native campaign implied by completed evidence.

**Baseline (revalidated 2026-11-15T18:20Z):** branch `main`; env `/tmp/crs-venv` ready. **C1–C11.3 COMPLETE; C12 COMPLETE (discovery, not decision-grade).** Gates: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**.

**Verdict state:**
- Cross-venue consolidated: **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). `is_hyperliquid_venue_data=false` for OKX/Binance.
- Native canonical (C11.3): **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** (`research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; consolidated native `research_state/decision_verdict_consolidated_20261115T155318Z.md`). 6 trades, spot −3,968.80, hedge +8,261.31, rebound 0, total +4,292.50.
- **Native C12 (2026-11-15T18:00Z stem family): `NO_DECISION_GRADE_GO` / discovery only** (`research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`). Best in-sample: `c12_25_9` (RSI 25, target 9%) total +23,244.22 (spot +6,836.44, hedge +4,762.24, rebound +11,904.32; 17 trades / 10 episodes / 11 crash days) but episode-block bootstrap CI95 spans 0 (spot [−26,795, +36,129], total [−36,650, +74,463], P(total>0)=0.770) — **underpowered, not validated GO**. `c12_20_5/22_5` totals positive but **hedge-masked** (spot deeply negative). `c12_25_5` and all RSI 30 configs negative total with large negative spot. **Canonical RSI(21)<20 preserved as NO_GO.**

**Bottlenecks removed this session (2026-11-15T18:20Z):** C12 compute bottleneck cleared by executing full C12: prereg written before compute, 7 real-engine native grid campaigns + censuses run (anchor reused), dependence-aware episode-block bootstrap inference produced, native C12 verdict written. Prior probe artifacts (`*_c12*rsi25_t5_probe*`) removed (not evidence).

**Remaining binding next work:** **C13 — pre-registered decision-grade follow-up on C12 lead hypothesis (`rsi_threshold 25, target_pct 9`) and power closure** on Hyperliquid-native real data (no handoff-only sessions).

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T18:20:00Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program (repo `CRASH-REBOUND-STRATEGY`).** C1–C12 are COMPLETE. Canonical `RSI(21)<20` is **NO_GO** (C11.3). **C12 is COMPLETE but `NO_DECISION_GRADE_GO`**: `c12_25_9` is the only in-sample positive-spot lead (+6,836.44 spot, +23,244.22 total, 17 trades/10 episodes/11 crash days) yet **underpowered** (episode-block bootstrap CI95 spans 0; not a validated GO). Do **not** claim GO from C12 point estimates or relitigate C1–C12/cross-venue evidence without a NEW stem and documented reason.

**PRIMARY MISSION — C13: pre-registered, decision-grade native validation attempt for the C12 lead (`rsi_threshold 25, target_pct 9`) with honest power.** A session that only edits this handoff or only reruns gates without producing C13 compute artifacts/verdict has failed.

### 0) Mandatory gate + readiness (every session, record stems/verdicts)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
```
Native inputs (fixed): cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`. **Provenance caveat (binding):** real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true`.

### 1) C13.0 — Pre-register C13 (REQUIRED before compute)
Write `research_state/hyperliquid_native_c13_prereg_<TS>Z.{json,md}`. Primary hypothesis: `rsi_threshold 25, target_pct 9` (C12 lead) vs canonical anchor on native evidence. Specify: (a) primary metrics separating **spot coin / ETH hedge / rebound-short** PnL, trade/episode/crash-day counts, DD/cost stress; (b) dependence-aware inference required for any claim — episode-block bootstrap CI **and** temporal-edge/permutation or portfolio-placebo evidence under the **matching** config (existing `run_episode_edge_okx_multiyear.py` / placebo runners hardcode canonical RSI/StrategyConfig; if using them, extend them to accept `--rsi-threshold/--target-pct`/config parity and record the change, or implement equivalent real-engine inference with fixed seed) — do **not** substitute C12 bootstrap-only inference as decision-grade; (c) explicit pass/fail/insufficient rules and power/episode targets; (d) if additional real native data (new Ironflow archive window/symbols) can be responsibly acquired/validated, pre-register ingestion+validation+re-run plan (no synthesis, provenance-labeled).

### 2) C13.1 — Execute validation/inference compute (REQUIRED)
Produce NEW-stem artifacts: real-engine campaign confirmation for lead (and anchor if needed), crash-event census, **config-matched** episode-edge/temporal permutation and portfolio placebo (or documented equivalent), and any pre-registered robustness/cost stress. Every artifact must state provenance caveat and separate spot/hedge/rebound legs. No synthetic data.

### 3) C13.2 — Native C13 verdict (REQUIRED)
Write `research_state/decision_verdict_hyperliquid_native_c13_<TS>Z.md` (and consolidated update if warranted): re-map stop/go for the lead hypothesis with dependence-aware results; state whether any claim clears pre-registered decision-grade thresholds (CI excludes 0 on relevant leg/total under adequate effective N, non-extreme placebo/permutation as applicable). **Never flip to GO from hedge-masked totals, point PnL, or underpowered results.** Preserve canonical NO_GO unless re-validated.

### 4) Close (every session)
- Re-run gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**.
- Re-timestamp this handoff with exact C13 artifact stems/verdicts; keep gate-token contract intact. No second handoff/status file.

**Definition of done (C13):** prereg + config-matched real-engine inference artifacts for lead hypothesis + `decision_verdict_hyperliquid_native_c13_<TS>Z.md`, with all three gates green and this handoff re-timestamped. **Handoff-only or gate-only sessions fail C13.**

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

## What changed this session (2026-11-15T18:20Z)

- **C12 pre-registered and executed (real Hyperliquid-native, Ironflow node-derived, CC BY 4.0, NOT venue candleSnapshot):**
  - Prereg: `research_state/hyperliquid_native_c12_prereg_20261115T180000Z.{json,md}`
  - Real-engine campaigns (NEW stems): `campaign_results_real_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.json` (+ `_metrics.csv/.json`) on fixed native cache/universe (anchor `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` reused for 20/9).
  - Censuses: `crash_event_census_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.{json,md}`.
  - Dependence-aware inference summary: `research_state/hyperliquid_native_c12_inference_20261115T180000Z.{json,md}` (episode-block bootstrap 98h, 20k resamples, seed 20261115 for spot/hedge/rebound/total per config; census alignment; anchor refs C11.3 episode-edge/placebo). Non-anchor configs: full engine permutation/placebo not rerun because existing parameterized runners hardcode canonical StrategyConfig — explicitly labeled, not decision-grade.
  - Verdict: `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` — **NO_DECISION_GRADE_GO** (lead `c12_25_9` in-sample positive spot/total but underpowered, CI spans 0; hedge-masked/negative others; canonical NO_GO preserved).
- **Cleanup:** removed prior non-evidence probe artifacts `research_state/*_c12_rsi25_t5_probe*`.
- **Gates re-run green:** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**.
- Handoff rewritten as single timestamped initial task for next session (C13). Gate-token contract preserved.

## Verified state (as of 2026-11-15T18:20Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | venv present |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| Cross-venue consolidated verdict | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Native canonical verdict (C11.3) | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE`, 0/7** | `decision_verdict_hyperliquid_native_20261115T155318Z.md` |
| **C12 prereg** | done | `hyperliquid_native_c12_prereg_20261115T180000Z.{json,md}` |
| **C12 campaigns (grid)** | 7 new + anchor reused; all real-engine | `campaign_results_real_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.json` (+ metrics) |
| **C12 censuses** | 7 configs | `crash_event_census_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.{json,md}` |
| **C12 inference** | episode-block bootstrap + census alignment (underpowered) | `hyperliquid_native_c12_inference_20261115T180000Z.{json,md}` |
| **C12 verdict** | **`NO_DECISION_GRADE_GO`** (lead in-sample, not validated) | `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` |
| API retention probe (C11.0 baseline) | 3861/6792 bars (expected external limit) | `hyperliquid_retention_probe.json` |

## Bottlenecks (current)

1. **C13 decision-grade validation — NOT YET RUN (PRIMARY).** C12 lead `rsi 25 / target 9` needs config-matched dependence-aware inference (temporal permutation/placebo under matching config) and/or additional real native data for power; current evidence **underpowered** (CI spans 0). Do not stop at handoff/gates.
2. **Inference tooling gap for non-canonical configs.** Existing episode-edge/placebo parameterized runners hardcode canonical `StrategyConfig`/RSI assumptions in places; C13 must extend or provide equivalent real-engine config-matched inference (no synthetic shortcuts).
3. **Statistical power — structural.** 283d native window; C12 lead shows 17 trades / 10 episodes / 11 crash days with wide CIs.
4. **Canonical/native economics context.** Canonical spot alpha negative; some C12 totals hedge-masked. Separate legs in every claim.
5. **Live Hyperliquid API 1h retention — external, expected (non-blocking).** Full-window evidence comes from accepted Ironflow archive, not API.
6. **Cross-venue evidence — exhausted/CLOSED.** OKX/Binance remain `is_hyperliquid_venue_data=false`.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Cross-venue multi-year/canonical artifacts under `research_state/` (`campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**).
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, C11.3 census/episode/placebo/robustness/verdict stems, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- **C12:** `hyperliquid_native_c12_prereg_20261115T180000Z.*`, `campaign_results_real_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z*`, `crash_event_census_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.*`, `hyperliquid_native_c12_inference_20261115T180000Z.*`, `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only

# C12 completed stems (20261115T180000Z family) — see research_state/.
# C13 (next): prereg + config-matched real-engine temporal/placebo inference for rsi25/t9 + verdict.
```

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite or only gate reruns.** C13 requires prereg + compute artifacts + native C13 verdict.
- **Do not claim GO from hedge-masked totals, point PnL, in-sample C12 discovery, or underpowered results.** `c12_25_9` is hypothesis-generating, not validated.
- **Do not substitute C12 episode-bootstrap-only summary for config-matched temporal permutation/placebo decision-grade inference.**
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` for OKX/Binance.
- **Do not misrepresent native archive provenance.** Node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`; record caveat in every native artifact.
- **Do not fabricate/synthesize data.** No synthetic candles/archives/results.
- **Do not relax `volume_filter_ok` / trailing-24h ≥ $5M gate or spec-literal opt-in defaults.**
- **Do not re-run canonical campaigns/censuses/C6-T3/C7/C10/C11.3/C12 without a new artifact stem and documented reason.**
- **Do not revert RSI incremental cache, epoch-timestamp fix, placebo fork-parallel runner, or C12 grid knobs in `run_real_campaign.py`.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

(End of file)
