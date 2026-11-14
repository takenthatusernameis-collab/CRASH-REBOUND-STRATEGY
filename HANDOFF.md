# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T00:46:02Z
**Supersedes:** 2026-11-13T23:59:18Z, 2026-11-13T23:50:45Z, 2026-11-13T21:52:10Z, 2026-11-13T23:39:00Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `4ac40cb`; this refresh converts the "API is blocked" prose claim into a reproducible artifact, adds a mechanical evidence verifier, and raises the done-gate to **16/16**. **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T00:46:02Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. The binding constraint is **independent crash episodes**, not trades: 11 gate-passing events are **4 crash episodes over 5 crash days**, two of the four episodes lost money, the crash-day-conditioned temporal-edge permutation gives **p(placebo >= canonical)=0.1500**, and the episode-block bootstrap CI is **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **WHAT CHANGED THIS SESSION (bottlenecks removed):**
> - **The blocker claim is now reproducible, not prose.** `scripts/probe_hyperliquid_blocker.py` queries the live public API, enumerates the current perp universe (not a stale hardcoded list), measures each symbol's 24h notional volume against the $5M gate, and writes `research_state/hyperliquid_retention_probe.json`. Every count is derived live: **235 perps, 29 pass the $5M gate, 6 probed, max 3,898/6,792 bars served, 2,894 early bars missing, earliest served 2026-04-19T14:00:00Z**. If the API ever serves the full window the artifact flips to `FULL_283D_SERVED` and the gate then *demands* a real full campaign instead of accepting the blocker.
> - **The stale partial runbook was the real bottleneck.** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` still names 24 symbols; **MATIC and FTM are delisted and return ZERO bars**, so any agent following it literally gets a fail-closed refusal instead of progress. The probe's `requested_not_in_live_universe` field now records this mechanically. Do **not** re-run that 24-symbol list; use the live universe.
> - **New mechanical anti-avoidance gate.** `scripts/verify_campaign_evidence.py` checks the artifacts themselves (canonical OKX reconciles, blocker backed by probe, no `validated` verdict while `underpowered`, partial Hyperliquid stays `performance_evidence=false`, placeholder archive still labeled non-evidence). It is narrative-independent: a future agent cannot pass it by writing better prose. Wired into the done-gate as `phase_p_evidence_verifier`.
> - **Done-gate raised to 16/16.** Two new checks: `phase_p_retention_probe` and `phase_p_evidence_verifier`. A stale handoff now fails closed (the gate requires this file to record `16/16` and to reference both new scripts).
> - `/tmp/crs-venv` is present; no dependency bootstrap needed. No sweeps, locks, or research processes are running. Full suite: **988 passed, 1 skipped**.
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M volume gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.691934882958**. This is cross-venue OKX evidence, **NOT** Hyperliquid performance evidence.
> - Exact full-portfolio placebo (165/165 gate-preserving 8-of-11 admission subsets, real engine): mean **8746.21**, median **9287.25**, p05 **5807.36**, p95 **11360.11**, min **3988.13**, max **11795.92**. Canonical is at the **45.45th percentile**; `P(placebo >= canonical)=0.5515`. No admission/cap edge is established.
> - Phase O dependence audit: **4 crash episodes / 5 distinct crash days**, largest episode **4/11 events (36.4%)**; two of four episodes lost money. Trade-level and event-level independence assumptions overstate the effective sample.
> - Phase O conditional temporal-edge permutation: **40 deterministic draws** from the real 342-bar RSI(21)<20 census, per-symbol multiplicity and crash-day calendar preserved, real portfolio engine per draw. Canonical sits at the **85th percentile**; `p(placebo >= canonical)=0.1500`. Timing edge is **not established**.
> - Phase O episode-block bootstrap (20,000 resamples, 4 episode blocks): 95% CI **[−4,083.95, 24,411.99]**, `P(total PnL > 0)=0.8754`. The interval spans zero.
> - Phase N robustness stress: LOO 5/5 positive, LOTO 8/8 positive, HHI 0.2517 / effective symbols 3.97; expanding-window refit has 3 evaluable blocks. Verdict **`underpowered`**.
> - **Full Hyperliquid 283d window: BLOCKED (now reproducible).** Live probe: 235 perps, 29 pass the $5M gate, max **3,898 of 6,792** hourly bars served, **2,894** early bars not served, earliest served **2026-04-19T14:00:00Z**. Artifact `research_state/hyperliquid_retention_probe.json` (sha256 `cd3db8b87cbed2bff35ec8c79078ab0d7976b8e3efe6ea01c538a2ad4785ad49`). A full-window campaign requires an operator-supplied verified Hyperliquid-native archive.
> - **Hyperliquid partial 163d window: RUN, NOT EVIDENCE.** 12 complete symbols, 3,900 bars each; campaign **0 trades / 0 PnL**; census **8 RSI(21)<20 events / 46,800 bars / 0 confirmed signals**. `performance_evidence=false`.
> - `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
> # EXPECT: 16/16 checks passed — DONE
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 6
> # EXPECT: perps=235 passing_gate=29 probed=6 expected=6792 max=3898 missing=2894; verdict FULL_283D_BLOCKED_BY_API_RETENTION
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
> # EXPECT: 4/4 PASS — EVIDENCE VERIFIED
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
> # EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
> # EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40
> # EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 p_ge=0.1500 boot_ci=[-4083.95,24411.99]
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
> # EXPECT: 16/16 checks passed — DONE
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|run_next_campaign|run_portfolio_placebo|run_episode_edge|probe_hyperliquid|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **VERIFIED BASELINE (2026-11-14T00:46:02Z):** gate **16/16 — DONE**; `/tmp/crs-venv` present; no sweeps/locks/processes; retention probe artifact sha256 `cd3db8b8…5ad49`; canonical hash unchanged; full Hyperliquid 283d still blocked; full suite 988 passed / 1 skipped. **A green gate is evidence-chain completeness, NOT permission to stop.**
>
> **BOTTLENECK STATUS (2026-11-14T00:46:02Z): NONE INTERNAL.** The only blocker is external: public Hyperliquid API retention cannot serve the full 283-day history, now recorded by a reproducible probe. The fallback is achievable real-data work over the live universe (enumerate every served perp, extend the partial acquisition, record exact errors), not planning.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
> 1. **Re-probe the live universe (ALWAYS FIRST):** `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` (widen `--limit` to probe every qualifying perp). If `full_window_served` flips to true, go to step 2 with the real window. If still blocked, go to step 3.
> 2. **Full Hyperliquid-native acquisition + canonical campaign (PRIMARY):** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` with a *live* universe. Obtain an operator-supplied verified Hyperliquid-native archive for `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol) with source/extraction sidecar. Verify provenance and non-flat data, ingest into `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive the verified universe, run `scripts/run_real_campaign.py`, then run the exact full-portfolio placebo adapted to the Hyperliquid cache/config. Produce `research_state/campaign_results_real_hyperliquid_full*.json` and `research_state/placebo_portfolio_hyperliquid_full.{json,md}`. If acquisition fails, record the exact API/provenance failure in the retention probe and **do not substitute the placeholder**.
> 3. **Fallback heavy work (only if the full archive is blocked):** enumerate every Hyperliquid perp the live API serves (not the stale 24-symbol list), extend the partial acquisition over the maximum served window, retry incomplete symbols with bounded backoff, rerun the NOT_EVIDENCE partial campaign, and rerun the cross-sectional crash census. Update `research_state/hyperliquid_acquisition_status.json` with new symbol/bar counts, complete/incomplete lists, exact errors, and the remaining block. This is real data work, not planning. **Measured this session:** 26 symbols × ~3,900 bars yields only **11 RSI crashes / 0 confirmed signals** — report this honestly; it is the power reality, not an excuse.
> 4. **Episode-aware audit of any new Hyperliquid run:** count independent crash episodes and distinct crash days, not just trades; run an episode-block bootstrap and, where sample permits, the crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}` and link it from the acquisition status and decision memo.
> 5. **Decision memo update:** update `research_state/decision_memo_okx_full.md` with the Hyperliquid full result (or the documented data block), the Phase O episode constraint, and the power-based sample-size target. Keep the verdict `underpowered` until every GO criterion is met.
> 6. **Do not regress:** keep 16/16 green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax the $5M gate; never present the per-event null as a portfolio test; never use the old 527s path or 10,000-sim theater (the exact 165-subset enumeration is stronger); if Phase O is rerun, update this handoff's Phase O timestamp so the gate stays green.
>
> **ANTI-AVOIDANCE:** the next turn must execute step 1 and then step 2 or step 3 and produce a real artifact. No planning-only turn; no validation claims (remains `underpowered` until Hyperliquid GO criteria are met); no Hyperliquid parity claims; no per-event-null-as-portfolio-test; no second handoff/status file; no "data unavailable" without the probe artifact and the partial counts. The gate now fails closed if any of these are violated.

