# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T06:50:30Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session, 2026-11-15T06:50Z):** branch `main`; **C1–C9 COMPLETE; C10 PARTIALLY EXECUTED.** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, and `scripts/verify_next_focus_campaign.py` **PASS** (all green at 2026-11-15T06:50Z). Consolidated verdict remains **`NO_GO`** (edge not established/fragile; Hyperliquid-native evidence absent). **This is the single durable handoff. If your only instruction is the recurring "leave a timestamped initial task" meta-prompt, DO NOT rewrite this handoff for its own sake — finish C10 below.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T06:50:30Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C9 are COMPLETE and C10 is partially executed with real computation (see "C10 status"). **Do NOT repeat completed C10 substeps, do NOT re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new stem and documented reason, and do NOT rewrite this handoff for its own sake.**

**Your job is to FINISH C10 end to end (complete C10.2, integrate, and re-gate) with real computation and no fabricated evidence.** Hyperliquid-native path remains externally blocked (retention 2026-11-15T06:44Z probe: 3,869/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION`; intake `REJECT_NOT_EVIDENCE` on placeholder). Work in order.

### C10 status (as of 2026-11-15T06:50Z)
- **C10.0 — gates/blocker (DONE):** `verify_next_focus_campaign.py` PASS; `session_gate.py` 21/21; `verify_campaign_evidence.py` 4/4; `probe_hyperliquid_blocker.py` + `validate_hyperliquid_archive_intake.py` run (2026-11-15T06:44Z) — no `ACCEPT_AS_EVIDENCE_CANDIDATE`.
- **C10.1 — cross-venue paired symbol/date agreement (DONE):** `scripts/cross_venue_paired_agreement.py` + artifacts `research_state/cross_venue_paired_agreement_20261115T064738Z.{json,md}`. Verdict **`DIRECTION_REPLICATES_MAJORITY`** (32 matched 1:1 pairs, same-sign rate 1.0000, mean diff OKX−Bin −454.03, 95% CI [−1057.09,+11.00]; by-leg buy/short same-sign 1.0). Direction replicates for matched pairs; magnitudes/unpaired admissions differ. `is_hyperliquid_venue_data=false`.
- **C10.2 — Binance C6-T3 portfolio placebo (IN PROGRESS / MUST COMPLETE):** script `scripts/run_portfolio_placebo_binance_um_multiyear.py` created (venue-parameterized, real engine, gates/sizing/cap/occupancy/hedge/fees/funding/liquidation preserved). A 200-draw run (seed 20261114, out `placebo_portfolio_binance_um_multiyear`) was started in-session but **no artifact exists yet** at `research_state/placebo_portfolio_binance_um_multiyear.{json,md}`. **Action:** check if a prior process is still running; if not, run to completion: `PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py --draws 200 --seed 20261114 --out placebo_portfolio_binance_um_multiyear` (may be long-running; use sufficient timeout/background and verify artifact is written with a real verdict).
- **C10.3 — pooled OKX+Binance episode meta (DONE):** `scripts/pooled_episode_meta_okx_binance.py` + artifacts `research_state/pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`. 38 pooled independent venue-episodes (OKX 19 + Binance 19). Observed +40,214.92; bootstrap 95% CI **[−69,065.03,+168,946.87]**, P(total>0)=0.74095; sign-flip perm p(one-sided)=0.26955, p(two-sided)=0.53560. Verdict **`underpowered`**. `is_hyperliquid_venue_data=false`.
- **C10.4 — consolidated verdict update (PARTIAL):** `research_state/decision_verdict_consolidated_20261115T064738Z.md` written integrating C10.1/C10.3 and noting C10.2 pending. **Must be finalized** once C10.2 completes (new stem or explicit finalized update) and overall verdict re-mapped (expect `NO_GO` unchanged absent verified Hyperliquid-native archive).

### Required next actions (finish C10)
1. **C10.2 completion (heavy, real):** produce `research_state/placebo_portfolio_binance_um_multiyear.{json,md}` with real verdict (`underpowered`/other) and `p(placebo ≥ canonical)`, `is_hyperliquid_venue_data=false`. Do not fabricate or skip.
2. **Finalize C10.4:** write a new consolidated stem `research_state/decision_verdict_consolidated_<TS>Z.md` that includes C10.2 results and integrates C10.1–C10.3, re-mapping the 7 stop/go criteria. Keep overall verdict **`NO_GO`** unless (and only if) a verified Hyperliquid-native archive is ingested. Do not overwrite `decision_verdict_consolidated_20261115T063642Z.md` or `20261115T064738Z.md` — cite and add a new stem.
3. **Gates (all green):** `verify_next_focus_campaign.py` PASS, `session_gate.py` 21/21, `verify_campaign_evidence.py` 4/4.
4. **Handoff close:** re-timestamp this single durable handoff with exact C10.1–C10.3 stems+verdicts, C10.2 artifact stem+verdict, and finalized consolidated stem — keeping gate-token contract intact.

**If a verified Hyperliquid operator archive lands mid-session:** prefer C9-step-2 (Hyperliquid-native end-to-end campaign + C6-T3 + C7 with NEW stems, `decision_verdict_hyperliquid_native_<TS>Z.md`, update consolidated) over further cross-venue refinement.

**Binding constraints (unchanged):** cross-venue evidence is NOT Hyperliquid evidence (`is_hyperliquid_venue_data=false`); no synthetic/fabricated data; no new handoff/status files (this file only); no unnecessary re-runs of canonical OKX/Binance multi-year campaigns/censuses/C6-T3/C7 without new stem+reason; do not relax $5M volume floor or spec-literal opt-in default; do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.

**Definition of done (C10 complete):** C10.2 artifact with real verdict exists; C10.4 finalized consolidated stem written including C10.2; all three gates green; this handoff re-timestamped with all C10 artifact stems and verdicts — no fabricated evidence.

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

## What changed this session (C10 partial — 2026-11-15T06:42Z–06:50Z)

- **C10.0 confirmed:** all gates green (C6 PASS, 21/21, 4/4). Hyperliquid probe 2026-11-15T06:44Z: 3,869/6,792 bars, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:2`. Intake 2026-11-15T06:44Z: `REJECT_NOT_EVIDENCE` (`archive_intake_validation_20261115T064406Z.{json,md}`) — placeholder not evidence.
- **C10.1 completed (real):** `scripts/cross_venue_paired_agreement.py` added; `research_state/cross_venue_paired_agreement_20261115T064738Z.{json,md}`. Verdict **`DIRECTION_REPLICATES_MAJORITY`** (32/32 same-sign matched pairs, mean diff −454.03, 95% CI [−1057.09,+11.00]). `is_hyperliquid_venue_data=false`.
- **C10.2 started (heavy, pending artifact):** `scripts/run_portfolio_placebo_binance_um_multiyear.py` added (venue-parameterized real-engine placebo). 200-draw run (seed 20261114) started; `research_state/placebo_portfolio_binance_um_multiyear.{json,md}` not yet written — **must be completed next session**.
- **C10.3 completed (real):** `scripts/pooled_episode_meta_okx_binance.py` added; `research_state/pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`. 38 pooled episodes, total +40,214.92, 95% CI [−69,065.03,+168,946.87], P(>0)=0.74095, perm p=0.26955 (1-sided). Verdict **`underpowered`**. `is_hyperliquid_venue_data=false`.
- **C10.4 partial:** `research_state/decision_verdict_consolidated_20261115T064738Z.md` written (C10.1/C10.3 integrated, C10.2 pending). Overall verdict **`NO_GO`** unchanged.

### Prior bottleneck removals still in force
- Cross-venue multi-year OKX/Binance archives/caches/campaigns/censuses/C6-T3/C7 on disk; OKX placebo done.
- RSI incremental cache (O(1)/bar) and epoch timestamp parsing fix — do not revert.
- Hyperliquid public API retention ~3,869/6,792 bars (decaying tail) — full 283d native archive not on disk; external/operator-only.
- Handoff duplication removed: this file is the only durable handoff.
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.
- Gate citation drift fixed (C9): `C6-T1` token and Phase O timestamp `2026-11-13T23:38:47Z` intact.

---

## Verified state (as of 2026-11-15T06:50Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** (C6-T1 multi-year OKX artifacts complete) | `scripts/verify_next_focus_campaign.py` |
| C6 campaign OKX/Binance | 42/42 trades; +18,220.86/+21,994.06; `is_hyperliquid_venue_data=false` | `campaign_results_real_okx_multiyear.json`, `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | CI [−50,660.49,+99,295.03] P(>0)=0.6649; perm p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C7 robustness OKX | **`FRAGILE_NOT_DECISION_GRADE`** | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}` |
| C6-T3 episode edge Binance | CI [−57,363.40,+122,139.16] P(>0)=0.65425; perm p=0.1850; **`underpowered`** | `episode_edge_binance_um_multiyear.{json,md}` |
| C7 robustness Binance | **`FRAGILE_NOT_DECISION_GRADE`** | `multiyear_robustness_battery_binance_um.{json,md}` |
| **C10.1 paired agreement** | **`DIRECTION_REPLICATES_MAJORITY`** (32 pairs, same-sign 1.0, mean diff −454.03, CI [−1057.09,+11.00]) | `cross_venue_paired_agreement_20261115T064738Z.{json,md}` |
| **C10.2 Binance placebo** | **PENDING** — script ready, artifact not yet written | `scripts/run_portfolio_placebo_binance_um_multiyear.py` (run needed) |
| **C10.3 pooled meta** | **`underpowered`** (38 eps, +40,214.92, CI [−69,065.03,+168,946.87], P(>0)=0.74095, perm p=0.26955) | `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}` |
| **Consolidated verdict** | **`NO_GO`** (unchanged; C10.1/C10.3 integrated, C10.2 pending) | `decision_verdict_consolidated_20261115T064738Z.md` (cites `20261115T063642Z.md`) |
| Hyperliquid readiness | 3,869/6,792 bars; `FULL_283D_BLOCKED_BY_API_RETENTION`; intake `REJECT_NOT_EVIDENCE` | `hyperliquid_retention_probe.json`, `archive_intake_validation_20261115T064406Z.{json,md}` |
| Canonical OKX 283d (cross-venue) | 8 trades; +9,159.69; `underpowered` | `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`) |

