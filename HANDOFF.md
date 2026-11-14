# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T01:53:24Z
**Supersedes:** 2026-11-14T01:44:05Z, 2026-11-14T01:41:05Z, 2026-11-14T00:46:02Z, 2026-11-13T23:59:18Z, 2026-11-13T23:50:45Z, 2026-11-13T21:52:10Z, 2026-11-13T23:39:00Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `04c8c97`; evidence chain **17/17 green**; retention probe re-run over the **full 29-perp qualifying universe**; full-universe partial snapshot + census + NOT_EVIDENCE campaign executed. **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T01:53:24Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. The binding constraint is **independent crash episodes**, not trades: 11 gate-passing events are **4 crash episodes over 5 crash days**, two of the four episodes lost money, the crash-day-conditioned temporal-edge permutation gives **p(placebo >= canonical)=0.1500**, and the episode-block bootstrap CI is **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **VERIFIED BASELINE (2026-11-14T01:53:24Z):** gate **17/17 — DONE**; `/tmp/crs-venv` present; no sweeps/locks/processes; retention probe regenerated **2026-11-14T01:41:51Z** over **all 29 qualifying perps** (sha256 `40156de090ee6bbe47b0118cb6a0d09f9ce7fe3b66d654351b90ff958b94f7fa`); canonical hash unchanged; full suite **1022 passed, 1 skipped**. **A green gate is evidence-chain completeness, NOT permission to stop.**
>
> **BOTTLENECK STATUS (2026-11-14T01:53:24Z): NONE INTERNAL. TWO EXTERNAL CONSTRAINTS.**
> 1. **Full 283-day window is API-blocked (reproducible).** Live probe over 235 perps / 29 passing the $5M gate: max **3,898 of 6,792** hourly bars served, **2,894** early bars missing, earliest served **2026-04-19T14:00:00Z**. Only an operator-supplied verified Hyperliquid-native archive escapes this.
> 2. **The partial window is a SLIDING window (new finding, time-critical).** The 2026-11-13T21:43Z acquisition recorded **3,900** served bars for BTC/ETH; by 2026-11-14T01:48Z the same symbols served **3,896/3,900**. Earliest served hour advances ~1h per elapsed hour, so the achievable snapshot decays. **Capture it now and re-capture periodically; do not treat the partial snapshot as stable evidence.**
>
> **ACHIEVED THIS SESSION (real artifacts, not planning):**
> - Full-universe probe: 29/29 qualifying perps probed (`hyperliquid_retention_probe.json`, 20s wall).
> - Full-universe partial snapshot: **27/29 symbols complete × 3,894 bars = 105,138 bars** (`research_state/cache/hyperliquid_universe_snapshot_20260419_20260928/`), window `2026-04-19T18:00Z..2026-09-28T23:00Z`. Incomplete: GRAM (2,127 bars), KPEPE (error).
> - Cross-sectional census: **13 RSI(21)<20 crash events / 105,138 bars / 0 confirmed signals** (`hyperliquid_universe_snapshot_census_20260419_20260928.json`, sha `0704e85d88918e97d817e99f852ce99c742a5117ef406d9dd86c3d3956571f16`).
> - Partial campaign over 27 symbols: **0 trades / 0 PnL / `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`** (`campaign_results_real_hyperliquid_universe_snapshot_20260419_20260928.json`, sha `d45c9fb4c422ae28a687ac040cb21d742db9a50379c4f9db065ad1e8115876ab`).
> - Consolidated coverage artifact `research_state/hyperliquid_universe_coverage.json` (sha `6c9428f9a4d99cb09def4b225c512d8f3738fdeebec97d6b685ead717aa9048e`), now **gate-checked** by `phase_q_universe_coverage`.
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M volume gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.691934882958**. This is cross-venue OKX evidence, **NOT** Hyperliquid performance evidence.
> - Exact full-portfolio placebo (165/165 gate-preserving 8-of-11 admission subsets, real engine): mean **8746.21**, median **9287.25**, p05 **5807.36**, p95 **11360.11**, min **3988.13**, max **11795.92**. Canonical is at the **45.45th percentile**; `P(placebo >= canonical)=0.5515`. No admission/cap edge is established.
> - Phase O dependence audit: **4 crash episodes / 5 distinct crash days**, largest episode **4/11 events (36.4%)**; two of four episodes lost money. Trade-level and event-level independence assumptions overstate the effective sample.
> - Phase O conditional temporal-edge permutation: **40 deterministic draws** from the real 342-bar RSI(21)<20 census, per-symbol multiplicity and crash-day calendar preserved, real portfolio engine per draw. Canonical sits at the **85th percentile**; `p(placebo >= canonical)=0.1500`. Timing edge is **not established**.
> - Phase O episode-block bootstrap (20,000 resamples, 4 episode blocks): 95% CI **[−4,083.95, 24,411.99]**, `P(total PnL > 0)=0.8754`. The interval spans zero.
> - Phase N robustness stress: LOO 5/5 positive, LOTO 8/8 positive, HHI 0.2517 / effective symbols 3.97; expanding-window refit has 3 evaluable blocks. Verdict **`underpowered`**.
> - **Full Hyperliquid 283d window: BLOCKED (reproducible).** See bottleneck 1 above. A full-window campaign requires an operator-supplied verified Hyperliquid-native archive.
> - **Hyperliquid partial window: RUN, NOT EVIDENCE.** Widened to 27 complete symbols / 105,138 bars: **13 RSI crashes / 0 confirmed signals / 0 trades / 0 PnL**. `performance_evidence=false`. This is the power reality, not an excuse.
> - `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
> # EXPECT: 17/17 checks passed — DONE
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
> # EXPECT: perps=235 passing_gate=29 probed=29 max=3898 missing=2894 verdict FULL_283D_BLOCKED_BY_API_RETENTION
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
> # EXPECT: 4/4 PASS — EVIDENCE VERIFIED
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
> # EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
> # EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40
> # EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 p_ge=0.1500 boot_ci=[-4083.95,24411.99]
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
> # EXPECT: 17/17 checks passed — DONE
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|run_next_campaign|run_portfolio_placebo|run_episode_edge|probe_hyperliquid|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
> 1. **Re-capture the sliding partial snapshot (ALWAYS FIRST — it decays):** re-run `scripts/probe_hyperliquid_blocker.py --limit 30`, then re-fetch the current maximum-served window for every qualifying perp into a **new** timestamped cache dir (e.g. `hyperliquid_universe_snapshot_<UTC>`), run `scripts/run_hyperliquid_partial_census.py` and `scripts/run_real_campaign.py --allow-partial-not-evidence` over the complete symbols, and refresh `hyperliquid_universe_coverage.json`. If the earliest-served hour has advanced, record the new window and the bar loss. This is real data work and it is time-sensitive.
> 2. **Full Hyperliquid-native acquisition + canonical campaign (EVIDENCE PATH — only if archive exists):** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`. Obtain an operator-supplied verified Hyperliquid-native archive for `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol) with source/extraction sidecar. Verify provenance and non-flat data, ingest into `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive the verified universe, run `scripts/run_real_campaign.py`, then run the exact full-portfolio placebo adapted to the Hyperliquid cache/config. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. If acquisition fails, record the exact API/provenance failure in the retention probe and **do not substitute the placeholder**.
> 3. **Episode-aware audit of any new Hyperliquid run:** count independent crash episodes and distinct crash days, not just trades; run an episode-block bootstrap and, where sample permits, the crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}` and link it from the coverage artifact and decision memo.
> 4. **Decision memo update:** update `research_state/decision_memo_okx_full.md` with the widened partial result (or the documented data block), the Phase O episode constraint, and the power-based sample-size target. Keep the verdict `underpowered` until every GO criterion is met.
> 5. **Do not regress:** keep 17/17 green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax the $5M gate; never present the per-event null as a portfolio test; never use the old 527s path or 10,000-sim theater (the exact 165-subset enumeration is stronger); if Phase O is rerun, update this handoff's Phase O timestamp so the gate stays green.
>
> **ANTI-AVOIDANCE:** the next turn must execute step 1 (re-capture the decaying snapshot) and produce a real artifact, and must satisfy the gate's `phase_q_universe_coverage` check. No planning-only turn; no validation claims (remains `underpowered` until Hyperliquid GO criteria are met); no Hyperliquid parity claims; no per-event-null-as-portfolio-test; no second handoff/status file; no "data unavailable" without the probe artifact and the full-universe counts; never cite the 27-symbol partial snapshot as performance evidence. The gate fails closed if any of these are violated.

---

## 0. Verified state (2026-11-14T01:53:24Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `04c8c97`, `main`; this handoff/gate update is the checkpoint delta. | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present; no bootstrap needed. | `test -x` |
| Done-gate | **17/17 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Retention probe | **3,898/6,792 bars served; 2,894 missing; 235 perps / 29 pass $5M gate / 29 probed.** | §5, `hyperliquid_retention_probe.json` |
| Universe coverage | **27/29 symbols complete × 3,894 bars = 105,138 bars; 13 RSI crashes / 0 signals.** | `hyperliquid_universe_coverage.json` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED.** | `scripts/verify_campaign_evidence.py` |
| Phase O artifact | `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | §5 |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | §1 |
| Phase N | Complete, unchanged. | `robustness_stress_okx_full.{json,md}` |
| Phase J3 | Full Hyperliquid **BLOCKED**; partial Hyperliquid **NOT_EVIDENCE run complete** (now 27 symbols). | §5 |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- J1 census: `crash_event_census_real_okx_full.{json,md}` — 342→187→39→89→11→8, 0 unexplained.
- J2 `sensitivity_sweep_real_okx_full.*`, K `interaction_sweep_real_okx_full.*`, L `robustness_real_okx_full.*` (**`underpowered`**).
- Phase M `placebo_portfolio_okx_full.{json,md}` — exact 165-subset enumeration; canonical at 45.45th percentile.
- Phase N `robustness_stress_okx_full.{json,md}` — LOO/LOTO/concentration/power/expanding-window refit; **`underpowered`**.
- Phase O `episode_edge_okx_full.{json,md}` — 4 episodes / 5 crash days; p=0.1500; episode-block CI spans zero; **`underpowered`**.

