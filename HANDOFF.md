# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-16T00:03:00Z — **C14 CAMPAIGN ACTIVE (MANDATORY HEAVY WORK)**. The prior "closed state / do nothing substantive" directive is **REMOVED** as an efficiency bottleneck. C1–C13 remain COMPLETE and their final verdict `NO_GO` is preserved as a prior, but the program is **NOT closed**: the decision-grade question is still open because effective crash-episode N is structurally too small (10 episodes). The next session's binding mission is **C14 — Broad-Universe Native Power Escalation** (section below). A session that only reads this file, reruns gates, or re-litigates C1–C13 has **not** done the work.
**Supersedes:** all earlier handoffs, including the 2026-11-15T20:55:41Z "closed state" handoff. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify the edge on **Hyperliquid-native** evidence with honest dependence-aware inference. **This priority is NOT satisfied.** C1–C13 produced only `NO_GO` / `UNDERPOWERED` because the 283-day, 5-symbol native window yields too few independent crash episodes. **The open bottleneck is sample size, not analysis effort.** C14 exists to remove it.

**Verdict state (priors — do not relitigate, do reference):**
- **FINAL CONSOLIDATED (C1–C13):** **`NO_GO`** — `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`.
- Cross-venue consolidated (C10-final): **`NO_GO`** (0/7, `is_hyperliquid_venue_data=false`) — `research_state/decision_verdict_consolidated_20261115T122636Z.md`.
- Native canonical (C11.3): **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** — `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`.
- Native C12: **`NO_DECISION_GRADE_GO`** (discovery only) — `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`.
- Native C13 (pre-registered validation, 200/200 draws, seed 20261115): **`UNDERPOWERED`** — `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md` (bootstrap CI95 [−22,799.52, +79,978.91] spans 0; permutation p=0.085; placebo p=0.32; spot leg −3,968.80).

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-16T00:03:00Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`).** Read this section as your **initial task message**. It is a heavy-work order, not a status note. Your session is **not complete** until the C14 acceptance contract below is satisfied (or a documented hard blocker is recorded per §"Acceptance contract").

**You must not:** claim GO; relabel cross-venue (`is_hyperliquid_venue_data=false`) as Hyperliquid; fabricate or synthesize candles/archives/results; relax the spec $5M trailing-24h volume gate or spec-literal defaults; edit canonical C1–C13 artifacts; do a handoff-only/gate-only commit; or stop at "closed, no actionable work".

### Primary mission: C14 — Broad-Universe Native Power Escalation
**Objective:** Raise effective independent crash-episode N from the C13 level (10 episodes / 5 symbols / 283 days) to the pre-registered decision floor by acquiring the **widest available real Hyperliquid-native Ironflow archive** (all perps, longest window), then run the **full dependence-aware validation battery** and issue a new decision-grade verdict. Two legitimate terminal states only: **(A)** pre-registered GO criteria met, or **(B)** full execution + a quantified `UNDERPOWERED`/`NO_GO` verdict with a power curve showing the exact episode count needed and the maximum feasible from available data.

**Why this is the right work:** the binding decision memo requires **≥10 independent crash episodes with episode-block bootstrap 95% CI excluding 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05**. C13 reached only 10 episodes / 5 symbols and failed all three. Power analysis (`research_state/power_target_hyperliquid_20261114T172700Z.md`) shows the 5-symbol set cannot plausibly deliver the floor; the only lever that is both real and spec-compliant is **more native symbols and a longer native window**, not more re-analysis of the same 5 series.

### Bottlenecks REMOVED this session (binding context)
1. **"Closed state / no idle churn" — REMOVED.** The previous handoff told agents to "do nothing substantive". That instruction is void. The program is open pending C14.
2. **"External Hyperliquid API 1h retention blocks acquisition" — BYPASSED.** Live `candleSnapshot` retention is a non-issue for C14 because the **Ironflow HF archive** (`ironflow/hyperliquid-candles-1h`, CC BY 4.0, node-derived) is the accepted full-window native source. Network reachability was re-verified at 2026-11-15T21:43Z (`https://huggingface.co` → HTTP 200). Acquisition is therefore **not blocked**; failing to attempt it is non-compliance.
3. **"Only 5 symbols exist" — FALSE as a permanent constraint.** The 5-symbol archive was a narrow user-supplied slice, not the dataset's full universe. The live probe already sees 32 perps passing the $5M gate (`research_state/hyperliquid_retention_probe.json`, generated 2026-11-15T21:42:44Z: `perps_total 235`, `perps_passing_volume_gate 32`). C14-T1 must pull the full available universe, not the 5-symbol slice.

### C14 execution steps (all mandatory; use `PYTHONPATH=. /tmp/crs-venv/bin/python`, bootstrap with `bash scripts/bootstrap_env.sh` if `/tmp/crs-venv` is missing)
Use a single run-stamp `TS` (UTC `YYYYMMDDTHHMMSSZ`) for every C14 artifact stem so results are traceable.

