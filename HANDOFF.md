# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T15:29:00Z
**Supersedes:** all earlier handoffs (incl. 2026-11-14T15:24:40Z, 15:23:23Z, 14:52:02Z). **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (from the repo name):** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the data block with fresh reproducible artifacts. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Baseline (this session):** branch `main` @ `ad923d5`; working tree clean. `scripts/session_gate.py` **17/17 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T15:29:00Z)

**You are continuing a Hyperliquid crash-rebound research program. The two real blockers are (a) a decaying public-API retention window that cannot serve the 283-day spec window, and (b) a structural 0-trade funnel: the implementation requires a same-bar `confirm_rebound` candle, while the spec enters at the next hourly open after the RSI crash close. Do not spend the session re-running the same partial campaign; that is the inefficiency this handoff removes. Do the heavy work below and leave a real artifact.**

**Objective:** Either produce a decision-grade Hyperliquid-native crash-rebound result, or prove the data block with fresh artifacts. Because the retained partial window contains only **4 distinct crash days (2026-05-28, 2026-06-02, 2026-06-05, 2026-06-24) = 4 independent crash episodes**, any partial result remains **underpowered**; the value of this session is a **spec-literal next-open adjudication with real trades/PnL**, an episode-aware audit, and a power-based stop/go target — not a repeated 0-trade run.

**Execute in order. No planning-only turn. No simulation theater. No cross-venue relabeling.**

### STEP 1 — LIVE PROBE (fast, mandatory, before any heavy work)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
```
Refresh `research_state/hyperliquid_retention_probe.json`. Record live `generated_at_utc` (>= session start), `earliest_served_start_utc`, `max_bars_returned` / `missing_early_bars_vs_expected`, `universe.perps_total/perps_passing_volume_gate/probed`, and `probe_summary.symbols_empty_or_error`. **No “data unavailable” without this live probe artifact + counts.**

**Latest live probe (this session, 2026-11-14T15:28:52Z):** earliest served **2026-04-20T04:00:00Z**, **3884/6792** bars (2908 missing), **235 perps / 28 pass $5M gate / 28 probed**, unprobeable/error **['KPEPE']**; full 283-day window **API-retention-blocked** (`FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`).

### STEP 2 — ADOPT-OR-KEEP, AND DO NOT RE-FETCH A DEGRADED SLICE (bottleneck removed)
The retained aligned chain is **24 complete symbols × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json`). The live probe serves at most **3884 bars from 2026-04-20T04:00:00Z**, which is strictly worse.

- **Do NOT run a fresh full-universe fetch this session unless the probe shows `earliest_served_start_utc <= 2026-04-20T03:00:00Z` AND `max_bars_returned >= 3885`.** Re-fetching a decaying window only produces another degraded slice and wastes the session; every prior re-fetch this session was worse than retained.
- If (and only if) the probe improves, fetch + derive and apply the adopt rule:
  ```bash
  TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
  PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
  PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
  ```
  Adopt the new slice **only if ≥3885 bars AND start ≤ 2026-04-20T03:00:00Z**; otherwise keep retained and record the comparison in `research_state/hyperliquid_universe_coverage.json`. Never point coverage/census/campaign/funnel at a degraded chain.
- **This session:** no fresh fetch is warranted; keep `..._20261114T104210Z_aligned_20260420T0300Z` and record `KEEP_RETAINED` (probe is strictly worse).

### STEP 3 — HEAVY WORK: SPEC-LITERAL NEXT-OPEN ADJUDICATION (mandatory, the point of this session)
The canonical path cannot trade the retained window: `generate_signal` calls `confirm_rebound` on the **same bar** (`src/strategy/crash_rebound.py:387`) before entry, while `research_state/strategy_spec.md:16-17` says “21-hour RSI closes below 20” → **“Buy at next hourly open.”** Funnel on the retained chain: 29 RSI<20 hours → 11 pass $5M volume → **0 same-bar confirm** → 5 next-bar confirm → **0 generate_signal**. The 0-trade result is structural, not a scanner bug.

Build and run an **exploratory** adjudication that enters at the **next hourly open after every volume-passing RSI crash hour**, without the same-bar confirmation gate, using the real engine/portfolio constraints, fees and risk limits, on the retained chain:
- Implement it as an **opt-in, default-off** path (e.g. a `entry_spec_literal_next_open: bool = False` config flag that bypasses only `confirm_rebound` when explicitly enabled, or a separate exploratory harness that truncates candles at crash+1 and calls the engine with the flag on). Add tests. **Do not change the canonical default path.**
- Output (new timestamped stem): `research_state/campaign_results_real_hyperliquid_exploratory_next_open_${TS}.json` (+ `_metrics.json`/`.csv`) with `num_trades`, `total_pnl`, win rate, max drawdown, monthly breakdown; and refresh `research_state/hyperliquid_signal_funnel_exploratory_next_open_${TS}.{json,md}`.
- Labels: `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`, `research_status=NOT_EVIDENCE_EXPLORATORY_FANOUT`. **Do not overwrite the canonical campaign, do not change the canonical baseline, do not claim validation, do not allocate capital.**
- **Acceptance:** the artifact exists and reports trades/PnL (0 is allowed, but the structural reason must be quantified). A prose note is not acceptance.

