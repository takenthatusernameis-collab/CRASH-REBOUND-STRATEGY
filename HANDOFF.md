# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-16T00:28:00Z — **C14 IN PROGRESS (HEAVY WORK ACTIVE)**. "Closed state / do nothing substantive" remains **REMOVED**. C1–C13 priors preserved (`NO_GO`/`UNDERPOWERED`); C14 broad-universe native power escalation is executing. This file is the only durable handoff.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap). **Priority:** decision-grade crash-rebound verdict on **Hyperliquid-native** evidence with honest dependence-aware inference. Open bottleneck: effective independent crash episodes (C13: 10 episodes/5 symbols/283d). C14 targets the widest real native Ironflow universe.

**Priors (do not relitigate):** FINAL consolidated **`NO_GO`** `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.md`; cross-venue C10 `NO_GO` (0/7, `is_hyperliquid_venue_data=false`) `research_state/decision_verdict_consolidated_20261115T122636Z.md`; native C11.3 `NO_GO/FRAGILE_NOT_DECISION_GRADE` `research_state/decision_verdict_hyperliquid_native_20261115T155318Z.md`; C12 `NO_DECISION_GRADE_GO` `research_state/decision_verdict_hyperliquid_native_c12_20261115T181500Z.md`; C13 `UNDERPOWERED` `research_state/decision_verdict_hyperliquid_native_c13_20261115T203734Z.md`.

---

## NEXT SESSION START HERE — INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (2026-11-16T00:28:00Z)

**You are the next agentic session continuing `CRASH-REBOUND-STRATEGY` (branch `main`).** C14-T1..T4 and prereg/gate scaffolding are complete; placebo is complete; **episode-edge (20k draws) may still be running**; verdict and final gate are **NOT** complete. Complete C14-T5..T7. No handoff-only/gate-only commit. Do not relabel cross-venue as Hyperliquid, do not fabricate data, do not relax the $5M gate/spec defaults, do not edit canonical C1–C13 artifacts.

### C14 progress (real artifacts, this session; verify before trusting)
- **T1 archive:** `research_state/archives/hyperliquid_ironflow_wide_20261115T214900Z/` (197 parquet symbols) with regenerated `SOURCE.md` (per-file rows/ts/sha256 + non-synthetic attestation). Source: Ironflow HF `ironflow/hyperliquid-candles-1h` (CC BY 4.0, node-derived, NOT venue `candleSnapshot`).
- **T2 intake:** `research_state/archive_intake_validation_20261116T001129Z.{json,md}` → **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (174 accepted symbols). Command recorded in md.
- **T3 universe:** `research_state/universe_hyperliquid_ironflow_wide_20261115T225100Z.json` — **selected_count 113**, $5M gate, 283d window, real/non-synthetic, `is_hyperliquid_venue_data` context native.
- **Cache/provenance:** `research_state/cache/hyperliquid_ironflow_wide_20261115T234000Z/` (`provenance.json`, candles).
- **T4 campaign (spec-canonical, rsi20/t9):** `research_state/campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json` (pathed with `is_hyperliquid_venue_data=true`, `venue_label` native). **7 trades, total_pnl 8914.334981956968** (leg attribution: buy 11,736.94 / short −2,822.60). Real data, non-fabricated.
- **T4 census (C14-aligned):** `research_state/crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.{json,md}` — events 661, volume_pass 235, bounce 71, regime 119, **signal_gate_pass 9, trades 7, matched 7, unexplained 0**; blocking: volume_gate 426, bounce_not_confirmed 209, regime 17, one_position_per_coin 2, trade_opened 7. Bound to C14 campaign (not OKX).
- **T5 placebo (done):** `research_state/placebo_portfolio_hyperliquid_ironflow_wide_20261116T001200Z.{json,md}` — exact enumeration, **runs 36** (choose 7 of 9 signal-gate events), canonical replay matches, **p_ge_canonical 0.4444**, P(total>0) 1.0, seed 20261116, config-matched rsi20/t9, node-derived provenance.
- **T5 episode-edge:** **NOT COMPLETE / may be running.** Started as bg process writing `research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json` and log `/tmp/c14_episode.log` (`scripts/run_episode_edge_okx_multiyear.py --draws 20000 --seed 20261116 ...`). **Check first:** `ls research_state/episode_edge_hyperliquid_ironflow_wide_20261116T001200Z*; tail -40 /tmp/c14_episode.log; pgrep -af run_episode_edge_okx_multiyear` (or background_process list). If missing/failed, rerun to completion.
- **T6 prereg:** `research_state/hyperliquid_native_c14_prereg_20261116T001200Z.{json,md}` (generated before compute; seed 20261116, min_draws 100, draws 20000/2000, spec-canonical rsi20/t9, priors listed).
- **T7 scaffolding:** `scripts/build_c14_prereg.py`, `scripts/verify_c14_focus_campaign.py`, `scripts/run_portfolio_placebo_hyperliquid_wide_c14.py` created. `verify_c14_focus_campaign.py` currently **FAILS** until episode-edge + verdict exist and handoff records completion.

