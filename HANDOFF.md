# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T01:13:03Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session):** branch `main`; C1, C2, C3, C4, **C5-T1..T4 COMPLETE**. `scripts/session_gate.py` is **21/21 checks passed — DONE** and `scripts/verify_campaign_evidence.py` is **4/4 — EVIDENCE VERIFIED**. **NEW: C6-T1/T2/T3 COMPLETE — the cross-venue power and inference bottlenecks are removed.** A real, gap-free, non-synthetic **34-symbol × 32,808-bar OKX multi-year archive (2023-01-01..2026-09-28)** is on disk, ingested, and run through the real portfolio engine: **42 trades, +18,220.86 PnL (+18.22% total, +5.07%/yr over 3.38y, max DD −33.57%, Sharpe 0.10, win rate 50%, profit factor 1.33)**. The multi-year census has **1,182 RSI crashes → 782 volume-pass → 55 signal-gate → 19 independent crash episodes over 23 crash days** — far above the ≥10-episode power floor. This is **CROSS-VENUE evidence, NOT Hyperliquid performance evidence**. **C6-T3 inference is DONE (Phase O artifact timestamp 2026-11-15T00:35:31Z): episode-block bootstrap 95% CI [−50,660.49, +99,295.03] P(>0)=0.6649; crash-day permutation p=0.1000; portfolio placebo p=0.4000; verdict `underpowered`.**

**META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, this file is already the current handoff. Do not spend the session rewriting it. The next real task is **operator archive acquisition** (Hyperliquid-native validation), not another handoff.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T01:13:03Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1–C6 are COMPLETE. C6-T1/T2/T3 are COMPLETE: the multi-year cross-venue archive, census, power reassessment, real campaign, and dependence-aware inference are all on disk and the gates are green. Do not repeat C1–C6, do not re-acquire the OKX multi-year archive, do not re-run the 42-trade campaign, do not re-run the C6-T3 inference battery, and do not re-run any deterministic campaign on the retained chain.**

**The remaining bottleneck is EXTERNAL and NOT agent-removable: Hyperliquid-native validation.** The public Hyperliquid API serves only 3,876/6,792 hourly bars (earliest 2026-04-20T12:00Z). Only an operator-supplied verified archive that passes `scripts/validate_hyperliquid_archive_intake.py` can unblock the Hyperliquid-native verdict. The runbook is `research_state/operator_archive_request_20261114T221003Z.{json,md}` (binding window 2023-12-20T17:19:21Z..2026-09-28T23:00:00Z, 1,013.2 days, 24,319 bars/symbol, ≥24 symbols, ≥10 distinct crash days, per-file SHA256, non-synthetic). The full-validation orchestrator is wired and dry-run ready: `scripts/run_full_validation_campaign.py` (6/6 steps PASS on a labelled non-evidence fixture). **If no operator archive is supplied, the only remaining work is to re-run the mandatory read-only retention probe and re-timestamp this handoff — never to manufacture, relabel, or interpolate Hyperliquid evidence.**

**Deliverables (if an archive lands, all new stems, no overwrites):**
1. **Ingest and validate** the operator archive through `scripts/validate_hyperliquid_archive_intake.py`; it must yield `ACCEPT_AS_EVIDENCE_CANDIDATE`. Reject any flat/synthetic/truncated fixture.
2. **Run the canonical campaign** through the real portfolio engine on the Hyperliquid-native chain; report trades, PnL, max DD, Sharpe, win rate, profit factor.
3. **Run the C6-T3 dependence-aware battery on the Hyperliquid-native campaign:** episode-block bootstrap 95% CI (98h single-linkage), crash-day conditional permutation p, exact/conditioned full-portfolio placebo p. Report all three and the effective number of independent crash episodes.
4. **Update the decision memo** (`research_state/decision_memo_okx_full.md`) with a Hyperliquid-native section and an explicit GO/STOP verdict against the 7 stop/go criteria. Do not quote the PDF's +115%/yr.
5. **Close the chain:** run `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py`, `scripts/session_gate.py` (21/21), and `scripts/verify_campaign_evidence.py` (4/4) green; re-timestamp this handoff.

