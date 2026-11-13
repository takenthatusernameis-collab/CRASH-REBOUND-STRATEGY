# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-13T12:46:12Z
**Supersedes:** 2026-11-13T11:47:38Z (and all earlier).
**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch:** `main` @ `e474127` (`origin/main` at `e474127` observed earlier in this session context may differ; HEAD is `e474127` now). Working tree has in-progress session edits: modified `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`, modified `scripts/run_sensitivity_sweep.py`, untracked `tests/test_reproducibility_contract_real_okx_full_20261113.py`. Do **not** `git reset`/`checkout` anything away. Nothing needs committing unless explicitly requested.
**Single durable handoff:** this file only. Do not create a second handoff/status file.

> ## READ FIRST — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-13T12:46:12Z)
>
> **Priority (inferred from repo name `CRASH-REBOUND-STRATEGY`):** deliver decision-grade, evidence-backed crash-rebound strategy research/backtest conclusions from real artifacts on disk, then close the remaining campaign phases. **This is not a quick-summary task; heavy execution is required and cannot be skipped.**
>
> **Start-of-session done-gate (run first, record result):**
> `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py`
> Current expected state at this handoff: **5/6 PASS**. The only failing check is **Phase J2 sensitivity sweep** artifacts (`research_state/sensitivity_sweep_real_okx_full.json` + `.md` missing). Phase H reproducibility-contract test is present and syntactically/collection-valid; Phase J3 executable Hyperliquid-native runbook is present and satisfies gate tokens. **Do not stop until this command prints 6/6 PASS, Phase H is fully evidenced (full suite green with recorded counts + reproducibility contract passing), J2 artifacts are complete and analyzed, and this handoff is re-dated with evidence.**
>
> **Current state (verified 2026-11-13T12:46:12Z):**
> - Git HEAD: `e474127`.
> - Done-gate: `scripts/session_gate.py` → **5/6 PASS** (fails only `phase_j2_sensitivity_sweep: json and/or md missing`).
> - Phase G+ spec-vs-actual: **done** (`research_state/real_okx_full_spec_comparison.{md,summary.json}`).
> - Phase J1 crash-event census: **done** (`research_state/crash_event_census_real_okx_full.{json,md}`).
> - Phase H progress (this session): added `tests/test_reproducibility_contract_real_okx_full_20261113.py` (sha256 `764a513c552731e0e9d230c4ba89f06f4595542da0e5eefd823e13e4c1dbd505`), collected OK (`1 test collected`). A manual reproducibility run to a distinct prefix (`reproducibility_check_real_okx_full`) completed successfully (`REAL run complete: 8 trades, total_pnl=9159.691934882958`) and verified `results.trades` and `results.total_pnl` match canonical (`campaign_results_real_okx_full.json`) modulo top-level `timestamp`; temporary repro artifacts were deleted; canonical hashes unchanged. **Full-suite pytest has NOT been re-run this session** — required for Phase H completion.
> - Phase J2 (IN PROGRESS, heavy): `scripts/run_sensitivity_sweep.py` fixed (sha256 `f520178b51506b7972d6f4fd7eedca738087334391ba2b8b0d1efacbb8f16173`) to pass `capital` into worker jobs/state (previous attempt rejected all runs with `KeyError 'capital'`; stale `research_state/sweep_runs/*.json` from that failed attempt removed). Relaunched in background process `bgp_1d4e41769001y36sfhugzewAxv` (pid 34033, started ~12:31Z): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`. At 12:46Z: 4 worker processes active/high CPU, log shows `[sweep] 17 runs, workers=4`, **0 per-run files in `research_state/sweep_runs/` and no aggregate artifacts yet** (runs are still executing; per-run JSONs/aggregate are written on completion/progress per script behavior — confirm actual state on resume). Budget: serial equivalent ~2.7h; with 4 workers expect materially less wall time. **Do not kill/restart unless failed; do not run serially.**
> - Phase J3: `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` rewritten (sha256 `6f085846b25372c6aafe8b61e4e384e1ace317ce9fae00f3d3a4556626177ae0`) with exact section `HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, includes `fetch_hyperliquid_candles.py`, `run_real_campaign.py`, and `NOT_RUN` tokens, stepwise commands/pass-fail/artifacts; status remains **NOT_RUN** (verified Hyperliquid-native full-window data unavailable). Gate check for J3 now passes.
> - Canonical real-OKX manifest/universe/campaign/metrics hashes unchanged (see §2). No canonical artifacts overwritten.
> - Env: `/tmp/venv_h` ready (pytest 9.2.0 + numpy/pandas/requests/pyarrow); 4 CPU / 15 GiB RAM. No stray temp dirs noted this update.
>
> **Mandatory remaining work — execute in order, do not stop early:**
> 1. **Phase H — complete & evidence:** ensure `tests/test_reproducibility_contract_real_okx_full_20261113.py` passes, re-run the full suite and record observed counts (`PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs`), and confirm `volume_filter_ok` (all-bars) and per-trade point-in-time trailing-24h ≥$5M gates remain intact. Do not overwrite canonical artifacts; delete only your own rerun files.
> 2. **Phase J2 — finish heavy sensitivity campaign (REQUIRED, in progress):** let the running sweep complete (or, if `bgp_1d4e41769001y36sfhugzewAxv`/PIDs are dead/failed on resume, restart with the exact command above using `--workers 4` to a fresh/consistent state). It must produce **17 runs** (baseline + 16 variants) in `research_state/sensitivity_sweep_real_okx_full.json` + `.md`, with per-run params/metrics/runtime, plus per-run files under `research_state/sweep_runs/`. Never overwrite canonical artifacts. State which knobs move results and which do not; no fabricated numbers.
> 3. **Phase J3 — verify/maintain executable Hyperliquid-native runbook (REQUIRED):** `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` already contains `HYPERLIQUID NATIVE ACQUISITION RUNBOOK` with required tokens; keep it accurate. If data remains unavailable, campaign remains `NOT_RUN`; **never fabricate or relabel OKX as Hyperliquid**.
> 4. **Phase I/J4 — final evidence refresh:** re-run the full suite and `scripts/session_gate.py`; record exact commands, observed test counts, new artifact paths + sha256, conclusions from G+/J1/J2/J3, and the next highest-value bottleneck. Re-date this header. Only mark done at **6/6**.
>
> **Bottlenecks addressed this session:** rewrote J3 runbook to satisfy gate; added Phase H reproducibility-contract test and manually verified reproducibility (trades/total_pnl match, temp outputs removed); fixed `scripts/run_sensitivity_sweep.py` capital-passing bug that blocked J2 and relaunched the heavy 4-worker sweep (now running). **Remaining blockers:** J2 aggregate artifacts not yet produced (sweep still running), full-suite green/counts not yet re-recorded in this session, final handoff/gate 6/6 refresh pending.
>
> **Anti-avoidance rules:** do not stop after reading, planning, or a narrative summary. Do not re-acquire OKX data, re-run the canonical campaign, redo J1, or redo G+ without cause. Do not claim Hyperliquid parity from OKX data. Do not relax the $5M volume gate. Do not overwrite canonical artifacts. Do not kill the running sweep just to “check”; monitor and wait for completion, or resume/restart only if actually failed. Do not mark done while `scripts/session_gate.py` is not 6/6.
>
> **Non-negotiables:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; **NOT Hyperliquid performance evidence**. Every conclusion must carry that caveat.

