# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T02:59:38Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session):** branch `main`; C1–C7 COMPLETE; **C7 COMPLETE — the cross-venue edge is now shown to be `FRAGILE_NOT_DECISION_GRADE`.** `scripts/session_gate.py` is **21/21 checks passed — DONE** and `scripts/verify_campaign_evidence.py` is **4/4 — EVIDENCE VERIFIED**. **C7 ran a robustness/fragility/achievable-power battery on the existing 34-symbol × 3.38y OKX multi-year campaign (no new data, no synthetic data).** The headline **+18,220.86 PnL (+5.07%/yr)** is an artifact: the **core buy leg loses −27,836.64 in every config**, the positive total is carried by the **optional rebound-short leg (+46,057.50)**, profit is concentrated in **2025 (+42,630) while 2023/2024 are both negative**, **dropping the single Oct-2025 episode flips the total to −11,285**, **5× slippage flips the total to −13,977**, and the **PDF-literal spec entry loses −55,057 over 113 trades**. The episode-mean t-stat is **0.477**; **~320 independent episodes** would be needed for a 95% CI excluding zero (only 19 exist). The **full 11-variant sensitivity grid** confirms the core buy leg is negative in **every** configuration (total positive only via the optional short leg; RSI-15 with 6 trades is negative overall). This is **CROSS-VENUE evidence, NOT Hyperliquid performance evidence**.

**META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, this file is already the current handoff and C7 is complete. Do not spend the session rewriting it. The next real task is the **C8 executable campaign** below — not another handoff and not waiting on the external archive.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T02:59:38Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1–C7 are COMPLETE. C7 is the heavy work that removes the old "underpowered waiting room" bottleneck: the multi-year cross-venue edge is now proven `FRAGILE_NOT_DECISION_GRADE` (core buy leg negative in every config, positive total carried by the optional rebound-short leg, 2025 + one episode carry everything, 5× slippage flips it negative, spec-literal entry loses −55k, ~320 episodes needed for significance). Do NOT repeat C1–C7, do NOT re-run the 42-trade campaign, do NOT re-run the C6-T3 inference battery, do NOT re-run the C7 battery without a new stem, and do NOT rewrite this handoff for its own sake.**

**The cross-venue track is now conclusively negative/fragile. The ONLY path to a positive (GO) verdict is Hyperliquid-native validation, which remains EXTERNAL and not agent-removable (public API serves only ~3,876/6,792 bars). Your job is NOT to wait on that archive. Your job is to execute the C8 campaign below, which is fully executable with existing resources and produces decision-grade evidence.**

### C8 — Executable next focus campaign (MANDATORY; heavy, no waiting)

Execute these in order. Each produces a NEW artifact stem. Never overwrite canonical artifacts.

1. **Complete the C7 sensitivity grid (residual Phase B variants) — DONE this session.** The full 11-variant grid is on disk as `research_state/multiyear_robustness_grid_20261115T013200Z.{json,md}` (slippage 2×/5×, funding 2×, spec-literal, RSI 15/25, target 5%/12%, time exit 24h/72h). **Result: the core buy leg is negative in every one of the 11 configs; the positive total is always the optional rebound-short leg; RSI-15 (6 trades) is negative overall.** Do not re-run; incorporate into the consolidated memo (step 3).

2. **Multi-venue fragility confirmation (heavy, executable) — BINANCE CAMPAIGN READY, BATTERIES NOT RUN.** The Binance USDT-M futures multi-year archive (33/34 symbols complete, 2023-01-01..2026-09-28, 32,808 bars/symbol) has been acquired and the canonical campaign has been run (`research_state/campaign_results_real_binance_um_multiyear.json`: 42 trades, +21,994 PnL, +6.03%/yr). **What remains:**
   a. Run C6-T3 episode-edge battery on Binance: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 --universe research_state/universe_binance_um_multiyear_verified.json --census research_state/crash_event_census_real_binance_um_multiyear.json --campaign research_state/campaign_results_real_binance_um_multiyear.json --venue-label "Binance UM" --out episode_edge_binance_um_multiyear`
   b. Run C7 robustness battery on Binance: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A B --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 --universe research_state/universe_binance_um_multiyear_verified.json --campaign research_state/campaign_results_real_binance_um_multiyear.json --census research_state/crash_event_census_real_binance_um_multiyear.json --episode-edge research_state/episode_edge_binance_um_multiyear.json --venue-label "Binance UM" --phase-label "C8-BINANCE" --out multiyear_robustness_battery_binance_um`
   **Question to answer:** is the buy-leg-negative fragility venue-universal, or OKX-specific? This is the single most informative remaining executable test. Do not relabel the result as Hyperliquid evidence.

