# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T10:08:00Z  ·  **Last session verified (UTC):** 2026-11-16T10:05:03Z
**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

> **PROGRAM STATE: C1–C19 CLOSED (final verdict `NO_GO`) · C20 IS THE NEXT FOCUS CAMPAIGN — NOT OPTIONAL.**
> C1–C19 closure re-confirmed 2026-11-16T10:05Z: acquisition CLOSED (`FULL_283D_BLOCKED_BY_API_RETENTION`, no new native archive under `research_state/archives/` beyond `hyperliquid_ironflow_wide_20261115T214900Z`), C19 adjudication `SPEC_LITERAL_NEXT_OPEN` wins, native C18 spec-literal = 22 trades / −47,933.58 / NO_GO, consolidated final `NO_GO` (C1–C19). Gates: `session_gate.py` **21/21 checks passed** (Phase O anchor: `research_state/episode_edge_okx_full.json`, `generated_at_utc 2026-11-13T23:38:47Z`), `verify_campaign_evidence.py` **EVIDENCE VERIFIED**, `verify_c19_focus_campaign.py` **C19 ACCEPTANCE: PASS**, `pytest tests/ -q` **1032 passed, 12 skipped, 4 failed (pandas dep, non-blocking)**.
>
> **The C1–C19 verdict is final and must not be relitigated. The next session's binding work is C20.**

---

## INITIAL TASK MESSAGE — NEXT SESSION (2026-11-16T10:08Z — EXECUTE C20 FOCUS CAMPAIGN)

**Program status: C1–C19 closed (`NO_GO`). C20 preregistered 2026-11-16T06:35:00Z (`PRE_REGISTERED_BEFORE_COMPUTE`) but compute NOT yet executed — this is the binding next focus campaign.** C20 runs the C19-adjudicated spec-faithful entry rule (`SPEC_LITERAL_NEXT_OPEN`, `entry_spec_literal_next_open=true`) on both independent multi-year cross-venue archives (OKX + Binance UM, 2023-01-01..2026-09-28, 32808 bars/symbol) with the full dependence-aware battery, then issues one cross-venue verdict plus a pooled venue-blocked synthesis and a consolidated C1–C20 final. OKX campaign+census artifacts already exist; Binance UM + all inference artifacts are missing. Acquisition stays closed — C20 is executable on already-verified real archives; no new data acquisition.

**Next session — do exactly this, in order:**

1. Re-read `HANDOFF.md`; do **not** re-open C1–C19 acquisition, relax the spec, or churn inference on exhausted C14 native data.
2. Execute C20 end-to-end on already-verified caches:
   ```bash
   PYTHONPATH=. python3 scripts/run_c20_cross_venue_campaign.py --venues okx binance_um --jobs 4 --resume
   ```
   `--resume` skips steps whose artifacts already exist (OKX campaign+census are done); Binance UM campaign+census + both episode edges + both placebos + both batteries + both per-venue verdicts + pooled synthesis + consolidated final must be produced.
3. Verify completion: `PYTHONPATH=. python3 scripts/verify_c20_focus_campaign.py` must report **C20 ACCEPTANCE: PASS** (all 15 requirements).
4. Gate hygiene (expected green): `PYTHONPATH=. python3 scripts/session_gate.py` (21/21), `PYTHONPATH=. python3 scripts/verify_campaign_evidence.py`, `PYTHONPATH=. python3 scripts/verify_c19_focus_campaign.py`, `PYTHONPATH=. python3 -m pytest tests/ -q`.
5. If C20 completes with an honest verdict (`GO`, `UNDERPOWERED`, or `NO_GO` with quantified power curve), update `HANDOFF.md` to reflect the new consolidated final `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.{json,md}` and mark C20 complete. Otherwise the C20 focus campaign is the ongoing heavy-work obligation until all 15 acceptance requirements pass.

**Bounded acquisition precondition — remains CLOSED (executed 2026-11-16T05:46Z):**
```bash
PYTHONPATH=. python3 scripts/probe_hyperliquid_blocker.py --limit 10 \
  --out research_state/hyperliquid_retention_probe_next_20261116T054408Z.json --json
```
**Result:** `FULL_283D_BLOCKED_BY_API_RETENTION` (3,849/6,792 bars served, earliest `2026-04-21`, 2,943 missing early bars). `archives/` contains no new native archive — latest is `hyperliquid_ironflow_wide_20261115T214900Z` (consumed by C14/C18). Acquisition stays CLOSED; C20 uses OKX + Binance UM only (`is_hyperliquid_venue_data=false`) and must never be relabeled as Hyperliquid performance evidence.

