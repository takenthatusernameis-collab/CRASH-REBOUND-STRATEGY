# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T17:18:00Z
**Supersedes:** 2026-11-13T15:25:31Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `4b8c58d` (`chore(kilo): checkpoint agent session`). Working tree has the uncommitted session changes listed in §0. **Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T17:18:00Z)
>
> **Priority (inferred from repo name `CRASH-REBOUND-STRATEGY`):** deliver decision-grade, evidence-backed crash-rebound strategy research/backtest conclusions from real artifacts on disk, then close the remaining heavy campaign phases. **This is not a quick-summary task; heavy execution is required and cannot be skipped.**
>
> **Start-of-session bootstrap + done-gate (run first, record result):**
> 1. Environment is already bootstrapped in this runner at `/tmp/crs-venv`. If it is missing, run `bash scripts/bootstrap_env.sh`.
> 2. Then run: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
>
> **Expected state at this handoff (verified 2026-11-13T17:18:00Z):** gate is **5/7** — Phase G+, J1, J3, and durable-handoff pass; **Phase J2 and Phase K sweep artifacts are not yet on disk**. The Phase J2 sweep is **running now** as a resumable background job: 9/17 per-run files are complete, 8 remain, PID 8069, background id `bgp_1d5da08f60017FUEbJplvtGwXS`, ETA ≈ 2026-11-13T17:51Z. **Do not start a second sweep while it runs** — the runner takes an exclusive lock and will refuse (rc=3). If the process is gone, run the resume command in §5; it reuses completed runs and executes only the missing ones.
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **Finish Phase J2:** confirm the running sweep or resume it; wait for **17/17** per-run files; verify `research_state/sensitivity_sweep_real_okx_full.{json,md}` contains 17 executed runs, baseline first, per-run evidence, conclusions, and the provenance caveat. Record wall-clock/speedup and which knobs move results.
> 2. **Phase H — reproducibility/quality evidence (REQUIRED):** run the full suite `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs` (includes the ~16-min reproducibility-contract rerun) and record exact counts. The fast suite excluding that test already passed this session: **946 passed, 1 skipped, 1 deselected in 668.24s**. Confirm `campaign_results_real_okx_full` reproduces (`results.trades`, `results.total_pnl`, `num_trades`) to a distinct prefix with the canonical artifact byte-identical afterward. Confirm `volume_filter_ok` and per-trade trailing-24h ≥$5M gates remain intact.
> 3. **Phase K — interaction campaign (REQUIRED, next heavy bottleneck):** after J2 releases the lock, run the two-factor grid in §5. It reuses the J2 baseline per-run file and executes **8** new combinations (9 total runs). Produce `research_state/interaction_sweep_real_okx_full.{json,md}` with per-run files under `research_state/sweep_runs/`. State which interactions are material and which are not, with evidence. This is required for **7/7**.
> 4. **Phase J3 — Hyperliquid-native acquisition runbook (maintain):** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` already contains `HYPERLIQUID NATIVE ACQUISITION RUNBOOK` with `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, and `NOT_RUN` tokens. Keep it accurate/executable. The full-window Hyperliquid campaign remains **`NOT_RUN`**: the only Hyperliquid artifact on disk is a flat placeholder (see §0), not evidence. Never fabricate data and never relabel OKX artifacts as Hyperliquid evidence.
> 5. **Phase I/J4 — final evidence refresh:** re-run `scripts/session_gate.py`; record exact commands, observed test counts, new artifact paths + sha256, conclusions from G+/J1/J2/K/J3, and the next highest-value bottleneck. Re-date this header. Only mark done at **7/7**.
>
> **Anti-avoidance rules:** do not stop after reading, planning, or a narrative summary. Do not start a duplicate J2/K sweep while the lock is held. Do not use `--no-resume` to redo completed runs. Do not re-acquire OKX data, re-run the canonical campaign, redo J1, or redo G+ without cause. Do not claim Hyperliquid parity from OKX data. Do not use the flat `_verified.parquet` placeholder as evidence. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. A missing J2/K aggregate is a bottleneck to clear by executing/resuming, not a reason to defer.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T17:18:00Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `4b8c58d`, branch `main`. Uncommitted: `scripts/run_sensitivity_sweep.py`, `scripts/session_gate.py`, `tests/test_sensitivity_sweep_resume_20261113.py`, `.gitignore`, new `research_state/sweep_runs/*.json` evidence. | `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/crs-venv` present with pytest/numpy/pandas/requests/pyarrow. Recreate via `bash scripts/bootstrap_env.sh` if absent. | `test -x`, imports |
| Done-gate | **5/7** — J2 and K missing. | `scripts/session_gate.py` |
| Phase J2 sweep | **Running**: 9/17 per-run files; PID 8069; background id `bgp_1d5da08f60017FUEbJplvtGwXS`. Resume/lock/null-safe fixes applied this session. | `ls research_state/sweep_runs`, `ps` |
| Phase H | Fast suite **946 passed, 1 skipped, 1 deselected in 668.24s** (reproducibility test excluded). Repro test not yet run this session. | background pytest log |
| Phase G+ | **Done (artifacts present).** | `research_state/real_okx_full_spec_comparison.{md,summary.json}` |
| Phase J1 | **Done (artifacts present).** | `research_state/crash_event_census_real_okx_full.{json,md}` |
| Phase J3 | **Runbook present & gate-shaped**; Hyperliquid-native campaign **NOT_RUN** (data unavailable). | `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` |
| Phase K | **Not started** — gate check added; interaction grid implemented. | `scripts/run_sensitivity_sweep.py --grid interaction` |

