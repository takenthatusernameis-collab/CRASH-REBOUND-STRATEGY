# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T11:25:52Z
**Supersedes:** 2026-11-13T11:16:18Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `a36fa09` (`origin/main`); working tree **dirty** (modified `scripts/build_spec_comparison.py` fix + untracked Phase G+ artifacts in `research_state/`). Do **not** `git reset`/`checkout` anything away. Nothing needs committing unless explicitly requested.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T11:25:52Z)
>
> **Priority (inferred from repo name `CRASH-REBOUND-STRATEGY`):** deliver decision-grade, evidence-backed crash-rebound strategy research/backtest conclusions from real artifacts on disk, then close remaining campaign phases. **This is not a quick-summary task; heavy execution is required.**
>
> **Current state (verified):** Phase G+ spec-vs-actual artifacts are **done** (`research_state/real_okx_full_spec_comparison.{md,summary.json}`). Phase J1 crash-event census is **done** (`research_state/crash_event_census_real_okx_full.{json,md}`). Full suite last observed **`941 passed, 1 skipped`**. Canonical real OKX campaign/manifest/universe hashes are intact (see §2). **No blocking infra/data bottlenecks observed.**
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **Phase H (reproducibility & hardening, NEXT):** bootstrap env if needed (`bash scripts/bootstrap_env.sh` or use `/tmp/venv_h`), run `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` and record observed counts; add an automated reproducibility-contract test proving re-run from committed on-disk manifest/cache/universe reproduces `results.trades` and `results.total_pnl` byte-for-byte modulo top-level `timestamp` (guard runtime/cache expected value appropriately); re-run suite; confirm `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M gates remain intact. Persisted-rebound-fields regression already exists — do not rewrite.
> 2. **Phase J2 (heavy sensitivity campaign, REQUIRED):** run one-factor-at-a-time sweep on on-disk OKX inputs with distinct output stems, never overwriting canonical artifacts. Produce `research_state/sensitivity_sweep_real_okx_full.json` + `.md` with **≥15 runs + baseline** and per-run params/metrics/runtime. Use `PYTHONPATH=. python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`. State which knobs move results and which do not; no fabricated numbers.
> 3. **Phase J3 (REQUIRED):** upgrade `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` into an executable Hyperliquid-native acquisition/verification runbook (source, exact archive format, `fetch_hyperliquid_candles.py --source archive`, provenance checks `all_complete=true`/`ready_for_real_campaign=true`, gated `run_real_campaign.py`). Every step must have command, pass/fail check, artifact. If unavailable mark `NOT_RUN`; **never fabricate or relabel OKX as Hyperliquid**.
> 4. **Phase I/J4 (REQUIRED):** update this `HANDOFF.md` with exact commands, observed test counts, new artifact paths + sha256, conclusions (G+ evidence + J1/J2/J3 outcomes), and next highest-value bottleneck; re-date header.
>
> **Bottlenecks (verified 2026-11-13T11:25:52Z):** deps/test env unblocked (`requirements-test.txt`, `scripts/bootstrap_env.sh`, `/tmp/venv_h` ready; `/tmp/crs-venv` may need bootstrap but is not a blocker). G+ script `NameError` fixed. Canonical data/campaign/J1/G+ artifacts intact — **do not re-acquire or rerun them without cause**. No stranded campaign/backtest/sweep processes observed. Remaining blockers are **missing outputs only** (H reproducibility-contract test, J2 sweep artifacts, executable J3 runbook, refreshed handoff).
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Do not fabricate/synthesize data, do not relax `volume_filter_ok`/trailing-24h ≥$5M gates, do not overwrite canonical artifacts, do not claim completion with partial phases.

---

## 0. Verified state (2026-11-13T11:25:52Z)

| Check | Result | Evidence |
|---|---|---|
| Git | `main...origin/main` @ `a36fa09`; dirty (modified `scripts/build_spec_comparison.py`; untracked Phase G+ artifacts). | `git status -sb`, `git log -1` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | `find . -name '*HANDOFF*'` |
| Canonical artifacts | Hashes re-verified unchanged (manifest/universe/campaign/metrics/census). | `sha256sum` → §2/§3 |
| Phase G+ | **Done:** `real_okx_full_spec_comparison.md` + `_summary.json` present (hashes §2). | artifact presence/hash |
| Phase J1 | **Done:** `crash_event_census_real_okx_full.{json,md}` present (hashes §3). | artifact presence/hash |
| Tests (last observed) | **`941 passed, 1 skipped`** (skip `tests/test_fetch_archive_ingest_temp_path_rejection_20261109.py:80`). | prior session full run recorded |
| Phase H reproducibility-contract test | **Missing.** | `tests/` |
| Phase J2 outputs | **Missing** (`sensitivity_sweep_real_okx_full.*` absent). | `research_state/` |
| Phase J3 runbook | **Not yet executable step-by-step** (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md` needs upgrade). | file present, not upgraded |
| Env | `/tmp/venv_h/bin/python` ready (pytest 9.2.0 + deps); `/tmp/crs-venv` absent but `bash scripts/bootstrap_env.sh` available. | fs checks |
| Processes | No stranded campaign/backtest/sweep processes observed. | `ps aux` |

