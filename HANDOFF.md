# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T08:13:18Z
**Supersedes:** 2026-11-13T08:07:08Z (and the earlier 07:56:11Z / 07:42:00Z handoffs).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `c148d3d`, tree clean at session start. This session adds only `requirements-test.txt`, `scripts/bootstrap_env.sh`, and this file. Do **not** `git reset`/`checkout` anything away. Nothing needs to be committed before starting Phase G+.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION
>
> **Inferred from repo `CRASH-REBOUND-STRATEGY` (crash-rebound strategy research/backtest) and the state verified at 2026-11-13T08:13:18Z.**
>
> **Mission:** produce decision-grade, evidence-backed analysis of the crash-rebound strategy on the real OKX run already on disk. Setup is done. The environment bootstrap is now one command. **Do not stop after setup, after the test suite, or after a summary — the session is incomplete until the Phase J artifacts exist and this file is re-dated.**
>
> **Priority order (repo-aligned: crash-rebound strategy first, everything else second):**
>
> 1. **Phase G+ — Spec-vs-actual analysis artifact (PRIMARY, do not skip).** Write `research_state/real_okx_full_spec_comparison.md` **and** `research_state/real_okx_full_spec_comparison_summary.json`. The markdown must be a decision-grade report: a metric-by-metric table (spec vs actual) plus evidence-backed divergence explanations for EVERY row, with exact artifact values and code-path citations. A summary paragraph is not acceptable.
> 2. **Phase H — Reproducibility & hardening.** Re-run the suite to green, codify the reproducibility contract as an automated test, and confirm no gate bypass. (The persisted-rebound-fields regression test already exists; do not rewrite it.)
> 3. **Phase I — Update this HANDOFF** with exact commands, observed test counts, artifact paths + sha256, conclusions, and the next highest-value heavy work.
> 4. **Phase J — Next focus campaign (NEW, heavy).** Crash-event census across all 54 symbols + a parameter-sensitivity sweep + a real Hyperliquid-native acquisition runbook. This is the "future agents cannot avoid heavy work" phase: see §6 for mandatory outputs.
>
> **Mandatory heavy campaign (execute in order; do not stop after step 1):**
> 0. **Bootstrap:** `bash scripts/bootstrap_env.sh` (~1 min; runner image has no pytest/numpy/pandas/requests/pyarrow).
> 1. **Phase G+** (primary, evidence-first spec-vs-actual).
> 2. **Phase H** (reproducibility & hardening).
> 3. **Phase I** (update this handoff).
> 4. **Phase J** (census + sensitivity + acquisition runbook).
>
> **Do not redo:** the real OKX 1H archive acquisition, the 54-symbol universe derivation, or the full campaign run. All are on disk and verified below (§2). Start from the artifacts.
>
> **Do not claim Hyperliquid parity from OKX data.** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
>
> **Definition of done for Phase G+ (all must be true):**
> - Spec-vs-actual table includes: total return, annualized return, worst drawdown, positive-month count, trade count, buys/shorts and their win rates, rebound-short profit contribution, and symbol-universe size.
> - Divergence is quantified with artifact evidence: trade-frequency gap (8 vs 85), universe actually traded vs admitted (5 of 54), exit-reason mix, leg mix, active-period coverage, and exposure/gross-cap utilization.
> - The rebound-short finding is stated explicitly: the **short leg's true PnL is −1,636.86** (short coin +1,067.73, rebound hedge −2,704.59); the previously cited `+2,988.22` was the whole BCH trade (buy + short), not the short leg. Contrast with the spec's "~27% of profit" claim.
> - Every claim carries the provenance caveat: "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence."

---

## 0. What the 2026-11-13T08:07Z session verified — no code bottlenecks remain

