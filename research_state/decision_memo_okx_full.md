# Decision Memo — Crash-Rebound Strategy (Real OKX 283d canonical evidence)

**Generated (UTC):** 2026-11-13T20:54:14Z
**Status:** `underpowered` / **not decision-grade** — do not allocate capital on this evidence.
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.

## Decision question

Is the canonical crash-rebound portfolio result distinguishable from noise, and is it
investable under the spec's gates, sizing and risk limits?

**Answer: no, not with the current sample.** The canonical +9.16% return is a small-sample
outcome of a gate-passing event pool. The exact full-portfolio placebo places it at the
**45th percentile** of all gate-preserving 8-of-11 admission subsets. The result is not
distinguishable from a random admission/cap/occupancy draw.

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
| Risk budget (existing sweeps) | `rsi25_maxpos8` +23.44% / **−18.34% DD**, 33 trades; baseline +9.16% / −2.03% DD, 8 trades | Return is a risk-budget trade; never quote +23% without −18% DD. |

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
- The sample has **8 trades, 5 symbols, 283 days**. No bootstrap or placebo can create
  power that the sample does not contain.
- The +9.16% return must not be presented as validated edge, and the strategy must not be
  funded on this evidence.

## Stop / go criteria (explicit)

**GO only if all of the following hold on Hyperliquid-native data:**

1. The full 283-day Hyperliquid window is acquired with verified provenance and no
   placeholder/flat series (see `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. The canonical campaign produces **≥ 100 trades** across **≥ 10 symbols** (or a
   pre-registered equivalent power target).
3. The trade bootstrap 95% CI excludes 0 **after** multiple-testing correction, and the
   sign-flip p < 0.05.
4. The exact full-portfolio placebo p(placebo ≥ real) < 0.05 on the Hyperliquid run.
5. Worst drawdown is within the mandate (the baseline −2.03% DD is acceptable; the
   `rsi25_maxpos8` −18.34% DD is not, unless explicitly risk-budgeted).

**STOP / do not fund if:**

- Hyperliquid-native data cannot be acquired or is synthetic/flat/placeholder.
- The Hyperliquid result remains inside its full-portfolio placebo distribution.
- The result depends on the `rsi25_maxpos8` risk budget without disclosing the −18.34% DD.
- Anyone reports the per-event null as a portfolio test.

## Immediate next work (not done by this memo)

1. **Hyperliquid-native acquisition and campaign** — the only path to decision-grade
   evidence. Use the runbook; never use
   `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`
   (flat synthetic placeholder) as evidence.
2. **Robustness stress / power analysis** on the OKX cache using the now-cheap exact
   portfolio path: leave-one-symbol-out, leave-one-trade-out, concentration-adjusted
   inference, and the sample size required for the CI to exclude 0.
3. **Walk-forward with refit** if feasible; otherwise document the refit cost and keep the
   directional label.
4. **Do not regress:** keep the done-gate green; do not re-run the canonical campaign,
   J1/J2/K/L, or re-acquire OKX; do not fabricate data; do not relax the $5M gate; do not
   create a second handoff.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
```