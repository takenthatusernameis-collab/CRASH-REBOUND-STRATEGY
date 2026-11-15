# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T20:43:39Z — C13 **COMPLETE** (200/200 draws, `UNDERPOWERED` verdict). **C1–C13 COMPLETE**. Gate `scripts/verify_c13_focus_campaign.py` → **C13 ACCEPTANCE: PASS**. Canonical **NO_GO preserved**. **Research program primary mission complete.** Next priority: **final consolidation/closeout**.
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify the edge on **Hyperliquid-native** evidence with honest dependence-aware inference. **C1–C13 are complete.** The single blocking priority C13 is done. The **next focus is final consolidation**: synthesize all campaigns (C1–C13 cross-venue + native) into a single consolidated verdict artifact and close the research program.

**Baseline (revalidated 2026-11-15T20:43Z):** branch `main`; env `/tmp/crs-venv` ready. **C1–C13 COMPLETE.** Gates (record stems/results each session): `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS — multi-year cross-venue campaign artifacts complete)**, `scripts/verify_c13_focus_campaign.py` **PASS (C13 ACCEPTANCE: PASS — config-matched native C13 artifacts complete)**.

**Verdict state (final):**
- Cross-venue consolidated: **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). `is_hyperliquid_venue_data=false` for OKX/Binance.
- Native canonical (C11.3): **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** (`research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; consolidated native `research_state/decision_verdict_consolidated_20261115T155318Z.md`). 6 trades, spot −3,968.80, hedge +8,261.31, rebound 0, total +4,292.50.
- Native C12 (2026-11-15T18:00Z stem family): **`NO_DECISION_GRADE_GO` / discovery only** (`research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`). Best in-sample: `c12_25_9` (RSI 25, target 9%) total +23,244.22 (spot +6,836.44, hedge +4,762.24, rebound +11,904.32; 17 trades / 10 episodes / 11 crash days) but episode-block bootstrap CI95 spans 0 (spot [−26,795, +36,129], total [−36,650, +74,463], P(total>0)=0.770) — **underpowered, not validated GO**. `c12_20_5/22_5` totals positive but **hedge-masked** (spot deeply negative). `c12_25_5` and all RSI 30 configs negative total with large negative spot. **Canonical RSI(21)<20 preserved as NO_GO.**
- **Native C13 (2026-11-15T20:37Z): `UNDERPOWERED`** (`research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`). Pre-registered validation of `rsi_threshold 25, target_pct 9` with 200 episode-edge draws + 200 placebo subsets (seed 20261115, SHA-bound to C12 lead). Results: bootstrap CI95 [−22,799, +79,979] spans 0; permutation p(null≥canon)=0.085; placebo p_ge_canon=0.32; spot leg −3,968.80 (negative), total +23,244.22 hedge-masked. Effective N: 17 trades / 10 episodes / 12 crash days / 5 symbols. **No GO criterion met. Canonical NO_GO preserved.**

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-15T20:43:39Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`).** **C1–C13 COMPLETE.** Canonical `RSI(21)<20` is **NO_GO**. C12 is **discovery only** (`NO_DECISION_GRADE_GO`). **C13 is COMPLETE** (`UNDERPOWERED`). The **single blocking priority C13 is done**. Do **not** claim GO from any campaign. Do **not** relitigate C1–C13 without a NEW stem + documented reason.

### Primary mission (single focus): FINAL CONSOLIDATION — synthesize C1–C13 into one consolidated verdict and close the research program
A session is **not** successful if it only edits this handoff, only reruns gates, or only reruns past campaigns. **Done means** a new `research_state/decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` exists that:
- references **all** prior verdict stems (cross-venue, C11.3, C12, C13),
- states a single final verdict token (`NO_GO`),
- cites dependence-aware evidence from every campaign,
- separates spot / ETH hedge / rebound-short legs in the summary,
- records the structural power limitation (283d window, effective N),
- and `scripts/session_gate.py` **21/21 checks passed — DONE** (all gates green).

### 0) Mandatory readiness + gates (run every session; record outputs/stems)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS
```
Fixed native inputs: cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`. C12 lead inputs: `research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`, `research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`. C13 artifacts: `episode_edge_hyperliquid_native_c13_20261115T200200Z.json`, `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json`. **Provenance (binding):** Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true`.

### 1) FINAL.0 — Inventory all verdict stems (no new compute required)
List and verify every decision-grade verdict artifact in `research_state/`:
- Cross-venue: `decision_verdict_consolidated_20261115T122636Z.md`
- Native canonical (C11.3): `decision_verdict_hyperliquid_native_20261115T155318Z.md`, `decision_verdict_consolidated_20261115T155318Z.md`
- C12: `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`
- C13: `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`
- Supporting: C13 prereg, episode-edge, placebo artifacts (stems above)

