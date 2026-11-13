# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T19:38:37Z
**Supersedes:** 2026-11-13T19:35:00Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `dd12ee8` (working tree may carry uncommitted changes from this session). **Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T19:38:37Z)
>
> **Inferred priority (from repo name `CRASH-REBOUND-STRATEGY`):** deliver a **decision-grade, statistically defensible validation** of the crash-rebound strategy on real evidence. The 8/8 evidence-chain gate is complete, but **Phase L verdict is `underpowered` (n=8 trades, bootstrap 95% CI crosses zero, sign-flip p=0.09375, concentrated)**. The strategy is **NOT validated**. The next session must do **heavy compute that moves power/out-of-sample confidence**, not another point sweep, not prose, not re-runs of completed phases.
>
> **Start-of-session bootstrap + done-gate (run first, record exact output):**
> 1. If `/tmp/crs-venv/bin/python` is missing, run `bash scripts/bootstrap_env.sh`.
> 2. Run: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` — must print **8/8 checks passed — DONE**.
> 3. Verify L (no writes): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py --check` — expect `OK: 8 trades, verdict=underpowered`.
> 4. Confirm no concurrent work: `ps aux | grep -E 'run_sensitivity|run_robustness|run_real_campaign|pytest' | grep -v grep || true` and `ls research_state/.sensitivity_sweep.lock 2>&1 || echo "no lock"`.
>
> **Verified baseline (as of 2026-11-13T19:38:37Z):** gate **8/8** (J2=17, K=9, L=`underpowered`, G+/J1/J3/handoff). Fast suite **966 passed, 1 skipped, 1 deselected**; repro contract green; canonical campaign artifact byte-identical (sha256 `57973b0c…2f9b8`). No sweeps running; `/tmp/crs-venv` present. **Missing next-campaign deliverables:** `research_state/placebo_okx_full.*`, `research_state/risk_budget_real_okx_full.*`, and any walk-forward artifact — **this is the blocking gap.**
>
> **Decision-critical facts (do not soften):**
> - Canonical real OKX (283d, 54 symbols, 6792 bars/symbol, 5M vol gate, non-synthetic): **8 trades (4W/4L, 5 symbols), +9.1597% total / +22.5995% annualized over 0.4301y, worst DD −2.0275%, PnL +9159.69**. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
> - Phase L (`underpowered`): bootstrap 95% CI total PnL **[-$930.66, +$19,152.38]** (crosses 0), sign-flip one-sided **p=0.09375** (2/256), concentration high (top symbol/trade share ~0.51/0.38, 5 traded symbols). Small-sample result — not decision-grade.
> - Phase K: `rsi25_maxpos8` => **+23.44% but −18.34% worst DD, 33 trades** (risk-budget trade, not free alpha); `rsi25_target6` is the only loss. Interaction is material/asymmetric on the same small-sample base.
> - Hyperliquid-native campaign **NOT_RUN**. `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` is a **flat synthetic placeholder** (BTC 60000 / ETH 3000, 1 distinct close each) — **never use as evidence**. All conclusions are **real OKX cross-venue, NOT Hyperliquid performance evidence**.
>
> **MANDATORY NEXT FOCUS CAMPAIGN (execute in order; heavy compute; do not stop early):**
> 1. **Structured placebo / null distribution (primary).** Build a placebo that respects the J1 funnel (342→187→39→89→11→8): random entries subject to the same volume/regime gates and same holding/exit rules, run over the same on-disk cache/manifest/universe (no network, no canonical overwrite). Generate a **null distribution of total PnL** (and return/DD) and report the real 8-trade result's percentile/p-value against it. This is the only rigorous path from `underpowered` → `signal`/`noise`.
>    - Deliverables: `research_state/placebo_okx_full.json`, `research_state/placebo_okx_full.md` (method, N simulations, seed, gates preserved, null stats, real-vs-null percentile, interpretation). Extend/emit robustness evidence as needed but **do not overwrite** `robustness_real_okx_full.*` unless adding a clearly versioned companion; prefer a new artifact that the gate/handoff can cite.
> 2. **Symbol-block bootstrap.** Resample **whole symbols** (not trades) to capture symbol-level dependence; report block-bootstrap CI for total PnL/return alongside the trade-level CI and state whether sign/conclusion survives.
>    - Deliverable: include in placebo/robustness companion artifact with explicit method and seed.
> 3. **Walk-forward / out-of-sample on same cache.** Expanding-window (e.g. first-half train/second-half test, or rolling) on 2025-12-20..2026-09-28 cache; report realized OOS performance, active horizon, and effect of 131-day no-trade tail. Directly test luck vs persistence.
>    - Deliverable: `research_state/walkforward_okx_full.json` and `research_state/walkforward_okx_full.md`.
> 4. **Risk-budget the K "winner".** If `rsi25_maxpos8` is discussed, produce a **drawdown-constrained/daily-loss-governed** variant and the **return vs worst-DD frontier** so +23% is never quoted without −18% DD.
>    - Deliverable: `research_state/risk_budget_real_okx_full.json` and `research_state/risk_budget_real_okx_full.md`.
> 5. **Hyperliquid parity remains `NOT_RUN`.** Keep `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` accurate; do not claim parity from OKX and do not use the flat placeholder parquet.
> 6. **Integrate & report.** Refresh this handoff with commands run, counts, new artifact paths + sha256, placebo/walk-forward/risk conclusions, and re-run `scripts/session_gate.py` (must remain **8/8**). Add gate checks for any new artifact you claim complete.
>
> **Acceptance criteria for this campaign:** placebo null distribution computed on real cache with preserved gates (no fabrication), symbol-block bootstrap reported, walk-forward OOS reported, risk/DD frontier reported, all caveats intact, handoff updated with hashes/commands, gate still 8/8.
>
> **Anti-avoidance rules:** Do not stop after reading/planning/summary. Do not re-run J2/K/L or re-acquire OKX data without cause (complete, byte-stable). Do not present the strategy as validated. Do not fabricate nulls or p-values. Do not claim Hyperliquid parity from OKX or use the flat placeholder. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. Do not create a second handoff file. The next session must execute **heavy compute** and produce the missing artifacts.

