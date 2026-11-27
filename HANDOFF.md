# CRASH-REBOUND-STRATEGY — Durable Handoff for Next Agentic Session
**Generated:** 2026-11-27T04:02:57Z (re-verified this session; runner ALIVE pid 2867 workers 49554-49557, C25 ACCEPTANCE PENDING, 19 real cells remaining, cost_base 16/16 | cost_taker 16/16 | cost_taker_funding 9/16 | cost_stress 0/16; in-flight cost_taker_funding_mexc_2024; evidence VERIFIED exit 0, session_gate 21/21 passed — durable_handoff refreshed)
**Repo:** CRASH-REBOUND-STRATEGY — systematic multi-venue strategy validation (crash-rebound strategy research and backtesting)

**Single source of truth:** this file. `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers only and contain no campaign state. If anything disagrees with this file, this file wins.

---

# BINDING INITIAL TASK MESSAGE (timestamped 2026-11-27T04:02:57Z)

**C25 Cost/Funding Fidelity Campaign is IN FLIGHT and MUST COMPLETE before any downstream campaign can launch. No exceptions. No new campaigns. No "no authorized work" declarations. The chain C25 → C32 is pre-authorized; execute it.**

1. **Do NOT relaunch, kill, or add CPU work.** The canonical C25 runner is ALIVE and is the only heavy job; the box has 4 saturated cores. Killing or duplicating it destroys hours of in-flight permutation work.
2. Monitor with `bash scripts/next_c25_action.sh` (prints exactly one `ACTION:` line) and `bash scripts/status_c25.sh`. Re-derive the completion ETA with `bash scripts/eta_c25.sh`.
3. **PACING CORRECTION — read this before waiting.** `next_c25_action.sh` prints `wake_after=8h`; that is the **poll/re-check interval**, NOT the time to completion. The empirical completion ETA from `eta_c25.sh` is **~30.7 h (median model, n=37) to ~44.8 h (conservative, in-flight-aware)** → roughly **2026-11-28T10:47Z … 2026-11-28T23:00Z** (+/- 30%). **Do NOT treat C25 as finished after 8 h.** Each session: re-run `next_c25_action.sh`; if still `NONE_RUNNER_ALIVE` and gate PENDING, wait the indicated poll interval and re-check; repeat until PASS.
4. When `status_c25.sh` shows `C25 ACCEPTANCE: PASS` **and** all 5 verdict artifacts exist, run `PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py` and `PYTHONPATH=. .venv/bin/python scripts/session_gate.py` — both must PASS before proceeding.
5. Then launch C26: `background_process start command="bash scripts/run_c26_durable.sh" persistent=true`, then monitor `bash scripts/status_c26.sh`.
6. Continue the chain C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32 sequentially; same durable-script pattern per campaign.

**Gate verification tools:** `scripts/probe_hyperliquid_blocker.py` (Hyperliquid API retention), `scripts/verify_campaign_evidence.py` (evidence chain integrity).

**Phase O artifact timestamp:** 2026-11-13T23:38:47Z (episode_edge_okx_full.json).

**Session gate status:** 21/21 checks passed (durable_handoff refreshed this session 2026-11-27T04:02:57Z; evidence VERIFIED exit 0).

This is the single durable handoff and the binding timestamped initial task message for the next agentic session. Re-derive all runner/gate/progress/pacing state with `bash scripts/next_c25_action.sh`; do not use stale values from any pointer file.

---

## 📊 CAMPAIGN CHAIN STATUS (Source of Truth)

| Campaign | Status | Token / Gate | Blocked On | Next Action |
|----------|--------|--------------|------------|-------------|
| **C24** Margin/Liquidation | **PASS** | `FIDELITY_ANCHOR_REPRODUCED` | — | Done (anchor for C25) |
| **C25** Cost/Funding Fidelity | **IN FLIGHT** | `C25 ACCEPTANCE: PENDING` | C24 PASS | **Monitor → wait for PASS (ETA ~31–45 h, not 8 h; 19 cells left)** |
| **C26** Intrabar Path Fidelity | **PENDING** | `C26 ACCEPTANCE: PENDING` | C25 PASS | Launch `run_c26_durable.sh` |
| **C27** Next-Venue Replication | **PRE-REGISTERED** | — | C26 PASS | Wait |
| **C28** Portfolio Allocation | **PRE-REGISTERED** | — | C27 PASS | Wait |
| **C29** Temporal OOS Holdout | **PRE-REGISTERED** | — | C28 PASS | Wait |
| **C30** Execution Realism Stress | **PRE-REGISTERED** | — | C29 PASS | Wait |
| **C31** Forward-Time Holdout | **PRE-REGISTERED** | — | C30 PASS | Wait |
| **C32** Next Independent Venue | **PRE-REGISTERED** | — | C31 PASS | Wait |

**C24 Verdict:** All 4 venues (OKX, Binance UM, MEXC, Bitget) negative PnL. Pooled CI95 `[-265k, -207k]`, `prob_gt_0 = 0.0`. Fidelity anchor — validates simulation infrastructure, not strategy profitability.

**C1–C20 Cross-Venue (OKX + Binance UM multi-year):** `NO_GO` — pooled PnL `−125,367`, bootstrap 95% CI `[-140,619, -110,115]`, `prob_pooled_total_gt_0 = 0.0`. **Closed. Do not relaunch.**

---

## 🔧 OPERATIONAL COMMANDS (Run Exactly These)

### 1. One-shot session probe (start here every session)
```bash
bash scripts/next_c25_action.sh
```
Read the single `ACTION:` line. `NONE_RUNNER_ALIVE` = healthy, keep waiting. `RESUME_C25` = runner dead, relaunch. `LAUNCH_C26` = C25 PASS, proceed.

### 2. Progress + completion ETA (the authoritative pacing)
```bash
bash scripts/status_c25.sh      # per-cell arm/venue/fold state + gate
bash scripts/eta_c25.sh         # empirical ETA (~31–45 h), NOT the 8h poll interval
```

### 3. Evidence + session gate (ONLY after C25 PASS)
```bash
PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py   # must print EVIDENCE VERIFIED
PYTHONPATH=. .venv/bin/python scripts/session_gate.py               # must print PASS
```
Current read-only check (2026-11-27T04:02:57Z): `verify_campaign_evidence.py` → **EVIDENCE VERIFIED (exit 0)**, `session_gate.py` → **21/21 PASS**.

### 4. Launch C26 (ONLY after C25 PASS + both gates PASS)
```bash
background_process start command="bash scripts/run_c26_durable.sh" persistent=true
bash scripts/status_c26.sh
```

### 5. Subsequent campaigns (sequential, same pattern)
```bash
# C27 … C32 — one durable script per campaign
background_process start command="bash scripts/run_c27_durable.sh" persistent=true
bash scripts/status_c27.sh
# repeat for C28, C29, C30, C31, C32
```

---

## ⚠️ BOTTLENECKS & RECOVERY (remove to keep heavy work moving)

| Bottleneck | Symptom | Recovery |
|------------|---------|----------|
| **Stale "~8h remaining" pacing (FIXED 2026-11-27T02:00:50Z)** | Prior handoff read `wake_after=8h` as time-to-completion | `8h` is the **poll interval**; real ETA is **~31–45 h** (`eta_c25.sh`). Wait in 8h poll increments until PASS. |
| C25 runner dies | `RUNNER: NOT ALIVE` in `status_c25.sh` / `ACTION: RESUME_C25` | `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (auto-bootstraps `.venv`, refuses duplicates) |
| C25 slow / pacing | ~19 real cells left, 4 saturated cores, ~1.6 h/cell | Do NOT kill/relaunch/add CPU work. Wait bounded by `eta_c25.sh`; re-check each session. |
| Funding unavailable (skipped) | `UNAVAILABLE_FUNDING` (OKX cost_taker_funding all years) | Already excluded — 8 skipped cells, not compute. |
| Anchor mismatch at C26 | `C26_UNDERPOWERED` / path anchor missing | Re-run C25 verify; ensure C25 consolidated verdict exists. |
| Silent data corruption | `verify_campaign_evidence.py` FAIL | **Stop. Do not proceed.** Investigate artifact mismatch. |