3. **Consolidate a single decision-grade GO/STOP memo.** Write `research_state/decision_verdict_consolidated_<TS>Z.md` that maps ALL evidence (C6 bootstrap/permutation/placebo, C7 per-leg/sub-period/LOEO/power/cost-stress/entry, Binance C6-T3 + C7) against the 7 stop/go criteria and issues an explicit **`NO_GO`** (or `GO` only if a Hyperliquid-native archive later clears all criteria). State plainly: the cross-venue edge is not established and is fragile; the only positive path is Hyperliquid-native.

4. **If (and only if) an operator Hyperliquid archive lands:** ingest via `scripts/validate_hyperliquid_archive_intake.py` (must yield `ACCEPT_AS_EVIDENCE_CANDIDATE`), run the canonical campaign on the Hyperliquid-native chain, run the C6-T3 + C7 batteries on it, update the consolidated memo, and close the gates. The runbook is `research_state/operator_archive_request_20261114T221003Z.{json,md}`.

5. **Close the chain:** run `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py`, `scripts/session_gate.py` (21/21), and `scripts/verify_campaign_evidence.py` (4/4) green; re-timestamp this handoff.

**Binding constraints:**
- **Cross-venue evidence is NOT Hyperliquid evidence.** OKX/Binance/multi-year archives are `is_hyperliquid_venue_data=false`; never relabel.
- **No synthetic/fabricated data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **No new handoff/status files.** This is the single durable handoff.
- **No unnecessary re-runs.** The multi-year archive, campaign, C6-T3 inference, and C7 battery are canonical; do not re-run without a new artifact stem and a documented reason.
- **No relaxing the $5M volume floor or the spec-literal opt-in default.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/yr as validated edge.** The honest cross-venue result is fragile and not decision-grade.

**Definition of done for the next session:** (a) C8 steps 2–3 complete (Binance C6-T3 + C7 batteries, consolidated GO/STOP memo) with gates 21/21 and 4/4 green and this handoff re-timestamped; or (b) if an operator archive lands, a Hyperliquid-native verdict with C6-T3+C7 inference artifacts, the consolidated memo updated, gates green, and this handoff re-timestamped — with no fabricated evidence of any kind.

---

## What changed this session (bottleneck removal — C7)

### The old bottleneck
Every prior session closed on "blocked: operator archive required." That made the handoff a waiting room: agents re-probed the decaying Hyperliquid API, re-documented the same gap, and produced no new inference. The C6 verdict was `underpowered` but did not expose *where* the +18,220 came from or whether it was stable.

### The removed bottleneck (C7)
C7 ran a robustness/fragility/achievable-power battery on the **existing** multi-year OKX cache + campaign + census + episode-edge artifacts. No new data, no synthetic data. It converts `underpowered` into a decision-grade fragility verdict:
- **Per-leg (A1):** buy leg **−27,836.64** (30 trades); rebound-short leg **+46,057.50** (12 trades). Coin PnL −28,557.90; hedge PnL +59,980.18; rebound-short PnL −25,157.11; rebound hedge +30,426.71.
- **Exit reason (A2):** liquidated **−44,947.31** (12) vs time_exit +17,110.67 (18) vs target_rebound_short +46,057.50 (12).
- **Sub-period (A3):** 2023 −17,994; 2024 −15,575; 2025 +42,630; 2026 +9,160.
- **Leave-one-out (A5):** drop 2025 → **−24,409.53**; drop episode 14 (Oct-2025) → **−11,285.53**. Both flip the sign.
- **Concentration (A4):** 9 positive / 10 negative episodes; gross +64,520 / −46,299; HHI 0.12.
- **Achievable power (A6):** mean episode 958.99, SD 8,756.16, t=0.477; **~320 episodes** needed for CI excluding zero; power 7.6% at n=19.
- **Engine re-runs (B, full 11-variant grid):** baseline +18,220.86; **slippage 5× −13,976.73**; funding 2× +21,266.94; **spec-literal next-open −55,057.45 (113 trades)**; RSI 25 +14,608.93; RSI 15 **−8,703.37 (6 trades)**; target 5% +5,983.67; target 12% +12,449.16; time exit 24h +2,182.33; time exit 72h +20,827.22; slippage 2× +8,846.58. **Buy leg negative in every one of the 11 configs.** Artifacts: `multiyear_robustness_battery_full_20261115T011700Z.{json,md}` + `multiyear_robustness_grid_20261115T013200Z.{json,md}`.
- **Verdict:** `FRAGILE_NOT_DECISION_GRADE`. Artifact: `research_state/multiyear_robustness_battery_full_20261115T011700Z.{json,md}` (2026-11-15T01:31:34Z). Decision memo updated with a C7 section.

