# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T12:31:13Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge on **Hyperliquid-native** data with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session, 2026-11-15T12:29Z):** branch `main`; **C1–C10 COMPLETE.** All gates green: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**. Consolidated verdict is **`NO_GO`** (0/7 stop/go criteria; edge not established/fragile; Hyperliquid-native evidence absent). **This is the single durable handoff. Do not rewrite it for its own sake — execute C11 below.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T12:31:13Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C10 are COMPLETE. All cross-venue work is finished and exhausted; the consolidated verdict is **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7 criteria). **There is no remaining cross-venue refinement that can change the verdict** — do not re-run canonical OKX/Binance campaigns, censuses, C6-T3, C7, or the C10 battery without a new stem and a documented reason.

**Your job is to run CAMPAIGN C11: the Hyperliquid-native decision campaign — the only path to a `GO`.** Do it with real computation and no fabricated evidence. Work strictly in this order; do not skip steps.

### C11.0 — Mandatory gate + external-block probe (read-only, every session)
Run and record stems/verdicts (these are binding; a session that does not run them has not started):
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py
```
Current baseline: probe **2026-11-15T12:31:13Z** → 3,863/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`; intake **2026-11-15T12:31:36Z** → `REJECT_NOT_EVIDENCE` (placeholder parquet is NOT evidence; BTC/ETH flat series all bars identical). Re-run and record the new stem; if it still reports blocked/REJECT, go to C11.2.

### C11.1 — Acquisition attempt (heavy, real; only if a real archive is plausibly obtainable)
Attempt a genuine Hyperliquid-native archive acquisition with the existing tooling, then validate intake:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py   # backward pagination / earliest-anchor stitching
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/acquire_exchange_archive.py     # operator-style archive acquisition
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py
```
- If intake returns **`ACCEPT_AS_EVIDENCE_CANDIDATE`** → go to C11.3 (full native battery) with NEW stems.
- If it returns `REJECT_NOT_EVIDENCE`/blocked again → the blocker is confirmed external; go to C11.2. Do **not** fabricate, interpolate, or relabel the placeholder parquet.

### C11.2 — Pre-registered Hyperliquid-native power & decision protocol (heavy, real; default path while blocked)
Build `scripts/build_hyperliquid_native_power_prereg.py` and produce `research_state/hyperliquid_native_power_prereg_<TS>Z.{json,md}` (new stem). It must, with real Monte-Carlo computation (no hand-waving):
1. Use the retained Hyperliquid partial chain's observed crash-episode rate and the cross-venue effect-size priors (OKX/Binance episode-block distributions) as inputs.
2. Run an episode-block-bootstrap **power grid** across candidate episode counts N to find the N that gives **≥80% power at α=0.05** for the C6-T3 episode-edge test, and the minimum detectable effect (MDE).
3. Pre-register the **GO/NO-GO decision rule** for the eventual Hyperliquid-native run (which of the 7 criteria must pass, thresholds, dependence-aware inference method, placebo/permutation plan).
4. State explicitly that this is a design/power artifact (`is_hyperliquid_venue_data=false`, `performance_evidence=false`) and NOT a verdict.
This is the anti-avoidance artifact: it makes the eventual Hyperliquid-native campaign pre-specified and unfakeable.

### C11.3 — Full Hyperliquid-native end-to-end battery (heavy; ONLY if C11.1 accepted an archive)
With NEW stems, run in order and write `research_state/decision_verdict_hyperliquid_native_<TS>Z.md`:
1. Campaign: `scripts/run_real_campaign.py` (or `scripts/run_hyperliquid_exploratory_next_open.py`) on the accepted native archive → `campaign_results_hyperliquid_native_<TS>Z.{json,md}`.
2. C6-T3 episode edge + placebo on native data (reuse `scripts/run_episode_edge_okx_multiyear.py` / `scripts/run_portfolio_placebo_okx_multiyear.py` with the native cache/universe/census/campaign) → `episode_edge_hyperliquid_native_<TS>Z.{json,md}`, `placebo_portfolio_hyperliquid_native_<TS>Z.{json,md}`.
3. C7 robustness battery on native data (`scripts/run_multiyear_robustness_battery.py --phases A B`) → `multiyear_robustness_battery_hyperliquid_native_<TS>Z.{json,md}`.
4. Re-map all 7 stop/go criteria on **Hyperliquid-native** evidence and write the native verdict; then add a new consolidated stem `decision_verdict_consolidated_<TS>Z.md` that cites the C8/C10 stems and this native stem. Flip to `GO` **only if** the native evidence clears the pre-registered rule in C11.2.

### C11 close (every session)
- Re-run all three gates: `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4, `verify_next_focus_campaign.py` PASS.
- Re-timestamp this handoff with the exact C11 artifact stems + verdicts and the gate results. Keep the gate-token contract intact.

