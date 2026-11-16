# C15 Decision Verdict — Hyperliquid-native window extension

- **Generated (UTC):** 2026-11-16T02:40:01Z
- **Verdict:** **`BLOCKED_EVIDENCED_DATA_REQUIRED`** (not GO/NO_GO/UNDERPOWERED re-adjudication; T2 battery not executable without extended native evidence)
- **Performance evidence:** false. Hyperliquid-native basis preserved; no cross-venue relabeling.

## Outcome
- **T1 executed (evidenced):** HuggingFace `ironflow/hyperliquid-candles-1h` probe (rows 3,641,742; **2025-05-25T14:00:00Z..2026-10-31T23:00:00Z**; covers 283d spec window, **cannot reach ≥2023-01-01**; same source as C14 widest archive) + live API retention probe (`hyperliquid_retention_probe.json`, earliest served 2026-04-21T15:00:00Z, 3849/6792 bars, moving tail). See `research_state/c15_acquisition_attempt_20261116T024001Z.md` / `.json`.
- **T2:** not executed — no extended verified Hyperliquid-native archive acquirable to add independent episodes.
- **T3:** evidenced hard blocker filed with data request stem `research_state/c15_data_request_stem_20261116T024001Z.md`.

## Anchor (unchanged)
- C14: `UNDERPOWERED` — 3 episodes / 4 crash days / 7 trades; bootstrap 95% CI [−1144,+17547] spans zero (first exclusion n=4); permutation p=0.03595; placebo p=0.4444 (`research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.json`).
- Consolidated FINAL (C1–C13): `NO_GO` (`research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`). Canonical C1–C14 artifacts unchanged.

## Gates
- `session_gate.py`: 21/21 checks passed
- `verify_c14_focus_campaign.py`: C14 ACCEPTANCE: PASS
- `verify_campaign_evidence.py`: 4/4 EVIDENCE VERIFIED

*Not a bare "closed/no work" outcome: T1 attempted with command-level evidence; blocker documented; explicit data request provided.*
