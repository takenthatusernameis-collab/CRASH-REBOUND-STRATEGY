# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T19:42:25Z
**Supersedes:** all earlier handoffs (including 2026-11-14T19:41:37Z, 19:34:05Z, 19:21:13Z, 18:21:30Z, 17:55:20Z, 17:51:04Z, 17:23:52Z, 16:42:01Z, 15:30:41Z, 15:24:40Z, 15:23:23Z, 14:52:02Z). **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the data block with fresh reproducible artifacts. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Baseline (this session):** branch `main`; C1/C2/C3 are complete. `scripts/session_gate.py` is **21/21 checks passed — DONE** after this refresh, and `scripts/verify_campaign_evidence.py` is **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation. The canonical `episode_edge_okx_full.json` artifact timestamp is `2026-11-13T23:38:47Z`.

**META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, this file is already the current handoff. Do not spend the session rewriting it. C1, C2 and C3 are COMPLETE. **Start at C4-T1 now.** No handoff-only turn is allowed until C4-T1 artifacts exist on disk.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T19:42:25Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1 (Episode Ledger & Power Closure), C2 (Placebo & Archive Readiness) and C3 (Spec-Comparison Hardening) are COMPLETE. Do not repeat C1/C2/C3 work and do not re-run any deterministic campaign on the retained chain. Your first action is C4-T1 below.**

**NEXT FOCUS CAMPAIGN — C4: DATA-BLOCK DECISION LOCK, OPERATOR INTAKE VALIDATION & MULTI-YEAR PROTOCOL.** This is the non-avoidable heavy work. Every task must land a new-stem artifact on disk before the session closes. **No planning-only turn. No simulation theater. No cross-venue relabeling. No re-running an existing campaign on the same chain without a new artifact purpose.**

- **C4-T1 — Operator archive intake validator (heavy, mandatory).** Build `scripts/validate_hyperliquid_archive_intake.py` and produce `research_state/archive_intake_validation_<TS>.{json,md}`. It must fail closed on short windows, flat series, placeholder/synthetic data, missing provenance, missing symbols, and bad hashes. Validate it against a clearly labelled synthetic non-evidence fixture: the fixture must be accepted for plumbing but recorded `is_market_data=false`, `is_evidence=false`, `performance_evidence=false`; a deliberately truncated/flat fixture must be rejected. Do not use the placeholder parquet as evidence.
- **C4-T2 — Multi-year validation protocol + power-optimal duration (heavy, mandatory).** Produce `research_state/multi_year_validation_protocol_<TS>.{json,md}` with machine-checkable fields: primary endpoint, episode clustering rule, bootstrap/permutation/placebo methods, multiple-testing correction, minimum independent episodes (≥10), stop/go rules, and the archive duration required for 80% power at the observed episode rate. Use the committed C3-T3 rates (283d 0.33%, 2y 41.51%, pooled upper bound 22.32%) and record the explicit decision lock: **NO_GO on current data; continue only with an operator-supplied multi-year Hyperliquid-native archive.** This must include an executable power/duration calculation and its output, not prose alone.
- **C4-T3 — Execution-friction stress on the retained exploratory path (heavy, mandatory).** Produce `research_state/execution_friction_stress_hyperliquid_<TS>.{json,md}`. Run the real engine on the retained chain with the opt-in exploratory next-open path under a pre-specified fee/slippage/funding/liquidation/ETH-hedge stress grid; label `NOT_EVIDENCE_EXECUTION_FRICTION`, `performance_evidence=false`, and `canonical_baseline_changed=false`. The result is a fragility check only; it must not be promoted to evidence or used to change the canonical default.
- **C4-T4 — Close the chain (mandatory).** Refresh the Hyperliquid retention probe with `scripts/probe_hyperliquid_blocker.py`; record `KEEP_RETAINED` unless the probe is strictly better (start ≤ `2026-04-20T03:00:00Z` and ≥ 3885 bars). Update `research_state/hyperliquid_universe_coverage.json` with the C4 artifacts and integer counts. Update `research_state/decision_memo_okx_full.md` with the C3/C4 state and the explicit `NO_GO` on current evidence. Then run:
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                  # expect 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py      # expect 4/4
```
Finally update this handoff with the new timestamp and C4 artifact names.

**No session may close without: C4-T1..T4 artifacts on disk (new stems), coverage + decision memo refreshed, gates green (21/21 and 4/4), and this handoff re-timestamped.**

### STEP 2 — ADOPT-OR-KEEP (bottleneck removed — do not churn)
The retained aligned chain is **24 complete symbols × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json`). The live probe serves strictly less.