**Binding constraints (unchanged):** cross-venue evidence is NOT Hyperliquid evidence (`is_hyperliquid_venue_data=false`); no synthetic/fabricated data; no new handoff/status files (this file only); no unnecessary re-runs of canonical OKX/Binance multi-year campaigns/censuses/C6-T3/C7 without a new stem+reason; do not relax the $5M volume floor or spec-literal opt-in default; do not quote the PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.

**Definition of done (C11):** either (a) a native battery + `decision_verdict_hyperliquid_native_<TS>Z.md` exists and the 7 criteria are re-mapped on Hyperliquid-native data, or (b) `hyperliquid_native_power_prereg_<TS>Z.{json,md}` exists with a real ≥80%-power N and a pre-registered GO/NO-GO rule — plus all three gates green and this handoff re-timestamped. **A session that only edits this handoff or only re-runs cross-venue work has failed C11.**

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

## What changed this session (C11 gate-run — 2026-11-15T12:31:13Z)

- **Mandatory gates executed and green:** `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4, `verify_next_focus_campaign.py` PASS.
- **Hyperliquid readiness re-probed (C11.0):** new retention probe stem `hyperliquid_retention_probe.json` @ **2026-11-15T12:31:13Z** (3,863/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` — KPEPE error); new intake validation stem `archive_intake_validation_20261115T123136Z.{json,md}` → **`REJECT_NOT_EVIDENCE`** (placeholder parquet; BTC/ETH flat series all bars identical).
- **No cross-venue re-runs** — C10 remains complete and exhausted; the `NO_GO` verdict (0/7) stands per `decision_verdict_consolidated_20261115T122636Z.md`.
- **Handoff re-timestamped** to 2026-11-15T12:31:13Z with C11.0 executed and CAMPAIGN C11 defined as the next focus (Hyperliquid-native decision campaign). All gate tokens intact.
- **C11 is the mandated next campaign** (see INITIAL TASK MESSAGE): native acquisition (C11.1) → native end-to-end battery (C11.3) if accepted, else pre-registered native power/decision protocol (C11.2).

### Prior bottleneck removals still in force
- Cross-venue multi-year OKX/Binance archives/caches/campaigns/censuses/C6-T3/C7 on disk; OKX + Binance placebo done.
- RSI incremental cache (O(1)/bar) and epoch timestamp parsing fix — do not revert.
- Placebo runner now fork-parallel (`--jobs`, default 4) — ~2.1h for 200 draws vs ~5h serial; keep.
- Hyperliquid public API retention ~3,869/6,792 bars (decaying tail) — full 283d native archive not on disk; external/operator-only.
- Handoff duplication removed: this file is the only durable handoff.
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.
- Gate citation drift fixed (C9): `C6-T1` token and Phase O timestamp `2026-11-13T23:38:47Z` intact.

---

## Verified state (as of 2026-11-15T12:29Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C6 campaign OKX/Binance | 42/42 trades; +18,220.86/+21,994.06; `is_hyperliquid_venue_data=false` | `campaign_results_real_okx_multiyear.json`, `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | CI [−50,660.49,+99,295.03] P(>0)=0.6649; perm p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C6-T3 episode edge Binance | CI [−57,363.40,+122,139.16] P(>0)=0.65425; perm p=0.1850; **`underpowered`** | `episode_edge_binance_um_multiyear.{json,md}` |
| C7 robustness OKX / Binance | **`FRAGILE_NOT_DECISION_GRADE`** (both) | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}` |
| **C10.1 paired agreement** | **`DIRECTION_REPLICATES_MAJORITY`** (32 pairs, same-sign 1.0, mean diff −454.03, CI [−1057.09,+11.00]) | `cross_venue_paired_agreement_20261115T064738Z.{json,md}` |
| **C10.2 Binance placebo** | **`underpowered`** (200 draws, p(placebo≥canon)=0.4150, P(>0)=0.9350, canon +21,994.06) | `placebo_portfolio_binance_um_multiyear.{json,md}` (12:26:21Z) |
| **C10.3 pooled meta** | **`underpowered`** (38 eps, +40,214.92, CI [−69,065.03,+168,946.87], P(>0)=0.74095, perm p=0.26955) | `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}` |
| **Consolidated verdict (C10 final)** | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` (cites `20261115T063642Z.md`, `20261115T064738Z.md`) |
| Hyperliquid readiness | 3,863/6,792 bars; `FULL_283D_BLOCKED_BY_API_RETENTION`; intake `REJECT_NOT_EVIDENCE` | `hyperliquid_retention_probe.json` (12:31:13Z), `archive_intake_validation_20261115T123136Z.{json,md}` (12:31:36Z) |