---

## C1–C19 CLOSED STATE (historical context, do not relitigate)

**Consolidated final (C1–C19):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`, supersedes `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`. No validated edge claimed.

**Completed C19 work (do not relitigate):**
- **C19-T1 Adjudication: COMPLETE.** `SPEC_LITERAL_NEXT_OPEN` wins (spec text: RSI(21)<20 crash close → buy at next hourly open; no same-bar `confirm_rebound()` gate). Artifact: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`.
- **C19-T2 Native battery re-run: COMPLETE.** C18 spec-literal on Ironflow wide archive = 22 trades, −47,933.58, win rate 31.8%, max DD −52,160. NO_GO under adjudicated reading.
- **C19-T3 Dependence-aware inference + power curve: COMPLETE.** 0/7 GO criteria met; max achievable 4 episodes < 5 required.
- **C19-T4 Native verdict: COMPLETE.** `decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}` — token `NO_GO`, `is_hyperliquid_evidence=true`, `cross_venue=false`.
- **C19-T5 Consolidated final: COMPLETE.** `decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}` — token `NO_GO`.

**Current state (prioritized, FINAL, CLOSED 2026-11-16T05:46Z):**
1. Acquisition: CLOSED / exhausted. Live Hyperliquid `candleSnapshot` moving tail (`full_window_served=false`, earliest ~`2026-04-21`). No verified native archive ≥2023-01-01 or adding ≥1 independent crash episode beyond C14. Cross-venue OKX/Binance are **not** admissible as native evidence.
2. Native evidence: underpowered / fragile. C14 = 7 trades, 3 episodes, bootstrap CI spans 0; max achievable 4 episodes < 5 GO floor.
3. C19 fork: `SPEC_LITERAL_NEXT_OPEN` wins; C18 spec-literal NO_GO decisively negative; C14 canonical same-bar demoted to non-spec sensitivity (+8,914.33 / 7 trades).
4. Cross-venue context (complete, not native): C6 OKX + Binance UM multi-year pooled 38 venue-episodes underpowered (CI spans 0). Context only, `is_hyperliquid_venue_data=false`.
5. Consolidated final: `NO_GO` for C1–C19.

---

## C20 FOCUS CAMPAIGN — MISSING ARTIFACTS (heavy work, must not be avoided)

Prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}` — `PRE_REGISTERED_BEFORE_COMPUTE`, config fixed (`entry_spec_literal_next_open=true`, RSI(21)<20, target 9%, ETH hedge on, $5M volume gate, seed 20261120). **No config switching after results.**

Already present (do not regenerate unless resuming):
- `campaign_results_real_okx_multiyear_specliteral_20261116T063500Z.json` (+ `_metrics.json`)
- `crash_event_census_real_okx_multiyear_specliteral_20261116T063500Z.json`

**Missing — the next session must produce all of these:**
| # | Artifact (stem `20261116T063500Z`) | Status |
|---|---|---|
| 1 | `campaign_results_real_binance_um_multiyear_specliteral` | MISSING |
| 2 | `crash_event_census_real_binance_um_multiyear_specliteral` | MISSING |
| 3 | `episode_edge_okx_multiyear_specliteral` | MISSING |
| 4 | `episode_edge_binance_um_multiyear_specliteral` | MISSING |
| 5 | `placebo_portfolio_okx_multiyear_specliteral` | MISSING |
| 6 | `placebo_portfolio_binance_um_multiyear_specliteral` | MISSING |
| 7 | `multiyear_robustness_battery_okx_specliteral` | MISSING |
| 8 | `multiyear_robustness_battery_binance_um_specliteral` | MISSING |
| 9 | `decision_verdict_cross_venue_okx_specliteral_c20` | MISSING |
| 10 | `decision_verdict_cross_venue_binance_um_specliteral_c20` | MISSING |
| 11 | `c20_pooled_cross_venue_synthesis` | MISSING |
| 12 | `decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z` | MISSING |

**C20 acceptance gate:** `scripts/verify_c20_focus_campaign.py` — fail-closed, all 15 requirements must pass (prereg + both venue campaigns + both censuses + both episode edges + both placebos + both batteries + both verdicts + pooled synthesis + consolidated final + handoff reference).

**C20 decision rules (from prereg):** GO only if pooled synthesis has episode-block bootstrap 95% CI excluding 0 with positive spot leg, permutation p<0.05, placebo p_ge_canonical<0.05, and ≥10 trades / ≥5 episodes / ≥5 crash days. Otherwise verdict `UNDERPOWERED` or `NO_GO` with a quantified power curve. C20 is cross-venue (`is_hyperliquid_venue_data=false`) — never Hyperliquid performance evidence.

---

## Bottleneck removal (what this session set up)

- **C20 was preregistered but never computed — the single biggest bottleneck.** `scripts/run_c20_cross_venue_campaign.py` orchestrates the full 8-step pipeline per venue (campaign, census, episode dependence audit, conditional permutation, placebo, robustness battery, per-venue verdict, pooled synthesis + consolidated final) with `--resume` for crash recovery. OKX half is already on disk; Binance UM is the missing half.
- **Missing acceptance gate created:** `scripts/verify_c20_focus_campaign.py` (fail-closed, 15 checks) so future agents cannot mark C20 done without the full artifact set.
- **HANDOFF.md now points at C20** (`verify_c20_focus_campaign.py` referenced, C20-T1 initial task message). No acceptance gate blocks the next session.

## Guardrails (never violate)

- No cross-venue relabeling as Hyperliquid-native evidence (`is_hyperliquid_venue_data=false` for all C20 artifacts).
- No synthetic gap-fill presented as verified.
- No spec relaxation to manufacture a GO; `SPEC_LITERAL_NEXT_OPEN` is the fixed C20 reading (default `entry_spec_literal_next_open=false` in canonical baseline — opt-in only).
- No inference-only churn on exhausted C14 native data; C19 adjudicated and closed.
- No silent change to the canonical baseline; any code change is opt-in, documented, justified.
- C1–C19 `NO_GO` verdict stands unless C20 produces a new consolidated final superseding it.

## Key files

- Handover/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C20 prereg: `research_state/c20_prereg_20261116T063500Z.{json,md}`
- C20 runner: `scripts/run_c20_cross_venue_campaign.py` (TS `20261116T063500Z`, seed `20261120`)
- C20 gate: `scripts/verify_c20_focus_campaign.py` (15 requirements, fail-closed)
- C19 artifacts (reference only): `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`, `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}`, `research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T054500Z.{json,md}`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`, `scripts/verify_c19_focus_campaign.py`, `scripts/verify_c20_focus_campaign.py`
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

## Session-end requirement — C20 IN PROGRESS (2026-11-16T10:08Z)

C1–C19 is closed. The next session's only legitimate initial task is to **execute C20 end-to-end** (`run_c20_cross_venue_campaign.py --resume` on OKX + Binance UM) and reach **C20 ACCEPTANCE: PASS** via `verify_c20_focus_campaign.py`. It must **not** re-open C1–C19 acquisition, relax the spec, or churn inference on exhausted C14 data. If a future session believes a new Hyperliquid-native archive exists, it must first validate it with `scripts/validate_hyperliquid_archive_intake.py` + `scripts/derive_verified_universe.py` before any evidence claim.

Verification commands (green as of C1–C19 closure; C20 gate is the new obligation):
- `PYTHONPATH=. python3 scripts/session_gate.py` → **21/21 checks passed**
- `PYTHONPATH=. python3 scripts/verify_campaign_evidence.py` → **evidence verified**
- `PYTHONPATH=. python3 scripts/verify_c19_focus_campaign.py` → **C19 ACCEPTANCE: PASS**
- `PYTHONPATH=. python3 scripts/verify_c20_focus_campaign.py` → **C20 ACCEPTANCE: PASS** (pending C20 compute)
- `PYTHONPATH=. python3 -m pytest tests/ -q` → **1032 passed, 12 skipped, 4 failed (pandas dep)**

Final program verdict C1–C19: **`NO_GO`**. C20 verdict pending — execute the campaign.

(End of file)
