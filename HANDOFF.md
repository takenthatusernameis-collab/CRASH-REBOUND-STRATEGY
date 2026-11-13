# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T21:52:10Z
**Supersedes:** 2026-11-13T20:55:06Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `295efeb` (working tree carries this session's edits and new artifacts; not committed). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T21:52:10Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** convert the canonical crash-rebound evidence into a decision-grade readout. The OKX evidence remains **`underpowered` / not decision-grade**: the exact full-portfolio placebo places the canonical +9.16% result at the **45th percentile** of all 165 gate-preserving admission subsets (`P(placebo >= canonical)=0.5515`). **Do not declare validated. Do not allocate capital.**
>
> **WHAT CHANGED THIS SESSION (bottlenecks removed):**
> - `/tmp/crs-venv` was absent; it is now bootstrapped. The next session must not repeat the dependency install.
> - The stale handoff claimed Phase N robustness stress still had to be created. It already exists and is committed: `research_state/robustness_stress_okx_full.{json,md}`. The handoff now records it as complete.
> - The gate did not check Phase N. It now does; the gate is **13/13** and fails closed on missing/stub Phase N, Hyperliquid status, or partial-campaign artifacts.
> - Hyperliquid-native data was previously only a plan. This session probed the public API, acquired the **maximum available real Hyperliquid window**, ran a **NOT_EVIDENCE partial campaign**, and recorded a crash census. The full 283-day window is **blocked by API retention**, not by missing effort.
> - The old "≥100 trades" GO criterion is replaced with the Phase N power-based target (≥10 trades / ≥8 symbols minimum; ≥23 / ≥17 for 80% power). The old criterion was unattainable for a rare-event strategy and would have caused an infinite "not enough data" block.
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M vol gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.69**. Cross-venue OKX, **NOT** Hyperliquid performance evidence.
> - **Exact full-portfolio placebo (165/165 subsets, real engine, gates/sizing/cap/occupancy preserved):** mean **8746.21**, median **9287.25**, p05 **5807.36**, p95 **11360.11**, min **3988.13**, max **11795.92**. Canonical 9159.69 is at the **45.45th percentile**; `P(placebo >= canonical)=0.5515`. **The canonical result is typical of a random 8-of-11 gate-passing admission subset — no admission/cap edge.**
> - Phase N robustness stress: LOO 5/5 positive (min 3495.11, max 10796.53), LOTO 8/8 positive (min 7485.96, max 13154.73), HHI 0.2517 / effective symbols 3.97. Power projection: first bootstrap CI > 0 at **10 trades / 8 symbols**; 80% power at **23 trades / 17 symbols**. Verdict **`underpowered`**.
> - **Full Hyperliquid 283d window: BLOCKED.** Public `candleSnapshot` returned **3,900** of 6,792 hourly BTC bars, starting only **2026-04-19T12:00:00Z**; 2,892 early bars are not served. Full-window evidence requires an operator-supplied verified Hyperliquid-native archive.
> - **Hyperliquid partial 163d window: RUN, NOT EVIDENCE.** Real non-synthetic API data, 12 complete symbols (ADA, ALGO, ARB, ATOM, AVAX, BTC, ETH, LTC, NEAR, OP, SOL, TIA), 3,900 bars each; campaign **0 trades / 0 PnL**; census **8 RSI(21)<20 events / 46,800 bars / 0 confirmed signals**. `performance_evidence=false`.
> - Hyperliquid-native campaign **`FULL_RUN=NOT_RUN` / `PARTIAL_RUN=NOT_EVIDENCE`**. `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py   # must print "13/13 checks passed — DONE"
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
> # EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
> # EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|run_next_campaign|run_portfolio_placebo|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **VERIFIED BASELINE (2026-11-13T21:52:10Z):** gate **13/13**; `/tmp/crs-venv` present; 4 cores; no sweeps/locks/processes; canonical hash unchanged; Phase N + Hyperliquid partial artifacts present. Working tree has session edits and new artifacts (not committed). **A green gate is evidence-chain completeness, NOT permission to stop.**
>
> **BOTTLENECK STATUS (2026-11-13T21:52:10Z): NONE KNOWN.** No running processes, no `.sensitivity_sweep.lock`, no 527s path in the next campaign, no 600s-timeout trap, venv present. The heavy remaining work is **full Hyperliquid 283d acquisition + canonical campaign** (primary; externally blocked) and, if that is blocked, **extend the Hyperliquid partial cross-sectional campaign / census** (fallback; achievable). Both must produce artifacts, not plans.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
> 1. **Full Hyperliquid-native acquisition + canonical campaign (PRIMARY):** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` runbook. Obtain a user/operator-supplied verified Hyperliquid-native archive for `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol) with source/extraction sidecar. Verify provenance and non-flat data, then run `scripts/run_real_campaign.py` on the full window and the exact full-portfolio placebo adapted to the Hyperliquid cache/config. Produce `research_state/campaign_results_real_hyperliquid_full*.json` and `research_state/placebo_portfolio_hyperliquid_full.{json,md}`. If acquisition fails, record the exact API/provenance failure in `research_state/hyperliquid_acquisition_status.json` and **do not substitute the placeholder**.
> 2. **Fallback heavy work (only if the full archive is blocked):** extend the Hyperliquid partial acquisition beyond the 12 complete symbols to every symbol the public API serves over `2026-04-19T12:00Z..2026-09-28T23:00Z`; rerun the NOT_EVIDENCE partial campaign; rerun the cross-sectional crash census; update `research_state/hyperliquid_acquisition_status.json` with the new symbol/bar counts and the exact remaining block. This is real data work, not planning.
> 3. **Decision memo update:** update `research_state/decision_memo_okx_full.md` with the Hyperliquid full result (or the documented data block) and the Phase N power target. Keep the verdict `underpowered` until every GO criterion is met.
> 4. **Do not regress:** keep 13/13 green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax the $5M gate; never present the per-event null as a portfolio test; never use the old 527s path or 10,000-sim theater (the exact 165-subset enumeration is stronger).
>
> **ANTI-AVOIDANCE:** the next turn must execute step 1 or step 2 and produce a real artifact. No planning-only turn; no validation claims (remains `underpowered` until Hyperliquid GO criteria are met); no Hyperliquid parity claims; no per-event-null-as-portfolio-test; no second handoff/status file; no "data unavailable" without the exact probe counts and the partial artifact.

---

## 0. Verified state (2026-11-13T21:52:10Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `295efeb`, `main`; session edits/new artifacts in tree (not committed). | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present (bootstrapped this session); 4 cores. | `test -x`, `nproc` |
| Done-gate | **13/13 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). sha256 `57973b0c…2f9b8`. | §1 |
| Cost calibration | canonical memoized replay **~0.25 s**; exact 165-subset placebo **42 s**; old full sim ~527 s. | measured prior session |
| Phase J2/K/L | Complete, unchanged. | artifacts |
| Phase M | Exact full-portfolio placebo + decision memo **complete**. | §5 |
| Phase N | Robustness stress / power analysis **complete**. | §5 |
| Phase J3 | Full Hyperliquid **BLOCKED** (API 3,900/6,792 bars); partial Hyperliquid **NOT_EVIDENCE run complete**. | §5 |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (sha `53ad860b…`).
- Universe: `research_state/universe_okx_full_verified.json` (sha `14c8066e…`, 54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` (sha `57973b0c…`), metrics (sha `3f95d30e…`). **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- J1 census: `crash_event_census_real_okx_full.{json,md}` — 342→187→39→89→11→8, 0 unexplained.
- J2 `sensitivity_sweep_real_okx_full.*`, K `interaction_sweep_real_okx_full.*`, L `robustness_real_okx_full.*` (**`underpowered`**).

## 2. Commands executed this session (recorded)

- `test -x /tmp/crs-venv/bin/python` → absent; `bash scripts/bootstrap_env.sh` → venv ready.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **13/13 — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py` → **runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545** (42 s).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py` → verdict **underpowered**, LOO=5, LOTO=8, evaluable_blocks=3.
- Hyperliquid API probe (BTC, full 283d request) → **3,900** bars, first `2026-04-19T12:00:00Z`, last `2026-09-28T23:00:00Z`; early 2,892 bars unavailable.
- Hyperliquid partial acquisition (24 symbols, `2026-04-19T12:00Z..2026-09-28T23:00Z`) → 12 complete symbols, 12 incomplete/error; manifest `research_state/cache/hyperliquid_partial_20260419_20260928/provenance.json`.
- Hyperliquid partial campaign (`--allow-partial-not-evidence`) → **0 trades / 0 PnL**, 12 symbols, `performance_evidence=false`.
- Hyperliquid partial crash census → **12 symbols / 46,800 bars / 8 RSI crashes / 0 confirmed signals**.
- Extended `scripts/session_gate.py` with `phase_n_robustness_stress`, `phase_j3_hyperliquid_status`, `phase_j3_hyperliquid_partial_campaign`.
- Updated `research_state/decision_memo_okx_full.md` with Phase N, Hyperliquid status, and power-based GO criteria.
- Updated `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` with the current API probe and partial-run blocker evidence.
- Added `tests/test_session_gate_hyperliquid_status_20261113.py`; targeted gate/provenance/robustness tests pass (**35 + 14**).

## 3. Reproduction recipe (canonical + exact placebo + Phase N)

```bash
# Canonical (exact; ~0.25s with memo, ~527s without)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545

# Phase N exact robustness stress
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
# EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py
# EXPECT: 12 symbols, 46800 bars, 8 RSI crashes, 0 confirmed signals

# Hyperliquid partial (NOT_EVIDENCE; requires the cached partial manifest)
# The bare symbol list is intentional: derive_verified_universe.py refuses the
# incomplete partial manifest by design; that is not a new blocker.
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py \
  --manifest research_state/cache/hyperliquid_partial_20260419_20260928/provenance.json \
  --cache-dir research_state/cache/hyperliquid_partial_20260419_20260928 \
  --universe-file research_state/universe_hyperliquid_partial_20260419_20260928.json \
  --output-prefix campaign_results_real_hyperliquid_partial_20260419_20260928 \
  --allow-partial-not-evidence \
  --window-start 2026-04-19T12:00:00Z --window-end 2026-09-28T23:00:00Z
# EXPECT: 0 trades, total_pnl=0.0, performance_evidence=false
```

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged from prior handoff. J3 full Hyperliquid-native **BLOCKED by API retention** (3,900/6,792 bars; operator archive required). Phase M (exact full-portfolio placebo + decision memo) **complete**. Phase N (robustness stress / power analysis) **complete**. Partial Hyperliquid NOT_EVIDENCE run + crash census **complete**. Placeholder parquet never evidence.

## 5. Artifacts recorded or produced this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/robustness_stress_okx_full.json` | `9b309246d1a2ac65b37678eed1ea58e6b23e5470620e529a60492681e35b6d99` | Phase N LOO/LOTO/concentration/power/refit; verdict underpowered. |
| `research_state/robustness_stress_okx_full.md` | `b44e72fe72613bfd3656e90db08be36aa9f242998ed1f03e9210fd56349cbe51` | Human-readable Phase N summary. |
| `research_state/hyperliquid_acquisition_status.json` | `230b7f4a5d1210b19f33e2be738e50521861c668e14402432d6505182febcb84` | Full-window block + partial API probe + partial campaign/census links. |
| `research_state/campaign_results_real_hyperliquid_partial_20260419_20260928.json` | `e32d7cf34e2be295aec6e5e5627775db4db9d6a83e31d31837a8544094ffb4bc` | Partial Hyperliquid campaign; **0 trades / 0 PnL / NOT_EVIDENCE**. |
| `research_state/hyperliquid_partial_crash_census_20260419_20260928.json` | `8b0f9d9e5421ed142442c1ab64b44441796cfcf330e4e5f9da900d6fbda77c14` | 12 symbols / 46,800 bars / 8 RSI crashes / 0 confirmed signals. |
| `research_state/cache/hyperliquid_partial_20260419_20260928/provenance.json` | `2da30957fa162361510a26b7748eeb6796fd9642e4fe5e60cac415eb0c553be7` | Real API provenance; 12 complete, 12 incomplete/error. |
| `research_state/decision_memo_okx_full.md` | `f0213fc7e15c23ea72c55f2eae9691b499ece7ec46358e914cc2b1e722d095a5` | Updated verdict, Phase N, Hyperliquid status, power-based GO. |
| `scripts/session_gate.py` | (modified) | 13 checks; Phase N + Hyperliquid status + partial campaign fail-closed. |
| `tests/test_session_gate_hyperliquid_status_20261113.py` | (new) | Fail-closed tests for Hyperliquid status and partial-campaign gates. |
| `scripts/run_hyperliquid_partial_census.py` | (new) | Reproducible cross-sectional RSI crash census for the partial API window. |

**Key results:** exact full-portfolio placebo (165 subsets) → canonical 9159.69 at **45.45th percentile**, `P(placebo >= canonical)=0.5515`, all subsets positive (mean 8746.21, median 9287.25, p05 5807.36, p95 11360.11). Canonical is **not distinguishable** from a random 8-of-11 gate-preserving admission subset. Phase N LOO/LOTO are positive but the sample remains 8 trades / 5 symbols; power projection requires **10 trades / 8 symbols** minimum and **23 / 17** for 80% power. Hyperliquid full 283d is **blocked by API retention**; the partial 163d run has **0 trades** and **8 RSI crashes / 0 confirmed signals**. Verdict: **`underpowered` / not decision-grade.**

## 6. Next focus campaign — status

**Phase M COMPLETE:** exact full-portfolio placebo + decision memo + gate checks. **Phase N COMPLETE:** robustness stress / power analysis. **Phase J3 PARTIAL COMPLETE:** maximum API window acquired and run as NOT_EVIDENCE; crash census recorded. **Still missing / blocking decision-grade verdict:** full 283-day Hyperliquid-native data (operator archive) + canonical campaign + full-portfolio placebo. Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX or partial Hyperliquid as full Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000-sim theater; the exact 165-subset enumeration is the standard. Do not use the old 527s path for placebo work.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **`underpowered`**; 13/13 = evidence-chain completeness, not profitability.
- Do not present the per-event null as a portfolio test.
- Do not cite the partial Hyperliquid run as performance evidence.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **13/13 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or a documented operator-data block with exact probe counts) + full-portfolio placebo + updated decision memo with stop/go criteria and the power-based sample-size target. **This file is the durable handoff.**