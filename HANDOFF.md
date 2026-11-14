# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T18:21:30Z
**Supersedes:** all earlier handoffs (incl. 2026-11-14T17:55:20Z, 17:51:04Z, 17:23:52Z, 16:42:01Z, 15:30:41Z, 15:24:40Z, 15:23:23Z, 14:52:02Z). **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or conclusively prove the data block with fresh reproducible artifacts. **OKX is cross-venue, underpowered, and NEVER Hyperliquid performance evidence.**

**Baseline (this session):** branch `main` @ `04dd3c8`; working tree clean. `scripts/session_gate.py` **18/18 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED** (re-run 2026-11-14T18:20:45Z). Green gate = evidence-chain completeness, **not** profitability/validation.

**META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, this file is already the current handoff. Do not spend the session rewriting it. C2 is now COMPLETE (T1–T4 on disk, gates re-run green). Start at C3-T1 now. No further handoff-only turns are allowed until C3-T1 artifacts exist on disk.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T18:21:30Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1 (Episode Ledger & Power Closure) and C2 (Placebo & Archive Readiness) are COMPLETE. Do not repeat C1-T1..T5 or C2-T1..T4, and do not re-run any deterministic campaign on the retained chain. Your first action is C3-T1 below.**

**NEXT FOCUS CAMPAIGN — C3: SPEC-COMPARISON HARDENING & OPERATOR-ESCALATION PACKAGE.** This is the non-avoidable heavy work. Every task must land a new-stem artifact on disk before the session closes. **No planning-only turn. No simulation theater. No cross-venue relabeling. No re-running an existing campaign on the same chain.**