### Prior bottleneck removals still in force
- OKX public REST v5 `history-candles` serves real, gap-free hourly OHLCV back to 2023. The 34-symbol × 32,808-bar OKX multi-year archive (2023-01-01..2026-09-28) is on disk, ingested, and canonical.
- Binance Vision USDT-M futures monthly klines serve real, gap-free hourly OHLCV back to 2023. The 33-symbol × 32,808-bar Binance multi-year archive (2023-01-01..2026-09-28) is on disk, ingested, and canonical (MINA incomplete).
- RSI incremental cache (`src/strategy/crash_rebound.py`) makes multi-year scans practical (O(1) per bar). Do not revert.
- Epoch timestamp parsing (`src/metrics/campaign_metrics.py`) fixed; corrected horizon is 3.38 years, annualized return +5.07% (not the garbage 0.43y/47.6%).
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.
- Handoff duplication removed: this file is the only durable handoff.

---

## Verified state (as of 2026-11-15T02:59:38Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C6 multi-year OKX archive | 34 symbols × 32,808 bars, 0 gaps, `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 multi-year Binance archive | 33/34 symbols × 32,808 bars, 0 gaps (MINA incomplete), `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/binance_um_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 cache OKX | 34/34 complete; expected 32,808; window 2023-01-01..2026-09-28 | `research_state/cache/okx_1h_multiyear_20230101_20260928/provenance.json` |
| C6 cache Binance | 33/34 complete; expected 32,808; window 2023-01-01..2026-09-28 | `research_state/cache/binance_um_1h_multiyear_20230101_20260928/provenance.json` |
| C6 census OKX | 1,182 events / 782 volume-pass / 55 signal-gate / 42 trades matched | `crash_event_census_real_okx_multiyear.json` |
| C6 census Binance | 1,204 events / 1,198 volume-pass / 64 signal-gate / 42 trades matched | `crash_event_census_real_binance_um_multiyear.json` |
| C6 campaign OKX | 42 trades; +18,220.86 PnL; +18.22% total; +5.07%/yr; max DD −33.57%; Sharpe 0.10; win 50%; PF 1.33 | `campaign_results_real_okx_multiyear.json` |
| C6 campaign Binance | 42 trades; +21,994.06 PnL; +21.99% total; +6.03%/yr; max DD −32.41%; Sharpe 0.10; win 48%; PF 1.37 | `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | bootstrap 95% CI [−50,660.49, +99,295.03] P(>0)=0.6649; permutation p=0.1000; verdict `underpowered` | `episode_edge_okx_multiyear.{json,md}` (2026-11-15T00:35:31Z) |
| **C6-T3 episode edge Binance** | **NOT RUN** | *Required for C8 step 2a* |
| C6-T3 portfolio placebo OKX | p(placebo≥canonical)=0.4000; verdict `underpowered` | `placebo_portfolio_okx_multiyear.{json,md}` (2026-11-15T00:35:50Z) |
| **C7 robustness battery OKX** | **`FRAGILE_NOT_DECISION_GRADE`**: buy leg −27,836.64; short +46,057.50; 2025 +42,630 / 2023-24 negative; drop-2025 → −24,410; drop-ep14 → −11,286; t=0.477; ~320 episodes needed; slippage 5× → −13,977; spec-literal → −55,057 (113 trades) | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}` (2026-11-15T01:31:34Z) |
| **C7 full sensitivity grid OKX** | **11/11 variants: buy leg negative in every config**; total positive only via short leg; RSI-15 (6 trades) negative overall | `multiyear_robustness_grid_20261115T013200Z.{json,md}` (2026-11-15T01:43Z) |
| **C7 robustness battery Binance** | **NOT RUN** | *Required for C8 step 2b* |
| Decision memo C6+C7 | C6 section + C7 section (per-leg, sub-period, LOEO, power, Phase B, `FRAGILE_NOT_DECISION_GRADE`) | `research_state/decision_memo_okx_full.md` |
| Latest live retention probe | **2026-11-15T00:42:24Z**; 3,874/6,792 bars max; earliest 2026-04-20T14:00:00Z; 37/38 partial, 1 empty/error (KPEPE); verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` | `research_state/hyperliquid_retention_probe.json` |
| Retained Hyperliquid chain | 24 × 3,885 bars; 11 RSI crashes / 0 confirmed signals; 4 crash days | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Canonical OKX 283d (cross-venue) | 8 trades; +9,159.69 PnL; 4 crash episodes / 5 days; `underpowered` | `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (2026-11-13T23:38:47Z) |