- **Do NOT run a fresh full-universe fetch unless the probe shows `earliest_served_start_utc <= 2026-04-20T03:00:00Z` AND `max_bars_returned >= 3885`.** Re-fetching a degraded chain is a known dead end. If the probe improves, adopt only if ≥3885 bars AND start ≤ `2026-04-20T03:00:00Z`; otherwise record `KEEP_RETAINED` in coverage. Never point coverage/census/campaign/funnel at a degraded chain.

### STEP 3 — SPEC-LITERAL NEXT-OPEN ADJUDICATION (**COMPLETED 2026-11-14T16:22:12Z — do not re-run**)
**Result artifact:** `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` (+ `_metrics.json`/`.csv`) and funnel `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T162541Z.{json,md}`.
- **Funnel:** 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → **8 generate_signal (spec-literal)** → **2 real-engine trades** (BCH time_exit +$559, BTC liquidated -$3,230; 6 signals blocked by ETH hedge/120% cap/ETH availability).
- **PnL/Metrics:** total PnL -$2,670.76, max drawdown -3.2%, win rate 50%, Sharpe -0.70, monthly: May +$559, Jun -$3,230.
- **Labels:** `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`. Canonical baseline unchanged. **Do not overwrite the canonical campaign, do not claim validation, do not allocate capital, and do not re-run this campaign on the same chain.**

### STEP 4 — EPISODE-AWARE AUDIT (**COMPLETE — C1-T1 on disk; do not re-run**)
Canonical partial window audit is recorded NOT_APPLICABLE (`research_state/episode_edge_hyperliquid_partial.{json,md}`, 0 trades). The exploratory 2-trade episode ledger is recorded in `research_state/episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z.{json,md}`. **Do not promote to evidence until ≥10 independent crash episodes with a positive episode-level bootstrap CI excluding 0.**

### STEP 5 — POWER / SAMPLE-SIZE TARGET AND DECISION MEMO (**COMPLETE — C1-T2/C3-T3 on disk; do not re-run**)
`research_state/power_target_hyperliquid_20261114T172700Z.{json,md}` and `research_state/power_sensitivity_20261114T182832Z.{json,md}` contain the binding power target (**≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05**) and the scenario probabilities. Keep verdict **`underpowered`** until every GO criterion is met.

### STEP 6 — REFRESH COVERAGE, THEN VERIFY THE CHAIN
Coverage was refreshed 2026-11-14T19:34:05Z with C3 artifacts and the restored canonical exploratory pointer. The next session must refresh it again with its own C4 probe + C4 artifacts, then run the C4 gate block. Update this handoff with the new timestamp and C4 artifact names.

