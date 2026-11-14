# Hyperliquid partial signal funnel — EXPLORATORY NEXT-OPEN ADJUDICATION

Label: **NOT_EVIDENCE_EXPLORATORY_FANOUT** | performance_evidence: **false** | canonical_baseline_changed: **false**

Cache: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z`
Generated: 2026-11-14T15:01:40Z

| Metric | Count |
|---|---|
| symbols | 24 |
| bars_total | 93240 |
| rsi_crash_hours_no_volume_gate | 29 |
| rsi_crash_hours_passing_trailing_24h_5m_volume (upper bound spec-literal entries) | 11 |
| same_bar_rebound_confirm (implementation) | 0 |
| next_bar_rebound_confirm (implementation) | 5 |
| generate_signal_confirmed (canonical) | 0 |
| spec_literal_next_open_entry_opportunities_after_volume_passing_crash (upper bound) | 11 |

## Adjudication
- **implementation_path:** Canonical implementation requires same-bar rebound confirmation (`confirm_rebound`) before `generate_signal`; retained funnel shows 0 same-bar confirmations and 0 `generate_signal` entries on 11 volume-passing RSI crash hours.
- **spec_literal_path:** Spec states buy at next hourly open after RSI(21)<20 crash close (no same-bar confirmation gate). Upper bound admits 11 next-open opportunities vs 0 canonical entries.
- **additional_admitted_crash_hours_vs_same_bar_confirm:** 11
- **next_bar_rebound_confirm_observed:** 5
- **structural_note:** 0-trade partial result is structurally explained by the same-bar confirmation filter blocking all 11 volume-passing crash hours in this retained window; spec-literal next-open path has a nonzero upper bound (11) but full portfolio constraints/sizing/cap/downstream exits are not evaluated. Canonical baseline remains unchanged and unvalidated.

Real Hyperliquid public-API candles, non-synthetic; PARTIAL aligned window; NOT the 283-day spec window and NOT performance evidence. Do not overwrite canonical campaign, do not claim validation, do not allocate capital.