| Check | Result this session | Evidence |
|---|---|---|
| Full suite (fresh venv, **pyarrow installed**) | **936 passed, 1 skipped in 376.89 s** | `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` |
| Skips explained | exactly 1: `tmp_path resolves to temp scratch marker in this environment` (`tests/test_fetch_archive_ingest_temp_path_rejection_20261109.py:80`). **No pyarrow skips** in this run (pyarrow was installed). | `-rs` output |
| Venv path canonicalization | `/tmp/venv_h` is the working venv on this runner. `scripts/bootstrap_env.sh` defaults to `/tmp/crs-venv`; both are valid — use whichever exists, or re-run bootstrap once. Not a blocker. | `ls /tmp/venv_h/bin/python` confirmed |
| Prior skip-count claims corrected | the prior handoff's "11 × pyarrow not installed + 1 × tmp_path" and "952 passed if pyarrow is installed" were **not reproducible**; the fresh pyarrow run is 936/1. Use 936/1 as the baseline. | this table |
| Artifacts intact | all four hashes below match the prior handoff exactly. | `sha256sum` |
| Phase G+ artifacts | **still absent** — `research_state/real_okx_full_spec_comparison{,_summary.json}` do not exist. This is the primary work. | `ls research_state/` |
| Environment bottleneck | **removed**: `requirements-test.txt` + `scripts/bootstrap_env.sh` now bootstrap pytest/numpy/pandas/requests/pyarrow in one command. | new files this session |

**Commands used this session:**
```bash
# /tmp/venv_h already has deps; bootstrap is one command if needed:
bash scripts/bootstrap_env.sh                      # -> /tmp/crs-venv (or existing /tmp/venv_h)
PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs
```

---

## 1. Previously resolved bottlenecks (do not re-litigate)

| Bottleneck (before) | Resolution | Evidence |
|---|---|---|
| Runner image has no test deps (`No module named pytest`) — biggest avoidable time sink. | Scripted: `requirements-test.txt` + `scripts/bootstrap_env.sh`. | new files, this session |
| `tests/test_track4f_leg_attribution_hardening.py` — 6 failures: `_split_leg_pnls` split EVERY `short`-legged trade into a phantom `buy` + zero `short`. | `_split_leg_pnls` splits ONLY when rebound constituents are present; buy = trade `pnl`; short = `rebound_short_pnl + rebound_hedge_pnl`. A `short` trade without rebound fields is attributed in full to its own leg. | `src/metrics/campaign_metrics.py:237` |
| Canonical gap report claimed `ready_for_real_campaign=true`. | Regenerated from canonical verified Hyperliquid provenance (synthetic ⇒ fail-closed). | `research_state/candle_coverage_gap_report.json` now `ready=false`, `blocked=true` |
| `trade_attribution_by_leg` disagreed with `leg_breakdown` for rebound trades. | Both now use the same constituent split and sum to the grand total. | `src/metrics/campaign_metrics.py:161` |
| Campaign artifact dropped `rebound_short_pnl`/`rebound_hedge_pnl`. | `scripts/run_portfolio.py` persists both fields on every serialized trade. | `scripts/run_portfolio.py:408` |

**Remaining (non-blocking) inefficiencies — noted, not fixed:**
- Full suite takes ~6.3 min here; the campaign re-run and any sensitivity sweep are heavier. Budget accordingly; cache expected hashes instead of re-running for pure equality checks.
- Canonical Hyperliquid provenance is synthetic, so the canonical gap report is fail-closed by design. Only OKX data is real; do not "fix" this by fabricating Hyperliquid data.

---

## 2. Verified current state (real, non-synthetic OKX full run)

**Data (real, non-synthetic, do not re-acquire):**
- OKX 1H archive: `research_state/archives/okx_1h_full_20251220_20260928/` — 64 entries (62 alt archives + `candles/` + `provenance.json`), `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`), sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
- Universe: `research_state/universe_okx_full_verified.json` — 54 selected symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb` (re-derivation previously confirmed identical except `generated_at_utc`).

**Campaign artifacts (hashes re-checked 2026-11-13T08:07Z):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, 54 loaded/complete, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c` (+ `.csv`).
- Note: `trades` lives at `results.trades`, not top level. Each trade's `pnl` is the coin leg; `total_pnl` includes the hedge. Top-level `timestamp` is volatile and must be excluded from reproducibility diffs.

