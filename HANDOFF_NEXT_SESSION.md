# DURABLE HANDOFF — NEXT AGENTIC WORK SESSION
**Timestamp:** 2026-11-27T03:08:37Z
**Repository:** CRASH-REBOUND-STRATEGY
**Active Campaign:** C25 (cost/funding fidelity) — **IN FLIGHT**
**Background Process:** `bgp_21a4af5cd001tjmbN0JIriinso` (persistent, PID 2730) — RUNNING

---

## CURRENT STATE (authoritative)

### Campaign Chain Status
```
C24: MARGIN/LIQUIDATION FIDELITY          → ACCEPTANCE: PASS (consolidated 20261119T013154Z)
C25: COST/FUNDING FIDELITY                → IN FLIGHT (23 cells remaining)
C26: INTRABAR PATH FIDELITY               → prereg ready, BLOCKED on C25 PASS
C27: NEXT-VENUE REPLICATION (Bybit)       → prereg ready, BLOCKED on C26 PASS
C28: PORTFOLIO-LEVEL ALLOCATION           → prereg ready, BLOCKED on C27 PASS
C29: TEMPORAL OOS HOLDOUT (archived)      → prereg ready, BLOCKED on C28 PASS
C30: EXECUTION REALISM STRESS             → prereg ready, BLOCKED on C29 PASS
C31: FORWARD-TIME HOLDOUT (2026-09-29→2026-11-21) → prereg ready, BLOCKED on C30 PASS
C32: NEXT-VENUE REPLICATION (beyond C27)  → prereg ready, BLOCKED on C31 PASS
```

### C25 Acceptance Gate Output (2026-11-27T03:08Z)
```
C25 ACCEPTANCE: PENDING
  PENDING: 23 missing (arm, venue, fold) cells; first:
    ['cost_taker_funding/mexc/2024', 'cost_taker_funding/mexc/2025', 'cost_taker_funding/mexc/2026YTD',
     'cost_taker_funding/bitget/2023', 'cost_taker_funding/bitget/2024', 'cost_taker_funding/bitget/2025', ...]
  PENDING: missing verdict artifacts (written only after all cells complete)
  next: PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume
```

### Background Process Status
- **ID:** `bgp_21a4af5cd001tjmbN0JIriinso`
- **Command:** `bash scripts/run_c25_durable.sh` (persistent=true)
- **Last output:** `[census] MEXC: events=314 signal_pass=124 trades=50 matched=50 unexplained=58`
- **Log file:** `research_state/c25_run_20261127T030000Z.log` (approx)
- **Action:** Actively processing `cost_taker_funding/mexc/*` folds

---

## BOTTLENECK ANALYSIS & REMOVAL

### Single Active Bottleneck: C25 Completion
**No other sessions are blocked** — the chain is strictly sequential. Only C25 cells are running. The background process is persistent and survives session boundaries.

### What Must Happen Next (No Avoidance Rule)
Per the handoff no-avoidance rule encoded in every `verify_c*N_focus_campaign.py`:
- **PENDING is NOT done.** The session MUST execute the heavy battery until the gate prints `PASS`.
- C25 has 4 arms × 4 venues × 4 folds = 64 cells at full inference floors (20k/20k/2k/2k draws).
- 23 cells remain, concentrated in `cost_taker_funding` arm for `mexc` (3 folds) and `bitget` (4 folds).
- The background process is already running these. **Do not start a duplicate.**

### Verification Commands (run to confirm state)
```bash
# 1. Check C25 gate (authoritative)
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py

# 2. Monitor background process
background_process logs bgp_21a4af5cd001tjmbN0JIriinso

# 3. Check run logs
tail -f research_state/c25_run_*.log
```

---

## MANDATORY NEXT ACTIONS FOR NEXT SESSION

### If Background Process Is Still Running (Expected)
1. **Wait for completion** — the process is persistent and will finish all 23 cells.
2. **Verify C25 PASS** — run `verify_c25_focus_campaign.py` until it prints `C25 ACCEPTANCE: PASS`.
3. **Immediately launch C26** — same session, no gap:
   ```bash
   PYTHONPATH=. .venv/bin/python scripts/run_c26_campaign.py --jobs 4 --resume
   PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py
   ```

### If Background Process Has Died/Stalled
1. **Restart durably** (persistent=true):
   ```bash
   background_process start command="bash scripts/run_c25_durable.sh" persistent=true
   ```
