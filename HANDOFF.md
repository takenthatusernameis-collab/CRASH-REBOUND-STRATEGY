# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T22:10:03Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** The duplicate `HANDOFF_20261114T202006Z.md` was deleted this session; do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the data block with fresh reproducible artifacts. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Baseline (this session):** branch `main`; C1, C2, C3, C4, **C5-T1, C5-T2, C5-T3, C5-T4 are COMPLETE**. `scripts/session_gate.py` is **21/21 checks passed — DONE** and `scripts/verify_campaign_evidence.py` is **4/4 — EVIDENCE VERIFIED** (re-run at the end of this session). Green gate = evidence-chain completeness, **not** profitability/validation. Canonical `episode_edge_okx_full.json` timestamp is `2026-11-13T23:38:47Z`.

**META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, this file is already the current handoff. Do not spend the session rewriting it. **C5-T1, C5-T2, C5-T3, C5-T4 are COMPLETE** (C5-T2: `research_state/operator_archive_request_20261114T221003Z.{json,md}`; C5-T4: coverage + memo refresh, probe 3877/6792, gates 21/21 and 4/4). **Next session starts at C5-T1 execution (awaits operator archive). No handoff-only turn is allowed until a C4-T1 `ACCEPT_AS_EVIDENCE_CANDIDATE` artifact exists.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T22:10:03Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1 (Episode Ledger & Power Closure), C2 (Placebo & Archive Readiness), C3 (Spec-Comparison Hardening), C4 (Data-Block Decision Lock, Operator Intake Validation & Multi-Year Protocol), C5-T1 (end-to-end archive-gated validation orchestrator), C5-T2 (operator data request v2 with machine-checkable acceptance), C5-T3 (pipeline negative/positive proof), and C5-T4 (close the chain: probe refresh, coverage + memo update, gates green) are COMPLETE. Do not repeat C1–C4 work, do not repeat C5-T1..T4, do not re-run any deterministic campaign on the retained chain, and do not re-run the C4 friction grid.**

**The evidence gap is unchanged and external: the public Hyperliquid API serves only 3,877 / 6,792 hourly bars (still decaying), so the 1,013.2-day multi-year archive required for 80% power does not exist in this environment. Your job is NOT to manufacture evidence; it is to execute C5-T1 (the full-validation orchestrator) the moment an operator-supplied verified Hyperliquid-native archive arrives and passes C4-T1 (`ACCEPT_AS_EVIDENCE_CANDIDATE`).**

**REMAINING FOCUS CAMPAIGN — C5-T1 EXECUTION (BLOCKED ON OPERATOR ARCHIVE).** The C5-T1 orchestrator (`scripts/run_full_validation_campaign.py`) is on disk and dry-run proven (6/6 steps PASS). When an operator archive lands, run C4-T1 intake validator → if `ACCEPT_AS_EVIDENCE_CANDIDATE` → run C5-T1 orchestrator → full decision-grade campaign. **No planning-only turn. No simulation theater. No cross-venue relabeling.**

**No session may close without: C5-T1 execution artifacts on disk (new stems) OR documented operator-data block with exact live probe counts + coverage/decision memo refresh + gates 21/21 and 4/4 green + this handoff re-timestamped to 2026-11-14T22:10:03Z or later.**

---

