# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T17:51:04Z
**Supersedes:** all earlier handoffs (incl. 2026-11-14T17:23:52Z, 16:42:01Z, 15:30:41Z, 15:24:40Z, 15:23:23Z, 14:52:02Z). **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the data block with fresh reproducible artifacts. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Baseline (this session):** branch `main` @ `53ae6f9`; one uncommitted file: `research_state/hyperliquid_universe_coverage.json` (probe block refreshed to 16:48:40Z artifact). `scripts/session_gate.py` **18/18 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED** (re-run 2026-11-14T17:19Z). Green gate = evidence-chain completeness, **not** profitability/validation.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T17:51:04Z)

**You are continuing a Hyperliquid crash-rebound research program. C1 (Episode Ledger & Power Closure) is COMPLETE: C1-T1 episode ledger (`episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z`, 2 episodes / 2 trades, NOT_APPLICABLE inference at n=2), C1-T2 power closure (`power_target_hyperliquid_20261114T172700Z`, ~809 days for E[N]=10, P(≥10 in 283d)≈0.0019, ~195 symbols needed), C1-T3 fragility (`fragility_hyperliquid_exploratory_next_open_20261114T172700Z`, 8 variants, BTC liquidation dominates, no variant rescues performance), C1-T4 data request update (`data_request_probe_update_20261114T172700Z`, probe 17:26:22Z, 3882/6792 bars, decay stabilized) are all on disk. Coverage refreshed 17:49:00Z (KEEP_RETAINED vs degraded chain). Verdict remains `UNDERPOWERED_NOT_EVIDENCE` and will stay so until a verified full 283-day Hyperliquid-native archive arrives. OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**IMMEDIATE NEXT (this session, non-negotiable):** C1-T5 closure — re-run Step 1 live probe + `scripts/session_gate.py` (expect 18/18) + `scripts/verify_campaign_evidence.py` (expect 4/4) against the new C1 artifacts, then re-timestamp this handoff. A session that closes without gates green has failed its acceptance gate.

**NEXT FOCUS CAMPAIGN — C2: PLACEBO & ARCHIVE READINESS (Hyperliquid-native).** This is the non-avoidable heavy work. Execute in order; every task must land a new-stem artifact on disk before the session closes. **No planning-only turn. No simulation theater. No cross-venue relabeling. No re-running an existing campaign on the same chain.**

- **C2-T1 — Full-portfolio placebo on exploratory path (heavy, mandatory).** Run the full-portfolio placebo for the spec-literal exploratory next-open campaign on the retained chain; record `research_state/placebo_portfolio_hyperliquid_exploratory_next_open_<TS>.{json,md}` labeled `NOT_EVIDENCE_PLACEBO`; reconcile with the memo's p<0.05 GO criterion. This was `NOT_RUN_THIS_SESSION` in C1-T1 and remains an open artifact gap.
- **C2-T2 — Blocker evidence refresh (mandatory).** Run Step 1 live probe; refresh `research_state/hyperliquid_retention_probe.json` with live `generated_at_utc` (>= session start), `earliest_served_start_utc`, `max_bars_returned`, `missing_early_bars_vs_expected`, `perps_total/perps_passing_volume_gate/probed`, `symbols_empty_or_error`; update `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` with fresh counts and decay trend; record `research_state/data_request_probe_update_<TS>.json` if numbers change. **No "data unavailable" without this live probe artifact + counts.**
- **C2-T3 — Operator archive ingestion readiness (mandatory).** Verify `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` runbook commands still match the repo (`scripts/`, bootstrapped env); prepare the ingest/derive/verified-universe pipeline so a verified 283-day Hyperliquid-native archive can be ingested and the canonical full-window campaign run immediately on arrival. Record `research_state/archive_readiness_<TS>.json`.
- **C2-T4 — Close the chain (mandatory).** Update `research_state/hyperliquid_universe_coverage.json` with C2 artifacts and integer counts, then run the gate block:
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py     # Step 1 first
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                  # expect 18/18
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py      # expect 4/4
```
Then update this handoff with the new timestamp and C2 artifact names.

**Latest live probe (2026-11-14T17:26:22Z):** earliest served **2026-04-20T06:00:00Z**, **3882/6792** bars (2910 missing), **235 perps / 32 pass $5M gate / 32 probed**, unprobeable/error **['KPEPE']**; full 283-day window **API-retention-blocked** (`FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`). Decay trend this session: 3884 from 04:00Z (15:28Z) → 3883 from 05:00Z (16:19Z) → 3882 from 06:00Z (16:48Z) → 3882 from 06:00Z (17:26Z, stabilized).

**No session may close without: Step 1 live probe on disk, C2-T1..T4 artifacts on disk (new stems), C2-T4 coverage refresh + gates green (18/18 and 4/4), and this handoff re-timestamped. If the live probe shows no data progress is possible, the session must still produce C2-T1..T4.**

### STEP 2 — ADOPT-OR-KEEP (bottleneck removed — do not churn)
The retained aligned chain is **24 complete symbols × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json`). The live probe serves strictly less.

