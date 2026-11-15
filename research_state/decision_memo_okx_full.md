# Decision Memo — Crash-Rebound Strategy (Real OKX 283d canonical evidence)

**Generated (UTC):** 2026-11-13T21:48:59Z
**Updated (UTC):** 2026-11-15T00:40:25Z (C6-T3 dependence-aware inference on the multi-year cross-venue campaign; gates 21/21 and 4/4 green; evidence gap unchanged)
**Status:** `underpowered` / **not decision-grade** — do not allocate capital on this evidence.
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

**Current status (2026-11-14T22:10:03Z):** C1/C2/C3/C4/C5-T2/C5-T3/C5-T4 are complete; the session gate is **21/21 checks passed** and the evidence verifier is **4/4 — EVIDENCE VERIFIED**. C5-T2 produced the binding operator archive request v2 (multi-year window: 2023-12-20T17:19:21Z..2026-09-28T23:00:00Z, 1,013.2 days, 24,319 bars/symbol, ≥24 symbols, ≥10 distinct crash days). C5-T3 proved the full-validation orchestrator end-to-end (all 6 steps PASS; placeholder rejected, truncated rejected, flat fixture not evidence). C5-T4 refreshed the retention probe (3,877/6,792 bars, earliest 2026-04-20T11:00:00Z, strictly worse than retained), updated coverage and this memo, and re-ran gates green. The verdict remains **`underpowered` / not decision-grade**. The evidence gap is unchanged and external: the public Hyperliquid API serves only 3,877/6,792 hourly bars (still decaying), so the 1,013.2-day multi-year archive required for 80% power does not exist in this environment. No session may close without C5-T2/T4 artifacts + coverage/memo refresh + gates 21/21 and 4/4 green.

## Decision question

Is the canonical crash-rebound portfolio result distinguishable from noise, and is it
investable under the spec's gates, sizing and risk limits?

**Answer: no, not with the current sample.** The canonical +9.16% return is a small-sample
outcome of a gate-passing event pool. The exact full-portfolio placebo places it at the
**45th percentile** of all gate-preserving 8-of-11 admission subsets. The result is not
distinguishable from a random admission/cap/occupancy draw.

## C6 — Multi-year cross-venue dependence-aware inference (2026-11-15T00:36:05Z)

C6-T1/T2 acquired a real, gap-free, non-synthetic **34-symbol × 32,808-bar OKX multi-year
archive (2023-01-01..2026-09-28)** and ran it through the real portfolio engine. C6-T3 applies
the Phase O dependence-aware battery to that campaign. **This is CROSS-VENUE evidence, NOT
Hyperliquid performance evidence.** The canonical OKX 283d section above is retained as-is.

### C6 canonical campaign metrics
- Window: 2023-01-01T00:00:00Z .. 2026-09-28T23:00:00Z (3.38 years), 34 symbols.
- Census: **1,182 RSI(21)<20 events → 782 volume-pass → 55 signal-gate → 42 trades matched**.
- Power: **19 signal-gate crash episodes over 23 distinct crash days** (largest episode 9 events, 16.4%). Far above the ≥10-episode floor.
- Total PnL: **+18,220.86**; **+18.22% total**; **+5.07%/yr** over 3.38y; max DD **−33.57%**; Sharpe **0.10**; win rate **50%**; profit factor **1.33**; 17 positive / 14 negative months.
- Artifact: `research_state/campaign_results_real_okx_multiyear.json` (sha256 `7d32720119597124f152b437012e8cdb88636bf0dedd72f25d4a69806676cdd1`).

### C6-T3 dependence-aware battery
1. **Episode-block bootstrap (98h single-linkage, 19 blocks, 20,000 resamples, seed 20261114):**
   95% CI total PnL **[−50,660.49, +99,295.03]**; mean 18,156.53; median 15,844.59;
   **P(total PnL > 0) = 0.6649**. The interval spans zero. The effective independent sample is
   19 crash episodes, not 42 trades.
2. **Crash-day conditional temporal-edge permutation (20 seeded draws, seed 20261114):**
   event bars redrawn from the real 1,182-bar RSI(21)<20 census, per-symbol multiplicity
   preserved, real engine per draw. Null mean 6,324.41; canonical at the **90.00th percentile**;
   **p(placebo ≥ canonical) = 0.1000** (2/20). Exact enumeration infeasible; deterministic seeded
   subset, seed and count documented.