### 2) FINAL.1 — Write final consolidated verdict (REQUIRED)
Create `research_state/decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` (and `.json` summary if useful) that:
- States **final verdict: `NO_GO`** (no GO claim from any campaign).
- References every prior verdict stem by filename (traceability).
- Synthesizes dependence-aware evidence: cross-venue (0/7), C11.3 (0/7, CI spans 0), C12 (discovery only, underpowered), C13 (pre-registered validation `UNDERPOWERED`, bootstrap CI95 [−22,799, +79,979] spans 0, permutation p=0.085, placebo p_ge=0.32).
- Separates legs: spot alpha negative in canonical and C13; hedge masks totals in C12/C13; rebound short zero in canonical.
- States effective N: 17 trades / 10 episodes / 12 crash days / 5 symbols (C13); 283-day structural window.
- Records provenance caveat: native evidence is **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**.
- Does **not** claim GO, does **not** relabel cross-venue as Hyperliquid evidence.

### 3) FINAL.2 — Close (every session)
- Re-run gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4**, `verify_next_focus_campaign.py` **PASS**, `verify_c13_focus_campaign.py` **PASS**.
- Update this handoff with the final consolidated verdict stem + timestamp; keep gate-token contract intact. **No second handoff/status file.**

### Bottlenecks to remove now (make next agents unavoidable to do final consolidation)
1. **No final consolidated verdict** → write `decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` (above).
2. **Ambiguity about "done"** → done = final verdict written + all gates green + handoff updated.
3. **Drift risk** → reference exact prior stems; do not invent new numbers.

**Definition of done (FINAL):** `decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` exists with `NO_GO` verdict + traceability to all prior stems + leg separation + power caveat, `scripts/session_gate.py` **21/21 checks passed — DONE**, other gates green, handoff re-timestamped. **Handoff-only / gate-only sessions fail FINAL.**

---

**You are the next agentic session continuing the Hyperliquid crash-rebound research program (repo `CRASH-REBOUND-STRATEGY`).** **C1–C13 COMPLETE.** Canonical `RSI(21)<20` is **NO_GO** (C11.3). **C12 is COMPLETE but `NO_DECISION_GRADE_GO`**: `c12_25_9` is the only in-sample positive-spot lead (+6,836.44 spot, +23,244.22 total, 17 trades/10 episodes/11 crash days) yet **underpowered** (episode-block bootstrap CI95 spans 0; not a validated GO). **C13 is COMPLETE (`UNDERPOWERED`)**: pre-registered validation of the C12 lead (`rsi_threshold 25, target_pct 9`) with 200/200 draws, seed 20261115, SHA-bound to C12 lead — bootstrap CI95 [−22,799, +79,979] spans 0; permutation p=0.085; placebo p_ge=0.32; spot leg −3,968.80; total +23,244.22 hedge-masked. **No GO criterion met in any campaign. Canonical NO_GO preserved.**

**PRIMARY MISSION — FINAL CONSOLIDATION: synthesize C1–C13 into one final `NO_GO` verdict and close the research program.** A session that only edits this handoff, only reruns gates, or only reruns past campaigns has failed. Your session is done only when a new `decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` exists with the requirements above and `scripts/session_gate.py` prints **21/21 checks passed — DONE**.