**Binding constraints:**
- **Hyperliquid-native validation is still external.** Do not relabel OKX, the multi-year archive, dry-run fixtures, or the partial Hyperliquid chain as Hyperliquid evidence.
- **No synthetic/fabricated data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **No new handoff/status files.** This is the single durable handoff.
- **No unnecessary re-acquisition/reruns.** The multi-year archive and campaign are canonical for the cross-venue track. Do not re-run them without a new artifact stem and a documented reason.
- **No relaxing the $5M volume floor or the spec-literal opt-in default.** The canonical strategy path remains default; spec-literal next-open remains opt-in.
- **Do not quote the PDF's +115%/yr.** The honest multi-year cross-venue result is +5.07%/yr with a −33.57% max drawdown.

**Definition of done for the next session:** either (a) a Hyperliquid-native verdict with C6-T3 inference artifacts on disk, decision memo updated, `verify_next_focus_campaign.py` PASS, gates 21/21 and 4/4 green, and this handoff re-timestamped; or (b) a refreshed retention probe, a re-verified `NO_GO`/`underpowered` state, gates green, and this handoff re-timestamped — with no fabricated evidence of any kind.

---

## What changed this session (bottleneck removal)

### The old bottleneck
Every prior session closed on "blocked: operator archive required." That made the handoff a waiting room: agents re-probed the decaying Hyperliquid API, re-documented the same gap, and produced no new inference. The power floor (≥10 independent crash episodes) was unreachable on the 283-day Hyperliquid/OKX window.

### The removed bottleneck
OKX public REST v5 `history-candles` serves real, gap-free hourly OHLCV back to 2023. We acquired and ingested a **multi-year cross-venue** archive:
- **Window:** 2023-01-01T00:00:00Z .. 2026-09-28T23:00:00Z
- **Symbols:** 34 (AAVE, ADA, ALGO, APT, ATOM, AVAX, BAT, BCH, COMP, CRV, DOGE, DOT, ETC, ETH, FIL, GRT, KSM, LINK, LTC, MANA, MINA, NEAR, OP, SAND, SHIB, SNX, SOL, SUSHI, THETA, TRX, UNI, XLM, XRP, XTZ)
- **Coverage:** 32,808 bars/symbol, **0 gaps**, all 34 complete
- **Provenance:** `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json`; `fabricated_data=false`; `is_hyperliquid_venue_data=false`
- **Ingest:** `research_state/cache/okx_1h_multiyear_20230101_20260928/provenance.json`
- **Universe:** `research_state/universe_okx_multiyear_verified.json` (34/34 selected, peak trailing-24h volume ≥ $5M)
- **Census:** `research_state/crash_event_census_real_okx_multiyear.{json,md}` — 1,182 events, 782 volume-pass, 55 signal-gate, 42 trades matched
- **Power:** `research_state/multiyear_cross_venue_power.{json,md}` — **19 signal-gate episodes / 23 crash days**, verdict `CROSS_VENUE_POWERED_OBSERVED`
- **Campaign:** `research_state/campaign_results_real_okx_multiyear.{json,_metrics.json,_metrics.csv}` — 42 trades, +18,220.86 PnL, +18.22% total, +5.07%/yr, max DD −33.57%, Sharpe 0.10, win rate 50%, profit factor 1.33, 17 positive / 14 negative months
- **Closeout:** `research_state/c6_closeout_20261114T234229Z.{json,md}` — verdict `CROSS_VENUE_MULTIYEAR_COMPLETE_NOT_HYPERLIQUID`
- **Gate:** `scripts/verify_next_focus_campaign.py` — checks archive/cache/universe/census/power/campaign/handoff; **passes** (after this handoff update)

### Engine/metrics fixes made to unblock the run
- **RSI incremental cache** (`src/strategy/crash_rebound.py`): the scanner's length-keyed cache did not actually make Wilder RSI incremental; each new bar recomputed the full prefix, giving O(n²) per symbol. The multi-year run would have taken hours. The cache now stores the latest Wilder state and updates it in O(1) when the caller advances one bar. Test: `tests/test_rsi_incremental_cache_20261114.py` (3 tests).
- **Epoch timestamp parsing** (`src/metrics/campaign_metrics.py`): numeric candle timestamps (epoch ms) were misread by `datetime.fromisoformat` as ISO basic dates (e.g. year 1770), producing a garbage 0.43-year horizon and an inflated annualized return. Numeric epochs are now converted explicitly. Test: `tests/test_campaign_metrics_epoch_timestamps_20261114.py` (2 tests). The corrected multi-year horizon is **3.38 years**; the corrected annualized return is **+5.07%**, not +47.6%.