3. **Exact/conditioned full-portfolio placebo (55 signal-gate pool, choose 42, 20 runs, seed 20261114):**
   mean 13,260.48; median 14,765.05; p05 −5,670.99; p95 +36,069.88; canonical at the
   **60.00th percentile**; **p(placebo ≥ canonical) = 0.4000**; P(placebo > 0) = 0.9000.
   C(55,42) infeasible to enumerate exactly; deterministic seeded subset documented.
- Artifacts: `research_state/episode_edge_okx_multiyear.{json,md}` (generated 2026-11-15T00:35:31Z),
  `research_state/placebo_portfolio_okx_multiyear.{json,md}` (generated 2026-11-15T00:35:50Z).

### C6 verdict
**`underpowered` / not decision-grade.** The +18.22% point estimate does **not** clear any of
the three stop/go criteria: the episode-block bootstrap 95% CI spans zero (P(>0)=0.66), the
crash-day permutation p = 0.10, and the portfolio placebo p = 0.40. None is below 0.05. The
multi-year window supplies **power for a cross-venue verdict** (19 episodes ≫ 10 floor), and the
honest answer is that the strategy's edge is **not established** on this evidence: the result is
inside both the episode-block and the admission-placebo distributions. **Do not quote +5.07%/yr
as validated edge; do not allocate capital.** The binding constraint remains that this is
cross-venue OKX, not Hyperliquid-native performance evidence. Hyperliquid-native validation is
still external and requires an operator-supplied verified archive.

## Canonical result (fixed; do not re-run or overwrite)

- Window: 2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z (283 days), 6,792 bars/symbol.
- Universe: 54 OKX symbols passing the trailing-24h ≥ $5M volume gate.
- Trades: **8** (4W/4L), **5/54 symbols**.
- Total PnL: **9,159.691934882958**; +9.1597% / +22.5995% annualized over 0.4301y.
- Worst drawdown: **−2.0275%**.
- Artifact: `research_state/campaign_results_real_okx_full.json`
  sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- This is **OKX cross-venue evidence**, not Hyperliquid performance evidence.

## Evidence ledger

| Evidence | Result | Read |
|---|---|---|
| Phase L trade bootstrap (10,000) | 95% CI PnL **[−930.66, +19152.38]**, P(>0)=0.9633 | CI crosses 0 → underpowered. |
| Phase L sign-flip (2^8=256) | one-sided p **0.09375** | Not significant at 5%. |
| Symbol-block bootstrap (2,000) | 95% CI **[−2026.39, 19249.18]**, P(>0)=**0.942** | Dependence-aware but wide; n=5 symbols. |
| Per-event exit null | P(null ≥ 9159.69)=**0.9865 / 0.985** | **Invalid comparison** (see below). |
| **Exact full-portfolio placebo (165/165 subsets)** | mean **8,746.21**, median **9,287.25**, p05 **5,807.36**, p95 **11,360.11**, min **3,988.13**, max **11,795.92** | Canonical at **45.45th percentile**; P(placebo ≥ canonical)=**0.5515**. |
| Full-portfolio placebo P(>0) | **1.0000** (all 165 subsets positive) | Conditional on the observed 11-event pool; not evidence of temporal edge. |
| Walk-forward (chronological) | first half 4 trades +1,070.36; second half 4 trades +8,089.33 | Both positive but clustered Jan–May; directional only, no refit. |
| Phase N leave-one-symbol-out | 5/5 positive; min 3,495.11, max 10,796.53 | No single symbol carries the result; SOL is the largest PnL contributor. |
| Phase N leave-one-trade-out | 8/8 positive; min 7,485.96, max 13,154.73 | No single trade is solely responsible. |
| Phase N concentration | HHI 0.2517; effective symbols 3.97; top trade 25.95% of gross | Still concentrated; n=5 traded symbols. |
| Phase N power projection | First bootstrap CI > 0 at **10 trades / 8 symbols**; 80% power at **23 trades / 17 symbols** | The sample is far below even the minimum power target. |
| Phase N expanding-window refit | 3 evaluable blocks; refit OOS +10,815.92 vs canonical incremental +9,159.69 | Directionally consistent but only 3 evaluable blocks; not proof. |
| **Hyperliquid public API partial probe** | API returns **3,877** of 6,792 bars (2026-04-20T11:00Z..2026-09-28T23:00Z); full 283d window **blocked** | Full Hyperliquid-native evidence requires an operator-supplied verified archive. |
| **Hyperliquid partial campaign (NOT_EVIDENCE)** | 12 complete symbols, 3,900 bars each; **0 trades, 0 PnL** | Partial window only; `performance_evidence=false`; not spec evidence. |
| Hyperliquid partial crash census | 12 symbols / 46,800 bars; **8 RSI(21)<20 events, 0 confirmed signals** | Rare-event strategy; the 163-day partial window has no trade to evaluate. |
| Risk budget (existing sweeps) | `rsi25_maxpos8` +23.44% / **−18.34% DD**, 33 trades; baseline +9.16% / −2.03% DD, 8 trades | Return is a risk-budget trade; never quote +23% without −18% DD. |
| **Phase O episode audit** | 11 gate-passing events collapse into **4 crash episodes** over **5 distinct crash days**; largest episode 4/11 events (36.4%) | The effective independent sample is **4 crashes / 5 days**, not 8 trades or 11 events. Every trade-level independence assumption overstates the sample. |
| **Phase O conditional temporal-edge permutation** | Event bars redrawn from the real 342-bar RSI(21)<20 census, per-symbol multiplicity preserved, real engine per draw; canonical at the **85th percentile**; p(placebo ≥ canonical)=**0.15** | The canonical PnL is largely explained by *which crash days occurred*. Timing is not distinguishable from crash-day luck. |
| **Phase O episode-block bootstrap** | 95% CI **[−4,083.95, 24,411.99]**, P(total PnL>0)=**0.8754**, resampled in 4 episode blocks | Dependence-aware interval spans zero. The trade-level bootstrap (Phase L) CI was narrower only because it assumed 8 independent trades. |