**C14-T1 — Acquire the widest real native archive (heavy I/O).**
- Obtain the full Ironflow `ironflow/hyperliquid-candles-1h` perp universe (all symbols, longest available window; target ≥ 24 symbols and, if available, > 283 days) into `research_state/archives/hyperliquid_ironflow_wide_<TS>/`.
- Write `SOURCE.md` recording: dataset id/revision, download UTC, per-symbol row counts, first/last timestamp, sha256 of each file, and an explicit non-synthetic attestation. **Real market data only; no synthetic candles.**
- Reuse `scripts/fetch_hyperliquid_candles.py --source archive --input-archive <dir> --cache-dir research_state/cache/hyperliquid_ironflow_wide_<TS>` (or `--input-archives` for multi-file merges) to produce `provenance.json`.
- Acceptance evidence: archive dir exists, `SOURCE.md` present, `provenance.json` generated, `real_market_data_intended=true`, `fabricated_data=false`.

**C14-T2 — Validate intake (hard gate).**
- `scripts/validate_hyperliquid_archive_intake.py --archive research_state/archives/hyperliquid_ironflow_wide_<TS> --start 2025-12-20T00:00:00Z --end 2026-09-28T23:00:00Z --min-symbols 24` (extend `--start`/`--end` to the true archive bounds if wider).
- Must print **`ACCEPT_AS_EVIDENCE_CANDIDATE`** and record the stem. If it does not, stop and record the failure artifact — do **not** proceed on unverified data.

**C14-T3 — Derive the verified spec-compliant universe.**
- `scripts/derive_verified_universe.py --manifest research_state/cache/hyperliquid_ironflow_wide_<TS>/provenance.json --min-24h-volume-usd 5000000 --require-complete-manifest --min-symbols 24 --output research_state/universe_hyperliquid_ironflow_wide_<TS>.json`.
- Record `selected_count` and per-symbol coverage. **Do not lower the $5M gate** to inflate N.

**C14-T4 — Crash census + spec-literal funnel.**
- `scripts/build_crash_event_census.py --manifest research_state/cache/hyperliquid_ironflow_wide_<TS>/provenance.json --cache-dir research_state/cache/hyperliquid_ironflow_wide_<TS> --universe-file research_state/universe_hyperliquid_ironflow_wide_<TS>.json --output-prefix crash_event_census_hyperliquid_ironflow_wide_<TS> --rsi-period 21 --rsi-threshold 20 --min-daily-volume-usd 5000000`.
- Record: RSI(21)<20 events, volume-pass, confirmed signals, trades, episodes, distinct crash days, symbols.

**C14-T5 — Episode edge, placebo, permutation (heavy compute; 20k/2k draws).**
- `scripts/run_episode_edge_okx_multiyear.py --draws 20000 --seed 20261116 --cache-dir research_state/cache/hyperliquid_ironflow_wide_<TS> --universe research_state/universe_hyperliquid_ironflow_wide_<TS>.json --census <census stem>.json --venue-label Hyperliquid --out episode_edge_hyperliquid_ironflow_wide_<TS>`.
- `scripts/run_portfolio_placebo_okx_multiyear.py --draws 2000 --seed 20261116 --out placebo_portfolio_hyperliquid_ironflow_wide_<TS>` (point it at the same cache/universe/campaign via module constants or a thin wrapper if flags are absent).
- Required outputs: episode-block bootstrap 95% CI, `P(total>0)`, crash-day permutation p, full-portfolio placebo p, and **leg separation (spot / ETH hedge / rebound short)**.

**C14-T6 — Pre-register, then issue a new verdict.**
- Create `scripts/build_c14_prereg.py` by adapting `scripts/build_c13_prereg.py`; **SHA-bind** it to the C14 universe/census/campaign stems and set a fixed seed (20261116). Thresholds must be frozen **before** looking at results: GO iff (bootstrap 95% CI excludes 0) AND (permutation p<0.05) AND (placebo p<0.05) AND (spot leg > 0).
- Write `research_state/decision_verdict_hyperliquid_native_c14_<TS>.{md,json}` referencing **all** priors (C11.3, C12, C13, consolidated FINAL) plus C14 artifacts. Verdict token must be exactly one of `GO`, `UNDERPOWERED`, `NO_GO`. If not GO, include a **power curve**: episodes required for CI exclusion at observed variance, and the maximum episodes achievable from the C14 archive.

**C14-T7 — Acceptance gate (create it; it is the done-marker).**
- Create `scripts/verify_c14_focus_campaign.py` that fails unless **all** hold: C14-T1..T6 artifacts exist and are SHA-consistent; provenance is `is_hyperliquid_venue_data=true` and non-synthetic; the verdict stem references all priors; the power curve is present; and `selected_count >= 24`. It must print **`C14 ACCEPTANCE: PASS`**.
- Your session is done only when this prints `C14 ACCEPTANCE: PASS` (terminal state A or B), or when §"Acceptance contract" blocker conditions are met.

