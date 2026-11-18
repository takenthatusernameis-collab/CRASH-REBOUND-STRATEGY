# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T07:14:23Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication, OKX + Binance UM). C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`, 12/12 artifacts, 8/8 checkpoints, 2026-11-18T06:15:08Z). **C22-T1 (Binance UM 283d full battery) is the binding next focus campaign — PREREGISTERED, SCRIPTED, AND AUTHORIZED FOR HEAVY EXECUTION.**

**Verified (2026-11-18T07:14:23Z):** `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`; `pytest tests/ -q` = `1047 passed, 1 skipped`; `session_gate.py` = `21/21 checks passed` (Phase O `2026-11-13T23:38:47Z`); `verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION` (acquisition CLOSED/exhausted). Working tree clean at HEAD `cd6ff5d`.

**Next action — execute C22-T1 (heavy, authorized):** build and run the Binance UM 283d full battery (placebo + walkforward + risk budget + robustness stress), plus fix the stale percode artifact. Full spec, guardrails, tokens, file map: `HANDOFF.md`.