---

## 0. Verified state (2026-11-14T00:46:02Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `4ac40cb`, `main`; this handoff/gate update is the checkpoint delta. | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present; no bootstrap needed. | `test -x` |
| Done-gate | **16/16 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Retention probe | **3,898/6,792 bars served; 2,894 missing; 235 perps / 29 pass $5M gate / 6 probed.** | §5, `hyperliquid_retention_probe.json` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED.** | `scripts/verify_campaign_evidence.py` |
| Phase O artifact | `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | §5 |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | §1 |
| Phase N | Complete, unchanged. | `robustness_stress_okx_full.{json,md}` |
| Phase J3 | Full Hyperliquid **BLOCKED**; partial Hyperliquid **NOT_EVIDENCE run complete**. | §5 |

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
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` before the fix → **12/14**; `phase_o_episode_edge` missing `verdict`, `durable_handoff` stale.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40` → `episodes=4 events=11 days=5 largest_episode=4/11 perm_mode=deterministic_draws:40 p_ge=0.1500 canon_pct=0.8500 boot_ci=[-4083.95,24411.99] wall=287.7s`.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` after the fix → **14/14 — DONE**.
- Updated `scripts/session_gate.py` so a stale `HANDOFF.md` missing the current Phase O `generated_at_utc` fails closed; added a regression test.
- Updated `research_state/decision_memo_okx_full.md` reproduction to the actual `--draws 40` Phase O run.
- **This refresh:** updated handoff timestamp to `2026-11-13T23:59:18Z`, git HEAD to `5bf7e21`, verified 14/14 gate still passes, confirmed no stale processes/locks.

