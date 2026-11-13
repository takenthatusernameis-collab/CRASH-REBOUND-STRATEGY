# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T19:35:00Z
**Supersedes:** 2026-11-13T19:33:07Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `dd12ee8` (working tree carries the new Phase K/L code + artifacts listed in §0). **Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T19:35:00Z)
>
> **Inferred priority (from repo name `CRASH-REBOUND-STRATEGY`):** the decision-grade crash-rebound validation on real OKX evidence is now **8/8 complete**. The prior bottlenecks (missing Phase L script, poisoned J2 run, dead-after-completion J2 aggregate) are **cleared**. The next work is **decision follow-through**, not another sweep.
>
> **Start-of-session bootstrap + done-gate (run first, record exact output):**
> 1. If `/tmp/crs-venv/bin/python` is missing, run `bash scripts/bootstrap_env.sh`.
> 2. Run: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` — it must print **8/8 checks passed — DONE**.
> 3. Run the Phase L verifier (no writes): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py --check` — expect `OK: 8 trades, verdict=underpowered`.
>
> **Verified state at this handoff (2026-11-13T19:35:00Z):** gate is **8/8** (J2=17 runs, K=9 runs, L=`underpowered`, G+/J1/J3/handoff pass). Full fast suite **966 passed, 1 skipped, 1 deselected**; the reproducibility-contract rerun passed and left the canonical artifact **byte-identical** (sha256 `57973b0c…2f9b8`). No sweeps running; `/tmp/crs-venv` present; next-campaign artifacts (`placebo_okx_full`, `risk_budget_real_okx_full`) **NOT yet present** — that is the remaining work.
>
> **The decision-critical finding (do not skip, do not soften):** Phase L's verdict is **`underpowered`** — the 8-trade bootstrap 95% CI for total PnL is **[-$930.66, +$19,152.38]** (crosses zero), sign-flip one-sided **p=0.09375** (2/256 masks ≥ observed), and the result is **concentrated** (5 traded symbols, top trade/symbol shares near half the PnL). Phase K then shows **RSI<25 + max-positions 8** lifts return to +23.44% **but drives worst drawdown to −18.3%** and trades 33 times — the "improvement" is a **risk-budget trade, not free alpha**, and it sits on the same small-sample base. **Conclusion: the strategy is NOT decision-grade validated; it is a plausible, concentration-heavy signal that is statistically underpowered at n=8.**
>
> **Mandatory next focus campaign (heavy, anti-avoidance) — execute in order, do not stop early:**
> 1. **Power, not another point estimate.** The single biggest blocker to a real decision is **sample size (8 trades)**. Build the next campaign around **statistical power**: (a) a **blocked/structured placebo** that respects the 342→187→39→89→11→8 funnel (e.g. random-entry, same holding/exit rules, same volume/regime gates) run over the same cache to produce a **null distribution** of total PnL — compare the real 8-trade result to it; (b) a **symbol-block bootstrap** (resample whole symbols, not trades) to test whether the result survives symbol-level dependence. Deliverables: `research_state/placebo_okx_full.{json,md}` and an extended `robustness_real_okx_full` that reports the null-distribution p-value. This is the only way to move `underpowered` toward `signal`.
> 2. **Walk-forward / out-of-sample on the same cache.** The current result is in-sample on 2025-12-20..2026-09-28 with a 131-day no-trade tail. Run an **expanding-window walk-forward** (train on the first half, evaluate on the second) and report realized vs realized-horizon annualization. This directly attacks the "is it luck / does it persist" question the handoff still owes.
> 3. **Risk-budget the K winner explicitly.** If RSI<25 + max-pos 8 is pursued, produce a **drawdown-constrained** variant (e.g. daily-loss / max-DD governor) and show the return/DD frontier, so the +23% is not presented without its −18% DD. Artifact: `research_state/risk_budget_real_okx_full.{json,md}`.
> 4. **Hyperliquid parity remains `NOT_RUN`.** Do **not** claim cross-venue parity from OKX data. The only Hyperliquid artifact on disk is the flat synthetic placeholder (`research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet`); never use it as evidence. Keep `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`'s runbook accurate and `NOT_RUN` until real Hyperliquid candles are acquired.
> 5. **Refresh this handoff** with commands, counts, new artifact paths + sha256, the placebo/walk-forward conclusions, and re-run the gate. Do not regress below **8/8**; add gate checks for any new artifact you claim.
>
> **Anti-avoidance rules:** do not stop after reading, planning, or a narrative summary. Do not re-run J2/K/L or re-acquire OKX data without cause (they are final and byte-stable). Do not present the strategy as validated — Phase L says `underpowered`. Do not claim Hyperliquid parity from OKX. Do not use the flat `_verified.parquet` placeholder as evidence. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. Do not fabricate a null distribution — implement the placebo/block-bootstrap for real. The next session must do **heavy compute** (placebo null + walk-forward), not prose.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T19:35:00Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `dd12ee8`, branch `main`. Working tree carries new `scripts/run_robustness_campaign.py`, `scripts/session_gate.py` (Phase L gate), `tests/test_run_robustness_campaign_20261113.py`, `tests/test_session_gate_robustness_20261113.py`, and the new J2/K/L artifacts + per-run files. | `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/crs-venv` present with pytest/numpy/pandas/requests/pyarrow. Recreate via `bash scripts/bootstrap_env.sh` if absent. | `test -x`, imports |
| Done-gate | **8/8 — DONE.** | `scripts/session_gate.py` |
| Phase J2 sweep | **Complete**: `sensitivity_sweep_real_okx_full.{json,md}`, 17 executed runs (baseline + 16 OFAT), 16 reused, wall 541.37s, speedup 27.94x. `no_rebound_short` re-executed successfully after the kwarg fix. | aggregate + `research_state/sweep_runs/*.json` |
| Phase K interaction | **Complete**: `interaction_sweep_real_okx_full.{json,md}`, 9 runs (baseline + 8 two-factor), 1 reused, wall 1623.1s, speedup 4.56x. | aggregate |
| Phase L robustness | **Complete**: `robustness_real_okx_full.{json,md}`, verdict **`underpowered`**, 10,000 resamples, sign-flip p=0.09375 (256 combos), 5 symbols. | artifact + `scripts/session_gate.py` |
| Phase H (suite) | Fast suite **966 passed, 1 skipped, 1 deselected in 306.40s**; reproducibility contract **1 passed in 523.96s**; canonical artifact **byte-identical** after rerun (sha256 `57973b0c…2f9b8`). | `/tmp/fast_out.txt`, `/tmp/repro_out.txt` |
| Phase G+ | **Done (artifacts present).** | `real_okx_full_spec_comparison.{md,summary.json}` |
| Phase J1 | **Done (artifacts present).** | `crash_event_census_real_okx_full.{json,md}` |
| Phase J3 | Runbook present & gate-shaped; Hyperliquid-native campaign **NOT_RUN** (data unavailable). | `DATA_REQUEST_283D_HYPERLIQUID.md` |
| **Next campaign (§5)** | **NOT STARTED.** `placebo_okx_full`, `risk_budget_real_okx_full`, walk-forward artifact all absent. | `ls research_state/` |

