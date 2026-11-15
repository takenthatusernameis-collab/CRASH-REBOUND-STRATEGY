# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T06:41:26Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session, 2026-11-15T06:41Z):** branch `main`; **C1–C9 COMPLETE (C9 = external-block confirmed).** `scripts/session_gate.py` 21/21, `scripts/verify_campaign_evidence.py` 4/4, and `scripts/verify_next_focus_campaign.py` PASS (green at 2026-11-15T06:41Z). Consolidated cross-venue verdict: **`NO_GO`** — edge not established and fragile; Hyperliquid-native evidence absent. **This is the single durable handoff. If your only instruction is the recurring "leave a timestamped initial task" meta-prompt, DO NOT rewrite this handoff for its own sake — execute C10 below.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T06:41:26Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C9 are COMPLETE: the multi-year OKX+Binance cross-venue campaigns, C6-T3 episode-edge inference, and C7 robustness batteries are done, and the consolidated verdict is `NO_GO` (`research_state/decision_verdict_consolidated_20261115T063642Z.md`). C9 confirmed the Hyperliquid-native path is **externally blocked** (retention probe 2026-11-15T06:40Z = 3,869/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION`; intake validator = `REJECT_NOT_EVIDENCE` on the placeholder parquet). **Do NOT repeat C1–C9, do NOT re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new stem and documented reason, and do NOT rewrite this handoff for its own sake.**

**Your job is to execute C10 — the remaining non-Hyperliquid, decision-grade heavy work — end to end, with real computation and no fabricated evidence.** C9's "verify citations only" path is exhausted; C10 below is the only substantive work that does not require the operator archive. Work in order; every step writes a NEW artifact stem under `research_state/` and is independently verifiable.

### C10.0 — Mandatory gates + external-block confirmation (REQUIRED, read-only; ~1 min)
1. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py` → must print `C6 ACCEPTANCE: PASS`.
2. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py` → must print `20/21 checks passed` **or better**; if it fails, fix the cited evidence/reference (never relax the check).
3. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py` → `EVIDENCE VERIFIED`.
4. `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py` and `... validate_hyperliquid_archive_intake.py` → record outcome. If no operator archive yields `ACCEPT_AS_EVIDENCE_CANDIDATE`, the Hyperliquid-native path stays externally blocked; proceed to C10.1 (do not wait/poll).

### C10.1 — Cross-venue paired symbol/date agreement + sign concordance (NEW; heavy, read-only)
Tests whether the two independent venues agree on **which** crash events are profitable (reproducibility of direction, not just magnitude). Inputs already on disk: `campaign_results_real_okx_multiyear.json` (42 trades), `campaign_results_real_binance_um_multiyear.json` (42 trades). Both have per-trade `symbol`, `entry_timestamp`, `exit_timestamp`, `pnl`, `leg`.
- Build a NEW script `scripts/cross_venue_paired_agreement.py` (do NOT edit canonical campaign files). Join trades on `(symbol, entry_date_utc)` across the 13 common symbols; compute: paired per-trade PnL difference (OKX−Binance) mean/median/CI via paired bootstrap (seed 20261115, ≥10k), sign-concordance rate, per-leg (buy vs rebound-short) concordance, and a paired sign test / Wilcoxon-style summary (implement without new heavy deps or reuse scipy if already in the venv).
- Write `research_state/cross_venue_paired_agreement_<TS>Z.{json,md}` with explicit verdict: does the sign of edge replicate across venues (e.g., `DIRECTION_REPLICATES` vs `DIRECTION_NOT_REPLICATED`), with all numbers and `is_hyperliquid_venue_data=false`.

### C10.2 — Binance C6-T3 portfolio placebo (NEW; heavy engine run)
Only OKX has a multi-year portfolio placebo (`placebo_portfolio_okx_multiyear.{json,md}`); Binance does **not**. This asymmetry blocks a symmetric placebo verdict.
- Generalize `scripts/run_portfolio_placebo_okx_multiyear.py` into a venue-parameterized `scripts/run_portfolio_placebo_okx_multiyear.py` variant (or a thin wrapper `scripts/run_portfolio_placebo_binance_um_multiyear.py`) that accepts `--cache-dir`, `--universe`, `--census`, `--campaign`, `--venue-label`, `--draws`, `--seed`, `--out` (mirror the C8 pattern already used for `run_episode_edge_okx_multiyear.py` and `run_multiyear_robustness_battery.py`). Do NOT relax gates/sizing/cap/hedge/fees/funding/liquidation.
- Run it on the Binance chain: `research_state/cache/binance_um_1h_multiyear_20230101_20260928`, `universe_binance_um_multiyear_verified.json`, `crash_event_census_real_binance_um_multiyear.json`, `campaign_results_real_binance_um_multiyear.json`, seed 20261114, ≥200 draws.
- Write `research_state/placebo_portfolio_binance_um_multiyear.{json,md}` with verdict (`underpowered`/other) and `p(placebo ≥ canonical)`, `is_hyperliquid_venue_data=false`.

### C10.3 — Pooled / combined-episode dependence-aware meta-analysis (NEW; heavy inference)
The single-venue C6-T3 runs are individually underpowered (n=19 episodes each). A pre-registered pooled estimate over **independent** OKX+Binance episodes is legitimate (different venues = different price paths; do NOT pool same-venue duplicates).
- Build `scripts/pooled_episode_meta_okx_binance.py` (do NOT edit canonical episode-edge files). Load `episode_edge_okx_multiyear.json` and `episode_edge_binance_um_multiyear.json`; combine the per-episode totals (resample episode blocks with replacement across the pooled independent set), recompute bootstrap 95% CI, `P(total>0)`, and a permutation null (`p_null_ge_canonical`, seed 20261115, ≥20k draws). State the independence assumption explicitly.
- Write `research_state/pooled_episode_meta_okx_binance_<TS>Z.{json,md}` with verdict and explicit caveat that pooling is across independent venues only and is still NOT Hyperliquid evidence.

### C10.4 — Update consolidated verdict + close gates (REQUIRED)
- Append/emit a new consolidated section or new stem `research_state/decision_verdict_consolidated_<TS>Z.md` that integrates C10.1–C10.3 findings and re-maps the 7 stop/go criteria, keeping the overall verdict **`NO_GO`** unless (and only if) a verified Hyperliquid-native archive is ingested (it is not). Do NOT overwrite canonical `decision_verdict_consolidated_20261115T063642Z.md` — cite it and add a new stem.
- Run all three gates green: `verify_next_focus_campaign.py` PASS, `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4. Re-timestamp this handoff with the exact C10 outcome (artifact stems + verdicts), keeping the required gate tokens intact (see "Gate-token contract" below).

