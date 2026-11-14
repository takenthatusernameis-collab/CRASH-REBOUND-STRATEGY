# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T15:23:23Z
**Supersedes:** all earlier handoffs (incl. 2026-11-14T14:52:02Z). **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Priority:** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Branch/HEAD (session baseline):** working tree has uncommitted research artifacts from this session; **do not adopt/promote** any degraded 134000Z/144234Z/145453Z Hyperliquid chain. **Gate/evidence (this session):** `scripts/session_gate.py` **17/17 checks passed — DONE** (run after this handoff update); `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T15:23:23Z)

**Objective:** Produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the Hyperliquid data block with fresh reproducible artifacts. Full 283-day Hyperliquid is API-retention-blocked; partial public-API windows **decay continuously** and any NOT_EVIDENCE result is **not validation**. The retained partial Hyperliquid window produces **0 trades** — adjudication shows this is structurally consistent with implementation **same-bar rebound confirmation** (`confirm_rebound`) vs spec **next hourly open** after RSI crash close (11 volume-passing crash hours, 0 same-bar confirms, 5 next-bar confirms, 11 spec-literal next-open upper-bound opportunities). Next session must **re-probe, refresh chain if improved, and adjudicate/follow through** with real artifacts; do not claim validation.

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical, before any heavy work)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
```
Refresh `research_state/hyperliquid_retention_probe.json`. Record live `generated_at_utc` (must be >= session start), `earliest_served_start_utc`, `max_bars_returned`/`missing_early_bars_vs_expected`, `universe.perps_total/perps_passing_volume_gate/probed`, and `probe_summary.symbols_empty_or_error`. **No “data unavailable” without this live probe artifact + counts.**

**Latest live probe (2026-11-14T14:42:12Z, this session — superseded by your re-probe):** earliest served **2026-04-20T03:00:00Z/04:00:00Z boundary in summary**, **3884/6792 bars** max returned (2908 missing), **235 perps / 28 pass $5M gate / 28 probed**, unprobeable/error **['KPEPE']**; full 283-day window **API-retention-blocked** (`FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`).

### RETAINED CHAIN (do not replace with degraded data)
- Raw snapshot: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z/`
- **Retained aligned complete slice (KEEP):** `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` — **24 complete symbols × 3885 bars**, window **2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`provenance.json` authoritative).
- Latest census (retained chain): `research_state/hyperliquid_universe_snapshot_census_20261114T125249Z.json` — 24 symbols / 93,240 bars / **11 RSI crash events / 0 confirmed signals**.
- Latest partial campaign (retained chain): `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T125249Z.json` — **0 trades, 0.0 PnL, `performance_evidence=false`, `real_market_data=true`, `NOT_EVIDENCE_PARTIAL_UNIVERSE`**.
- Canonical signal funnel (retained): `research_state/hyperliquid_signal_funnel_20261114T145550Z.{json,md}` (reconciled this session on retained cache).
- Exploratory next-open adjudication (NOT evidence): `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T145550Z.{json,md}` — label `NOT_EVIDENCE_EXPLORATORY_FANOUT`, canonical baseline unchanged.
- Gate-checked coverage: `research_state/hyperliquid_universe_coverage.json` (updated 2026-11-14T15:02:30Z).

**Degraded/uncommitted artifacts — must NOT be adopted or pointed to by coverage:** `research_state/cache/hyperliquid_universe_snapshot_20261114T134000Z*`, `...20261114T144234Z*`, and **this-session `...20261114T145453Z` + `_aligned_20260420T0700Z` (24 complete but only 3881 bars from 2026-04-20T07:00:00Z, worse than retained)**. Adopt-or-keep recorded as **KEEP_RETAINED** in coverage. Any future degraded/smaller slice must be rejected and the comparison recorded.

### MANDATORY EXECUTION CAMPAIGN (execute in order, no early stop, no planning-only turn)
1. **Probe retention NOW** → NEW `hyperliquid_retention_probe.json`.
2. **Fetch full qualifying served universe (partial snapshot):** set `<live-earliest>` from probe; use a new timestamped cache.
   ```bash
   TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
3. **Derive deterministic aligned complete slice:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
4. **ADOPT-OR-KEEP CHECK (mandatory):** compare new aligned slice `summary.complete_symbols` count, bar count, and `aligned_window.start` against retained `..._20261114T104210Z_aligned_20260420T0300Z/provenance.json` (**24 complete × 3885 bars, start 2026-04-20T03:00:00Z**). **Adopt new slice ONLY if it has ≥3885 bars AND start ≤ 2026-04-20T03:00:00Z**; otherwise keep retained chain and record comparison in `research_state/hyperliquid_universe_coverage.json`. Never point coverage/census/campaign/funnel at a degraded chain.
5. **Census over FULL aligned complete set (critical trap):** `run_hyperliquid_partial_census.py` **refuses without `--symbols`** — never run without full set.
   ```bash
   ALIGNED="research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z"  # or adopted slice
   SYMS=$(python3 -c "import json;d=json.load(open('$ALIGNED/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir "$ALIGNED" --symbols $SYMS --output "research_state/hyperliquid_universe_snapshot_census_${TS}.json"
   ```
6. **Partial campaign artifact (NOT evidence):** flag is **`--allow-partial-not-evidence`** (hyphens).
   ```bash
   PREFIX="research_state/campaign_results_real_hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest "$ALIGNED/provenance.json" --allow-partial-not-evidence --window-start 2026-04-20T03:00:00Z --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix "$PREFIX"
   ```
   Must remain `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`.