## 2. Commands executed this session (recorded)

- `test -x /tmp/crs-venv/bin/python` → present; no bootstrap needed.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 — DONE** (after adding `phase_q_universe_coverage`).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → `perps=235 passing_gate=29 probed=29 max=3898 missing=2894 earliest=2026-04-19T14:00:00Z verdict FULL_283D_BLOCKED_BY_API_RETENTION` (20s wall).
- `scripts/fetch_hyperliquid_candles.py` over 29 qualifying perps → `27 complete × 3894 bars; GRAM incomplete 2127; KPEPE error` (1m31s).
- `scripts/run_hyperliquid_partial_census.py` over 27 complete symbols → `symbols=27 bars=105138 rsi_crash_events=13 confirmed_signals=0` (1m19s).
- `scripts/run_real_campaign.py --allow-partial-not-evidence` over 27 symbols → `0 trades / 0 PnL / NOT_EVIDENCE` (1m22s).
- Added `scripts/session_gate.py::check_universe_coverage` + regression test `tests/test_session_gate_universe_coverage_20261114.py`.

## 3. Reproduction recipe (canonical + exact placebo + Phase O)

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 17/17 checks passed — DONE

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
# EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40
# EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 p_ge=0.1500
#         boot_ci=[-4083.95,24411.99]

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20260419_20260928 \
  --output research_state/hyperliquid_universe_snapshot_census_20260419_20260928.json \
  --symbols AAVE ADA ARB AVAX BNB BTC DOGE ENA ETH HYPE INIT INJ LINK LIT NEAR PUMP SOL SUI TAO UNI VVV WLD XMR XPL XRP ZEC ZRO
