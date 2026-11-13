# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T11:16:18Z (this session; repo name `CRASH-REBOUND-STRATEGY` ⇒ crash-rebound strategy research/backtest is the priority lens)
**Supersedes:** 2026-11-13T10:25:13Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `a36fa09` (`origin/main`); working tree **dirty** (fixed `scripts/build_spec_comparison.py` NameError + new untracked Phase G+ artifacts). Do **not** `git reset`/`checkout` anything away. Nothing needs committing before Phase H+ (user did not ask to commit).

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T11:16:18Z)
>
> **Inferred from repo `CRASH-REBOUND-STRATEGY` (crash-rebound strategy research/backtest) and state verified 2026-11-13T11:16:18Z.**
>
> **Mission (heavy, mandatory):** complete decision-grade, evidence-backed analysis of the real OKX 283-day crash-rebound campaign already on disk and execute the remaining forward-looking campaign work. **Phase G+ is DONE (artifacts present, hashes §2). Phase H reproducibility-contract test, J2 sensitivity sweep, J3 Hyperliquid runbook, and I/J4 handoff are NOT done. The session is incomplete until their artifacts exist and this handoff is re-dated with evidence.** Do not stop after bootstrap, after tests, or after a narrative summary.
>
> **Execute in order (no shortcuts):**
> 1. **Phase H (NEXT, now that G+ is done):** full suite green (observed `941 passed, 1 skipped` this session); add the automated reproducibility-contract test proving re-run from committed on-disk manifest/cache/universe reproduces `results.trades` and `results.total_pnl` modulo top-level `timestamp`; confirm `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M gates intact. Record observed test counts. Persisted-rebound-fields regression already exists — do not rewrite.
> 2. **Phase J2 (MANDATORY, heavy):** parameter sensitivity sweep on-disk OKX run → `research_state/sensitivity_sweep_real_okx_full.json` + `.md`, ≥15 one-factor-at-a-time runs + baseline, each with params/metrics/runtime; never overwrite canonical artifacts (distinct `--output-prefix` stems; delete only your own rerun files). Use `scripts/run_sensitivity_sweep.py` (parallel, workers=4).
> 3. **Phase J3 (MANDATORY):** upgrade `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` into an executable real Hyperliquid-native acquisition/verification runbook — every step has command, pass/fail check, artifact; if unavailable mark `NOT_RUN` (never fabricate, never relabel OKX as Hyperliquid).
> 4. **Phase I/J4:** update this `HANDOFF.md` with exact commands, observed test counts, artifact paths + sha256, conclusions, J2/J3 outcomes, and the next highest-value bottleneck; re-date header.
>
> **Start now (bottlenecks cleared):**
> 1. `bash scripts/bootstrap_env.sh` (or use `/tmp/venv_h`, pytest 9.2.0 + numpy/pandas/requests/pyarrow ready).
> 2. Phase H: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` → add reproducibility-contract test → re-run → record counts.
> 3. Phase J2: `PYTHONPATH=. python scripts/run_sensitivity_sweep.py --workers 4`.
> 4. Phase J3 → Phase I/J4 (this file).
>
> **Bottleneck status (verified 2026-11-13T11:16:18Z — none blocking):**
> - Deps/env: **unblocked** (`requirements-test.txt`, `scripts/bootstrap_env.sh`, `/tmp/venv_h` ready).
> - Phase G+ **unblocked & done:** fixed `scripts/build_spec_comparison.py:574` (`NameError: buy_share` → reads `actual["buy_leg_pnl_share_pct"]`); ran `scripts/build_spec_comparison.py` → artifacts present with hashes §2.
> - Canonical data/campaign artifacts: **intact, hashes re-verified** (§2). No re-acquisition/re-run needed.
> - Phase J1 census: **complete** (`crash_event_census_real_okx_full.{json,md}`, hashes §3). Do not redo.
> - Working tree: dirty only from the G+ fix + new G+ artifacts (untracked). No stranded campaign/backtest/sweep processes observed. No open gate-bypass/attribution defects.
> - **Remaining work is missing outputs only:** reproducibility-contract test (H), `sensitivity_sweep_real_okx_full.*` (J2), executable J3 runbook, updated handoff (I/J4).
>
> **Do not redo:** OKX archive acquisition, 54-symbol universe derivation, canonical campaign run, J1 census, or G+. **Do not claim Hyperliquid parity from OKX data.** All conclusions must state: "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence."