- **C3-T1 — Spec-comparison divergence closure (heavy, mandatory).** The current `research_state/real_okx_full_spec_comparison.md` records 8 divergences vs the PDF spec. Re-audit each divergence against `research_state/strategy_spec.md` and the current `src/` code: for each, record whether it is (a) resolved in code, (b) intentionally retained (with justification), or (c) a genuine gap requiring code change. Produce `research_state/spec_divergence_closure_<TS>.{json,md}` with a per-divergence status table. Do not change strategy behavior silently; any code change must be opt-in and default-off.
- **C3-T2 — Full-window campaign dry-run harness (mandatory).** Build and record `research_state/full_window_dry_run_readiness_<TS>.json`: a verified, executable command sequence that will run the canonical full-window campaign, full-portfolio placebo, episode-aware audit, and decision-memo update the instant an operator-supplied verified 283-day Hyperliquid-native archive lands. Validate it against a synthetic-but-clearly-labeled dry-run fixture (NOT evidence) to prove the pipeline is wired end-to-end. The placeholder parquet remains NEVER evidence.
- **C3-T3 — Statistical power sensitivity (mandatory).** The retained window has 4 crash days; C1-T2 recorded the binding power target (≥10 independent crash episodes). Produce `research_state/power_sensitivity_<TS>.{json,md}`: given the observed episode rate (2/4 crash days traded, Poisson λ), compute the probability of reaching ≥10 episodes under (a) the partial window extended to 283 days, (b) a 2-year window, (c) a multi-venue pooled window (HL+OKX, clearly labeled cross-venue). This quantifies whether ANY achievable dataset can reach the power floor.
- **C3-T4 — Close the chain (mandatory).** Update `research_state/hyperliquid_universe_coverage.json` with C3 artifacts and integer counts, then run the gate block:
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                  # expect 18/18
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py      # expect 4/4
```
Then update this handoff with the new timestamp and C3 artifact names.

**Latest live probe (2026-11-14T18:19:17Z):** earliest served **2026-04-20T07:00:00Z**, **3881/6792** bars (2911 missing), **235 perps / 32 pass $5M gate / 32 probed**, unprobeable/error **['KPEPE']**; full 283-day window **API-retention-blocked** (`FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`). Decay trend this session: 3884 from 04:00Z (15:28Z) → 3883 from 05:00Z (16:19Z) → 3882 from 06:00Z (16:48Z) → 3882 from 06:00Z (17:26Z) → 3881 from 07:00Z (18:19Z, still decaying slowly).

**No session may close without: C3-T1..T4 artifacts on disk (new stems), C3-T4 coverage refresh + gates green (18/18 and 4/4), and this handoff re-timestamped.**

### STEP 2 — ADOPT-OR-KEEP (bottleneck removed — do not churn)
The retained aligned chain is **24 complete symbols × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z** (`research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json`). The live probe serves strictly less.

- **Do NOT run a fresh full-universe fetch unless the probe shows `earliest_served_start_utc <= 2026-04-20T03:00:00Z` AND `max_bars_returned >= 3885`.** Five consecutive probes this session were worse than retained; re-fetching is now a known dead end. If (and only if) the probe improves, follow the fetch/derive/adopt commands in the prior handoff revision (git `53ae6f9`), adopt only if ≥3885 bars AND start ≤ 2026-04-20T03:00:00Z, else record `KEEP_RETAINED` in `research_state/hyperliquid_universe_coverage.json`. Never point coverage/census/campaign/funnel at a degraded chain.
- **This session:** C1 and C2 are complete; C2-T2 probe refreshed 18:19:17Z (KEEP_RETAINED, decay continues). No fresh fetch is warranted; keep `..._20261114T104210Z_aligned_20260420T0300Z`, record `KEEP_RETAINED`, and proceed directly to C3-T1.

### STEP 3 — SPEC-LITERAL NEXT-OPEN ADJUDICATION (**COMPLETED 2026-11-14T16:22:12Z — do not re-run**)
**Result artifact:** `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json` (+ `_metrics.json`/`.csv`) and funnel `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T162212Z.{json,md}`.
- **Funnel:** 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → **8 generate_signal (spec-literal)** → **2 real-engine trades** (BCH time_exit +$559, BTC liquidated -$3,230; 6 signals blocked by ETH hedge/120% cap/ETH availability).
- **PnL/Metrics:** total PnL -$2,671, max drawdown -3.2%, win rate 50%, Sharpe -0.70, monthly: May +$559, Jun -$3,230.
- **Labels:** `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`, `research_status=NOT_EVIDENCE_EXPLORATORY_FANOUT`. Canonical baseline unchanged. **Do not overwrite the canonical campaign, do not claim validation, do not allocate capital, and do not re-run this campaign on the same chain (deterministic — it wastes the session).**

### STEP 4 — EPISODE-AWARE AUDIT (**COMPLETE — C1-T1 on disk; do not re-run**)
Canonical partial window audit is recorded NOT_APPLICABLE (`research_state/episode_edge_hyperliquid_partial.{json,md}`, 2026-11-14T12:56Z, 0 trades). The exploratory 2-trade episode ledger is recorded in `research_state/episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z.{json,md}` (`NOT_APPLICABLE` for bootstrap/permutation at n=2 with explicit reasons). **Do not promote to evidence until ≥10 independent crash episodes with a positive episode-level bootstrap CI excluding 0.** The retained window has only 4 crash days total; expect `underpowered`.

### STEP 5 — POWER / SAMPLE-SIZE TARGET AND DECISION MEMO (**COMPLETE — C1-T2 on disk; do not re-run**)
`research_state/decision_memo_okx_full.md` (updated 2026-11-14T16:26Z) and `research_state/power_target_hyperliquid_20261114T172700Z.{json,md}` contain the fresh probe facts, the spec-literal vs same-bar structural finding, the exploratory result (2 trades, -$2,671), the episode count (2/4 crash days produced trades), and the binding power target (**≥10 independent crash episodes + episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05**). C3-T3 extends this with power-sensitivity scenarios. Keep verdict **`underpowered`** until every GO criterion is met.

### STEP 6 — REFRESH COVERAGE, THEN VERIFY THE CHAIN
Coverage was refreshed 2026-11-14T18:20:45Z to the 18:19:17Z probe (KEEP_RETAINED) with C2 artifacts; gates re-run green 18:20:45Z. The next session must refresh it again with its own C3-T2 probe + C3 artifacts, then run the C3-T4 gate block. Update this handoff with the new timestamp and C3 artifact names.

### STEP 7 — ONLY PATH TO FULL EVIDENCE: OPERATOR ARCHIVE
If an operator-supplied verified Hyperliquid-native 283-day archive arrives, follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, full-portfolio placebo, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder). C2-T3 confirmed the runbook is READY (`research_state/archive_readiness_20261114T182045Z.json`).

**No session may close without: C3-T1..T4 artifacts on disk (new stems), C3-T4 coverage refresh + gates green (18/18 and 4/4), and this handoff re-timestamped.**

---

## Verified state (as of 2026-11-14T18:21:30Z; retained/gate-checked chain unless noted)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **18/18 — DONE** (re-run 2026-11-14T18:20:45Z) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (re-run 2026-11-14T18:20:45Z) | `scripts/verify_campaign_evidence.py` |
| Latest live retention probe | **2026-11-14T18:19:17Z**; 3881/6792 bars; 2911 missing; earliest 2026-04-20T07:00Z; 235 perps / 32 pass $5M / 32 probed; unprobeable/error=['KPEPE']; sha256 `ffd11714f91b2b57305f2f8877aca9d02d4933e0a4afd9082c6c7da6e3a97b27` | `research_state/hyperliquid_retention_probe.json` |
| Retained aligned slice | 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Retained census | 24 symbols / 93,240 bars / **11 RSI crashes / 0 confirmed signals**; 4 distinct crash days (2026-05-28, 06-02, 06-05, 06-24) | `hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Retained partial campaign (canonical) | `performance_evidence=false` / `NOT_EVIDENCE_PARTIAL_UNIVERSE`, 0 trades, 0.0 PnL; sha256 `225887ef4d11ffb4e158fbe15e990ec2c0c488250ae877152ceec01c1d7ec1fa` | `campaign_results_real_hyperliquid_universe_snapshot_20261114T151710Z.json` |
| Canonical funnel (retained) | 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirm → 5 next-bar confirm → 0 generate_signal; sha256 `f746a83f1fe99f34734e1342612fce269b83c8e4d1cd77a4334796dd12ffab72` | `hyperliquid_signal_funnel_20261114T151710Z.{json,md}` |
| **Exploratory next-open adjudication (NOT evidence)** | **COMPLETED 2026-11-14T16:22:12Z: 2 trades (BCH +559, BTC -3230), total PnL -$2,671, max DD -3.2%, 8 signals → 2 trades (portfolio constraints); label `NOT_EVIDENCE_EXPLORATORY_FANOUT`** | `campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json`, `hyperliquid_signal_funnel_exploratory_next_open_20261114T162212Z.{json,md}` |
| Exploratory episode audit (canonical partial) | `NOT_APPLICABLE_NO_EPISODES` (0 trades) — exploratory 2-trade ledger recorded via C1-T1 (`episode_edge_hyperliquid_exploratory_next_open_20261114T172700Z.{json,md}`) | `episode_edge_hyperliquid_partial.{json,md}` |
| **C2-T1 HL exploratory full-portfolio placebo (NOT evidence)** | **COMPLETED 2026-11-14T18:20:23Z: 8 signal-gate events, C(8,2)=28 exact subsets, canonical replay reproduced exactly (2 trades, -$2,670.7568), canonical at 89.3rd percentile, mean -$2,901, P(PnL>0)=3.6%; label `NOT_EVIDENCE_PLACEBO`, verdict `underpowered`** | `placebo_portfolio_hyperliquid_exploratory_next_open_20261114T182023Z.{json,md}` |
| **C2-T3 archive-ingestion readiness** | **READY (2026-11-14T18:20:45Z): all runbook scripts/flags verified against repo; full archive dir absent (operator must supply); placeholder parquet confirmed non-evidence; ingest pipeline wired end-to-end** | `archive_readiness_20261114T182045Z.json` |
| Gate-checked coverage | KEEP_RETAINED vs degraded 145453Z/151710Z; verdict `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED`; probe block = 18:19:17Z | `hyperliquid_universe_coverage.json` |
| Degraded chains (DO NOT ADOPT) | 134000Z, 144234Z, 145453Z, 145453Z_aligned_20260420T0700Z (3881 bars), 151710Z aligned (26×2127 bars, start 2026-07-02T09:00Z) | `research_state/*{134000Z,144234Z,145453Z,151710Z}*`, `cache/*` |
| Phase O artifact timestamp (gate) | 2026-11-13T23:38:47Z | `research_state/episode_edge_okx_full.json` |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99]; 8 trades, total PnL 9159.691934882958 | `episode_edge_okx_full.json`, `campaign_results_real_okx_full.json` |

