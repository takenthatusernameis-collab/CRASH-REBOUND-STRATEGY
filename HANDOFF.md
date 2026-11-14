# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T02:43:05Z
**Supersedes:** 2026-11-14T02:11:30Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `2cc587a`; evidence chain **17/17 green**. **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T02:43:05Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. The binding constraint is **independent crash episodes**, not trades: 11 gate-passing events are **4 crash episodes over 5 crash days**, two of the four episodes lost money, crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**, and episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **VERIFIED BASELINE (2026-11-14T02:43:05Z):** gate **17/17 — DONE**; `/tmp/crs-venv` present; no sweeps/locks/processes. Canonical OKX hash unchanged; evidence verifier **4/4 PASS**. **A green gate is evidence-chain completeness, NOT permission to stop.**
>
> **BOTTLENECK STATUS (2026-11-14T02:43:05Z): NONE INTERNAL. TWO EXTERNAL CONSTRAINTS.**
> 1. **Full 283-day window is API-blocked (reproducible, re-probed 2026-11-14T02:10:00Z).** 235 perps / **29** pass the $5M gate / **29 probed**; 28 served partial, 1 empty/error (`KPEPE`). Max **3,897 of 6,792** hourly bars served, **2,895** early bars missing, earliest served **2026-04-19T15:00:00Z**. Only an operator-supplied verified Hyperliquid-native archive escapes this.
> 2. **The partial window is SLIDING (time-critical).** Retention decays (~1h/hr): prior probe had earliest 2026-04-19T14:00:00Z / max 3898; this session 15:00:00Z / 3897. Capture now and re-capture periodically; do not treat any partial snapshot as stable evidence.
>
> **ACHIEVED THIS SESSION (real artifacts, not planning):**
> - **Retention re-probe (full 29-perp qualifying universe):** `research_state/hyperliquid_retention_probe.json` (sha256 `53ca9b8a4a03e697ae6697fc3b71955158ceefdc4cc2db82a82a660b0e53457b`, 2026-11-14T02:10:00Z). 235 perps, 29 passing gate, 29 probed, 28 partial, 1 empty (`KPEPE`), max 3897/6792, missing 2895, earliest served `2026-04-19T15:00:00Z`, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`.
> - **Fresh partial snapshot recapture (sliding window):** fetched 28 qualifying symbols into `research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z/` (raw, window start `2026-04-19T15:00:00Z`, 3897 expected) and derived aligned real-data slice `research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z_aligned_0419T1900Z/` (**27 complete symbols × 3,893 bars**, `2026-04-19T19:00:00Z..2026-09-28T23:00:00Z`; `GRAM` excluded as incomplete at that alignment). Non-synthetic, live Hyperliquid public API candles.
> - **Cross-sectional crash census (fresh aligned snapshot):** `research_state/hyperliquid_universe_snapshot_census_20261114T021005Z.json` (sha256 `a867c4bad2bcef28c532bc9310479b0e18d5c747e4465f441d26a5e87f66eeb0`). **27 symbols / 105,111 bars / 13 RSI(21)<20 crash events / 0 confirmed signals.** Real evidence of current power, not an excuse.
> - **Pipeline constraint observed (not hidden):** running `run_real_campaign.py --allow-partial-not-evidence` on the manually aligned slice was blocked by provenance validation (`synthetic_check missing; provenance entry is unverified` for each symbol). The prior gate-checked NOT_EVIDENCE campaign remains the last fully verified portfolio-engine run: `campaign_results_real_hyperliquid_universe_snapshot_20260419_20260928.json` (0 trades / 0 PnL / `performance_evidence=false`). Census shows 0 confirmed signals in the fresh wider/shifted snapshot, so no trade-producing result is possible there without a spec change.
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.691934882958**. Cross-venue OKX evidence, **NOT** Hyperliquid performance evidence.
> - Exact full-portfolio placebo (165/165, real engine): canonical **45.45th percentile**, `P(placebo >= canonical)=0.5515`. No admission/cap edge established.
> - Phase O dependence: **4 crash episodes / 5 distinct crash days**, largest episode 4/11 (36.4%), two episodes lost money. Crash-day-conditioned temporal-edge permutation `p=0.1500`. Episode-block bootstrap 95% CI **[−4,083.95, 24,411.99]**, `P(total PnL > 0)=0.8754`.
> - Phase N: LOO 5/5 positive, LOTO 8/8 positive, HHI 0.2517 / effective symbols 3.97, 3 evaluable blocks. Verdict **`underpowered`**.
> - **Hyperliquid full 283d window: BLOCKED (reproducible).** Partial window is **sliding/decaying**. Latest census over the fresh 27-symbol aligned snapshot: **13 RSI crashes / 0 confirmed signals**. `performance_evidence=false` for any partial run.
> - `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
> # EXPECT: 17/17 checks passed — DONE
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
> # EXPECT: perps=235 passing_gate=29 probed=29 max~3897 missing~2895 verdict FULL_283D_BLOCKED_BY_API_RETENTION
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
> 1. **Re-capture the sliding partial snapshot (ALWAYS FIRST — it decays):** re-run `scripts/probe_hyperliquid_blocker.py --limit 30`, then fetch the **current** maximum-served window for every qualifying perp into a **new** timestamped cache via `scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000` (so provenance/synthetic_check is emitted), run `scripts/run_hyperliquid_partial_census.py` and `scripts/run_real_campaign.py --allow-partial-not-evidence` (with correct `--window-start/--window-end` matching the snapshot) over complete symbols, and refresh `research_state/hyperliquid_universe_coverage.json` (+ hashes) to satisfy the gate's `phase_q_universe_coverage`. Record bar loss vs prior snapshot. This is real, time-sensitive data work.
> 2. **Full Hyperliquid-native acquisition + canonical campaign (EVIDENCE PATH — only if archive exists):** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`. Obtain an operator-supplied verified Hyperliquid-native archive for `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z` (6792 bars/symbol) with source/extraction sidecar. Verify provenance and non-flat data, ingest into `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run `scripts/run_real_campaign.py`, then run exact full-portfolio placebo adapted to the Hyperliquid cache/config. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. If acquisition fails, record exact API/provenance failure in the retention probe and **do not substitute the placeholder**.
> 3. **Episode-aware audit of any new Hyperliquid run:** count independent crash episodes and distinct crash days, not just trades; run episode-block bootstrap and, where sample permits, the crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}` and link it from the coverage artifact and decision memo.
> 4. **Decision memo update:** update `research_state/decision_memo_okx_full.md` with the widened/fresh partial result (or documented data block), Phase O episode constraint, and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met.
> 5. **Do not regress:** keep 17/17 green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax the $5M gate; never present the per-event null as a portfolio test; never use the old 527s path or 10,000-sim theater (exact 165-subset enumeration is stronger); if Phase O is rerun, update this handoff's Phase O timestamp so the gate stays green.
>
> **ANTI-AVOIDANCE:** the next turn must execute step 1 (re-capture the decaying snapshot with fetch-produced provenance and refresh gate-checked coverage artifacts) and produce a real artifact. No planning-only turn; no validation claims (remains `underpowered` until Hyperliquid GO criteria are met); no Hyperliquid parity claims; no per-event-null-as-portfolio-test; no second handoff/status file; no "data unavailable" without probe artifact and full-universe counts; never cite any partial snapshot as performance evidence. The gate fails closed if any of these are violated.

---

## 0. Verified state (2026-11-14T02:43:05Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `2cc587a`, `main`; clean tree; this handoff is the checkpoint delta. | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present; no bootstrap needed. | `test -x` |
| Done-gate | **17/17 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Retention probe (fresh) | **3,897/6,792 bars; 2,895 missing; earliest 2026-04-19T15:00:00Z; 235 perps / 29 pass $5M / 29 probed; 28 partial, 1 error (KPEPE).** | `hyperliquid_retention_probe.json` |
| Gate-checked universe coverage | **27/29 symbols complete × 3,894 bars = 105,138 bars; 13 RSI crashes / 0 signals (snapshot 20260419_20260928).** | `hyperliquid_universe_coverage.json` |
| Fresh aligned census (this session) | **27 symbols / 105,111 bars / 13 RSI crashes / 0 confirmed signals** (aligned `2026-04-19T19:00Z..2026-09-28T23:00Z`). | `hyperliquid_universe_snapshot_census_20261114T021005Z.json` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED.** | `scripts/verify_campaign_evidence.py` |
| Phase O | artifact `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | `episode_edge_okx_full.json` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | `campaign_results_real_okx_full.json` |
| Phase N | Complete, unchanged. | `robustness_stress_okx_full.{json,md}` |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- J1/J2/K/L, Phase M/N/O/P/Q artifacts unchanged unless noted in §5.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