---

## 0. Verified state this session (2026-11-13T11:16:18Z)

| Check | Result | Evidence |
|---|---|---|
| Git | `main...origin/main` @ `a36fa09`; dirty (modified `scripts/build_spec_comparison.py`; new untracked G+ artifacts). | `git status -sb`, `git log -1` |
| Key artifacts intact | Canonical hashes **re-verified unchanged** (cache provenance, universe, campaign, metrics, census). | `sha256sum` this session → §2/§3 |
| Phase G+ outputs | **Present** (`real_okx_full_spec_comparison.md` + `._summary.json`, hashes §2). Built with `scripts/build_spec_comparison.py` after fixing `NameError` at line 574. | `ls`, `sha256sum` |
| Phase J1 census | **Present, complete.** | `crash_event_census_real_okx_full.json` `46ba…9bec`, `.md` `cbcd…e5b9` |
| Phase H suite | **Green:** `941 passed, 1 skipped` (skip: `tests/test_fetch_archive_ingest_temp_path_rejection_20261109.py:80`). Full suite run this session (~6 min 16 s). | `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` |
| Phase H reproducibility-contract test | **Absent** (not yet added). | `ls tests/` |
| Phase J2/J3 outputs | **Absent** (no `sensitivity_sweep*`; J3 runbook not yet executable step-by-step). | `ls`, `DATA_REQUEST_283D_HYPERLIQUID.md` |
| Environment | `/tmp/venv_h` ready (pytest 9.2.0 + numpy/pandas/requests/pyarrow); `scripts/bootstrap_env.sh` + `requirements-test.txt` present. | `python -m pytest --version` |
| Working tree / processes | Dirty only from G+ fix + artifacts; no stranded campaign/backtest/sweep processes. **No blocking bottlenecks.** | `git status -sb`, `ps aux` |

---

## 1. Previously resolved bottlenecks (do not re-litigate)

| Bottleneck | Resolution | Evidence |
|---|---|---|
| Runner missing test deps | `requirements-test.txt` + `scripts/bootstrap_env.sh` (venv `/tmp/crs-venv`) and `/tmp/venv_h` prebuilt. | files present |
| `_split_leg_pnls` phantom buy on rebound-short trades | Fixed: split only when rebound constituents present; short-only trade attributed to short leg. | `src/metrics/campaign_metrics.py:237` |
| Canonical gap report falsely `ready_for_real_campaign=true` | Regenerated fail-closed from synthetic canonical Hyperliquid provenance. | `research_state/candle_coverage_gap_report.json` `ready=false, blocked=true` |
| `trade_attribution_by_leg` disagreed with `leg_breakdown` | Unified constituent split; sums to grand total. | `src/metrics/campaign_metrics.py:161` |
| Campaign artifact dropped `rebound_short_pnl`/`rebound_hedge_pnl` | Persisted on every serialized trade. | `scripts/run_portfolio.py:408` |
| Trade-frequency gap unexplained | **J1 census completed:** 342 RSI<20 events → 187 vol-pass → 39 bounce → 11 signal-gate-pass → 8 trades; blocking reasons sum to 342 with 0 unexplained signal-gate events. | `research_state/crash_event_census_real_okx_full.{json,md}` |
| `build_spec_comparison.py` crashed (Phase G+ blocked) | Fixed `NameError: buy_share` at line 574 → reads `actual["buy_leg_pnl_share_pct"]`; G+ artifacts now produced. | `scripts/build_spec_comparison.py:574`, `research_state/real_okx_full_spec_comparison.{md,json}` |

**Remaining inefficiencies (not blockers):** full suite ~6+ min; canonical Hyperliquid provenance synthetic so canonical gap report fail-closed by design (do not "fix" by fabricating). Budget heavy runs/sweeps accordingly.

---

## 2. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries: 62 alts + `candles/` + `provenance.json`), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`, sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, 54 loaded/complete, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`. Trades at `results.trades` (not top-level); top-level `timestamp` volatile — exclude from reproducibility diffs.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c` (+ `.csv`).

