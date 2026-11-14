# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T02:47:30Z
**Supersedes:** 2026-11-14T02:43:05Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `2cc587a`; evidence chain **17/17 green** (verified this session). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T02:47:30Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. Binding constraint is **independent crash episodes**, not trades: 11 gate-passing events = **4 crash episodes over 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **VERIFIED THIS SESSION (2026-11-14T02:47Z, real commands run):**
> - `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 — DONE** (start).
> - `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → **perps=235, passing_gate=30, probed=30, max=3896/6792, missing=2896, earliest_served=2026-04-19T16:00:00Z, full_window_served=False, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`** (`KPEPE` HTTP 500). **ONDO** now passes $5M gate (30 vs prior 29). Window slid again (~1h lost vs stored 02:10 probe max 3897/earliest 15:00Z).
> - `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **4/4 PASS — EVIDENCE VERIFIED**.
> - No conflicting processes; no `.sensitivity_sweep.lock`; working tree clean.
>
> **BOTTLENECK STATUS (2026-11-14T02:47:30Z): NONE INTERNAL. TWO EXTERNAL + ONE STALENESS BOTTLENECK.**
> 1. **Full 283-day Hyperliquid window: API-blocked (reproducible, live-probed 2026-11-14T02:45Z).** 235 perps / **30** pass $5M gate / **30 probed** / 29 partial, 1 empty-error (`KPEPE`). Max **3,896 of 6,792** bars, **2,896** missing, earliest served **2026-04-19T16:00:00Z**. Only an operator-supplied verified Hyperliquid-native archive (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`) can provide the missing early history.
> 2. **Partial window is SLIDING (time-critical).** Retention decays (~1h/hr): 2026-11-14T01:41Z max 3898, 02:10Z max 3897 (earliest 15:00Z), **02:45Z max 3896 (earliest 16:00Z)**. Gate-checked stored artifacts trail live state. Any uncaptured hour is permanently lost from the public API path.
> 3. **Gate-checked Hyperliquid coverage artifacts are stale vs live universe/window.** `research_state/hyperliquid_universe_coverage.json` / probe / snapshot / census / partial campaign currently reflect prior (27 complete, 29 probed, 3894-bar aligned window ending at older boundary). Live probe shows 30 qualifying symbols and a shifted window; `ONDO` is newly in-gate. This is the actionable bottleneck this session must remove by producing a fresh, fetch-provenance, gate-compliant capture.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP; NO PLANNING-ONLY TURN):**
> 1. **RE-CAPTURE THE SLIDING PARTIAL WINDOW NOW (highest priority, removes staleness bottleneck):**
>    - Re-run probe and persist: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` (and ensure `research_state/hyperliquid_retention_probe.json` reflects current result).
>    - Fetch **every currently qualifying, probed-served** perp (all passing-gate symbols except provably unservable like `KPEPE` if still erroring) into a **new timestamped cache** with **fetch-emitted provenance/synthetic_check** (do NOT hand-slice raw files into a campaign without provenance): use `scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <current earliest/max-aligned start> --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_<UTCSTAMP>/ ...` per script contract. Record actual bars/symbol and any symbol lost to the slide.
>    - Derive/identify the common complete aligned set across fetched symbols (all symbols sharing identical complete coverage over the same hourly window). Run `scripts/run_hyperliquid_partial_census.py` over that complete aligned cache and write a timestamped census artifact.
>    - Run `scripts/run_real_campaign.py --allow-partial-not-evidence` over the same fetch-provenanced aligned complete cache (correct `--window-start/--window-end`) to produce a `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact.
>    - Refresh `research_state/hyperliquid_universe_coverage.json` (and referenced artifact paths/hashes/counts) so `scripts/session_gate.py` `phase_q_universe_coverage` passes against the **new** real artifacts while preserving honest `BLOCKED`+`UNDERPOWERED` verdict semantics. End with `session_gate.py` 17/17 and `verify_campaign_evidence.py` 4/4.
> 2. **IF (and only if) an operator-supplied verified Hyperliquid-native 283-day archive is available now:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` to verify provenance/non-flat data, ingest to `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid cache/config, and run episode-aware audit. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. Never substitute the flat placeholder parquet.
> 3. **Episode-aware audit for any new Hyperliquid run:** count independent crash episodes and distinct crash days (not trades); run episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}` and link from coverage/memo artifacts.
> 4. **Update `research_state/decision_memo_okx_full.md`** with fresh partial evidence/data-block facts, Phase O episode constraint, and power-based sample-size target (episode-based). Keep verdict `underpowered` until every GO criterion is met.
> 5. **Do not regress:** keep 17/17 green; no re-runs of J2/K/L/canonical OKX; no OKX re-acquire; no second handoff; no fabricated data; never relax $5M gate; never present per-event null as portfolio test; never use old 527s placebo path or 10,000-sim theater (exact 165-subset enumeration is stronger for OKX canonical case).
>
> **ANTI-AVOIDANCE (hard):** Execute step 1 and produce real, gate-relevant artifacts. No planning-only turn. No validation claims. No Hyperliquid parity claims. No per-event-null-as-portfolio-test. No second handoff/status file. No "data unavailable" without live probe artifact + full-universe counts. Never cite any partial snapshot/campaign as performance evidence. A green gate is completeness, not profitability. Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder). If a manually derived slice lacks fetch provenance, do not pass it off as a verified campaign input—fix provenance via fetch/ingest tooling.

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