---

## 0. Verified state (2026-11-13T12:46:12Z)

| Check | Result | Evidence |
|---|---|---|
| Git | HEAD `e474127`; modified `DATA_REQUEST_283D_HYPERLIQUID.md`, `scripts/run_sensitivity_sweep.py`; untracked reproducibility-contract test. | `git status -sb`, `git log -1` |
| Durable handoff | Single file: `./HANDOFF.md` (this file). | `find . -name '*HANDOFF*'` |
| Done-gate | **5/6 PASS** (only J2 fails). | `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py` |
| Canonical artifacts | Hashes re-verified unchanged in-session (not re-listed fully here beyond prior record; no overwrites). | prior §2/§3 + no canonical writes |
| Phase G+ | **Done.** | `research_state/real_okx_full_spec_comparison.*` present |
| Phase J1 | **Done.** | `research_state/crash_event_census_real_okx_full.*` present |
| Phase H reproducibility-contract test | **Present/collectable** (`tests/test_reproducibility_contract_real_okx_full_20261113.py`, 1 collected). Manual repro run matched `results.trades`/`results.total_pnl` to canonical; temp outputs deleted. **Full suite not re-run this session.** | pytest collect + manual run |
| Phase J2 outputs | **In progress / missing aggregates** (running `bgp_1d4e41769001y36sfhugzewAxv`, workers active, 0 files in `sweep_runs/`, no `sensitivity_sweep_real_okx_full.*` yet at 12:46Z). | log/ps/fs snapshot |
| Phase J3 runbook | **Present & gate-passing** (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, tokens present); campaign `NOT_RUN`. | `DATA_REQUEST_283D_HYPERLIQUID.md` |
| Env | `/tmp/venv_h` ready; 4 CPU / 15 GiB RAM. | fs/process checks |

