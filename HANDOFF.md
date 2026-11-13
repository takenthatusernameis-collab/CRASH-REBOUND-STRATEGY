# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T17:43:00Z
**Supersedes:** 2026-11-13T17:33:00Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `2ce4ca5` (`chore(kilo): checkpoint agent session`). Working tree has the uncommitted session changes listed in §0. **Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T17:43:00Z)
>
> **Inferred priority (from repo name `CRASH-REBOUND-STRATEGY`):** finish the decision-grade crash-rebound validation on real exchange evidence. The gate is **5/8**; the three missing gate items are **Phase J2** (running), **Phase K** (two-factor interaction campaign), and **Phase L** (robustness / signal-vs-noise). **This is heavy compute, not a summary task; do not skip or shortcut it.**
>
> **Start-of-session bootstrap + done-gate (run first, record exact output):**
> 1. If `/tmp/crs-venv/bin/python` is missing, run `bash scripts/bootstrap_env.sh`.
> 2. Then run: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
>
> **Verified state at this handoff (2026-11-13T17:43:00Z, re-checked live):** gate is **5/8** — Phase G+, J1, J3, and durable-handoff pass; **Phase J2, K, and L artifacts are not yet on disk**. The Phase J2 sweep is **running now** as a resumable background job: **14/17** per-run files complete at 17:43:00Z (baseline + 13 variants), 3 remain — `eth_hedge_cap_2x`, `max_positions_3`, `max_positions_8` — PID **8069** (4 workers, elapsed ~44m), background id `bgp_1d5da08f60017FUEbJplvtGwXS`. The runner is **CPU-bound at capacity on this 4-core box** (all 4 workers ~92% CPU). **Do not start a second sweep or a concurrent pytest/campaign while it runs** — the runner takes an exclusive lock (rc=3) and CPU contention skews both. If PID 8069 is gone, run the resume command in §5; it reuses completed runs and executes only the missing ones. Verify with `ls research_state/sweep_runs/*.json | wc -l` before acting.
>
> **Unblock-first ordering — clear the Phase L bottleneck while J2 computes (CPU-safe, no lock contention):**
> - **Phase L is the only item with a missing script:** `scripts/run_robustness_campaign.py` does **not exist** (confirmed 17:43:00Z). The gate contract is fully specified in §7, and the trade-level data it needs is present in `campaign_results_real_okx_full.json` → `results.trades` (8 trades with `symbol`, `exit_timestamp`, `total_pnl`). **Writing this script and its focused test is pure-Python, needs no sweep lock and negligible CPU, and can be done NOW while J2 runs.** Do it first so the moment J2/K finish, Phase L is one command away.
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **(Do now, CPU-safe) Implement Phase L:** write `scripts/run_robustness_campaign.py` per §7 (read-only vs canonical artifacts; fail closed on missing/invalid trades; write ONLY `research_state/robustness_real_okx_full.{json,md}`; deterministic seed=20261113) plus a focused test under `tests/`. Verify it against the **current 8 trades** now (the canonical result is final and will not change). Do not run the full pytest suite concurrently with J2 — run the single new test file only.
> 2. **Finish Phase J2:** confirm PID 8069 alive or resume per §5; wait for **17/17** per-run files; verify `research_state/sensitivity_sweep_real_okx_full.{json,md}` has 17 executed runs, baseline first, per-run evidence, ranked conclusions, spec-locked rejections, provenance caveat. Record wall-clock/speedup and which knobs move results.
> 3. **Phase K — interaction campaign (next heavy bottleneck):** after J2 releases the lock, run the two-factor grid in §5 (reuses J2 baseline → **8** new ~16-min runs, 9 total). Produce `research_state/interaction_sweep_real_okx_full.{json,md}` with per-run files. Required for **8/8**.
> 4. **Phase H — reproducibility/quality evidence (REQUIRED):** run the full suite `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs` (includes the ~16-min reproducibility-contract rerun) and record exact counts. The fast suite excluding that test last passed this campaign at **946 passed, 1 skipped, 1 deselected in 668.24s**; confirm `campaign_results_real_okx_full` reproduces (`results.trades`, `results.total_pnl`, `num_trades`) to a distinct prefix with the canonical artifact byte-identical afterward, then delete the temp outputs. Confirm `volume_filter_ok` and per-trade trailing-24h ≥$5M gates remain intact. **Run only after K releases the lock/CPU.**
> 5. **Execute Phase L for real:** run `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py`; verify `robustness_real_okx_full.{json,md}` satisfies the §7 gate contract (bootstrap resamples≥1000 + CIs + P(pnl>0); sign_flip 256 combos + p_value; concentration symbols/top shares; time_split halves; verdict ∈ {signal,noise,underpowered}) and the OKX/Hyperliquid caveat. **Do not stop before 8/8.**
> 6. **Phase J3 — Hyperliquid-native acquisition runbook (maintain):** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` already contains `HYPERLIQUID NATIVE ACQUISITION RUNBOOK` with `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, and `NOT_RUN` tokens. Keep it accurate/executable. The full-window Hyperliquid campaign remains **`NOT_RUN`**: the only Hyperliquid artifact on disk is a flat placeholder (see §0), not evidence. Never fabricate data and never relabel OKX artifacts as Hyperliquid evidence.
> 7. **Phase I/J4 — final evidence refresh:** re-run `scripts/session_gate.py`; record exact commands, observed test counts, new artifact paths + sha256, conclusions from G+/J1/J2/K/L/J3, and the next highest-value bottleneck. Re-date this header. Only mark done at **8/8**.
>
> **Anti-avoidance rules:** do not stop after reading, planning, or a narrative summary. Do not start a duplicate J2/K sweep while the lock is held. Do not use `--no-resume` to redo completed runs. Do not run the full pytest suite concurrently with a sweep. Do not re-acquire OKX data, re-run the canonical campaign, redo J1, or redo G+ without cause. Do not claim Hyperliquid parity from OKX data. Do not use the flat `_verified.parquet` placeholder as evidence. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. A missing J2/K aggregate or the missing Phase L script is a bottleneck to clear by executing/resuming/implementing, not a reason to defer. Do not call the strategy validated on 8 trades without Phase L.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T17:43:00Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `2ce4ca5`, branch `main`. Uncommitted: `HANDOFF.md`, `scripts/session_gate.py` (Phase L gate check), `tests/test_session_gate_robustness_20261113.py`, plus the newest `research_state/sweep_runs/*.json` evidence; the sweep/resume/null-safe fixes are committed at `2ce4ca5`. | `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/crs-venv` present with pytest/numpy/pandas/requests/pyarrow. Recreate via `bash scripts/bootstrap_env.sh` if absent. | `test -x`, imports |
| Done-gate | **5/8** — J2, K, and L missing. | `scripts/session_gate.py` |
| Phase J2 sweep | **Running**: 14/17 per-run files at 17:43:00Z; PID 8069 alive (4 workers, elapsed ~44m, all ~92% CPU); background id `bgp_1d5da08f60017FUEbJplvtGwXS`. Resume/lock/null-safe fixes committed at `2ce4ca5`. | `ls research_state/sweep_runs`, `ps -p 8069` |
| Phase L script | **MISSING** — `scripts/run_robustness_campaign.py` does not exist (confirmed 17:43:00Z). This is the sole remaining *code* bottleneck; it is CPU-safe to write now. Trade data present in `campaign_results_real_okx_full.json` → `results.trades` (8 trades). | `ls scripts/run_robustness_campaign.py` → absent |
| Phase H | Fast suite **946 passed, 1 skipped, 1 deselected in 668.24s** (reproducibility test excluded, recorded earlier this campaign). Full suite + repro test not yet run. | background pytest log |
| Phase G+ | **Done (artifacts present).** | `research_state/real_okx_full_spec_comparison.{md,summary.json}` |
| Phase J1 | **Done (artifacts present).** | `research_state/crash_event_census_real_okx_full.{json,md}` |
| Phase J3 | **Runbook present & gate-shaped**; Hyperliquid-native campaign **NOT_RUN** (data unavailable). | `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` |
| Phase K | **Not started** — gate check added; interaction grid implemented and executable. | `scripts/run_sensitivity_sweep.py --grid interaction` |
| Phase L | **Not started** — robustness campaign defined in §7; **script missing, no artifact yet**. | §7 |

