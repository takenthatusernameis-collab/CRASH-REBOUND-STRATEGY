# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T09:48:20Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch/HEAD:** `main` @ `33b0bd7` (working tree includes session artifacts).
**Gate/evidence (re-verified this session):** `scripts/session_gate.py` **17/17 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation.

**Binding facts:** **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]** (canonical unchanged: 8 trades, net PnL 8141.29 / total PnL 9159.691934882958). **Latest Hyperliquid partial window (live probe re-captured this session 2026-11-14T09:36:12Z):** earliest served **2026-04-19T22:00:00Z**, **3890/6792 bars** (2902 missing), **235 perps / 27 pass $5M gate / 27 probed**, unprobeable/empty **['KPEPE']** (fetch also saw MATIC/FTM errors). Latest aligned snapshot: **24 complete symbols × 3886 bars** (2026-04-20T02:00:00Z..2026-09-28T23:00:00Z, raw `hyperliquid_universe_snapshot_20261114T094413Z` → aligned `..._aligned_20260420T0200Z`); census **11 RSI crashes / 0 confirmed signals / 93,264 bars**. Partial campaign **0 trades, 0 PnL, `performance_evidence=false`, `real_market_data=true`, fabricated=false** (`research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T094413Z.json`). **Full 283-day window is API-retention-blocked (decaying).** **Do not declare validated. Do not allocate capital.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T09:48:20Z)

**Priority (repo `CRASH-REBOUND-STRATEGY`):** Produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. OKX is cross-venue/underpowered and **never** Hyperliquid evidence. Full 283-day Hyperliquid is retention-blocked; partial window **decays continuously** and any NOT_EVIDENCE result is not validation.

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical)
Re-probe before any heavy work:
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
```
Refresh `research_state/hyperliquid_retention_probe.json`; record live `earliest_served_start_utc`, max/missing bars, probed/gate-pass counts, unprobeable/empty symbols. Produce a NEW artifact with `generated_at_utc >= session start`.

### BOTTLENECK REMOVAL — EXECUTE IN ORDER, NO EARLY STOP (planning-only turns prohibited)

**External:** Full 283-day Hyperliquid window blocked by API retention — only an operator-supplied **verified Hyperliquid-native archive** can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
**Statistical:** OKX underpowered (4 episodes, p=0.15, CI spans 0); no Hyperliquid-native performance evidence.
**Maintenance:** partial public-API window decays; re-probe/re-capture each session before heavy work.

1. **Probe retention NOW** (command above) → NEW `hyperliquid_retention_probe.json`.
2. **Fetch full qualifying served universe (partial snapshot):** set `<live-earliest>` from probe; use a new timestamped cache.
   ```bash
   TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
3. **Derive deterministic aligned complete slice:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
4. **Census over FULL aligned complete set (critical trap):** `run_hyperliquid_partial_census.py` **refuses without `--symbols`** — never run without full set.
   ```bash
   ALIGNED="research_state/cache/hyperliquid_universe_snapshot_${TS}_aligned_<start>"
   SYMS=$(python3 -c "import json;d=json.load(open('$ALIGNED/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir "$ALIGNED" --symbols $SYMS --output "research_state/hyperliquid_universe_snapshot_census_${TS}.json"
   ```
5. **Partial campaign artifact (NOT evidence):** flag is **`--allow-partial-not-evidence`** (hyphens; underscore form errors).
   ```bash
   PREFIX="research_state/campaign_results_real_hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest "$ALIGNED/provenance.json" --allow-partial-not-evidence --window-start <aligned_start> --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix "$PREFIX"
   ```
   Must remain `performance_evidence=false` / NOT_EVIDENCE.
6. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to reference new probe/snapshot/aligned/census/campaign artifacts, hashes, integer counts (symbols/bars/rsi_crash_events/confirmed_signals, num_trades/total_pnl), and verdict (`PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` unless facts change). Gate requires probe with perps/passing/probed, snapshot ≥12 complete + `complete_symbols`, census matching complete set, partial campaign `performance_evidence=false`, verdict containing `BLOCKED` and `UNDERPOWERED`.
7. **Verify chain before close:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
   ```
8. **If operator-supplied verified Hyperliquid-native 283-day archive arrives:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).
9. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0**.
10. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met (full window + ≥10 independent episodes with positive bootstrap CI + trade bootstrap CI excludes 0 + episode-block CI excludes 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05 + DD within mandate).

**NEXT FOCUS CAMPAIGN (unavoidable heavy work, every session):** (a) re-probe retention; (b) capture partial snapshot before it slides; (c) census over full aligned symbol set; (d) gated NOT_EVIDENCE campaign via `--allow-partial-not-evidence`; (e) verify 17/17 + 4/4. **No session may close without steps 1-7 complete and artifacts on disk.**

**ANTI-AVOIDANCE (hard):** execute 1-7 and produce real gate-relevant artifacts first; no planning-only turn; no validation/parity/capital-allocation claims; no per-event-null as portfolio test; no 10,000-sim theater (exact 165-subset enumeration); no second handoff; no fabricated data; never relax $5M gate; no "data unavailable" without live probe artifact + counts; never run census without `--symbols` on >12-symbol slice; flag is `--allow-partial-not-evidence` (hyphens).

---

## Verified state (2026-11-14T09:48:20Z)

| Check | Result | Evidence |
|---|---|---|
| Git | `main` @ `33b0bd7` | `git rev-parse --short HEAD` |
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present | `test -x` |
| Session gate | **17/17 — DONE** (this session) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (this session) | `scripts/verify_campaign_evidence.py` |
| Retention probe (this session) | 3890/6792 bars; 2902 missing; earliest 2026-04-19T22:00:00Z; 235 perps / 27 pass $5M / 27 probed; unprobeable/empty=['KPEPE']; 2026-11-14T09:36:12Z (**re-probe before next heavy work**) | `research_state/hyperliquid_retention_probe.json` |
| Latest raw snapshot | `hyperliquid_universe_snapshot_20261114T094413Z` (fetch-produced provenance; MATIC/FTM errors) | cache snapshot |
| Latest aligned slice | `hyperliquid_universe_snapshot_20261114T094413Z_aligned_20260420T0200Z` — 24 complete × 3886 bars (2026-04-20T02:00:00Z..2026-09-28T23:00:00Z) | aligned provenance |
| Latest aligned census (full set) | 24 symbols / 93,264 bars / 11 RSI crashes / 0 confirmed signals | `research_state/hyperliquid_universe_snapshot_census_20261114T094413Z.json` |
| Latest partial campaign | `performance_evidence=false` / NOT_EVIDENCE, 0 trades, 0.0 PnL, real_market_data=true | `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T094413Z.json` |
| Gate-checked coverage | points to 20261114T094413Z artifacts + hashes/counts; `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED` | `research_state/hyperliquid_universe_coverage.json` |
| Phase O (OKX, artifact 2026-11-13T23:38:47Z) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99] | `research_state/episode_edge_okx_full.json` |
| Canonical OKX baseline | 8 trades, total PnL **9159.691934882958** (unchanged, cross-venue) | `research_state/campaign_results_real_okx_full.json` |

---

## Bottlenecks (current)

1. **External/data block:** Full 283-day Hyperliquid window API-blocked (retention-limited). Only operator-supplied verified Hyperliquid-native archive can provide missing early history.
2. **Maintenance (decaying):** partial public-API window slides; re-probe and re-capture before heavy work each session.
3. **Statistical:** OKX evidence underpowered / few independent episodes; no Hyperliquid-native performance evidence yet.
4. **Resolved traps (do not reintroduce):** census requires `--symbols`; campaign flag is `--allow-partial-not-evidence` (hyphens); `derive_hyperliquid_aligned_slice.py` removes manual aligned-slice bottleneck; gate coverage requires integer aggregate counts for census/campaign.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- OKX data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54). Campaign: `research_state/campaign_results_real_okx_full.json` — 100k→109,159.69, net PnL 8141.29, 8 trades (4W/4L). **OKX cross-venue, not Hyperliquid evidence.**
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
```

## Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No duplicate sensitivity sweep while lock held.
- No per-event-null as portfolio test; no validation/capital-allocation claims (`underpowered`).
- Never run census without `--symbols` on >12-symbol slice. Never use `--allow-partial_not_evidence` (underscores).
- No additional handoff/status files. This file is the single durable handoff.

## Definition of done

Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI).
