# Consolidated Final Decision Verdict — CRASH-REBOUND-STRATEGY (C1–C13)

**Generated (UTC):** 2026-11-15T20:49:33Z
**Scope:** Final consolidation of all completed campaigns C1–C13 (cross-venue and Hyperliquid-native). This file closes the research program.
**Final verdict token:** `NO_GO` (no GO claim from any campaign)

This verdict synthesizes prior decision-grade artifacts; it does **not** relabel cross-venue evidence as Hyperliquid evidence, does **not** claim a validated edge, and does **not** introduce new data or reruns.

---

## 1. Traceability — referenced prior verdict/artifact stems

| Campaign / scope | Verdict stem (filename) | Verdict token / outcome |
|---|---|---|
| Cross-venue consolidated (C1–C10, OKX + Binance UM) | `research_state/decision_verdict_consolidated_20261115T122636Z.md` | **`NO_GO`** (0/7 stop/go criteria pass); `is_hyperliquid_venue_data=false` |
| Native canonical (C11.3, Hyperliquid-native, `RSI(21)<20`) | `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md` | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (`underpowered`)** (0/7) |
| Native consolidated (C11.3 context) | `research_state/decision_verdict_consolidated_20261115T155318Z.md` | Consolidated native context (canonical NO_GO preserved) |
| Native C12 (discovery/grid, Hyperliquid-native) | `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` | **`NO_DECISION_GRADE_GO`** (discovery only; best in-sample lead underpowered, not validated) |
| Native C13 (pre-registered validation of C12 lead) | `research_state/decision_verdict_hyperliquid_native_c13_203734Z.md` | **`UNDERPOWERED`** (pre-registered decision-grade thresholds not met) |

**C13 supporting artifacts (referenced):**
- Prereg: `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.json`, `research_state/hyperliquid_native_c13_prereg_20261115T185721Z.md`
- Episode-edge: `research_state/episode_edge_hyperliquid_native_c13_20261115T200200Z.json`, `research_state/episode_edge_hyperliquid_native_c13_20261115T200200Z.md`
- Placebo: `research_state/placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.json`, `research_state/placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.md`

(Additional prior consolidated stems exist in `research_state/` for historical traceability, e.g. `decision_verdict_consolidated_20261115T063642Z.md`, `decision_verdict_consolidated_20261115T064738Z.md`; C10-final `20261115T122636Z` supersedes them for cross-venue finality.)

---

## 2. Synthesized dependence-aware evidence (all campaigns)

### 2.1 Cross-venue (C1–C10, OKX & Binance UM) — **NOT Hyperliquid evidence**
- **Verdict:** `NO_GO` (0/7 stop/go criteria pass). Source: `decision_verdict_consolidated_20261115T122636Z.md`.
- **Provenance:** real OKX/Binance UM exchange data, non-synthetic; **`is_hyperliquid_venue_data=false`** for all cross-venue artifacts.
- **Dependence-aware / inference:** C10.3 pooled 38 independent venue-episodes (OKX 19 + Binance 19) — observed total +40,214.92; episode-block bootstrap 95% CI **[−69,065.03, +168,946.87]** (spans 0), **P(total>0)=0.74095**; sign-flip permutation p(one-sided)=0.26955, p(two-sided)=0.53560 → **underpowered**.
- **Placebo:** OKX p(placebo≥canon)=0.40; Binance p(placebo≥canon)=0.4150 — no separation from gate-passing pool.
- **Cross-venue agreement:** paired (symbol, entry_date_utc, leg) same-sign rate 1.0000 (32/32 matched pairs) but mean magnitude diff CI crosses 0; directional replication only, not edge sufficiency.
- **Binding fragility (C8/C10):** buy leg negative on both venues; short-leg-carried totals; concentrated/unstable across sub-periods/episodes; stress-fragile (e.g. slippage/entry/parameter sensitivity). No criterion flips to pass.