### Session recovery / bottleneck playbook (use instead of guessing)

- **Sweep alive (lock held by live PID):** do not kill it, do not start a second sweep, do not run the full pytest suite; write the Phase L script + its single test file now (CPU-safe), then poll `ls research_state/sweep_runs | wc -l`. A second invocation correctly exits rc=3.
- **Sweep dead / PID gone:** run the Phase J2 command in §5. Resume reuses every matching per-run file and executes only the missing runs; the stale lock is replaced automatically.
- **17/17 files present but aggregate missing:** re-run the same J2 command; it rebuilds the aggregate from per-run files without re-executing runs.
- **Phase K blocked by J2 lock:** wait for J2 to release it; do not use `--no-resume` and do not isolate with `--runs-dir` to bypass the lock (it would duplicate compute and baseline).
- **`/tmp/crs-venv` missing:** run `bash scripts/bootstrap_env.sh` (requires network); then re-run the gate.
- **Null equity metrics:** the aggregate renderer and conclusions are null-safe (`n/a`, PnL/trade-count ranking); do not "fix" by dropping variants.

### Bottlenecks cleared this campaign (do not re-litigate)

1. **The Phase J2 sweep was killed with its previous session at 5/17 runs.** The runner had no resume, so every interruption discarded ~70 minutes of completed work. It now reuses any per-run file whose tag and knob values match (`_reusable_record`), takes an exclusive lock (`.sensitivity_sweep.lock`, stale-PID recovery), and refuses partial aggregates. Verified: resume reported `5/17 runs reused`, then continued; a second invocation correctly returned `BLOCKER: sweep already running (pid 8069)` (rc=3).
2. **A null equity-curve return crashed the final aggregate.** Several variants (`rsi_threshold_15/18`, `buy_target_12pct`, …) have `total_return_pct=null` because no explicit curve horizon is derivable; the old renderer/conclusions did arithmetic/formatting on `None` and would have crashed after all 17 runs completed. Both are now null-safe (`n/a` + PnL/trade-count ranking), with regression tests.
3. **The "verified" Hyperliquid parquet is a flat placeholder.** `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` has BTC close `60000.0` and ETH close `3000.0` for all 6,792 bars (1 distinct value each). Its cache provenance flags `synthetic_series_detected: [BTC, ETH]`. Despite the filename, it is **not** Hyperliquid market evidence; do not use it. This is why the Hyperliquid campaign remains `NOT_RUN`.
4. **Compute is CPU-bound at 4 workers on a 4-core runner.** Adding workers oversubscribes; the remaining J2 batch is ~2 × 16-minute waves. The only safe speedups are resume (never redo completed runs) and running Phase K immediately after J2 releases the lock; do not run the pytest suite concurrently with a sweep (it contends for the same cores and skews both).

