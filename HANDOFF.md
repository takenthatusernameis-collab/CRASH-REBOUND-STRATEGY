# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T11:46:07Z
**Supersedes:** 2026-11-13T11:25:52Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `87b05cf` (`origin/main`); working tree **clean**. Do **not** `git reset`/`checkout` anything away. Nothing needs committing unless explicitly requested.
**Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T11:46:07Z)
>
> **Priority (inferred from repo name `CRASH-REBOUND-STRATEGY`):** deliver decision-grade, evidence-backed crash-rebound strategy research/backtest conclusions from real artifacts on disk, then close the remaining campaign phases. **This is not a quick-summary task; heavy execution is required.**
>
> **Start-of-session done-gate (run first):**
> `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py`
> Expected after this handoff refresh: **4/6 PASS**. The two failures are the heavy missing work: **Phase J2 sensitivity sweep** and **Phase J3 executable Hyperliquid-native runbook**. Do not stop until this command prints **6/6 PASS**.
>
> **Current state (verified 2026-11-13T11:46:07Z):**
> - Git: `main...origin/main` @ `87b05cf`; working tree clean.
> - Phase G+ spec-vs-actual: **done** (`research_state/real_okx_full_spec_comparison.{md,summary.json}`).
> - Phase J1 crash-event census: **done** (`research_state/crash_event_census_real_okx_full.{json,md}`).
> - Full suite: **`941 passed, 1 skipped`**; **942 tests collected**; runtime **375.84s** (`PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs`).
> - Canonical real-OKX manifest/universe/campaign/metrics hashes are intact (see §2).
> - Phase H reproducibility-contract test: **missing**.
> - Phase J2 sweep artifacts: **missing** (`research_state/sensitivity_sweep_real_okx_full.{json,md}` absent).
> - Phase J3 runbook: **not yet executable step-by-step** (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md` needs the required runbook section).
> - Env: `/tmp/venv_h` ready (pytest 9.2.0 + numpy/pandas/requests/pyarrow); 4 CPU / 15 GiB RAM. No stranded campaign/backtest/sweep processes observed.
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **Phase H — reproducibility & hardening (NEXT):** add an automated reproducibility-contract test (suggested `tests/test_reproducibility_contract_real_okx_full_20261113.py`) proving a re-run from the committed on-disk manifest/cache/universe reproduces canonical `results.trades` and `results.total_pnl`, modulo the volatile top-level `timestamp`. Use a **distinct output prefix** (e.g. `reproducibility_check_real_okx_full`), never overwrite canonical artifacts, and delete only your own rerun files. Then re-run the full suite and record observed counts. Confirm `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M gates remain intact. The persisted-rebound-fields regression already exists — do not rewrite it.
> 2. **Phase J2 — heavy sensitivity campaign (REQUIRED):** run the parallel one-factor-at-a-time sweep on the on-disk OKX inputs. Use exactly:
>    `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
>    It must produce **17 runs** (baseline + 16 variants) in `research_state/sensitivity_sweep_real_okx_full.json` + `.md`, with per-run params/metrics/runtime, plus per-run files under `research_state/sweep_runs/`. Never overwrite canonical artifacts. State which knobs move results and which do not; no fabricated numbers. Budget: serial equivalent is ~2.7h; with 4 workers expect materially less wall time, but do not run serially.
> 3. **Phase J3 — executable Hyperliquid-native acquisition/verification runbook (REQUIRED):** upgrade `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` with a section titled exactly `HYPERLIQUID NATIVE ACQUISITION RUNBOOK`. Include source, exact archive format, `fetch_hyperliquid_candles.py --source archive ...`, provenance checks (`all_complete=true` / `ready_for_real_campaign=true`), and the gated `run_real_campaign.py` command. Every step must have a command, pass/fail check, and artifact. If data is unavailable, mark the campaign `NOT_RUN`; **never fabricate or relabel OKX as Hyperliquid**. The gate requires the tokens `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, and `NOT_RUN`.
> 4. **Phase I/J4 — final evidence refresh:** re-run the full suite and `scripts/session_gate.py`; record exact commands, observed test counts, new artifact paths + sha256, conclusions from G+/J1/J2/J3, and the next highest-value bottleneck. Re-date this header.
>
> **Bottlenecks removed this session (do not re-litigate):** refreshed stale handoff to current HEAD/clean tree; corrected the G+ Markdown sha256 to the actual on-disk hash; verified the full suite green; wired the existing machine-checkable `scripts/session_gate.py` into this handoff; verified canonical hashes unchanged; confirmed no stranded processes and a ready test environment. **Remaining blockers are missing outputs only** (Phase H test, Phase J2 sweep artifacts, Phase J3 runbook, final handoff refresh).
>
> **Anti-avoidance rules:** do not stop after reading, planning, bootstrapping, or a narrative summary. Do not re-acquire OKX data, re-run the canonical campaign, redo J1, or redo G+ without cause. Do not claim Hyperliquid parity from OKX data. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. Do not mark done while `scripts/session_gate.py` is not 6/6.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T11:46:07Z)