## 1. Previously resolved bottlenecks (do not re-litigate)

- Phase G+ comparison completed; J1 census completed (342→8, 0 unexplained). See prior handoff sections for details/evidence.
- Canonical campaign/gap/provenance integrity and prior script fixes remain in place.
- **This session:** J3 runbook made executable/gate-compliant; Phase H reproducibility contract added and manually verified against canonical; J2 sweep script `KeyError 'capital'` fixed and sweep relaunched with 4 workers.

## 2. Canonical real OKX artifacts (verified, non-synthetic; do not re-acquire/re-run/overwrite)

**Data/provenance:**
- Archive: `research_state/archives/okx_1h_full_20251220_20260928/` (64 entries), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol, `gap_count=0`.
- Manifest/provenance: `research_state/cache/okx_1h_full_20251220_20260928/provenance.json` — `all_complete=true`, `ready_for_real_campaign=true`, sha256 `53ad860b7d9787d3763f23e48070067899f6363b96ab48a61b05b970a675a554`.
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

- **Phase H:** full suite green with recorded counts; reproducibility-contract test passes; gate integrity (`volume_filter_ok` all-bars + per-trade trailing-24h ≥$5M) confirmed.
- **Phase J2:** `sensitivity_sweep_real_okx_full.json` + `.md`, 17 runs (baseline + 16 one-factor-at-a-time variants) with per-run params/metrics/runtime, per-run files under `research_state/sweep_runs/`, canonical untouched, evidence-backed conclusions (which knobs move results and which do not).
- **Phase J3:** executable Hyperliquid-native acquisition/verification runbook maintained (`HYPERLIQUID NATIVE ACQUISITION RUNBOOK`, required tokens present); `NOT_RUN` if unavailable, never fabricated/relabeled.
- **Phase I/J4:** this handoff updated with commands, observed test counts, new artifact paths+sha256, conclusions, J2/J3 outcomes, next highest-value bottleneck. `scripts/session_gate.py` **6/6**.

## 5. Canonical commands

- Done-gate: `PYTHONPATH=. /tmp/venv_h/bin/python scripts/session_gate.py`
- Bootstrap: `bash scripts/bootstrap_env.sh` (or use `/tmp/venv_h`).
- Tests: `PYTHONPATH=. /tmp/venv_h/bin/python -m pytest -q -rs`
- Phase H repro (distinct prefix, delete after): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_real_campaign.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --output-prefix reproducibility_check_real_okx_full --apply-vault-fees`
- Phase J2 sweep (4 workers, do not run serially): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/run_sensitivity_sweep.py --manifest research_state/cache/okx_1h_full_20251220_20260928/provenance.json --cache-dir research_state/cache/okx_1h_full_20251220_20260928 --universe-file research_state/universe_okx_full_verified.json --workers 4 --output-prefix sensitivity_sweep_real_okx_full`
- Canonical gap report (fail-closed by design): `PYTHONPATH=. /tmp/venv_h/bin/python scripts/generate_candle_coverage_gap_report.py`

## 6. Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX/partial runs as Hyperliquid evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition or reruns of canonical campaign/J1/G+; no Hyperliquid parity claims from OKX.
- No overwriting canonical artifacts; reruns to new stems only.
- No "done" without Phase H reproducibility-contract test passing + full suite recorded, Phase J2 artifacts, Phase J3 executable runbook maintained, and a refreshed evidence-backed handoff at **6/6** on `scripts/session_gate.py`.

**This file is the durable handoff.** Next agent: run the done-gate, check J2 background process/artifacts (`bgp_1d4e41769001y36sfhugzewAxv` / `research_state/sweep_runs/` / `sensitivity_sweep_real_okx_full.*`) and let it finish or restart if truly failed, then complete Phase H → J2 → J3 verification → I/J4 with evidence and leave updated artifacts + this handoff re-dated.