---

## Bottlenecks (current)

1. **Hyperliquid-native archive — EXTERNAL, NOT agent-removable.** Public API serves ~3,869/6,792 bars; no 283d native archive here. C11.1/C11.2 handle it: attempt acquisition, otherwise pre-register the native power/decision protocol.
2. **Cross-venue evidence exhausted — CLOSED.** C10 complete; further cross-venue work cannot change the verdict (do not re-run).
3. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
4. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
5. **Retention decay / wasted re-fetch — REMOVED.** Do not re-fetch a degraded chain.
6. **Placebo serial slowness — REMOVED.** Fork-parallel `--jobs`; do not revert.
7. **Structural 0-trade funnel (canonical Hyperliquid path) — RESOLVED as known property.**

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Multi-year archives/caches/universes/campaigns/censuses (OKX, Binance UM, `is_hyperliquid_venue_data=false`) under `research_state/archives/`, `research_state/cache/`, `universe_*_multiyear_verified.json`, `campaign_results_real_{okx,binance_um}_multiyear.*`, `crash_event_census_real_{okx,binance_um}_multiyear.*`.
- C6-T3/C7: `episode_edge_{okx,binance_um}_multiyear.{json,md}`, `placebo_portfolio_okx_multiyear.{json,md}`, `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_grid_20261115T013200Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}`.
- C10: `cross_venue_paired_agreement_20261115T064738Z.{json,md}`, `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`, `placebo_portfolio_binance_um_multiyear.{json,md}` (12:26:21Z), `decision_verdict_consolidated_20261115T122636Z.md`, scripts `scripts/cross_venue_paired_agreement.py`, `scripts/pooled_episode_meta_okx_binance.py`, `scripts/run_portfolio_placebo_binance_um_multiyear.py`.
- Canonical verdicts: C8 `decision_verdict_consolidated_20261115T063642Z.md` (**`NO_GO`**), C10 final `decision_verdict_consolidated_20261115T122636Z.md` (**`NO_GO`**).
- Canonical OKX 283d: `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh

# Gates (all must be green)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS

# Hyperliquid readiness (mandatory, read-only)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py

# C10 completed artifacts (do not rerun)
# C10.1: research_state/cross_venue_paired_agreement_20261115T064738Z.{json,md}
# C10.2: research_state/placebo_portfolio_binance_um_multiyear.{json,md}
# C10.3: research_state/pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}

# C11 (next focus): see INITIAL TASK MESSAGE. Default (blocked) path:
#   build scripts/build_hyperliquid_native_power_prereg.py ->
#   research_state/hyperliquid_native_power_prereg_<TS>Z.{json,md}
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite or only cross-venue re-runs.** C11 requires a real native artifact (C11.2 or C11.3).
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache, the epoch-timestamp parser fix, or the placebo fork-parallel runner.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove the gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 `NO_GO`** (0/7 stop/go). **C9 external-block confirmed.** **C10 COMPLETE:** C10.1 `DIRECTION_REPLICATES_MAJORITY`; C10.2 `underpowered` (p(placebo≥canon)=0.4150); C10.3 `underpowered`; C10 final consolidated `decision_verdict_consolidated_20261115T122636Z.md` (**`NO_GO`**, 0/7). **Next: C11 Hyperliquid-native decision campaign** — native acquisition (C11.1) → native end-to-end battery (C11.3) if accepted, else pre-registered native power/decision protocol (C11.2). Hyperliquid-native validation remains blocked on an operator archive and is the only path to a potential `GO`.

(End of file)