## Bottlenecks (current) — what is removable vs not

1. **External/data block (NOT agent-removable):** full 283-day Hyperliquid window API-blocked by retention (3881/6792 bars at 18:19Z, still decaying slowly). Only an operator-supplied verified Hyperliquid-native archive can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`; readiness confirmed READY by C2-T3).
2. **Retention decay / wasted re-fetch (REMOVED):** five probes this session all strictly worse than or equal to the retained chain; the fetch-unless-improved rule (Step 2) stops the per-session churn. Probing remains mandatory; fetching does not.
3. **C1 campaign (COMPLETED):** C1-T1 episode ledger, C1-T2 power closure, C1-T3 fragility (8 variants), C1-T4 data request update all on disk (17:27:00Z–17:48:16Z); coverage refreshed 17:49:00Z (KEEP_RETAINED). C1-T5 closed (gates re-run 18/18 and 4/4 at 17:55:20Z).
4. **C2 campaign (COMPLETED):** C2-T2 probe refreshed 18:19:17Z; C2-T1 HL exploratory placebo (28 subsets, canonical at 89.3rd pctile) on disk 18:20:23Z; C2-T3 archive readiness (READY) on disk 18:20:45Z; C2-T4 coverage refresh + gates green 18:20:45Z. Do not redo any C2 step.
5. **Exploratory re-run churn (REMOVED this handoff):** the spec-literal result is deterministic on the retained chain; re-running it (or the canonical campaign) without a new chain is forbidden. The placebo (C2-T1) is a distinct inference artifact, not a re-run.
6. **Structural 0-trade funnel (RESOLVED):** same-bar `confirm_rebound` vs spec next-hourly-open entry is quantified: 11 volume-passing crashes → 0 same-bar confirms → 8 spec-literal signals → 2 trades (portfolio constraints). Canonical path stays 0-trade by default (correct); exploratory path is opt-in only.
7. **Statistical (agent-mitigating, not removable):** retained window has only **4 independent crash episodes**; even the spec-literal path is underpowered (2 trades from 2 episodes). C1-T1/T2 closed the bookkeeping and power math; C2-T1 placebo adds the inference artifact; C3-T3 will quantify whether any achievable dataset reaches the power floor. Do not promote to evidence.
8. **Episode-audit ambiguity (REMOVED):** n<10 episode audits recorded as `NOT_APPLICABLE` with explicit reasons in C1-T1 — this blocks both fabricated p-values and silent deferral.
9. **Resolved traps (do not reintroduce):** census requires `--symbols` (full aligned set); campaign flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with a degraded slice; coverage needs integer aggregate counts and correct probe field mapping.

## Canonical artifacts (do not re-acquire/re-run/overwrite)
- OKX: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol; manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`; universe `research_state/universe_okx_full_verified.json` (54); campaign `research_state/campaign_results_real_okx_full.json` (**cross-venue**).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence** (flat synthetic).
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).
- Coverage/probe/census/campaign/funnel/placebo artifacts under `research_state/` as referenced above.