## The binding constraint: independent crash episodes

Every earlier inference in this memo is conditioned on the observed 11 gate-passing
events and treats trades (or events) as independent draws. Phase O measures what those
events actually are. Linked at the spec's own 98-hour holding horizon (50h max buy hold +
48h max rebound short), the 11 events form **4 crash episodes** spread over **5 distinct
crash days**:

| Episode | Window (UTC) | Events | Symbols | Distinct days | Episode PnL |
|---|---|---|---|---|---|
| 0 | 2026-01-19T02:00Z .. 2026-01-20T19:00Z | 4 | ETH, SOL | 2 | +3,040.34 |
| 1 | 2026-01-25T20:00Z | 2 | LINK, SOL | 1 | **−1,969.97** |
| 2 | 2026-01-31T18:00Z .. 2026-01-31T21:00Z | 4 | AVAX, BCH, SOL | 1 | +8,161.33 |
| 3 | 2026-05-18T08:00Z | 1 | BCH | 1 | **−72.00** |

**Two of the four episodes lost money.** The canonical +9,159.69 is the sum of four
realized crash episodes, three of which are in a single 13-day January stretch. The
correct denominator for any claim about this strategy is **4 crashes**, not 8 trades and
not 11 events.

### Conditional temporal-edge test (new; the gap Phase M could not close)

The Phase M placebo holds event *timing* fixed and varies admission. Phase O does the
opposite: it holds the number of events, the per-symbol multiplicity and the crash-day
calendar fixed, and redraws *which* real RSI(21)<20 bars the events sit on. Each draw is
run through the real portfolio engine. This is the first test in the chain that can
detect a timing edge, and it does not find one:

- Canonical PnL sits at the **85th percentile** of crash-day-timed alternatives.
- **p(placebo ≥ canonical) = 0.15.**
- Null total PnL: mean 5,234, median 4,858, p05 −250, p95 10,948; P(null > 0) = 0.875.

The canonical result is *better than typical* but not distinguishable from what you get
by dropping the same crash events on other real crash bars. **This is the honest answer
to "is there a temporal edge?" — not yet demonstrable.**

### Dependence-aware power requirement (replaces the trade-level projection)

Resampling trades as if independent understates variance, because trades inside an
episode co-move. The episode-block bootstrap gives the correct interval:
**95% CI [−4,083.95, 24,411.99]**, P(total PnL > 0) = **0.8754**. Extrapolating the
observed episode-total dispersion, the interval does not exclude zero at any episode count
up to 20, because two of four episodes are negative. **The binding power requirement is
therefore in independent crash episodes, not trades: the strategy needs a materially
longer crash history in which most episodes are positive.** No amount of re-slicing the
283-day OKX window can supply this; only a longer, Hyperliquid-native history can.