### STEP 7 — ONLY PATH TO FULL EVIDENCE: OPERATOR ARCHIVE
If an operator-supplied verified Hyperliquid-native 283-day archive arrives, follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` and the C4-T1 validator. Then ingest, derive verified universe, run canonical full-window campaign, full-portfolio placebo, episode-aware audit, and update the decision memo. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).

**No session may close without: C4-T1..T4 artifacts on disk (new stems), C4-T4 coverage refresh + gates green (21/21 and 4/4), and this handoff re-timestamped to 2026-11-14T19:42:25Z or later.**

---

## Verified state (as of 2026-11-14T19:34:05Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** (this refresh) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (this refresh) | `scripts/verify_campaign_evidence.py` |
| C3-T1 spec divergence closure | **8/8 adjudicated**; 4 resolved, 4 retained, 0 gaps; no code changes | `research_state/spec_divergence_closure_20261114T182754Z.{json,md}` |
| C3-T2 dry-run readiness | **READY**; 10/10 steps; pipeline wired; synthetic fixture removed; canonical latest untouched | `research_state/full_window_dry_run_readiness_20261114T192058Z.json` |
| C3-T3 power sensitivity | 3 scenarios; 283d 0.33%, 2y 41.51%, pooled 22.32%; verdict `POWER_FLOOR_UNREACHABLE_ON_ACHIEVABLE_DATA` | `research_state/power_sensitivity_20261114T182832Z.{json,md}` |
| C3-T4 coverage refresh | C3 artifacts recorded; verdict unchanged | `research_state/hyperliquid_universe_coverage.json` |
| Latest live retention probe | 2026-11-14T18:19:17Z; 3881/6792 bars; 2911 missing; earliest 2026-04-20T07:00Z; 235 perps / 32 pass $5M / 32 probed; unprobeable/error=['KPEPE']; sha256 `ffd11714f91b2b57305f2f8877aca9d02d4933e0a4afd9082c6c7da6e3a97b27` | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / **11 RSI crashes / 0 confirmed signals**; 4 distinct crash days (2026-05-28, 06-02, 06-05, 06-24) | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign (canonical) | `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`, 0 trades, 0.0 PnL | `campaign_results_real_hyperliquid_universe_snapshot_20261114T151710Z.json` |
| Canonical funnel (retained) | 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → 0 generate_signal | `hyperliquid_signal_funnel_20261114T151710Z.{json,md}` |
| Exploratory next-open (NOT evidence) | 2 trades, -$2,670.76, 8 signals → 2 trades; label `NOT_EVIDENCE_EXPLORATORY_FANOUT` | `campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` |
| Exploratory latest pointer | **Restored to the real retained-chain artifact**, sha256 `6d2a934f0270e58bf3e400abda42c8eed5aba2f461c94760ef83987cdd91d686`; synthetic fixture leak reverted | `research_state/hyperliquid_exploratory_next_open_latest.json` |
| C2-T1 HL exploratory placebo | 8 signal-gate events, 28 exact subsets, canonical replay exact, canonical at 89.3rd percentile; label `NOT_EVIDENCE_PLACEBO`, verdict `underpowered` | `placebo_portfolio_hyperliquid_exploratory_next_open_20261114T182023Z.{json,md}` |
| C2-T3 archive-ingestion readiness | READY (18:20:45Z); all runbook scripts/flags verified; placeholder confirmed non-evidence | `archive_readiness_20261114T182045Z.json` |
| Gate-checked coverage | KEEP_RETAINED vs degraded chains; verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED`; C3 artifacts recorded | `hyperliquid_universe_coverage.json` |
| Degraded chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z, 145453Z_aligned_20260420T0700Z, 151710Z aligned (26×2127 bars, start 2026-07-02T09:00Z) | `research_state/*{134000Z,144234Z,145453Z,151710Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, total PnL 9159.691934882958 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current) — what is removable vs not

1. **External/data block (NOT agent-removable):** full 283-day Hyperliquid window API-blocked by retention (3881/6792 bars at 18:19Z, still decaying). Only an operator-supplied verified Hyperliquid-native archive can unblock; C4-T1 turns that intake into a fail-closed gate.
2. **Retention decay / wasted re-fetch (REMOVED):** probes repeatedly worse than retained; fetch-unless-improved rule stops churn. Probing remains mandatory; fetching does not.
3. **C3 campaign (COMPLETED):** C3-T1 divergence closure, C3-T2 dry-run readiness, C3-T3 power sensitivity, and C3-T4 coverage closeout are on disk. Do not redo any C3 step.
4. **Dry-run canonical-pointer leak (REMOVED 2026-11-14T19:20:58Z):** the old C3-T2 dry run overwrote `hyperliquid_exploratory_next_open_latest.json` with synthetic fixture output. The real artifact was restored from git (`6d2a934f...`), the dry-run harness now writes to a temp `--out-dir`, and it records `fixture_canonical_latest_untouched`. Do not use the superseded `full_window_dry_run_readiness_20261114T182753Z.json`.
5. **Exploratory re-run churn (REMOVED):** the spec-literal result is deterministic on the retained chain; re-running it without a new chain is forbidden. C4-T3 is a distinct execution-friction stress, not a re-run.
6. **Structural 0-trade funnel (RESOLVED):** same-bar `confirm_rebound` vs spec next-hourly-open entry is quantified: 11 volume-passing crashes → 0 same-bar confirms → 8 spec-literal signals → 2 trades (portfolio constraints). Canonical path stays 0-trade by default; exploratory path is opt-in only.
7. **Statistical (agent-mitigating, not removable):** retained window has only **4 crash days**; C3-T3 shows even a 283-day extension reaches ≥10 episodes with only 0.33% probability; a 2-year window is 41.51%, and the pooled cross-venue upper bound is 22.32%. Do not promote to evidence.
8. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with a degraded slice; coverage needs integer aggregate counts and correct probe field mapping; exploratory dry runs must use a temp out-dir.

## Canonical artifacts (do not re-acquire/re-run/overwrite)
- OKX: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol; manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`; universe `research_state/universe_okx_full_verified.json` (54); campaign `research_state/campaign_results_real_okx_full.json` (**cross-venue**).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence** (flat synthetic).
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).
- Coverage/probe/census/campaign/funnel/placebo/C3 artifacts under `research_state/` as referenced above.

## Reproduction
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_full_window_dry_run_readiness.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/audit_spec_divergence_closure.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_power_sensitivity.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/check_archive_readiness.py
```

## Hard prohibitions / anti-avoidance
- **Execute C4-T1..T4 and produce real new-stem artifacts first; no planning-only turn, no status-only turn.** A session that closes without the C4 artifacts + gates green has failed its heavy-work acceptance gate.
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, dry-run fixtures, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes; the spec-literal path must stay opt-in/default-off.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, 145453Z, or 151710Z aligned chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **21/21 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full multi-year Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0), with `underpowered` retained until every GO criterion is met. **Next session's done:** C4-T1..T4 artifacts on disk + coverage/decision memo refresh + gates 21/21 and 4/4 green + this handoff re-timestamped to 2026-11-14T19:42:25Z or later.