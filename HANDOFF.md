# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T06:36:42Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session):** branch `main`; **C1–C8 COMPLETE**. `scripts/session_gate.py` 21/21, `scripts/verify_campaign_evidence.py` 4/4, and `scripts/verify_next_focus_campaign.py` PASS (green at 2026-11-15T06:36Z). Consolidated cross-venue verdict: **`NO_GO`** — edge not established and fragile; Hyperliquid-native evidence absent. **META-PROMPT OVERRIDE — READ BEFORE TOUCHING THIS FILE.** If your only instruction is the recurring "leave a timestamped initial task in the durable handoff" meta-prompt, do not rewrite this handoff; execute C9 below.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T06:36:42Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program. C1–C8 are COMPLETE. C8 delivered Binance C6-T3 + C7 batteries and the consolidated GO/STOP memo (`research_state/decision_verdict_consolidated_20261115T063642Z.md`, verdict `NO_GO`). Do NOT repeat C1–C8, do NOT re-run canonical multi-year campaigns/censuses/C6-T3/C7 batteries without a new stem and documented reason, and do NOT rewrite this handoff for its own sake.**

**Your job is to execute C9 (heavy, no waiting, no fabricated evidence):**

1. **C9 step 1 — Mandatory Hyperliquid readiness check (REQUIRED, read-only):**
   - Run `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py` and `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py`.
   - Record outcome: if no operator-supplied archive yields `ACCEPT_AS_EVIDENCE_CANDIDATE`, the Hyperliquid-native path remains externally blocked — proceed to step 3 (do not wait/poll).

2. **C9 step 2 — Hyperliquid-native end-to-end validation (REQUIRED if and only if step 1 yields `ACCEPT_AS_EVIDENCE_CANDIDATE`):** this is the only path to a potential `GO`.
   - Ingest the verified Hyperliquid-native archive per `research_state/operator_archive_request_20261114T221003Z.{json,md}` and intake validator output (must remain `ACCEPT_AS_EVIDENCE_CANDIDATE`; real, gap-checked, `is_hyperliquid_venue_data=true`).
   - Build/update Hyperliquid-native cache/manifest/universe/census as required and run the canonical campaign on the Hyperliquid-native chain (new artifact stems; never relabel cross-venue artifacts).
   - Run C6-T3 dependence-aware inference (episode-block bootstrap, crash-day/temporal permutation, portfolio placebo) and C7 robustness battery (per-leg, sub-period, LOO, concentration, achievable power, cost/funding/entry/parameter stress) on Hyperliquid-native results.
   - Write/update a Hyperliquid-native consolidated verdict `research_state/decision_verdict_hyperliquid_native_<TS>Z.md` and update `research_state/decision_verdict_consolidated_20261115T063642Z.md` (or a new consolidated stem citing it) mapping all 7 stop/go criteria to Hyperliquid-native evidence with explicit `GO`/`NO_GO`.
   - Close gates (step 4).