**Headline metrics (actual):**
- Equity: start `100,000`, final `109,159.69`; gross/net PnL `9,159.69 / 8,141.29`; fees AUM `2.15` + profit-share `1,016.26` = `1,018.40`.
- Return: `+9.1597%` total, `+22.5995%` annualized (over `0.4301` yr realized-trade horizon — see caveat), worst DD `-2.0275%` (`-2,091.61` at `1769551200000`), Sharpe `0.6258`, Sortino `1.2618`, Calmar `4.3793`, win rate `0.5`, profit factor `5.2335`.
- Months: `4` positive / `3` negative / `0` flat across `7` buckets (`1768946 +3161.97`, `1769115 −121.63`, `1769551 −1969.97`, `1770112 +2988.22`, `1770062 +3499.37`, `1770069 +1673.73`, `1779271 −72.00`).
- Annual: `1768 +3.16%`, `1769 −2.03%`, `1770 +8.07%`, `1779 −0.07%`.
- Trades: `8` (wins/losses `4/4`); exit reasons `time_exit 6`, `liquidated 1`, `target_rebound_short 1`; traded symbols `SOL 3, BCH 2, ETH 1, LINK 1, AVAX 1` (5 of 54 admitted). `final_open_positions=0`, `final_gross_exposure=0`.
- Per-leg (authoritative): **buy** `8` trades (`4` wins) `+10,796.55`, share `117.87%`, PF `5.99`; **short** `1` trade (`0` wins) `−1,636.86`, share `−17.87%`, PF `0.0`. `trade_attribution_by_leg` matches and sums to `9,159.69`.

**Caveats the analyst must carry into Phase G+:**
- **Horizon:** the equity curve is exit-event based (9 points: initial + 8 exits). Last realized exit is `2026-05-20T10:00:00Z`; there are **no trades in the final ~4 months** (2026-05-20 → 2026-09-28). `equity_horizon_years=0.4301` (~151 days), so `22.60%` annualized is over the active window, NOT the full 283-day spec window.
- **Venue:** OKX 1H real data; the strategy spec/test basis is Hyperliquid. Cross-venue differences (funding, liquidity, listing set, microstructure) must be stated in any comparison.
- **Rebound-short economics:** short leg is net negative once the rebound ETH hedge is separated (short coin `+1,067.73`, rebound hedge `−2,704.59`). The `+2,988.22` in older notes is the whole BCH trade (buy + short), not the short leg.

---

## 3. Phase G+ (heavy, evidence-first) — write BOTH artifacts

Write `research_state/real_okx_full_spec_comparison.md` and `research_state/real_okx_full_spec_comparison_summary.json`. The markdown must be a decision-grade report, not a stub.

### 3.1 Required spec-vs-actual table (populate every cell; cite artifact values)

| Metric | Spec (Hyperliquid test) | Actual (OKX full run) | Delta / note |
|---|---|---|---|
| Total return | `+81.2%` | `+9.1597%` | Actual is ~11% of spec; do NOT claim equivalence. |
| Annualized return | `+115.2%/yr` | `+22.5995%/yr` (0.4301 yr horizon) | Different horizon; flag. |
| Worst drawdown | `−5.4%` | `−2.0275%` | Smaller DD, but on a much smaller realized book. |
| Positive months | `6 of 10` | `4 of 7` | Different month count/period. |
| Trades | `85` | `8` | 9.4% of spec count. |
| Buys (win rate) | `73 (71%)` | buy leg `8` constituent trades (`4` wins, 50%) | Mixed semantics: 7 buy-only trades + 1 rebound-buy constituent. |
| Shorts (win rate) | `12 (83%)` | short leg `1` (`0` wins, 0%) | One rebound short, net negative. |
| Rebound-short profit contribution | `~27%` | `−17.87%` of total (leg PnL `−1,636.86`) | Directly contradicts spec; explain. |
| Universe | spec-relevant ≥$5M set | `54` admitted / `5` traded | Quantify admitted-but-not-traded. |

### 3.2 Required divergence analysis (evidence-only)