### 0) Mandatory gates + readiness (every session, record stems/verdicts)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS
```
Native inputs (fixed): cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json`. C12 lead artifacts: census `research_state/crash_event_census_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`, campaign `research_state/campaign_results_real_hyperliquid_native_c12_rsi25_t9_20261115T180000Z.json`. C13 artifacts: `episode_edge_hyperliquid_native_c13_20261115T200200Z.json`, `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json`. **Provenance caveat (binding):** real Hyperliquid-native, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true`.

### 1) FINAL.0 — Inventory all verdict stems (no new compute required)
List and verify every decision-grade verdict artifact in `research_state/`:
- Cross-venue: `decision_verdict_consolidated_20261115T122636Z.md`
- Native canonical (C11.3): `decision_verdict_hyperliquid_native_20261115T155318Z.md`, `decision_verdict_consolidated_20261115T155318Z.md`
- C12: `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`
- C13: `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`
- Supporting: C13 prereg `hyperliquid_native_c13_prereg_20261115T185721Z.{json,md}`, episode-edge `episode_edge_hyperliquid_native_c13_20261115T200200Z.{json,md}`, placebo `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.{json,md}`

### 2) FINAL.1 — Write final consolidated verdict (REQUIRED)
Create `research_state/decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` (and `.json` summary if useful) that:
- States **final verdict: `NO_GO`** (no GO claim from any campaign).
- References every prior verdict stem by filename (traceability).
- Synthesizes dependence-aware evidence: cross-venue (0/7), C11.3 (0/7, CI spans 0), C12 (discovery only, underpowered), C13 (pre-registered validation `UNDERPOWERED`, bootstrap CI95 [−22,799, +79,979] spans 0, permutation p=0.085, placebo p_ge=0.32).
- Separates legs: spot alpha negative in canonical and C13; hedge masks totals in C12/C13; rebound short zero in canonical.
- States effective N: 17 trades / 10 episodes / 12 crash days / 5 symbols (C13); 283-day structural window.
- Records provenance caveat: native evidence is **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**.
- Does **not** claim GO, does **not** relabel cross-venue as Hyperliquid evidence.

### 3) FINAL.2 — Close (every session)
- Re-run gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4**, `verify_next_focus_campaign.py` **PASS**, `verify_c13_focus_campaign.py` **PASS**.
- Re-timestamp this handoff with the final consolidated verdict stem + timestamp; keep the gate-token contract intact. No second handoff/status file.

**Definition of done (FINAL):** `decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` exists with `NO_GO` verdict + traceability to all prior stems + leg separation + power caveat, `scripts/session_gate.py` **21/21 checks passed — DONE**, other gates green, handoff re-timestamped. **Handoff-only, gate-only sessions fail FINAL.**

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

## What changed this session (2026-11-15T20:43Z)

- **C13 already COMPLETE** (from prior session 2026-11-15T20:37Z): heavy compute executed (200/200 draws), native verdict `UNDERPOWERED` written, C13 gate **PASS**.
- **This session**: Handoff updated to reflect C1–C13 COMPLETE; primary mission shifted from C13 execution to **FINAL CONSOLIDATION** (synthesize all campaigns into one `NO_GO` verdict and close research program).
- **Gate status:** `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**, `verify_c13_focus_campaign.py` **PASS**.

## Verified state (as of 2026-11-15T20:43Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | venv present |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| **C13 acceptance gate** | **PASS** | `scripts/verify_c13_focus_campaign.py` |
| C13 prereg | **PASS** (staged 2026-11-15T18:57:21Z) | `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.json` |
| C13 episode-edge | **200 draws, seed 20261115, config-matched** | `episode_edge_hyperliquid_native_c13_20261115T200200Z.json` |
| C13 placebo | **200 runs, seed 20261115, config-matched** | `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json` |
| C13 native verdict | **`UNDERPOWERED`** | `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md` |
| Cross-venue consolidated verdict | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Native canonical verdict (C11.3) | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE`, 0/7** | `decision_verdict_hyperliquid_native_20261115T155318Z.md` |
| C12 verdict | **`NO_DECISION_GRADE_GO`** (lead in-sample, not validated) | `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` |
| Episode-edge runner | config-matched (`--rsi-threshold/--target-pct`), smoke-validated | prior session |
| Placebo runner | config-matched + parameterized paths, smoke-validated | prior session |
| API retention probe (C11.0 baseline) | 3861/6792 bars (expected external limit) | `hyperliquid_retention_probe.json` |

## Bottlenecks (current)

1. **No final consolidated verdict** → write `decision_verdict_CONSOLIDATED_FINAL_<TS>Z.md` (see FINAL.1 above).
2. **Statistical power — structural.** 283d native window; C12/C13 lead shows 17 trades / 10 episodes / 12 crash days with wide CIs. C13 honestly labeled `UNDERPOWERED` (bootstrap CI95 spans 0, permutation p=0.085, placebo p_ge=0.32). Note: the episode-edge artifact reports **12 distinct signal-event days** (all crash bars), while C12 inference reports **11 trade crash days**; this is a counting-unit difference, not a contradiction.
3. **Canonical/native economics context.** Canonical spot alpha negative; some C12 totals hedge-masked. Separate legs in every claim.
4. **Live Hyperliquid API 1h retention — external, expected (non-blocking).** Full-window evidence comes from the accepted Ironflow archive, not the API.
5. **Cross-venue evidence — exhausted/CLOSED.** OKX/Binance remain `is_hyperliquid_venue_data=false`. Do not re-acquire or re-run.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Cross-venue multi-year/canonical artifacts under `research_state/` (`campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**).
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, C11.3 census/episode/placebo/robustness/verdict stems, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- **C12:** `hyperliquid_native_c12_prereg_20261115T180000Z.*`, `campaign_results_real_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z*`, `crash_event_census_hyperliquid_native_c12_rsi{20,22,25,30}_t{5,9}_20261115T180000Z.*`, `hyperliquid_native_c12_inference_20261115T180000Z.*`, `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`.
- **C13 (this session):** `hyperliquid_native_c13_prereg_20261115T185721Z.{json,md}`, `episode_edge_hyperliquid_native_c13_20261115T200200Z.{json,md}`, `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.{json,md}`, `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md` — do not overwrite without new stem and documented reason.
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