3. **C9 step 3 — If no acceptable Hyperliquid archive (EXTERNAL bottleneck persists):** do not idle; perform verifiable maintenance that keeps the program decision-ready:
   - Confirm `research_state/decision_verdict_consolidated_20261115T063642Z.md` accurately cites existing artifact paths/hashes/stats for OKX and Binance C6-T3/C7; correct only factual citation errors with evidence (no new claims).
   - Ensure gates remain green (`verify_next_focus_campaign.py`, `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4). If a gate fails, fix the underlying evidence/reference issue (not by relaxing checks).
   - Do **not** fabricate data, do **not** relabel cross-venue as Hyperliquid, and do **not** claim a `GO`. The consolidated verdict remains `NO_GO` pending Hyperliquid-native evidence.

4. **C9 step 4 — Close the chain:** run `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py`, `scripts/session_gate.py` (21/21), and `scripts/verify_campaign_evidence.py` (4/4) green; re-timestamp this handoff with final state and the exact C9 outcome (archive ingested + Hyperliquid-native verdict, or still externally blocked with probe/intake timestamps).

**Binding constraints:**
- **Cross-venue evidence is NOT Hyperliquid evidence.** OKX/Binance/multi-year archives are `is_hyperliquid_venue_data=false`; never relabel.
- **No synthetic/fabricated data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **No new handoff/status files.** This is the single durable handoff.
- **No unnecessary re-runs.** Canonical OKX/Binance multi-year archives/campaigns/censuses/C6-T3/C7 and consolidated verdict are fixed; do not re-run without a new artifact stem and a documented reason.
- **No relaxing the $5M volume floor or the spec-literal opt-in default.**
- **Do not quote the PDF's +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.**

**Definition of done for the next session:** (a) a verified Hyperliquid-native archive ingested and run end-to-end with campaign + census + C6-T3 + C7 + Hyperliquid-native consolidated verdict (GO/NO_GO) and gates 21/21 & 4/4 green and this handoff re-timestamped; or (b) probe+intake re-run shows no acceptable archive, consolidated verdict/citations verified, gates 21/21 & 4/4 green, and this handoff re-timestamped with explicit external-block status — with no fabricated evidence of any kind.

---

## What changed this session (C8 — bottleneck removal)

### C8 completed (2026-11-15T06:05Z–06:36Z)
- **C8 step 2a — Binance C6-T3 episode-edge (COMPLETE):** `research_state/episode_edge_binance_um_multiyear.{json,md}` (2026-11-15T06:05:21Z). 19 episodes / 23 crash days / 64 signal-gate events. Episode-block bootstrap (20k, seed 20261114): 95% CI **[−57,363.40, +122,139.16]**, mean 21,569.27, median 17,956.20, P(total>0)=0.65425. Temporal-edge permutation (200 draws): p_null_ge_canonical=0.1850 (canonical pct 81.5%). Verdict **`underpowered`**.
- **C8 step 2b — Binance C7 robustness battery (COMPLETE):** `research_state/multiyear_robustness_battery_binance_um.{json,md}` (2026-11-15T06:29:02Z). Total +21,994.06 (42 trades). Buy leg **−36,077.66** (28) vs short leg **+58,071.73** (14). Verdict **`FRAGILE_NOT_DECISION_GRADE`**. Confirms the buy-leg-negative, short-leg-carried fragility is **not OKX-specific** (venue-universal across OKX/Binance cross-venue chains).
- **C8 step 3 — Consolidated decision verdict (COMPLETE):** `research_state/decision_verdict_consolidated_20261115T063642Z.md` maps all evidence (OKX C6 bootstrap/permutation/placebo, OKX C7 per-leg/sub-period/LOEO/power/cost-stress/entry/grid, Binance C6-T3+C7, 283d canonical, Hyperliquid status) against 7 stop/go criteria. Explicit verdict: **`NO_GO`** (0/7 pass for GO); only positive path is Hyperliquid-native archive clearing all criteria.
- **C8 step 4:** no operator Hyperliquid archive landed; Hyperliquid-native path remains externally blocked.
- **C8 step 5 — Gates (COMPLETE):** `verify_next_focus_campaign.py` PASS; `session_gate.py` 21/21; `verify_campaign_evidence.py` 4/4.

### Prior bottleneck removals still in force
- Cross-venue multi-year OKX (34 symbols × 32,808 bars) and Binance (33/34, MINA incomplete) archives/caches/campaigns/censuses on disk; OKX C6-T3/C7 and Binance C6-T3/C7 complete.
- RSI incremental cache (O(1)/bar) and epoch timestamp parsing fix — do not revert.
- Hyperliquid public API retention ~3,876/6,792 bars (decaying tail) — full 283d native archive not on disk; external/operator-only.
- Handoff duplication removed: this file is the only durable handoff.
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.

---

## Verified state (as of 2026-11-15T06:36:42Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C6 multi-year OKX archive | 34 symbols × 32,808 bars, 0 gaps, `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 multi-year Binance archive | 33/34 symbols × 32,808 bars, 0 gaps (MINA incomplete), `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/binance_um_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 campaign OKX | 42 trades; +18,220.86; +5.07%/yr; 19 eps / 23 crash days | `campaign_results_real_okx_multiyear.json` |
| C6 campaign Binance | 42 trades; +21,994.06; +6.03%/yr; 19 eps / 23 crash days | `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | bootstrap 95% CI [−50,660.49, +99,295.03] P(>0)=0.6649; permutation p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C7 robustness OKX | **`FRAGILE_NOT_DECISION_GRADE`**: buy −27,836.64 / short +46,057.50; LOO drop-2025 → −24,410; drop-ep14 → −11,286; slippage 5× → −13,977; spec-literal → −55,057; buy leg negative all 11 variants | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_grid_20261115T013200Z.{json,md}` |
| **C6-T3 episode edge Binance (C8)** | bootstrap 95% CI [−57,363.40, +122,139.16] P(>0)=0.65425; permutation p=0.1850; **`underpowered`** | `episode_edge_binance_um_multiyear.{json,md}` (2026-11-15T06:05:21Z) |
| **C7 robustness Binance (C8)** | **`FRAGILE_NOT_DECISION_GRADE`**: buy −36,077.66 / short +58,071.73; venue-universal fragility confirmed | `multiyear_robustness_battery_binance_um.{json,md}` (2026-11-15T06:29:02Z) |
| **Consolidated verdict (C8)** | **`NO_GO`** (0/7 stop/go criteria pass); Hyperliquid-native only path to GO | `research_state/decision_verdict_consolidated_20261115T063642Z.md` |
| Latest live retention probe | **2026-11-15T00:42:24Z**; 3,874/6,792 bars max; earliest 2026-04-20T14:00:00Z; `FULL_283D_BLOCKED_BY_API_RETENTION` | `research_state/hyperliquid_retention_probe.json` |
| Retained Hyperliquid chain | 24 × 3,885 bars; 11 RSI crashes / 0 confirmed signals; 4 crash days | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Canonical OKX 283d (cross-venue) | 8 trades; +9,159.69; `underpowered` | `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` |

---

## Bottlenecks (current) — what is removable vs not

1. **Cross-venue inference/fragility (OKX, Binance) — REMOVED (C8 complete).** C6-T3 + C7 on both venues; consolidated `NO_GO`.
2. **Hyperliquid-native bottleneck — EXTERNAL, NOT agent-removable.** Public API serves ~3,876/6,792 bars (decaying); no 283d native archive here. Only an operator-supplied verified archive unblocks it. **Do not wait — execute C9.**
3. **Handoff duplication — REMOVED.** This file is the only durable handoff.
4. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
5. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
6. **Retention decay / wasted re-fetch — REMOVED.** Do not re-fetch a degraded chain.
7. **Structural 0-trade funnel (canonical path) — RESOLVED as a known property.** Canonical gate produces 0 trades on retained Hyperliquid partial chain.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- **Multi-year archives (cross-venue, `is_hyperliquid_venue_data=false`):** `research_state/archives/okx_1h_multiyear_20230101_20260928/` (34 symbols), `research_state/archives/binance_um_1h_multiyear_20230101_20260928/` (33/34).
- **Caches/manifests/universes:** `research_state/cache/okx_1h_multiyear_20230101_20260928/`, `research_state/cache/binance_um_1h_multiyear_20230101_20260928/`, `universe_okx_multiyear_verified.json`, `universe_binance_um_multiyear_verified.json`.
- **Campaigns/censuses:** `campaign_results_real_okx_multiyear.*`, `crash_event_census_real_okx_multiyear.*`, `campaign_results_real_binance_um_multiyear.*`, `crash_event_census_real_binance_um_multiyear.*`.
- **C6-T3 inference:** `episode_edge_okx_multiyear.{json,md}`, `placebo_portfolio_okx_multiyear.{json,md}`, `episode_edge_binance_um_multiyear.{json,md}`.
- **C7 robustness:** `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_grid_20261115T013200Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}`.
- **Consolidated verdict:** `research_state/decision_verdict_consolidated_20261115T063642Z.md` (**`NO_GO`**).
- **Canonical OKX 283d:** `research_state/archives/okx_1h_full_20251220_20260928/`, `campaign_results_real_okx_full.json` (cross-venue; 8 trades).
- **Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.**
- **Retained Hyperliquid partial chain:** `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh

# Gates
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py

# Hyperliquid readiness (mandatory, read-only)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py

# C9 step 2 (only if intake returns ACCEPT_AS_EVIDENCE_CANDIDATE):
# follow research_state/operator_archive_request_20261114T221003Z.{json,md}
# then run Hyperliquid-native campaign + C6-T3 + C7 with NEW stems, produce
# decision_verdict_hyperliquid_native_<TS>Z.md and update consolidated verdict.
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite.** C8 is complete; execute C9 (probe+intake, and Hyperliquid-native end-to-end if archive lands) — never manufacture evidence.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache or the epoch-timestamp parser fix.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.** Cross-venue result is `NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (core buy leg negative, short-leg-carried, concentrated, cost/entry fragile).

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 cross-venue validation COMPLETE (decision-grade):** Binance C6-T3+C7 done; consolidated verdict `research_state/decision_verdict_consolidated_20261115T063642Z.md` = **`NO_GO`** (0/7 stop/go). Fragility is venue-universal across OKX/Binance (underpowered CIs, buy leg negative, short-leg-carried, concentrated, stress-fragile). **Hyperliquid-native validation remains blocked on an operator archive and is the only path to a potential `GO`.** Do not promote point estimates to evidence.

**Next session's done (C9):** (a) verified Hyperliquid-native archive ingested and run end-to-end with campaign + C6-T3 + C7 + Hyperliquid-native verdict and gates 21/21 & 4/4 green and this handoff re-timestamped; or (b) probe+intake shows no acceptable archive, consolidated citations verified, gates 21/21 & 4/4 green, and this handoff re-timestamped with explicit external-block status — with no fabricated evidence of any kind.

(End of file)