## Why the per-event null is not a portfolio null

The per-event simulation sizes each trade at 1.25% of 24h volume with **no portfolio gross
cap**. Desired notionals reach **$7.29M** (ETH), while the canonical portfolio caps gross
exposure at **$120k** (120% of $100k) and admits only a handful of concurrent positions.
The per-event null mean (~$232k) is therefore a sizing artifact, not a valid comparison to
the 8-trade portfolio PnL. The exact full-portfolio placebo fixes this by running the real
portfolio engine with the same gates, sizing, cap, occupancy, ETH hedge, fees, funding and
liquidation, varying only which gate-passing events are allowed to trade.

## Full-portfolio placebo method (exact, no Monte Carlo)

- The J1 census enumerates all 342 RSI(21)<20 events; 187 pass the volume gate, 39 pass
  bounce, 89 pass regime/price, and **11** pass every signal gate.
- The canonical run admitted **8** of those 11; 3 were blocked by one-position-per-coin.
- Every 8-of-11 subset is run through the real portfolio engine with all other signals
  masked. There are C(11,8)=**165** subsets, so the null is enumerated exactly.
- The memoized `generate_signal` path is exact: it reproduces the canonical campaign to the
  cent (8 trades, PnL 9159.691934882958) in ~0.25s instead of ~527s.
- Artifact: `research_state/placebo_portfolio_okx_full.{json,md}`
  sha256 `6b82dcb61fc6ccbec0ba8aa0c1069ab2c7c6be2dc8a704484c28520f2e981a97` /
  `fef74f99922e919abfda78783fb37dace0d3773f0ee3bd941e7b470b311fb868`.

## Verdict

**`underpowered` — not decision-grade.**

- The canonical result is **inside** the exact full-portfolio placebo distribution
  (45th percentile; P(placebo ≥ canonical)=0.5515). There is no evidence that the specific
  8 admitted trades are special beyond admission/cap/occupancy selection.
- **The 11 events are 4 crash episodes over 5 crash days; 2 of 4 episodes lost money.**
  Every independence-based statistic in this memo overstates the effective sample.
- **Temporal edge is not established:** p(placebo ≥ canonical)=**0.15** under a
  crash-day-conditioned permutation that preserves event count and per-symbol multiplicity.
- The sample has **8 trades, 5 symbols, 4 crash episodes, 283 days**. No bootstrap or
  placebo can create power that the sample does not contain.
- The +9.16% return must not be presented as validated edge, and the strategy must not be
  funded on this evidence.

## Hyperliquid-native status (updated 2026-11-14T22:10:03Z; C5-T2/T4 complete; supersedes all earlier Hyperliquid blocks below)

- **C5-T2 — Operator archive request v2 with machine-checkable acceptance (HEAVY, MANDATORY).**
  Artifacts: `research_state/operator_archive_request_20261114T221003Z.{json,md}`. Binding
  window: **2023-12-20T17:19:21Z .. 2026-09-28T23:00:00Z (1,013.2 days, 24,319 hourly bars/symbol)**
  at observed episode rate 0.012355/day for **80% power** (≥10 independent crash episodes +
  episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio
  placebo p<0.05). Requirements: ≥24 symbols, ≥10 distinct crash days, Hyperliquid-native
  provenance, per-file SHA256, non-synthetic. Includes exact command sequence (7 steps),
  pass/fail predicates for every field, and the explicit statement that **the 283-day spec
  window is 2.78× too short** (0.33% power per C3-T3). Updated `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`
  to point at v2 (v1 retained as history).
- **C5-T3 — Full-validation orchestrator (COMPLETE).**
  `scripts/run_full_validation_campaign.py` on disk. Dry-run readiness:
  `research_state/full_validation_pipeline_readiness_20261114T212055Z.{json,md}` — all **6 steps
  PASS**; placeholder rejected, truncated fixture rejected, flat fixture accepted only as
  `ACCEPT_FIXTURE_NON_EVIDENCE` (`is_market_data=false`, `is_evidence=false`,
  `performance_evidence=false`). The orchestrator is ready to run the moment a C4-T1
  `ACCEPT_AS_EVIDENCE_CANDIDATE` archive lands.