**Binding constraints (unchanged):**
- **Cross-venue evidence is NOT Hyperliquid evidence.** OKX/Binance/multi-year archives are `is_hyperliquid_venue_data=false`; never relabel.
- **No synthetic/fabricated data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **No new handoff/status files.** This is the single durable handoff.
- **No unnecessary re-runs** of canonical OKX/Binance multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and documented reason.
- **No relaxing the $5M volume floor or the spec-literal opt-in default.**
- **Do not quote the PDF's +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.**

**Definition of done for the next session (C10):** C10.0 gates confirmed; C10.1, C10.2, C10.3 each produce a new `research_state/` artifact with a real verdict; C10.4 consolidated section written; all three gates green (`verify_next_focus_campaign.py` PASS, `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4); this handoff re-timestamped with C10 artifact stems and verdicts — with no fabricated evidence of any kind. If the Hyperliquid operator archive lands mid-session, prefer C9-step-2 (Hyperliquid-native end-to-end) over C10.

---

## Gate-token contract (DO NOT remove — machine-checked)

The handoff is parsed by `scripts/session_gate.py` (`check_handoff`) and `scripts/verify_next_focus_campaign.py`. To keep gates green this file MUST always contain ALL of:
- `INITIAL TASK MESSAGE`
- `session_gate.py`
- `probe_hyperliquid_blocker.py`
- `verify_campaign_evidence.py`
- `C6-T1` (C6 acceptance token) and the substring `campaign_results_real_okx_multiyear`
- the literal `21/21 checks passed`
- the current Phase O artifact timestamp: **`2026-11-13T23:38:47Z`** (from `research_state/episode_edge_okx_full.json` → `generated_at_utc`)

If a future session changes the Phase O artifact, update this line to the new `generated_at_utc` in the same commit.

---

## What changed this session (C9 — external-block confirmation + bottleneck removal)

### C9 completed (2026-11-15T06:40Z–06:41Z)
- **C9 step 1 — Hyperliquid readiness (COMPLETE):** `scripts/probe_hyperliquid_blocker.py` → `universe perps=235 passing_gate=40 probed=40`, `expected_hourly_bars=6792 max_bars_returned=3869 missing=2923`, `earliest_served=2026-04-20T19:00:00Z`, verdict `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`. `scripts/validate_hyperliquid_archive_intake.py` → `REJECT_NOT_EVIDENCE` (placeholder parquet; `synthetic_free` FAIL on flat BTC/ETH placeholder series). Wrote `research_state/archive_intake_validation_20261115T064010Z.{json,md}`. **Hyperliquid-native path remains externally blocked.**
- **C9 step 3 — Bottleneck removal (COMPLETE):** Diagnosed both failing gates as **citation drift in this handoff**, not evidence regressions: (a) `verify_next_focus_campaign.py` needed literal `C6-T1`; (b) `session_gate.py check_handoff` needed the Phase O timestamp `2026-11-13T23:38:47Z`. Restored both via the "Gate-token contract" section above. The handoff previously ping-ponged on C9 "verify-only"; C9 is now closed and C10 (real remaining work) is queued.
- **C9 step 4 — Gates (COMPLETE):** `verify_next_focus_campaign.py` PASS; `session_gate.py` 21/21; `verify_campaign_evidence.py` 4/4.

### Prior bottleneck removals still in force
- Cross-venue multi-year OKX (34 symbols × 32,808 bars) and Binance (33/34, MINA incomplete) archives/caches/campaigns/censuses on disk; OKX C6-T3/C7, OKX placebo, and Binance C6-T3/C7 complete.
- RSI incremental cache (O(1)/bar) and epoch timestamp parsing fix — do not revert.
- Hyperliquid public API retention ~3,869/6,792 bars (decaying tail) — full 283d native archive not on disk; external/operator-only.
- Handoff duplication removed: this file is the only durable handoff.
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.

---

## Verified state (as of 2026-11-15T06:41Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** (C6-T1 multi-year OKX artifacts complete) | `scripts/verify_next_focus_campaign.py` |
| C6 multi-year OKX archive | 34 symbols × 32,808 bars, 0 gaps, `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/okx_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 multi-year Binance archive | 33/34 symbols × 32,808 bars, 0 gaps (MINA incomplete), `fabricated_data=false`, `is_hyperliquid_venue_data=false` | `research_state/archives/binance_um_1h_multiyear_20230101_20260928/SOURCE.json` |
| C6 campaign OKX | 42 trades; +18,220.86; +5.07%/yr; 19 eps / 23 crash days | `campaign_results_real_okx_multiyear.json` |
| C6 campaign Binance | 42 trades; +21,994.06; +6.03%/yr; 19 eps / 23 crash days | `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | bootstrap 95% CI [−50,660.49, +99,295.03] P(>0)=0.6649; permutation p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C7 robustness OKX | **`FRAGILE_NOT_DECISION_GRADE`**: buy −27,836.64 / short +46,057.50; LOO drop-2025 → −24,410; drop-ep14 → −11,286; slippage 5× → −13,977; spec-literal → −55,057; buy leg negative all 11 variants | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_grid_20261115T013200Z.{json,md}` |
| C6-T3 episode edge Binance | bootstrap 95% CI [−57,363.40, +122,139.16] P(>0)=0.65425; permutation p=0.1850; **`underpowered`** | `episode_edge_binance_um_multiyear.{json,md}` (2026-11-15T06:05:21Z) |
| C7 robustness Binance | **`FRAGILE_NOT_DECISION_GRADE`**: buy −36,077.66 / short +58,071.73; venue-universal fragility confirmed | `multiyear_robustness_battery_binance_um.{json,md}` (2026-11-15T06:29:02Z) |
| **Consolidated verdict** | **`NO_GO`** (0/7 stop/go criteria pass); Hyperliquid-native only path to GO | `decision_verdict_consolidated_20261115T063642Z.md` |
| Latest Hyperliquid retention probe | **2026-11-15T06:40Z**; 3,869/6,792 bars max; earliest 2026-04-20T19:00Z; `FULL_283D_BLOCKED_BY_API_RETENTION` | `research_state/hyperliquid_retention_probe.json` |
| Latest intake validation | **2026-11-15T06:40Z**; `REJECT_NOT_EVIDENCE`; placeholder parquet never evidence | `research_state/archive_intake_validation_20261115T064010Z.{json,md}` |
| Retained Hyperliquid chain | 24 × 3,885 bars; 11 RSI crashes / 0 confirmed signals; 4 crash days | `.../hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` |
| Canonical OKX 283d (cross-venue) | 8 trades; +9,159.69; `underpowered` | `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`) |
| **Remaining non-HL work (C10)** | C10.1 cross-venue paired agreement (missing); C10.2 Binance portfolio placebo (missing); C10.3 pooled OKX+Binance episode meta (missing) | new stems to be created |