---

## Verified state (as of 2026-11-15T01:13:03Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C6 multi-year archive | 34 symbols × 32,808 bars, 0 gaps, `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 cache | 34/34 complete; expected 32,808; window 2023-01-01..2026-09-28 | `research_state/cache/okx_1h_multiyear_20230101_20260928/provenance.json` |
| C6 universe | 34/34 selected; peak 24h volume ≥ $5M | `research_state/universe_okx_multiyear_verified.json` |
| C6 census | 1,182 events / 782 volume-pass / 55 signal-gate / 42 trades matched | `crash_event_census_real_okx_multiyear.json` |
| C6 power | 19 signal-gate episodes / 23 crash days / largest share 16.4%; `CROSS_VENUE_POWERED_OBSERVED` | `multiyear_cross_venue_power.json` |
| C6 campaign | 42 trades; +18,220.86 PnL; +18.22% total; +5.07%/yr; max DD −33.57%; Sharpe 0.10; win 50%; PF 1.33 | `campaign_results_real_okx_multiyear.json` |
| C6 closeout | `CROSS_VENUE_MULTIYEAR_COMPLETE_NOT_HYPERLIQUID` | `c6_closeout_20261114T234229Z.json` |
| **C6-T3 episode edge** | 19 episodes / 23 crash days / 13 symbols; bootstrap 95% CI [−50,660.49, +99,295.03] P(>0)=0.6649; permutation p=0.1000 (90th pct); verdict `underpowered` | `episode_edge_okx_multiyear.{json,md}` (2026-11-15T00:35:31Z) |
| **C6-T3 portfolio placebo** | 55-event pool, choose 42, 20 runs; mean 13,260.48; canonical 60th pct; p(placebo≥canonical)=0.4000; verdict `underpowered` | `placebo_portfolio_okx_multiyear.{json,md}` (2026-11-15T00:35:50Z) |
| **Decision memo C6** | C6 section added: campaign metrics, power counts, bootstrap CI, permutation p, placebo p, explicit `underpowered` verdict | `research_state/decision_memo_okx_full.md` |
| Latest live retention probe | **2026-11-15T00:42:24Z** (this session); **3,874/6,792 bars** max; earliest 2026-04-20T14:00:00Z; 37/38 probed symbols partial, 1 empty/error (KPEPE); verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` | `research_state/hyperliquid_retention_probe.json` |
| Retained Hyperliquid chain | 24 × 3,885 bars; 11 RSI crashes / 0 confirmed signals; 4 crash days | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Canonical OKX 283d (cross-venue) | 8 trades; +9,159.69 PnL; 4 crash episodes / 5 days; `underpowered` | `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (2026-11-13T23:38:47Z) |
| OKX (cross-venue, NOT HL evidence) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [−4083.95, 24411.99] | `episode_edge_okx_full.json` (2026-11-13T23:38:47Z) |

## Bottlenecks (current) — what is removable vs not

