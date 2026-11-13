# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T20:11:33Z
**Supersedes:** all earlier handoffs (2026-11-13T19:40:37Z and before).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `876945c` (working tree may carry session edits). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T20:11:33Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** move the crash-rebound result from `underpowered` (n=8, bootstrap CI crosses zero, sign-flip p=0.09375) to a **statistically defensible signal-vs-noise verdict** — using the existing real OKX cache, not new prose, not re-runs of finished phases.
>
> **DO NOT TRUST THE OLD "10,000 full simulations" INSTRUCTION — IT IS COMPUTATIONALLY IMPOSSIBLE AND WAS A BOTTLENECK.** Measured this session (2026-11-13T20:11:33Z): the full 54-symbol simulation takes **~527 s (8.8 min)** and reproduces the canonical result **exactly** (8 trades, total PnL **+9159.691934882958**). 10,000 such draws ≈ **88 days of single-core CPU**. Any plan whose headline step is "10,000 full-portfolio placebo sims" will stall. The campaign below is **calibrated to the real cost** and is achievable.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> # 0. Prerequisites (run once if venv missing)
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
>
> # 1. Done-gate — must print "8/8 checks passed — DONE"
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
>
> # 2. Verify canonical baseline reproduces (writes nothing; ~9 min, single core)
> #    EXPECT: trades 8, total_pnl 9159.691934882958  (see §3 recipe)
>
> # 3. Confirm no concurrent sweeps/locks
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **VERIFIED BASELINE (2026-11-13T20:11:33Z):** gate **8/8**; `/tmp/crs-venv` present; 4 cores; no sweeps/locks running. Canonical artifact sha256 `57973b0c4a0d68c7…` (unchanged). **MISSING NEXT-CAMPAIGN ARTIFACTS (the blocking gap):** `research_state/placebo_okx_full.*`, `research_state/walkforward_okx_full.*`, `research_state/risk_budget_real_okx_full.*` — **NONE EXIST.**
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars/symbol, $5M vol gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% total / +22.5995% annualized over 0.4301y, worst DD −2.0275%, PnL +9159.69**. sha256 `57973b0c…2f9b8`. **Reproduced this session bit-for-bit.**
> - Phase L = **`underpowered`**: bootstrap 95% CI PnL **[−930.66, +19152.38]** (crosses 0), sign-flip one-sided **p=0.09375**, concentration high (5 traded symbols).
> - Phase K: `rsi25_maxpos8` ⇒ **+23.44% but −18.34% worst DD, 33 trades** (risk-budget trade, not free alpha).
> - Hyperliquid-native campaign **`NOT_RUN`**. `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER use as evidence.**
>
> **BOTTLENECKS CLEARED THIS SESSION (do not re-litigate):**
> 1. **Cost is now known and documented:** full sim = **527 s**; single-symbol sim ≈ **8 s**; cache load ≈ **2.3 s**. Plan against these numbers.
> 2. **The full 54-symbol engine is the only faithful unit** (sizing = 1.25% of each symbol's trailing-24h volume, so results depend on the full symbol set). A subset run is **not** comparable to the canonical 8 trades (SOL alone gives 3 trades). Never quote subset runs as the null of the canonical result.
> 3. **A real null pool exists on disk:** the J1 census ledger (`research_state/crash_event_census_real_okx_full.json`, `events[]`) has **342 crashes → 187 volume-pass → 28 bounce-confirmed / 64 regime-ok → 11 signal-gate → 8 traded**, with per-event `symbol, bar_timestamp_ms/utc, rsi, close, trailing_24h_volume_usd, desired_notional, volume_gate_pass, bounce_confirmed, regime_min_price_ok`. **This is the raw material for a cheap, honest placebo** (see §1) — no network, no fabrication.
> 4. **Parallelism:** 4 cores. Run at most **3 concurrent workers**; do not run pytest alongside sims.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
>
> ### 1. CHEAP HONEST PLACEBO / NULL DISTRIBUTION (PRIMARY — DO THIS FIRST; budget ≤ ~3 h)
> Build the null from **real funnel candidates**, not random walks:
> - For each of the **187 volume-pass** events (and separately the **39 bounce-confirmed** set), construct a **matched synthetic entry** that mirrors the real trade's sizing/stop/target/time-exit, run it through the **existing low-level exit engine** (`src/backtest/engine.py`, `apply_slippage_commission`) on the **cached bars** for that symbol/timestamp — **no portfolio re-simulation**, so each draw is cheap (~ms).
> - Draw **≥ 2,000 null trials** (bootstrap over the 187 candidates; record seed, e.g. `20261113`) and compute the **null distribution of total PnL and of the 8-trade-matched mean**, then report the real +9159.69 percentile / one-sided p.
> - **Gate-preserving proof (required):** report each candidate's `volume_gate_pass / bounce_confirmed / regime_min_price_ok` and state explicitly that the ≥$5M gate is **not** relaxed; also report the **8 real trades' percentile** within the matched null.
> - **Acceptance:** a real, reproducible null (no fabrication); N and seed recorded; real-vs-null percentile/p; the honest caveat that this is a **per-event exit-model null**, complementary to (not a replacement for) a full-portfolio placebo.
>
> ### 2. FULL-PORTFOLIO PLACEBO, RIGHT-SIZED (budget ≤ ~12 h)
> If §1 is inconclusive, run a **small** full-engine placebo: **B = 200–500** full-portfolio draws, each with the **crash bars masked** (roll each symbol's history by a fixed per-symbol offset so the real crash bar is not at the same index) so the *same gates and sizing* run over *non-crash* data. At 527 s/draw this is **~29–73 h single-core**; **shard across 3 workers (~10–24 h)**. Record actual wall time and shard map. **Do NOT attempt 10,000.**
>
> ### 3. SYMBOL-BLOCK BOOTSTRAP (cheap; do in the same script)
> Resample **whole symbols** (not trades) to capture symbol-level dependence; report block-bootstrap CI for total PnL alongside the trade-level CI; state whether the sign/conclusion survives. Pure recomputation on the 8 trades — **minutes**.
>
> ### 4. WALK-FORWARD / OUT-OF-SAMPLE (moderate)
> Expanding-window split (first-half train / second-half test, and rolling) on the 2025-12-20..2026-09-28 cache. Note: only **~3–4** trades fall in each half, so report it as **directional, underpowered OOS**, not proof. **Deliverable:** `research_state/walkforward_okx_full.{json,md}`.
>
> ### 5. RISK-BUDGET THE K "WINNER" (cheap; from existing sweep artifacts)
> For `rsi25_maxpos8` (+23.44% / −18.34% DD), emit a **return-vs-worst-DD frontier** and a drawdown/governed variant so +23% is never quoted without −18% DD. **Deliverable:** `research_state/risk_budget_real_okx_full.{json,md}`.
>
> ### 6. INTEGRATE & REPORT
> Refresh this handoff (timestamp, commands run, artifact paths + sha256, placebo/walk-forward/risk conclusions, actual wall times). Re-run `scripts/session_gate.py` (must remain **8/8**) and **add gate checks for any new artifact you claim complete** (`scripts/session_gate.py` is the machine-checkable gate — extend it).
>
> **ACCEPTANCE CRITERIA:** §1 null computed on real cache with preserved gates (no fabrication, N+seed recorded); symbol-block bootstrap reported; §2 either executed right-sized or explicitly deferred with the measured cost; walk-forward reported; risk/DD frontier reported; OKX-not-Hyperliquid caveat intact; handoff updated with hashes/commands; gate ≥ 8/8.
>
> **ANTI-AVOIDANCE RULES (VIOLATION = FAILURE):**
> - ❌ Do NOT stop after reading/planning/summary. **Produce artifacts.**
> - ❌ Do NOT attempt 10,000 full sims, and do NOT cite them as feasible.
> - ❌ Do NOT re-run J2/K/L or re-acquire OKX data (complete, byte-stable).
> - ❌ Do NOT present the strategy as validated. Phase L = `underpowered`.
> - ❌ Do NOT fabricate nulls/p-values; do NOT relax the $5M gate.
> - ❌ Do NOT claim Hyperliquid parity from OKX or use the flat placeholder.
> - ❌ Do NOT overwrite canonical artifacts; write new stems only.
> - ❌ Do NOT create a second handoff/status file.
> - ✅ MUST EXECUTE the cheap null (§1) + bootstrap (§3) + risk frontier (§5) and produce real artifacts this session.

---

## 0. Verified state (2026-11-13T20:11:33Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `876945c`, branch `main`; working tree may have session edits. | `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/crs-venv` present (pytest/numpy/pandas/requests/pyarrow); 4 cores. Recreate via `bash scripts/bootstrap_env.sh`. | `test -x`, `nproc` |
| Done-gate | **8/8 — DONE.** | `scripts/session_gate.py` |
| Canonical reproducibility | **Reproduced exactly this session**: 8 trades, total PnL `9159.691934882958`, wall **526.6 s**. | §3 recipe |
| Cost calibration | full sim 527 s; single-symbol 8 s; cache load 2.3 s. | measured |
| Phase J2/K/L | Complete (unchanged): J2 17 runs, K 9 runs, L `underpowered`. | artifacts |
| Next campaign (§READ FIRST 1–6) | **NOT STARTED** — placebo/walkforward/risk artifacts absent. | `ls research_state/` |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

**Data:** `research_state/archives/okx_1h_full_20251220_20260928/` (63 symbols), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`. Universe `research_state/universe_okx_full_verified.json` (54 symbols; 54 pass the ≥$5M gate).

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Headline:** 100,000 → 109,159.69; net PnL 8,141.29; **+9.1597% total / +22.5995% annualized** over 0.4301 yr; worst DD −2.0275%; 8 trades (4W/4L), 5/54 symbols. **Caveat:** real OKX cross-venue, NOT Hyperliquid performance evidence.