**Pre-flight facts confirmed at 2026-11-13T19:35:00Z (no surprises):**
- `git status --short` clean except the `HANDOFF.md` edit just made; HEAD `dd12ee8`, branch `main`.
- `ps aux | grep run_sensitivity|run_robustness|run_real_campaign|pytest` → no sweeps running; `research_state/.sensitivity_sweep.lock` absent.
- `/tmp/crs-venv/bin/python` present and importable.
- `scripts/session_gate.py` → **8/8 checks passed — DONE** (re-run live).
- `scripts/run_robustness_campaign.py --check` → `OK: 8 trades, verdict=underpowered` (re-run live).

### Session recovery / bottleneck playbook (use instead of guessing)

- **All sweeps done; nothing running.** Confirm with `ps aux | grep run_sensitivity` and `ls research_state/.sensitivity_sweep.lock` (should be absent).
- **Re-run a sweep by accident?** The runner is resumable and takes an exclusive lock (rc=3 if held); a fresh invocation reuses every matching per-run file and rebuilds the aggregate without re-executing. Do not use `--no-resume` unless a full redo is intended.
- **`/tmp/crs-venv` missing:** run `bash scripts/bootstrap_env.sh` (requires network); then re-run the gate.
- **Null equity metrics:** the aggregate renderer and conclusions are null-safe (`n/a`, PnL/trade-count ranking); do not "fix" by dropping variants.