---

## 0. Verified state (2026-11-13T19:38:37Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `dd12ee8`, branch `main`. Working tree may have session edits (e.g. this handoff). | `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/crs-venv` present with pytest/numpy/pandas/requests/pyarrow. Recreate via `bash scripts/bootstrap_env.sh` if absent. | `test -x`, imports |
| Done-gate | **8/8 — DONE.** | `scripts/session_gate.py` |
| Phase J2 sweep | **Complete**: `sensitivity_sweep_real_okx_full.{json,md}`, 17 executed runs (baseline + 16 OFAT), 16 reused, wall 541.37s, speedup 27.94x. | aggregate + `research_state/sweep_runs/*.json` |
| Phase K interaction | **Complete**: `interaction_sweep_real_okx_full.{json,md}`, 9 runs (baseline + 8 two-factor), 1 reused, wall 1623.1s, speedup 4.56x. | aggregate |
| Phase L robustness | **Complete**: `robustness_real_okx_full.{json,md}`, verdict **`underpowered`**, 10,000 resamples, sign-flip p=0.09375 (256 combos), 5 symbols. | artifact + `--check` |
| Phase H (suite) | Fast suite **966 passed, 1 skipped, 1 deselected**; reproducibility contract passed; canonical artifact **byte-identical** (sha256 `57973b0c…2f9b8`). | prior verified run |
| Phase G+ | **Done.** | `real_okx_full_spec_comparison.{md,summary.json}` |
| Phase J1 | **Done.** | `crash_event_census_real_okx_full.{json,md}` |
| Phase J3 | Runbook present; Hyperliquid-native campaign **NOT_RUN** (data unavailable). | `DATA_REQUEST_283D_HYPERLIQUID.md` |
| **Next campaign (§5)** | **NOT STARTED.** `placebo_okx_full`, `walkforward_okx_full`, `risk_budget_real_okx_full` absent. | `ls research_state/` |

**Pre-flight facts (reconfirm at session start):** no `research_state/.sensitivity_sweep.lock`, no active sweep/pytest processes, `/tmp/crs-venv` usable.

### Bottlenecks cleared (do not re-litigate)

1. J2 runner is resumable with exclusive lock (`.sensitivity_sweep.lock`, stale-PID recovery) and refuses partial aggregates; matching per-run files reused.
2. Poisoned `no_rebound_short` case fixed (`_reusable_record` rejects rejected records; kwarg merge collision fixed) and re-executed cleanly.
3. Null equity-curve rendering/conclusions are null-safe (`n/a`, PnL/trade-count ranking).
4. "Verified" Hyperliquid parquet is a **flat placeholder** (BTC 60000 / ETH 3000, synthetic-flagged) — **not evidence**; Hyperliquid campaign remains `NOT_RUN`.
5. CPU-bound (4 workers/4 cores): do not run concurrent sweeps or pytest alongside sweeps; speedups are resume + sequential phases.

## 1. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run/overwrite)

