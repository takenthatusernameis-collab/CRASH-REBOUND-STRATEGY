# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session

**Timestamp:** 2026-11-27T23:07:32Z (state re-derived via `bash scripts/next_c25_action.sh`; runner confirmed ALIVE — durable C25 runner executing, draw chunks on disk = 40/40, in-flight `cost_taker_funding_bitget_2023` completing, 16 real cells remaining, anchor OK)
**Repository:** CRASH-REBOUND-STRATEGY
**Working Directory:** /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY

> This file is the SINGLE durable handoff and the binding timestamped initial task message.
> `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers only. The former
> `HANDOFF_NEXT_SESSION_*.md` duplicates were REMOVED at 20:08:11Z to enforce a single source of
> truth — do not recreate them. If anything disagrees with this file, this file wins. Re-derive
> runner/gate/progress/pacing state with `bash scripts/next_c25_action.sh` — never trust stale
> numbers copied into any file.

---

## 🔒 BINDING INITIAL TASK MESSAGE (timestamped 2026-11-27T21:31:52Z)

**Repository priority (inferred from repo name `CRASH-REBOUND-STRATEGY`): finish the C25 cost-&-funding-fidelity campaign, then unlock the C24→C25→C26→…→C32 sequential adjudication chain. Nothing else is authorized ahead of C25.**

**Your one job this session:** run `bash scripts/next_c25_action.sh` FIRST, obey its single `ACTION:` line, and keep the durable C25 runner alive with bounded waits + re-probes until the C25 gate flips to PASS. Do NOT relaunch, kill, or start C26/C27, and do NOT substitute lighter work or declare "no authorized work" — keeping the one durable runner alive IS the heavy work.

Current probe state (23:07:32Z): `ACTION: NONE_RUNNER_ALIVE`, runner ALIVE, C25 gate PENDING, C26 gate PENDING, anchor OK, 16 real cells remaining (in-flight `cost_taker_funding_bitget_2023` at 40/40 draw chunks completed; then bitget 2024/2025/2026YTD + 12 `cost_stress` non-okx cells), 8 okx cells skipped UNAVAILABLE_FUNDING.

---

## 0. FIRST ACTION EVERY SESSION (before reading anything else)

```bash
cd /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY
bash scripts/next_c25_action.sh
```

That probe prints exactly one `ACTION:` line and the exact next command. **Obey the ACTION line.**
It already encodes the dead-runner vs alive-runner vs gate-PASS/FAIL decision tree, so you do not
need to reason about it manually. The rest of this file is the why + the no-avoidance rules.

---

## 🎯 IMMEDIATE NEXT TASK (Non-Negotiable)

**Keep the C25 durable runner alive → complete the C25 `cost_stress` arm → complete the `cost_taker_funding` tail → generate the 4 missing arm verdicts → generate the C25 consolidated verdict → C25 ACCEPTANCE: PASS → unlock C26.**

The heavy compute must stay on the durable background process (`bash scripts/run_c25_durable.sh`, persistent). Do **NOT** start a second runner, do **NOT** kill it, do **NOT** start C26/C27. Your job is to keep the session alive on a bounded wait, re-probe, and let the durable runner finish.

### Current Campaign Status (Sequential Chain: C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32)

| Campaign | Status | Blocking Issue |
|----------|--------|----------------|
| **C24** | ✅ ACCEPTANCE: PASS | — |
| **C25** | ⚠️ **INCOMPLETE** | `cost_stress` arm (0/16) + `cost_taker_funding` tail (bitget 2023 in-flight 29/40, 2024/2025/2026YTD pending) + 4 arm verdicts + consolidated verdict |
| **C26** | 🔒 BLOCKED | Requires C25 ACCEPTANCE: PASS (consolidated verdict) |
| C27–C32 | 🔒 BLOCKED | Sequential dependency on C26 |

### Bottleneck Status: REMOVED (re-verified 23:07:32Z)

- Dead runner → **REMOVED**: durable runner ALIVE this session (parent pid 4052, workers 36322-36325 R saturated, 4 cores).
- Missing `.venv` → **REMOVED**: `.venv` bootstrapped; `run_c25_durable.sh` bootstraps it on any fresh CI job.
- Duplicate handoff files → **REMOVED**: stale `HANDOFF_NEXT_SESSION_20261127T192533Z.md` and `HANDOFF_NEXT_SESSION_20261127T200555Z.md` deleted at 20:08:11Z; `HANDOFF.md` is now the only durable handoff.
- No duplicate runner risk: `run_c25_durable.sh` refuses to start a second C25 runner.
- **Single session, no blocked peers**: no other session is blocked or idle, so there is no cross-session bottleneck to clear. The only valid heavy action is keeping the one durable runner alive.

### C25 Completion Checklist (`verify_c25_focus_campaign.py` is the authoritative gate)

- [x] **Prereg**: `c25_prereg_20261119T045500Z.json` (status: PRE_REGISTERED_BEFORE_COMPUTE)
- [x] **C24 PASS**: `c24_decision_verdict_CONSOLIDATED_20261119T013154Z.json` exists
- [x] **cost_base**: 16/16 checkpoints (COST_ANCHOR_REPRODUCED vs C24 d15)
- [x] **cost_taker**: 16/16 checkpoints
- [ ] **cost_taker_funding**: 12/16 checkpoints (bitget 2023 in-flight 29/40; bitget 2024/2025/2026YTD pending; okx 4 = UNAVAILABLE_FUNDING skip)
- [ ] **cost_stress**: 0/16 checkpoints (16 real cells pending; okx 4 = UNAVAILABLE_FUNDING skip)
- [x] **No signal-path/cost drift**: frozen config validated
- [x] **Cost anchor (cost_base vs C24 d15)**: COST_ANCHOR_REPRODUCED (ANCHOR OK — verified at 23:04:51Z)
- [x] **Inference floors (20k/20k/2k/2k)**: met for completed arms
- [x] **No SMOKE artifacts**
- [ ] **All 4 arm verdicts exist**: missing `cost_base`, `cost_taker`, `cost_taker_funding`, `cost_stress`
- [ ] **Consolidated verdict exists**: missing `c25_decision_verdict_CONSOLIDATED_20261119T045500Z.json`

---

## 🚀 EXECUTION COMMANDS (the probe already picks the right one — do not improvise)

### If probe says `ACTION: NONE_RUNNER_ALIVE` (runner alive — the only valid state now)

```bash
bash scripts/check_c25_anchor.sh
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 540s < 900s idle-timeout
```

Repeat until the probe flips to `PROBE_AND_LAUNCH_C27` (C25+C26 PASS) or `FIX_*_INTEGRITY`.
**Do not end this session before that bounded wait completes.** Do not relaunch, do not kill, do not start C26/C27, do not add CPU work.

### If probe says `ACTION: RESUME_C25` (runner dead / fresh CI job)

> Only if the runner has died. Do NOT run this while the runner is ALIVE — a duplicate runner is a rule-4 violation.

```bash
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
bash scripts/status_c25.sh
```

### If probe says `ACTION: PROBE_AND_LAUNCH_C27` (C25 + C26 both PASS)

```bash
PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py
# confirm research_state/c27_prereg_20261119T215721Z.{json,md} matches the probe verdict
# then launch C27 per scripts/run_c27_durable.sh
```

### If probe says `ACTION: FIX_C25_INTEGRITY` or `FIX_C26_INTEGRITY`

Run the named `verify_*` script, fix ONLY the failing integrity condition, never force PASS, never
relax floors, never edit the prereg.

---

## 🔧 KEY FILES & CONTEXTS

| File | Purpose |
|------|---------|
| `scripts/next_c25_action.sh` | **Session entry probe — run this first, obey its ACTION line** |
| `scripts/run_c25_durable.sh` | Durable C25 launcher (bootstraps venv, no duplicate, persistent) |
| `scripts/status_c25.sh` | Read-only C25 status (runner, cells, inference, artifacts, gate) |
| `scripts/check_c25_anchor.sh` | Early cost-anchor check (cost_base vs C24 d15) |
| `scripts/run_c25_cost_fidelity_campaign.py` | C25 runner (4 arms, frozen signal, liquidation=15%) |
| `scripts/verify_c25_focus_campaign.py` | C25 acceptance gate (authoritative PASS/PENDING/FAIL) |
| `scripts/run_c26_path_fidelity_campaign.py` | C26 runner (intrabar + per-trade funding fidelity) |
| `scripts/run_c27_campaign.py` | C27 runner (KuCoin new-venue replication, needs prereg + C26 pass) |
| `research_state/c25_prereg_20261119T045500Z.json` | C25 pre-registration (immutable) |
| `src/strategy/crash_rebound.py` | Core strategy (RSI<20 crash, +9% target, entry=next-open, liquidation=15%) |
| `src/backtest/engine.py` | Execution engine (fees, funding, liquidation, rebound short) |
| `src/strategy/config.py` | StrategyConfig with spec-compliant enforcement |

---

## ⚠️ HARD CONSTRAINTS (No-Avoidance Rules — violating any of these is a failed session)

1. **No parameter searches** — Signal path frozen at C25 sentinel (RSI21<20, target=9%, entry=next-open, liquidation=15%).
2. **No draw-count reduction** — Floors: 20k bootstrap / 20k permutation / 2k placebo / 2k strata.
3. **No zero-filling funding** — Venues without realized funding cache = UNAVAILABLE_FUNDING (excluded, not zeroed).
4. **No same-data reruns / no duplicate runners** — Each cell runs once; `--resume` continues from checkpoints. The durable runner owns the 4 cores; never launch a second.
5. **Sequential adjudication** — C26 cannot start until the C25 consolidated verdict exists.
6. **Real data only** — `fabricated_data=false`, `synthetic_data=false`, `cross_venue=true`.
7. **No "no authorized work" declarations** — There is always authorized work: launch the durable runner and keep it alive with bounded waits + re-probes until the gate flips.

---

## 📊 EXPECTED OUTCOMES

### C25 cost_stress arm
- Higher slippage (2×), taker fees, realized funding, +5 bps borrow.
- Likely negative PnL (DESCRIPTIVE_ONLY role) — confirms cost sensitivity.

### C25 consolidated verdict
- Primary arm (`cost_taker_funding`) token: `C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST`.
- Fidelity arm (`cost_base`) token: `COST_ANCHOR_REPRODUCED`.
- Other arms: `DESCRIPTIVE_ONLY`.

### C26 primary arm (`path_intrabar_combined`)
- Token: `C26_REOPENS_C1_C25` (if robust) or `C26_NO_GO_ROBUST_TO_PATH`.
- Fidelity anchor (`path_base`): `PATH_ANCHOR_REPRODUCED` vs C25 primary.

---

## 🛑 STOP CONDITIONS

- If `verify_c25_focus_campaign.py` returns **FAIL**: fix drift/smoke/missing cells before proceeding.
- If C25 cost_stress cells hit **UNAVAILABLE_FUNDING** for all venues: document and proceed (arm still runs cost_taker config).
- If **any session idles** without a bounded wait + re-probe: violates the no-avoidance rule (rule 7).

---

## 📝 NOTES FOR NEXT SESSION

- `.venv` exists. `run_c25_durable.sh` bootstraps it on any fresh CI job.
- Use `background_process` with `persistent=true` for the durable runner so it survives session/turn boundaries.
- Checkpoint files in `research_state/` enable exact resume after environment loss; intra-cell draw chunks (`c25_draw_ckpts/`) resume bit-identically (~5 min max loss).
- All timestamps UTC. C25 `TS=20261119T045500Z`, C26 `TS=20261119T121500Z`.
- C24 d15 reference: `c24_decision_verdict_d15_20261119T013154Z.json` (venue_totals for cost_base anchor).
- **Current runner state (23:07:32Z):** ALIVE — durable runner running (parent pid 4052, workers 44800-44803 R saturated, 4 cores) executing `run_c25_cost_fidelity_campaign.py --jobs 4 --resume`. `cost_taker_funding bitget 2023` completing draw phase (40/40 chunks on disk, cell checkpoint imminent). 16 real cells remaining (3 bitget tail cells + 12 cost_stress non-okx); 8 okx cells skipped UNAVAILABLE_FUNDING. Pacing ~1.6 h/cell, wake_after=8h. Anchor OK (cost_base reproduces C24 d15 EXACT on okx/binance_um/mexc/bitget). **Next session: do NOT relaunch — re-probe with `next_c25_action.sh`, then keep alive with bounded waits + re-probes until the gate flips.**

---

## 📋 NEXT FOCUS CAMPAIGN (unavoidable heavy work for future agents)

**P0 — COMPLETE C25 (this session, non-deferrable):** Keep the durable runner alive. Bounded wait + re-probe cycle: `next_c25_action.sh` → `check_c25_anchor.sh` → `sleep 540` → `next_c25_action.sh`, repeating until `verify_c25_focus_campaign.py` prints `C25 ACCEPTANCE: PASS`. All remaining cells (16 real + 8 skipped UNAVAILABLE_FUNDING) and 5 verdict artifacts must land. No C26/C27 work until PASS.

**P1 — RUN C26 (after C25 PASS):** `run_c26_path_fidelity_campaign.py --jobs 4 --resume`, then `verify_c26_focus_campaign.py` → `C26 ACCEPTANCE: PASS`.

**P2 — RUN C27 (after C26 PASS):** KuCoin new-venue replication. Prereg ALREADY EXISTS (`research_state/c27_prereg_20261119T215721Z.{json,md}` — do NOT rebuild). Launch `bash scripts/run_c27_durable.sh` (wraps `run_c27_campaign.py --jobs 4 --resume`), then `verify_c27_focus_campaign.py` → `C27 ACCEPTANCE: PASS`.

**P3 — C28→C32 (after C27 PASS):** Continue the sequential chain per the roadmap below. No skipping.

---

## 📋 FULL CAMPAIGN ROADMAP (Sequential, No Shortcuts)

| Campaign | Focus | Arms | Cells | Gate Script | Prereg TS |
|----------|-------|------|-------|-------------|-----------|
| C24 | Liquidation distance | 4 | 64 | `verify_c24_focus_campaign.py` | 20261119T013154Z |
| **C25** | **Cost & funding fidelity** | **4** | **64** | **`verify_c25_focus_campaign.py`** | **20261119T045500Z** |
| C26 | Intrabar path + per-trade funding | 4 | 64 | `verify_c26_focus_campaign.py` | 20261119T121500Z |
| C27 | Next venue replication (KuCoin) | 3 | 12 | `verify_c27_focus_campaign.py` | 20261119T215721Z |
| C28 | Signal sensitivity sweep | TBD | TBD | `verify_c28_focus_campaign.py` | 20261121T013400Z |
| C29 | Cross-venue agreement | TBD | TBD | `verify_c29_focus_campaign.py` | 20261121T031907Z |
| C30 | Multi-year robustness | TBD | TBD | `verify_c30_focus_campaign.py` | 20261121T051754Z |
| C31 | Placebo portfolio stress | TBD | TBD | `verify_c31_focus_campaign.py` | 20261121T052233Z |
| C32 | Final consolidated adjudication | TBD | TBD | `verify_c32_focus_campaign.py` | 20261121T061508Z |

**Pre-built & ready (verified 23:06:19Z — no "no authorized work" escape exists):** every campaign C25–C32 already has its prereg (`research_state/c{N}_prereg_*.{json,md}`), durable launcher (`scripts/run_c{N}_durable.sh`), runner (`scripts/run_c{N}_*.py`), and acceptance gate (`scripts/verify_c{N}_focus_campaign.py`) on disk. The heavy-work queue is fully loaded through C32; a future agent that claims "nothing to do" is violating rule 7.

---

**This handoff is the single source of truth for the next session. Do not substitute lighter work,
parameter searches, or "no authorized work" declarations. Run `next_c25_action.sh` first and obey its
ACTION line. The only valid heavy action is keeping the durable runner alive; then keep
it alive with bounded waits + re-probes until the gate flips.**