## Reproduction
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_hyperliquid_exploratory.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/check_archive_readiness.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/reconcile_hyperliquid_signal_funnel.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z \
  --output research_state/hyperliquid_signal_funnel_repro.json
```

## Hard prohibitions / anti-avoidance
- **Execute C3-T1..T4 and produce real new-stem artifacts first; no planning-only turn, no status-only turn.** A session that closes without the C3 artifacts + gates green has failed its heavy-work acceptance gate.
- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater (C1-T3 is capped at 8 configs). No per-event-null as portfolio test.
- No validation/parity/capital-allocation claims (`underpowered`). No silent strategy-baseline changes; the spec-literal path must stay opt-in/default-off.
- Never run census without `--symbols` on >12-symbol slice. Flag is `--allow-partial-not-evidence` (hyphens).
- Do not adopt/point coverage at degraded 134000Z, 144234Z, 145453Z, or 151710Z aligned chains.
- No additional handoff/status files. **This file is the single durable handoff.**

## Definition of done
Evidence chain **18/18 achieved** (completeness). **Decision-grade validation NOT achieved.** Required for done/GO consideration: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0), with `underpowered` retained until every GO criterion is met. **Next session's done:** C3-T1..T4 artifacts on disk + coverage refresh + gates 18/18 and 4/4 green + this handoff re-timestamped.

(End of file - total 131 lines)