### Bottlenecks cleared this session (do not re-litigate)

1. **The Phase J2 sweep was killed with its previous session at 5/17 runs.** The runner had no resume, so every interruption discarded ~70 minutes of completed work. It now reuses any per-run file whose tag and knob values match (`_reusable_record`), takes an exclusive lock (`.sensitivity_sweep.lock`, stale-PID recovery), and refuses partial aggregates. Verified: resume reported `5/17 runs reused`, then continued; a second invocation correctly returned `BLOCKER: sweep already running (pid 8069)` (rc=3).
2. **A null equity-curve return crashed the final aggregate.** Several variants (`rsi_threshold_15/18`, `buy_target_12pct`, …) have `total_return_pct=null` because no explicit curve horizon is derivable; the old renderer/conclusions did arithmetic/formatting on `None` and would have crashed after all 17 runs completed. Both are now null-safe (`n/a` + PnL/trade-count ranking), with regression tests.
3. **The "verified" Hyperliquid parquet is a flat placeholder.** `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` has BTC close `60000.0` and ETH close `3000.0` for all 6,792 bars (1 distinct value each). Its cache provenance flags `synthetic_series_detected: [BTC, ETH]`. Despite the filename, it is **not** Hyperliquid market evidence; do not use it. This is why the Hyperliquid campaign remains `NOT_RUN`.

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

## 3. Remaining work — definition of done (all required for 7/7)

- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md` with **17 executed runs** (baseline + 16 one-factor-at-a-time variants), per-run params/metrics/runtime, per-run files under `research_state/sweep_runs/`, canonical untouched, evidence-backed conclusions on which knobs move results and which do not.
- **Phase K:** `interaction_sweep_real_okx_full.json` + `.md` with **9 executed runs** (baseline + 8 two-factor combinations), per-run files under `research_state/sweep_runs/`, evidence-backed interaction conclusions.
- **Phase H:** full suite green with recorded counts; reproducibility-contract test passes against canonical `campaign_results_real_okx_full` (distinct-prefix rerun, temp outputs deleted); gate integrity (`volume_filter_ok` all-bars + per-trade trailing-24h ≥$5M) confirmed.
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook maintained (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, required tokens present); `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/K/J3 outcomes, next highest-value bottleneck. `scripts/session_gate.py` **7/7**.

## 4. Canonical commands

- Bootstrap (only if `/tmp/crs-venv` missing): `bash scripts/bootstrap_env.sh`
- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
- Fast suite (excludes the ~16-min repro test): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs -k "not reproducibility_contract"`
- Full suite (Phase H, includes repro): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Repro test alone: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs tests/test_reproducibility_contract_real_okx_full_20261113.py`
- Phase J2 sweep (parallel, resumable): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Phase K interaction sweep (after J2 releases the lock): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --grid interaction --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix interaction_sweep_real_okx_full`
- Phase H repro (distinct prefix, delete after): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/generate_candle_coverage_gap_report.py`

## 5. Next focus campaign (Phase K) — executable, heavy, gated

The one-factor J2 grid cannot see interactions. Phase K is a 3×3-style two-factor grid around the knobs J2 flags as material (RSI crash trigger × concurrent-position cap, and RSI trigger × buy target). It reuses the same locked, resumable runner and the same committed inputs; the baseline per-run file from J2 is reused, so only **8** new ~16-min runs execute. Aggregate: `research_state/interaction_sweep_real_okx_full.{json,md}`; per-run files under `research_state/sweep_runs/`. `scripts/session_gate.py` now requires this artifact (`phase_k_interaction_sweep`, 9 runs). Until it exists the gate is **not** 7/7.

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- **Do not use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence**: it is a flat placeholder (BTC 60000 / ETH 3000, one distinct close each), flagged synthetic by its cache provenance. The full-window Hyperliquid campaign is `NOT_RUN`.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No duplicate sweep while `research_state/.sensitivity_sweep.lock` is held; no `--no-resume` unless a fresh full run is explicitly intended.
- No "done" without J2 + K artifacts complete/analyzed, Phase H reproducibility-contract test passing + full suite recorded, Phase J3 runbook maintained, and a refreshed evidence-backed handoff at **7/7** on `scripts/session_gate.py`.

**This file is the durable handoff.** Next agent: confirm/resume J2 to 17/17, run the Phase H full suite and reproducibility contract, run Phase K to 9/9, verify J3, then re-date this handoff with recorded evidence and leave the gate at 7/7.