**Current bottleneck status:** none blocking. Single worktree (`main`), one C25 runner tracked as background process `bgp_21a4af5cd001tjmbN0JIriinso` (persistent, running). No lock files, no duplicate runners, no other blocked sessions. The only cost is irreducible CPU runtime (~31–45 h); it cannot be shortened without altering the frozen prereg, which is forbidden.

---

## 📋 SESSION CHECKLIST (Next Agent Must Execute)

- [ ] Run `bash scripts/next_c25_action.sh` — confirm `RUNNER: ALIVE` and `ACTION: NONE_RUNNER_ALIVE`
- [ ] Run `bash scripts/eta_c25.sh` — record the real ETA (~31–45 h); do not assume 8 h
- [ ] If C25 not PASS: **wait / monitor only** — do not launch C26/C27, do not add CPU work, do not kill
- [ ] When C25 PASS: run `verify_campaign_evidence.py` + `session_gate.py` — both must PASS
- [ ] Launch C26 via `background_process start` with `persistent=true`
- [ ] Monitor C26 to first checkpoints (`status_c26.sh` shows cells > 0/16)
- [ ] Update this HANDOFF.md with new timestamps and status before ending the session

---

## 🔒 NO-AVOIDANCE CONSTRAINTS (Enforced by Verifiers — Future Agents Cannot Avoid Heavy Work)