1. **Trade-frequency gap (8 vs 85):** count RSI(21)<20 crash events across the 54-symbol universe over the window; count how many became trades; break down why (no signal, per-trade trailing-24h ≥$5M gate, bounce confirmation gate, gross-cap/equal-share admission, one-position-at-a-time occupancy). Cite code paths (`src/strategy/crash_rebound.py`, `scripts/run_portfolio.py`, `src/backtest/engine.py`) and artifact counts.
2. **Universe utilization:** list the 54 admitted symbols and mark the 5 traded vs 49 never-traded; for a representative sample, state the blocking reason (no qualifying crash, volume gate at decision bar, cap). Do not hand-wave.
3. **Time coverage:** quantify the active window (`2025-12-20T21:00Z` → `2026-05-20T10:00Z`) and the ~4-month no-trade tail. This is a first-class divergence driver.
4. **Exit/leg mix:** `time_exit 6`, `liquidated 1`, `target_rebound_short 1`; per-leg win rates and PnL shares (use `leg_breakdown`, not `trade_attribution_by_leg` alone).
5. **Exposure/gross-cap utilization:** derive from `results.trades[].max_live_coin_notional`, `equity_curve`, and config `gross_cap_pct=120`; state peak concurrent exposure and how often the cap/equal-share cut bound admissions.
6. **Rebound-short attribution:** document the corrected split (buy `+10,796.55` / short `−1,636.86`) and explicitly retract the earlier `short +2,988.22` interpretation. Explain the hedge drag.
7. **Provenance caveat:** include the exact sentence: "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence."

### 3.3 Phase H — reproducibility & hardening