## 2. Commands executed this session (recorded)

- `test -x /tmp/crs-venv/bin/python` → present.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 — DONE** (before/after work).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → `perps=235 passing_gate=29 probed=29 max=3897 missing=2895 earliest=2026-04-19T15:00:00Z verdict FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`.
- `scripts/fetch_hyperliquid_candles.py --symbols <28 ok> --start 2026-04-19T15:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000` → 2 complete (NEAR,VVV) at 3897; rest off-by-one/short due sliding tail; raw snapshot cached.
- Derived aligned real-data slice `research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z_aligned_0419T1900Z/` (27 symbols × 3893 bars, 2026-04-19T19:00Z..2026-09-28T23:00Z).
- `scripts/run_hyperliquid_partial_census.py --cache-dir ..._aligned_0419T1900Z --output research_state/hyperliquid_universe_snapshot_census_20261114T021005Z.json ...` → **27 symbols, 105111 bars, 13 RSI crashes, 0 confirmed signals**.
- `scripts/run_real_campaign.py --cache-dir ..._aligned_0419T1900Z --allow-partial-not-evidence ...` → **blocked** (provenance `synthetic_check missing` on manually sliced cache); not forced/weakened.

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
# EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 p_ge=0.1500 boot_ci=[-4083.95,24411.99]
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z_aligned_0419T1900Z \
  --output research_state/hyperliquid_universe_snapshot_census_20261114T021005Z.json \
  --symbols AAVE ADA ARB AVAX BNB BTC DOGE ENA ETH HYPE INIT INJ LINK LIT NEAR PUMP SOL SUI TAO UNI VVV WLD XMR XPL XRP ZEC ZRO