### Bottlenecks cleared this campaign (do not re-litigate)

1. **J2 sweep had no resume and kept dying with its session.** It now reuses any per-run file whose tag and knob values match (`_reusable_record`), takes an exclusive lock (`.sensitivity_sweep.lock`, stale-PID recovery), and refuses partial aggregates. Verified: resume reported `16/17 reused`, then `1 to execute`.
2. **A poisoned `no_rebound_short` per-run file** (old `TypeError: got multiple values for keyword argument 'enable_rebound_short'`) was reused by earlier resumes. `_reusable_record` now refuses rejected records, and `_build_config_kwargs` merges the override instead of colliding. Re-executed cleanly: 8 trades, PnL +15,260.10.
3. **A null equity-curve return crashed the final aggregate.** Renderer/conclusions are null-safe (`n/a` + PnL/trade-count ranking), with regression tests.
4. **The "verified" Hyperliquid parquet is a flat placeholder.** `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` has BTC close `60000.0` and ETH close `3000.0` for all 6,792 bars (1 distinct value each), flagged `synthetic_series_detected`. Despite the filename it is **not** Hyperliquid evidence; do not use it. This is why the Hyperliquid campaign remains `NOT_RUN`.
5. **Compute is CPU-bound at 4 workers on a 4-core runner.** Do not run a second sweep or the pytest suite concurrently with a sweep; the only safe speedups are resume and running phases sequentially.

## 1. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run/overwrite)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`; re-hash before citing.
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8` (**re-verified byte-identical at 2026-11-13T19:12:00Z**).
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Headline metrics (actual, from artifacts):** equity 100,000→109,159.69; net PnL 8,141.29; return **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`); worst DD −2.0275%; 8 trades (4W/4L), 5 traded symbols of 54. **Caveats:** active ~151-day horizon; real OKX cross-venue, **NOT Hyperliquid performance evidence**.

## 2. Phase J1 — Crash-event census (COMPLETE, do not redo)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae2b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`
- Reconciliation (0 unexplained): **342** → volume 187 → bounce 39 → regime 89 → signal 11 → trades 8. Blocking-reason counts: `bounce_not_confirmed` 159, `volume_gate` 155, `regime_min_price` 17, `one_position_per_coin` 3, `trade_opened` 8.

## 3. Completed this session — evidence (do not redo)

- **Phase J2** `research_state/sensitivity_sweep_real_okx_full.json` (sha256 `62563cc0cb97e8f64aa47e557e927b76bef60142f73b0540255726c148c67d5a`) + `.md` (`199d903067a271e6e5312d30f3b2e610f0095bbe1c0dacd447c3101e3db341a4`). 17 executed runs, 16 reused, wall 541.37s, speedup 27.94x. Material knobs: `rsi_threshold_25` (+7.97pp, +22 trades), `no_rebound_short` (+6,100 PnL, 0 Δ trades), `buy_target_12pct` (+3,826), `rsi_threshold_15/18` (−3,249, −6 trades), `eth_hedge_cap_1x` (−2.35pp). Spec-locked `position_size_*` rejected by design.
- **Phase K** `research_state/interaction_sweep_real_okx_full.json` (sha256 `b122fe71f2fbe0896bec91cd67a5fc4b54104e45a13779d6eca2be63e6b28b9a`) + `.md` (`f4ab2aeaa2ea3fd7a3a4b9ce770bb3ea60706342ee94b4ebd677163a416172bc`). 9 runs, 1 reused, wall 1623.1s, speedup 4.56x. **`rsi25_maxpos8` = +23.44% return but −18.34% worst DD, 33 trades**; `rsi25_target6` = −1.21% (the only loss); `rsi18_*`/`rsi15_*` collapse to 2 trades. Interaction is material and asymmetric.
- **Phase L** `research_state/robustness_real_okx_full.json` (sha256 `cc3d0eafa36d6ea212127e89491cbd20f247aca4a7bbb468c5844a6825075346`) + `.md` (`58ff4719163714c286a273cc787223d83cb271237c77dbd83733b8e46e837d7e`). **verdict=`underpowered`**: bootstrap 95% CI total PnL **[-930.66, 19152.38]** (crosses 0), P(pnl>0) reported, sign-flip one-sided p=**0.09375** (2/256), 5 symbols, concentration HHI/top-trade share recorded, time split first/second half, J1 absence ledger included.