- Confirm `PYTHONPATH=. python -m pytest -q -rs` is green; **expected baseline is `936 passed, 1 skipped`** (only skip is the documented `tmp_path` marker; pyarrow installed). Record the exact numbers you observe.
- Re-derive universe and re-run campaign from on-disk manifest/cache/universe; confirm `results.trades` and `results.total_pnl` are identical across runs, excluding top-level `timestamp`. **Manually confirmed in the prior session (§2 of the 07:56 handoff)**; the remaining work is to encode this as an automated test.
- The persisted-rebound-fields regression test is **done** (`tests/test_campaign_trade_persistence_rebound_fields_20261113.py`). The remaining Phase H item is the reproducibility-contract test: a re-run of the campaign over the committed manifest/cache/universe reproduces `results.trades` and `results.total_pnl` byte-for-byte modulo `timestamp`. Guard runtime: run the campaign once per session, or cache the expected hash.
- Re-confirm no gate bypass: `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M remain enforced; no synthetic/fabricated path.

### 3.4 Phase I — update this handoff

Record exact commands, test counts, artifact paths + sha256, the analysis conclusions, and the next highest-value heavy work (Phase J results; REAL Hyperliquid-native acquisition plan per `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` — never fabricate).

---

## 4. Phase J — next focus campaign (heavy, mandatory; this is why the next session exists)

Phase G+ explains the gap between spec and actual. Phase J is the forward-looking heavy work that prevents the next session from stopping at a report. All outputs go under `research_state/` with new names; never overwrite the canonical campaign artifacts.

### J1 — Crash-event census (mandatory)
For **every one of the 54 admitted symbols**, over `2025-12-20T00:00Z..2026-09-28T23:00Z`, emit one record per hourly bar where `RSI(21) < 20` on close:
- `symbol`, `bar_timestamp`, `rsi`, `close`, `next_bar_open`, `trailing_24h_volume_usd`, `volume_gate_pass` (≥$5M at decision bar), `admitted_under_gross_cap`, `trade_opened`, `blocking_reason` (one of: `no_signal` n/a, `volume_gate`, `bounce_not_confirmed`, `gross_cap`, `one_position_per_coin`, `other`).
- Reconcile counts: total events → volume-gated → bounce-confirmed → admitted → trades opened. The 8 realized trades must be a strict subset with a reason for every dropped event.
- Outputs: `research_state/crash_event_census_real_okx_full.json` (machine) + `research_state/crash_event_census_real_okx_full.md` (tables + top blocking reasons). Acceptance: every event has a `blocking_reason`; counts sum; the census is reproducible from the on-disk archive alone.
- This directly answers the trade-frequency gap (8 vs 85) with per-symbol evidence, not assertion.

### J2 — Parameter sensitivity sweep (mandatory)
One-factor-at-a-time sweep around the current spec, using the on-disk OKX manifest/cache/universe:
- RSI threshold: `15 / 20 / 25`
- Buy target: `6% / 9% / 12%`; buy max hold: `24h / 50h / 72h`
- Rebound-short target: `6% / 9% / 12%`; short max hold: `24h / 48h / 72h`
- ETH hedge cap: `1x / 2x / 3x`
- Position size: `0.5% / 1.25% / 2.0%` of 24h volume
- Minimum sensible grid: ≥ 15 runs (one-factor-at-a-time) plus the baseline. Record per-run: total return, annualized, worst DD, trade count, per-leg PnL, and runtime.
- Outputs: `research_state/sensitivity_sweep_real_okx_full.json` + `research_state/sensitivity_sweep_real_okx_full.md`. Use a new `--output-prefix` per run; delete only your own rerun files. Acceptance: table includes every run's parameters and metrics; conclusions state which knobs move the result and which do not; no fabricated numbers.

### J3 — Real Hyperliquid-native acquisition runbook (mandatory)
The OKX run is cross-venue and cannot establish Hyperliquid performance. Produce an executable runbook, not a promise:
- Update/extend `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` into a step-by-step acquisition + verification plan: source(s), exact archive format, the `fetch_hyperliquid_candles.py --source archive` invocation, provenance checks (`all_complete=true`, `ready_for_real_campaign=true`), and the gated `run_real_campaign.py` command.
- Acceptance: every step has a command, a pass/fail check, and the artifact it writes. If data is unavailable, the runbook says so explicitly and marks the campaign `NOT_RUN`; never fabricate or relabel OKX results as Hyperliquid.

### J4 — Phase J handoff update
Append the J1/J2/J3 results, artifact paths, sha256, and the next bottleneck to this file; re-date the header.

---

## 5. Canonical commands / artifacts

- Bootstrap: `bash scripts/bootstrap_env.sh` (venv at `/tmp/crs-venv`; deps from `requirements-test.txt`).
- Tests: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs` (add `-rs` to audit skips).
- Derive universe: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
- Real campaign: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full --apply-vault-fees`
  - `--output-prefix` must be a bare filename stem under `research_state/`; absolute paths and `..` are rejected by design (`scripts/run_real_campaign.py:286`).
- Canonical gap report: `PYTHONPATH=. python scripts/generate_candle_coverage_gap_report.py` (writes `research_state/candle_coverage_gap_report.json`; currently fail-closed by design because canonical Hyperliquid verified provenance is synthetic).
- Key artifacts: `research_state/universe_okx_full_verified.json`, `research_state/campaign_results_real_okx_full.json`, `research_state/campaign_results_real_okx_full_metrics.{json,csv}`, `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`, `research_state/archives/okx_1h_full_20251220_20260928/`.

## 6. Hard prohibitions

- Do **not** fabricate/synthesize/"fill" data. Do **not** relabel per-code/partial/BTC-only runs as full spec evidence.
- Do **not** remove `volume_filter_ok` (all-bars) or the per-trade point-in-time volume filter.
- Do **not** re-acquire data already on disk. Do **not** claim Hyperliquid performance parity from OKX data.
- Do **not** re-litigate closed Phase A. Do **not** treat the stale `fix/*-20261030` remote branches as blockers: they are old, unmerged, and not required for the current main line; review before any merge.
- Do **not** delete or "clean up" `research_state/` artifacts to make a rerun easier; write reruns to a new `--output-prefix` stem and delete only your own rerun files after diffing.
- Do **not** mark the session done with only Phase G+ written: the Phase J artifacts are part of the definition of done for the next focus campaign.

**This file is the durable handoff.** The next agent starts at step 0 (bootstrap), executes Phase G+ → H → I → J from the artifacts above, and must leave an updated, evidence-backed handoff plus the Phase G+ comparison artifacts and the Phase J census/sensitivity/runbook artifacts.