- **C5-T4 — Close the chain (MANDATORY).**
  - Retention probe refreshed: `scripts/probe_hyperliquid_blocker.py` →
    `research_state/hyperliquid_retention_probe.json` (2026-11-14T21:23:00Z, sha256
    `27adec869b4593f472d92049cd62d6c1273804027730836866e26fe3827d6927`): **3,877 / 6,792**
    bars, **2,915 missing**, earliest served **2026-04-20T11:00:00Z**, 235 perps / 37 pass
    $5M gate / 37 probed, unprobeable `['KPEPE', '...']`. **KEEP_RETAINED** (retained chain
    24 × 3,885 bars, start 2026-04-20T03:00:00Z is strictly better; no fetch).
  - Coverage updated: `research_state/hyperliquid_universe_coverage.json` with C5 artifacts
    and integer counts (see `c5_session_artifacts` section).
  - Decision memo updated: this section with C5 state and standing **`NO_GO`**.
  - Gates re-run green:
    ```
    test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
    PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                  # 21/21
    PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py      # 4/4
    ```
  - Handoff re-timestamped to 2026-11-14T22:10:03Z.

## C4 Decision Lock (retained from 2026-11-14T20:47:08Z)

- **C4-T1 — archive intake gate is executable and fail-closed.**
  `scripts/validate_hyperliquid_archive_intake.py` →
  `research_state/archive_intake_validation_20261114T202957Z.{json,md}`. Verdict on the
  committed placeholder parquet: **`REJECT_NOT_EVIDENCE`** (flat series, 1/6,792 distinct
  signature per symbol). Built-in self-test **4/4 expectations met**: flat full-window
  fixture is rejected without `--allow-synthetic-fixture` and accepted only as
  `ACCEPT_FIXTURE_NON_EVIDENCE` (`is_market_data=false`, `is_evidence=false`,
  `performance_evidence=false`) with it; a truncated 300-bar fixture is **rejected even
  with the opt-in**; the placeholder is rejected even with the opt-in.
- **C4-T2 — multi-year protocol and executed power calculation.**
  `research_state/multi_year_validation_protocol_20261114T203040Z.{json,md}`. At the
  observed traded-episode rate (0.012355/day), **80% power for ≥10 independent crash
  episodes requires 1,013.2 days (~2.78 years) = 24,319 hourly bars/symbol** (×24 symbols
  = 583,656 bars). The 283-day spec window is 2.78× too short; the crash-day rate needs
  404.9 days. Protocol binds: primary endpoint episode-level net PnL, 72h crash-day
  clustering, crash-day block bootstrap (10,000), crash-day permutation (10,000),
  full-portfolio placebo, Holm–Bonferroni across 3 endpoints.
- **C4-T3 — execution-friction stress on the retained exploratory path.**
  `research_state/execution_friction_stress_hyperliquid_20261114T204632Z.{json,md,csv}`,
  label `NOT_EVIDENCE_EXECUTION_FRICTION`, `performance_evidence=false`,
  `canonical_baseline_changed=false`. 9 variants on the same retained chain: **all 9 have
  negative total PnL**, range **−7,945.88 .. −501.77** vs baseline −2,670.76; trade count
  is 2 in every variant; the no-ETH-hedge variant is worst (−7,945.88), slippage 10× is
  −5,062.61. This is a fragility check on a 2-trade path, never performance evidence.

## Hyperliquid-native status (updated 2026-11-14T16:26:00Z; supersedes all earlier Hyperliquid blocks below)

- **Full 283-day window: BLOCKED, and now measurably worse.** Live re-probe this session
  (`research_state/hyperliquid_retention_probe.json`, **2026-11-14T16:19:34Z**, sha256
  `b6ea031bf4f02bec4ea62707124878e59b7c1fa44d17dbb389adef5398e10a43`) served **3,883 of
  6,792** hourly bars; **2,909 missing**; earliest served **2026-04-20T05:00:00Z**. Universe:
  **235 perps / 29 pass the $5M trailing-24h gate / 29 probed**; unprobeable/empty =
  `['KPEPE']`. Verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`. The
  retained chain (`hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z`,
  24 complete × 3,885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) is still strictly
  better than anything the live API serves, so it is kept; no fresh full-universe fetch was
  run. A full-window campaign requires an operator-supplied verified Hyperliquid-native
  archive following `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.
