# INITIAL TASK MESSAGE — NEXT SESSION (2026-11-19T21:57:21Z — C25 RUNNER ALIVE, 1/56 REAL CELLS DONE, ETA ~2026-11-28, DO NOT RELAUNCH)

**Single durable handoff / source of truth:** `HANDOFF.md`. This file is a pointer only — do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound edge adjudication on real-market, cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps). Real data, `cross_venue=true`, `is_hyperliquid_venue_data=false`; never Hyperliquid performance evidence. Prioritize the `C24 → C25 → C26 → C27` heavy queue above all else; no session may idle or declare "no authorized work."

**Position:** C1–C20 closed `NO_GO`; C21/C22/C23-T1 complete (`PASS`), consolidated `NO_GO`. **C24-T1 complete — `C24 ACCEPTANCE: PASS`, `C24_REOPENS_C1_C23`** (d15 pooled +144,651.69, CI95 [+117,408.41, +173,074.50], prereg rule met over all 16 cells; C1–C23 `NO_GO` superseded). **C25-T1 in flight** — cost/funding fidelity, `cost_base/okx/2023` done (+34,420.88), 1 of 56 real inference cells, gate `C25 ACCEPTANCE: PENDING`, ETA ~2026-11-28 (±30 %). **C26-T1 built, blocked on C25 PASS.** **C27-T1 pre-compute staged** (probe + prereg, NOT launched — launch only after `C26 ACCEPTANCE: PASS`).

**Do exactly this, in order:**

1. `bash scripts/status_c25.sh` then `bash scripts/eta_c25.sh` — these two are the truth.
2. Runner ALIVE → do **not** relaunch, kill, resume, or start any C26 cell. Optionally run `bash scripts/check_c25_anchor.sh` (must be `ANCHOR: OK`; `MISMATCH` is a P0 stop). Then suspend with `schedule_wakeup` at 6–12 h intervals (each cell takes ~3.6 h on this 4-core box).
3. Runner NOT ALIVE and gate PENDING → fix the cause, then resume exactly once: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true`.
4. Gate FAIL → fix only the failing integrity condition; never relax draw floors or edit the prereg.
5. On `C25 ACCEPTANCE: PASS` → deliver the arm × venue × fold cost/funding table + token (`C25_REOPENS_C1_C24` / `C25_NO_GO_ROBUST_TO_COST`), state `funding_model=VENUE_MEAN_SCALAR_FROM_REALIZED_HISTORY` citing `research_state/c25_funding_model_disclosure_20261119T091800Z.json`, report okx as `UNAVAILABLE_FUNDING`, then **immediately durably launch C26-T1** (`bash scripts/run_c26_durable.sh`, `persistent=true`). Do not idle, do not claim no authorized work.
6. On `C26 ACCEPTANCE: PASS` (same session) → run `scripts/probe_c27_venue_acquisition.py` (stage-0, returns `ACQUISITION_VIABLE_*` / `*_BLOCKED_BY_API_RETENTION`), then `c27_prereg_<TS>.{json,md}` with `prereg_status: PRE_REGISTERED_BEFORE_COMPUTE` **before any compute**, then durably launch C27-T1. If no new venue is viable, the only legitimate alternative is a new pre-registered hypothesis on new data — never a same-data rerun or a frozen-signal parameter search.

**No-avoidance rule (binding):** `C24 → C25 → C26 → C27` is the heavy queue. No idling, no "no authorized work", no frozen-signal parameter search, no same-data rerun, no retry of closed acquisitions (`FULL_283D_BLOCKED_BY_API_RETENTION`, `OKX_FUNDING_BLOCKED_BY_API_RETENTION`), no zero-filled funding, no reduced draw counts.

**Full binding context — verified state, measured throughput/ETA, arm definitions, decision rules, monitoring protocol and guardrails:** `HANDOFF.md`.