# EXPECT: 27 symbols, 105138 bars, 13 RSI crashes, 0 confirmed signals
```

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged. Phase M (exact full-portfolio placebo + decision memo) complete. Phase N (robustness stress / power analysis) complete. Phase O (crash-episode dependence audit + conditional temporal-edge test + episode-block bootstrap) complete. Phase P (reproducible retention probe + narrative-independent evidence verifier) complete. Phase Q (full-universe coverage: widened probe + 27-symbol snapshot + census + NOT_EVIDENCE campaign) complete. Placeholder parquet never evidence.

## 5. Artifacts recorded or produced this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/hyperliquid_retention_probe.json` | `40156de090ee6bbe47b0118cb6a0d09f9ce7fe3b66d654351b90ff958b94f7fa` | Widened to 29/29 qualifying perps; still 3898/6792 served; 2894 missing. |
| `research_state/hyperliquid_universe_coverage.json` | `6c9428f9a4d99cb09def4b225c512d8f3738fdeebec97d6b685ead717aa9048e` | Phase Q consolidated coverage; gate-checked by `phase_q_universe_coverage`. |
| `research_state/cache/hyperliquid_universe_snapshot_20260419_20260928/provenance.json` | `072fa71d2123eb0f2825bfdd32baf3a01e705d49545e1de5ede5e130e17b46bc` | 29 requested / 27 complete / 2 incomplete; 3894-bar window. |
| `research_state/hyperliquid_universe_snapshot_census_20260419_20260928.json` | `0704e85d88918e97d817e99f852ce99c742a5117ef406d9dd86c3d3956571f16` | 27 symbols / 105,138 bars / 13 RSI crashes / 0 confirmed signals. |
| `research_state/campaign_results_real_hyperliquid_universe_snapshot_20260419_20260928.json` | `d45c9fb4c422ae28a687ac040cb21d742db9a50379c4f9db065ad1e8115876ab` | Partial campaign; **0 trades / 0 PnL / NOT_EVIDENCE**. |
| `research_state/episode_edge_okx_full.json` | `dda600eeaee1811c282c205032e53e0c96b6433842be331edacab5cf096a397d` | Phase O; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95,24411.99]. |
| `research_state/robustness_stress_okx_full.json` | `9b309246d1a2ac65b37678eed1ea58e6b23e5470620e529a60492681e35b6d99` | Phase N; verdict underpowered. |
| `research_state/hyperliquid_acquisition_status.json` | (modified) | Full-universe probe + sliding-window snapshot + partial campaign links. |
| `scripts/session_gate.py` | (modified) | 17 checks; Phase Q coverage fails closed. |
| `tests/test_session_gate_universe_coverage_20261114.py` | (new) | Regression test: full-universe probe/snapshot/census/campaign required. |