### 2.2 Native canonical C11.3 (Hyperliquid-native, `RSI(21)<20`, 2025-12-20..2026-09-28)
- **Verdict:** `NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (`underpowered`), 0/7. Source: `decision_verdict_hyperliquid_native_20261115T155318Z.md`.
- **Inference:** 43 crash events → 7 signal-gate → 6 trades in 3 episodes across 4 crash days. Episode-block bootstrap (20k) 95% CI **[−1,143.66, +10,339.42]** (spans 0), P(total>0)=0.9624; conditional temporal permutation (200) p_null_ge_canonical=0.0800 (≥0.05) → underpowered.
- **Placebo:** exact enumeration of all C(7,6)=7 subsets, p_ge_canonical=0.7143 (canonical 42.86th percentile) — no distinguishing alpha.
- **Economics:** total +4,292.50 but **spot coin PnL −3,968.80**; **ETH hedge +8,261.31**; **rebound short 0.00** (canonical target 9% triggered none). 5x slippage → negative; RSI<15 → negative; trades concentrated in 2026-01.

### 2.3 Native C12 (discovery grid, Hyperliquid-native)
- **Verdict:** `NO_DECISION_GRADE_GO` (discovery only). Source: `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`.
- **Best in-sample lead:** `c12_25_9` (`rsi_threshold 25, target_pct 9`) — total +23,244.22 (spot +6,836.44, hedge +4,762.24, rebound +11,904.32; 17 trades / 10 episodes / 11 crash days). Episode-block bootstrap CI95 spans 0 (spot [−26,795, +36,129], total [−36,650, +74,463], P(total>0)=0.770) → **underpowered, not a validated GO**.
- **Other configs:** `c12_20_5/22_5` totals positive but **hedge-masked** (spot deeply negative). `c12_25_5` and all RSI 30 configs negative total with large negative spot.
- **Canonical preserved:** `RSI(21)<20` remains NO_GO.

### 2.4 Native C13 (pre-registered validation of C12 lead `rsi 25 / target 9`)
- **Verdict:** `UNDERPOWERED` (no GO, no validated NO_GO flip; decision-grade thresholds not met). Source: `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`.
- **Methods (pre-registered, seed 20261115, SHA-bound to C12 lead):** episode-block bootstrap (20k), temporal-edge permutation (200 draws), full-portfolio placebo (200 subsets of 17-from-33).
- **Results:** bootstrap CI95 **[−22,799.52, +79,978.91]** spans 0 (P(total>0)=0.803; CI excludes 0 only near n≈37+ episodes, far beyond observed 10); permutation **p(null≥canonical)=0.085** (91.5th pct, 17/200); placebo **p_ge_canonical=0.32** (canonical 68th pct, P(total>0)=0.875, CI95 [−8,535.90, +35,076.30] spans 0).
- **Interpretation:** evidence consistent with timing luck; canonical subset not extreme in placebo distribution; pre-registered GO criteria not satisfied. C12 `c12_25_9` remains hypothesis-generating, not validated.

---

## 3. Leg separation summary (spot / ETH hedge / rebound short)

| Scope | Spot (coin) | ETH hedge | Rebound short | Total | Note |
|---|---:|---:|---:|---:|---|
| Native C11.3 canonical (`RSI21<20`) | **−3,968.80** | **+8,261.31** | **0.00** | +4,292.50 | Headline total entirely hedge-manufactured; spot alpha negative |
| Native C12 lead `c12_25_9` (discovery, in-sample) | +6,836.44 | +4,762.24 | +11,904.32 | +23,244.22 | Underpowered/CI spans 0; **not validated GO** |
| Native C13 validation of `c12_25_9` lead | **−3,968.80** | **+8,261.31** | **+11,904.32** | +23,244.22 | **Hedge/rebound-masked positive total with negative spot**; UNDERPOWERED (permutation/placebo/CI all fail GO thresholds) |
| Cross-venue (OKX / Binance UM) | **Negative buy legs** (OKX −27,837; Binance −36,078) | (per strategy mechanics) | Short-leg carried (OKX +46,058; Binance +58,072) | Positive totals but fragile | Not Hyperliquid; not decision-grade |

**Leg conclusion:** No campaign demonstrates a robust, decision-grade positive **spot** crash-rebound alpha. Positive totals, where present, rely on hedge/rebound-short components and/or fail dependence-aware validation.

---

## 4. Effective sample size and structural power limitation

- **Native window:** 283 days (`2025-12-20 .. 2026-09-28`, 6,792 hourly bars/symbol, 5 symbols) — structurally short for crash-cluster inference.
- **C13 (lead validation, pre-registered):** 17 trades / 10 episodes / 12 distinct crash days / 5 symbols. C13 bootstrap power extrapolation indicates CI exclusion of 0 only near ~37+ episodes (far beyond observed 10).
- **C12 lead (discovery):** 17 trades / 10 episodes / 11 crash days (trade crash days). **Counting-unit note:** C12 reports 11 trade crash days while the C13 episode-edge artifact reports 12 distinct signal-event days (all crash bars); this is a counting-unit difference, not a contradiction.
- **C11.3 canonical:** 6 trades / 3 episodes / 4 distinct crash days.
- **Cross-venue pooled:** 38 independent venue-episodes (OKX 19 + Binance 19) still underpowered (CI spans 0, permutation non-significant).
- **Implication:** Effective N is insufficient across campaigns for decision-grade positive inference under dependence-aware methods; additional evidence would require materially more native crash episodes (beyond the available 283-day window) or genuinely new independent data — neither is claimed here.

---

## 5. Provenance and scope caveats (binding)

- **Hyperliquid-native evidence:** real, non-synthetic, **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot` REST data**; `is_hyperliquid_venue_data=true` for native artifacts only. Full-window native coverage comes from the accepted Ironflow archive, not the live API (API retention externally limited/expected, non-blocking for the archived evidence used).
- **Cross-venue evidence:** OKX/Binance UM results are **`is_hyperliquid_venue_data=false`** and must not be relabeled as Hyperliquid performance.
- **No fabrication:** no synthetic candles, archives, or results.
- **Spec constraints respected in canonical runs:** volume filter / trailing-24h ≥ $5M gate and spec-literal opt-in defaults not relaxed (per program rules).

---

## 6. Final integrated decision

| Evidence stream | Token |
|---|---|
| Cross-venue consolidated (C10-final) | **NO_GO** (0/7) |
| Hyperliquid-native canonical C11.3 | **NO_GO / FRAGILE_NOT_DECISION_GRADE (underpowered)** (0/7) |
| Hyperliquid-native C12 discovery | **NO_DECISION_GRADE_GO** (not validated) |
| Hyperliquid-native C13 pre-registered validation | **UNDERPOWERED** (GO criteria unmet) |

**Overall final verdict: `NO_GO`.**
The crash-rebound strategy (as specified/tested across C1–C13) is **not validated** as a decision-grade positive edge on available evidence. Cross-venue results do not transfer as validated Hyperliquid edge; Hyperliquid-native canonical results show negative spot alpha with hedge-masked totals and underpowered dependence-aware inference; the C12 lead is discovery-only and fails pre-registered C13 validation (bootstrap CI spans 0, permutation p=0.085, placebo p_ge=0.32, spot leg negative). No campaign warrants a GO claim.

**Program status:** Research program primary mission complete; consolidated final verdict recorded. Further positive claims would require new, decision-grade independent evidence with adequate effective crash episodes — not produced in C1–C13.

*End of consolidated final verdict.*