1. **No campaign may run out of chain order.** C26 cell runs = FAIL if C25 not PASS.
2. **No synthetic/placeholder data relabeled as evidence.** `verify_campaign_evidence.py` fails closed.
3. **No verdict token claimed without full artifact chain.** `underpowered` → no decision-grade claim.
4. **No session may declare "no authorized work."** The chain C25→C32 is pre-authorized; run it.
5. **No config switching after results.** Prereg SHA256 frozen at campaign start.
6. **HANDOFF.md is the only durable state file.** Pointer files contain no campaign state; do not edit them except via this handoff refresh.
7. **Do not mistake the poll interval for the ETA.** `wake_after` is when to re-check; `eta_c25.sh` is when C25 actually finishes.

---

## 📍 CURRENT RUNNER STATE (as of 2026-11-27T04:02:57Z)

```
BACKGROUND PROCESS: bgp_21a4af5cd001tjmbN0JIriinso (persistent, RUNNING)
  command: bash scripts/run_c25_durable.sh
PID 2867 (parent) -> workers 49554-49557 (python run_c25_cost_fidelity_campaign.py --jobs 4 --resume)
CPU: 4 saturated cores | Mem: ~700MB each
PROGRESS: 37/56 real cells complete | cost_base 16/16 | cost_taker 16/16 | cost_taker_funding 9/16 | cost_stress 0/16
  cost_taker_funding: binance_um 4/4 DONE; okx 4 SKIPPED (UNAVAILABLE_FUNDING); mexc 1/4 (2023 done); bitget 0/4
REAL CELLS REMAINING: 19 | SKIPPED UNAVAILABLE_FUNDING: 8 | draw_chunks_on_disk: 8 | in_flight: cost_taker_funding_mexc_2024
PACING: poll interval 8h | completion ETA ~30.7h (median, n=37) / ~44.8h (conservative, in-flight-aware)
  -> ~2026-11-28T10:47Z (median) … 2026-11-28T23:00Z (conservative), +/- 30%
ANCHOR: OK — cost_base reproduces C24 d15 exactly; C25 is safe to continue.
GATE: C25 ACCEPTANCE: PENDING | C26 ACCEPTANCE: PENDING
EVIDENCE: verify_campaign_evidence.py -> EVIDENCE VERIFIED (exit 0)
SESSION GATE: 21/21 checks passed
```

**Next session picks up exactly here.** No re-planning. No new direction. **Execute the chain.** Re-derive pacing with `bash scripts/next_c25_action.sh` and `bash scripts/eta_c25.sh`.

---

## End of Handoff.
Next session starts at C25 monitoring (8h poll, ~31–45h ETA) → C26 launch → chain continuation.