---

## Bottlenecks (current)

1. **C10.2 Binance portfolio placebo artifact — REMOVABLE (in progress).** Script exists; 200-draw run must complete and write `placebo_portfolio_binance_um_multiyear.{json,md}`. **Top priority for next session.**
2. **C10.4 final consolidated stem including C10.2 — REMOVABLE** after C10.2 completes.
3. **Hyperliquid-native bottleneck — EXTERNAL, NOT agent-removable.** Public API serves ~3,869/6,792 bars; no 283d native archive here. Only an operator-supplied verified archive unblocks it.
4. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
5. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
6. **Retention decay / wasted re-fetch — REMOVED.** Do not re-fetch a degraded chain.
7. **Structural 0-trade funnel (canonical Hyperliquid path) — RESOLVED as known property.**

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Multi-year archives/caches/universes/campaigns/censuses (OKX, Binance UM, `is_hyperliquid_venue_data=false`) under `research_state/archives/`, `research_state/cache/`, `universe_*_multiyear_verified.json`, `campaign_results_real_{okx,binance_um}_multiyear.*`, `crash_event_census_real_{okx,binance_um}_multiyear.*`.
- C6-T3/C7: `episode_edge_{okx,binance_um}_multiyear.{json,md}`, `placebo_portfolio_okx_multiyear.{json,md}`, `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_grid_20261115T013200Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}`.
- C10 new: `cross_venue_paired_agreement_20261115T064738Z.{json,md}`, `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`, `decision_verdict_consolidated_20261115T064738Z.md`, scripts `scripts/cross_venue_paired_agreement.py`, `scripts/pooled_episode_meta_okx_binance.py`, `scripts/run_portfolio_placebo_binance_um_multiyear.py`.
- Canonical verdict C8: `decision_verdict_consolidated_20261115T063642Z.md` (**`NO_GO`**).
- Canonical OKX 283d: `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`).
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — NEVER evidence.
- Retained Hyperliquid partial chain: `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24×3885).

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh

# Gates (all must be green)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS

# Hyperliquid readiness (mandatory, read-only)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py

# C10 completed artifacts (do not rerun)
# C10.1: research_state/cross_venue_paired_agreement_20261115T064738Z.{json,md}
# C10.3: research_state/pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}

# C10.2 (MUST COMPLETE — heavy)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_portfolio_placebo_binance_um_multiyear.py \
  --draws 200 --seed 20261114 --out placebo_portfolio_binance_um_multiyear
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite.** Finish C10.2 + finalize C10.4 with real artifacts.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache or the epoch-timestamp parser fix.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not adopt/point coverage at degraded 134000Z, 144000Z, 144234Z, 145453Z, or 151710Z aligned chains.**
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove the gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 `NO_GO`** (0/7 stop/go). **C9 external-block confirmed.** **C10 in progress:** C10.1 `DIRECTION_REPLICATES_MAJORITY` (`cross_venue_paired_agreement_20261115T064738Z`), C10.3 `underpowered` (`pooled_episode_meta_okx_binance_20261115T064738Z`), consolidated partial `decision_verdict_consolidated_20261115T064738Z.md`; **C10.2 Binance placebo artifact pending**. Hyperliquid-native validation remains blocked on an operator archive and is the only path to a potential `GO`.

**Next session's done (C10 complete):** (a) `research_state/placebo_portfolio_binance_um_multiyear.{json,md}` exists with real verdict; (b) finalized `decision_verdict_consolidated_<TS>Z.md` includes C10.2; (c) all three gates green (C6 PASS, 21/21, 4/4); (d) this handoff re-timestamped with all C10 artifact stems and verdicts — no fabricated evidence. If verified Hyperliquid operator archive lands, prefer C9-step-2 Hyperliquid-native end-to-end.

(End of file)