- **Structural 0-trade funnel is now explained by a real-engine run, not prose.** The
  canonical implementation requires a **same-bar** `confirm_rebound` candle before entry
  (`src/strategy/crash_rebound.py`), while the spec's entry rule is "buy at next hourly
  open" after the RSI(21)<20 crash close with no confirmation candle
  (`research_state/strategy_spec.md`). Funnel on the retained chain (real bars, real
  generator): **29 RSI<20 hours → 11 pass the trailing-24h ≥ $5M volume floor → 0 same-bar
  confirm → 5 next-bar confirm → 0 canonical `generate_signal`**. With the opt-in
  `entry_spec_literal_next_open=True` flag (default **False**; bypasses ONLY the same-bar
  confirmation; every other gate, the 120% cap, ETH hedge, fees, funding and liquidation
  checks unchanged) the same retained chain yields **8 spec-literal signals → 2 real-engine
  trades, total PnL −2,670.76, win rate 0.50, max drawdown −3,230.12, 1 positive / 1
  negative month**. Artifact:
  `research_state/campaign_results_real_hyperliquid_exploratory_next_open_20261114T162212Z.json`
  (+ `_metrics.json`/`.csv`) and
  `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261114T162541Z.{json,md}`,
  labeled `NOT_EVIDENCE_EXPLORATORY_FANOUT`, `performance_evidence=false`,
  `canonical_baseline_changed=false`.
- **This does NOT make the strategy investable.** Two trades from **2 distinct crash days**
  (2026-05-28 BCH, 2026-06-02 BTC) are **2 independent crash episodes at most**; one of the
  two lost ~$9,990. The exploratory result is a structural-funnel explanation and a
  power-reality check, never Hyperliquid performance evidence, validation, or a capital
  allocation basis. Verdict remains **`underpowered`**.
- **Power-based sample-size target (binding unit = independent crash episodes).** The
  retained window contains only **4 distinct crash days** (2026-05-28, 06-02, 06-05,
  06-24). Even a full-window spec-literal run cannot be promoted to evidence without **≥ 10
  independent crash episodes** whose **episode-block bootstrap 95% CI excludes 0**, plus the
  crash-day-conditioned temporal-edge permutation p < 0.05 and the exact full-portfolio
  placebo p < 0.05. Because the public API serves at most ~3,883 of 6,792 bars and that
  window is still decaying, the episode target is **not reachable from the public API** at
  any amount of re-slicing; only the operator archive path (or a longer verified
  Hyperliquid-native history) can supply it.
- **Session gate 21/21 — DONE; evidence verifier 4/4 — EVIDENCE VERIFIED** on the refreshed
  artifacts.
- **Do not cite the exploratory run as Hyperliquid performance evidence.** It is a
  structural-funnel and power-reality check only.

## Stop / go criteria (explicit)

**GO only if all of the following hold on Hyperliquid-native data:**

