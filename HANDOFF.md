# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T15:25:31Z
**Supersedes:** 2026-11-13T12:46:12Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `e474127` (`chore(kilo): checkpoint agent session`). Working tree clean at handoff time. **Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T15:25:31Z)
>
> **Priority (inferred from repo name `CRASH-REBOUND-STRATEGY`):** deliver decision-grade, evidence-backed crash-rebound strategy research/backtest conclusions from real artifacts on disk, then close the remaining campaign phases. **This is not a quick-summary task; heavy execution is required and cannot be skipped.**
>
> **Start-of-session bootstrap + done-gate (run first, record result):**
> 1. Environment is **not** prebuilt in this runner (`/tmp/venv_h` missing). Bootstrap first: `bash scripts/bootstrap_env.sh` (creates `/tmp/crs-venv` and installs `requirements-test.txt`: pytest, numpy, pandas, requests, pyarrow).
> 2. Then run: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py`
>
> **Current expected state at this handoff (verified 2026-11-13T15:25:31Z):** Phase G+ comparison, Phase J1 census, Phase J3 executable runbook, and durable handoff checks are satisfied by artifacts on disk; **Phase J2 sensitivity sweep artifacts are missing** (`research_state/sensitivity_sweep_real_okx_full.{json,md}` absent, `research_state/sweep_runs/` absent) and **no sweep process is running**. The previous handoff referenced an in-progress sweep (`bgp_1d4e41769001y36sfhugzewAxv`) that is **not present** in this environment. Therefore the gate is expected **< 6/6 until J2 is completed**. **Do not stop until `scripts/session_gate.py` prints 6/6 PASS, Phase H is fully evidenced (full suite green with recorded counts and reproducibility contract passing), J2 artifacts are complete and analyzed, and this handoff is re-dated with evidence.**
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **Bootstrap & baseline gate:** create/use a working venv, run `scripts/session_gate.py`, and record the exact pass/fail state before changes.
> 2. **Phase H — reproducibility/quality evidence (REQUIRED):** run the full suite `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs` and record observed counts. Ensure the reproducibility-contract test for `campaign_results_real_okx_full` passes (if missing, add a focused test that re-runs to a distinct `--output-prefix` such as `reproducibility_check_real_okx_full` and asserts `results.num_trades`/`results.total_pnl` match canonical modulo top-level `timestamp`; **delete only your own rerun files, never touch canonical artifacts**). Confirm `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M gates remain intact.
> 3. **Phase J2 — finish heavy sensitivity campaign (REQUIRED, currently missing):** produce the full sweep from committed inputs (no re-acquisition, no canonical overwrites). Preferred command: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`. Must yield **baseline + 16 one-factor-at-a-time runs (17 total executed per grid/baseline)** with aggregate `research_state/sensitivity_sweep_real_okx_full.json` + `.md` and per-run files under `research_state/sweep_runs/`. Analyze and state explicitly which knobs move results and which do not (with evidence); record runtime/wall-clock and speedup as reported. Do **not** run serially unless workers unavailable; do **not** overwrite canonical artifacts.
> 4. **Phase J3 — Hyperliquid-native acquisition runbook (REQUIRED to maintain):** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` already contains `HYPERLIQUID NATIVE ACQUISITION RUNBOOK` with `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, and `NOT_RUN` tokens. Keep it accurate/executable. Verified Hyperliquid-native full-window data is unavailable in this environment — campaign remains **`NOT_RUN`** unless/until a verified Hyperliquid-native archive is provided and gated steps pass. **Never fabricate data and never relabel OKX artifacts as Hyperliquid evidence.**
> 5. **Phase I/J4 — final evidence refresh:** re-run full suite and `scripts/session_gate.py`; record exact commands, observed test counts, new artifact paths + sha256, conclusions from G+/J1/J2/J3, and the next highest-value bottleneck. Re-date this header. Only mark done at **6/6**.
>
> **Anti-avoidance rules:** do not stop after reading, planning, or a narrative summary. Do not re-acquire OKX data, re-run the canonical campaign, redo J1, or redo G+ without cause. Do not claim Hyperliquid parity from OKX data. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. A failed/absent prior sweep is a bottleneck to clear by executing J2 now, not a reason to defer.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T15:25:31Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `e474127` (`chore(kilo): checkpoint agent session`), branch `main`; working tree clean. | `git log -1 --oneline`, `git status --short` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | repo root |
| Environment | `/tmp/venv_h` **missing**; `/tmp/crs-venv` **missing**; system `python3` 3.12.3 available. Bootstrap via `scripts/bootstrap_env.sh` (deps in `requirements-test.txt`: pytest, numpy, pandas, requests, pyarrow). | `test -x`, `/tmp` listing |
| Done-gate | Not executed this pass (no venv). Expected blocker: `phase_j2_sensitivity_sweep` missing (`research_state/sensitivity_sweep_real_okx_full.*` and `research_state/sweep_runs/` absent). | filesystem check, `scripts/session_gate.py` logic |
| Prior sweep status | Referenced background sweep/process/log **not present**; no aggregate/per-run J2 artifacts on disk. | `ps`, filesystem |
| Phase G+ | **Done (artifacts present).** | `research_state/real_okx_full_spec_comparison.{md,summary.json}` |
| Phase J1 | **Done (artifacts present).** | `research_state/crash_event_census_real_okx_full.{json,md}` |
| Phase J3 | **Runbook present & gate-shaped** (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, tokens `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, `NOT_RUN`); Hyperliquid-native campaign **NOT_RUN** (data unavailable). | `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` |
| Phase H | Full-suite pass/counts and reproducibility-contract evidence **not re-recorded in this pass** (must be completed/evidenced). | — |

