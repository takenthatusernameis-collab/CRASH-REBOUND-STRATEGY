# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T05:49:27Z
**Supersedes:** 2026-11-14T05:45:07Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main`, base HEAD `66a67fd`; evidence chain **17/17 green** and evidence verifier **4/4 PASS** (re-verified this session). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## 🚀 INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-14T05:49:27Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** force a decision-grade Hyperliquid-native verdict, or prove the data block with a reproducible probe. The OKX evidence is **cross-venue, `underpowered`, and NOT Hyperliquid performance evidence**. Binding constraint is **independent crash episodes**, not trades: 11 gate-passing events = **4 crash episodes over 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**
>
> **FIRST ACTION — EXECUTE IMMEDIATELY (time-critical, window sliding ~1h/hr):** The partial public-API window decays ~1h/hr. Latest fresh probe (2026-11-14T05:40:40Z) shows `earliest_served_start_utc` 2026-04-19T18:00:00Z and max 3894/6792 bars (2898 missing), `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` (`KPEPE`). Re-probe before any fetch because the window may have slid since this probe.
> 1. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` — capture current retention state into `research_state/hyperliquid_retention_probe.json`.
> 2. If `earliest_served_start_utc` has slid past the last captured aligned start (`2026-04-19T21:00:00Z` for snapshot 044431 aligned slice), treat delay as permanent data loss from the public API path. Use the new earliest as `--start` for fetch.
> 3. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_<UTC>/` — fetch all qualifying, probed-served perps except unservable symbols (e.g. `KPEPE` HTTP 500).
> 4. Derive a fetch-provenance aligned complete slice, run `scripts/run_hyperliquid_partial_census.py`, produce a `performance_evidence=false` / `NOT_EVIDENCE` partial campaign artifact, and refresh `research_state/hyperliquid_universe_coverage.json` (paths/hashes/counts) so `scripts/session_gate.py` `phase_q_universe_coverage` passes against the **new** real artifacts.
> 5. End with `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` **17/17** and `scripts/verify_campaign_evidence.py` **4/4**.
>
> **VERIFIED THIS SESSION (2026-11-14T05:49:27Z, real commands run):**
> - Gate re-verified: **17/17 — DONE**. Evidence verifier re-verified: **4/4 PASS — EVIDENCE VERIFIED**.
> - Fresh probe re-run (2026-11-14T05:40:40Z): **perps=235, passing_gate=27, probed=27, max=3894/6792, missing=2898, earliest_served=2026-04-19T18:00:00Z, full_window_served=False, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`** (`KPEPE`). No slide past current aligned start observed at this probe; re-probe again before fetching.
> - Latest gate-compliant fetch snapshot `research_state/cache/hyperliquid_universe_snapshot_20261114T044431Z/` (fetch-produced provenance). Derived aligned complete slice `research_state/cache/hyperliquid_universe_snapshot_20261114T044431Z_aligned_20260419T2100Z/` (**23 symbols × 3891 bars, 2026-04-19T21:00:00+00:00..2026-09-28T23:00:00+00:00**, synthetic checks ok; ARB rejected for incomplete own window/gap, MATIC/FTM error).
> - Latest census `research_state/hyperliquid_universe_snapshot_census_20261114T044431Z.json` → **23 symbols / 89493 bars / 11 RSI crashes / 0 confirmed signals**.
> - Latest partial campaign `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T044431Z.json` (**performance_evidence=false, NOT_EVIDENCE_PARTIAL_UNIVERSE, 0 trades/0 PnL**). Coverage `research_state/hyperliquid_universe_coverage.json` references these artifacts + fresh probe.
>
> **BOTTLENECK STATUS (2026-11-14T05:49:27Z): ONE EXTERNAL BLOCK (actionable maintenance continues).**
> 1. **EXTERNAL BLOCK:** Full 283-day Hyperliquid window remains API-blocked (reproducible, live-probed 2026-11-14T05:40:40Z). 235 perps / **27** pass $5M gate / **27 probed** / max **3894 of 6,792** bars, **2898** missing, earliest served **2026-04-19T18:00:00Z**, 1 unprobeable (`KPEPE`). Only an operator-supplied verified Hyperliquid-native archive (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`) can provide missing early history.
> 2. **MAINTENANCE (URGENT — decaying):** Partial public-API window decays ~1h/hr. Latest gate-compliant aligned snapshot is 044431 at 2026-04-19T21:00:00+00:00 (**23 complete symbols**). Re-capture before the served window slides further; treat slid bars as permanent loss from the public API path.
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

## 0. Verified state (2026-11-14T05:45:07Z)

| Check | Result | Evidence |
|---|---|---|
| Git | base HEAD `66a67fd`, `main` | `git rev-parse --short HEAD` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present. | `test -x` |
| Done-gate | **17/17 — DONE** (re-verified 2026-11-14T05:45Z). | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED** (re-verified 2026-11-14T05:45Z). | `scripts/verify_campaign_evidence.py` |
| Retention probe (fresh this session) | **3894/6792 bars; 2898 missing; earliest 2026-04-19T18:00:00Z; 235 perps / 27 pass $5M / 27 probed; 1 unprobeable (KPEPE).** Probe generated 2026-11-14T05:40:40Z. Decays ~1h/hr. | `hyperliquid_retention_probe.json` (`5044968ace76461f58db24737732cc283eb5ace3540367004fcc64f38b4c9899`) |
| Raw fetch snapshot (latest gate-compliant) | Fetch-produced provenance for 044431 (26 symbol entries; 23 complete in aligned slice, ARB incomplete/gap, MATIC/FTM error). | `cache/hyperliquid_universe_snapshot_20261114T044431Z/provenance.json` (`83f074f28e2d8f2bff316bea6c424de2c6df86e295c69b54ab2095c4b4347543`) |
| Aligned partial slice (latest) | **23 complete symbols × 3891 bars (2026-04-19T21:00:00+00:00..2026-09-28T23:00:00+00:00)**, derived from real fetch cache with synthetic checks. | `cache/hyperliquid_universe_snapshot_20261114T044431Z_aligned_20260419T2100Z/provenance.json` (`27c5a56bae6bb51bb7b9cbaeedcd5bbe14b6c981803f1392cb631d9d8712eb91`) |
| Fresh aligned census (latest) | **23 symbols / 89493 bars / 11 RSI crashes / 0 confirmed signals.** | `hyperliquid_universe_snapshot_census_20261114T044431Z.json` (`e039f4fc5e031316cb576f3c4c0fc4147ad675e6b01ddbbe23aef1ea90badcfa`) |
| Partial campaign (latest, NOT_EVIDENCE) | `performance_evidence=false`, 0 trades/0 PnL (consistent with 0 signals). | `campaign_results_real_hyperliquid_universe_snapshot_20261114T044431Z.json` (`53ff9e1b57e1eb6b7b833af5d9c5fecd6736086b845aacc0b27212d6f9353d29`) |
| Gate-checked coverage | Points to 044431 probe/snapshot/census/campaign; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED`. | `hyperliquid_universe_coverage.json` (`5cc6686b6e9ad71d58667aa9c09dabe38a1d1c62fa5488c95ad2cc8df23d5e17`) |
| Phase O | artifact `2026-11-13T23:38:47Z`; 4 episodes / 11 events / 5 crash days; p=0.1500; CI [-4083.95, 24411.99]. | `episode_edge_okx_full.json` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). | `campaign_results_real_okx_full.json` |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

