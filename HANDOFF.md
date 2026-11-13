# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T20:55:06Z
**Supersedes:** 2026-11-13T20:32:51Z and all earlier handoffs.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `54931c9` (working tree carries this session's edits; not committed). **This file is the only durable handoff.** Never create a second status/handoff file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T20:55:06Z)
>
> **Inferred priority (repo `CRASH-REBOUND-STRATEGY`):** convert the canonical crash-rebound evidence into a decision-grade readout. The OKX evidence is now **`underpowered` / not decision-grade**: the exact full-portfolio placebo places the canonical +9.16% result at the **45th percentile** of all 165 gate-preserving admission subsets. **Do not declare validated. Do not allocate capital.** The only path to decision-grade evidence is **Hyperliquid-native data and campaign**; the OKX cache is cross-venue and cannot substitute.
>
> **WHAT CHANGED THIS SESSION (bottleneck removed):** the old 527s full-portfolio simulation recomputed `generate_signal` for every bar of every symbol. The new `scripts/run_portfolio_placebo_okx.py` memoizes `generate_signal` at all 342 census RSI-crash bars, reproduces the canonical campaign **to the cent in ~0.25s**, and enumerates **all 165** 8-of-11 gate-preserving portfolio subsets in **42s**. The 10,000-sim fear and the 600s shell-timeout trap are gone. Do not re-run the old slow path.
>
> **DO NOT TRUST the per-event null as a portfolio test.** Per-event sims size each trade at 1.25% of 24h volume with **no portfolio gross cap** (desired notionals up to **$7.29M**), while the canonical portfolio caps gross at **$120k** (120% of $100k). Its mean (~$232k) and `P(null >= 9159.69)=0.9865` are a sizing artifact. The exact full-portfolio placebo is the valid comparison.
>
> **START-OF-SESSION BOOTSTRAP + DONE-GATE (RUN FIRST, RECORD EXACT OUTPUT):**
> ```bash
> test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py   # must print "10/10 checks passed — DONE"
> PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
> # EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545
> ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|run_next_campaign|run_portfolio_placebo|pytest' | grep -v grep || true
> ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"
> ```
>
> **VERIFIED BASELINE (2026-11-13T20:55:06Z):** gate **10/10**; `/tmp/crs-venv` present; 4 cores; no sweeps/locks/processes; canonical hash unchanged; new Phase M artifacts present. Working tree has session edits (per-event/walkforward/risk refreshed; placebo + decision memo + new script untracked). **A green gate is evidence-chain completeness, NOT permission to stop.**
>
> **BOTTLENECK STATUS (2026-11-13T20:55:06Z): NONE.** No running processes, no `.sensitivity_sweep.lock`, no 527s path in the next campaign, no 600s-timeout trap. The heavy remaining work is **Hyperliquid-native acquisition + campaign** (primary) and, if that is data-blocked, the **OKX robustness stress / power analysis** (fallback) — both must produce artifacts, not plans.
>
> **DECISION-CRITICAL FACTS (DO NOT SOFTEN):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars, $5M vol gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% / +22.5995% ann. over 0.4301y, worst DD −2.0275%, total PnL 9159.69**. Cross-venue OKX, **NOT** Hyperliquid performance evidence.
> - **Exact full-portfolio placebo (this session, 165/165 subsets, real engine, gates/sizing/cap/occupancy preserved):** mean **8746.21**, median **9287.25**, p05 **5807.36**, p95 **11360.11**, min **3988.13**, max **11795.92**. Canonical 9159.69 is at the **45.45th percentile**; `P(placebo >= canonical)=0.5515`. **The canonical result is typical of a random 8-of-11 gate-passing admission subset — no admission/cap edge.**
> - All 165 placebo subsets are positive (min 3988.13), but this is conditional on the observed 11-event pool; it is **not** evidence of a temporal crash-rebound edge.
> - Phase L: trade bootstrap 95% CI PnL **[−930.66, +19152.38]** (crosses 0), sign-flip one-sided p **0.09375**. Symbol-block bootstrap (2,000) 95% CI **[−2026.39, 19249.18]**, P(>0)=**0.942** — dependence-aware but wide/underpowered (n=5 traded symbols).
> - Walk-forward (directional, no refit): chronological halves both positive (4 trades +1070.36 / 4 trades +8089.33) but trades cluster Jan–May with a long no-trade tail; not proof.
> - Risk budget (existing sweeps): `rsi25_maxpos8` **+23.44% / −18.34% DD, 33 trades** vs baseline **+9.16% / −2.03% DD, 8 trades** — risk-budget trade; **never quote +23% without −18% DD**.
> - Hyperliquid-native campaign **`NOT_RUN`**. `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** — **NEVER evidence**.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (EXECUTE IN ORDER — HEAVY, ACHIEVABLE, NO EARLY STOP):**
> 1. **Hyperliquid-native acquisition + canonical campaign (PRIMARY):** use `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` runbook. Acquire the full 283d Hyperliquid BTC/ETH (and alts if available), verify provenance and non-flat data, then run the canonical campaign. Adapt `scripts/run_portfolio_placebo_okx.py` to the Hyperliquid cache/config and produce `research_state/campaign_results_hyperliquid_283d*.json` plus `research_state/placebo_portfolio_hyperliquid_283d.{json,md}`. If acquisition fails, record the exact API/provenance failure and **do not substitute the placeholder**.
> 2. **Fallback heavy work (only if Hyperliquid is data-blocked):** create `scripts/run_robustness_stress_okx.py` using the memoized exact path (0.25s/sim) and produce `research_state/robustness_stress_okx_full.{json,md}`: leave-one-symbol-out, leave-one-trade-out, concentration-adjusted inference, power analysis (how many trades/symbols are needed for the bootstrap CI to exclude 0), and a refit/expanding-window walk-forward with warmup-preserving prefixes. Then extend `scripts/session_gate.py` with a `phase_n_robustness_stress` check and keep it green.
> 3. **Decision memo update:** update `research_state/decision_memo_okx_full.md` with the Hyperliquid result (or the documented data block). Keep the verdict `underpowered` until every GO criterion is met. Extend the gate check to require the updated memo.
> 4. **Do not regress:** keep 10/10 green; no re-runs of J2/K/L/canonical; no OKX re-acquire; no second handoff; no fabricated data; never relax the $5M gate; never present the per-event null as a portfolio test.
>
> **ANTI-AVOIDANCE:** the next turn must execute step 1 or step 2 and produce a real artifact. No planning-only turn; no validation claims (remains `underpowered` until Hyperliquid GO criteria are met); no Hyperliquid parity claims; no 10,000-sim theater (exact 165-subset enumeration is stronger); no per-event-null-as-portfolio-test; no second handoff/status file.

---

## 0. Verified state (2026-11-13T20:55:06Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `54931c9`, `main`; session edits in tree (not committed). | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md`. | repo root |
| Environment | `/tmp/crs-venv` present; 4 cores. | `test -x`, `nproc` |
| Done-gate | **10/10 — DONE.** | `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` |
| Canonical baseline | 8 trades, total PnL **9159.691934882958** (unchanged). sha256 `57973b0c…2f9b8`. | §1 |
| Cost calibration | canonical memoized replay **~0.25 s**; exact 165-subset placebo **42 s**; old full sim ~527 s. | measured this session |
| Phase J2/K/L | Complete, unchanged. | artifacts |
| Phase M (new) | Exact full-portfolio placebo + decision memo **produced**. | §5 |

## 1. Canonical artifacts (verified; do not re-acquire/re-run/overwrite)

- Data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (sha `53ad860b…`).
- Universe: `research_state/universe_okx_full_verified.json` (sha `14c8066e…`, 54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` (sha `57973b0c…`), metrics (sha `3f95d30e…`). **100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols.** OKX cross-venue, not Hyperliquid evidence.
- J1 census: `crash_event_census_real_okx_full.{json,md}` — 342→187→39→89→11→8, 0 unexplained.
- J2 `sensitivity_sweep_real_okx_full.*`, K `interaction_sweep_real_okx_full.*`, L `robustness_real_okx_full.*` (**`underpowered`**).

## 2. Commands executed this session (recorded)

- `test -x /tmp/crs-venv/bin/python && echo venv_ok` → `venv_ok`; `nproc` → 4.
- `ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|placebo|walkforward|pytest' | grep -v grep` → none; lock absent.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → **10/10 — DONE**.
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py` → **runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545** (42 s).
- `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_next_campaign_okx.py` → placebo 0.2 s, walkforward 0.0 s, risk budget done (heavy walk-forward re-sim removed).
- Verified canonical campaign hash unchanged; per-event/walkforward/risk stems refreshed (timestamp only).
- Created `scripts/run_portfolio_placebo_okx.py` (exact memoized full-portfolio placebo).
- Extended `scripts/session_gate.py` with `phase_m_portfolio_placebo` and `phase_m_decision_memo`.
- Wrote `research_state/decision_memo_okx_full.md`.

## 3. Reproduction recipe (canonical + exact placebo)

```bash
# Canonical (exact; ~0.25s with memo, ~527s without)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_okx.py
# EXPECT: runs=165 mean=8746.21 median=9287.25 p_ge_canon=0.5515 canon_pct=0.4545

# Canonical campaign equality check (optional, slow ~527s)
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

# Light post-L refresh (placebo per-event null, walk-forward chronology, risk frontier)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_next_campaign_okx.py
```

## 4. Completed phases (do not redo)

J1/J2/K/L/H/J3-status unchanged from prior handoff. J3 Hyperliquid-native **`NOT_RUN`** (data unavailable); placeholder parquet never evidence. Phase M (exact full-portfolio placebo + decision memo) **complete**.

## 5. New artifacts this session (hashes)

| Artifact | sha256 | Notes |
|---|---|---|
| `research_state/placebo_portfolio_okx_full.json` | `6b82dcb61fc6ccbec0ba8aa0c1069ab2c7c6be2dc8a704484c28520f2e981a97` | **Exact full-portfolio placebo**: 165/165 subsets, real engine, canonical replay exact. |
| `research_state/placebo_portfolio_okx_full.md` | `fef74f99922e919abfda78783fb37dace0d3773f0ee3bd941e7b470b311fb868` | Summary + interpretation. |
| `research_state/decision_memo_okx_full.md` | `213ae34b915c005aac23a31de9da93116e1eca8babd656e76aa2acaa928869d8` | Verdict `underpowered`; stop/go criteria; Hyperliquid prerequisite. |
| `research_state/placebo_okx_full.json` | `f6eb223aa8c89b0fe3f350b30edd4eb8072cda78934704665abb7eb92d202198` | Per-event null (complementary only; NOT a portfolio test). |
| `research_state/placebo_okx_full.md` | `76879daee7e3d58a2be15c5a4bca13af9ccc377d2ca5ff1b3daeee40be7a656a` | Per-event summary. |
| `research_state/walkforward_okx_full.json` | `2f1d9d8407ba8ea3755286c462d269020c8ffc74175e24e3903067d22d876554` | Directional chronological split; no heavy re-sim. |
| `research_state/walkforward_okx_full.md` | `160fb061a2f0c1eb9266446b2aa0f20dcabecf33754f310acb6c0c55e91ae576` | Directional summary. |
| `research_state/risk_budget_real_okx_full.json` | `1ce56d3dd74c5bcf8b13db1579e1f821e2dd4f4d9b4ea04fd78757899ca40364` | Return-vs-worst-DD frontier. |
| `research_state/risk_budget_real_okx_full.md` | `1011aa03d1dee1ed84f70e4e7baa7506bfb9f193e896d22a12c9d46381c75b88` | Frontier summary. |
| `scripts/run_portfolio_placebo_okx.py` | (new, untracked) | Memoized exact full-portfolio placebo; canonical equality hard gate. |
| `scripts/session_gate.py` | (modified) | 10 checks; Phase M placebo + decision memo fail-closed. |
| `scripts/run_next_campaign_okx.py` | (modified) | Heavy walk-forward re-sim removed (600s timeout trap). |

**Key results:** exact full-portfolio placebo (165 subsets) → canonical 9159.69 at **45.45th percentile**, `P(placebo >= canonical)=0.5515`, all subsets positive (mean 8746.21, median 9287.25, p05 5807.36, p95 11360.11). Canonical is **not distinguishable** from a random 8-of-11 gate-preserving admission subset. Per-event null is invalid (uncapped sizing). Phase L and symbol-block bootstrap remain underpowered. Verdict: **`underpowered` / not decision-grade.**

## 6. Next focus campaign — status

**Phase M COMPLETE:** exact full-portfolio placebo + decision memo + gate checks. **Still missing / blocking decision-grade verdict:** Hyperliquid-native data and campaign (primary), or documented data block + OKX robustness stress/power analysis (fallback). Verdict remains **`underpowered` / not validated**.

## 7. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX as Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/J2/K/L.
- No 10,000-sim theater; the exact 165-subset enumeration is the standard. Do not use the old 527s path for placebo work.
- No overwriting canonical artifacts; new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` held.
- Do not present strategy as validated: **`underpowered`**; 10/10 = evidence-chain completeness, not profitability.
- Do not present the per-event null as a portfolio test.
- No additional handoff/status files. This file is the single durable handoff.

## 8. Definition of done

Evidence chain **10/10 achieved**. **Decision-grade validation NOT achieved.** Required for done: Hyperliquid-native campaign (or documented data block) + robustness stress/power analysis (or documented cost block) + updated decision memo with stop/go criteria and Hyperliquid-data prerequisite. **This file is the durable handoff.**