## 1. Previously resolved bottlenecks (do not re-litigate)

- Phase G+ spec-vs-actual comparison completed; Phase J1 crash-event census completed (342→8, 0 unexplained). See §3 and prior handoff history.
- Canonical campaign/gap/provenance integrity and prior script fixes remain in place.
- Prior session work (per committed state/history): J3 runbook made executable/gate-compliant; Phase H reproducibility contract added/verified against canonical in that session context; J2 sweep script `capital`-passing issue fixed. **However, J2 aggregate outputs are not present in this environment now** — treat J2 as the active heavy bottleneck to close.

## 2. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run/overwrite)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`, sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554` (per prior verified record; re-hash before reporting if you cite).
- Universe: `research_state/universe_okx_full_verified.json` — 54 symbols, `min_24h_volume_usd=5,000,000`, sha256 `14c8066ecb879fa24ecb33c30ec3bf8da40ad3fda4a7e4c270ffe83b07ea72fb`.

**Campaign (do not overwrite):**
- `research_state/campaign_results_real_okx_full.json` — `run_type=real_market_campaign`, `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`, `results.num_trades=8`, `results.total_pnl=9159.691934882958`. sha256 `57973b0c4a0d68c783cd4dffd1c6817d20ad4613bee6e2e28939f9b497d2f9b8`.
- `research_state/campaign_results_real_okx_full_metrics.json` — sha256 `3f95d30e4b557912baeca449514c447fbdd4c253f45be4b6f085c1a826f2867c`.

**Phase G+:** `real_okx_full_spec_comparison.md` sha256 `fb0da9dddeac53177d1a5f946f0eb38f37a2a38fdf3072802da360cb10dd951b`; `real_okx_full_spec_comparison_summary.json` sha256 `58752ccf35214e53291bae2d9ff7d6cb2130cb220f21016d21794012dffef452`.

**Headline metrics (actual, from artifacts):** equity 100,000→109,159.69; net PnL 8,141.29; return **+9.1597% total / +22.5995% annualized** over **0.4301 yr** (last exit `2026-05-20T10:00:00Z`); worst DD −2.0275%; 8 trades (4W/4L), 5 traded symbols of 54. **Caveats:** active ~151-day horizon; real OKX cross-venue, **NOT Hyperliquid performance evidence**.

## 3. Phase J1 — Crash-event census (COMPLETE, do not redo)

- `research_state/crash_event_census_real_okx_full.json` — sha256 `46ba710ec83a17e45e4fe8bbfc3436353f7ace0cd6a1e942e1d7c3b464779bec`
- `research_state/crash_event_census_real_okx_full.md` — sha256 `cbcd74bd58ae0b55317d5716456841cdcb0f167e1ba756bf389be6d30acee5b9`
- Reconciliation (0 unexplained): **342** → vol pass **187** → bounce **39** → regime **89** → signal **11** → trades **8**.

## 4. Remaining work — definition of done (all required)

- **Phase H:** full suite green with recorded counts; reproducibility-contract test passes against canonical `campaign_results_real_okx_full` (distinct-prefix rerun, temp outputs deleted); gate integrity (`volume_filter_ok` all-bars + per-trade trailing-24h ≥$5M) confirmed.
- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md` with **17 executed runs** (baseline + 16 one-factor-at-a-time variants) including per-run params/metrics/runtime; per-run files under `research_state/sweep_runs/`; canonical untouched; evidence-backed conclusions on which knobs move results and which do not.
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook maintained (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, required tokens present); `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/J3 outcomes, next highest-value bottleneck. `scripts/session_gate.py` **6/6**.

## 5. Canonical commands

- Bootstrap: `bash scripts/bootstrap_env.sh` (default `/tmp/crs-venv`)
- Done-gate: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` (or equivalent venv)
- Tests: `PYTHONPATH=. /tmp/crs-venv/bin/python -m pytest -q -rs`
- Phase H repro (distinct prefix, delete after): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Phase J2 sweep (parallel, required): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/generate_candle_coverage_gap_report.py`

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No "done" without Phase H reproducibility-contract test passing + full suite recorded, Phase J2 artifacts complete/analyzed, Phase J3 executable runbook maintained, and a refreshed evidence-backed handoff at **6/6** on `scripts/session_gate.py`.

**This file is the durable handoff.** Next agent: bootstrap env, run the done-gate, execute Phase H evidence, run/complete the heavy Phase J2 sensitivity sweep (primary bottleneck), verify/maintain Phase J3 runbook status, then complete Phase I/J4 with recorded evidence and leave this handoff re-dated at 6/6.