## 1. Previously resolved bottlenecks (do not re-litigate)

| Bottleneck | Resolution | Evidence |
|---|---|---|
| Runner missing test deps | `requirements-test.txt` + `scripts/bootstrap_env.sh`; `/tmp/venv_h` ready. | files/env present |
| `_split_leg_pnls` phantom buy on rebound-short trades | Split only when rebound constituents present; short-only attribution fixed. | `src/metrics/campaign_metrics.py:237` |
| Canonical gap report falsely ready | Regenerated fail-closed from synthetic canonical Hyperliquid provenance. | `research_state/candle_coverage_gap_report.json` fail-closed |
| `trade_attribution_by_leg` vs `leg_breakdown` mismatch | Unified constituent split; sums to grand total. | `src/metrics/campaign_metrics.py:161` |
| Campaign artifact dropped rebound-short fields | `rebound_short_pnl`/`rebound_hedge_pnl` persisted per trade. | `scripts/run_portfolio.py:408` |
| Trade-frequency gap unexplained | J1 census completed: 342→187→39→11→8 with 0 unexplained signal-gate events. | `research_state/crash_event_census_real_okx_full.*` |
| `build_spec_comparison.py` crash (G+ blocked) | Fixed `NameError` (`buy_share` → `actual["buy_leg_pnl_share_pct"]`); G+ artifacts produced. | `scripts/build_spec_comparison.py:574`, §2 artifacts |

## 2. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries: 62 alts + `candles/` + `provenance.json`), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`, sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, 54 loaded/complete, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`. Trades at `results.trades` (not top-level); top-level `timestamp` volatile — exclude from reproducibility diffs.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Phase G+ outputs:**
- `research_state/real_okx_full_spec_comparison.md` — sha256 `4e86b41342885da8e4a7fca420eb1f0caad1c4e8127d9d7d18ae1a97f5400b36`.
- `research_state/real_okx_full_spec_comparison_summary.json` — sha256 `58752ccf35214e53291bae2d9ff7d6cb2130cb220f21016d21794012dffef452`.

**Headline metrics (actual, from artifacts):** equity 100,000→109,159.69; gross/net PnL 9,159.69/8,141.29; fees 1,018.40; return **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`, ~4 months with no trades to 2026-09-28); worst DD −2.0275%; Sharpe 0.6258, Sortino 1.2618, Calmar 4.3793; 8 trades (4W/4L), exits `time_exit 6, liquidated 1, target_rebound_short 1`, 5 traded symbols of 54. Per-leg: buy +10,796.55 (117.87%), short −1,636.86 (−17.87%, short coin +1,067.73, hedge −2,704.59); attribution sums to total. **Caveats:** active ~151-day horizon not full 283 days; real OKX cross-venue, **NOT Hyperliquid performance evidence**; rebound-short leg net negative (BCH whole-trade total +2,988.22 ≠ short-leg PnL).

## 3. Phase J1 — Crash-event census (COMPLETE, do not redo)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae0b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`

Reconciliation (0 unexplained): **342** RSI<20 events → volume_gate_pass **187** → bounce_confirmed **39** → regime_min_price_ok **89** → signal_gate_pass **11** → trades opened **8**. Blocking: `trade_opened 8, volume_gate 155, bounce_not_confirmed 159, regime_min_price 17, one_position_per_coin 3` (sum 342). Use as primary trade-frequency (8 vs 85) evidence in Phase G+.

## 4. Remaining work — definition of done (all required)

- **Phase H:** full suite green with recorded counts; add automated reproducibility-contract test (re-run from committed on-disk manifest/cache/universe reproduces `results.trades` and `results.total_pnl` modulo top-level `timestamp`); confirm gate integrity.
- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md`, ≥15 one-factor-at-a-time runs + baseline (RSI 15/20/25; buy target 6/9/12%; buy hold 24/50/72h; short target 6/9/12%; short hold 24/48/72h; ETH hedge 1x/2x/3x; pos size 0.5/1.25/2.0% dv), per-run params/metrics/runtime, distinct stems, canonical untouched, evidence-backed conclusions.
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook in/linked from `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (command + pass/fail + artifact per step); `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/J3 outcomes, next highest-value bottleneck.

## 5. Canonical commands

- Bootstrap: `bash scripts/bootstrap_env.sh` (or use `/tmp/venv_h`).
- Tests: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs`
- G+ (done): `PYTHONPATH=. python scripts/build_spec_comparison.py`
- Universe (do not redo): `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
- Real campaign (canonical, do not rerun): `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full --apply-vault-fees`
- J2 sweep: `PYTHONPATH=. python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. python scripts/generate_candle_coverage_gap_report.py`

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No "done" without H reproducibility-contract test, J2 artifacts, J3 executable runbook, and refreshed evidence-backed handoff.

**This file is the durable handoff.** Next agent: complete Phase H → J2 → J3 → I/J4 with evidence and leave updated artifacts + this handoff re-dated.