---

## Bottlenecks (current) — what is removable vs not

1. **Cross-venue sample-size bottleneck — REMOVED.** 34-symbol × 3.38y OKX archive yields 19 episodes / 23 crash days (above the ≥10 floor). Real, non-synthetic, cross-venue. Binance adds 33-symbol × 3.38y with 23 episodes / 23 crash days.
2. **Inference bottleneck — REMOVED (C6-T3 on OKX).** Episode-block bootstrap, crash-day permutation, and portfolio placebo are on disk for OKX. Verdict `underpowered`. **Binance C6-T3 NOT RUN** — required for C8.
3. **Fragility/robustness bottleneck — REMOVED (C7 on OKX).** Per-leg, sub-period, leave-one-out, achievable-power, cost stress, and entry decomposition show the headline is fragile and not decision-grade. **Binance C7 NOT RUN** — required for C8.
4. **Hyperliquid-native bottleneck — EXTERNAL, NOT agent-removable.** The public API serves ~3,876/6,792 bars; the 1,013.2-day native archive does not exist here. Only an operator-supplied verified archive unblocks it. **Do not wait on it — execute C8.**
5. **Handoff duplication — REMOVED.** This file is the only durable handoff.
6. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
7. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
8. **Retention decay / wasted re-fetch — REMOVED.** Do not re-fetch a degraded chain.
9. **Structural 0-trade funnel (canonical path) — RESOLVED as a known property.** The canonical gate produces 0 trades on the retained Hyperliquid partial chain; the multi-year cross-venue campaign is the active inference track.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- **C6 multi-year cross-venue archive OKX (C6-T1):** `research_state/archives/okx_1h_multiyear_20230101_20260928/` (34 symbols, 32,808 bars each, `SOURCE.json`).
- **C6 multi-year cross-venue archive Binance (C8 step 2 pre-requisite):** `research_state/archives/binance_um_1h_multiyear_20230101_20260928/` (33/34 symbols, 32,808 bars each, `SOURCE.json`; MINA incomplete).
- **C6 cache/manifest OKX:** `research_state/cache/okx_1h_multiyear_20230101_20260928/` (`provenance.json`, `candles/*.json`).
- **C6 cache/manifest Binance:** `research_state/cache/binance_um_1h_multiyear_20230101_20260928/` (`provenance.json`, `candles/*.json`).
- **C6 universe OKX:** `research_state/universe_okx_multiyear_verified.json`.
- **C6 universe Binance:** `research_state/universe_binance_um_multiyear_verified.json`.
- **C6 census/power/campaign/closeout OKX:** `crash_event_census_real_okx_multiyear.{json,md}`, `multiyear_cross_venue_power.{json,md}`, `campaign_results_real_okx_multiyear.{json,_metrics.json,_metrics.csv}`, `c6_closeout_20261114T234229Z.{json,md}`.
- **C6 census/campaign Binance:** `crash_event_census_real_binance_um_multiyear.{json,md}`, `campaign_results_real_binance_um_multiyear.{json,_metrics.json,_metrics.csv}`.
- **C6-T3 inference (dependence-aware) OKX:** `episode_edge_okx_multiyear.{json,md}` (bootstrap CI, episode audit, crash-day permutation), `placebo_portfolio_okx_multiyear.{json,md}` (full-portfolio placebo). Both canonical; do not re-run without a new stem.
- **C7 robustness battery OKX:** `multiyear_robustness_battery_full_20261115T011700Z.{json,md}` (per-leg, sub-period, LOEO, achievable-power, Phase B) and `multiyear_robustness_grid_20261115T013200Z.{json,md}` (full 11-variant sensitivity grid). Canonical; do not re-run without a new stem.
- **Canonical OKX 283d:** `research_state/archives/okx_1h_full_20251220_20260928/` (63 symbols), `campaign_results_real_okx_full.json` (cross-venue; 8 trades; +9,159.69).
- **Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence** (flat synthetic; C4-T1 rejects it).
- **Retained Hyperliquid partial chain:** `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh

# Gates
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py

# C7 battery OKX (already done; do not re-run)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A --out multiyear_robustness_battery
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A B \
  --variants baseline slippage_5x funding_2x entry_spec_literal_next_open rsi_threshold_25 \
  --out multiyear_robustness_battery_full_<TS>Z

# C8 step 2a: C6-T3 episode-edge on Binance
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 \
  --universe research_state/universe_binance_um_multiyear_verified.json \
  --census research_state/crash_event_census_real_binance_um_multiyear.json \
  --campaign research_state/campaign_results_real_binance_um_multiyear.json \
  --venue-label "Binance UM" \
  --out episode_edge_binance_um_multiyear

# C8 step 2b: C7 robustness battery on Binance
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py --phases A B \
  --cache-dir research_state/cache/binance_um_1h_multiyear_20230101_20260928 \
  --universe research_state/universe_binance_um_multiyear_verified.json \
  --campaign research_state/campaign_results_real_binance_um_multiyear.json \
  --census research_state/crash_event_census_real_binance_um_multiyear.json \
  --episode-edge research_state/episode_edge_binance_um_multiyear.json \
  --venue-label "Binance UM" \
  --phase-label "C8-BINANCE" \
  --out multiyear_robustness_battery_binance_um

# C6 artifacts OKX (already on disk; do not re-run without a documented reason)
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

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite.** C7 is complete; the next session must execute the C8 campaign (Binance C6-T3 + C7 batteries, consolidated GO/STOP memo) or ingest an operator-supplied Hyperliquid archive — never manufacture evidence.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** The multi-year campaign is `CROSS_VENUE_MULTIYEAR_NOT_HYPERLIQUID`; `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run the canonical OKX 283d campaign, the multi-year campaign, the C6-T3 battery, or the C7 battery without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache or the epoch-timestamp parser fix.** Both are tested; reverting reintroduces the multi-hour bottleneck and the garbage 0.43-year horizon.
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/yr as validated edge.** The honest cross-venue result is `FRAGILE_NOT_DECISION_GRADE` (core buy leg negative, carried by the optional short leg, concentrated in 2025 and one episode, ~320 episodes needed for significance).

