# Consolidated Final Decision Verdict — CRASH-REBOUND-STRATEGY (C1–C19)

**Generated (UTC):** 2026-11-16T05:45:00Z
**Scope:** Final consolidation of all completed campaigns C1–C19 (cross-venue and Hyperliquid-native). This verdict supersedes `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`.
**Final verdict token:** `NO_GO` (no GO claim from any campaign)

This verdict synthesizes prior decision-grade artifacts plus the C19 spec adjudication and native verdict; it does **not** relabel cross-venue evidence as Hyperliquid evidence, does **not** claim a validated edge, and does **not** introduce new data or reruns beyond the C18 spec-literal campaign already executed on the retained archive.

---

## C19 — Spec Adjudication & Native Verdict (binding update)

**Adjudication (C19-T1):** `SPEC_LITERAL_NEXT_OPEN` wins on direct spec-text support. `research_state/strategy_spec.md` states "Signal: coin's 21-hour RSI closes below 20" and "Buy at next hourly open" — no same-bar rebound confirmation candle is required. The canonical `confirm_rebound()` gate in `src/strategy/crash_rebound.py:288` is an implementation extra, gated behind `entry_spec_literal_next_open=False` by default (canonical baseline preserved).

**Native verdict (C19-T4):** `NO_GO`. On the adjudicated spec-faithful reading, the C18 spec-literal campaign on the same 283-day Ironflow wide archive yields 22 trades, −47,933.58 total PnL, win rate 31.8%, profit factor 0.254, max drawdown −52,160.28. GO criteria 0/7 met. C14 canonical same-bar (+8,914.33, 7 trades, UNDERPOWERED) is demoted to a non-spec sensitivity.

**Artifacts:**
- Adjudication: `research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.{json,md}`
- Native verdict: `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.{json,md}`

---

## 1. Traceability — referenced prior verdict/artifact stems

| Campaign / scope | Verdict stem (filename) | Verdict token / outcome |
|---|---|---|
| Cross-venue consolidated (C1–C10, OKX + Binance UM) | `research_state/decision_verdict_consolidated_20261115T122636Z.md` | **`NO_GO`** (0/7); `is_hyperliquid_venue_data=false` |
| Native canonical (C11.3, Hyperliquid-native, `RSI(21)<20`) | `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md` | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE`** (0/7) |
| Native consolidated (C11.3 context) | `research_state/decision_verdict_consolidated_20261115T155318Z.md` | Consolidated native context (canonical NO_GO preserved) |
| Native C12 (discovery/grid, Hyperliquid-native) | `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` | **`NO_DECISION_GRADE_GO`** (discovery only; not validated) |
| Native C13 (pre-registered validation of C12 lead) | `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md` | **`UNDERPOWERED`** (GO criteria unmet) |
| Native C14 (canonical same-bar, Hyperliquid-native) | `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.md` | **`UNDERPOWERED`** (CI spans 0; demoted to non-spec sensitivity per C19) |
| Native C18 (spec-literal next-open, Hyperliquid-native) | `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.md` | **`NO_GO`** (adjudicated spec-faithful reading; −47,933.58 / 22 trades) |
| C19 consolidated native final | `research_state/decision_verdict_hyperliquid_native_c19_20261116T054000Z.md` | **`NO_GO`** |

**Supersedes:** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{json,md}` (token `NO_GO`, C1–C13 scope).

---

## 2. Synthesized dependence-aware evidence (all campaigns)

### 2.1 Cross-venue (C1–C10, OKX & Binance UM) — NOT Hyperliquid evidence
**Verdict:** `NO_GO` (0/7 stop/go criteria pass). Source: `decision_verdict_consolidated_20261115T122636Z.md`.
- Pooled 38 independent venue-episodes — observed total +40,214.92; episode-block bootstrap 95% CI **[−69,065.03, +168,946.87]** (spans 0), P(total>0)=0.74095; sign-flip permutation p(one-sided)=0.26955 → underpowered.
- Placebo: OKX p=0.40; Binance p=0.4150 — no separation from gate-passing pool.
- Cross-venue agreement: paired same-sign 32/32 but magnitude CI crosses 0; directional replication only, not edge sufficiency.

### 2.2 Hyperliquid-native canonical C11.3 / C13 / C14 / C18
**C11.3 canonical (`RSI(21)<20`):** `NO_GO` / underpowered, 0/7. 6 trades / 3 episodes / 4 crash days. Bootstrap CI95 [−1,143.66, +10,339.42] spans 0; permutation p=0.0800; placebo p_ge=0.7143. Spot PnL −3,968.80; ETH hedge +8,261.31 (hedge-manufactured total).

**C13 validation of C12 lead (`rsi25_target9`):** `UNDERPOWERED`. 17 trades / 10 episodes / 12 crash days. Bootstrap CI95 [−22,799.52, +79,978.91] spans 0; permutation p=0.085; placebo p_ge=0.32. Spot leg negative.

**C14 canonical same-bar (non-spec sensitivity per C19):** `UNDERPOWERED`. 7 trades / 3 episodes / 4 crash days. Total +8,914.33 but bootstrap CI95 [−1,144, +17,547] spans 0; placebo p_ge=0.4444. Same-bar `confirm_rebound` is an implementation extra, not spec-text — demoted.