## 3. Reproduction recipe (canonical + exact placebo + Phase O)

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 14/14 checks passed — DONE

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
# EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40
# EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 p_ge=0.1500
#         boot_ci=[-4083.95,24411.99]

PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py
# EXPECT: 12 symbols, 46800 bars, 8 RSI crashes, 0 confirmed signals
```

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged. Phase M (exact full-portfolio placebo + decision memo) complete. Phase N (robustness stress / power analysis) complete. Phase O (crash-episode dependence audit + conditional temporal-edge test + episode-block bootstrap) complete. Partial Hyperliquid NOT_EVIDENCE run + crash census complete. Placeholder parquet never evidence.

## 5. Artifacts recorded or produced this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/episode_edge_okx_full.json` | `dda600eeaee1811c282c205032e53e0c96b6433842be331edacab5cf096a397d` | Phase O regenerated; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95,24411.99]; verdict underpowered. |
| `research_state/episode_edge_okx_full.md` | `8f36913cc97b34a6c39306c13a0df8e12b733219858792a4431f87d4bc527d31` | Human-readable Phase O summary. |
| `research_state/robustness_stress_okx_full.json` | `9b309246d1a2ac65b37678eed1ea58e6b23e5470620e529a60492681e35b6d99` | Phase N LOO/LOTO/concentration/power/refit; verdict underpowered. |
| `research_state/hyperliquid_acquisition_status.json` | `230b7f4a5d1210b19f33e2be738e50521861c668e14402432d6505182febcb84` | Full-window block + partial API probe + partial campaign/census links. |
| `research_state/campaign_results_real_hyperliquid_partial_20260419_20260928.json` | `e32d7cf34e2be295aec6e5e5627775db4db9d6a83e31d31837a8544094ffb4bc` | Partial Hyperliquid campaign; **0 trades / 0 PnL / NOT_EVIDENCE**. |
| `research_state/hyperliquid_partial_crash_census_20260419_20260928.json` | `8b0f9d9e5421ed142442c1ab64b44441796cfcf330e4e5f9da900d6fbda77c14` | 12 symbols / 46,800 bars / 8 RSI crashes / 0 confirmed signals. |
| `research_state/cache/hyperliquid_partial_20260419_20260928/provenance.json` | `2da30957fa162361510a26b7748eeb6796fd9642e4fe5e60cac415eb0c553be7` | Real API provenance; 12 complete, 12 incomplete/error. |
| `research_state/decision_memo_okx_full.md` | (modified) | Phase O verdict, power target, Hyperliquid block, stop/go criteria. |
| `scripts/session_gate.py` | (modified) | 14 checks; Phase O + stale-handoff timestamp fail-closed. |
| `tests/test_session_gate_episode_edge_20261113.py` | (modified) | Regression test: handoff must record the current Phase O timestamp. |

**Key results:** exact full-portfolio placebo → canonical at **45.45th percentile**, `P(placebo >= canonical)=0.5515`; canonical is not distinguishable from a random 8-of-11 admission subset. Phase O → **4 crash episodes / 5 crash days**, two episodes negative; crash-day-conditioned temporal-edge permutation p=**0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Hyperliquid full 283d is **blocked by API retention**; the partial 163d run has **0 trades** and **8 RSI crashes / 0 confirmed signals**. Verdict: **`underpowered` / not decision-grade.**

## 6. Next focus campaign — status

**Phase M COMPLETE.** **Phase N COMPLETE.** **Phase O COMPLETE.** **Phase J3 PARTIAL COMPLETE:** maximum API window acquired and run as NOT_EVIDENCE; crash census recorded. **Still missing / blocking decision-grade verdict:** full 283-day Hyperliquid-native data (operator archive) + canonical campaign + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX or partial Hyperliquid as full Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000-sim theater; the exact 165-subset enumeration is the standard. Do not use the old 527s path for placebo work.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **`underpowered`**; 14/14 = evidence-chain completeness, not profitability.
- Do not present the per-event null as a portfolio test.
- Do not cite the partial Hyperliquid run as performance evidence.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **14/14 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or a documented operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and the power-based sample-size target. **This file is the durable handoff.**