7. **FUNNEL ADJUDICATION (heavy, mandatory):** re-run funnel on adopted chain and quantify the spec-literal entry path **without changing the canonical baseline**.
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/reconcile_hyperliquid_signal_funnel.py \
     --cache-dir "$ALIGNED" \
     --output "research_state/hyperliquid_signal_funnel_${TS}.json" \
     --md-output "research_state/hyperliquid_signal_funnel_${TS}.md"
   ```
   Produce/refresh an **exploratory** artifact (label `NOT_EVIDENCE_EXPLORATORY_FANOUT`) adjudicating entries when an RSI crash hour is followed by the **next hourly open** (spec-literal, no same-bar `confirm_rebound`) vs the implementation path. Record counts and structural finding. **Do not overwrite canonical campaign, do not claim validation, do not allocate capital.**
8. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to reference new probe/snapshot/aligned/census/campaign/funnel artifacts, SHA256 hashes, integer counts (symbols/bars/rsi_crash_events/confirmed_signals, num_trades/total_pnl), the adopt-or-keep decision, and verdict. Map probe fields correctly (`universe.perps_total/perps_passing_volume_gate/probed`, `probe_summary.*`). Gate requires probe w/ perps/passing/probed, snapshot ≥12 complete + `complete_symbols`, census matching complete set w/ sufficient bars, partial campaign `performance_evidence=false`.
9. **Verify chain before close:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
   ```
10. **If operator-supplied verified Hyperliquid-native 283-day archive arrives:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).
11. **Episode-aware audit for any new Hyperliquid run with trades/episodes:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0**.
12. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts, funnel finding, and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met.

**No session may close without steps 1–9 executed (or blocked only by the live probe proving no progress possible, with that probe artifact written), gates green, and artifacts on disk.** No planning-only turn. No simulation theater. No cross-venue relabeling.

---

## Verified state (as of 2026-11-14T15:23:23Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **17/17 — DONE** (this session) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (this session) | `scripts/verify_campaign_evidence.py` |
| Latest live retention probe (this session) | 3884/6792 bars; 2908 missing; earliest 2026-04-20T03:00/04:00Z (probe summary); 235 perps / 28 pass $5M / 28 probed; unprobeable/error=['KPEPE']; 2026-11-14T14:42:12Z | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / 11 RSI crashes / 0 confirmed signals | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign | `performance_evidence=false` / NOT_EVIDENCE_PARTIAL_UNIVERSE, 0 trades, 0.0 PnL | `campaign_results_real_hyperliquid_universe_snapshot_20261114T125249Z.json` |
| Canonical funnel (retained, this session) | 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → 0 generate_signal | `hyperliquid_signal_funnel_20261114T145550Z.{json,md}` |
| Exploratory next-open adjudication (NOT evidence) | spec-literal upper bound 11 next-open opportunities (all vol-passing crash hours) vs 0 canonical entries; structural same-bar filter | `hyperliquid_signal_funnel_exploratory_next_open_20261114T145550Z.{json,md}` |
| Gate-checked coverage | KEEP_RETAINED vs degraded 20261114T145453Z aligned (24×3881, 07:00Z); verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED` | `hyperliquid_universe_coverage.json` |
| Degraded uncommitted chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z/145453Z_aligned_20260420T0700Z (3881 bars) | `research_state/*{134000Z,144234Z,145453Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, total PnL 9159.691934882958 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current)

1. **External/data block (NOT agent-removable):** Full 283-day Hyperliquid window API-blocked by retention (3884/6792 bars served). Only an operator-supplied verified Hyperliquid-native archive can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. **Maintenance (decaying) — agent-removable each session:** partial public-API window slides; re-probe and re-capture **before** heavy work. Fresh fetch this session produced degraded aligned slice (3881/07:00Z) — **adopt-or-keep check mandatory**; retained 104210Z chain kept.
3. **Signal funnel (primary structural/statistical blocker) — agent-removable to adjudicate:** partial Hyperliquid yields **0 trades** because implementation requires **same-bar** `confirm_rebound`, while spec entry is **next hourly open after RSI crash close** (29→11 pass volume→0 same-bar confirm→5 next-bar confirm→0 generate_signal; 11 spec-literal upper-bound opportunities). Exploratory adjudication recorded (NOT evidence); no silent baseline change.
4. **Statistical — agent-mitigating, not removable:** OKX underpowered/few independent episodes; no Hyperliquid-native performance evidence.
5. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); derive script handles alignment; never replace retained 104210Z chain with degraded slices; coverage needs integer aggregate counts and correct probe field mapping.

## Canonical artifacts (do not re-acquire/re-run/overwrite)
- OKX: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol; manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`; universe `research_state/universe_okx_full_verified.json` (54); campaign `research_state/campaign_results_real_okx_full.json` (**cross-venue**).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence** (flat synthetic).
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).
- Coverage/probe/census/campaign/funnel artifacts under `research_state/` as referenced above.

## Reproduction
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/reconcile_hyperliquid_signal_funnel.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z \
  --output research_state/hyperliquid_signal_funnel_repro.json
```

## Hard prohibitions / anti-avoidance
- **Execute steps 1–9 and produce real artifacts first; no planning-only turn.**
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, or 145453Z chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0) + documented adjudication of partial-window entry funnel (same-bar confirmation vs spec next-open entry), with `underpowered` retained until every GO criterion is met.
