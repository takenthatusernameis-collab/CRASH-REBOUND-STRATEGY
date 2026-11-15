# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T20:49:33Z — **FINAL CONSOLIDATION COMPLETE**. `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` (+ `.json`) written: **final verdict `NO_GO`** with traceability to all C1–C13 verdict stems, dependence-aware synthesis, leg separation, and power/provenance caveats. **C1–C13 COMPLETE. Research program primary mission complete (closed).** Gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS (C6 ACCEPTANCE: PASS)**, `verify_c13_focus_campaign.py` **PASS (C13 ACCEPTANCE: PASS)**.
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from repo name):** produce a **decision-grade crash-rebound verdict** — validate or falsify the edge on **Hyperliquid-native** evidence with honest dependence-aware inference. **This priority is satisfied to closure:** C1–C13 executed and synthesized; **final consolidated verdict is `NO_GO`**. No further compute campaign is required unless genuinely new, independent, decision-grade evidence (with adequate effective crash episodes) is supplied.

**Verdict state (final):**
- **FINAL CONSOLIDATED:** **`NO_GO`** — `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` (synthesizes all campaigns; no GO claim).
- Cross-venue consolidated (C10-final): **`NO_GO`** (0/7, `is_hyperliquid_venue_data=false`) — `research_state/decision_verdict_consolidated_20261115T122636Z.md`.
- Native canonical (C11.3): **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (underpowered), 0/7** — `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md` (consolidated native `research_state/decision_verdict_consolidated_20261115T155318Z.md`). Spot −3,968.80, hedge +8,261.31, rebound 0, total +4,292.50.
- Native C12: **`NO_DECISION_GRADE_GO`** (discovery only; lead underpowered/CI spans 0, not validated) — `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`. Canonical `RSI(21)<20` preserved as NO_GO.
- Native C13 (pre-registered validation, 200/200 draws, seed 20261115, SHA-bound to C12 lead): **`UNDERPOWERED`** — `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`; bootstrap CI95 [−22,799.52, +79,978.91] spans 0; permutation p(null≥canon)=0.085; placebo p_ge_canon=0.32; legs spot −3,968.80 / hedge +8,261.31 / rebound +11,904.32 (total +23,244.22, hedge/rebound-masked, spot negative). No GO criterion met.

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-15T20:49:33Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`).** **C1–C13 and FINAL CONSOLIDATION are COMPLETE.** Final verdict: **`NO_GO`** (`research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`). **Do not claim GO. Do not relabel cross-venue as Hyperliquid. Do not rerun/relitigate C1–C13 or fabricate data.**

### Primary mission: MAINTAIN CLOSED STATE (no idle churn)
The program is closed on available evidence. A session **must not** do handoff-only edits, gate-only reruns, or redundant campaign reruns. Productive work is allowed **only if** one of the following applies:
1. **New independent, decision-grade evidence is actually present in-repo** (e.g. a verified Hyperliquid-native archive not yet ingested that can pass `scripts/validate_hyperliquid_archive_intake.py` with `ACCEPT_AS_EVIDENCE_CANDIDATE` and materially increase effective crash episodes). If so: run `probe_hyperliquid_blocker.py`/intake validation, preregister a dependence-aware campaign, execute it with config-matched inference/placebo, write a new verdict stem referencing all priors, and update this handoff — no shortcuts.
2. **A concrete, verifiable defect** breaks gates or corrupts canonical artifacts; fix it with minimal change and record evidence.

If neither applies: **do nothing substantive** — confirm gates are green if already verified and report "closed, no actionable work". Do **not** invent work.

### 0) Readiness + gates (run only when performing allowed work or if verification is required; record outputs/stems)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS
```
Provenance (binding): Hyperliquid-native evidence is **node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`**; `is_hyperliquid_venue_data=true` only for native artifacts. Cross-venue OKX/Binance are `is_hyperliquid_venue_data=false`.

### Bottlenecks / constraints (binding)
1. **Statistical power — structural (closed on current data).** 283d native window; C13 effective N 17 trades / 10 episodes / 12 distinct crash days / 5 symbols (C12 reported 11 trade crash days — counting-unit difference, not contradiction). Bootstrap CI95 spans 0; permutation/placebo not extreme; CI exclusion of 0 extrapolated near ~37+ episodes. No more power available from C1–C13 data.
2. **External Hyperliquid API 1h retention — expected, non-blocking.** Archived Ironflow native evidence is the accepted full-window source.
3. **Cross-venue evidence — exhausted/CLOSED (`is_hyperliquid_venue_data=false`).** Do not re-acquire/re-run or relabel.

**Definition of done (closed state):** No GO claim; canonical artifacts unchanged; gates green when checked; this handoff remains the single durable handoff with gate-token contract intact.

---

## Gate-token contract (DO NOT remove — machine-checked)

This file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `verify_c13_focus_campaign.py` (C13 acceptance gate)
- `C13` (C13 campaign token)
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## What changed this session (2026-11-15T20:49Z)

- **FINAL CONSOLIDATION executed:** wrote `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` and `.json` — final verdict **`NO_GO`**, traceability to all prior verdict stems (cross-venue C10-final, native C11.3/consolidated, C12, C13) and C13 supporting artifacts, dependence-aware synthesis, leg separation, effective-N/power limitation, provenance caveats.
- **Handoff updated (single durable):** marked C1–C13 + FINAL consolidation complete, program closed on available evidence; next-session mission set to maintain closed state (no idle churn) unless new independent decision-grade evidence/defect.
- **Gates (recorded):** `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**, `verify_c13_focus_campaign.py` **PASS**.