## 1. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run/overwrite)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`; re-hash before citing.
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Phase G+:** `real_okx_full_spec_comparison.md` sha256 `fb0da9dddeac53177d1a5f946f0eb38f37a2a38fdf3072802da360cb10dd951b`; `real_okx_full_spec_comparison_summary.json` sha256 `58752ccf35214e53291bae2d9ff7d6cb2130cb220f21016d21794012dffef452`.

**Headline metrics (actual, from artifacts):** equity 100,000→109,159.69; net PnL 8,141.29; return **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`); worst DD −2.0275%; 8 trades (4W/4L), 5 traded symbols of 54. **Caveats:** active ~151-day horizon; real OKX cross-venue, **NOT Hyperliquid performance evidence**.

## 2. Phase J1 — Crash-event census (COMPLETE, do not redo)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae0b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`
- Reconciliation (0 unexplained): **342** → vol pass **187** → bounce **39** → regime **89** → signal **11** → trades **8**.

## 3. Remaining work — definition of done (all required for 8/8; Phase L is a gate check)

- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md` with **17 executed runs** (baseline + 16 one-factor-at-a-time variants), per-run params/metrics/runtime, per-run files under `research_state/sweep_runs/`, canonical untouched, evidence-backed conclusions on which knobs move results and which do not.
- **Phase K:** `interaction_sweep_real_okx_full.json` + `.md` with **9 executed runs** (baseline + 8 two-factor combinations), per-run files under `research_state/sweep_runs/`, evidence-backed interaction conclusions.
- **Phase H:** full suite green with recorded counts; reproducibility-contract test passes against canonical `campaign_results_real_okx_full` (distinct-prefix rerun, temp outputs deleted); gate integrity (`volume_filter_ok` all-bars + per-trade trailing-24h ≥$5M) confirmed.
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook maintained (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, required tokens present); `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/K/L/J3 outcomes, next highest-value bottleneck. `scripts/session_gate.py` **8/8**.
- **Phase L (gate check, required):** `robustness_real_okx_full.{json,md}` with bootstrap CI, sign-flip p-value, concentration, time-split, and an explicit signal/noise/underpowered verdict. **8/8 proves the evidence chain and signal-vs-noise characterization, not future profitability.**