1. **Cross-venue sample-size bottleneck — REMOVED.** The 34-symbol × 3.38-year OKX archive yields 19 signal-gate episodes / 23 crash days, above the ≥10 floor. This is real, non-synthetic, cross-venue data.
2. **Inference bottleneck — REMOVED.** C6-T3 produced the episode-block bootstrap, crash-day permutation, and portfolio placebo on the multi-year campaign (all artifacts on disk). Verdict: `underpowered` — the cross-venue edge is not established.
3. **Hyperliquid-native bottleneck — EXTERNAL, NOT agent-removable.** The public API serves 3,876/6,792 bars; the 1,013.2-day native archive does not exist in this environment. Only an operator-supplied verified archive unblocks it. Do not manufacture it.
4. **Handoff duplication — REMOVED.** This file is the only durable handoff.
5. **RSI O(n²) bottleneck — REMOVED.** Incremental cache makes multi-year scans practical. Do not revert.
6. **Epoch-timestamp metric bug — REMOVED.** Numeric epoch parsing is fixed. Do not revert.
7. **Retention decay / wasted re-fetch — REMOVED.** Fetch-unless-improved rule remains: do not re-fetch a degraded chain.
8. **Structural 0-trade funnel (canonical path) — RESOLVED as a known property.** The canonical gate produces 0 trades on the retained Hyperliquid partial chain; the multi-year cross-venue campaign is the active inference track.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- **C6 multi-year cross-venue archive:** `research_state/archives/okx_1h_multiyear_20230101_20260928/` (34 symbols, 32,808 bars each, `SOURCE.json`).
- **C6 cache/manifest:** `research_state/cache/okx_1h_multiyear_20230101_20260928/` (`provenance.json`, `candles/*.json`).
- **C6 universe:** `research_state/universe_okx_multiyear_verified.json`.
- **C6 census/power/campaign/closeout:** `crash_event_census_real_okx_multiyear.{json,md}`, `multiyear_cross_venue_power.{json,md}`, `campaign_results_real_okx_multiyear.{json,_metrics.json,_metrics.csv}`, `c6_closeout_20261114T234229Z.{json,md}`.
- **C6-T3 inference (dependence-aware):** `episode_edge_okx_multiyear.{json,md}` (bootstrap CI, episode audit, crash-day permutation), `placebo_portfolio_okx_multiyear.{json,md}` (full-portfolio placebo). Both canonical; do not re-run without a new stem.
- **Canonical OKX 283d:** `research_state/archives/okx_1h_full_20251220_20260928/` (63 symbols), `campaign_results_real_okx_full.json` (cross-venue; 8 trades; +9,159.69).
- **Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence** (flat synthetic; C4-T1 rejects it).
- **Retained Hyperliquid partial chain:** `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh

# Gates
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py

# C6 artifacts (already on disk; do not re-run without a documented reason)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_crash_event_census.py \
  --manifest research_state/cache/okx_1h_multiyear_20230101_20260928/provenance.json \
  --cache-dir research_state/cache/okx_1h_multiyear_20230101_20260928 \
  --universe-file research_state/universe_okx_multiyear_verified.json \
  --campaign research_state/campaign_results_real_okx_multiyear.json \
  --output-prefix crash_event_census_real_okx_multiyear
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_multiyear_cross_venue_power.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_multiyear_cross_venue_closeout.py

# Hyperliquid retention probe (mandatory, read-only)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py

# Tests for the engine/metrics fixes
PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q \
  tests/test_rsi_incremental_cache_20261114.py \
  tests/test_campaign_metrics_epoch_timestamps_20261114.py
```

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite.** C6-T3 is complete; the next session must either ingest an operator-supplied Hyperliquid archive or re-run the mandatory read-only retention probe and re-timestamp — never manufacture evidence.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** The multi-year campaign is `CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID`; `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run the canonical OKX 283d campaign or the multi-year campaign without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache or the epoch-timestamp parser fix.** Both are tested; reverting reintroduces the multi-hour bottleneck and the garbage 0.43-year horizon.
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr.** The honest multi-year cross-venue result is +5.07%/yr with a −33.57% max drawdown.

## Definition of done

Evidence-chain completeness **21/21** remains achieved. **Cross-venue validation is COMPLETE:** C6-T3 produced the episode-block bootstrap CI, crash-day permutation p, and portfolio placebo p on the multi-year campaign, plus a decision-memo C6 section with an explicit `underpowered` verdict. The honest cross-venue answer is that the strategy's edge is **not established** (bootstrap CI spans zero, P(>0)=0.66; permutation p=0.10; placebo p=0.40). **Hyperliquid-native** validation remains blocked on an operator archive and is not a substitute. Do not promote the +18.22% point estimate to evidence on its own.

**Next session's done:** either (a) an operator-supplied verified Hyperliquid archive ingested and run end-to-end with C6-T3 inference, a decision-memo Hyperliquid section and GO/STOP verdict, `verify_next_focus_campaign.py` PASS, gates 21/21 and 4/4 green, and this handoff re-timestamped; or (b) a refreshed retention probe, a re-verified `NO_GO`/`underpowered` state, gates green, and this handoff re-timestamped — with no fabricated evidence of any kind.

(End of file - total 152 lines)