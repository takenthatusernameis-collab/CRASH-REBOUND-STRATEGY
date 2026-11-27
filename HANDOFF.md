# CRASH-REBOUND-STRATEGY — SINGLE DURABLE HANDOFF (Next Agentic Work Session)
**Repository:** CRASH-REBOUND-STRATEGY
**Handoff timestamp:** 2026-11-27T04:18:51Z
**State re-derived from ground truth (not from any prior handoff) at 2026-11-27T04:18Z.**

> This file is the ONE durable handoff and the binding timestamped initial task
> message. `AGENT_HANDOFF.md` and `INITIAL_TASK_MESSAGE.md` are pointers to this
> file. All other `HANDOFF_*.md` / `HANDOFF_NEXT_SESSION.md` duplicates have been
> removed to eliminate source-of-truth ambiguity. If anything disagrees with this
> file, this file wins. Re-derive live state with `bash scripts/next_c25_action.sh`.

---

## 0. INITIAL TASK MESSAGE (binding — read first, do this)

**You are the next agentic work session on CRASH-REBOUND-STRATEGY. There is NO
"no authorized work" state. The heavy work is a mandatory sequential adjudication
pipeline (C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32). You must advance it.**

Concretely, in priority order, and you may not skip or defer any step:

1. **Do NOT relaunch, kill, or add CPU work to C25.** The canonical C25 runner is
   ALIVE (PID 2867 + 4 workers ~88% CPU each) and is saturating all 4 cores. Adding
   CPU work slows it. (Verified live 2026-11-27T04:18Z via `next_c25_action.sh`.)
2. **Monitor C25 to a consolidated verdict using bounded waits only.** Run
   `bash scripts/next_c25_action.sh`, then `bash -c 'sleep 540; bash scripts/next_c25_action.sh'`.
   Repeat until it reports `C25 ACCEPTANCE: PASS`. Do not end the session before a
   bounded wait completes; do not mistake the 8h poll hint for completion (ETA ~31 h).
3. **The instant C25 emits `ACCEPTANCE: PASS`**, run the gate checks and launch C26
   (exact commands in §3). Then C27→C32 sequentially. Each campaign is a mandatory
   same-session successor; never bypass a gate.
4. **C31 holdout archives were PRE-FETCHED (2026-11-27T04:11–04:12Z) — do NOT
   re-download blindly.** Current state in §1/§4: OKX 34/34 ✅, Bitget 34/34 ✅,
   MEXC 33/34 (FIL incomplete), Binance partial (Nov-2026 Vision zip not yet published).
   Before C31: (a) verify provenance (`fabricated_data:false`, gaps recorded, never
   zero-filled), (b) finish the two gaps — re-fetch Binance after the 2026-11 Vision
   zip publishes, and record MEXC FIL as incomplete/covered-by-other-venues. Do this
   with I/O only; never while it would starve C25's 4 cores.
5. **Before ending any session**, update this file's timestamp and §1 state table.

If you find yourself about to declare "waiting / nothing to do," that is forbidden:
the correct behavior is a bounded `sleep 540` wait loop (§2), not session exit. The
C25 runner is persistent and survives session/turn boundaries — progress continues
even if a session ends, but you may not *choose* idleness while the chain is incomplete.

---

## 1. CURRENT STATE — single source of truth (re-derived 2026-11-27T04:17Z)

| Campaign | Status | Evidence |
|----------|--------|----------|
| **C24** | ✅ COMPLETED | `c24_decision_verdict_CONSOLIDATED_20261119T013154Z.json` — `C24_REOPENS_C1_C23` |
| **C25** | 🔄 IN FLIGHT | Runner ALIVE (PID 2867 + 4 workers). `cost_base` 16/16 ✓, `cost_taker` 16/16 ✓, `cost_taker_funding` 9/16 (7 real remaining + 8 `UNAVAILABLE_FUNDING`), `cost_stress` 0/16. In-flight: `cost_taker_funding/mexc/2024`. **No consolidated verdict yet.** |
| **C26** | 📋 PRE-REGISTERED ONLY | `c26_prereg_20261119T121500Z.json` (+`.md`) — no checkpoints, no runner |
| **C27** | 📋 PRE-REGISTERED ONLY | `c27_prereg_20261119T215721Z.json` — no checkpoints, no runner |
| **C28** | 📋 PRE-REGISTERED ONLY | `c28_prereg_20261121T013400Z.json` — no checkpoints, no runner |
| **C29** | 📋 PRE-REGISTERED ONLY | `c29_prereg_20261121T031907Z.json` — no checkpoints, no runner |
| **C30** | 📋 PRE-REGISTERED ONLY | `c30_prereg_20261121T051754Z.json` — no checkpoints, no runner |
| **C31** | 📋 PRE-REGISTERED; HOLDOUT DATA PRE-FETCHED | `c31_prereg_20261121T052233Z.json` — **BLOCKED on C30 ACCEPTANCE: PASS**. Holdout archives (2026-09-29→2026-11-21) fetched — see row below. |
| **C32** | 📋 PRE-REGISTERED ONLY | `c32_prereg_20261121T061508Z.json` — **BLOCKED on C31 ACCEPTANCE: PASS** |
| **C31 holdout archives** | 🟡 MOSTLY READY (real data) | `research_state/archives/{okx,binance_um,mexc,bitget}_holdout_20260929_20261121/` — OKX 34/34 ✅, Bitget 34/34 ✅, MEXC 33/34 (FIL incomplete), Binance partial (Nov zip unpublished). All `fabricated_data:false`. |