## Verified state (as of 2026-11-15T20:49Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` ready | venv present |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C13 acceptance gate | **PASS** | `scripts/verify_c13_focus_campaign.py` |
| **Final consolidated verdict** | **`NO_GO`** | `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md` (+ `.json`) |
| Cross-venue consolidated verdict | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Native canonical verdict (C11.3) | **`NO_GO` / `FRAGILE_NOT_DECISION_GRADE`, 0/7** | `decision_verdict_hyperliquid_native_20261115T155318Z.md` |
| C12 verdict | **`NO_DECISION_GRADE_GO`** | `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md` |
| C13 verdict | **`UNDERPOWERED`** | `decision_verdict_hyperliquid_native_c13_20261115T203734Z.md` |
| C13 artifacts | prereg/episode-edge/placebo present (200/200, seed 20261115) | `hyperliquid_native_c13_prereg_20261115T185721Z.*`, `episode_edge_hyperliquid_native_c13_20261115T200200Z.*`, `placebo_portfolio_hyperliquid_native_c13_20261115T200309Z.*` |

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- **Final:** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`, `.json`.
- Cross-venue/canonical: `campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, C6-T3/C7/C10 stems, `decision_verdict_consolidated_20261115T122636Z.md`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**.
- **C11 native:** `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `archive_intake_validation_20261115T140420Z.*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`, `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`, C11.3 census/episode/placebo/robustness/verdict stems, `hyperliquid_native_power_prereg_20261115T123859Z.*`.
- **C12:** prereg/campaign/census/inference/verdict stems under `research_state/` (incl. `decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`).
- **C13:** prereg/episode-edge/placebo/verdict stems (20261115T185721Z, 20261115T200200Z, 20261115T200309Z, 20261115T203734Z).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Hard prohibitions

- **No GO claim.** Do not claim edge from hedge-masked totals, point PnL, in-sample discovery, or underpowered results.
- **No relabeling.** Do not relabel cross-venue (`is_hyperliquid_venue_data=false`) as Hyperliquid; do not misstate native provenance (node-derived Ironflow HF, CC BY 4.0, NOT venue `candleSnapshot`).
- **No fabrication/synthesis.** No synthetic candles/archives/results.
- **No churn.** No handoff-only/gate-only sessions, no redundant reruns of canonical campaigns/censuses/C6-T3/C7/C10/C11.3/C12/C13 without a new artifact stem and documented reason tied to genuinely new evidence/defect.
- **No spec relaxation.** Do not relax `volume_filter_ok` / trailing-24h ≥ $5M gate or spec-literal opt-in defaults.
- **Single durable handoff only.** Do not create a second handoff/status file.
- **Preserve gate-token contract tokens** listed above.

(End of file)
