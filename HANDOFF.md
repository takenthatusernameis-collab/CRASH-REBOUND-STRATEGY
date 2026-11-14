# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T05:52:19Z
**Supersedes:** 2026-11-14T05:49:27Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `342647c`; evidence chain **17/17 green** and evidence verifier **4/4 PASS** (re-verified this session against fresh 055219Z artifacts). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## 🚀 INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T05:52:19Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. Binding constraint is **independent crash episodes**, not trades: 11 gate-passing events = **4 crash episodes over 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **FIRST ACTION — EXECUTE IMMEDIATELY (time-critical, window sliding ~1h/hr):** The partial public-API window decays ~1h/hr. Latest fresh probe (2026-11-14T05:51Z) shows `earliest_served_start_utc` 2026-04-19T**19:00:00Z** (slid from 18:00Z at 05:40:40Z), max **3893/6792** bars, missing **2899**, perps 235 / **26** pass $5M gate / **26 probed** / 2 unprobeable (`MATIC`, `FTM`), verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:2`. Re-probe before any fetch because the window may have slid since this probe.
> 1. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` — capture current retention state into `research_state/hyperliquid_retention_probe.json`.
> 2. If `earliest_served_start_utc` has slid past the last captured aligned start (`2026-04-19T22:00:00Z` for snapshot 055219Z aligned slice), treat delay as permanent data loss from the public API path. Use the new earliest as `--start` for fetch.
> 3. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_<UTC>/` — fetch all qualifying, probed-served perps except unservable symbols (`MATIC`/`FTM` HTTP error).
> 4. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src research_state/cache/hyperliquid_universe_snapshot_<UTC>` — deterministic aligned complete slice with fetch provenance linkage.
> 5. **CENSUS OVER THE FULL ALIGNED SET (critical — fixes the silent undercount):** `scripts/run_hyperliquid_partial_census.py` defaults to a hardcoded 12-symbol list. If you omit `--symbols`, it will silently count only those 12 and understate crash events. ALWAYS pass the full complete set from the aligned provenance:
>    `SYMS=$(python3 -c "import json;d=json.load(open('research_state/cache/<aligned>/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")`
>    `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir <aligned> --symbols $SYMS --output research_state/hyperliquid_universe_snapshot_census_<UTC>.json`
> 6. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest <aligned>/provenance.json --allow-partial-not-evidence --window-start <aligned_start> --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix research_state/campaign_results_real_hyperliquid_universe_snapshot_<UTC>` — produce `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact (0 trades/0 PnL expected with 0 signals).
> 7. Refresh `research_state/hyperliquid_universe_coverage.json` (paths/hashes/counts) to the **new** real artifacts so `scripts/session_gate.py` `phase_q_universe_coverage` passes against them.
> 8. End with `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` **17/17** and `scripts/verify_campaign_evidence.py` **4/4**.
>
> **VERIFIED THIS SESSION (2026-11-14T05:52:19Z, real commands run):**
> - Gate re-verified: **17/17 — DONE**. Evidence verifier re-verified: **4/4 PASS — EVIDENCE VERIFIED** (against fresh 055219Z artifacts).
> - Fresh probe re-run (2026-11-14T05:51Z): **perps=235, passing_gate=26, probed=26, max=3893/6792, missing=2899, earliest_served=2026-04-19T19:00:00Z, full_window_served=False, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:2`** (`MATIC`, `FTM`). Window slid from 18:00Z→19:00Z vs the 05:40:40Z probe.
> - Latest gate-compliant fetch snapshot `research_state/cache/hyperliquid_universe_snapshot_20261114T055219Z/` (fetch-produced provenance). Derived aligned complete slice `research_state/cache/hyperliquid_universe_snapshot_20261114T055219Z_aligned_20260419T2200Z/` (**23 symbols × 3890 bars, 2026-04-19T22:00:00+00:00..2026-09-28T23:00:00+00:00**, synthetic checks ok; ARB now complete, DOT incomplete own window, MATIC/FTM error).
> - Latest census `research_state/hyperliquid_universe_snapshot_census_20261114T055219Z.json` → **23 symbols / 89470 bars / 11 RSI crashes / 0 confirmed signals** (run over the full aligned set, not the 12-symbol default).
> - Latest partial campaign `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T055219Z.json` (**performance_evidence=false, NOT_EVIDENCE_PARTIAL_UNIVERSE, 0 trades/0 PnL**). Coverage `research_state/hyperliquid_universe_coverage.json` references these artifacts + fresh probe.
>
> **BOTTLENECK STATUS (2026-11-14T05:52:19Z): ONE EXTERNAL BLOCK + ONE SCRIPT TRAP (both now handled for this session).**
> 1. **EXTERNAL BLOCK:** Full 283-day Hyperliquid window remains API-blocked (reproducible, live-probed 2026-11-14T05:51Z). 235 perps / **26** pass $5M gate / **26 probed** / max **3893 of 6,792** bars, **2899** missing, earliest served **2026-04-19T19:00:00Z**, 2 unprobeable (`MATIC`, `FTM`). Only an operator-supplied verified Hyperliquid-native archive (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`) can provide missing early history.
> 2. **MAINTENANCE (URGENT — decaying):** Partial public-API window decays ~1h/hr (slid 18:00Z→19:00Z between the 05:40 and 05:51 probes). Re-capture before the served window slides further; treat slid bars as permanent loss from the public API path.
> 3. **SCRIPT TRAP (fixed this session):** `scripts/run_hyperliquid_partial_census.py` has a hardcoded 12-symbol `DEFAULT_SYMBOLS`. Running it without `--symbols` over a 23-symbol aligned slice silently counts 12 symbols / 46680 bars and understates crash events. **Always pass the full complete-symbol set from the aligned provenance.** This is a standing trap: any future aligned slice larger than 12 symbols is undercounted unless `--symbols` is supplied.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP; NO PLANNING-ONLY TURN):**
> 1. **RE-CAPTURE SLIDING PARTIAL WINDOW (time-critical):** probe → fetch every qualifying probed-served perp into new timestamped cache with fetch-emitted provenance/synthetic_check → derive aligned complete set → run partial census **over the full complete-symbol set (`--symbols`, not the 12-symbol default)** → produce `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact → refresh `hyperliquid_universe_coverage.json` → end with `session_gate.py` 17/17 and `verify_campaign_evidence.py` 4/4.
> 2. **IF operator-supplied verified Hyperliquid-native 283-day archive is available:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` to verify provenance/non-flat data, ingest to `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, and run episode-aware audit. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. Never substitute the flat placeholder parquet.
> 3. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. A candidate Hyperliquid run cannot be promoted to evidence until it shows **>2 independent crash episodes with positive mean PnL and episode-block bootstrap CI excluding 0**.
> 4. **Update `research_state/decision_memo_okx_full.md`** with fresh partial evidence/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met.
> 5. **Do not regress:** keep 17/17 green; no re-runs of J2/K/L/canonical OKX; no OKX re-acquire; no second handoff; no fabricated data; never relax $5M gate; never present per-event null as portfolio test; no 10,000-sim theater.
>
> **ANTI-AVOIDANCE (hard):** Execute step 1 and produce real, gate-relevant artifacts **first thing**. No planning-only turn. No validation claims. No Hyperliquid parity claims. No per-event-null as portfolio test. No second handoff/status file. No "data unavailable" without live probe artifact + full-universe counts. Never relabel any partial snapshot/campaign as performance evidence. A green gate is completeness, not profitability. Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder). If a manually derived slice lacks fetch provenance linkage, do not pass it off as verified campaign input—fix provenance via fetch/ingest tooling. Never run the census without `--symbols` on a >12-symbol slice (it will undercount and look falsely healthy).