## 2. Commands executed this session (recorded, 2026-11-14T05:45:07Z)

- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30` → `perps=235 passing_gate=27 probed=27 max=3894 missing=2898 earliest=2026-04-19T18:00:00Z verdict FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` (2026-11-14T05:40:40Z; window unchanged vs prior aligned start).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **17/17 checks passed — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → **4/4 PASS — EVIDENCE VERIFIED**.
- Latest gate-compliant artifacts remain: fetch `cache/hyperliquid_universe_snapshot_20261114T044431Z/`, aligned slice `cache/hyperliquid_universe_snapshot_20261114T044431Z_aligned_20260419T2100Z/` (**23 complete symbols × 3891 bars, 2026-04-19T21:00:00+00:00..2026-09-28T23:00:00+00:00**), census `hyperliquid_universe_snapshot_census_20261114T044431Z.json` (**23/89493 bars/11 crashes/0 signals**), NOT_EVIDENCE campaign `campaign_results_real_hyperliquid_universe_snapshot_20261114T044431Z.json` (0 trades/0 PnL).

**Key results:** full 283d Hyperliquid still blocked by API retention (3894/6792, earliest 2026-04-19T18:00:00Z, probed 2026-11-14T05:40:40Z). Latest aligned partial snapshot shows **11 RSI crashes / 0 confirmed signals** — **0-trade, underpowered**; not performance evidence. OKX canonical/Phase M/N/O verdicts unchanged: **`underpowered` / not decision-grade**.

## 3. Current gate-relevant artifacts (hashes, verified 2026-11-14T05:45:07Z)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/hyperliquid_retention_probe.json` | `5044968ace76461f58db24737732cc283eb5ace3540367004fcc64f38b4c9899` | Re-run 2026-11-14T05:40:40Z (retention state unchanged). |
| `cache/hyperliquid_universe_snapshot_20261114T044431Z/provenance.json` | `83f074f28e2d8f2bff316bea6c424de2c6df86e295c69b54ab2095c4b4347543` | Raw fetch-produced provenance (044431). |
| `cache/hyperliquid_universe_snapshot_20261114T044431Z_aligned_20260419T2100Z/provenance.json` | `27c5a56bae6bb51bb7b9cbaeedcd5bbe14b6c981803f1392cb631d9d8712eb91` | Aligned 23-symbol complete slice with synthetic checks. |
| `research_state/hyperliquid_universe_snapshot_census_20261114T044431Z.json` | `e039f4fc5e031316cb576f3c4c0fc4147ad675e6b01ddbbe23aef1ea90badcfa` | 23 symbols / 89493 bars / 11 RSI crashes / 0 signals. |
| `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T044431Z.json` | `53ff9e1b57e1eb6b7b833af5d9c5fecd6736086b845aacc0b27212d6f9353d29` | NOT_EVIDENCE, performance_evidence=false, 0 trades. |
| `research_state/hyperliquid_universe_coverage.json` | `5cc6686b6e9ad71d58667aa9c09dabe38a1d1c62fa5488c95ad2cc8df23d5e17` | Gate-checked Phase Q artifact referencing above. |

## 4. Reproduction recipe (canonical + gate)

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 17/17 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
# EXPECT: 4/4 PASS — EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
# EXPECT: max_bars_returned < 6792, BLOCKED verdict (as of 2026-11-14T04:44:27Z probe)
```

## 5. Next focus campaign — status (2026-11-14T05:49:27Z)

**Gate/evidence re-verified 17/17 and 4/4 this session; probe re-run shows same retention state (no slide past aligned start yet).** Still missing / blocking decision-grade verdict: (a) continuous re-capture of decaying partial window (public API retention slides ~1h/hr; re-probe and re-fetch before next work), and/or (b) full 283-day Hyperliquid-native campaign (or operator-data block with exact probe counts) + full-portfolio placebo + episode-aware audit. Verdict remains **`underpowered` / not validated**. No planning-only turn is acceptable: execute probe→fetch→derive→census→campaign→coverage→gate first.

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