### STEP 4 — EPISODE-AWARE AUDIT (heavy, mandatory if the exploratory run produces trades)
Independent crash episodes/distinct crash days (not trades); episode-block bootstrap; if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. **Do not promote to evidence until ≥10 independent crash episodes with a positive episode-level bootstrap CI excluding 0.** The retained window has only 4 crash days, so expect `underpowered`.

### STEP 5 — POWER / SAMPLE-SIZE TARGET AND DECISION MEMO
Update `research_state/decision_memo_okx_full.md` with: the fresh probe facts, the spec-literal vs same-bar structural finding, the exploratory result (or its absence), the episode count, and a **power-based sample-size target** (trades / symbols / independent episodes needed). Keep verdict **`underpowered`** until every GO criterion is met.

### STEP 6 — REFRESH COVERAGE, THEN VERIFY THE CHAIN
Update `research_state/hyperliquid_universe_coverage.json` to reference the fresh probe, the adopt-or-keep decision, the exploratory adjudication, and integer counts (`symbols/bars/rsi_crash_events/confirmed_signals`, `num_trades/total_pnl`). Then:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
```
Then update this handoff with the new timestamp and the exploratory artifact reference.

### STEP 7 — ONLY PATH TO FULL EVIDENCE: OPERATOR ARCHIVE
If an operator-supplied verified Hyperliquid-native 283-day archive arrives, follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, full-portfolio placebo, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).

**No session may close without Steps 1–6 executed and artifacts on disk, gates green. The heavy-work acceptance gate is Step 3 + Step 4. If the live probe proves no data progress is possible, the session must still produce the Step 3 spec-literal adjudication on the retained chain.**

---

## Verified state (as of 2026-11-14T15:29:00Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **17/17 — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| Latest live retention probe | **2026-11-14T15:28:52Z**; 3884/6792 bars; 2908 missing; earliest 2026-04-20T04:00Z; 235 perps / 28 pass $5M / 28 probed; unprobeable/error=['KPEPE']; sha256 `5816532733d7ce78d73b0b44a4975676b3a677d88306cc056e528c0f241ce8d2` | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / **11 RSI crashes / 0 confirmed signals**; 4 distinct crash days (2026-05-28, 06-02, 06-05, 06-24) | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign | `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`, 0 trades, 0.0 PnL; sha256 `225887ef4d11ffb4e158fbe15e990ec2c0c488250ae877152ceec01c1d7ec1fa` | `campaign_results_real_hyperliquid_universe_snapshot_20261114T151710Z.json` |
| Canonical funnel (retained) | 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → 0 generate_signal; sha256 `f746a83f1fe99f34734e1342612fce269b83c8e4d1cd77a4334796dd12ffab72` | `hyperliquid_signal_funnel_20261114T151710Z.{json,md}` |
| Exploratory next-open adjudication (NOT evidence) | spec-literal upper bound 11 next-open opportunities (all vol-passing crash hours) vs 0 canonical entries; structural same-bar filter | `hyperliquid_signal_funnel_exploratory_next_open_20261114T145550Z.{json,md}` |
| Gate-checked coverage | KEEP_RETAINED vs degraded 20261114T145453Z/151710Z aligned; verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED` | `hyperliquid_universe_coverage.json` |
| Degraded chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z/145453Z_aligned_20260420T0700Z (3881 bars), 151710Z aligned (26×2127 bars, start 2026-07-02T09:00Z) | `research_state/*{134000Z,144234Z,145453Z,151710Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, total PnL 9159.691934882958 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current) — what is removable vs not

1. **External/data block (NOT agent-removable):** full 283-day Hyperliquid window API-blocked by retention (3884/6792 bars served). Only an operator-supplied verified Hyperliquid-native archive can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. **Retention decay / wasted re-fetch (REMOVED this handoff):** the partial window slides; re-fetching every session only produces a smaller/degraded slice (this session's 145453Z = 3881 bars, 151710Z aligned = 2127 bars). New rule: probe first, and **skip the fetch unless the probe improves** over the retained chain. This stops the per-session churn.
3. **Structural 0-trade funnel (agent-removable — the primary blocker):** same-bar `confirm_rebound` vs spec next-hourly-open entry. The exploratory adjudication (Step 3) removes it by measuring the spec-literal path with real engine constraints; the canonical baseline stays unchanged. The prior funnel counts (29→11→0→5→0) are now a known structural fact, not a new mystery.
4. **Statistical (agent-mitigating, not removable):** the retained partial window has only **4 independent crash episodes**; even the spec-literal path is underpowered. Record the power target; do not promote to evidence.
5. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with a degraded slice; coverage needs integer aggregate counts and correct probe field mapping.

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
- **Execute Steps 1–6 and produce real artifacts first; no planning-only turn.** Step 3 (spec-literal adjudication) + Step 4 (episode audit) are the non-negotiable heavy work.
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes; the spec-literal path must be opt-in/default-off.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, 145453Z, or 151710Z aligned chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0) + **the Step 3 spec-literal next-open adjudication artifact and Step 4 episode audit**, with `underpowered` retained until every GO criterion is met.