### C14 completion steps (mandatory)
1. **Ensure episode-edge finished:** produce `episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.{json,md}` with `temporal_edge_permutation.draws_evaluated>=20000`, seed 20261116, config rsi20/t9, node-derived provenance, episode/bootstrap/CI/permutation/crash-days reported.
2. **Write verdict (T6):** `research_state/decision_verdict_hyperliquid_native_c14_20261116T001200Z.{md,json}`. Reference **all priors** (C11.3 `decision_verdict_hyperliquid_native_20261115T155318Z`, C12 `decision_verdict_hyperliquid_native_c12_20261115T181500Z`, C13 `decision_verdict_hyperliquid_native_c13_20261115T203734Z`, consolidated C10 `decision_verdict_consolidated_20261115T122636Z`, FINAL `decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z`) plus all C14 stems (prereg, intake, archive SOURCE, universe, campaign, census, episode-edge, placebo). Include dependence-aware evidence (episode-block bootstrap 95% CI, permutation p, placebo p, leg separation spot/ETH hedge/rebound short), effective N (trades/episodes/crash days). Token exactly `GO`, `UNDERPOWERED`, or `NO_GO`. **If not GO:** include quantified **power curve** (episodes required for CI exclusion at observed variance; max episodes achievable from C14 archive). Given observed funnel (9 signal-gate events, 7 trades) GO is unlikely; be honest and quantified.
3. **Run gate:** `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py` must print **`C14 ACCEPTANCE: PASS`**. Fix any real missing consistency (SHA/seed/config/provenance) — do not weaken the gate.
4. **Update this handoff** with final verdict token, key numbers (N/trades/episodes/days, CI, perm p, placebo p, power curve summary), and `C14 ACCEPTANCE: PASS` status; keep all gate-token contract tokens.

### Readiness + gates
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # expect 21/21 checks passed
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 read-only (record stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c13_focus_campaign.py    # C13 ACCEPTANCE: PASS (prior)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_c14_focus_campaign.py    # must print C14 ACCEPTANCE: PASS to finish
```
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

## Verified state (as of 2026-11-16T00:28:00Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Session gate | **21/21 checks passed** | `scripts/session_gate.py` (confirmed post-C14 work) |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` (last recorded prior; re-run at end) |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` (prior) |
| C13 acceptance gate | **PASS** | `scripts/verify_c13_focus_campaign.py` (prior) |
| C14 acceptance gate | **FAIL (incomplete)** — needs episode-edge + verdict | `scripts/verify_c14_focus_campaign.py` (target: `C14 ACCEPTANCE: PASS`) |
| C14 intake | ACCEPT_AS_EVIDENCE_CANDIDATE | `archive_intake_validation_20261116T001129Z.json` |
| C14 universe | 113 selected / 195 symbols, $5M gate | `universe_hyperliquid_ironflow_wide_20261115T225100Z.json` |
| C14 campaign | 7 trades, pnl 8914.33, buy/short legs split | `campaign_results_real_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 census | 661 events, 9 signal-pass, 7 trades | `crash_event_census_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 placebo | exact 36 runs, p_ge 0.4444 | `placebo_portfolio_hyperliquid_ironflow_wide_20261116T001200Z.json` |
| C14 episode-edge | running/pending | `episode_edge_hyperliquid_ironflow_wide_20261116T001200Z.json` + `/tmp/c14_episode.log` |

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Priors/final: `research_state/decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z.{md,json}`, `decision_verdict_consolidated_20261115T122636Z.md`, C11.3/C12/C13 verdict+evidence stems, C6/C7/C10 stems, `campaign_results_real_okx_multiyear*`, `campaign_results_real_binance_um_multiyear*`, Phase O `episode_edge_okx_full.json` timestamp **2026-11-13T23:38:47Z**.
- Native prior: `archives/hyperliquid_ironflow_1h_20251220_20260928/*`, `cache/hyperliquid_ironflow_native_20251220_20260928/`, `universe_hyperliquid_ironflow_native_20251220_20260928.json`.
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.

## Hard prohibitions
- No GO claim without pre-registered criteria met. No relabeling cross-venue as Hyperliquid. No fabrication/synthesis. No spec relaxation ($5M/RSI/spec defaults). No churn/avoidance or handoff-only stop. Single durable handoff only. Preserve gate-token contract tokens.
