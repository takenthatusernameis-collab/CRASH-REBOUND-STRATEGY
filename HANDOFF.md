# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T20:18:35Z
**Supersedes:** 2026-11-13T20:11:33Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `e9583ee` (working tree carries session edits). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T20:18:35Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** resolve whether the canonical OKX crash-rebound edge is distinguishable from noise with **decision-grade, gate-preserving evidence** and convert that into an investable decision framework (or a justified stop). Prior post-Phase-L campaign artifacts now exist (cheap placebo/bootstrap/risk/walkforward) but the signal remains **`underpowered` / not decision-grade** — do not declare validated.
>
> **DO NOT TRUST "10,000 full simulations" — COMPUTATIONALLY IMPOSSIBLE here.** Measured: full 54-symbol canonical sim **~527 s** (8.8 min, exact repro: 8 trades, PnL **9159.691934882958**). 10,000 draws ≈ ~88 days single-core. Plan against measured cost (4 cores; ≤3 concurrent workers; no pytest alongside sims).
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py   # must print "8/8 checks passed — DONE"
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|run_next_campaign_okx|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **VERIFIED BASELINE (2026-11-13T20:18:35Z):** gate **8/8**; `/tmp/crs-venv` present; no sweeps/locks. Canonical artifact sha256 `57973b0c…2f9b8` unchanged. New artifacts present: `placebo_okx_full.*`, `walkforward_okx_full.*`, `risk_budget_real_okx_full.*` (hashes in §5).
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M vol gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.69**. Cross-venue OKX, **NOT** Hyperliquid performance evidence.
> - Phase L: **`underpowered`** — trade bootstrap 95% CI PnL **[−930.66, +19152.38]** (crosses 0), sign-flip one-sided p **0.09375**.
> - **New per-event exit-model null (this session, seed 20261113, 2000 draws, k=8, gates preserved, $5M not relaxed):** volume-pass pool (187 events, 11 sim-ok) null mean **151,441** / p05 **−18,456** / p95 **326,770**, `P(null >= 9159.69)=0.9865`; bounce-confirmed (39, 11 sim-ok) similar; real 9159.69 is **below** the matched per-event null mean (percentile ~1.4%). **This is a per-event independent exit simulation (no portfolio cap/occupancy/admission interactions) — complementary, not a replacement for full-portfolio placebo.** Interpretation: against this simple gate-passing event pool the observed 8-trade portfolio outcome is not evidence of positive edge; portfolio selection/admission effects are unisolated.
> - **Symbol-block bootstrap (whole symbols, 2000, seed 20261113):** 95% CI **[−2026.39, 19249.18]**, P(>0)=**0.942** — dependence-aware but still wide/underpowered (n=5 traded symbols).
> - **Walk-forward/OOS (directional, underpowered):** chronological halves both positive (4 trades, +1070.36 / 4 trades, +8089.33) but trades cluster Jan–May with long no-trade tail; not proof.
> - **Risk budget (from existing sweeps):** `rsi25_maxpos8` **+23.44% / −18.34% DD, 33 trades** vs baseline **+9.16% / −2.03% DD, 8 trades** — risk-budget trade, **never quote +23% without −18% DD**. Frontier tags: `baseline_spec, rsi18_maxpos3, rsi18_maxpos8, rsi25_maxpos8, rsi15_maxpos3, rsi15_maxpos8`.
> - Hyperliquid-native campaign **`NOT_RUN`**. `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
> 1. **Interpret & harden the placebo (PRIMARY):** The per-event null shows canonical 9159.69 < mean of matched volume-pass/bounce-confirmed event exits, yet the full portfolio admitted only 8 specific trades. Reconcile this: (a) characterize *why* the 8 admitted trades underperform the per-event pool mean (admission timing, cap/occupancy, hedge/funding/liquidation, concurrency) using on-disk artifacts; (b) run a **right-sized full-portfolio placebo B=60–120** (sharded ≤3 workers, ~9–18 h) with crash-bar masking/offsets preserving gates/sizing — record wall time, shard map, seed/offsets; **do NOT attempt 10,000**. Deliver `research_state/placebo_portfolio_okx_full.{json,md}`.
> 2. **Robustness stress:** leave-one-symbol / leave-one-trade already in L; add concentration-adjusted inference and report how many symbols must contribute positively for CI to exclude 0 (power analysis on existing 283d cache).
> 3. **Walk-forward with refit/re-sim:** if feasible, expanding-window portfolio re-sims (≥2 windows) with warmup-preserving prefixes; else formally document cost-block and keep directional labels.
> 4. **Decision memo artifact:** produce `research_state/decision_memo_okx_full.md` synthesizing placebo (per-event + portfolio), block bootstrap, walk-forward, risk frontier into a clear **signal / noise / underpowered** investment readout with explicit stop/go criteria and Hyperliquid-data prerequisite. Extend `scripts/session_gate.py` to require it once written.
> 5. **Do not regress:** keep 8/8 gate green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax $5M gate.
>
> **ANTI-AVOIDANCE:** no planning-only turn; no 10k sims; no validation claims (remains underpowered until portfolio-placebo + decision memo resolve); no Hyperliquid parity claims.

---

## 0. Verified state (2026-11-13T20:18:35Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `e9583ee`, `main`; session edits in tree. | `git log -1`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present; 4 cores. | `test -x`, `nproc` |
| Done-gate | **8/8 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`. | §1 |
| Cost calibration | full sim ~527 s; per-event sims cheap (~0.17 s for 187). | measured/prior |
| Phase J2/K/L | Complete, unchanged. | artifacts |
| Post-L campaign (§1,3,4,5 of 20:11 plan) | **ARTIFACTS PRODUCED** (see §5). Full-portfolio placebo (B≥200 right-sized) **not run** (cost). | `research_state/placebo_okx_full.*` etc. |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (sha `53ad860b…`).
- Universe: `research_state/universe_okx_full_verified.json` (sha `14c8066e…`, 54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` (sha `57973b0c…`), metrics (sha `3f95d30e…`). **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- J1 census: `crash_event_census_real_okx_full.{json,md}` — 342→187→39→89→11→8, 0 unexplained.
- J2 `sensitivity_sweep_real_okx_full.*`, K `interaction_sweep_real_okx_full.*`, L `robustness_real_okx_full.*` (**`underpowered`**).

## 2. Commands executed this session (recorded)

- `test -x /tmp/crs-venv/bin/python && echo venv_ok` → `venv_ok`
- `ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|placebo|walkforward' | grep -v grep || echo "no relevant processes"` → none; lock absent.
- Verified next-campaign artifacts absent before run.
- Inspected census/campaign/engine/strategy/portfolio/sweeps to understand per-event vs portfolio semantics.
- Created `scripts/run_next_campaign_okx.py` (per-event placebo/bootstrap) and executed: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_next_campaign_okx.py` (initial run timed out at 600s shell limit after producing placebo artifacts; script then observed not running). Placebo artifacts present.
- Generated risk-budget + walkforward (trade-chronology, no re-sim) via inline `PYTHONPATH=. /tmp/crs-venv/bin/python - <<'PYTHON' ...` (completed; DeprecationWarning only).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **8/8 checks passed — DONE**.

## 3. Reproduction recipe (canonical, measured)

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
syms = validate_symbol_volume_coverage(man, uni, 5_000_000.0)
cd = {s: d for s, d in load_verified_cache(cache, man).items() if s in syms}
cfg = StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                     enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0)
t = time.time(); r = run_portfolio_simulation(cd, cfg, 100000.0, {"ETH": cd["ETH"]}, require_eth_hedge=True)
print("wall %.1fs" % (time.time()-t), "trades", r["num_trades"], "pnl", r["total_pnl"])
PY
# EXPECT: wall ~527s  trades 8  pnl 9159.691934882958
```
Post-L artifacts: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_next_campaign_okx.py` (produces/refreshes placebo/walkforward/risk-budget stems as implemented; walkforward re-sim path costly — this session emitted trade-chronology walkforward).

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged from prior handoff. J3 Hyperliquid-native **`NOT_RUN`** (data unavailable); placeholder parquet never evidence.

## 5. New artifacts this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/placebo_okx_full.json` | `0148a0214c9ca6744c809488017a5c39a8caf02513cb1b5bc1e3279f72824bc8` | Per-event exit-model null (vol-pass & bounce pools), seed 20261113, 2000 draws, k=8; gate-preserving proof included. |
| `research_state/placebo_okx_full.md` | `7c93ad423095dbe36c634638f7cb306c4573a4bfe9d62e2687c9807ae90c8c4b` | Summary. |
| `research_state/walkforward_okx_full.json` | `553d1b8d501c2daac2784aaf724f742b5fae8a01cbbedf02468563369451fcc1` | Directional chronological/rolling/monthly split of realized trades (no bar-split portfolio re-sim). |
| `research_state/walkforward_okx_full.md` | `8278d8d8a25f54fc3fa2443f191a6a57b1ff3bd821cb42940067e2ead71a4e3c` | Summary. |
| `research_state/risk_budget_real_okx_full.json` | `24d42be7fe5b741e80c026e7e700ee475fcea9e649cce3287057cf4772f65062` | Return-vs-worst-DD frontier from J2/K artifacts. |
| `research_state/risk_budget_real_okx_full.md` | `2a450e3ba66cd9a2e0d953d0a2d982f6c8752bf141b409a8c867eba9b7ed97cd` | Summary. |
| `scripts/run_next_campaign_okx.py` | (new, untracked/staged as session edit) | Generates placebo/walkforward/risk-budget artifacts from on-disk cache/census/campaign. |

**Key results:** per-event null (vol-pass sim-ok 11, bounce sim-ok 11) → `P(null >= 9159.69)` **0.9865 / 0.985**, real below null mean (null means ~151k, p05 ~−18k, p95 ~327k) — per-event complementary null, not portfolio placebo. Symbol-block bootstrap 95% CI **[−2026.39, 19249.18]**, P(>0) **0.942**. Walk-forward halves positive but clustered/underpowered. `rsi25_maxpos8` **+23.44% / −18.34% DD (33 trades)** is risk-budget, not free alpha.

## 6. Next focus campaign — status

**PARTIALLY COMPLETE (post-L):** cheap per-event null, symbol-block bootstrap, walk-forward (directional trade-chronology), and risk-budget frontier **done**. **Still missing / blocking decision-grade verdict:** right-sized **full-portfolio placebo** (B~60–120, sharded) to isolate cap/occupancy/admission effects; portfolio-resim walk-forward if feasible; reconciled interpretation (why 8 admitted trades < per-event pool mean) and a synthesized **decision memo**. Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX as Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000 full sims; no claims of feasibility.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **underpowered**; 8/8 = evidence-chain completeness, not profitability.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **8/8 achieved**. **Decision-grade validation NOT achieved.** Required for done: portfolio-placebo + reconciled inference + walk-forward rigor (or cost-justified deferral) + decision memo with stop/go criteria and Hyperliquid-data prerequisite. **This file is the durable handoff.**
