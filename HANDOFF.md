# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T05:46:00Z  ·  **Last session verified (UTC):** 2026-11-16T08:03:00Z
**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **THIS SESSION (2026-11-16T08:03Z) — CLOSURE RE-VERIFIED, NO FURTHER WORK WARRANTED.**
> Re-confirmed closure state: no new native archive under `research_state/archives/` (latest `hyperliquid_ironflow_wide_20261115T214900Z` already consumed by C14/C18); prior probe artifact `research_state/hyperliquid_retention_probe_next_20261116T054408Z.json` remains `FULL_283D_BLOCKED_BY_API_RETENTION` (`full_window_served=false`, 3849/6792 bars). Re-ran gates: `session_gate.py` **21/21 PASS**, `verify_campaign_evidence.py` **EVIDENCE VERIFIED**, `verify_c19_focus_campaign.py` **C19 ACCEPTANCE: PASS**. `pytest tests/ -q` not re-run this session (last verified 2026-11-16T05:46Z: **1047 passed, 1 skipped**). Decision rule binds: acquisition **CLOSED**, final program verdict **`NO_GO`** (C1–C19). Do **not** open a new campaign, relax the spec, or churn inference on exhausted data.

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T05:46:00Z — CLOSURE)

**Program status: CLOSED.** Consolidated final verdict `NO_GO` for C1–C19 (`research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}`). C19 spec-literal adjudication + native verdict + consolidated final are all done. Research program closed; no validated edge claimed.

**Bounded acquisition precondition — EXECUTED THIS SESSION (do not re-run):**
```bash
PYTHONPATH=. python3 scripts/probe_hyperliquid_blocker.py --limit 10 \
  --out research_state/hyperliquid_retention_probe_next_20261116T054408Z.json --json
ls -1 research_state/archives/
```
**Result (artifact: `research_state/hyperliquid_retention_probe_next_20261116T054408Z.json`, `generated_at_utc 2026-11-16T05:44:15Z`):** probe verdict `FULL_283D_BLOCKED_BY_API_RETENTION` (3,849/6,792 bars served, earliest `2026-04-21`, 2,943 missing early bars; `run_type=hyperliquid_api_retention_probe`, `provenance_caveat` records it as a live public-API probe, not performance evidence). `archives/` contains **no new native archive** — latest is `hyperliquid_ironflow_wide_20261115T214900Z` (already consumed by C14/C18).

**Decision rule outcome (binds all future sessions):** `full_window_served=false` AND no new native archive → **acquisition remains CLOSED.** All gates re-verified green (see below). `NO_GO` is the final program verdict. **No further research work. Do NOT open a new acquisition campaign, do NOT relax the spec, do NOT churn inference on exhausted C14 data.**

### Completed C19 work (do not relitigate)

**C19-T1 — Adjudication: COMPLETE.** `SPEC_LITERAL_NEXT_OPEN` wins. Spec text (`research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`) requires only RSI(21)<20 crash close → buy at next hourly open; no same-bar `confirm_rebound()` gate. Artifact: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}` (`label=NOT_EVIDENCE_SPEC_INTERPRETATION_ADJUDICATION`, `performance_evidence=false`, `decision=SPEC_LITERAL_NEXT_OPEN`, `reconciles_c14_c18=true`, `code_changes_made=false`).

**C19-T2 — Native battery re-run under winning reading: COMPLETE.** The C18 spec-literal campaign (`research_state/campaign_results_real_hyperliquid_ironflow_wide_c18_specliteral_20261116T045000Z.json`) already ran under `entry_spec_literal_next_open=true` on the retained Ironflow wide archive — this IS the re-run under the adjudicated reading. 22 trades, −47,933.58, win rate 31.8%, max DD −52,160. No new acquisition needed (exhausted).

**C19-T3 — Dependence-aware inference + power curve: COMPLETE.** Inference block in C19 native verdict (bootstrap 20000, permutation 20000, placebo 2000, seed 20261116). GO criteria 0/7 met (trades>=10 yes; episodes>=5 no — archive max 4; CI excludes 0 on negative side; permutation structural negative; placebo p_ge~1.0; spot leg negative). Power curve: max achievable 4 episodes < 5 required for GO.

**C19-T4 — C19 native verdict: COMPLETE.** `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}` — token `NO_GO`, `is_hyperliquid_evidence=true`, `cross_venue=false`, references both `20261116T001200Z` (C14) and `20261116T045000Z` (C18), inference block with bootstrap/permutation/placebo.

**C19-T5 — Consolidated final verdict: COMPLETE.** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`, postdates C19 prereg, references C19, `supersedes=decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`.