- **Do NOT run a fresh full-universe fetch unless the probe shows `earliest_served_start_utc <= 2026-04-20T03:00:00Z` AND `max_bars_returned >= 3885`.** Three consecutive probes this session were worse than retained; re-fetching is now a known dead end. If (and only if) the probe improves, follow the fetch/derive/adopt commands in the prior handoff revision (git `53ae6f9`), adopt only if ≥3885 bars AND start ≤ 2026-04-20T03:00:00Z, else record `KEEP_RETAINED` in `research_state/hyperliquid_universe_coverage.json`. Never point coverage/census/campaign/funnel at a degraded chain.
- **This session:** C1 already complete (T1-T4 on disk, coverage KEEP_RETAINED 17:49:00Z). No fresh fetch warranted; keep `..._20261114T104210Z_aligned_20260420T0300Z` and record `KEEP_RETAINED`. C1-T5 gate re-run + handoff re-timestamp is the remaining C1 step; then proceed to C2.

### STEP 3 — SPEC-LITERAL NEXT-OPEN ADJUDICATION (**COMPLETED 2026-11-14T16:22:12Z — do not re-run**)
**Result artifact:** `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` (+ `_metrics.json`/`.csv`) and funnel `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T162212Z.{json,md}`.
- **Funnel:** 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → **8 generate_signal (spec-literal)** → **2 real-engine trades** (BCH time_exit +$559, BTC liquidated -$3,230; 6 signals blocked by ETH hedge/120% cap/ETH availability).
- **PnL/Metrics:** total PnL -$2,671, max drawdown -3.2%, win rate 50%, Sharpe -0.70, monthly: May +$559, Jun -$3,230.
- **Labels:** `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`, `research_status=NOT_EVIDENCE_EXPLORATORY_FANOUT`. Canonical baseline unchanged. **Do not overwrite the canonical campaign, do not claim validation, do not allocate capital, and do not re-run this campaign on the same chain (deterministic — it wastes the session).**

### STEP 4 — EPISODE-AWARE AUDIT (partially done; close via C1-T1)
Canonical partial window audit is recorded NOT_APPLICABLE (`research_state/episode_edge_hyperliquid_partial.{json,md}`, 2026-11-14T12:56Z, 0 trades). The exploratory 2-trade episode ledger is still an **open artifact gap**: produce it via **C1-T1** (expect `NOT_APPLICABLE` for bootstrap/permutation at n=2 with explicit reasons). **Do not promote to evidence until ≥10 independent crash episodes with a positive episode-level bootstrap CI excluding 0.** The retained window has only 4 crash days total; expect `underpowered`.

### STEP 5 — POWER / SAMPLE-SIZE TARGET AND DECISION MEMO (target present; close via C1-T2)
`research_state/decision_memo_okx_full.md` (updated 2026-11-14T16:26Z) already contains the fresh probe facts, the spec-literal vs same-bar structural finding, the exploratory result (2 trades, -$2,671), the episode count (2/4 crash days produced trades), and the binding power target (**≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05**). The remaining heavy work is the quantitative power closure (**C1-T2**): base-rate → calendar-time/symbol requirement and CI-width projection. Keep verdict **`underpowered`** until every GO criterion is met.

### STEP 6 — REFRESH COVERAGE, THEN VERIFY THE CHAIN
Coverage was refreshed 2026-11-14T17:18:30Z to the 16:48:40Z probe (KEEP_RETAINED; gates re-run green 17:19Z). The next session must refresh it again with its own fresh probe + C1 artifacts, then run the gate block in C1-T5. Update this handoff with the new timestamp and C1 artifact names.

### STEP 7 — ONLY PATH TO FULL EVIDENCE: OPERATOR ARCHIVE
If an operator-supplied verified Hyperliquid-native 283-day archive arrives, follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, full-portfolio placebo, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder). See **C1-T4** for the required request update.

**No session may close without: Step 1 live probe on disk, C2-T1..T4 artifacts on disk (new stems), C2-T4 coverage refresh + gates green (18/18 and 4/4), and this handoff re-timestamped. If the live probe shows no data progress is possible, the session must still produce C2-T1..T4.**

---

