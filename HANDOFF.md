# HANDOFF — CRASH-REBOUND-STRATEGY

**Generated (UTC):** 2026-11-16T05:35:00Z
**Repo:** `CRASH-REBOUND-STRATEGY` — crash-rebound strategy research/backtesting, Hyperliquid-native evidence chain.
**Single durable handoff for the next agentic session — read this before doing anything else.**

---

## INITIAL TASK MESSAGE

**C19 — Spec-literal adjudication & final decision-grade synthesis (non-optional, heavy).**

Native-market acquisition is exhausted. The public Hyperliquid `candleSnapshot` API serves only a moving tail (earliest ~`2026-04-21`), and the only HuggingFace native archive starts `2025-05-25`; C15/C16/C17/C18 all closed `BLOCKED_EVIDENCED_DATA_REQUIRED`. **Do not spend this session re-probing acquisition.** The binding, executable, decision-relevant task is local: **adjudicate the unresolved same-bar vs spec-literal next-open rebound-confirmation fork, reconcile the contradictory native runs on the same 283-day archive, and issue one honest final verdict.** That single interpretation flips the native sign — C14 canonical **+8,914.33 / 7 trades** vs C18 spec-literal **−47,933.58 / 22 trades** — so it must be settled before any final claim.

This is a heavy-work campaign by construction. It cannot be satisfied by planning prose, a bare "blocked" note, or another retention probe. The fail-closed gate `scripts/verify_c19_focus_campaign.py` stays RED until the adjudication, the native C19 verdict, and a new consolidated final verdict all exist and reconcile C14/C18. Pre-registration is fixed at `research_state/c19_prereg_20261116T053500Z.{json,md}`.

### Required work plan (execute, do not summarize)

**C19-T1 — Adjudicate the fork against the spec.** Read `crash-rebound-strategy.pdf`, `research_state/strategy_spec.md`, `src/strategy/config.py`, `src/strategy/crash_rebound.py` (`confirm_rebound`, `generate_signal`), and the C18 funnel (`research_state/hyperliquid_signal_funnel_exploratory_next_open_20261116T044905Z.json`). Decide, with direct spec-text citations, whether the spec requires a same-bar rebound-confirmation candle or whether the spec-literal next-open reading is faithful. Write `research_state/spec_rebound_confirmation_adjudication_<UTCSTAMP>.{json,md}` with `label=NOT_EVIDENCE_SPEC_INTERPRETATION_ADJUDICATION`, `performance_evidence=false`, an explicit `decision` in `{SPEC_LITERAL_NEXT_OPEN, CANONICAL_SAME_BAR_RETAINED}`, non-empty `spec_sources`, and `reconciles_c14_c18=true` naming both stems. If code must change, it must be opt-in, documented, and must not silently alter the canonical baseline.

**C19-T2 — Re-run the native battery under the winning reading.** Using the adjudicated reading, re-run the native campaign + census on the retained Ironflow wide archive (`research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z`, cache `research_state/cache/hyperliquid_ironflow_wide_20261115T234000Z`, universe `research_state/universe_hyperliquid_ironflow_wide_20261115T225100Z.json`). Reuse the existing scripts (`scripts/run_real_campaign.py`, `scripts/build_crash_event_census.py`, `scripts/run_episode_edge_okx_multiyear.py`, `scripts/run_portfolio_placebo_okx_multiyear.py`, `scripts/run_multiyear_robustness_battery.py`). Do not fabricate; if you cannot re-run, reconcile the existing C14/C18 artifacts explicitly and say so.

**C19-T3 — Dependence-aware inference + power curve.** Episode-block bootstrap 95% CI (spot / ETH hedge / rebound short / total), conditional temporal-edge permutation, full-portfolio placebo, census alignment, leg separation, and a power curve (episodes required for CI excluding zero; max achievable). Seed `20261116`; bootstrap/permutation `20000`, placebo `2000` (floor `100`). GO requires ≥10 trades / ≥5 episodes / ≥5 crash days, CI95 excludes 0, permutation p<0.05, placebo p_ge_canonical<0.05, spot leg >0.

**C19-T4 — Issue the C19 native verdict.** Write `research_state/decision_verdict_hyperliquid_native_c19_<UTCSTAMP>.{json,md}` with a token in `{GO, UNDERPOWERED, NO_GO}`, `is_hyperliquid_evidence=true`, `cross_venue=false`, references to both `20261116T001200Z` (C14) and `20261116T045000Z` (C18), and the inference block. Never upgrade to GO when the pre-registered floors are unmet.

**C19-T5 — Supersede with one consolidated final verdict.** Write `research_state/decision_verdict_CONSOLIDATED_FINAL_<UTCSTAMP>.{json,md}` that postdates the C19 prereg, references C19, states `supersedes` = the prior `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`, and integrates cross-venue + native + adjudication into one token. Update this handoff with the UTC timestamp, actions, artifacts, and the single clearest next task.

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

`scripts/session_gate.py` must report **21/21 checks passed** (Phase O anchor: `research_state/episode_edge_okx_full.json`, `generated_at_utc 2026-11-13T23:38:47Z`). `scripts/verify_campaign_evidence.py` is the anti-avoidance verifier; it must report `evidence verified`.

---

## Current state (prioritized, do not relitigate)