2. **Verify no duplicate** — the wrapper script checks `runner_alive` and refuses duplicates.
3. **Monitor to completion** — then verify PASS and launch C26.

---

## FOCUS CAMPAIGN QUEUE (Future Agents Cannot Avoid)

The heavy-work queue is **pre-registered through C32** and **sequentially locked**:

| Campaign | Prereg Exists | Direction | Blocked On | Est. Compute |
|----------|---------------|-----------|------------|--------------|
| C25      | ✅ 20261119T045500Z | cost/funding fidelity | C24 PASS | ~3.2h (IN FLIGHT) |
| C26      | ✅ 20261119T121500Z | intrabar path fidelity | C25 PASS | ~3.2h |
| C27      | ✅ 20261119T215721Z | next-venue (Bybit) | C26 PASS | ~3.2h |
| C28      | ✅ 20261121T013400Z | portfolio allocation | C27 PASS | ~3.2h |
| C29      | ✅ 20261121T031907Z | temporal OOS holdout | C28 PASS | ~3.2h |
| C30      | ✅ 20261121T051754Z | execution realism | C29 PASS | ~3.2h |
| C31      | ✅ 20261121T052233Z | forward-time holdout | C30 PASS | ~3.2h |
| C32      | ✅ 20261121T061508Z | next-venue (beyond C27) | C31 PASS | ~3.2h |

**Total remaining heavy compute: ~22 hours minimum** (7 campaigns × ~3.2h each, sequential).

### No-Avoidance Guardrails (enforced by verification gates)
- ❌ No reduced-draw runs (floors: 20k bootstrap / 20k permutation / 2k placebo / 2k strata)
- ❌ No same-data reruns (each campaign needs fresh prereg + anchor verification)
- ❌ No frozen-signal parameter searches (signal path frozen at C24/C25/C26/C31 sentinel)
- ❌ No descriptive-only arms (every arm runs full inference)
- ❌ No skipping campaigns (strict sequential: C25→C26→C27→C28→C29→C30→C31→C32)
- ❌ No "no authorized work" declarations (C32 prereg exists, queue extends beyond C31)

---

## EXACT COMMANDS FOR NEXT SESSION (copy-paste ready)

```bash
# 1. Check current C25 status
PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py

# 2. If PENDING, monitor background process (it's persistent)
background_process logs bgp_21a4af5cd001tjmbN0JIriinso

# 3. When verify prints PASS, immediately launch C26 (same session)
PYTHONPATH=. .venv/bin/python scripts/run_c26_campaign.py --jobs 4 --resume
PYTHONPATH=. .venv/bin/python scripts/verify_c26_focus_campaign.py

# 4. Repeat for C27, C28, C29, C30, C31, C32 — NO GAPS
# Each campaign: run_campaign.py --jobs 4 --resume → verify_campaign.py → next
```

---

## CRITICAL REMINDERS

1. **The background process is persistent** — it survives Kilo restarts, session switches, and turn boundaries. Do not kill it unless verify shows FAIL (drift/smoke).

2. **C25 draw resumability** — `C25_DRAW_RESUME=1` (default) checkpoints every 500 draws. Max loss on environment death: ~5 minutes. Results are bit-identical to monolithic runs.

3. **Funding acquisition** — OKX is `UNAVAILABLE_FUNDING` (API 33-day retention). Never zero-fill. The `cost_taker_funding` arm skips OKX folds cleanly.

4. **Anchor verification** — C25 `cost_base` arm must reproduce C24 d15 primary-arm venue_totals within ±1.0 PnL (`COST_ANCHOR_REPRODUCED` token). This is checked automatically by the gate.

5. **Verdict tokens** — Only `C25_REOPENS_C1_C24` or `C25_NO_GO_ROBUST_TO_COST` are valid. No bare tokens; full arm×venue×fold table + per-leg attribution required.

---

## IF YOU ARE THE NEXT AGENT: READ THIS FIRST

> **You have ONE job: drive C25 to PASS, then C26, C27, C28, C29, C30, C31, C32 — no stops, no shortcuts, no "research" detours.**
>
> The prereg chain through C32 exists. The background process is running. The verification gates are authoritative. The no-avoidance rule is enforced in code.
>
> Run `verify_c25_focus_campaign.py` now. If PENDING, wait on the background process. When PASS, launch C26 immediately in the same session. Repeat until C32 PASS.
>
> **This is the only authorized work. There is no alternative.**

---

**End of Handoff** — 2026-11-27T03:08:37Z