# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-16T02:20:57Z — **C14 COMPLETE: VERDICT UNDERPOWERED, GATE PASS; C15 NEXT CAMPAIGN DEFINED**. "Closed state / do nothing substantive" remains **REMOVED**. C1–C13 priors preserved (`NO_GO`/`UNDERPOWERED`); C14 broad-universe native power escalation completed with full battery on widest available Ironflow universe (verdict `UNDERPOWERED`, 3 effective episodes, max 4 achievable, first CI exclusion at n=4). This file is the only durable handoff.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap). **Priority (per repo name):** decision-grade crash-rebound verdict on **Hyperliquid-native** evidence with honest dependence-aware inference. Cross-venue OKX/Binance remain `is_hyperliquid_venue_data=false` and must NOT be relabeled as Hyperliquid. Open bottleneck: effective independent crash episodes (C13: 10/5/283d; C14: 3/4/283d, max 4). Resolution requires window extension (more native crash episodes) or an evidenced hard blocker — never a bare "closed/no work".

**Priors (do not relitigate):** FINAL consolidated **`NO_GO`** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`; cross-venue C10 `NO_GO` (0/7, `is_hyperliquid_venue_data=false`) `research_state/decision_verdict_consolidated_20261115T122636Z.md`; native C11.3 `NO_GO/FRAGILE_NOT_DECISION_GRADE` `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; C12 `NO_DECISION_GRADE_GO` `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`; C13 `UNDERPOWERED` `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`; C14 `UNDERPOWERED` `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.md`.

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-16T02:20:57Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`).** C14 is **COMPLETE**: full pre-registered inference battery executed on widest available Hyperliquid-native universe (197 symbols, 113 selected at $5M gate, 283d). Gate prints `C14 ACCEPTANCE: PASS`. Verdict: **`UNDERPOWERED`** — 3 effective independent episodes (max 4 achievable from C14 archive), bootstrap 95% CI spans zero at n=3, first CI exclusion at n=4; permutation p=0.03595, placebo p=0.4444. Consolidated final verdict C1–C13: `NO_GO`. Do not relabel cross-venue as Hyperliquid, do not fabricate data, do not relax the $5M gate/spec defaults, do not edit canonical C1–C14 artifacts.

**Next focus campaign: C15 — Hyperliquid-native window extension to decision-grade power.**
The C14 power curve requires n>=4 episodes for CI-excluding-zero; C14 archive maxes at 4 and observed n=3. Resolution requires MORE independent crash episodes via window extension (spec: "Longer history since 2020 for context") OR an evidenced hard blocker if no more native data exists. A bare "closed / no work" is not an acceptable outcome (acceptance contract condition C). This campaign is heavy by design: future sessions must not be able to skip data acquisition, the full battery, or the acceptance gate.

**C15 steps (heavy, machine-gated; do in order):**
- **T1 Data acquisition (required, first):** Probe/extend the Hyperliquid-native Ironflow archive beyond 2025-12-20 (target multiyear ≥2023-01-01 parity with OKX/Binance) using `scripts/fetch_hyperliquid_candles.py` + `scripts/acquire_exchange_archive.py`. Record command/HTTP/DNS evidence. If reachable: build extended archive (parquet, per-file SHA256, non-synthetic attestation SOURCE.md) → intake validation → universe ($5M gate) → cache/provenance.
- **T2 If data acquired:** Re-run the full C14-aligned battery on the extended native universe: crash-event census → spec-canonical campaign (rsi20/t9) → episode-edge (20000 draws, recorded seed) → placebo → decision verdict (GO / UNDERPOWERED / NO_GO with power curve) → acceptance gate must print `C15 ACCEPTANCE: PASS`.
- **T3 If no more native data:** Document an evidenced hard blocker (command + HTTP + DNS evidence, not a bare statement), record a `data_request_stem`, and file an explicit data request for additional Hyperliquid-native episodes/windows. Session may close under acceptance contract condition (C) ONLY with that evidence on file.

**Gates (must all pass before session end):**
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py    # C14 ACCEPTANCE: PASS (prior, do not regress)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only blocker probe (record stem)
```
**Do not** claim GO without pre-registered criteria met (CI95 excludes zero + permutation p<0.05 + placebo p_ge_canonical<0.05 + spot leg > 0). **Do not** end the session with an unevidenced "no work."
Provenance: Hyperliquid-native = node-derived Ironflow HF (CC BY 4.0), NOT venue `candleSnapshot`; `is_hyperliquid_venue_data=true` only for native artifacts. Cross-venue OKX/Binance remain `is_hyperliquid_venue_data=false`.

