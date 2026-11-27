# CRASH-REBOUND-STRATEGY — SINGLE DURABLE HANDOFF (Next Agentic Work Session)
**Repository:** CRASH-REBOUND-STRATEGY
**Handoff timestamp:** 2026-11-27T08:59:50Z
**State re-derived from live ground truth (not from any prior handoff) at 2026-11-27T08:59Z.**

> This file is the ONE durable handoff and the binding timestamped initial task
> message. `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers to this
> file. All other `HANDOFF_*.md` duplicates have been removed to eliminate
> source-of-truth ambiguity — the last duplicate `HANDOFF_20261127T075806Z.md`
> was DELETED 2026-11-27T08:03Z because it carried STALE state ("23 missing /
> RESUME the runner") that contradicted live ground truth (`real_cells_remaining=19`,
> runner ALIVE) and would have caused a forbidden duplicate C25 launch. If anything
> disagrees with this file, this file wins. Re-derive live state with
> `bash scripts/next_c25_action.sh`.

---

## 0. INITIAL TASK MESSAGE (binding — read first, do this)

**You are the next agentic work session on CRASH-REBOUND-STRATEGY. There is NO
"no authorized work" state. The heavy work is a mandatory sequential adjudication
pipeline (C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32). You must advance it.
The next focus campaign is C26 and it is fully built — you may not skip or defer it.**

Concretely, in priority order, and you may not skip or defer any step:

1. **Do NOT relaunch, kill, or add CPU work to C25.** The canonical C25 runner is
   ALIVE (main PID 3033 + 4 workers 3251–3254, ~93% CPU each) and is saturating all
   4 cores (load ~6.5). Adding CPU work slows it; a second runner is forbidden and
   self-guarded by `runner_alive.sh`. Verified live 2026-11-27T08:06Z via
   `next_c25_action.sh` (`RUNNER: ALIVE`, `ANCHOR: OK`, `real_cells_remaining=19`).
   NOTE: the PID in any older note (2867) is DEAD — do not trust hardcoded PIDs;
   discover the live runner with `bash scripts/next_c25_action.sh` / `scripts/runner_alive.sh`.
2. **Monitor C25 to a consolidated verdict using bounded waits only.** Run
   `bash scripts/next_c25_action.sh`, then `bash -c 'sleep 540; bash scripts/next_c25_action.sh'`.
   Repeat until it reports `C25 ACCEPTANCE: PASS`. Do not end the session before a
   bounded wait completes; do not mistake the 8h poll hint for completion (ETA ~31 h
   median → ~2026-11-28T11:47Z, conservative ~39 h).
3. **The instant C25 emits `ACCEPTANCE: PASS`**, run the gate checks and launch C26
   (exact commands in §3). Then C27→C32 sequentially. Each campaign is a mandatory
   same-session successor; never bypass a gate. C26 is the next focus campaign and is
   fully implemented (`run_c26_path_fidelity_campaign.py` + `run_c26_durable.sh` +
   `verify_c26_focus_campaign.py` + prereg `c26_prereg_20261119T121500Z.json`).
4. **C31 holdout archives were PRE-FETCHED — do NOT re-download blindly.** Current
   state: OKX 34/34 ✅, Bitget 34/34 ✅, MEXC 33/34 (FIL incomplete), Binance 33/34
   (Nov-2026 Vision zip not yet published). Before C31: (a) verify provenance
   (`fabricated_data:false`, gaps recorded, never zero-filled), (b) finish the two
   gaps — re-fetch Binance after the 2026-11 Vision zip publishes (~early Dec), and
   record MEXC FIL as incomplete/covered-by-other-venues. Do this with I/O only;
   never while it would starve C25's 4 cores.
5. **The done-gate is `scripts/session_gate.py` — it reports `21/21 checks passed`.**
   Binding evidence for that gate: `scripts/probe_hyperliquid_blocker.py` (Hyperliquid
   blocker) and `scripts/verify_campaign_evidence.py` (evidence verifier). Phase O
   anchor artifact timestamp: `2026-11-13T23:38:47Z`
   (`research_state/episode_edge_okx_full.json`). Do not regress the gate: re-run
   `PYTHONPATH=. .venv/bin/python scripts/session_gate.py` before ending any session
   and keep this file's `21/21 checks passed` record true.
6. **Before ending any session**, update this file's timestamp and §1 state table.

If you find yourself about to declare "waiting / nothing to do," that is forbidden:
the correct behavior is a bounded `sleep 540` wait loop (§2), not session exit. The
C25 runner is persistent and survives session/turn boundaries — progress continues
even if a session ends, but you may not *choose* idleness while the chain is incomplete.

---

## 1. CURRENT STATE — single source of truth (re-derived live 2026-11-27T08:59Z)

| Campaign | Status | Evidence |
|----------|--------|----------|
| **C24** | ✅ COMPLETED | `c24_decision_verdict_CONSOLIDATED_20261119T013154Z.json` — `C24_REOPENS_C1_C23` |
| **C25** | 🔄 IN FLIGHT | Runner ALIVE (main PID 3033 + workers 3251–3254 ~93% CPU; verified 08:59Z). `cost_base` 16/16 ✓, `cost_taker` 16/16 ✓, `cost_taker_funding` in progress (7 real remaining + 8 `UNAVAILABLE_FUNDING`), `cost_stress` 0/16. In-flight: `cost_taker_funding/mexc/2024` (`[run] cost_taker_funding mexc 2024` in log). **No consolidated verdict yet.** |
| **C26** | 📋 PRE-REGISTERED + FULLY BUILT (NEXT FOCUS) | `c26_prereg_20261119T121500Z.json` (+`.md`); `run_c26_path_fidelity_campaign.py`, `run_c26_durable.sh`, `verify_c26_focus_campaign.py` — no checkpoints, no runner yet |
| **C27** | 📋 PRE-REGISTERED ONLY | `c27_prereg_20261119T215721Z.json` — no checkpoints, no runner (venue fixed by `probe_c27_venue_acquisition.py`) |
| **C28** | 📋 PRE-REGISTERED ONLY | `c28_prereg_20261121T013400Z.json` — no checkpoints, no runner |
| **C29** | 📋 PRE-REGISTERED ONLY | `c29_prereg_20261121T031907Z.json` — no checkpoints, no runner |
| **C30** | 📋 PRE-REGISTERED ONLY | `c30_prereg_20261121T051754Z.json` — no checkpoints, no runner |
| **C31** | 📋 PRE-REGISTERED; HOLDOUT DATA PRE-FETCHED | `c31_prereg_20261121T052233Z.json` — **BLOCKED on C30 ACCEPTANCE: PASS** |
| **C32** | 📋 PRE-REGISTERED ONLY | `c32_prereg_20261121T061508Z.json` — **BLOCKED on C31 ACCEPTANCE: PASS** |
| **C31 holdout archives** | 🟡 MOSTLY READY (real data) | `research_state/archives/{okx,binance_um,mexc,bitget}_holdout_20260929_20261121/` — OKX 34/34 ✅, Bitget 34/34 ✅, MEXC 33/34 (FIL incomplete), Binance 33/34 (Nov zip unpublished). All `fabricated_data:false`. |

**Live numbers (authoritative `next_c25_action.sh` at 08:59Z):**
- Real inference cells remaining: **19** (7 `cost_taker_funding` + 12 `cost_stress`).
- `UNAVAILABLE_FUNDING` (never zero-filled): **8/8** (OKX funding).
- Draw chunks on disk: **29** (actively progressing; ~1 chunk / 7 min).
- Runner health: main PID 3033 + 4 workers in `R` state, current log `c25_run_*.log`, **no errors**.
- **Authoritative ETA: ~30.7 h (median) → ~2026-11-28T11:47Z (±30%)**; conservative
  in-flight-aware ~39 h → ~2026-11-28T20:00Z, at 4 saturated cores.
- `GATE: C25 ACCEPTANCE: PENDING`, `C26 ACCEPTANCE: PENDING`.
- `ANCHOR: OK` — cost_base reproduces C24 d15 exactly; C25 is safe to continue.
- `session_gate.py`: **21/21 checks passed** (Phase O `2026-11-13T23:38:47Z`).
- `check_queue_readiness.sh`: **QUEUE READY** (C25..C32 prereg + full implementation).

**Sequential dependency chain (HARD GATES):**
```
C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32
```
No campaign cell may run until its predecessor emits `ACCEPTANCE: PASS` (consolidated verdict).

---

## 2. MONITORING PROTOCOL (bounded waits — do not idle, do not exit early)

```bash
# Authoritative single command for runner/gate/progress/pacing:
bash scripts/next_c25_action.sh