### Acceptance contract (machine-checkable done-marker)
A C14 session is **complete** iff one of:
- **(A) GO path:** `C14 ACCEPTANCE: PASS` and verdict token `GO` with all pre-registered criteria met; or
- **(B) Quantified power wall:** `C14 ACCEPTANCE: PASS`, verdict `UNDERPOWERED` or `NO_GO`, full C14 battery executed on the widest available native universe, and a power curve + explicit data request for the additional episodes/windows required; or
- **(C) Hard blocker (only if genuine and evidenced):** Ironflow is unreachable **and** no alternate verified native archive exists **and** no cached wide archive is present. Then write a blocker artifact with the failed command output, the HTTP/DNS evidence, and an updated data request — **not** a bare "closed/no work". Bare handoff/gate edits never satisfy this contract.

### Readiness + gates (run; record outputs/stems)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # expect 21/21 checks passed
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem; retention block is expected)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS (prior; keep green)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py    # C14 ACCEPTANCE: PASS (new; required to finish)
```
Provenance (binding): Hyperliquid-native evidence is **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true` only for native artifacts. Cross-venue OKX/Binance are `is_hyperliquid_venue_data=false`.

### Definition of done (this session)
`C14 ACCEPTANCE: PASS` from `scripts/verify_c14_focus_campaign.py`, a new C14 verdict stem, this handoff updated (single durable), canonical C1–C13 artifacts untouched, and all prior gates still green (`session_gate.py` **21/21 checks passed**, `verify_campaign_evidence.py` 4/4, `verify_next_focus_campaign.py` PASS, `verify_c13_focus_campaign.py` PASS, `probe_hyperliquid_blocker.py` expected-blocked).

---

## Gate-token contract (DO NOT remove — machine-checked)

This file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `verify_c13_focus_campaign.py` (C13 acceptance gate)
- `verify_c14_focus_campaign.py` (C14 acceptance gate)
- `C13` (C13 campaign token) and `C14` (C14 campaign token)
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## What changed this session (2026-11-16T00:03Z)

- **Bottleneck removal:** deleted the "closed state / do nothing substantive / no idle churn" directive from the prior handoff; it was the reason sessions were unproductive.
- **C14 campaign authored:** mandatory broad-universe native power escalation (C14-T1..T7) with exact scripts, acceptance contract, and anti-avoidance rules.
- **Provenance correction recorded:** the 5-symbol archive is a slice, not the dataset's full universe; live probe sees 32 perps passing the $5M gate; HuggingFace reachable (HTTP 200, 2026-11-15T21:43Z) so acquisition is not blocked.
- **Priors preserved:** C1–C13 and consolidated `NO_GO` retained as priors; not re-run, not relabeled.

## Verified state (as of 2026-11-16T00:03:00Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | venv present |
| Session gate | **21/21 checks passed** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C13 acceptance gate | **PASS** | `scripts/verify_c13_focus_campaign.py` |
| C14 acceptance gate | **NOT_RUN — this session's job** | `scripts/verify_c14_focus_campaign.py` (to create) |
| **Final consolidated verdict (prior)** | **`NO_GO`** | `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` (+ `.json`) |
| Native universe (prior, narrow) | 5 symbols / 283d / 10 episodes | `universe_hyperliquid_ironflow_native_20251220_20260928.json` |
| Live universe probe | 235 perps, 32 pass $5M gate | `research_state/hyperliquid_retention_probe.json` (2026-11-15T21:42:44Z) |
| HF reachability | HTTP 200 | `https://huggingface.co` @ 2026-11-15T21:43Z |

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- **Prior final:** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`, `.json`.
- Cross-venue/canonical: `campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**.
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, C11.3 census/episode/placebo/robustness/verdict stems, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- **C12:** prereg/campaign/census/inference/verdict stems under `research_state/` (incl. `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`).
- **C13:** prereg/episode-edge/placebo/verdict stems (20261115T185721Z, 20261115T200200Z, 20261115T200309Z, 20261115T203734Z).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Hard prohibitions

- **No GO claim** without C14 pre-registered criteria met.
- **No relabeling.** Do not relabel cross-venue (`is_hyperliquid_venue_data=false`) as Hyperliquid; do not misstate native provenance (node-derived Ironflow HF, CC BY 4.0, NOT venue `candleSnapshot`).
- **No fabrication/synthesis.** No synthetic candles/archives/results.
- **No churn / no avoidance.** No handoff-only/gate-only sessions; no re-running C1–C13; no "closed, no actionable work" stop. C14 must actually execute T1–T7.
- **No spec relaxation.** Do not relax `volume_filter_ok` / trailing-24h ≥ $5M gate or spec-literal opt-in defaults to inflate N.
- **Single durable handoff only.** Do not create a second handoff/status file.
- **Preserve gate-token contract tokens** listed above.

(End of file)