**Key results:** exact full-portfolio placebo → canonical at **45.45th percentile**, `P(placebo >= canonical)=0.5515`; canonical is not distinguishable from a random 8-of-11 admission subset. Phase O → **4 crash episodes / 5 crash days**, two episodes negative; crash-day-conditioned temporal-edge permutation p=**0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Hyperliquid full 283d is **blocked by API retention**, and the partial window is **sliding/decaying**: the widened 27-symbol snapshot yields **13 RSI crashes / 0 confirmed signals / 0 trades**. Verdict: **`underpowered` / not decision-grade.**

## 6. Next focus campaign — status

**Phase M COMPLETE.** **Phase N COMPLETE.** **Phase O COMPLETE.** **Phase P COMPLETE.** **Phase Q PARTIAL COMPLETE:** full universe probed, 27-symbol snapshot captured, census and NOT_EVIDENCE campaign run. **Still missing / blocking decision-grade verdict:** full 283-day Hyperliquid-native data (operator archive) + canonical campaign + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, the decaying partial snapshot, or the 27-symbol partial campaign as full Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000-sim theater; the exact 165-subset enumeration is the standard. Do not use the old 527s path for placebo work.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **`underpowered`**; 17/17 = evidence-chain completeness, not profitability.
- Do not present the per-event null as a portfolio test.
- Do not cite the partial Hyperliquid run as performance evidence.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **17/17 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or a documented operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and the power-based sample-size target. **This file is the durable handoff.**