## 2. Completed phases — evidence (do not redo)

- **J1** `crash_event_census_real_okx_full.{json,md}` — funnel 342→187→39→89→11→8, 0 unexplained. sha256 `46ba710e…` / `cbcd74bd…`.
- **J2** `sensitivity_sweep_real_okx_full.{json,md}` — 17 runs. sha256 `62563cc0…` / `199d9030…`.
- **K** `interaction_sweep_real_okx_full.{json,md}` — 9 runs. sha256 `b122fe71…` / `f4ab2aea…`.
- **L** `robustness_real_okx_full.{json,md}` — **verdict `underpowered`**; bootstrap CI PnL **[−930.66, 19152.38]**; sign-flip p **0.09375** (2/256); 5 symbols. sha256 `cc3d0eaf…` / `58ff4719…`.
- **H** fast suite 966 passed, 1 skipped; canonical artifact byte-identical.
- **J3** Hyperliquid-native campaign **`NOT_RUN`** (data unavailable); runbook in `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`.

## 3. Reproduction recipe (measured, canonical)

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python - <<'PY'
import time, sys; from pathlib import Path; sys.path.insert(0, ".")
from scripts.run_real_campaign import load_verified_cache, load_universe, validate_symbol_volume_coverage
from src.data.provenance import load_provenance
from src.strategy.config import StrategyConfig
from scripts.run_portfolio import run_portfolio_simulation
cache = Path("research_state/cache/okx_1h_full_20251220_20260928")
man = load_provenance(str(cache/"provenance.json"))
uni = load_universe(Path("research_state/universe_okx_full_verified.json"), man)
syms = validate_symbol_volume_coverage(man, uni, 5_000_000.0)   # 54 symbols
cd = {s: d for s, d in load_verified_cache(cache, man).items() if s in syms}
cfg = StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                     enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0)
t = time.time(); r = run_portfolio_simulation(cd, cfg, 100000.0, {"ETH": cd["ETH"]}, require_eth_hedge=True)
print("wall %.1fs" % (time.time()-t), "trades", r["num_trades"], "pnl", r["total_pnl"])
PY
# EXPECT: wall ~527s  trades 8  pnl 9159.691934882958
```

## 4. Canonical commands

- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
- Fast suite: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs -k "not reproducibility_contract"`
- Full suite (Phase H): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Phase L verify (no writes): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py --check`

## 5. Next focus campaign — status

**NOT STARTED.** Sole bottleneck: **no placebo / symbol-block bootstrap / walk-forward / risk-budget artifacts exist**. Execute READ-FIRST items 1–6. Use existing on-disk cache/manifest/universe; preserve gates; emit reproducible artifacts (paths + sha256 + method/seed); keep the OKX-not-Hyperliquid caveat. Do not regress below 8/8.

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX as Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder: BTC 60000 / ETH 3000).
- No removal/relaxation of `volume_filter_ok` or the trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/G+/J2/K/L.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` is held.
- Do not present the strategy as validated: **Phase L = `underpowered`**; 8/8 proves evidence-chain completeness, not profitability.
- Do not create additional handoff/status files. This file is the single durable handoff.

## 7. Definition of done

Evidence chain **8/8 achieved**; **decision-grade validation NOT achieved** until §READ-FIRST campaign produces real placebo / block-bootstrap / walk-forward / risk-budget artifacts. **This file is the durable handoff.**