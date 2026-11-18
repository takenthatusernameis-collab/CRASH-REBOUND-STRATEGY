# INITIAL TASK MESSAGE (POINTER) — 2026-11-18T07:12:11Z

**Single durable handoff / source of truth:** `HANDOFF.md` — read it in full before acting. Do not maintain a second source of truth here.

**Repo:** `CRASH-REBOUND-STRATEGY` (crash-rebound edge adjudication, OKX + Binance UM). C1–C20 CLOSED `NO_GO`; **C21-T1 COMPLETE** (`C21 ACCEPTANCE: PASS`, consolidated `NO_GO`, 12/12 artifacts, 8/8 checkpoints, 2026-11-18T06:15:08Z). No active runner. No uncommitted changes (HEAD `d35fda6`).

**Verified (2026-11-18T07:12:11Z):** `verify_c21_focus_campaign.py` → `C21 ACCEPTANCE: PASS`; `pytest tests/ -q` = `1047 passed, 1 skipped`; `session_gate.py` = `21/21 checks passed` (Phase O `2026-11-13T23:38:47Z`); `verify_campaign_evidence.py` = `EVIDENCE VERIFIED`; `probe_hyperliquid_blocker.py` = `FULL_283D_BLOCKED_BY_API_RETENTION` (acquisition CLOSED/exhausted).

**Next action (verify then stop):** (1) confirm `C21 ACCEPTANCE: PASS` + 12 artifacts / 8 ckpts + no runner. (2) **Await explicit operator direction** — no heavy execution authorized on current data. Do NOT relitigate C1–C21, relaunch C20, invent a same-data C22+ rerun, reduce draw counts, or commit unless asked. Any work beyond C21 requires new prereg + new data + explicit operator authorization.

Full binding spec, guardrails, tokens, file map: `HANDOFF.md`.