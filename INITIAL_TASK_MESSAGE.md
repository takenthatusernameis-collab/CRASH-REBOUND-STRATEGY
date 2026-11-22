# INITIAL TASK MESSAGE — NEXT AGENTIC SESSION (POINTER ONLY)

**Repository:** `CRASH-REBOUND-STRATEGY` — crash-rebound trading strategy research/backtesting on real-market cross-venue data (OKX, Binance UM, MEXC, Bitget USDT-perps).

**SOURCE OF TRUTH:** `HANDOFF.md` is the single durable handoff and the binding initial task message (its section 1). This file is a pointer only — if this file and `HANDOFF.md` disagree, `HANDOFF.md` wins.

**LIVE PRIORITY:** The **C25 round-trip cost & realized-funding fidelity campaign**. Runner state, gate tokens, anchor status, remaining-cell count, pacing interval, and the exact next command are all printed by:

```bash
bash scripts/next_c25_action.sh
```

**OBEY THE `ACTION:` LINE IT PRINTS.** That is the whole session loop. Everything you need to act (goal start, probe, anchor check, bounded wait, resume-once, mandatory same-session successor launches C26→C32, guardrails, bottleneck register) is in `HANDOFF.md` sections 1–7.

**This is a pointer only.** Read `HANDOFF.md` for full detail, campaign specs, gate tokens, and the complete launch chain. Explicit directions are present for the whole queue `C24 → C25 → C26 → C27 → C28 → C29 → C30 → C31 → C32+`; do not build C33 speculatively (C33 opens only after `C32 ACCEPTANCE: PASS`). No sessions are blocked.