**Phase G+ outputs (produced this session):**
- `research_state/real_okx_full_spec_comparison.md` — sha256 `4e86b41342885da8e4a7fca420eb1f0caad1c4e8127d9d7d18ae1a97f5400b36`.
- `research_state/real_okx_full_spec_comparison_summary.json` — sha256 `58752ccf35214e53291bae2d9ff7d6cb2130cb220f21016d21794012dffef452`.

**Headline metrics (actual, from artifacts):**
- Equity: 100,000 → 109,159.69; gross/net PnL 9,159.69 / 8,141.29; fees AUM 2.15 + profit-share 1,016.26 = 1,018.40.
- Return: **+9.1597% total**, **+22.5995% annualized** over **0.4301 yr** realized-trade horizon (exit-event equity curve, 9 points); worst DD −2.0275% (−2,091.61 @ `1769551200000`); Sharpe 0.6258, Sortino 1.2618, Calmar 4.3793, win rate 0.5, PF 5.2335.
- Months: 4 positive / 3 negative / 0 flat (7 buckets). Annual: 1768 +3.16%, 1769 −2.03%, 1770 +8.07%, 1779 −0.07%.
- Trades: 8 (4/4); exits `time_exit 6, liquidated 1, target_rebound_short 1`; traded symbols `SOL 3, BCH 2, ETH 1, LINK 1, AVAX 1` (5 of 54). `final_open_positions=0`.
- Per-leg (authoritative): **buy** 8 trades (4 wins) PnL **+10,796.55**, share **117.87%**, PF 5.99; **short** 1 trade (0 wins) PnL **−1,636.86** (short coin +1,067.73, rebound hedge −2,704.59), share **−17.87%**, PF 0.0. `trade_attribution_by_leg` sums to 9,159.69.
- Realized trades: SOL buy liq −9454.97/total +3161.97; ETH buy time_exit −1367.57/−121.63; SOL buy +4333.67/−168.59; LINK buy +2805.23/−1801.38; BCH short target_rebound_short coin+4625.09 (rebound_short_pnl +1067.73, rebound_hedge_pnl −2704.59) total +2988.22; AVAX buy +1537.25/+3499.37; SOL buy +949.82/+1673.73; BCH buy −26.44/−72.00.

**Mandatory caveats (carry into every analysis):**
- **Horizon:** last realized exit `2026-05-20T10:00:00Z`; **no trades in final ~4 months** to 2026-09-28. Annualized is over active ~151-day window, not full 283-day spec window.
- **Venue:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**.
- **Rebound-short:** short leg net negative after hedge separation; `+2,988.22` is the whole BCH trade (buy+short), not the short leg.

---

## 3. Phase J1 — Crash-event census (COMPLETE, do not redo)

