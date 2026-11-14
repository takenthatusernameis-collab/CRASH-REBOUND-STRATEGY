# Power Sensitivity — 2026-11-14T18:28:32Z

**Label:** `NOT_EVIDENCE_POWER_SENSITIVITY` — projections from observed base rates, NOT performance evidence.

Target: **>= 10 independent crash episodes**. Observed traded-episode rate: **0.012355/calendar day** (24 symbols, 161.875 retained days).

| Scenario | Days | λ (expected episodes) | P(N ≥ target) | Cross-venue |
|---|---|---|---|---|
| `a_partial_extended_to_283d_spec_window` | 283 | 3.497 | **0.33%** | False |
| `b_two_year_window_24_symbols` | 730 | 9.019 | **41.51%** | False |
| `c_multi_venue_pooled_hl_plus_okx` | 283 | 7.497 | **22.32%** | True |

## Rate sensitivity (±50% on the traded-episode rate)

- 283d: 0.00% (low) .. 4.16% (high)
- 730d: 1.73% (low) .. 86.64% (high)

## Interpretation

Even the most favourable achievable scenario stays well below even odds of reaching the >=10 independent-episode floor. The 283-day spec window at the observed rate cannot reach the floor; only a multi-year archive or a materially higher episode rate can, and the pooled cross-venue scenario is an upper bound, not evidence.

## Caveats

- Poisson independence is an approximation: crash episodes cluster on shared crash days.
- The traded-episode rate rests on 2 observed episodes; the ±50% band is a diagnostic, not a CI.
- Scenario (c) pools venues and is NOT Hyperliquid evidence.
- No data was fabricated; every input is a committed artifact.

**Verdict:** `POWER_FLOOR_UNREACHABLE_ON_ACHIEVABLE_DATA`