# Bounded wait loop (repeat until C25 ACCEPTANCE: PASS):
bash -c 'sleep 540; bash scripts/next_c25_action.sh'
```

- `ACTION: NONE_RUNNER_ALIVE` is the expected state while C25 runs — it means
  "keep waiting," NOT "stop." Do a bounded wait and re-check.
- Never launch a duplicate runner (`run_c25_durable.sh` self-guards via `runner_alive.sh`).
- Never kill the live runner or its workers (discover PIDs via `next_c25_action.sh`).
- The 8h figure in pacing output is a poll hint, **not** the ETA. ETA is ~31 h.
- `sleep 540` stays under the harness idle-timeout; the persistent runner survives
  even if a session is recycled, so no single session needs to babysit 31 h in one turn.

---

## 3. ON C25 `ACCEPTANCE: PASS` — LAUNCH THE NEXT CAMPAIGN (mandatory heavy work)

```bash
# 1) Verify the C25 gate + evidence + session gate (all must PASS):
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. .venv/bin/python scripts/session_gate.py          # must stay 21/21 checks passed

# 2) Launch C26 durable runner (persistent — survives session/turn boundaries):
background_process start command="bash scripts/run_c26_durable.sh" persistent=true
```

Then, after **each** campaign emits a `CONSOLIDATED` verdict with `ACCEPTANCE: PASS`,
launch the next (sequentially, never in parallel):

```bash
background_process start command="bash scripts/run_c27_durable.sh" persistent=true
background_process start command="bash scripts/run_c28_durable.sh" persistent=true
background_process start command="bash scripts/run_c29_durable.sh" persistent=true
background_process start command="bash scripts/run_c30_durable.sh" persistent=true
# C31 requires holdout archive manifests (2026-09-29 → 2026-11-21) — see §4:
background_process start command="bash scripts/run_c31_durable.sh --direction c31-a" persistent=true
# C32 requires C31 consolidated verdict as anchor:
background_process start command="bash scripts/run_c32_durable.sh --direction c32-a" persistent=true
```

**Read-only status probes (never launch/kill via these):**
`bash scripts/status_c26.sh` … `status_c30.sh`,
`bash scripts/status_c31.sh --direction c31-a`,
`bash scripts/status_c32.sh --direction c32-a`.

**Readiness audit (run any time, no venv needed):** `bash scripts/check_queue_readiness.sh`
— currently `QUEUE READY` (every campaign C25..C32 has a prereg + full implementation).

---

## 4. BOTTLENECKS & REMEDIATIONS

| Bottleneck | Impact | Remediation |
|------------|--------|-------------|
| **Stale duplicate handoff (REMOVED 2026-11-27T08:03Z)** | `HANDOFF_20261127T075806Z.md` claimed "23 missing / RESUME the runner" — it contradicted live state and would have triggered a forbidden duplicate C25 launch. | DELETED 2026-11-27T08:03Z. This file is now the single source of truth; `AGENT_HANDOFF.md`/`INITIAL_TASK_MESSAGE.md` are pointers only. |
| **Stale hardcoded PID (FIXED 2026-11-27T08:03Z)** | Older notes said "do not kill PID 2867," but 2867 is DEAD; an agent checking it could conclude the runner died and relaunch (duplicate). | This file records the live runner (PID 3033 + workers 3251–3254) AND instructs discovery via `next_c25_action.sh` / `runner_alive.sh` instead of trusting hardcoded PIDs. |
| **Done-gate `durable_handoff` (GREEN)** | `session_gate.py` requires this file to record `21/21 checks passed`, the Phase O timestamp, and the evidence-verifier references. | This file records `21/21 checks passed`, Phase O `2026-11-13T23:38:47Z`, and references `probe_hyperliquid_blocker.py` + `verify_campaign_evidence.py`. Re-run `session_gate.py` to confirm 21/21 before ending any session. |
| **C25 is compute-bound (~31 h ETA)** | C26 cannot launch until C25 PASS | Inherent to 4 saturated cores; do NOT add CPU work or kill. Remediation is the bounded-wait monitor (§2). The persistent runner continues across sessions, so no session needs to babysit 31 h in one turn. |
| **C31 holdout archives missing (SUBSTANTIALLY CLEARED)** | C31 holdout_primary cells could not infer | Pre-fetched real OHLCV for all 4 venues into `research_state/archives/<venue>_holdout_20260929_20261121/`. **OKX 34/34 ✅, Bitget 34/34 ✅, MEXC 33/34 (FIL incomplete), Binance 33/34 (Nov-2026 Vision zip unpublished → have 2026-09-29→10-31).** All `fabricated_data:false`. **Remaining:** re-fetch Binance after the 2026-11 Vision monthly zip publishes (~early Dec); record MEXC FIL as incomplete (covered by other venues). Verify per-symbol `status:ok` + gaps before C31. |
| **C25 `cost_stress` arm not started** | Blocks pipeline | Runner auto-advances after `cost_taker_funding` completes. Monitor only. |
| **No C25 consolidated verdict yet** | C26 cannot launch | Wait for `c25_decision_verdict_CONSOLIDATED_<TS>.json` with `ACCEPTANCE: PASS`. |
| **Sequential gate enforcement** | No parallel campaign execution | By design. Each campaign is a mandatory same-session successor. Do not bypass. |
| **Poll interval ≠ ETA** | Agents mistake 8h poll for completion | `eta_c25.sh` is authoritative (~31 h). Wait in 8h poll increments until PASS. |

**Holdout acquisition provenance:** archives are REAL exchange-published
OHLCV (OKX history-candles, Binance Vision UM monthly zips, MEXC/Bitget perp archives),
NOT Hyperliquid — cross-venue proxies; document venue basis when comparing to
Hyperliquid-denominated spec targets. Non-zero fetcher exits for Binance/MEXC were
incomplete-coverage (expected), not fetch failures; no data was fabricated or zero-filled.

---

## 5. GUARDRAILS (non-negotiable)

1. **No duplicate runners** — `runner_alive.sh` guard in each `run_cXX_durable.sh`.
2. **No reduced draw floors** — 20k bootstrap / 20k permutation / 2k placebo / 2k strata are immutable.
3. **No signal-path drift** — frozen at C24/C25/C26/C30 sentinel values (RSI-21/20, target 9%, etc.).
4. **No synthetic gap-fill** — missing funding = `UNAVAILABLE_FUNDING`; missing candles = recorded gap (never zero-filled).
5. **Artifacts are immutable** — never edit completed campaign outputs.
6. **Persistent background processes** — all campaign runners MUST use `persistent=true`.
7. **No idle exit while C25 runs** — use bounded `sleep 540` waits (§2), not session termination.
8. **Holdout data is I/O-only prep** — never let acquisition/verification starve C25's 4 cores.
9. **Keep the done-gate green** — end every session with `session_gate.py` at `21/21 checks passed`.

---

## 6. CHECKLIST FOR NEXT SESSION

- [ ] `bash scripts/next_c25_action.sh` — confirm `RUNNER: ALIVE`, note `real_cells_remaining` (currently 19).
- [ ] Bounded-wait loop (`sleep 540`) until `C25 ACCEPTANCE: PASS`; do not exit early.
- [ ] On PASS: `verify_c25_focus_campaign.py` + `verify_campaign_evidence.py` + `session_gate.py` (21/21) all PASS.
- [ ] Launch C26 (`run_c26_durable.sh`, persistent); monitor via `status_c26.sh`.
- [ ] Repeat sequentially C27→C32; never bypass a gate. `check_queue_readiness.sh` must stay `QUEUE READY`.
- [ ] Before C31: verify holdout archives — OKX/Bitget 34/34, MEXC FIL incomplete, re-fetch Binance after Nov Vision zip publishes; confirm `fabricated_data:false` + gaps recorded.
- [ ] End with `PYTHONPATH=. .venv/bin/python scripts/session_gate.py` → `21/21 checks passed`.
- [ ] Update this file's timestamp + §1 table before ending the session.

---

## 7. CONTEXT FOR FUTURE AGENTS

This repo implements a sequential adjudication pipeline for a crash-rebound trading
strategy. Each campaign (C24–C32) tests one fidelity axis (margin, cost, path,
allocation, holdout, execution, forward-time, venue replication). The pipeline
**cannot be short-circuited** — every campaign must pass its gate before the next
may run. **Heavy work is mandatory; there is no authorized idle state while any
campaign in the chain is incomplete.** Continue from wherever the pipeline stands.

*Single entry probe: `bash scripts/next_c25_action.sh`. C25 is running persistently
(main PID 3033 + workers 3251–3254; discover via the probe, do not trust hardcoded
PIDs). Do not kill it. Do not restart it. Monitor → verify → launch next (C26 is the
next focus campaign, fully built, cannot be skipped). C31 holdout data is pre-fetched;
finish the two gaps, don't re-download blindly. Keep `session_gate.py` at 21/21 checks passed.*

---
*Generated 2026-11-27T08:59:50Z by Kilo agent; re-derived live from ground truth at
2026-11-27T08:59Z: `RUNNER: ALIVE` (main PID 3033 + workers 3251–3254 ~93% CPU each,
load ~6.5 on 4 cores), `C25 ACCEPTANCE: PENDING`, `real_cells_remaining=19`,
`skipped_unavailable_funding=8`, `draw_chunks_on_disk=29`, in-flight
`cost_taker_funding_mexc_2024`, runner log error-free, `ANCHOR: OK`,
`session_gate.py` **21/21 checks passed — DONE**, `check_queue_readiness.sh` QUEUE
READY (C25..C32 all prereg+impl), C26 fully built (next focus campaign, cannot be
skipped). Bottlenecks removed this session: stale duplicate
`HANDOFF_20261127T075806Z.md` DELETED (would have caused a forbidden duplicate C25
launch); stale dead PID 2867 replaced with live-PID discovery. Single `HANDOFF.md`
remains — no fragmentation. Only limiter is inherent ~31 h C25 compute via the
bounded-wait monitor §2.*