---

## Bottlenecks (current) — what is removable vs not

1. **Cross-venue inference/fragility (OKX, Binance) — REMOVED (C8).** C6-T3 + C7 on both venues; consolidated `NO_GO`.
2. **Hyperliquid-native bottleneck — EXTERNAL, NOT agent-removable.** Public API serves ~3,869/6,792 bars (decaying); no 283d native archive here. Only an operator-supplied verified archive unblocks it. **Do not wait — execute C10.**
3. **Handoff citation drift (gate red) — REMOVED (C9).** `C6-T1` token and Phase O timestamp `2026-11-13T23:38:47Z` restored via the gate-token contract.
4. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
5. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
6. **Retention decay / wasted re-fetch — REMOVED.** Do not re-fetch a degraded chain.
7. **Structural 0-trade funnel (canonical Hyperliquid path) — RESOLVED as a known property.** Canonical gate produces 0 trades on retained partial chain.
8. **C9 "verify-only" loop — REMOVED (C9→C10).** C10 replaces the exhausted verify-only path with real heavy computation.

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

# Gates (all must be green to close any session)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS

# Hyperliquid readiness (mandatory, read-only)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py

# C9 step 2 (only if intake returns ACCEPT_AS_EVIDENCE_CANDIDATE):
# follow research_state/operator_archive_request_20261114T221003Z.{json,md}
# then run Hyperliquid-native campaign + C6-T3 + C7 with NEW stems, produce
# decision_verdict_hyperliquid_native_<TS>Z.md and update consolidated verdict.