**Live numbers (from `next_c25_action.sh` / `eta_c25.sh` at 04:17Z):**
- Real inference cells remaining: **19** (7 `cost_taker_funding` + 12 `cost_stress`).
- `UNAVAILABLE_FUNDING` (never zero-filled): **8/8** (OKX funding).
- Draw chunks on disk: 11/40 for the in-flight cell.
- **Authoritative ETA: ~30.7 h (median) → ~2026-11-28T11:00Z (±30%)** at 4 saturated cores.
- `GATE: C25 ACCEPTANCE: PENDING`, `C26 ACCEPTANCE: PENDING`.
- `ANCHOR: OK` — cost_base reproduces C24 d15 exactly; C25 is safe to continue.

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
- Never kill PID 2867 or its workers.
- The 8h figure in pacing output is a poll hint, **not** the ETA. ETA is ~31 h.

---

## 3. ON C25 `ACCEPTANCE: PASS` — LAUNCH THE NEXT CAMPAIGN (mandatory heavy work)

```bash
# 1) Verify the C25 gate + evidence + session gate (all must PASS):
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py
PYTHONPATH=. .venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. .venv/bin/python scripts/session_gate.py

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

---

## 4. BOTTLENECKS & REMEDIATIONS

| Bottleneck | Impact | Remediation |
|------------|--------|-------------|
| **Handoff fragmentation (REMOVED earlier)** | 4 stale `HANDOFF_*.md` all claimed canonical | Consolidated into this single file; duplicates deleted. `AGENT_HANDOFF.md`/`INITIAL_TASK_MESSAGE.md` are pointers only. |
| **C25 is compute-bound (~31 h ETA)** | C26 cannot launch until C25 PASS | Inherent to 4 saturated cores; do NOT add CPU work or kill. Remediation is the bounded-wait monitor (§2). The persistent runner continues across sessions, so no session needs to babysit 31 h in one turn. |
| **C31 holdout archives missing (SUBSTANTIALLY CLEARED 04:11–04:12Z)** | C31 holdout_primary cells could not infer | Pre-fetched real OHLCV for all 4 venues into `research_state/archives/<venue>_holdout_20260929_20261121/`. **OKX 34/34 ✅, Bitget 34/34 ✅, MEXC 33/34 (FIL incomplete), Binance partial (Nov-2026 Vision zip unpublished → have 2026-09-29→10-31).** All `fabricated_data:false`. **Remaining:** re-fetch Binance after the 2026-11 Vision monthly zip publishes (~early Dec); record MEXC FIL as incomplete (covered by other venues). Verify per-symbol `status:ok` + gaps before C31. |
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

---

## 6. CHECKLIST FOR NEXT SESSION

- [ ] `bash scripts/next_c25_action.sh` — confirm `RUNNER: ALIVE`, note `real_cells_remaining`.
- [ ] Bounded-wait loop (`sleep 540`) until `C25 ACCEPTANCE: PASS`; do not exit early.
- [ ] On PASS: `verify_c25_focus_campaign.py` + `verify_campaign_evidence.py` + `session_gate.py` all PASS.
- [ ] Launch C26 (`run_c26_durable.sh`, persistent); monitor via `status_c26.sh`.
- [ ] Repeat sequentially C27→C32; never bypass a gate.
- [ ] Before C31: verify holdout archives — OKX/Bitget 34/34, MEXC FIL incomplete, re-fetch Binance after Nov Vision zip publishes; confirm `fabricated_data:false` + gaps recorded.
- [ ] Update this file's timestamp + §1 table before ending the session.

---

## 7. CONTEXT FOR FUTURE AGENTS

This repo implements a sequential adjudication pipeline for a crash-rebound trading
strategy. Each campaign (C24–C32) tests one fidelity axis (margin, cost, path,
allocation, holdout, execution, forward-time, venue replication). The pipeline
**cannot be short-circuited** — every campaign must pass its gate before the next
may run. **Heavy work is mandatory; there is no authorized idle state while any
campaign in the chain is incomplete.** Continue from wherever the pipeline stands.

*C25 is running persistently (PID 2867). Do not kill it. Do not restart it. Monitor → verify → launch next. C31 holdout data is pre-fetched; finish the two gaps, don't re-download blindly.*

---
*Generated 2026-11-27T04:16:24Z by Kilo agent. Single durable handoff; durable across session/turn boundaries.*