| Check | Result | Evidence |
|---|---|---|
| Git | `main...origin/main` @ `87b05cf`; clean. | `git status -sb`, `git log -1` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | `find . -name '*HANDOFF*'` |
| Done-gate | `scripts/session_gate.py` exists; current result **4/6** after this refresh (J2/J3 remain). | `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py` |
| Canonical artifacts | Hashes re-verified unchanged. | `sha256sum` → §2/§3 |
| Phase G+ | **Done:** `real_okx_full_spec_comparison.md` (12,840 bytes) + `_summary.json` (8 divergences). | artifact presence/hash |
| Phase J1 | **Done:** `crash_event_census_real_okx_full.{json,md}`; 342 events, 8 trades matched, 0 unexplained. | artifact/hash |
| Tests | **`941 passed, 1 skipped`**; 942 collected; 375.84s. Skip: `tests/test_fetch_archive_ingest_temp_path_rejection_20261109.py:80`. | full pytest run |
| Phase H reproducibility-contract test | **Missing.** | `tests/` |
| Phase J2 outputs | **Missing** (`sensitivity_sweep_real_okx_full.*` absent). | `research_state/` |
| Phase J3 runbook | **Not yet executable step-by-step** (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md` needs the runbook section). | file present, not upgraded |
| Env | `/tmp/venv_h/bin/python` ready (pytest 9.2.0 + deps); `scripts/bootstrap_env.sh` available. | fs checks |
| Processes | No stranded campaign/backtest/sweep processes observed. | `ps` |

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
| Stale handoff/hash mismatch | Handoff re-dated to `2026-11-13T11:46:07Z`; G+ Markdown hash corrected to actual `fb0da9...`; branch/HEAD updated to `87b05cf`. | this file, `sha256sum` |

## 2. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries: 62 alts + `candles/` + `provenance.json`), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`, sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, 54 loaded/complete, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`. Trades at `results.trades` (not top-level); top-level `timestamp` volatile — exclude from reproducibility diffs.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Phase G+ outputs:**
- `research_state/real_okx_full_spec_comparison.md` — sha256 `fb0da9dddeac53177d1a5f946f0eb38f37a2a38fdf3072802da360cb10dd951b`.
- `research_state/real_okx_full_spec_comparison_summary.json` — sha256 `58752ccf35214e53291bae2d9ff7d6cb2130cb220f21016d21794012dffef452`.

**Headline metrics (actual, from artifacts):** equity 100,000→109,159.69; gross/net PnL 9,159.69/8,141.29; fees 1,018.40; return **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`, ~4 months with no trades to 2026-09-28); worst DD −2.0275%; Sharpe 0.6258, Sortino 1.2618, Calmar 4.3793; 8 trades (4W/4L), exits `time_exit 6, liquidated 1, target_rebound_short 1`, 5 traded symbols of 54. Per-leg: buy +10,796.55 (117.87%), short −1,636.86 (−17.87%, short coin +1,067.73, hedge −2,704.59); attribution sums to total. **Caveats:** active ~151-day horizon not full 283 days; real OKX cross-venue, **NOT Hyperliquid performance evidence**; rebound-short leg net negative (BCH whole-trade total +2,988.22 ≠ short-leg PnL).

## 3. Phase J1 — Crash-event census (COMPLETE, do not redo)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae0b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`

Reconciliation (0 unexplained): **342** RSI<20 events → volume_gate_pass **187** → bounce_confirmed **39** → regime_min_price_ok **89** → signal_gate_pass **11** → trades opened **8**. Blocking: `trade_opened 8, volume_gate 155, bounce_not_confirmed 159, regime_min_price 17, one_position_per_coin 3` (sum 342). Use as primary trade-frequency (8 vs 85) evidence in Phase G+.

## 4. Remaining work — definition of done (all required)

- **Phase H:** full suite green with recorded counts; automated reproducibility-contract test (re-run from committed on-disk manifest/cache/universe reproduces `results.trades` and `results.total_pnl` modulo top-level `timestamp`); gate integrity confirmed.
- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md`, 17 runs (baseline + 16 one-factor-at-a-time variants: RSI 15/18/25; buy target 6/12%; buy hold 24/72h; short target 6/12%; short hold 24/72h; ETH hedge 1x/2x; no rebound short; max positions 3/8; plus two spec-locked position-size probes recorded as rejected), per-run params/metrics/runtime, distinct stems, canonical untouched, evidence-backed conclusions. The gate requires `runs` to be a list of at least 16.
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook in `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` with exact `HYPERLIQUID NATIVE ACQUISITION RUNBOOK` section; command + pass/fail + artifact per step; `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/J3 outcomes, next highest-value bottleneck.

## 5. Canonical commands

- Done-gate: `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py`
- Bootstrap: `bash scripts/bootstrap_env.sh` (or use `/tmp/venv_h`).
- Tests: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs`
- G+ (done): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/build_spec_comparison.py`
- Universe (do not redo): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
- Real campaign (canonical, do not rerun): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full --apply-vault-fees`
- Phase H reproducibility check (use a distinct prefix; do not overwrite canonical): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Phase J2 sweep: `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/generate_candle_coverage_gap_report.py`

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No "done" without the Phase H reproducibility-contract test, Phase J2 artifacts, Phase J3 executable runbook, and a refreshed evidence-backed handoff at **6/6** on `scripts/session_gate.py`.

**This file is the durable handoff.** Next agent: run the done-gate, then complete Phase H → J2 → J3 → I/J4 with evidence and leave updated artifacts + this handoff re-dated.