## 4. Canonical commands

- Bootstrap (only if `/tmp/crs-venv` missing): `bash scripts/bootstrap_env.sh`
- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
- Fast suite (excludes the ~16-min repro test): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs -k "not reproducibility_contract"`
- Full suite (Phase H, includes repro): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Repro test alone: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs tests/test_reproducibility_contract_real_okx_full_20261113.py`
- Phase J2 sweep (parallel, resumable): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Phase K interaction sweep (after J2 releases the lock): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --grid interaction --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix interaction_sweep_real_okx_full`
- Phase L robustness (after implementing `scripts/run_robustness_campaign.py`): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py` (writes only `research_state/robustness_real_okx_full.{json,md}`; must satisfy the §7 gate contract)
- Phase H repro (distinct prefix, delete after): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/generate_candle_coverage_gap_report.py`

## 5. Next focus campaign (Phase K) — executable, heavy, gated

The one-factor J2 grid cannot see interactions. Phase K is a 3×3-style two-factor grid around the knobs J2 flags as material (RSI crash trigger × concurrent-position cap, and RSI trigger × buy target). It reuses the same locked, resumable runner and the same committed inputs; the baseline per-run file from J2 is reused, so only **8** new ~16-min runs execute. Aggregate: `research_state/interaction_sweep_real_okx_full.{json,md}`; per-run files under `research_state/sweep_runs/`. `scripts/session_gate.py` now requires this artifact (`phase_k_interaction_sweep`, 9 runs). Until it exists the gate is **not** 8/8.

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- **Do not use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence**: it is a flat placeholder (BTC 60000 / ETH 3000, one distinct close each), flagged synthetic by its cache provenance. The full-window Hyperliquid campaign is `NOT_RUN`.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No duplicate sweep while `research_state/.sensitivity_sweep.lock` is held; no `--no-resume` unless a fresh full run is explicitly intended.
- No "done" without J2 + K artifacts complete/analyzed, Phase H reproducibility-contract test passing + full suite recorded, Phase J3 runbook maintained, a refreshed evidence-backed handoff at **8/8** on `scripts/session_gate.py` (the gate now includes Phase L).

## 7. Next focus campaign after K — Phase L (robustness: signal vs noise)

**Why this is mandatory:** the canonical result is **8 trades, 5 traded symbols, 4W/4L, +9.1597%**, with a **131.54-day no-trade tail** and only **1 rebound short**. The G+/J1/J2/K gates prove the evidence chain; the 8/8 gate only passes when Phase L exists, but it still does **not** establish that the return is distinguishable from luck or that it will persist. Do not present the strategy as validated, and do not stop before 8/8.

**Deliverable:** `research_state/robustness_real_okx_full.json` + `.md` (new stems; never overwrite canonical campaign artifacts), carrying the exact provenance caveat: *"Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence."*

**Required analyses (all must be present with numeric evidence, not adjectives):**
1. **Trade-level bootstrap:** deterministic seeded resample (default 10,000) of the 8 realized trades' `total_pnl`; report 95% CI for total PnL, total return on 100k, win rate, profit factor, and `P(total PnL > 0)`. State the small-sample limitation explicitly.
2. **Exact sign-flip permutation test:** all 2^8 sign combinations of the 8 trade PnLs; report the fraction with total ≥ observed (two-sided p-value). This is the minimum bar for "not obviously symmetric noise".
3. **Concentration:** per-symbol trade count and PnL share, HHI, top-trade share of total PnL, and leave-one-symbol-out / leave-one-trade-out totals. Flag if one trade or symbol carries the result.
4. **Time split and activity:** first-half vs second-half trade PnL, monthly buckets, realized-horizon vs full-window annualization, and the 131.54-day no-trade tail. Do not annualize the full window as if it were the realized horizon.
5. **Placebo/absence check:** compare against the J1 census funnel (342 → 187 → 39 → 89 → 11 → 8) and state how many signal-gate events were not traded and why; if a cheap placebo is implemented, document its design and limitations. Do not fabricate unseen data.
6. **Go/no-go conclusion:** a single explicit sentence — signal, noise, or underpowered — supported by the CIs/p-value/concentration numbers, with the OKX/Hyperliquid caveat.

**Implementation guidance:** add `scripts/run_robustness_campaign.py` (read-only against canonical artifacts), a focused test under `tests/`, and record the exact command in this handoff. The script must fail closed on missing/invalid trade data and must never write to canonical stems. If the analysis shows the result is underpowered, say so plainly; that is a valid decision-grade conclusion. Do not relax the $5M volume gate or relabel OKX results as Hyperliquid.

**Formulas (deterministic, seed=20261113):** bootstrap total = sum of 10,000 with-replacement resamples of the 8 `total_pnl` values; return = total / 100,000; CI = 2.5/97.5 percentiles; `prob_total_pnl_positive` = fraction of resamples with total > 0. Sign-flip: for each of the 256 sign masks, total = Σ(sign_i × pnl_i); `p_value` = fraction with total ≥ observed (state one- or two-sided). Concentration: `share_i` = symbol PnL / total PnL, HHI = Σ share_i²; top shares from sorted |pnl|. Time split: sort trades by exit timestamp, split at the median trade, sum each half.

**Gate contract (exact JSON keys checked by `scripts/session_gate.py` → `phase_l_robustness`):** the JSON must contain `generated_at_utc`, `provenance_caveat` (the exact caveat sentence), `bootstrap` with `resamples` ≥ 1000 plus `ci_low_pnl`, `ci_high_pnl`, `prob_total_pnl_positive`; `sign_flip` with `combinations` = 256 and `p_value`; `concentration` with non-empty `symbols`, `top_symbol_pnl_share`, `top_trade_pnl_share`; `time_split` with `first_half_pnl`, `second_half_pnl`; and `conclusion.verdict` ∈ {`signal`, `noise`, `underpowered`}. The Markdown must contain the caveat and the verdict. This makes Phase L machine-checkable, not optional prose.

**This file is the durable handoff.** Next agent (in this order, all mandatory): **(1)** write `scripts/run_robustness_campaign.py` + its test now (CPU-safe while J2 runs) and verify against the current 8 trades; **(2)** confirm/resume J2 to 17/17; **(3)** run Phase K to 9/9 after J2 releases the lock; **(4)** run the Phase H full suite and reproducibility contract; **(5)** execute Phase L and verify it satisfies the §7 gate contract; **(6)** verify J3; **(7)** re-date this handoff with recorded evidence and leave the gate at **8/8**. Do not stop at 5/8.