---

## 0. Verified state (2026-11-14T05:52:19Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `342647c`, `main` | `git rev-parse --short HEAD` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present. | `test -x` |
| Done-gate | **17/17 — DONE** (re-verified 2026-11-14T05:52Z against fresh 055219Z artifacts). | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED** (re-verified 2026-11-14T05:52Z). | `scripts/verify_campaign_evidence.py` |
| Retention probe (fresh this session) | **3893/6792 bars; 2899 missing; earliest 2026-04-19T19:00:00Z; 235 perps / 26 pass $5M / 26 probed; 2 unprobeable (MATIC, FTM).** Probe generated 2026-11-14T05:51Z. Decays ~1h/hr. | `hyperliquid_retention_probe.json` (`b47396e9c0701b02f27201b8b180104f74e1f61545d5ba4587913b7ac8c709aa`) |
| Raw fetch snapshot (latest gate-compliant) | Fetch-produced provenance for 055219Z. | `cache/hyperliquid_universe_snapshot_20261114T055219Z/provenance.json` (`4555805a910bedfb13e9fe5a0cea9b56af8f78bb5e81237aa10f9734fe796728`) |
| Aligned partial slice (latest) | **23 complete symbols × 3890 bars (2026-04-19T22:00:00+00:00..2026-09-28T23:00:00+00:00)**, derived from real fetch cache with synthetic checks. | `cache/hyperliquid_universe_snapshot_20261114T055219Z_aligned_20260419T2200Z/provenance.json` (`a0f8ed90fd1a9b9ca10839fb81d4b7c169b8ac4547a2d3372f22edf0ca721999`) |
| Fresh aligned census (latest) | **23 symbols / 89470 bars / 11 RSI crashes / 0 confirmed signals** (full aligned set, not 12-symbol default). | `hyperliquid_universe_snapshot_census_20261114T055219Z.json` (`261e440accc621cc5a9934282953b40ecead70f0dfefbe4ee74ac118b1bb9218`) |
| Partial campaign (latest, NOT_EVIDENCE) | `performance_evidence=false`, 0 trades/0 PnL (consistent with 0 signals). | `campaign_results_real_hyperliquid_universe_snapshot_20261114T055219Z.json` (`ca3c203aeb2bc56c7067373a8677e051a19f27b97a9f7312cfcb32b631312890`) |
| Gate-checked coverage | Points to 055219Z probe/snapshot/census/campaign; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED`. | `hyperliquid_universe_coverage.json` |
| Phase O | artifact `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | `episode_edge_okx_full.json` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | `campaign_results_real_okx_full.json` |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