## 4. Canonical commands

- Bootstrap (only if `/tmp/crs-venv` missing): `bash scripts/bootstrap_env.sh`
- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
- Fast suite (excludes the ~9-min repro test): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs -k "not reproducibility_contract"`
- Full suite (Phase H, includes repro): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Phase L verify (no writes): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py --check`
- Phase L regenerate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py`
- Phase J2 sweep (resumable, already complete): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Phase K interaction sweep (already complete): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --grid interaction --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix interaction_sweep_real_okx_full`
- Phase H repro (distinct prefix, delete after): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/generate_candle_coverage_gap_report.py`

## 5. Next focus campaign (heavy, executable) — power & out-of-sample (NOT STARTED as of 2026-11-13T19:35:00Z)

The gate is 8/8 but the result is `underpowered`. The next campaign must attack **sample size and dependence**, not re-run what exists. **No placebo / walk-forward / risk-budget artifact exists yet** — that is the sole remaining bottleneck and the only path to a decision-grade conclusion.

1. **Structured placebo + null distribution.** Implement a placebo that respects the J1 funnel (random entries passing the same volume/regime gates, same holding/exit rules), run it over the same cache, and report the real result's percentile against the placebo total-PnL distribution. This is the only rigorous way to move `underpowered` → `signal`/`noise`. Deliverable: `research_state/placebo_okx_full.{json,md}` + an extended `robustness_real_okx_full` null-distribution field.
2. **Symbol-block bootstrap.** Resample whole symbols (not trades) to test whether the +9.16% survives symbol-level dependence; report the block-bootstrap CI alongside the trade-level CI.
3. **Walk-forward / out-of-sample.** Expanding-window train/test on the same cache; report realized vs realized-horizon annualization and the 131-day no-trade tail. Directly answers "luck vs persist".
4. **Risk-budget the K winner.** If RSI<25 + max-pos 8 is pursued, add a DD/daily-loss governor and show the return/DD frontier so +23% is never quoted without −18% DD. Deliverable: `research_state/risk_budget_real_okx_full.{json,md}`.
5. **Hyperliquid parity remains `NOT_RUN`** until real candles are acquired; keep the runbook accurate and never relabel OKX as Hyperliquid.

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- **Do not use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence**: it is a flat placeholder (BTC 60000 / ETH 3000, one distinct close each), flagged synthetic. The full-window Hyperliquid campaign is `NOT_RUN`.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+/J2/K/L; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No duplicate sweep while `research_state/.sensitivity_sweep.lock` is held; no `--no-resume` unless a fresh full run is explicitly intended.
- Do not present the strategy as validated: Phase L verdict is `underpowered`; the 8/8 gate proves the evidence chain and a signal-vs-noise characterization, **not future profitability**.

## 7. Definition of done — achieved (8/8)

- **Phase J2:** 17 executed runs, per-run files, evidence-backed conclusions. ✅
- **Phase K:** 9 executed runs, per-run files, interaction conclusions. ✅
- **Phase L:** `robustness_real_okx_full.{json,md}` with bootstrap CI, sign-flip p-value, concentration, time split, verdict. ✅ (`underpowered`)
- **Phase H:** full suite green (fast 966 passed/1 skipped/1 deselected; repro 1 passed); canonical artifact byte-identical. ✅
- **Phase J3:** executable Hyperliquid acquisition runbook maintained; `NOT_RUN`. ✅
- **Phase I/J4:** this handoff refreshed with commands, counts, artifact paths + sha256, conclusions, and the next highest-value bottleneck. Gate **8/8**. ✅

**This file is the durable handoff.** The 8/8 gate is met; the next session must execute the §5 power/out-of-sample campaign (heavy compute), keep the caveat, and not regress below 8/8.