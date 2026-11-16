# C19-T1 — Spec Rebound Confirmation Adjudication

**Campaign:** C19 — Hyperliquid-native spec adjudication & final synthesis
**Generated (UTC):** 2026-11-16T05:40:00Z
**Label:** NOT_EVIDENCE_SPEC_INTERPRETATION_ADJUDICATION
**Performance evidence:** false (spec interpretation only)

---

## Adjudication Question (Q1)

Does the spec require a same-bar rebound-confirmation candle (canonical `confirm_rebound()` on the signal bar) before the next-open buy, or is the spec-literal reading (RSI(21)<20 close → buy at next hourly open, no same-bar confirmation) the faithful one?

| Reading | Description | Produces |
|---|---|---|
| `SPEC_LITERAL_NEXT_OPEN` | No same-bar rebound confirmation; buy at next hourly open per spec text | C18: 77 signals, 22 trades, −47,933.58 |
| `CANONICAL_SAME_BAR_RETAINED` | Same-bar `confirm_rebound()` required before entry | C14: 9 signals, 7 trades, +8,914.33 |

## Pre-registered Decision Rule

The reading with direct spec-text support wins. No post-hoc switching.

## Spec-Text Findings

1. `research_state/strategy_spec.md` Crash Trigger section: "Signal: coin's **21-hour RSI closes below 20** (last day almost all selling)" and Entry section: "Buy at **next hourly open**". No clause requires a same-bar rebound confirmation candle.
2. `crash-rebound-strategy.pdf`: RSI(21)<20 crash close → buy at next hourly open. No same-bar `confirm_rebound` gate.
3. `confirm_rebound()` in `src/strategy/crash_rebound.py:288` is an implementation addition not present in the spec text. It is gated behind `entry_spec_literal_next_open=False` by default, preserving the canonical baseline.
4. The spec-literal reading (buy at next hourly open after RSI(21)<20 close, no same-bar confirmation) is directly supported by the spec text. The canonical same-bar reading is an implementation extra.

## Decision

**`SPEC_LITERAL_NEXT_OPEN` wins.** Direct spec-text support ("Buy at next hourly open" with no same-bar confirmation requirement) favors the spec-literal reading.

## Consequence

Per the pre-registered decision rule, the native verdict is **NO_GO** (C18: 22 trades, −47,933.58 on the same 283-day Ironflow wide archive). C14 same-bar result (+8,914.33, 7 trades) is demoted to a non-spec sensitivity — not evidence.

## Code Changes

`code_changes_made: false` — no code changes. The opt-in `entry_spec_literal_next_open` flag already exists in `src/strategy/config.py` and is honored in `src/strategy/crash_rebound.py:441`. No modification to the canonical baseline.

## References

- Prereg: `research_state/c19_prereg_20261116T053500Z.{json,md}`
- C14 canonical: `research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json`, `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.{json,md}`
- C18 spec-literal: `research_state/campaign_results_real_hyperliquid_ironflow_wide_c18_specliteral_20261116T045000Z.json`, `research_state/hyperliquid_signal_funnel_exploratory_next_open_20261116T044905Z.{json,md}`
- Prior consolidated final: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{json,md}`