## 2. Commands executed this session (recorded, 2026-11-14T05:52:19Z)

- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → `perps=235 passing_gate=26 probed=26 max=3893 missing=2899 earliest=2026-04-19T19:00:00Z verdict FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:2` (2026-11-14T05:51Z; window slid 18:00Z→19:00Z vs 05:40:40Z probe).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start 2026-04-19T19:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T055219Z` → 26 symbols fetched (23 ok, DOT incomplete own window, MATIC/FTM error).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src research_state/cache/hyperliquid_universe_snapshot_20261114T055219Z` → aligned `..._aligned_20260419T2200Z`, **23 complete symbols × 3890 bars**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir <aligned> --symbols <full 23> --output research_state/hyperliquid_universe_snapshot_census_20261114T055219Z.json` → **23/89470 bars/11 crashes/0 signals**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest <aligned>/provenance.json --allow-partial-not-evidence --window-start 2026-04-19T22:00:00Z --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T055219Z` → NOT_EVIDENCE, 0 trades/0 PnL, 23 symbols.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 checks passed — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **4/4 PASS — EVIDENCE VERIFIED**.

**Key results:** full 283d Hyperliquid still blocked by API retention (3893/6792, earliest 2026-04-19T19:00:00Z, probed 2026-11-14T05:51Z). Latest aligned partial snapshot shows **11 RSI crashes / 0 confirmed signals** across 23 symbols — **0-trade, underpowered**; not performance evidence. OKX canonical/Phase M/N/O verdicts unchanged: **`underpowered` / not decision-grade**.

## 3. Current gate-relevant artifacts (hashes, verified 2026-11-14T05:52:19Z)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/hyperliquid_retention_probe.json` | `b47396e9c0701b02f27201b8b180104f74e1f61545d5ba4587913b7ac8c709aa` | Re-run 2026-11-14T05:51Z (window slid 18:00Z→19:00Z). |
| `cache/hyperliquid_universe_snapshot_20261114T055219Z/provenance.json` | `4555805a910bedfb13e9fe5a0cea9b56af8f78bb5e81237aa10f9734fe796728` | Raw fetch-produced provenance (055219Z). |
| `cache/hyperliquid_universe_snapshot_20261114T055219Z_aligned_20260419T2200Z/provenance.json` | `a0f8ed90fd1a9b9ca10839fb81d4b7c169b8ac4547a2d3372f22edf0ca721999` | Aligned 23-symbol complete slice with synthetic checks. |
| `research_state/hyperliquid_universe_snapshot_census_20261114T055219Z.json` | `261e440accc621cc5a9934282953b40ecead70f0dfefbe4ee74ac118b1bb9218` | 23 symbols / 89470 bars / 11 RSI crashes / 0 signals. |
| `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T055219Z.json` | `ca3c203aeb2bc56c7067373a8677e051a19f27b97a9f7312cfcb32b631312890` | NOT_EVIDENCE, performance_evidence=false, 0 trades. |
| `research_state/hyperliquid_universe_coverage.json` | (refreshed this session) | Gate-checked Phase Q artifact referencing above. |

## 4. Reproduction recipe (canonical + gate)

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 17/17 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
# EXPECT: 4/4 PASS — EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
# EXPECT: max_bars_returned < 6792, BLOCKED verdict (as of 2026-11-14T05:51Z probe)
```

## 5. Next focus campaign — status (2026-11-14T05:52:19Z)

**Gate/evidence re-verified 17/17 and 4/4 this session against fresh 055219Z artifacts; probe re-run shows the window slid 18:00Z→19:00Z (no full-window service yet).** Still missing / blocking decision-grade verdict: (a) continuous re-capture of decaying partial window (public API retention slides ~1h/hr; re-probe and re-fetch before next work, census with full `--symbols` set), and/or (b) full 283-day Hyperliquid-native campaign (or operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**. No planning-only turn is acceptable: execute probe→fetch→derive→census(full set)→campaign→coverage→gate first.

## 6. Hard prohibitions

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
- **Never run `scripts/run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice** — its hardcoded 12-symbol default silently undercounts crash events and makes the slice look falsely healthy.
- No additional handoff/status files. This file is the single durable handoff.

## 7. Definition of done

Evidence chain **17/17 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target. **This file is the durable handoff.**

(End of file)