### Machine-checkable done state (all must hold)

```bash
PYTHONPATH=. python3 scripts/session_gate.py                 # 21/21 checks passed
PYTHONPATH=. python3 scripts/verify_campaign_evidence.py     # evidence verified
PYTHONPATH=. python3 scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS
PYTHONPATH=. python3 scripts/verify_c14_focus_campaign.py    # C14 ACCEPTANCE: PASS
PYTHONPATH=. python3 scripts/verify_c15_focus_campaign.py    # C15 ACCEPTANCE: PASS
PYTHONPATH=. python3 scripts/verify_next_focus_campaign.py   # C6 ACCEPTANCE: PASS
PYTHONPATH=. python3 scripts/verify_c19_focus_campaign.py    # C19 ACCEPTANCE: PASS
PYTHONPATH=. python3 -m pytest tests/ -q                     # all green
```

`scripts/session_gate.py` must report **21/21 checks passed** (Phase O anchor: `research_state/episode_edge_okx_full.json`, `generated_at_utc 2026-11-13T23:38:47Z`). `scripts/verify_campaign_evidence.py` is the anti-avoidance verifier; it must report `evidence verified`. `scripts/verify_c19_focus_campaign.py` must report **C19 ACCEPTANCE: PASS**.

---

## Current state (prioritized, do not relitigate) — FINAL, CLOSED 2026-11-16T05:46Z

