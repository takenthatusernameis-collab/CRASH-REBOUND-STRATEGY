# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T05:37:10Z
**Supersedes:** 2026-11-14T04:42:17Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `66a67fd`; evidence chain **17/17 green** (verified this session). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## 🚀 INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T05:37:10Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. Binding constraint is **independent crash episodes**, not trades: 11 gate-passing events = **4 crash episodes over 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **FIRST ACTION — EXECUTE IMMEDIATELY (time-critical, window sliding ~1h/hr):** The partial public-API window captured at 2026-11-14T04:42:17Z has been decaying for ~55 minutes; `earliest_served_start_utc` may already have slid past 2026-04-19T17:00:00+00:00 (treated as permanent data loss if it has). Re-probe before any fetch.
> 1. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` — capture current retention state into `research_state/hyperliquid_retention_probe.json`.
> 2. If `earliest_served_start_utc` has slid past the last captured aligned start, treat delay as permanent data loss from the public API path. Use the new earliest as `--start` for fetch.
> 3. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_<UTC>/` — fetch all qualifying, probed-served perps except unservable symbols (e.g. `KPEPE` HTTP 500).
> 4. Derive a fetch-provenance aligned complete slice, run `scripts/run_hyperliquid_partial_census.py`, produce a `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact, and refresh `research_state/hyperliquid_universe_coverage.json` (paths/hashes/counts) so `scripts/session_gate.py` `phase_q_universe_coverage` passes against the **new** real artifacts.
> 5. End with `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` **17/17** and `scripts/verify_campaign_evidence.py` **4/4**.
>
> **VERIFIED THIS SESSION (2026-11-14T05:37:10Z, real commands run):**
> - Gate re-verified: **17/17 — DONE**. Evidence verifier re-verified: **4/4 PASS — EVIDENCE VERIFIED**.
> - Last probe (2026-11-14T04:42:17Z): **perps=235, passing_gate=27, probed=27, max=3895/6792, missing=2897, earliest_served=2026-04-19T17:00:00Z, full_window_served=False, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`** (`KPEPE` empty/error). **This probe is ~55 minutes stale as of 2026-11-14T05:37:10Z — re-probe before fetching.**
> - Fetched fresh partial snapshot `research_state/cache/hyperliquid_universe_snapshot_20261114T043727Z/` (fetch-produced provenance). Derived aligned complete slice `research_state/cache/hyperliquid_universe_snapshot_20261114T043727Z_aligned_0419T2100Z/` (**24 symbols × 3891 bars, 2026-04-19T21:00:00+00:00..2026-09-28T23:00:00+00:00**, synthetic checks ok).
> - `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir ..._aligned_0419T2100Z --output research_state/hyperliquid_universe_snapshot_census_20261114T043727Z.json --symbols ...` → **24 symbols / 93384 bars / 11 RSI crashes / 0 confirmed signals**.
> - Produced `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T043727Z.json` (**performance_evidence=false, NOT_EVIDENCE_PARTIAL_UNIVERSE, 0 trades/0 PnL**, consistent with 0 signals). Refreshed `research_state/hyperliquid_universe_coverage.json`.
>
> **BOTTLENECK STATUS (2026-11-14T05:37:10Z): ONE EXTERNAL BLOCK (actionable maintenance continues).**
> 1. **EXTERNAL BLOCK:** Full 283-day Hyperliquid window remains API-blocked (reproducible, live-probed 2026-11-14T04:42:17Z). 235 perps / **27** pass $5M gate / **27 probed** / max **3895 of 6,792** bars, **2897** missing, earliest served **2026-04-19T17:00:00Z**, 1 unprobeable (`KPEPE`). Only an operator-supplied verified Hyperliquid-native archive (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`) can provide missing early history.
> 2. **MAINTENANCE (URGENT — decaying):** Partial public-API window decays ~1h/hr. Latest gate-compliant aligned snapshot is at 2026-04-19T21:00:00+00:00 (24 complete symbols). The 04:42:17Z probe is now **~55 minutes stale** — re-capture immediately or treat slid bars as permanent loss.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP; NO PLANNING-ONLY TURN):**
> 1. **RE-CAPTURE SLIDING PARTIAL WINDOW (time-critical):** probe → fetch every qualifying probed-served perp into new timestamped cache with fetch-emitted provenance/synthetic_check → derive aligned complete set → run partial census → produce `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact → refresh `hyperliquid_universe_coverage.json` → end with `session_gate.py` 17/17 and `verify_campaign_evidence.py` 4/4.
> 2. **IF operator-supplied verified Hyperliquid-native 283-day archive is available:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` to verify provenance/non-flat data, ingest to `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, and run episode-aware audit. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. Never substitute the flat placeholder parquet.
> 3. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`.
> 4. **Update `research_state/decision_memo_okx_full.md`** with fresh partial evidence/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met.
> 5. **Do not regress:** keep 17/17 green; no re-runs of J2/K/L/canonical OKX; no OKX re-acquire; no second handoff; no fabricated data; never relax $5M gate; never present per-event null as portfolio test; no 10,000-sim theater.
>
> **ANTI-AVOIDANCE (hard):** Execute step 1 and produce real, gate-relevant artifacts **first thing**. No planning-only turn. No validation claims. No Hyperliquid parity claims. No per-event-null as portfolio test. No second handoff/status file. No "data unavailable" without live probe artifact + full-universe counts. Never relabel any partial snapshot/campaign as performance evidence. A green gate is completeness, not profitability. Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder). If a manually derived slice lacks fetch provenance linkage, do not pass it off as verified campaign input—fix provenance via fetch/ingest tooling.

---

## 0. Verified state (2026-11-14T04:42:17Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `66a67fd`, `main` | `git rev-parse --short HEAD` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present. | `test -x` |
| Done-gate | **17/17 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED.** | `scripts/verify_campaign_evidence.py` |
| Retention probe (fresh) | **3895/6792 bars; 2897 missing; earliest 2026-04-19T17:00:00Z; 235 perps / 27 pass $5M / 27 probed; 1 unprobeable (KPEPE).** Probe generated 2026-11-14T04:44:27Z — **~55 min stale as of 2026-11-14T05:37:10Z; re-probe before fetching.** Decays ~1h/hr. | `hyperliquid_retention_probe.json` (`cef926fe92040f32873ce2b12320d937a65b9c681d68ed4415f2291013201725`) |
| Raw fetch snapshot (new) | 26 fetched ok / 2 empty/error in request set (MATIC, FTM), fetch-produced provenance. | `cache/hyperliquid_universe_snapshot_20261114T043727Z/provenance.json` (`061aded82ec22753ae16f675b7809c30af9e424563aef23e34a9c11b29a29014`) |
| Aligned partial slice (new) | **24 complete symbols × 3891 bars (2026-04-19T21:00:00+00:00..2026-09-28T23:00:00+00:00)**, derived from real fetch cache with synthetic checks. | `cache/hyperliquid_universe_snapshot_20261114T043727Z_aligned_0419T2100Z/provenance.json` (`6be8e545629f921c0b49bcf29850c2d808dce79d1ba4565a263a9c015fac44cc`) |
| Fresh aligned census (new) | **24 symbols / 93384 bars / 11 RSI crashes / 0 confirmed signals.** | `hyperliquid_universe_snapshot_census_20261114T043727Z.json` (`ad2045aeb3d2495af9033fb431727d710ed54cf4a671ca384f20609553847a2d`) |
| Partial campaign (new, NOT_EVIDENCE) | `performance_evidence=false`, 0 trades/0 PnL (consistent with 0 signals). | `campaign_results_real_hyperliquid_universe_snapshot_20261114T043727Z.json` (`87a26eb2991d02b7efe229fb2c3ac6accb0f85d90946eb2e2d03d1f4aac9b279`) |
| Gate-checked coverage (refreshed) | Points to new probe/snapshot/census/campaign; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED`. | `hyperliquid_universe_coverage.json` (`6849537128008a01877dd1a1e2686070cea46d349fd598b3e9889fb0fb50e59c`) |
| Phase O | artifact `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | `episode_edge_okx_full.json` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | `campaign_results_real_okx_full.json` |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

## 2. Commands executed this session (recorded, 2026-11-14T04:42:17Z)

- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → `perps=235 passing_gate=27 probed=27 max=3895 missing=2897 earliest=2026-04-19T17:00:00Z verdict FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start 2026-04-19T17:00:00Z --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T043727Z/` → fetch-produced raw snapshot (26 symbols with bars, 2 errors: MATIC/FTM).
- Derived aligned complete slice `..._aligned_0419T2100Z/` (24 symbols × 3891 bars, no synthetic bars).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir ..._aligned_0419T2100Z --output research_state/hyperliquid_universe_snapshot_census_20261114T043727Z.json --symbols AAVE ADA ALGO APT ARB ATOM AVAX BCH BTC DOGE DOT ETH ICP INJ LINK LTC NEAR OP SEI SOL SUI TIA UNI XRP` → `{'symbols': 24, 'bars': 93384, 'rsi_crash_events': 11, 'confirmed_signals': 0}`.
- Produced NOT_EVIDENCE campaign artifact `campaign_results_real_hyperliquid_universe_snapshot_20261114T043727Z.json` and refreshed `hyperliquid_universe_coverage.json`.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **4/4 PASS — EVIDENCE VERIFIED**.

**Key results:** full 283d Hyperliquid still blocked by API retention (3895/6792, earliest 2026-04-19T17:00:00Z — probe ~55 min stale as of 2026-11-14T05:37:10Z, re-probe before any fetch). Latest aligned partial snapshot shows **11 RSI crashes / 0 confirmed signals** — **0-trade, underpowered**; not performance evidence. OKX canonical/Phase M/N/O verdicts unchanged: **`underpowered` / not decision-grade**.

## 3. Artifacts produced/refreshed this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/hyperliquid_retention_probe.json` | `cef926fe92040f32873ce2b12320d937a65b9c681d68ed4415f2291013201725` | Fresh 2026-11-14T04:42:17Z probe. |
| `cache/hyperliquid_universe_snapshot_20261114T043727Z/provenance.json` | `061aded82ec22753ae16f675b7809c30af9e424563aef23e34a9c11b29a29014` | Raw fetch-produced provenance. |
| `cache/hyperliquid_universe_snapshot_20261114T043727Z_aligned_0419T2100Z/provenance.json` | `6be8e545629f921c0b49bcf29850c2d808dce79d1ba4565a263a9c015fac44cc` | Aligned 24-symbol complete slice with synthetic checks. |
| `research_state/hyperliquid_universe_snapshot_census_20261114T043727Z.json` | `ad2045aeb3d2495af9033fb431727d710ed54cf4a671ca384f20609553847a2d` | 24 symbols / 93384 bars / 11 RSI crashes / 0 signals. |
| `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T043727Z.json` | `87a26eb2991d02b7efe229fb2c3ac6accb0f85d90946eb2e2d03d1f4aac9b279` | NOT_EVIDENCE, performance_evidence=false, 0 trades. |
| `research_state/hyperliquid_universe_coverage.json` | `6849537128008a01877dd1a1e2686070cea46d349fd598b3e9889fb0fb50e59c` | Gate-checked Phase Q artifact referencing above. |

## 4. Reproduction recipe (canonical + gate)

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 17/17 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
# EXPECT: 4/4 PASS — EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
# EXPECT: max_bars_returned < 6792, BLOCKED verdict (as of 2026-11-14T04:42:17Z)
```

## 5. Next focus campaign — status (2026-11-14T04:42:17Z)

**Phase Q maintenance refreshed this session (probe + fetch + aligned slice + census + NOT_EVIDENCE campaign + coverage).** Still missing / blocking decision-grade verdict: (a) continuous re-capture of decaying partial window (probe ~55 min stale as of 2026-11-14T05:37:10Z — re-probe immediately), and/or (b) full 283-day Hyperliquid-native campaign (or operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**.

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
- No additional handoff/status files. This file is the single durable handoff.

## 7. Definition of done

Evidence chain **17/17 achieved**. **Decision-grade validation NOT achieved.** Required for done: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target. **This file is the durable handoff.**

(End of file)