---

## Definition of done

Evidence-chain completeness **21/21** remains achieved. **Cross-venue validation on OKX is COMPLETE and now decision-grade negative:** C6-T3 produced the episode-block bootstrap CI, crash-day permutation p, and portfolio placebo p on the multi-year campaign; C7 added per-leg/sub-period/LOEO/achievable-power/cost-stress/entry decomposition and the `FRAGILE_NOT_DECISION_GRADE` verdict. The honest cross-venue answer is that the strategy's edge is **not established and is fragile**: the core buy leg loses money in every config, the positive total is carried by the optional rebound-short leg, profit is concentrated in 2025 and one episode, 5× slippage flips the total negative, and the PDF-literal entry path loses −55k. **Hyperliquid-native** validation remains blocked on an operator archive and is the only path to a positive verdict. Do not promote the +18.22% point estimate to evidence on its own.

**Next session's done:** (a) C8 steps 2–3 complete (Binance C6-T3 + C7 batteries, consolidated GO/STOP memo) with gates 21/21 and 4/4 green and this handoff re-timestamped; or (b) an operator-supplied verified Hyperliquid archive ingested and run end-to-end with C6-T3+C7 inference, the consolidated memo updated, gates green, and this handoff re-timestamped — with no fabricated evidence of any kind.

(End of file)