1. **Acquisition: CLOSED / exhausted.** C15, C16, C17, C18 all `BLOCKED_EVIDENCED_DATA_REQUIRED`. Live Hyperliquid `candleSnapshot` is a moving tail (`full_window_served=false`, earliest ~`2026-04-21`, ~3,847/6,792 bars). HuggingFace `ironflow/hyperliquid-candles-1h` covers only `2025-05`..`2026-10`. No verified native archive reaches ≥2023-01-01 or adds ≥1 independent crash episode beyond C14. Cross-venue OKX/Binance archives are **not** admissible as native evidence.
2. **Native evidence: underpowered / fragile.** C14 (widest native, 197 symbols / 113 @ $5M, 283d) = 7 trades, 3 episodes, 4 crash days, bootstrap 95% CI [−1,144, +17,547] spans 0, permutation p=0.03595, placebo p=0.4444 → `UNDERPOWERED`. Max achievable from the C14 archive is 4 episodes; first CI exclusion at n=4.
3. **C19 fork: ADJUDICATED — `SPEC_LITERAL_NEXT_OPEN` wins.** Spec text ("Buy at next hourly open", no same-bar confirmation candle) supports spec-literal reading. C18 spec-literal on same archive = 77 signals / 22 trades / **−47,933.58** → `NO_GO`. C14 canonical same-bar = 9 signals / 7 trades / +8,914.33 → demoted to non-spec sensitivity. C19 artifacts complete (see INITIAL TASK MESSAGE).
4. **Cross-venue context (complete, not native).** C6-T1 OKX multi-year campaign + Binance UM multi-year are real and complete; pooled 38 venue-episodes remain underpowered (bootstrap CI spans 0, sign-flip p=0.27/0.54); paired same-sign 32/32 but magnitude CI crosses 0. Context only, `is_hyperliquid_venue_data=false`.
5. **Consolidated final (current):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.md` = `NO_GO` for C1–C19, supersedes `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`.

---

## Bottleneck removal (what changed this session)

- **All bottlenecks cleared and closure executed.** `scripts/session_gate.py` reports **21/21 checks passed** (Phase O anchor `research_state/episode_edge_okx_full.json`, `generated_at_utc 2026-11-13T23:38:47Z`). `scripts/verify_campaign_evidence.py` reports `evidence verified`. `scripts/verify_c19_focus_campaign.py` reports **C19 ACCEPTANCE: PASS**. `pytest tests/ -q`: 1047 passed, 1 skipped. No acceptance gate blocks the next session.
- **The acquisition loop is bounded, not the mission — and it is now CLOSED.** `scripts/probe_hyperliquid_blocker.py` remains the single reproducible retention probe. It was run once this session as the precondition; verdict `FULL_283D_BLOCKED_BY_API_RETENTION`, no new native archive appeared, so acquisition is closed and no new campaign may be opened.
- **C19 focus campaign is complete.** `scripts/verify_c19_focus_campaign.py` reports **C19 ACCEPTANCE: PASS** — all C19-T1..T5 artifacts exist (adjudication, native verdict, consolidated final). The gate no longer blocks.

## Acquisition precondition — CLOSED (executed 2026-11-16T05:46Z, result recorded above)

The decision rule in the INITIAL TASK MESSAGE was applied and resolved to **CLOSED**: `full_window_served=false` AND no new native archive under `research_state/archives/`. The probe artifact is `research_state/hyperliquid_retention_probe_next_20261116T054408Z.json` (generated 2026-11-16T05:44:15Z). No further precondition runs are needed; if an operator later supplies a verified Hyperliquid-native archive, validate it with `scripts/validate_hyperliquid_archive_intake.py` + `scripts/derive_verified_universe.py` before any evidence claim, then fold it into C19-T2.

## Guardrails (never violate)

- No cross-venue relabeling as Hyperliquid-native evidence.
- No synthetic gap-fill presented as verified.
- No spec relaxation to manufacture a GO.
- No inference-only churn on exhausted C14 data; C19 must adjudicate and synthesize.
- No silent change to the canonical baseline; any code change is opt-in, documented, and justified by the adjudication.

## Key files

- Handoff/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C19 prereg: `research_state/c19_prereg_20261116T053500Z.{json,md}`
- C19 adjudication: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}` (decision=SPEC_LITERAL_NEXT_OPEN)
- C19 native verdict: `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}` (token=NO_GO)
- C19 consolidated final: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` (token=NO_GO, supersedes C1-C13 consolidated final)
- C14 native (canonical): `research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.md`
- C18 native (spec-literal): `research_state/campaign_results_real_hyperliquid_ironflow_wide_c18_specliteral_20261116T045000Z.json`, `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261116T044905Z.md`
- Cross-venue C6-T1: `research_state/campaign_results_real_okx_multiyear.json`, `research_state/c6_closeout_20261114T234229Z.md`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

## Session-end requirement — CLOSED (2026-11-16T05:46Z)

This session is complete and the program is closed. The next session's only legitimate action is to re-read this handoff and confirm the closure state; it must **not** open a new campaign, relax the spec, or churn inference on exhausted data. If a future session believes new evidence exists, it must first supply a verified Hyperliquid-native archive under `research_state/archives/` and validate it with `scripts/validate_hyperliquid_archive_intake.py` + `scripts/derive_verified_universe.py` before any evidence claim.

Verification commands (all green as of this session):
- `PYTHONPATH=. python3 scripts/session_gate.py` → **21/21 checks passed**
- `PYTHONPATH=. python3 scripts/verify_campaign_evidence.py` → **evidence verified**
- `PYTHONPATH=. python3 scripts/verify_c19_focus_campaign.py` → **C19 ACCEPTANCE: PASS**
- `PYTHONPATH=. python3 -m pytest tests/ -q` → **1047 passed, 1 skipped**

Final program verdict: **`NO_GO`** for C1–C19. No validated edge claimed.