### Acceptance contract (done-marker)
Complete iff (A) `C14 ACCEPTANCE: PASS` + verdict `GO` with pre-registered criteria met; or (B) `C14 ACCEPTANCE: PASS` + verdict `UNDERPOWERED`/`NO_GO` with full battery executed on widest available native universe and a power curve + explicit data request for additional episodes/windows; or (C) evidenced hard blocker (Ironflow unreachable AND no alternate verified native archive AND no cached wide archive) with command/HTTP/DNS evidence — never a bare "closed/no work".

---

## Gate-token contract (DO NOT remove — machine-checked)

This file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `verify_c13_focus_campaign.py` (C13 acceptance gate)
- `verify_c14_focus_campaign.py` (C14 acceptance gate)
- `C13` (C13 campaign token) and `C14` (C14 campaign token)
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## Verified state (as of 2026-11-16T02:20:57Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Session gate | **21/21 checks passed** | `scripts/session_gate.py` (confirmed post-C14 work) |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` (last recorded prior; re-run at end) |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` (prior) |
| C13 acceptance gate | **PASS** | `scripts/verify_c13_focus_campaign.py` (prior) |
| C14 acceptance gate | **PASS** | `scripts/verify_c14_focus_campaign.py` → `C14 ACCEPTANCE: PASS` |
| C14 intake | ACCEPT_AS_EVIDENCE_CANDIDATE | `archive_intake_validation_20261116T001129Z.json` |
| C14 universe | 113 selected / 197 symbols, $5M gate | `universe_hyperliquid_ironflow_wide_20261115T225100Z.json` |
| C14 campaign | 7 trades, pnl 8914.33, buy/short legs split | `campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 census | 661 events, 9 signal-pass, 7 trades | `crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 placebo | exact 36 runs, p_ge 0.4444 | `placebo_portfolio_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 episode-edge | done (20000 draws, seed 20261116, episodes 3, days 4) | `episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 verdict | **UNDERPOWERED** | `decision_verdict_hyperliquid_native_c14_20261116T001200Z.{md,json}` |
| C15 next campaign | **DEFINED, NOT EXECUTED** | `HANDOFF.md` → NEXT SESSION START HERE (T1 data acquisition → T2 battery/verdict/gate, or T3 evidenced hard blocker) |

**Key C14 numbers:** N=7 trades / 3 episodes / 4 symbols / 4 crash days; bootstrap 95% CI [−1144, +17547] (spans zero at n=3, first exclusion n=4); permutation p=0.03595; placebo p=0.4444; power curve quantified (max 4 episodes achievable from C14 archive). C15 target: n>=4+ independent episodes via window extension to reach CI-excluding-zero (GO), or evidenced hard blocker if no more native data.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Priors/final: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{md,json}`, `decision_verdict_consolidated_20261115T122636Z.md`, C11.3/C12/C13 verdict+evidence stems, C6/C7/C10 stems, `campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**.
- Native prior: `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Hard prohibitions
- No GO claim without pre-registered criteria met. No relabeling cross-venue as Hyperliquid. No fabrication/synthesis. No spec relaxation ($5M/RSI/spec defaults). No churn/avoidance or handoff-only stop. Single durable handoff only. Preserve gate-token contract tokens.