**C18 spec-literal next-open (adjudicated spec-faithful):** `NO_GO`. 22 trades / total −47,933.58 / win rate 31.8% / max DD −52,160. Decisively negative on its face.

### 2.3 Native C12 (discovery grid)
**Verdict:** `NO_DECISION_GRADE_GO` (discovery only). Best lead `c12_25_9` total +23,244.22 but bootstrap CI95 [−36,650, +74,463] spans 0; P(total>0)=0.77 → underpowered, not validated.

---

## 3. Leg separation summary (spot / ETH hedge / rebound short)

| Scope | Spot (coin) | ETH hedge | Rebound short | Total | Note |
|---|---:|---:|---:|---:|---|
| Native C11.3 canonical (`RSI21<20`) | **−3,968.80** | **+8,261.31** | **0.00** | +4,292.50 | Headline total entirely hedge-manufactured; spot alpha negative |
| Native C12 lead `c12_25_9` (discovery, in-sample) | +6,836.44 | +4,762.24 | +11,904.32 | +23,244.22 | Underpowered/CI spans 0; **not validated GO** |
| Native C13 validation of `c12_25_9` lead | **−3,968.80** | **+8,261.31** | **+11,904.32** | +23,244.22 | Hedge/rebound-masked positive total with negative spot; UNDERPOWERED |
| Native C14 same-bar (non-spec sensitivity) | — | — | — | +8,914.33 | CI spans 0; demoted per C19 |
| Native C18 spec-literal (adjudicated) | Negative | Partially offsets | Negative | −47,933.58 | Decisively negative; NO_GO |
| Cross-venue (OKX / Binance UM) | **Negative buy legs** | — | Short-leg carried | Positive but fragile | Not Hyperliquid; not decision-grade |

**Leg conclusion:** No campaign demonstrates a robust, decision-grade positive **spot** crash-rebound alpha. Positive totals, where present, rely on hedge/rebound-short components and/or fail dependence-aware validation.

---

## 4. Effective sample size and structural power limitation

- **Native window:** 283 days (`2025-12-20 .. 2026-09-28`, 6,792 hourly bars/symbol, 5 symbols) — structurally short for crash-cluster inference.
- **C13 (lead validation):** 17 trades / 10 episodes / 12 distinct crash days / 5 symbols. CI exclusion of 0 only near ~37+ episodes (far beyond observed 10).
- **C14 archive:** max achievable 4 episodes (< 5 required for GO).
- **Cross-venue pooled:** 38 independent venue-episodes still underpowered (CI spans 0, permutation non-significant).
- **Implication:** Effective N is insufficient across campaigns for decision-grade positive inference under dependence-aware methods; additional evidence would require materially more native crash episodes (beyond the available 283-day window) or genuinely new independent data — neither is claimed here.

---

## 5. Provenance and scope caveats (binding)

- **Hyperliquid-native evidence:** real, non-synthetic, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot` REST data**; `is_hyperliquid_venue_data=true` for native artifacts only.
- **Cross-venue evidence:** OKX/Binance UM results are **`is_hyperliquid_venue_data=false`** and must not be relabeled as Hyperliquid performance.
- **No fabrication:** no synthetic candles, archives, or results.
- **C19 adjudication:** `SPEC_LITERAL_NEXT_OPEN` wins on direct spec-text support ("Buy at next hourly open", no same-bar confirmation required). Canonical same-bar `confirm_rebound` is an implementation extra demoted to non-spec sensitivity. No silent change to the canonical baseline.
- **Spec constraints respected:** volume filter / trailing-24h ≥ $5M gate and spec-literal opt-in defaults not relaxed.

---

## 6. Final integrated decision

| Evidence stream | Token |
|---|---|
| Cross-venue consolidated (C10-final) | **NO_GO** (0/7) |
| Hyperliquid-native canonical C11.3 | **NO_GO / FRAGILE_NOT_DECISION_GRADE (underpowered)** (0/7) |
| Hyperliquid-native C12 discovery | **NO_DECISION_GRADE_GO** (not validated) |
| Hyperliquid-native C13 pre-registered validation | **UNDERPOWERED** (GO criteria unmet) |
| Hyperliquid-native C14 same-bar (non-spec sensitivity) | **UNDERPOWERED** (CI spans 0; demoted) |
| Hyperliquid-native C18 spec-literal (adjudicated) | **NO_GO** (−47,933.58 / 22 trades) |
| C19 consolidated native final | **NO_GO** |

**Overall final verdict: `NO_GO`.** The crash-rebound strategy (as specified/tested across C1–C19) is **not validated** as a decision-grade positive edge on available evidence. Cross-venue results do not transfer as validated Hyperliquid edge; Hyperliquid-native canonical results show negative spot alpha with hedge-masked totals and underpowered dependence-aware inference; the C19 adjudication confirms the spec-faithful reading yields a decisively negative native result. No campaign warrants a GO claim.

**Program status:** Research program complete; consolidated final verdict C19 supersedes C1–C13 consolidated final. Further positive claims would require new, decision-grade independent evidence with adequate effective crash episodes — not produced in C1–C19.

*End of consolidated final verdict.*