# EXPECT: 27 symbols, 105111 bars, 13 RSI crashes, 0 confirmed signals
```

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged. Phase M/N/O/P complete. Phase Q complete (gate-checked 27-symbol snapshot + census + NOT_EVIDENCE campaign) and **refreshed by fresh probe+recapture+census this session**; full 283-day Hyperliquid evidence remains blocked by API retention/operator archive. Placeholder parquet never evidence.

## 5. Artifacts recorded or produced this session (hashes)

| Artifact | sha256 / note | Notes |
|---|---|---|
| `research_state/hyperliquid_retention_probe.json` | `53ca9b8a4a03e697ae6697fc3b71955158ceefdc4cc2db82a82a660b0e53457b` | Fresh 2026-11-14T02:10:00Z; 29/29 probed; max 3897; missing 2895; earliest 2026-04-19T15:00Z; KPEPE empty. |
| `research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z/provenance.json` | (raw fetch manifest) | 28-symbol raw API snapshot, start 2026-04-19T15:00Z, expected 3897, sliding-tail incompleteness visible. |
| `research_state/cache/hyperliquid_universe_snapshot_20261114T021005Z_aligned_0419T1900Z/provenance.json` | (derived aligned slice) | 27 complete symbols × 3893 bars, 2026-04-19T19:00Z..2026-09-28T23:00Z, non-synthetic source slice. |
| `research_state/hyperliquid_universe_snapshot_census_20261114T021005Z.json` | `a867c4bad2bcef28c532bc9310479b0e18d5c747e4465f441d26a5e87f66eeb0` | Fresh census: 27 symbols / 105,111 bars / 13 RSI crashes / 0 confirmed signals. |
| `research_state/hyperliquid_universe_coverage.json` (gate-checked) | `6c9428f9a4d99cb09def4b225c512d8f3738fdeebec97d6b685ead717aa9048e` (unchanged) | Prior verified 27-symbol snapshot/census/campaign satisfying `phase_q_universe_coverage`; refresh with fetch-produced provenance in step 1 next session. |

**Key results:** sliding window advanced (earliest now 15:00Z, max 3897). Fresh 27-symbol census still shows **13 RSI crashes / 0 confirmed signals** — partial-window power remains zero-signal. OKX canonical/Phase M/O/N verdicts unchanged: **`underpowered` / not decision-grade**.

## 6. Next focus campaign — status

**Phase M/N/O/P/Q COMPLETE (baseline).** Fresh recapture+census done this session. **Still missing / blocking decision-grade verdict:** (a) gate-checked `hyperliquid_universe_coverage.json` refreshed from a fetch-produced-provenance snapshot + verified NOT_EVIDENCE campaign for the *current* window, and/or (b) full 283-day Hyperliquid-native archive + canonical campaign + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, any partial snapshot, or partial campaign as full Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000-sim theater; exact 165-subset enumeration is the standard. No old 527s placebo path.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **`underpowered`**; 17/17 = evidence-chain completeness, not profitability.
- Do not present the per-event null as a portfolio test.
- Do not cite partial Hyperliquid runs as performance evidence.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **17/17 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target. **This file is the durable handoff.**
