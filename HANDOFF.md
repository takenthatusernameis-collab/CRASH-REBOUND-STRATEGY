# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T07:42:00Z
**Supersedes:** 2026-11-13T06:48:24Z. This session re-verified the whole state from scratch, corrected a **stale count claim** in the prior handoff, and closed the last open Phase H gap (the persisted-rebound-fields regression test now exists).
**Uncommitted at handoff time:** `M HANDOFF.md` + new `tests/test_campaign_trade_persistence_rebound_fields_20261113.py` (3 tests, passing). The next session must commit these two files first (they are the only working-tree changes), then start Phase G+. Do not `git reset`/`checkout` them away.
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `8e38824` (verified via `git status --porcelain`: the only working-tree changes are the handoff refresh below plus the new test; the committed tree at `8e38824` was clean).

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION
>
> *(Inferred from repo `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtest — and the state verified on 2026-11-13T07:42:00Z.)*
>
> **Priority order (repo-aligned: crash-rebound strategy first, everything else second):**
>
> **Phase G+ — Spec-vs-actual analysis artifact (PRIMARY, do not skip).** Write `research_state/real_okx_full_spec_comparison.md` AND `research_state/real_okx_full_spec_comparison_summary.json`. The markdown must be a decision-grade report: a metric-by-metric table (spec vs actual) plus evidence-backed divergence explanations for EVERY row. A summary paragraph is not acceptable.
>
> **Phase H — Reproducibility & hardening.** Re-run the full suite to green, re-derive the universe and re-run the campaign from on-disk provenance/cache/universe, prove `results.trades` and `results.total_pnl` are byte-stable across runs (exclude the volatile top-level `timestamp`), and add a regression test that serialized campaign trades carry `rebound_short_pnl`/`rebound_hedge_pnl`. **Already verified manually this session — see §0; Phase H is now mostly a matter of codifying the checks as tests.**
>
> **Phase I — Update this HANDOFF** with exact commands, test counts, artifact paths + sha256, conclusions, and the next highest-value heavy work (sensitivity/reruns; a REAL Hyperliquid-native acquisition plan per `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` if true spec parity is required — never fabricate data).
>
> **Do not redo:** the real OKX 1H archive acquisition, the 54-symbol universe derivation, or the full campaign run. All are on disk and verified below (§2). Start from the artifacts.
>
> **Do not claim Hyperliquid parity from OKX data.** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
>
> **Mandatory heavy campaign (execute Phase G+ → H → I in order; do not stop after step 1):**
> 1. **Phase G+** (primary, evidence-first spec-vs-actual).
> 2. **Phase H** (reproducibility & hardening).
> 3. **Phase I** (update this handoff).
>
> **Definition of done for Phase G+ (all must be true):**
> - Spec-vs-actual table includes: total return, annualized return, worst drawdown, positive-month count, trade count, buys/shorts and their win rates, rebound-short profit contribution, and symbol-universe size.
> - Divergence is quantified with artifact evidence: trade-frequency gap (8 vs 85), universe actually traded vs admitted (5 of 54), exit-reason mix, leg mix, active-period coverage, and exposure/gross-cap utilization.
> - The rebound-short finding is stated explicitly: the **short leg's true PnL is −1,636.86** (short coin +1,067.73, rebound hedge −2,704.59); the previously cited `+2,988.22` was the whole BCH trade (buy + short), not the short leg. Contrast with the spec's "~27% of profit" claim.
> - Every claim carries the provenance caveat: "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence."

---

## 0. What this session (2026-11-13T07:42Z) verified — no bottlenecks remain

The prior handoff claimed a RED suite was fixed and the tree clean. Re-verification from a fresh checkout at `8e38824` confirms the fixes hold, corrects one stale number, and adds the missing regression test.

| Check | Result this session | Evidence |
|---|---|---|
| Full suite (fresh venv: `pytest numpy pandas requests`) | **936 passed, 1 skipped**, ~385 s **after** adding the new Phase H regression test (`tests/test_campaign_trade_persistence_rebound_fields_20261113.py`, 3 tests); 933 passed before it. | `PYTHONPATH=. python -m pytest -q` |
| All skips explained | 11 × `pyarrow not installed` (5 files) + 1 × `tmp_path resolves to temp scratch marker` (`tests/test_fetch_archive_ingest_temp_path_rejection_20261109.py:80`). | `-rs` output |
| pyarrow-gated tests actually pass | `16 passed` after `pip install pyarrow` | `tests/test_parquet_*`, `tests/test_streaming_ingest_*` |
| Stale claim in prior handoff | `933 passed, 1 skipped` did not match a fresh run (922/12 before the new test). The earlier number predates the pyarrow/`tmp_path` skip classification. | this table |
| New regression test added | `tests/test_campaign_trade_persistence_rebound_fields_20261113.py` asserts every persisted trade carries `rebound_short_pnl`/`rebound_hedge_pnl`, and that per-leg attribution sums to the grand total. Verified it FAILS if the two fields are removed from `scripts/run_portfolio.py:408` (mutation-checked), then passes. | `git status` shows only this new file + HANDOFF |
| Universe re-derivation | 54 symbols; **identical** to on-disk `universe_okx_full_verified.json` except `generated_at_utc` | `scripts/derive_verified_universe.py` → `/tmp/uni_rerun.json` diff |
| Campaign re-run | `REAL run complete: 8 trades, total_pnl=9159.691934882958`; artifact **identical to committed artifact modulo `timestamp`** | `scripts/run_real_campaign.py --output-prefix rerun_verify_campaign` (temp artifacts deleted after diff) |
| Rebound fields persist on trades | all 8 serialized trades carry `rebound_short_pnl` and `rebound_hedge_pnl` (0.0 for non-rebound legs) | `results.trades[]` |
| Working tree | committed tree at `8e38824` clean; no leftover rerun artifacts. Only intended edits: `HANDOFF.md` + the new test file. | `git status --porcelain` |

**Environment note for the next session:** the runner image has **no pytest/numpy/pandas/requests/pyarrow** preinstalled (`python3 -m pytest` → `No module named pytest`). Create a venv first, e.g. `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pytest numpy pandas requests pyarrow`. This is the single biggest avoidable time sink; do it before anything else.

---

## 1. Previously resolved bottlenecks (do not re-litigate)

| Bottleneck (before) | Resolution | Evidence |
|---|---|---|
| `tests/test_track4f_leg_attribution_hardening.py` — 6 failures: `_split_leg_pnls` split EVERY `short`-legged trade into a phantom `buy` + zero `short`. | `_split_leg_pnls` splits ONLY when rebound constituents are present; buy = trade `pnl`; short = `rebound_short_pnl + rebound_hedge_pnl`. A `short` trade without rebound fields is attributed in full to its own leg. | `src/metrics/campaign_metrics.py:237` |
| Canonical gap report claimed `ready_for_real_campaign=true`. | Regenerated from canonical verified Hyperliquid provenance (synthetic ⇒ fail-closed). | `research_state/candle_coverage_gap_report.json` now `ready=false`, `blocked=true` |
| `trade_attribution_by_leg` disagreed with `leg_breakdown` for rebound trades. | Both now use the same constituent split and sum to the grand total. | `src/metrics/campaign_metrics.py:161` |
| Campaign artifact dropped `rebound_short_pnl`/`rebound_hedge_pnl`. | `scripts/run_portfolio.py` persists both fields on every serialized trade. | `scripts/run_portfolio.py:408` |

---

## 2. Verified current state (real, non-synthetic OKX full run)

**Data (real, non-synthetic, do not re-acquire):**
- OKX 1H archive: `research_state/archives/okx_1h_full_20251220_20260928/` — 64 entries (62 alt archives + `candles/` + `provenance.json`), `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` (`all_complete=true`, `ready_for_real_campaign=true`), sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
- Universe: `research_state/universe_okx_full_verified.json` — 54 selected symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb` (re-derivation confirmed identical).

**Campaign artifacts (verified 2026-11-13T07:31Z, hashes re-checked):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, 54 loaded/complete, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c` (+ `.csv`).
- Note: `trades` lives at `results.trades`, not top level. Top-level `timestamp` is volatile and must be excluded from reproducibility diffs.

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

## 3. Mandatory next campaign — Phase G+ (heavy, evidence-first)

Write BOTH `research_state/real_okx_full_spec_comparison.md` and `research_state/real_okx_full_spec_comparison_summary.json`. The markdown must be a decision-grade report, not a stub.

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

- Confirm `PYTHONPATH=. python3 -m pytest -q` is green; **expected baseline is `936 passed, 1 skipped`** with the documented env-only skips (§0), or `952 passed` if `pyarrow` is installed. Record the exact numbers you observe and the skip reasons.
- Re-derive universe and re-run campaign from on-disk manifest/cache/universe; confirm `results.trades` and `results.total_pnl` are identical across runs, excluding top-level `timestamp`. **Already confirmed manually this session (§0)**; the remaining work is to encode this as an automated test (see next bullet).
- The persisted-rebound-fields regression test is **done** (`tests/test_campaign_trade_persistence_rebound_fields_20261113.py`). The remaining Phase H item is the reproducibility-contract test: a re-run of the campaign over the committed manifest/cache/universe reproduces `results.trades` and `results.total_pnl` byte-for-byte modulo `timestamp`. The manual check passed this session (§0); codify it (guard runtime: run the campaign once per session, or cache the expected hash).
- Re-confirm no gate bypass: `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M remain enforced; no synthetic/fabricated path.

### 3.4 Phase I — update this handoff

Record exact commands, test counts, artifact paths + sha256, the analysis conclusions, and the next highest-value heavy work (sensitivity/reruns; REAL Hyperliquid-native acquisition plan per `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` — never fabricate).

---

## 4. Canonical commands / artifacts

- Test bootstrap (runner image has no deps): `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pytest numpy pandas requests pyarrow`
- Tests: `PYTHONPATH=. /tmp/venv/bin/python -m pytest -q` (add `-rs` to audit skips)
- Derive universe: `PYTHONPATH=. python scripts/derive_verified_universe.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --output research_state/universe_okx_full_verified.json`
- Real campaign: `PYTHONPATH=. python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix campaign_results_real_okx_full --apply-vault-fees`
  - `--output-prefix` must be a bare filename stem under `research_state/`; absolute paths and `..` are rejected by design (`scripts/run_real_campaign.py:286`).
- Canonical gap report: `PYTHONPATH=. python scripts/generate_candle_coverage_gap_report.py` (writes `research_state/candle_coverage_gap_report.json`, sha256 `c8de76070409927233b51fa918300d33d5fb18fcd7c0ffd4fe28f522354b273b`; currently fail-closed by design because canonical Hyperliquid verified provenance is synthetic).
- Key artifacts: `research_state/universe_okx_full_verified.json`, `research_state/campaign_results_real_okx_full.json`, `research_state/campaign_results_real_okx_full_metrics.{json,csv}`, `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`, `research_state/archives/okx_1h_full_20251220_20260928/`.

## 5. Hard prohibitions

- Do **not** fabricate/synthesize/"fill" data. Do **not** relabel per-code/partial/BTC-only runs as full spec evidence.
- Do **not** remove `volume_filter_ok` (all-bars) or the per-trade point-in-time volume filter.
- Do **not** re-acquire data already on disk. Do **not** claim Hyperliquid performance parity from OKX data.
- Do **not** re-litigate closed Phase A. Do **not** treat the stale `fix/*-20261030` remote branches as blockers: they are old, unmerged, and not required for the current main line; review before any merge.
- Do **not** delete or "clean up" `research_state/` artifacts to make a rerun easier; write reruns to a new `--output-prefix` stem and delete only your own rerun files after diffing.

**This file is the durable handoff.** The next agent starts with Phase G+ from the artifacts above and must leave an updated, evidence-backed handoff plus the two comparison artifacts.