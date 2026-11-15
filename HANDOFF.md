# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T19:56:20Z — C13 prereg remains staged; C13 compute **not yet run**; canonical remains **NO_GO**. The prereg (`research_state/hyperliquid_native_c13_prereg_20261115T185721Z.{json,md}`) and hardened gate (`verify_c13_focus_campaign.py` requiring ≥100 draws, seed/SHA binding, max-compute selection, verdict traceability) are in place. `scripts/build_c13_prereg.py` exists for regeneration if needed (use --force with documented reason).
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify the edge on **Hyperliquid-native** evidence with honest dependence-aware inference. Canonical and C12 discovery are complete; the remaining priority is **C13**, the pre-registered validation of the only positive-spot lead (`rsi_threshold 25, target_pct 9`).

**Baseline (revalidated 2026-11-15T18:57Z):** branch `main`; env `/tmp/crs-venv` ready. **C1–C12 COMPLETE.** Gates: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**, `scripts/verify_c13_focus_campaign.py` **FAIL (expected — C13 compute/verdict not yet run; prereg requirement now PASSES)**.

**Verdict state:**
- Cross-venue consolidated: **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). `is_hyperliquid_venue_data=false` for OKX/Binance.
- Native canonical (C11.3): **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** (`research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; consolidated native `research_state/decision_verdict_consolidated_20261115T155318Z.md`). 6 trades, spot −3,968.80, hedge +8,261.31, rebound 0, total +4,292.50.
- **Native C12 (2026-11-15T18:00Z stem family): `NO_DECISION_GRADE_GO` / discovery only** (`research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`). Best in-sample: `c12_25_9` (RSI 25, target 9%) total +23,244.22 (spot +6,836.44, hedge +4,762.24, rebound +11,904.32; 17 trades / 10 episodes / 11 crash days) but episode-block bootstrap CI95 spans 0 (spot [−26,795, +36,129], total [−36,650, +74,463], P(total>0)=0.770) — **underpowered, not validated GO**. `c12_20_5/22_5` totals positive but **hedge-masked** (spot deeply negative). `c12_25_5` and all RSI 30 configs negative total with large negative spot. **Canonical RSI(21)<20 preserved as NO_GO.**

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-15T19:54:32Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program (repo `CRASH-REBOUND-STRATEGY`).** C1–C12 are COMPLETE. Canonical `RSI(21)<20` is **NO_GO** (C11.3). **C12 is COMPLETE but `NO_DECISION_GRADE_GO`**: `c12_25_9` is the only in-sample positive-spot lead (+6,836.44 spot, +23,244.22 total, 17 trades/10 episodes/11 crash days) yet **underpowered** (episode-block bootstrap CI95 spans 0; not a validated GO). Do **not** claim GO from C12 point estimates or relitigate C1–C12/cross-venue evidence without a NEW stem and documented reason. The C13 tooling and prereg are **already staged**; do not redo them.

**PRIMARY MISSION — C13: execute the pre-registered, decision-grade native validation of the C12 lead (`rsi_threshold 25, target_pct 9`) with honest power.** A session that only edits this handoff, only reruns gates, or only reruns canonical campaigns has failed. Your session is done only when `scripts/verify_c13_focus_campaign.py` prints **C13 ACCEPTANCE: PASS**.

### 0) Mandatory gates + readiness (every session, record stems/verdicts)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # currently FAIL — your definition of done
```
Native inputs (fixed): cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`. C12 lead artifacts: census `research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`, campaign `research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`. **Provenance caveat (binding):** real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true`.

### 1) C13.0 — Prereg (ALREADY STAGED; verify, do not silently rewrite)
`research_state/hyperliquid_native_c13_prereg_20261115T185721Z.json` + `.md` are pre-registered and gate-valid (`prereg validation: PASS`). They fix:
- lead hypothesis `rsi_threshold 25`, `target_pct 9`;
- seed `20261115`; minimum heavy-compute floor `100` permutation draws and `100` placebo subsets; planned `200`/`200`;
- explicit **GO / NO_GO / UNDERPOWERED** decision rules and power targets (10 trades / 5 episodes / 5 crash days minimum for GO; 283d window is structurally underpowered);
- provenance caveat (node-derived, NOT candleSnapshot), `fabricated_data=false`, `synthetic_data=false`;
- exact compute commands.

If you disagree with the plan, regenerate **before any compute** and record why:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_c13_prereg.py --force
```
Do **not** edit the prereg after C13 results exist. A changed plan requires a new stem and a documented reason.

### 2) C13.1 — Execute validation/inference compute (REQUIRED; heavy work)
Use NEW timestamped stems (do not overwrite the prereg or canonical artifacts). The exact commands are in the prereg markdown; canonical form:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --draws 200 --seed 20261115 --rsi-threshold 25 --target-pct 9 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --campaign research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \
  --out episode_edge_hyperliquid_native_c13_<TS>Z

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py \
  --draws 200 --seed 20261115 --rsi-threshold 25 --target-pct 9 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --campaign research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json \
  --venue-label 'Hyperliquid (Ironflow node-derived, native)' \
  --out placebo_portfolio_hyperliquid_native_c13_<TS>Z
```
Both runners hard-verify exact canonical replay (17 trades / +23,244.224 for the lead config) and record `config.config_matched=true` with the node-derived caveat, plus `seed` and campaign/census SHA256. Add a pre-registered robustness/cost-stress battery on the lead config if the prereg says so. Every artifact must separate spot / ETH hedge / rebound-short legs. No synthetic data; no canonical overwrites.

### 3) C13.2 — Native C13 verdict (REQUIRED)
Write `research_state/decision_verdict_hyperliquid_native_c13_<TS>Z.md` (and consolidated update if warranted). The gate requires the verdict to:
- state the lead config (RSI **25** / target **9**);
- state a verdict token (`GO` / `NO_GO` / `NO_DECISION_GRADE_GO` / `UNDERPOWERED` / `FRAGILE`);
- reference dependence-aware evidence (bootstrap / permutation / placebo / CI95) and the effective sample (trades / episodes);
- reference the **prereg filename** and the **episode-edge + placebo artifact filenames** (traceability);
- not claim GO while also stating underpowered / spans-0 / not-validated (contradiction check).

Re-map stop/go for the lead hypothesis with dependence-aware results; state whether any claim clears the pre-registered decision-grade thresholds (CI excludes 0 on the relevant leg/total under adequate effective N, non-extreme placebo/permutation as applicable). **Never flip to GO from hedge-masked totals, point PnL, or underpowered results.** Preserve canonical NO_GO unless re-validated.

### 4) Close (every session)
- Re-run gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**, and `verify_c13_focus_campaign.py` **C13 ACCEPTANCE: PASS**.
- Re-timestamp this handoff with the exact C13 artifact stems/verdict; keep the gate-token contract intact. No second handoff/status file.

**Definition of done (C13):** prereg (staged) + config-matched episode-edge + config-matched placebo (each **≥100 draws/subsets**, seed/SHA-bound) + `decision_verdict_hyperliquid_native_c13_<TS>Z.md`, with `scripts/verify_c13_focus_campaign.py` printing **C13 ACCEPTANCE: PASS**, all other gates green, and this handoff re-timestamped. **Handoff-only, gate-only, or canonical-rerun-only sessions fail C13.**

---

## Gate-token contract (DO NOT remove — machine-checked)

The handoff is parsed by `scripts/session_gate.py` (`check_handoff`), `scripts/verify_next_focus_campaign.py`, and `scripts/verify_c13_focus_campaign.py`. To keep gates green this file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `verify_c13_focus_campaign.py` (C13 acceptance gate)
- `C13` (C13 campaign token)
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## What changed this session (2026-11-15T19:54Z)

- **C13 prereg remains staged (prereg-before-compute satisfied):** `scripts/build_c13_prereg.py` wrote and validated `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.{json,md}` (`prereg validation: PASS`). It fixes lead `rsi 25 / target 9`, seed `20261115`, floor `100` draws/subsets, planned `200/200`, GO/NO_GO/UNDERPOWERED rules, power targets, provenance caveat, and exact commands.
- **C13 gate hardened against thin/avoidant runs:** `scripts/verify_c13_focus_campaign.py` now requires:
  - **≥100** episode-edge permutation draws and **≥100** placebo subsets (`MIN_DRAWS`);
  - effective sample **≥10 trades / ≥5 episodes**;
  - artifacts **seed-bound to the prereg** and **SHA-bound to the C12 lead campaign/census**;
  - selection of the **max-compute** eligible artifact (a stale thin artifact cannot shadow or substitute);
  - verdict **traceability** to the prereg and both artifact filenames, plus effective-sample and dependence-aware evidence.
  Unit-tested in an isolated temp state: 2-draw artifacts **FAIL** (`evaluated only 2 ... need >= 100`); 100-draw seed/SHA-bound artifacts **PASS**; wrong-seed artifacts are ignored.
- **C13 runners smoke-validated (artifacts deleted; NOT evidence):** episode-edge rsi25/t9 (`--draws 2`) reproduced C12 `c12_25_9` exactly — 33 signal-gate events, 10 episodes, 17 trades, +23,244.22, bootstrap CI [−22,799.52, 79,978.91], permutation p=0.0000, verdict `underpowered` (1.8s). Placebo rsi25/t9 (`--draws 2`) replayed 17 trades / +23,244.224 and evaluated 2 seeded subsets (p_ge_canon=0.50). These smoke artifacts were deleted and must not be cited.
- **Gate status:** `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**, `verify_c13_focus_campaign.py` **FAIL** with `c13_prereg_before_compute: PASS`, `c13_config_matched_inference: FAIL` (compute not run), `c13_native_verdict: FAIL` (verdict not written). This is the expected pre-C13 state.

## Verified state (as of 2026-11-15T19:54Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | venv present |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| **C13 acceptance gate** | **FAIL (expected — compute/verdict pending)** | `scripts/verify_c13_focus_campaign.py` |
| C13 prereg | **PASS** (staged 2026-11-15T18:57:21Z) | `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.json` |
| Cross-venue consolidated verdict | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Native canonical verdict (C11.3) | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE`, 0/7** | `decision_verdict_hyperliquid_native_20261115T155318Z.md` |
| C12 verdict | **`NO_DECISION_GRADE_GO`** (lead in-sample, not validated) | `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` |
| Episode-edge runner | config-matched (`--rsi-threshold/--target-pct`), smoke-validated | this session |
| Placebo runner | config-matched + parameterized paths, smoke-validated | this session |
| API retention probe (C11.0 baseline) | 3861/6792 bars (expected external limit) | `hyperliquid_retention_probe.json` |

## Bottlenecks (current)

1. **C13 decision-grade compute — NOT YET RUN (PRIMARY).** The prereg is staged and the runners are config-matched and smoke-validated. Run the two commands in C13.1, then write the verdict. Do not stop at handoff/gates; `verify_c13_focus_campaign.py` must reach PASS.
2. **Statistical power — structural.** 283d native window; C12 lead shows 17 trades / 10 episodes / 11 crash days with wide CIs. C13 must report effective N and honestly label underpowered results. Note: the episode-edge artifact reports **12 distinct signal-event days** (all crash bars), while C12 inference reports **11 trade crash days**; this is a counting-unit difference, not a contradiction.
3. **Canonical/native economics context.** Canonical spot alpha negative; some C12 totals hedge-masked. Separate legs in every claim.
4. **Live Hyperliquid API 1h retention — external, expected (non-blocking).** Full-window evidence comes from the accepted Ironflow archive, not the API.
5. **Cross-venue evidence — exhausted/CLOSED.** OKX/Binance remain `is_hyperliquid_venue_data=false`. Do not re-acquire or re-run.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Cross-venue multi-year/canonical artifacts under `research_state/` (`campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**).
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, C11.3 census/episode/placebo/robustness/verdict stems, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- **C12:** `hyperliquid_native_c12_prereg_20261115T180000Z.*`, `campaign_results_real_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z*`, `crash_event_census_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.*`, `hyperliquid_native_c12_inference_20261115T180000Z.*`, `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`.
- **C13 prereg (this session):** `hyperliquid_native_c13_prereg_20261115T185721Z.{json,md}` — do not overwrite without `--force` and a documented reason.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 gate (FAIL until C13 done)

# C13 is pre-registered. Run the two commands in:
#   research_state/hyperliquid_native_c13_prereg_20261115T185721Z.md
# then write research_state/decision_verdict_hyperliquid_native_c13_<TS>Z.md
# and re-run verify_c13_focus_campaign.py until it prints C13 ACCEPTANCE: PASS.
```

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite, only gate reruns, or only canonical campaign reruns.** C13 requires prereg + config-matched episode-edge + config-matched placebo + native C13 verdict; `verify_c13_focus_campaign.py` enforces this and is RED until then.
- **Do not run a thin C13.** The gate requires ≥100 permutation draws and ≥100 placebo subsets, seed-bound to the prereg and SHA-bound to the C12 lead campaign/census. A 2-draw smoke run is not evidence.
- **Do not claim GO from hedge-masked totals, point PnL, in-sample C12 discovery, or underpowered results.** `c12_25_9` is hypothesis-generating, not validated.
- **Do not substitute C12 episode-bootstrap-only summary for config-matched temporal permutation/placebo decision-grade inference** — the tooling exists; use it.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` for OKX/Binance.
- **Do not misrepresent native archive provenance.** Node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`; record caveat in every native artifact.
- **Do not fabricate/synthesize data.** No synthetic candles/archives/results.
- **Do not relax `volume_filter_ok` / trailing-24h ≥ $5M gate or spec-literal opt-in defaults.**
- **Do not re-run canonical campaigns/censuses/C6-T3/C7/C10/C11.3/C12 without a new artifact stem and documented reason.**
- **Do not revert RSI incremental cache, epoch-timestamp fix, placebo fork-parallel runner, C12 grid knobs in `run_real_campaign.py`, the config-matched parameterization of the episode-edge/placebo runners, or this session's C13 gate hardening/prereg builder.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `verify_c13_focus_campaign.py`, `C13`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

(End of file)