Artifacts:
- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae0b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`
- Generated `2026-11-13T09:34:53.360163+00:00`; params RSI(21)<20, min_daily_volume_usd 5M, min_price $5, rebound lookback 3/body 0.5, pos 1.25% dv, max_positions 5, gross_cap 120%, capital 100k. Inputs/manifests match canonical hashes in §2.

Reconciliation (every event has exactly one blocking reason; counts sum; 0 unexplained):
- Events total **342** (RSI<20 across 54 symbols) → volume_gate_pass **187** → bounce_confirmed **39** → regime_min_price_ok **89** → signal_gate_pass **11** → trades opened **8** (all matched to events).
- Blocking reasons: `trade_opened 8`, `volume_gate 155`, `bounce_not_confirmed 159`, `regime_min_price 17`, `one_position_per_coin 3` (sum 342).

**Use this as primary evidence for the trade-frequency gap (8 vs 85) in Phase G+.** Do not regenerate unless inputs change.

---

## 4. Remaining work (definition of done — all required)

### Phase G+ — Spec-vs-actual artifacts (DONE this session)
`research_state/real_okx_full_spec_comparison.md` and `research_state/real_okx_full_spec_comparison_summary.json` written (hashes §2). Every metric table cell populated; divergence analysis evidence-backed with code-path citations; J1 census used as primary trade-frequency evidence. Caveat carried on every claim.

### Phase H — Reproducibility & hardening (NEXT)
- Run full suite green: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` (observed `941 passed, 1 skipped` this session). Record observed counts.
- Encode reproducibility-contract as automated test: re-run campaign from committed on-disk manifest/cache/universe reproduces `results.trades` and `results.total_pnl` byte-for-byte modulo top-level `timestamp`. Guard runtime (run once/cache expected hash). Persisted-rebound-fields regression already done — do not rewrite.
- Re-confirm no gate bypass: `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M enforced; no synthetic/fabricated path.

### Phase J2 — Parameter sensitivity sweep (MANDATORY, heavy)
One-factor-at-a-time around current spec on on-disk OKX manifest/cache/universe:
- RSI threshold 15/20/25; buy target 6/9/12%; buy max hold 24/50/72h; rebound-short target 6/9/12%; short max hold 24/48/72h; ETH hedge cap 1x/2x/3x; position size 0.5/1.25/2.0% of 24h volume.
- ≥15 runs + baseline. Record per-run: params, total/annualized return, worst DD, trade count, per-leg PnL, runtime.
- Outputs: `research_state/sensitivity_sweep_real_okx_full.json` + `.md`. Use distinct `--output-prefix` stems per run; never overwrite canonical artifacts; delete only own rerun files. Conclusions must state which knobs move results and which do not; no fabricated numbers.
- Command: `PYTHONPATH=. python scripts/run_sensitivity_sweep.py --workers 4` (parallel; ~2.7 h serial → wall-clock of a few sequential runs).

### Phase J3 — Real Hyperliquid-native acquisition runbook (MANDATORY)
Produce executable step-by-step runbook (update/extend `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`): source(s), exact archive format, `fetch_hyperliquid_candles.py --source archive` invocation, provenance checks (`all_complete=true`, `ready_for_real_campaign=true`), gated `run_real_campaign.py` command. Every step: command, pass/fail check, artifact written. If data unavailable, state explicitly and mark campaign `NOT_RUN`; never fabricate or relabel OKX as Hyperliquid.

### Phase I / J4 — Handoff update
Record exact commands, observed test counts, all new artifact paths + sha256, analysis conclusions, J2/J3 outcomes, and next highest-value heavy bottleneck. Re-date header.

---

## 5. Canonical commands

- Bootstrap: `bash scripts/bootstrap_env.sh` (venv `/tmp/crs-venv`, deps in `requirements-test.txt`). Alt ready env: `/tmp/venv_h`.
- Tests: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs` (observed `941 passed, 1 skipped`).
- Phase G+: `PYTHONPATH=. python scripts/build_spec_comparison.py` → `research_state/real_okx_full_spec_comparison.{md,json}` (bare filename stem under `research_state/`).
- Derive universe (do not redo unless inputs change): `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
- Real campaign (canonical, do not rerun needlessly): `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full --apply-vault-fees` (`--output-prefix` must be bare filename stem under `research_state/`).
- Phase J2 sweep: `PYTHONPATH=. python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`.
- Canonical gap report: `PYTHONPATH=. python scripts/generate_candle_coverage_gap_report.py` (fail-closed by design on synthetic Hyperliquid provenance).

---

## 6. Hard prohibitions

- Do **not** fabricate/synthesize/"fill" data. Do **not** relabel per-code/partial/BTC-only/OKX runs as Hyperliquid spec evidence.
- Do **not** remove `volume_filter_ok` (all-bars) or per-trade point-in-time trailing-24h ≥$5M filter.
- Do **not** re-acquire data or redo J1/canonical campaign/G+ without cause. Do **not** claim Hyperliquid performance parity from OKX data.
- Do **not** re-litigate closed Phase A. Do **not** treat stale `fix/*-20261030` remote branches as blockers.
- Do **not** delete/clean `research_state/` artifacts; write reruns to new `--output-prefix` stems and delete only your own rerun files after diffing.
- Do **not** mark done with only partial phases: H (incl. reproducibility-contract test), J2, J3, and updated handoff are all required.

**This file is the durable handoff.** The next agent bootstraps env, completes Phase H → J2 → J3 → I/J4 from artifacts above, and leaves updated evidence-backed handoff plus `sensitivity_sweep_real_okx_full.{json,md}`, the reproducibility-contract test, and the Hyperliquid acquisition runbook.