# C10 (execute when Hyperliquid archive absent — the current state):
# See "INITIAL TASK MESSAGE" above for C10.0–C10.4 exact steps.
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite.** C9 is complete; execute C10 (cross-venue paired agreement, Binance placebo, pooled episode meta) — never manufacture evidence.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling the placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache or the epoch-timestamp parser fix.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.** Cross-venue result is `NO_GO` / `FRAGILE_NOT_DECISION_GRADE` (core buy leg negative, short-leg-carried, concentrated, cost/entry fragile).
- **Do not remove the gate-token contract tokens** (they are machine-checked by `session_gate.py` and `verify_next_focus_campaign.py`).

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 cross-venue validation COMPLETE (decision-grade):** Binance C6-T3+C7 done; consolidated verdict `research_state/decision_verdict_consolidated_20261115T063642Z.md` = **`NO_GO`** (0/7 stop/go). **C9 external-block confirmation COMPLETE:** Hyperliquid retention 3,869/6,792 bars; intake `REJECT_NOT_EVIDENCE`; gate citation drift fixed. Fragility is venue-universal across OKX/Binance (underpowered CIs, buy leg negative, short-leg-carried, concentrated, stress-fragile). **Hyperliquid-native validation remains blocked on an operator archive and is the only path to a potential `GO`.** Do not promote point estimates to evidence.

**Next session's done (C10):** (a) C10.0 gates confirmed; (b) C10.1 `cross_venue_paired_agreement_<TS>Z.{json,md}`, C10.2 `placebo_portfolio_binance_um_multiyear.{json,md}`, C10.3 `pooled_episode_meta_okx_binance_<TS>Z.{json,md}` each produced with a real verdict; (c) C10.4 consolidated section written (`decision_verdict_consolidated_<TS>Z.md`); (d) all three gates green (C6 PASS, 21/21, 4/4); (e) this handoff re-timestamped with C10 artifact stems and verdicts — with no fabricated evidence of any kind. If the Hyperliquid operator archive lands mid-session, prefer C9-step-2 (Hyperliquid-native end-to-end) over C10.

(End of file)