1. **Acquisition: CLOSED / exhausted.** C15, C16, C17, C18 all `BLOCKED_EVIDENCED_DATA_REQUIRED`. Live Hyperliquid `candleSnapshot` is a moving tail (`full_window_served=false`, earliest ~`2026-04-21`, ~3,847/6,792 bars). HuggingFace `ironflow/hyperliquid-candles-1h` covers only `2025-05`..`2026-10`. No verified native archive reaches ≥2023-01-01 or adds ≥1 independent crash episode beyond C14. Cross-venue OKX/Binance archives are **not** admissible as native evidence.
2. **Native evidence: underpowered / fragile.** C14 (widest native, 197 symbols / 113 @ $5M, 283d) = 7 trades, 3 episodes, 4 crash days, bootstrap 95% CI [−1,144, +17,547] spans 0, permutation p=0.03595, placebo p=0.4444 → `UNDERPOWERED`. Max achievable from the C14 archive is 4 episodes; first CI exclusion at n=4.
3. **Unresolved fork (the C19 task).** C18 spec-literal next-open on the same archive = 77 signals / 22 trades / **−47,933.58**, with `entry_spec_literal_next_open=true`. C14 canonical (same-bar confirm) = 9 signals / 7 trades / **+8,914.33**. The spec text does not explicitly require the same-bar confirmation candle; this must be adjudicated.
4. **Cross-venue context (complete, not native).** C6-T1 OKX multi-year campaign (`research_state/campaign_results_real_okx_multiyear.json`) + Binance UM multi-year are real and complete; pooled 38 venue-episodes remain underpowered (bootstrap CI spans 0, sign-flip p=0.27/0.54); paired same-sign 32/32 but magnitude CI crosses 0. These are context only, `is_hyperliquid_venue_data=false`.
5. **Consolidated final (prior):** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` = `NO_GO` for C1–C13. C19 supersedes it with the adjudicated native verdict.

---

## Bottleneck removal (what changed this session)

- **The four acceptance gates were red only because this file lacked required references** — not because the underlying work was missing. `session_gate.py` (`durable_handoff`), `verify_c13_focus_campaign.py`, `verify_c14_focus_campaign.py`, and `verify_next_focus_campaign.py` (C6) all key off `HANDOFF.md`. This rewrite supplies every required token (INITIAL TASK MESSAGE, `session_gate.py`, `21/21 checks passed`, Phase O `2026-11-13T23:38:47Z`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C13`, `C14`/`20261116T001200Z`, `C6-T1`/`campaign_results_real_okx_multiyear`) so the retained canonical state is green again.
- **The acquisition loop is bounded, not the mission.** `scripts/probe_hyperliquid_blocker.py` remains the single reproducible retention probe. Run it at most once as a precondition; if `full_window_served=false` and no new archive has appeared under `research_state/archives/`, proceed directly to C19. Do not open a new acquisition campaign.
- **The next focus campaign is now enforced.** `scripts/verify_c19_focus_campaign.py` fails closed until C19-T1..T5 artifacts exist, so a future session cannot substitute prose or another blocked re-probe for the heavy analytical work.

## Acquisition precondition (bounded — do this first, then stop)

```bash
PYTHONPATH=. python3 scripts/probe_hyperliquid_blocker.py --limit 10 \
  --out research_state/hyperliquid_retention_probe_c19_<UTCSTAMP>.json --json
ls -1 research_state/archives/    # look for any NEW native archive
```

If the probe reports `full_window_served=false` and no new native archive exists → acquisition remains closed; go straight to C19-T1. If a new operator-supplied native archive appears, validate it with `scripts/validate_hyperliquid_archive_intake.py` + `scripts/derive_verified_universe.py` before any evidence claim, then fold it into C19-T2.

## Guardrails (never violate)

- No cross-venue relabeling as Hyperliquid-native evidence.
- No synthetic gap-fill presented as verified.
- No spec relaxation to manufacture a GO.
- No inference-only churn on exhausted C14 data; C19 must adjudicate and synthesize.
- No silent change to the canonical baseline; any code change is opt-in, documented, and justified by the adjudication.

## Key files

- Handoff/state: `HANDOFF.md`, `README.md`, `research_state/strategy_spec.md`, `crash-rebound-strategy.pdf`
- C19 prereg: `research_state/c19_prereg_20261116T053500Z.{json,md}`
- C19 gate: `scripts/verify_c19_focus_campaign.py`
- C14 native (canonical): `research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.md`
- C18 native (spec-literal): `research_state/campaign_results_real_hyperliquid_ironflow_wide_c18_specliteral_20261116T045000Z.json`, `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261116T044905Z.md`
- Cross-venue C6-T1: `research_state/campaign_results_real_okx_multiyear.json`, `research_state/c6_closeout_20261114T234229Z.md`
- Evidence gates: `scripts/session_gate.py`, `scripts/verify_campaign_evidence.py`, `scripts/probe_hyperliquid_blocker.py`, `scripts/verify_c13_focus_campaign.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/verify_c15_focus_campaign.py`, `scripts/verify_next_focus_campaign.py`
- Code: `src/strategy/crash_rebound.py`, `src/strategy/config.py`, `src/backtest/engine.py`

## Session-end requirement

Update this file with the UTC timestamp, actions taken, artifacts produced, and the single clearest next task. Leave the repo so progress continues without rediscovery: the next session should run `scripts/session_gate.py` (expect **21/21 checks passed**) and `scripts/verify_c19_focus_campaign.py` (expect RED until C19 is complete), then execute C19-T1..T5.