# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T06:52:27Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch/HEAD:** `main` @ `b989650` (working tree clean at handoff time).
**Gate/evidence (re-verified this session):** `scripts/session_gate.py` **17/17 — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T06:52:27Z)

**Inferred priority (repo name):** produce a **decision-grade Hyperliquid-native** verdict, or prove the data block with a reproducible live probe. **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** Binding constraint is **independent crash episodes**, not trades: 11 gate-passing events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. **Do not declare validated. Do not allocate capital.**

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical; window slides ~1h/hr)
The partial Hyperliquid public-API window decays ~1h/hr. Last recorded probe (2026-11-14T05:52:03Z, `research_state/hyperliquid_retention_probe.json`) showed `earliest_served_start_utc=2026-04-19T19:00:00Z`, max **3893/6792** bars, missing **2899**, perps **235** / **26** pass $5M gate / **26 probed**, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:2` (`MATIC`,`FTM`). **>1h has elapsed since that probe — the window has likely slid further and served bars are permanently lost from the public API path. Re-probe before any other heavy work.**

### BOTTLENECK REMOVAL — EXECUTE IN ORDER, NO EARLY STOP (no planning-only turn)
1. **Probe retention now:**
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30`
   → refresh `research_state/hyperliquid_retention_probe.json`; record live `earliest_served_start_utc`, max bars, missing bars, probed/gate-pass counts, unprobeable symbols.
2. **Fetch full qualifying served universe (partial snapshot):** pick `<live-earliest>` from probe; create new timestamped cache.
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir research_state/cache/hyperliquid_universe_snapshot_<UTC>/`
3. **Derive deterministic aligned complete slice** (with fetch provenance linkage):
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src research_state/cache/hyperliquid_universe_snapshot_<UTC>`
4. **Census over the FULL aligned complete set (critical script trap):** `scripts/run_hyperliquid_partial_census.py` defaults to a hardcoded 12-symbol list. **Never run it without `--symbols` on a >12-symbol slice** or it will silently undercount. Always:
   `SYMS=$(python3 -c "import json;d=json.load(open('research_state/cache/<aligned>/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")`
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir <aligned> --symbols $SYMS --output research_state/hyperliquid_universe_snapshot_census_<UTC>.json`
5. **Partial campaign artifact (NOT evidence):**
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest <aligned>/provenance.json --allow-partial-not-evidence --window-start <aligned_start> --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix research_state/campaign_results_real_hyperliquid_universe_snapshot_<UTC>`
   Must remain `performance_evidence=false` / NOT_EVIDENCE; never relabel partial as performance evidence.
6. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to point to the new probe/snapshot/aligned/census/campaign artifacts, hashes, counts, and status (`PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` unless facts change).
7. **Verify chain:**
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → expect **17/17 — DONE**
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → expect **4/4 — EVIDENCE VERIFIED**
8. **If operator-supplied verified Hyperliquid-native 283-day archive becomes available:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` to verify provenance/non-flat data, ingest to `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, and run episode-aware audit. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).
9. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **>2 independent crash episodes with positive mean PnL and episode-block bootstrap CI excluding 0**.
10. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met.

**ANTI-AVOIDANCE (hard):** execute step 1–7 and produce real gate-relevant artifacts first; no planning-only turn; no validation/parity claims; no per-event-null as portfolio test; no 10,000-sim theater (exact 165-subset enumeration standard); no second handoff; no fabricated data; never relax $5M gate; no "data unavailable" without live probe artifact + full-universe counts.

---

## Verified state (2026-11-14T06:52:27Z)

| Check | Result | Evidence |
|---|---|---|
| Git | `main` @ `b989650`, clean | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single: `./HANDOFF.md` | repo root scan |
| Env | `/tmp/crs-venv` present | `test -x` |
| Session gate | **17/17 — DONE** (re-verified 2026-11-14T06:52Z) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED** (re-verified 2026-11-14T06:52Z) | `scripts/verify_campaign_evidence.py` |
| Retention probe (last recorded) | 3893/6792 bars; 2899 missing; earliest 2026-04-19T19:00:00Z; 235 perps / 26 pass $5M / 26 probed; 2 unprobeable (MATIC,FTM); generated 2026-11-14T05:52:03Z (**likely slid since**) | `hyperliquid_retention_probe.json` (`b47396e9...`) |
| Latest gate-compliant raw snapshot | fetch-produced provenance 055219Z | `cache/hyperliquid_universe_snapshot_20261114T055219Z/provenance.json` (`4555805a...`) |
| Latest aligned partial slice | 23 complete symbols × 3890 bars (2026-04-19T22:00:00Z..2026-09-28T23:00:00Z), synthetic checks ok | `..._aligned_20260419T2200Z/provenance.json` (`a0f8ed90...`) |
| Latest aligned census (full set) | 23 symbols / 89470 bars / 11 RSI crashes / 0 confirmed signals | `hyperliquid_universe_snapshot_census_20261114T055219Z.json` (`261e440a...`) |
| Latest partial campaign | `performance_evidence=false` / NOT_EVIDENCE, 0 trades, 0 PnL (consistent with 0 signals) | `campaign_results_real_hyperliquid_universe_snapshot_20261114T055219Z.json` (`ca3c203a...`) |
| Gate-checked coverage | points to 055219Z artifacts; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` | `hyperliquid_universe_coverage.json` |
| Phase O (OKX) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99] | `episode_edge_okx_full.json` |
| Canonical OKX baseline | 8 trades, total PnL **9159.691934882958** (unchanged) | `campaign_results_real_okx_full.json` |

---

## Bottlenecks (current)

1. **External/data block:** Full 283-day Hyperliquid window API-blocked (retention-limited). Only operator-supplied verified Hyperliquid-native archive can provide missing early history (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. **Urgent maintenance (decaying):** partial public-API window slides ~1h/hr; delay permanently loses served bars — re-capture continuously.
3. **Known script trap:** `run_hyperliquid_partial_census.py` hardcoded 12-symbol default; always pass full complete-symbol `--symbols` from aligned provenance.
4. **Statistical:** OKX evidence underpowered / few independent episodes; no Hyperliquid-native performance evidence yet.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- OKX data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — 100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols. **OKX cross-venue, not Hyperliquid evidence.**
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30  # live retention/probe
```

---

## Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX campaign/J1/J2/K/L or overwrite of canonical artifacts (new stems only).
- No 10,000-sim theater; exact 165-subset enumeration is the placebo standard. No old 527s placebo path.
- No duplicate sensitivity sweep while `.sensitivity_sweep.lock` held.
- No per-event null presented as portfolio test; no validation/capital-allocation claims (`underpowered`).
- Never run `run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice.
- No additional handoff/status files. This file is the single durable handoff.

---

## Definition of done

Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target.