1. The full 283-day Hyperliquid window is acquired with verified provenance and no
   placeholder/flat series (see `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. The canonical campaign produces at least **10 trades across ≥ 8 symbols** (the Phase N
   minimum for the trade bootstrap CI to exclude 0), with **≥ 23 trades across ≥ 17 symbols**
   as the stronger 80%-power target. A blanket "≥100 trades" requirement is not a valid
   power target for this rare-event strategy: 46,800 Hyperliquid partial-window bars produced
   only 8 RSI crashes and 0 confirmed signals. Use the pre-registered power target above.
   **Superseding refinement (Phase O): the binding unit is the independent crash episode.**
   The run must produce **≥ 10 independent crash episodes with a positive episode-level
   bootstrap CI**; 23 trades drawn from 4 episodes would not satisfy this.
3. The trade bootstrap 95% CI excludes 0 **after** multiple-testing correction, and the
   sign-flip p < 0.05.
4. The episode-block bootstrap 95% CI excludes 0 (Phase O method).
5. The crash-day-conditioned temporal-edge permutation p(placebo ≥ real) < 0.05 (Phase O
   method).
6. The exact full-portfolio placebo p(placebo ≥ real) < 0.05 on the Hyperliquid run.
7. Worst drawdown is within the mandate (the baseline −2.03% DD is acceptable; the
   `rsi25_maxpos8` −18.34% DD is not, unless explicitly risk-budgeted).

**STOP / do not fund if:**

- Hyperliquid-native data cannot be acquired or is synthetic/flat/placeholder.
- The Hyperliquid result remains inside its full-portfolio placebo distribution.
- The result depends on the `rsi25_maxpos8` risk budget without disclosing the −18.34% DD.
- Anyone reports the per-event null as a portfolio test.

## Immediate next work (status after this memo)

1. **Hyperliquid-native acquisition and campaign — BLOCKED on full data.** The public API
   cannot serve the full 283-day window (3,877 of 6,792 bars at 2026-11-14T21:23:00Z, and
   decaying). The only decision-grade path is an operator-supplied verified archive; use the
   **C5-T2 v2 runbook** (`research_state/operator_archive_request_20261114T221003Z.md`).
   Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`
   (flat synthetic placeholder) as evidence.
2. **C5-T1 — Full validation orchestrator (READY, waiting for operator archive).**
   When C4-T1 yields `ACCEPT_AS_EVIDENCE_CANDIDATE`, run:
   `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_full_validation_campaign.py`
   (dry-run proved 6/6 steps PASS; placeholder rejected, truncated rejected).
3. **Spec-literal next-open adjudication — DONE (NOT_EVIDENCE, 2026-11-14T16:22Z).** The
   structural 0-trade funnel was executed through the real engine with the opt-in
   `entry_spec_literal_next_open=True` flag: **8 spec-literal signals → 2 trades, total PnL
   −2,670.76** on the retained chain. This closes the "0 trades is a scanner bug" question:
   the canonical gate, not the data, produces the 0. It does not create power — 2 trades / 2
   crash days is still `underpowered`. Do not re-run this without a new retained chain.
4. **Episode-aware audit on the exploratory run — NOT APPLICABLE at n=2.** Two trades on two
   crash days cannot support an episode-block bootstrap or a crash-day permutation; running
   one would be manufactured inference. Recorded as not applicable; the binding requirement
   is ≥ 10 independent crash episodes, which the retained window (4 crash days) cannot supply.
5. **Robustness stress / power analysis — DONE.** Phase N LOO/LOTO, concentration,
   bootstrap power projection, and expanding-window refit are complete and recorded in
   `research_state/robustness_stress_okx_full.{json,md}`. The verdict remains `underpowered`.
6. **Do not regress:** keep the done-gate green; do not re-run the canonical campaign,
   J1/J2/K/L, or re-acquire OKX; do not fabricate data; do not relax the $5M gate; do not
   create a second handoff; do not flip `entry_spec_literal_next_open` to True by default.
7. **Dependence audit and temporal-edge test — DONE (Phase O).** The 11 events are 4 crash
   episodes over 5 crash days (2 episodes negative); crash-day-conditioned permutation gives
   p(placebo ≥ canonical)=0.15; episode-block bootstrap CI [−4,083.95, 24,411.99]. Artifacts:
   `research_state/episode_edge_okx_full.{json,md}`. Verdict remains `underpowered`.
8. **Phase O (Hyperliquid partial) — NOT APPLICABLE, recorded honestly.** The canonical
   partial window produced zero confirmed signals, zero trades, and therefore zero crash
   episodes; the episode-aware audit, episode-block bootstrap and conditional temporal-edge
   permutation are all vacuous on that data and are recorded as NOT RUN / NOT APPLICABLE in
   `research_state/episode_edge_hyperliquid_partial.{json,md}` rather than being reported as
   fabricated p-values. The exploratory spec-literal run produces only 2 trades on 2 crash
   days, which is likewise below any episode-aware inference floor. A longer
   Hyperliquid-native history is required before any episode-aware inference is possible on
   Hyperliquid.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_stress_okx.py
# EXPECT: verdict=underpowered; LOO=5, LOTO=8, evaluable_blocks=3
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx.py --draws 40
# EXPECT: episodes=4 events=11 days=5 largest_episode=4/11 perm_p=0.1500
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
# EXPECT (2026-11-14T21:23Z): 3877/6792 bars; 2915 missing; 235 perps / 37 pass $5M / 37 probed; earliest 2026-04-20T11:00:00Z
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
# EXPECT: 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
# EXPECT: 4/4 — EVIDENCE VERIFIED
```

## Exploratory reproduction (NOT_EVIDENCE; never overwrite canonical artifacts)

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_exploratory_next_open.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z
# EXPECT: 2 trades, total_pnl=-2670.7567875859345, symbols=24
# EXPECT funnel: 29 RSI<20 -> 11 volume-pass -> 0 same-bar confirm -> 8 spec-literal signals
```