### STEP 2 — ADOPT-OR-KEEP (bottleneck removed — do not churn)
The retained aligned chain is **24 complete symbols × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json`). The latest live probe (2026-11-14T21:23:00Z) serves **3,877** bars from **2026-04-20T11:00:00Z** — strictly worse.

- **Do NOT run a fresh full-universe fetch unless the probe shows `earliest_served_start_utc <= 2026-04-20T03:00:00Z` AND `max_bars_returned >= 3885`.** Re-fetching a degraded chain is a known dead end. If the probe improves, adopt only if ≥3885 bars AND start ≤ `2026-04-20T03:00:00Z`; otherwise record `KEEP_RETAINED` in coverage. Never point coverage/census/campaign/funnel at a degraded chain.

### STEP 3 — SPEC-LITERAL NEXT-OPEN ADJUDICATION (**COMPLETED 2026-11-14T16:22:12Z — do not re-run**)
**Result artifact:** `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` (+ `_metrics.json`/`.csv`) and funnel `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T162541Z.{json,md}`.
- **Funnel:** 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → **8 generate_signal (spec-literal)** → **2 real-engine trades** (BCH time_exit +$559, BTC liquidated -$3,230; 6 signals blocked by ETH hedge/120% cap/ETH availability).
- **PnL/Metrics:** total PnL -$2,670.76, max drawdown -3.2%, win rate 50%, Sharpe -0.70.
- **Labels:** `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`. Canonical baseline unchanged. **Do not overwrite the canonical campaign, do not claim validation, do not allocate capital, and do not re-run this campaign on the same chain.**

### STEP 4 — EPISODE-AWARE AUDIT (**COMPLETE — C1-T1 on disk; do not re-run**)
Canonical partial window audit is recorded NOT_APPLICABLE (`research_state/episode_edge_hyperliquid_partial.{json,md}`, 0 trades). The exploratory 2-trade episode ledger is recorded in `research_state/episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z.{json,md}`. **Do not promote to evidence until ≥10 independent crash episodes with a positive episode-level bootstrap CI excluding 0.**

### STEP 5 — POWER / SAMPLE-SIZE TARGET AND DECISION MEMO (**COMPLETE — C1-T2/C3-T3 on disk; do not re-run**)
`research_state/power_target_hyperliquid_20261114T172700Z.{json,md}` and `research_state/power_sensitivity_20261114T182832Z.{json,md}` contain the binding power target (**≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05**) and the scenario probabilities. Keep verdict **`underpowered`** until every GO criterion is met.

### STEP 6 — C4 CLOSE-OUT (**COMPLETE 2026-11-14T20:48:30Z — do not re-run**)
- C4-T1 intake validator: `research_state/archive_intake_validation_20261114T202957Z.{json,md}` — placeholder `REJECT_NOT_EVIDENCE`, self-test 4/4, truncated fixture rejected, flat fixture accepted only as `ACCEPT_FIXTURE_NON_EVIDENCE` (`is_market_data=false`, `is_evidence=false`, `performance_evidence=false`).
- C4-T2 multi-year protocol: `research_state/multi_year_validation_protocol_20261114T203040Z.{json,md}` — `NO_GO`; 80% power needs **1,013.2 days** (~2.78 y) = **24,319 hourly bars/symbol** at 0.012355 episodes/day.
- C4-T3 execution-friction stress: `research_state/execution_friction_stress_hyperliquid_20261114T204632Z.{json,md,csv}` — 9 variants, **all negative**, range −7,945.88..−501.77, label `NOT_EVIDENCE_EXECUTION_FRICTION`, `canonical_baseline_changed=false`.
- C4-T4: probe refreshed (3,879/6,792; earliest 2026-04-20T09:00:00Z), coverage + memo updated, duplicate handoff deleted, gates re-run green.

### STEP 7 — C5 CLOSE-OUT (**COMPLETE 2026-11-14T22:10:03Z — do not re-run**)
- **C5-T1 validation orchestrator:** `scripts/run_full_validation_campaign.py` on disk — **COMPLETE**.
- **C5-T2 operator data request v2:** `research_state/operator_archive_request_20261114T221003Z.{json,md}` — binding multi-year window `2023-12-20T17:19:21Z..2026-09-28T23:00:00Z` (1,013.2 days, 24,319 bars/symbol, ≥24 symbols, ≥10 distinct crash days, Hyperliquid-native provenance, per-file SHA256, non-synthetic); 7-step executable command sequence with pass/fail predicates; explicit statement that 283 days is 2.78× too short. `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` updated to point at v2.
- **C5-T3 dry-run negative/positive proof:** `research_state/full_validation_pipeline_readiness_20261114T212055Z.{json,md}` — all 6 steps PASS; placeholder rejected, truncated rejected, flat fixture not evidence — **COMPLETE**.
- **C5-T4 close the chain:** retention probe refreshed (3,877/6,792; earliest 2026-04-20T11:00:00Z; `KEEP_RETAINED`); coverage `hyperliquid_universe_coverage.json` updated with C5 artifacts and integer counts; decision memo `decision_memo_okx_full.md` updated with C5 state and standing `NO_GO`; gates re-run green (21/21 and 4/4).

### STEP 8 — ONLY PATH TO FULL EVIDENCE: OPERATOR ARCHIVE (v2 request in C5-T2)
If an operator-supplied verified Hyperliquid-native archive arrives, it must first pass C4-T1 (`ACCEPT_AS_EVIDENCE_CANDIDATE`) and then the C5-T1 orchestrator. Follow `research_state/operator_archive_request_20261114T221003Z.md`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder; C4-T1 rejects it).

**No session may close without: C5-T1 execution artifacts on disk (new stems) OR documented operator-data block with exact live probe counts + coverage/decision memo refresh + gates 21/21 and 4/4 green + this handoff re-timestamped to 2026-11-14T22:10:03Z or later.**

---

## Verified state (as of 2026-11-14T22:10:03Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` (duplicate deleted) | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** (re-run this session) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (re-run this session) | `scripts/verify_campaign_evidence.py` |
| C3-T1 spec divergence closure | **8/8 adjudicated**; 4 resolved, 4 retained, 0 gaps | `spec_divergence_closure_20261114T182754Z.{json,md}` |
| C3-T2 dry-run readiness | **READY**; 10/10 steps; canonical latest untouched | `full_window_dry_run_readiness_20261114T192058Z.json` |
| C3-T3 power sensitivity | 283d 0.33%, 2y 41.51%, pooled 22.32% | `power_sensitivity_20261114T182832Z.{json,md}` |
| C4-T1 intake validator | placeholder `REJECT_NOT_EVIDENCE`; self-test 4/4; truncated rejected | `archive_intake_validation_20261114T202957Z.{json,md}` |
| C4-T2 multi-year protocol | `NO_GO`; 80% power = 1,013.2 d / 24,319 bars/symbol | `multi_year_validation_protocol_20261114T203040Z.{json,md}` |
| C4-T3 execution friction | 9/9 variants negative; −7,945.88..−501.77; not evidence | `execution_friction_stress_hyperliquid_20261114T204632Z.{json,md,csv}` |
| Latest live retention probe | 2026-11-14T21:23:00Z; 3877/6792 bars; 2,915 missing; earliest 2026-04-20T11:00Z; 235 perps / 37 pass $5M / 37 probed; unprobeable `['KPEPE', '...']`; sha256 `27adec869b4593f472d92049cd62d6c1273804027730836866e26fe3827d6927` | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / **11 RSI crashes / 0 confirmed signals**; 4 distinct crash days | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign (canonical) | `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`, 0 trades | `campaign_results_real_hyperliquid_universe_snapshot_20261114T151710Z.json` |
| Exploratory next-open (NOT evidence) | 2 trades, -$2,670.76, 8 signals → 2 trades | `campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` |
| Exploratory latest pointer | real retained-chain artifact, sha256 `6d2a934f...d91d686` (synthetic leak reverted) | `hyperliquid_exploratory_next_open_latest.json` |
| C2-T1 HL exploratory placebo | 8 signal-gate events, 28 exact subsets, canonical at 89.3rd percentile; `underpowered` | `placebo_portfolio_hyperliquid_exploratory_next_open_20261114T182023Z.{json,md}` |
| Gate-checked coverage | KEEP_RETAINED; verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED`; C4+C5 artifacts recorded | `hyperliquid_universe_coverage.json` |
| Degraded chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z, 151710Z aligned (26×2127, start 2026-07-02T09:00Z) | `research_state/*{134000Z,144234Z,145453Z,151710Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| C5-T1 validation orchestrator | **COMPLETE**; `scripts/run_full_validation_campaign.py` on disk | `scripts/run_full_validation_campaign.py` |
| C5-T2 operator archive request v2 | **COMPLETE**; binding multi-year window, 7-step executable commands, 8 predicates | `research_state/operator_archive_request_20261114T221003Z.{json,md}` |
| C5-T3 dry-run negative/positive proof | **COMPLETE**; all 6 steps PASS; placeholder rejected, truncated rejected, flat fixture not evidence | `full_validation_pipeline_readiness_20261114T212055Z.{json,md}` |
| C5-T4 closeout | probe 3877/6792; KEEP_RETAINED; coverage+memo updated; gates 21/21, 4/4 | `hyperliquid_universe_coverage.json`, `decision_memo_okx_full.md` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, PnL 9159.69 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current) — what is removable vs not

1. **External/data block (NOT agent-removable):** the public Hyperliquid API serves 3,877/6,792 bars and is still decaying; the 80%-power archive needs **1,013.2 days** (start 2023-12-20T17:19:21Z), which is beyond any public-API retention. Only an operator-supplied verified archive unblocks this; C4-T1 and C5-T1 turn that intake into a fail-closed gate.
2. **Handoff duplication (REMOVED):** `HANDOFF_20261114T202006Z.md` deleted; `HANDOFF.md` is the single durable handoff.
3. **Analysis-side gaps (REMOVED by C4/C5):** intake validation, multi-year power/duration, execution-friction bound, operator request v2, full-validation orchestrator dry-run — all exist as executable artifacts. Do not redo them.
4. **Retention decay / wasted re-fetch (REMOVED):** fetch-unless-improved rule stops churn. Probing remains mandatory; fetching does not.
5. **Dry-run canonical-pointer leak (REMOVED 2026-11-14T19:20:58Z):** dry runs write to a temp `--out-dir`; the canonical latest pointer is hash-checked. Do not use the superseded `full_window_dry_run_readiness_20261114T182753Z.json`.
6. **Exploratory re-run churn (REMOVED):** the spec-literal result is deterministic on the retained chain; re-running it without a new chain is forbidden. The C4-T3 friction grid was a distinct stress, not a re-run.
7. **Structural 0-trade funnel (RESOLVED):** 11 volume-passing crashes → 0 same-bar confirms → 8 spec-literal signals → 2 trades (portfolio constraints). Canonical path stays 0-trade by default; exploratory path is opt-in only.
8. **Statistical (agent-mitigating, not removable):** retained window has only **4 crash days**; C3-T3 shows even a 283-day extension reaches ≥10 episodes with only 0.33% probability, and the pooled cross-venue upper bound is 22.32%. Do not promote to evidence.
9. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with a degraded slice; coverage needs integer aggregate counts and correct probe field mapping; exploratory dry runs must use a temp out-dir; C4-T1 must keep the placeholder as a hard reject even with `--allow-synthetic-fixture`.

## Canonical artifacts (do not re-acquire/re-run/overwrite)
- OKX: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol; manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`; universe `research_state/universe_okx_full_verified.json` (54); campaign `research_state/campaign_results_real_okx_full.json` (**cross-venue**).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence** (flat synthetic; C4-T1 rejects it).
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).
- Coverage/probe/census/campaign/funnel/placebo/C3/C4/C5 artifacts under `research_state/` as referenced above.

## Reproduction
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_multi_year_validation_protocol.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_execution_friction_stress_hyperliquid.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_power_sensitivity.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/check_archive_readiness.py
```

## Hard prohibitions / anti-avoidance
- **Execute C5-T1 (when operator archive arrives) and produce real new-stem artifacts first; no planning-only turn, no status-only turn.** A session that closes without the C5-T1 execution artifacts + gates green has failed its heavy-work acceptance gate.
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, dry-run fixtures, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes; the spec-literal path must stay opt-in/default-off.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, 145453Z, or 151710Z aligned chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **21/21 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full multi-year Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0), with `underpowered` retained until every GO criterion is met. **Next session's done:** C5-T1 execution artifacts on disk (when operator archive arrives) + coverage/decision memo refresh + gates 21/21 and 4/4 green + this handoff re-timestamped to 2026-11-14T22:10:03Z or later.

(End of file - total 136 lines)