## Verified state (as of 2026-11-14T17:20:21Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **18/18 — DONE** (re-run 17:19Z) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (re-run 17:19Z) | `scripts/verify_campaign_evidence.py` |
| Latest live retention probe | **2026-11-14T17:26:22Z**; 3882/6792 bars; 2910 missing; earliest 2026-04-20T06:00Z; 235 perps / 32 pass $5M / 32 probed; unprobeable/error=['KPEPE']; sha256 `cdaa0c6a603cede77b7316565586d86eee3da50e355667f1c4911e4313d210db` | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / **11 RSI crashes / 0 confirmed signals**; 4 distinct crash days (2026-05-28, 06-02, 06-05, 06-24) | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign (canonical) | `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`, 0 trades, 0.0 PnL; sha256 `225887ef4d11ffb4e158fbe15e990ec2c0c488250ae877152ceec01c1d7ec1fa` | `campaign_results_real_hyperliquid_universe_snapshot_20261114T151710Z.json` |
| Canonical funnel (retained) | 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → 0 generate_signal; sha256 `f746a83f1fe99f34734e1342612fce269b83c8e4d1cd77a4334796dd12ffab72` | `hyperliquid_signal_funnel_20261114T151710Z.{json,md}` |
| **Exploratory next-open adjudication (NOT evidence)** | **COMPLETED 2026-11-14T16:22:12Z: 2 trades (BCH +559, BTC -3230), total PnL -$2,671, max DD -3.2%, 8 signals → 2 trades (portfolio constraints); label `NOT_EVIDENCE_EXPLORATORY_FANOUT`** | `campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json`, `hyperliquid_signal_funnel_exploratory_next_open_20261114T162212Z.{json,md}` |
| Exploratory episode audit (canonical partial) | `NOT_APPLICABLE_NO_EPISODES` (0 trades) — exploratory 2-trade ledger recorded via C1-T1 (`episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z.{json,md}`) | `episode_edge_hyperliquid_partial.{json,md}` |
| Gate-checked coverage | KEEP_RETAINED vs degraded 145453Z/151710Z; verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED`; probe block = 17:26:22Z | `hyperliquid_universe_coverage.json` |
| Degraded chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z, 145453Z_aligned_20260420T0700Z (3881 bars), 151710Z aligned (26×2127 bars, start 2026-07-02T09:00Z) | `research_state/*{134000Z,144234Z,145453Z,151710Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, total PnL 9159.691934882958 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current) — what is removable vs not

1. **External/data block (NOT agent-removable):** full 283-day Hyperliquid window API-blocked by retention (3882/6792 bars at 17:26Z and stabilized). Only an operator-supplied verified Hyperliquid-native archive can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`, escalation = C2-T2/C2-T3).
2. **Retention decay / wasted re-fetch (REMOVED):** four probes this session all strictly worse than or equal to the retained chain; the fetch-unless-improved rule (Step 2) stops the per-session churn. Probing remains mandatory; fetching does not.
3. **C1 campaign (COMPLETED):** C1-T1 episode ledger, C1-T2 power closure, C1-T3 fragility (8 variants), C1-T4 data request update all on disk (17:27:00Z–17:48:16Z); coverage refreshed 17:49:00Z (KEEP_RETAINED). C1-T5 gate re-run + handoff re-timestamp is the only remaining C1 step — do not redo C1-T1..T4.
4. **Exploratory re-run churn (REMOVED this handoff):** the spec-literal result is deterministic on the retained chain; re-running it (or the canonical campaign) without a new chain is forbidden. New engine work must go through C2 bounded variants only (C2-T1 placebo is on the exploratory path but is a distinct artifact, not a re-run).
5. **Structural 0-trade funnel (RESOLVED):** same-bar `confirm_rebound` vs spec next-hourly-open entry is quantified: 11 volume-passing crashes → 0 same-bar confirms → 8 spec-literal signals → 2 trades (portfolio constraints). Canonical path stays 0-trade by default (correct); exploratory path is opt-in only.
6. **Statistical (agent-mitigating, not removable):** retained window has only **4 independent crash episodes**; even the spec-literal path is underpowered (2 trades from 2 episodes). C1-T1/T2 closed the bookkeeping and power math; C2-T1 placebo adds the missing inference artifact. Do not promote to evidence.
7. **Episode-audit ambiguity (REMOVED):** n<10 episode audits recorded as `NOT_APPLICABLE` with explicit reasons in C1-T1 — this blocks both fabricated p-values and silent deferral.
8. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with a degraded slice; coverage needs integer aggregate counts and correct probe field mapping.

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
- **Execute Step 1 and C2-T1..T4 and produce real new-stem artifacts first; no planning-only turn, no status-only turn.** A session that closes without the C2 artifacts + gates green has failed its heavy-work acceptance gate.
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater (C1-T3 is capped at 8 configs). No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes; the spec-literal path must stay opt-in/default-off.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, 145453Z, or 151710Z aligned chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **18/18 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0), with `underpowered` retained until every GO criterion is met. **Next session's done:** Step 1 probe + C2-T1..T4 artifacts on disk + coverage refresh + gates 18/18 and 4/4 green + this handoff re-timestamped.

(End of file - total 131 lines)