**Data/provenance:** `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`). Universe `research_state/universe_okx_full_verified.json` (54 symbols, `min_24h_volume_usd=5,000,000`).

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Headline:** 100,000→109,159.69; net PnL 8,141.29; **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`); worst DD −2.0275%; 8 trades (4W/4L), 5/54 symbols. **Caveat:** active ~151d horizon; **real OKX cross-venue, NOT Hyperliquid performance evidence**.

## 2. Phase J1 — Crash-event census (COMPLETE)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae2b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`
- Reconciliation (0 unexplained): **342** → volume 187 → bounce 39 → regime 89 → signal 11 → trades 8.

## 3. Completed phases — evidence (do not redo)

- **J2** `sensitivity_sweep_real_okx_full.{json,md}` (sha256 `62563cc0cb97e8f64aa47e557e927b76bef60142f73b0540255726c148c67d5a` / `199d903067a271e6e5312d30f3b2e610f0095bbe1c0dacd447c3101e3db341a4`). 17 runs, 16 reused. Material: `rsi_threshold_25` (+7.97pp,+22), `no_rebound_short` (+6100 PnL), `rsi_threshold_15/18` (−3249,−6), `eth_hedge_cap_1x` (−2.35pp). Spec-locked sizing rejected by design.
- **K** `interaction_sweep_real_okx_full.{json,md}` (sha256 `b122fe71f2fbe0896bec91cd67a5fc4b54104e45a13779d6eca2be63e6b28b9a` / `f4ab2aeaa2ea3fd7a3a4b9ce770bb3ea60706342ee94b4ebd677163a416172bc`). 9 runs. `rsi25_maxpos8` **+23.44% / −18.34% DD / 33 trades**; `rsi25_target6` −1.21%; `rsi18_*`/`rsi15_*` collapse to 2 trades.
- **L** `robustness_real_okx_full.{json,md}` (sha256 `cc3d0eafa36d6ea212127e89491cbd20f247aca4a7bbb468c5844a6825075346` / `58ff4719163714c286a273cc787223d83cb271237c77dbd83733b8e46e837d7e`). **verdict=`underpowered`**: bootstrap 95% CI PnL **[-930.66, 19152.38]**, sign-flip one-sided p **0.09375** (2/256), 5 symbols, concentration/time-split/J1 ledger recorded.

## 4. Canonical commands

- Bootstrap (if needed): `bash scripts/bootstrap_env.sh`
- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
- Fast suite: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs -k "not reproducibility_contract"`
- Full suite (Phase H): `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Phase L verify (no writes): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py --check`
- Phase L regenerate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_robustness_campaign.py`
- Phase J2 (resumable, complete): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Phase K (complete): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --grid interaction --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix interaction_sweep_real_okx_full`
- Repro check (distinct prefix, delete after): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Gap report (fail-closed): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/generate_candle_coverage_gap_report.py`

## 5. Next focus campaign (heavy, executable) — power & out-of-sample (NOT STARTED)

Sole remaining bottleneck: **no placebo / symbol-block bootstrap / walk-forward / risk-budget artifacts exist**. Execute §READ FIRST items 1-6. All work must use existing on-disk real OKX cache/manifest/universe, preserve gates, emit reproducible artifacts (paths + sha256 + method/seed), and keep the OKX-not-Hyperliquid caveat. Do not regress below 8/8.

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- **Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence** (flat placeholder: BTC 60000 / ETH 3000, 1 distinct close each, synthetic). Hyperliquid campaign `NOT_RUN`.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical campaign/J1/G+/J2/K/L; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No duplicate sweep while `.sensitivity_sweep.lock` is held; no `--no-resume` unless explicitly intended.
- Do not present the strategy as validated: **Phase L = `underpowered`**; 8/8 proves evidence-chain completeness, **not future profitability**.
- Do not create additional handoff/status files. This file is the single durable handoff.

## 7. Definition of done — evidence chain achieved (8/8), decision validation NOT achieved

- **J2:** 17 runs, evidence-backed conclusions. ✅
- **K:** 9 runs, interaction conclusions. ✅
- **L:** bootstrap CI, sign-flip p, concentration, time split, verdict **`underpowered`**. ✅
- **H:** full suite green; canonical artifact byte-identical. ✅
- **J3:** Hyperliquid runbook maintained; `NOT_RUN`. ✅
- **I/J4:** handoff current, single-file, next bottleneck explicit. ✅

**This file is the durable handoff.** Gate 8/8 met for evidence chain; **decision-grade validation remains open** until §5 power/OOS/risk-budget campaign produces real artifacts. Next session must do heavy compute, not avoid it.
