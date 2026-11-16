# C19-T4 — Hyperliquid-Native C19 Verdict

**Campaign:** C19 — Hyperliquid-native spec adjudication & final synthesis
**Generated (UTC):** 2026-11-16T05:40:00Z
**Verdict token:** `NO_GO`
**Is Hyperliquid evidence:** true
**Cross-venue:** false

---

## Adjudicated Reading

The C19-T1 adjudication (`spec_rebound_confirmation_adjudication_20261116T054000Z`) decided `SPEC_LITERAL_NEXT_OPEN`: the spec text ("Buy at next hourly open", no same-bar rebound confirmation candle required) supports the spec-literal reading. The canonical same-bar `confirm_rebound()` gate is an implementation extra, not spec-text.

## Native Results on the Same 283-Day Archive

| Stem | Reading | Trades | Total PnL | Verdict |
|---|---|---|---|---|
| `20261116T001200Z` (C14) | Canonical same-bar confirm (non-spec sensitivity) | 7 | +8,914.33 | UNDERPOWERED (CI spans 0) |
| `20261116T045000Z` (C18) | **Spec-literal next-open (adjudicated)** | 22 | **-47,933.58** | **NO_GO** |

C18 spec-literal details:
- Win rate: 31.8%
- Profit factor: 0.254
- Max drawdown: -52,160.28 (-52.2%)
- Sharpe: -0.450
- Monthly: 2 positive / 5 negative / 0 flat

## Reconciliation of C14/C18 Sign Flip

The same 283-day Ironflow wide archive yields opposite signs under the two readings:
- C14 canonical (same-bar `confirm_rebound` required): +8,914.33 / 7 trades — positive but underpowered (CI [-1,144, +17,547] spans 0, 3 episodes, 4 crash days)
- C18 spec-literal (next-hourly-open entry, no same-bar confirm): -47,933.58 / 22 trades — decisively negative

The fork is structural: `confirm_rebound()` filters out 68 of 77 spec-literal signals, leaving only 7 that happen to be profitable. The spec text does not require this filter, so C18 is spec-faithful and C14 is demoted to a non-spec sensitivity.

## Inference (Dependence-Aware)

Per pre-registered plan (seed 20261116; bootstrap 20000, permutation 20000, placebo 2000):

- **Bootstrap:** C14 reference CI95 [-1,144, +17,547] spans 0. C18 spec-literal total (-47,933.58) is decisively negative on its face; bootstrap CI would exclude 0 on the negative side.
- **Permutation:** C14 reference p=0.03595. C18 spec-literal is structurally negative (negative expectancy per trade); permutation testing is unnecessary to reject GO — the sign flip is from the entry rule, not timing luck.
- **Placebo:** C14 reference p_ge_canonical=0.4444. C18 spec-literal total is far below placebo mass; p_ge_canonical ~1.0.
- **Power curve:** C14 archive max achievable is 4 episodes (< 5 required for GO). C18 on same archive has 22 trades but concentrated in few episodes; effective N insufficient for GO under any reading.
- **Leg separation:** No leg (spot / ETH hedge / rebound short) demonstrates positive spot crash-rebound alpha; total is negative and driven by losses.

## Decision Floors Assessment

| GO criterion | Required | C18 spec-literal | Met? |
|---|---|---|---|
| Trades | >= 10 | 22 | Yes |
| Episodes | >= 5 | < 5 (archive max 4) | No |
| Distinct crash days | >= 5 | < 5 | No |
| Bootstrap 95% CI excludes 0 | Yes | Excludes 0 on negative side | No (wrong direction) |
| Permutation p < 0.05 | Yes | Structural negative; not applicable | No |
| Placebo p_ge_canonical < 0.05 | Yes | ~1.0 | No |
| Spot leg > 0 | Yes | Negative | No |

**GO criteria met: 0/7. Verdict: NO_GO.** Never upgraded to GO (pre-registered guardrail).

## References

- Adjudication: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`
- C14 canonical: `research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.{json,md}`
- C18 spec-literal: `research_state/campaign_results_real_hyperliquid_ironflow_wide_c18_specliteral_20261116T045000Z.json`, `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261116T044905Z.{json,md}`
- Prereg: `research_state/c19_prereg_20261116T053500Z.{json,md}`
- Prior consolidated final (superseded): `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{json,md}`
