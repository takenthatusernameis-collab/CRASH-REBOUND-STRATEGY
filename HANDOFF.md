# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session

**Timestamp:** 2026-11-27T18:24:03Z (state re-derived via `bash scripts/next_c25_action.sh`: RUNNER NOT ALIVE, C25 ACCEPTANCE: UNKNOWN, .venv missing, 16 real cells remaining = cost_stress arm, cost_taker_funding bitget 2023 in flight with 6 draw chunks on disk)
**Repository:** CRASH-REBOUND-STRATEGY
**Working Directory:** /home/runner/work/CRASH-REBOUND-STRATEGY/CRASH-REBOUND-STRATEGY

> This file is the SINGLE durable handoff and the binding timestamped initial task message.
> `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers only. If anything disagrees
> with this file, this file wins. Re-derive runner/gate/progress/pacing state with
> `bash scripts/next_c25_action.sh` — never trust stale numbers copied into any file.

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

**Launch the C25 durable runner (fresh CI job, no .venv) → complete the C25 `cost_stress` arm → generate the 2 missing arm verdicts → generate the C25 consolidated verdict → C25 ACCEPTANCE: PASS → unlock C26.**

The heavy compute must be launched via the durable background process (`bash scripts/run_c25_durable.sh`, persistent). Do **NOT** start a second runner, do **NOT** kill it, do **NOT** start C26/C27. Your job is to keep the session alive on a bounded wait, re-probe, and let the durable runner finish.

### Current Campaign Status (Sequential Chain: C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32)

| Campaign | Status | Blocking Issue |
|----------|--------|----------------|
| **C24** | ✅ ACCEPTANCE: PASS | — |
| **C25** | ⚠️ **INCOMPLETE** | `cost_stress` arm (16 real cells) + `cost_taker_funding` tail (4 cells) + 4 arm verdicts + consolidated verdict |
| **C26** | 🔒 BLOCKED | Requires C25 ACCEPTANCE: PASS (consolidated verdict) |
| C27–C32 | 🔒 BLOCKED | Sequential dependency on C26 |

### C25 Completion Checklist (`verify_c25_focus_campaign.py` is the authoritative gate)

- [x] **Prereg**: `c25_prereg_20261119T045500Z.json` (status: PRE_REGISTERED_BEFORE_COMPUTE)
- [x] **C24 PASS**: `c24_decision_verdict_CONSOLIDATED_20261119T013154Z.json` exists
- [ ] **All 4 arms × 4 venues × 4 folds checkpoints**: cost_base 16/16, cost_taker 16/16, cost_taker_funding 12/16 (bitget 2023 in flight), **cost_stress 0/16** (okx 4 = UNAVAILABLE_FUNDING skip)
- [x] **No signal-path/cost drift**: frozen config validated
- [x] **Cost anchor (cost_base vs C24 d15)**: COST_ANCHOR_REPRODUCED (ANCHOR OK)
- [x] **Inference floors (20k/20k/2k/2k)**: met for completed arms
- [x] **No SMOKE artifacts**
- [ ] **All 4 arm verdicts exist**: missing `cost_base`, `cost_taker`, `cost_taker_funding`, `cost_stress`
- [ ] **Consolidated verdict exists**: missing `c25_decision_verdict_CONSOLIDATED_20261119T045500Z.json`

---

## 🚀 EXECUTION COMMANDS (the probe already picks the right one — do not improvise)

### If probe says `ACTION: RESUME_C25` (runner dead / fresh CI job, no .venv) — **CURRENT STATE**

```bash
background_process start command="bash scripts/run_c25_durable.sh" persistent=true
bash scripts/status_c25.sh
```

`run_c25_durable.sh` bootstraps `.venv` if missing and refuses to start a duplicate runner.

### After launch — bounded wait + re-probe (the only valid action while runner alive)

```bash
bash scripts/check_c25_anchor.sh
bash -c 'sleep 540; bash scripts/next_c25_action.sh'   # 540s < 900s idle-timeout
```

Repeat until the probe flips to `PROBE_AND_LAUNCH_C27` (C25+C26 PASS) or `FIX_*_INTEGRITY`.

### If probe says `ACTION: PROBE_AND_LAUNCH_C27` (C25 + C26 both PASS)

```bash
PYTHONPATH=. .venv/bin/python scripts/probe_c27_venue_acquisition.py
# confirm research_state/c27_prereg_20261119T215721Z.{json,md} matches the probe verdict
# then launch C27 per the C27 section of scripts/run_c27_durable.sh
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
| `scripts/run_c25_cost_fidelity_campaign.py` | C25 runner (4 arms, frozen signal, liquidation=15%) |
| `scripts/verify_c25_focus_campaign.py` | C25 acceptance gate (authoritative PASS/PENDING/FAIL) |
| `scripts/run_c26_path_fidelity_campaign.py` | C26 runner (intrabar + per-trade funding fidelity) |
| `research_state/c25_prereg_20261119T045500Z.json` | C25 pre-registration (immutable) |
| `src/strategy/crash_rebound.py` | Core strategy (RSI<20 crash, +9% target, ETH hedge) |
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

- `.venv` does **not** exist (fresh CI job). `run_c25_durable.sh` bootstraps it on launch.
- Use `background_process` with `persistent=true` for the durable runner so it survives session/turn boundaries.
- Checkpoint files in `research_state/` enable exact resume after environment loss; intra-cell draw chunks (`c25_draw_ckpts/`) resume bit-identically (~5 min max loss).
- All timestamps UTC. C25 `TS=20261119T045500Z`, C26 `TS=20261119T121500Z`.
- C24 d15 reference: `c24_decision_verdict_d15_20261119T013154Z.json` (venue_totals for cost_base anchor).
- **Current runner state (18:24Z):** NOT ALIVE, `.venv` missing, 6 draw chunks on disk for `cost_taker_funding bitget 2023`, 16 real cells remaining (all cost_stress; okx cost_stress = UNAVAILABLE_FUNDING skip), pacing: ~1.6 h/cell on 4 saturated cores, wake_after=8h.

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

---

**This handoff is the single source of truth for the next session. Do not substitute lighter work,
parameter searches, or "no authorized work" declarations. Run `next_c25_action.sh` first and obey its
ACTION line. The only valid heavy action is launching the durable runner via `RESUME_C25`; then keep
it alive with bounded waits + re-probes until the gate flips.**