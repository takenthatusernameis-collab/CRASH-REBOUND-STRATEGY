# INITIAL TASK MESSAGE — POINTER ONLY (2026-11-23T05:40:16Z)

**This file is not a source of truth.** The single durable handoff AND the
binding timestamped initial task message live in `HANDOFF.md` §1.

Next session, do exactly this and nothing else:

1. `goal start` (objective is quoted in `HANDOFF.md` §1 step 0), then `cancel_wakeup list`.
2. `bash scripts/next_c25_action.sh` — the single read-only source of truth. Obey its one `ACTION:` line; never build your own `ps`/`ls`/log chain.
3. If `ACTION: NONE_RUNNER_ALIVE` → `bash scripts/check_c25_anchor.sh`, then exactly one bounded wait `bash -c 'sleep 540; bash scripts/next_c25_action.sh'` (600000 ms tool timeout), then end the turn.
4. If `ACTION: RESUME_C25` → resume exactly once: `background_process start command="bash scripts/run_c25_durable.sh" persistent=true` (self-bootstraps `.venv`).
5. On any `ACCEPTANCE: PASS` → launch the mandatory same-session successor per `HANDOFF.md` §1 steps 4–5 and §7.

**Live priority:** C25 round-trip cost & realized-funding fidelity campaign (heavy queue `C24 → C25 → … → C32+`, all BUILT/STAGED and gate-held behind C25 PASS). Repo priority `CRASH-REBOUND-STRATEGY`: crash-rebound edge adjudication on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps); `cross_venue=true`; `is_hyperliquid_venue_data=false`; never relabelled as Hyperliquid evidence.

Read `HANDOFF.md` for the full ordered task list, ground truth, monitoring protocol, persistence model, bottleneck register, guardrails, and the C26–C32 launch chain.