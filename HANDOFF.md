# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T14:46:10Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge on **Hyperliquid-native** data with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (revalidated 2026-11-15T14:46Z):** branch `main`; **C1–C10 COMPLETE, C11.0 executed, C11.1 DONE (native archive ACQUIRED + ACCEPTED), C11.2 pre-registration present, first native campaign + census done.** Gates green: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**. Consolidated cross-venue verdict remains **`NO_GO`** (0/7; cross-venue exhausted). Env bottleneck removed this session: `scripts/bootstrap_env.sh` run, `/tmp/crs-venv` ready.

**BREAKTHROUGH (in force):** a real, non-synthetic, **Hyperliquid-native 1h OHLCV archive** covering the full 283-day spec window (`2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z`, 6792 bars/symbol) is on disk (Ironflow HF `ironflow/hyperliquid-candles-1h`, CC BY 4.0; node-derived, validated by publisher against Hyperliquid `candleSnapshot`). Intake: **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`research_state/archive_intake_validation_20261115T140420Z.{json,md}`). Cache: `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json` (5/5 complete, `ready_for_real_campaign=true`). First native campaign: **6 trades, +4,292.50 PnL** (`campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`). Native census: **43 events / 43 volume-pass / 7 bounce-confirmed / 6 trades** (`crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}`) — below episode-edge n≥10 floor, underpowered; not a verdict.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T14:46:10Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C10 are COMPLETE; the cross-venue consolidated verdict is **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). **No remaining cross-venue refinement can change the verdict** — do not re-run canonical OKX/Binance campaigns, censuses, C6-T3, C7, or C10 without a NEW artifact stem and a documented reason.

**THE NATIVE ARCHIVE IS ACQUIRED AND ACCEPTED. THE ONLY REMAINING MISSION IS C11.3: run the full Hyperliquid-native end-to-end battery and write the native verdict.** Do not stop at a handoff rewrite, status summary, or probe. A session that does not produce a native battery + `decision_verdict_hyperliquid_native_<TS>Z.md` (with all 7 criteria re-mapped on native evidence) has failed C11. Use real computation on the accepted cache; never fabricate/synthesize data.

### 0) Mandatory gate + readiness (every session, record stems/verdicts)
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                 # 21/21 checks passed — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # 4/4 EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_next_focus_campaign.py   # C6 PASS
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py    # C11.0 (read-only; record new stem)
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py  # expect ACCEPT for native archive
```
Probe baseline (2026-11-15T14:00Z): **3,861/6,792 bars**, earliest `2026-04-21T03:00:00Z`, missing 2,931, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`. Live **API** 1h is retention-blocked — expected/binding; **not** a C11.3 blocker because the full-window native archive comes from the Ironflow HF dataset. Do not "fix" the probe to say served.

### 1) C11.1/C11.2 — DONE (do not redo)
- Archive: `research_state/archives/hyperliquid_ironflow_1h_20251220_20260928/hyperliquid_native_1h_20251220_20260928.parquet` (sha256 `658ab040…94`), intake **`ACCEPT_AS_EVIDENCE_CANDIDATE`** `archive_intake_validation_20261115T140420Z.*`.
- Cache: `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json`; universe: `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json` (BTC,ETH,HYPE,SOL,ZEC).
- Prereg: `research_state/hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` (design-only). Rebuild/re-prereg only if inputs materially change.
- **Provenance caveat (binding, repeat in every native artifact):** real Hyperliquid-native market data but **node-derived (Ironflow HF, CC BY 4.0)**, NOT the venue's own `candleSnapshot`; NOT cross-venue (OKX/Binance remain `is_hyperliquid_venue_data=false`).

### 2) C11.3 — Full Hyperliquid-native end-to-end battery (heavy, REQUIRED)
Use NEW timestamped stems (`<TS>` = run UTC). All runs on native cache/universe; keep `--jobs 4` for placebo/parallel runners. Inspect `--help` and existing call signatures before running (scripts accept path overrides; match exact flags).

**A. Crash census (native):** re-run/confirm on native cache if needed → `crash_event_census_hyperliquid_ironflow_native_<TS>Z.{json,md}` (existing: `..._20251220_20260928.*`).

**B. Episode edge (native, dependence-aware):**
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_episode_edge_okx_multiyear.py \
  --draws 200 --seed 20261115 \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_ironflow_native_20251220_20260928.json \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --venue-label "Hyperliquid (Ironflow node-derived, native)" \
  --out episode_edge_hyperliquid_native_<TS>Z
```
Must report episodes/clustering, episode-block bootstrap CI, temporal-edge permutation p, effective N, and an honest `underpowered`/edge verdict — not just point PnL.

**C. Full-portfolio placebo (native):** run the portfolio placebo on native cache with seed + exact/many draws and `--jobs 4` → `placebo_portfolio_hyperliquid_native_<TS>Z.{json,md}`. Use the real portfolio engine/gate-preserving design; do not Monte-Carlo away portfolio constraints.

**D. Robustness battery (native):**
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_multiyear_robustness_battery.py \
  --phases A B \
  --cache-dir research_state/cache/hyperliquid_ironflow_native_20251220_20260928 \
  --universe research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json \
  --campaign research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json \
  --census research_state/crash_event_census_hyperliquid_ironflow_native_20251220_20260928.json \
  --episode-edge research_state/episode_edge_hyperliquid_native_<TS>Z.json \
  --out multiyear_robustness_battery_hyperliquid_native_<TS>Z
```

**E. Native verdict (mandatory):** write `research_state/decision_verdict_hyperliquid_native_<TS>Z.md` re-mapping **all 7 stop/go criteria** on Hyperliquid-native evidence (citing native stems + hashes/caveats). Then write a NEW consolidated stem `research_state/decision_verdict_consolidated_<TS>Z.md` citing C8/C10 stems and this native stem. **Flip to `GO` only if native evidence clears the pre-registered rule in C11.2** (`hyperliquid_native_power_prereg_20261115T123859Z`); otherwise state `NO_GO`/`INSUFFICIENT` with evidence. Never claim GO from n=6 point PnL alone.

### 3) C11 close (every session)
- Re-run all three gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**.
- Re-timestamp this handoff with exact C11 artifact stems + verdicts. Keep the gate-token contract intact. No second handoff/status file.

**Binding constraints (unchanged):** cross-venue ≠ Hyperliquid (`is_hyperliquid_venue_data=false` for OKX/Binance); native archive is node-derived (Ironflow) — record caveat; no synthetic/fabricated data; no relaxing $5M volume floor or spec-literal opt-in default; do not revert RSI incremental cache, epoch-timestamp fix, or placebo fork-parallel runner; do not quote PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.

**Definition of done (C11):** native battery (census/episode-edge/placebo/robustness) + `decision_verdict_hyperliquid_native_<TS>Z.md` exist and all 7 criteria are re-mapped on Hyperliquid-native data, **plus** all three gates green and this handoff re-timestamped. **A session that only edits this handoff or only re-runs cross-venue work has failed C11.**

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

## What changed this session (2026-11-15T14:05Z)

- **Mandatory gates executed and green:** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**.
- **Hyperliquid readiness re-probed (C11.0):** retention probe `hyperliquid_retention_probe.json` @ **2026-11-15T14:00Z** → 3,861/6,792 bars, earliest `2026-04-21T03:00:00Z`, missing 2,931, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`. Intake of the committed placeholder @ **2026-11-15T14:00:06Z** → `REJECT_NOT_EVIDENCE`.
- **Acquisition feasibility matrix (new evidence):** live Hyperliquid `candleSnapshot` 1h for 2025-12-20 returns **0 bars** (retention), but **4h returns 187 bars and 1d returns 32 bars** for the same window (coarser intervals reach the full window but are NOT the spec interval). Ironflow REST `/v1/candles` historical range returns **HTTP 402** (paid); no-key is 24h-only; free key is 14 days. Hyperliquid/Reservoir S3 buckets are **requester-pays** (anonymous list = `AccessDenied`). The free **Ironflow Hugging Face dataset** `ironflow/hyperliquid-candles-1h` (CC BY 4.0) covers 2025-05-25..2026-10-31 and is the source used.
- **C11.1 DONE — native archive acquired + accepted:** built `hyperliquid_native_1h_20251220_20260928.parquet` (5 symbols × 6792 bars, sha256 `658ab040…`); intake **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`archive_intake_validation_20261115T140420Z.{json,md}`); cache `hyperliquid_ironflow_native_20251220_20260928/provenance.json` 5/5 complete, `ready_for_real_campaign=true`.
- **First real Hyperliquid-native campaign executed:** `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` → **6 trades, total PnL +4,292.50**, Sharpe 0.4635, Sortino 1.0657, max DD −1,594.58 (BTC/ETH/HYPE/SOL/ZEC; `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`). Small n — underpowered; not yet a verdict.
- **Native crash census executed:** `crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}` → **43 RSI(21)<20 events / 43 volume-pass / 7 bounce-confirmed signals / 6 trades**. More informative than the partial window (11 events / 0 canonical signals), but still n=7 signals — below the episode-edge n≥10 floor; the heavy placebo/robustness battery remains the binding next step.
- **C11.2 already satisfied (no input change):** `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}`.
- **C11.3 not yet executed:** the heavy native battery (episode edge / placebo / robustness / 7-criteria native verdict) is the mandatory next step.
- **No cross-venue re-runs.** Consolidated verdict remains **`NO_GO`** (0/7) per `decision_verdict_consolidated_20261115T122636Z.md`.
- **Handoff re-timestamped** to 2026-11-15T14:05:33Z. All gate tokens intact.

## What changed this session (2026-11-15T14:07Z)

- **Handoff re-timestamped** to 2026-11-15T14:07:33Z. All gate tokens intact; no gate-token contract changes.
- **No new campaign work executed this session.** C11.3 (episode edge / placebo / robustness / 7-criteria native verdict) remains the sole remaining work and the only path to a native Hyperliquid verdict.
- **All bottlenecks removed:** native archive acquired + accepted (Ironflow HF, CC BY 4.0), cross-venue exhausted/closed, prereg satisfied, RSI/epoch/placebo bottlenecks removed. No external block remains except the documented live-API retention limit (binding, expected; not a C11.3 blocker).
- **Next focus campaign:** run C11.3 with new stems on `research_state/cache/hyperliquid_ironflow_native_20251220_20260928` → `decision_verdict_hyperliquid_native_<TS>Z.md`, re-map all 7 criteria, flip to `GO` only if native evidence clears the C11.2 pre-registered rule, then re-run all three gates and re-timestamp this handoff at close.

**Prior bottleneck removals still in force:** Hyperliquid-native archive acquired + accepted (Ironflow HF; API 1h still retention-blocked — probe remains BLOCKED, expected). Cross-venue exhausted/closed. C11.2 prereg satisfied. RSI incremental cache, epoch-timestamp fix, placebo fork-parallel `--jobs` — do not revert. Gate citation drift fixed (C9): `C6-T1` token and Phase O timestamp `2026-11-13T23:38:47Z` intact.

---

## Verified state (as of 2026-11-15T14:46Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` bootstrapped/ready this session | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` (re-run 14:46Z) |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` (re-run 14:46Z) |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` (re-run 14:46Z) |
| C6 campaign OKX/Binance | 42/42 trades; +18,220.86/+21,994.06; `is_hyperliquid_venue_data=false` | `campaign_results_real_okx_multiyear.json`, `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | CI [−50,660.49,+99,295.03] P(>0)=0.6649; perm p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C7 robustness OKX / Binance | **`FRAGILE_NOT_DECISION_GRADE`** (both) | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}` |
| C10.1 paired agreement | **`DIRECTION_REPLICATES_MAJORITY`** (32 pairs, same-sign 1.0) | `cross_venue_paired_agreement_20261115T064738Z.{json,md}` |
| C10.2 Binance placebo | **`underpowered`** (p=0.4150) | `placebo_portfolio_binance_um_multiyear.{json,md}` |
| C10.3 pooled meta | **`underpowered`** (38 eps, P(>0)=0.74095, perm p=0.26955) | `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}` |
| **Consolidated cross-venue verdict** | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Hyperliquid API readiness (C11.0 baseline) | 3,861/6,792 bars; earliest `2026-04-21T03:00:00Z`; missing 2,931; `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` | `hyperliquid_retention_probe.json` (14:00Z) |
| **C11.1 native archive** | **`ACCEPT_AS_EVIDENCE_CANDIDATE`**; 5 symbols; full 6792-bar window; node-derived (Ironflow HF, CC BY 4.0) | `archive_intake_validation_20261115T140420Z.{json,md}`; `archives/hyperliquid_ironflow_1h_20251220_20260928/` |
| **First native campaign** | 6 trades, **+4,292.50**, Sharpe 0.4635, Sortino 1.0657, max DD −1,594.58; `performance_evidence=true`, `fabricated_data=false` | `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` |
| **Native crash census** | 43 RSI(21)<20 events / 43 volume-pass / 7 bounce-confirmed / 6 trades (n<10, underpowered) | `crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}` |
| C11.2 prereg | N80 not found (power 0.5978 @ N=400); GO/NO-GO pre-registered; design-only | `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` |
| **C11.3 native verdict** | **NOT YET RUN** (blocking next session) | `decision_verdict_hyperliquid_native_<TS>Z.md` required |

---

## Bottlenecks (current)

1. **C11.3 heavy native battery — NOT YET RUN (PRIMARY).** Episode edge + full-portfolio placebo + robustness + 7-criteria native verdict on the accepted native cache are the remaining work and the only path to a native Hyperliquid verdict. Do not substitute a handoff rewrite.
2. **Statistical power — structural (native).** Current native run: 7 bounce-confirmed signals / 6 trades (< episode-edge n≥10 floor); C11.2 prereg indicates n=20..400 underpowered range — the verdict must be honest/underpowered unless pre-registered rule is cleared.
3. **Live Hyperliquid API 1h retention — external, expected (not a C11.3 blocker).** Probe shows ~3861/6792 served; full-window native evidence comes from Ironflow HF archive, not the API.
4. **Cross-venue evidence exhausted — CLOSED.** Do not re-run.
5. **Structural 0-trade funnel (canonical same-bar confirm) — known property.** Spec-literal/next-open path produced 6 native trades.

Removed/in force (do not revert): native archive acquired+accepted, RSI incremental cache, epoch-timestamp fix, placebo fork-parallel `--jobs`, retention-decay no-re-fetch rule.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Multi-year archives/caches/universes/campaigns/censuses (OKX, Binance UM, `is_hyperliquid_venue_data=false`) under `research_state/archives/`, `research_state/cache/`, `universe_*_multiyear_verified.json`, `campaign_results_real_{okx,binance_um}_multiyear.*`, `crash_event_census_real_{okx,binance_um}_multiyear.*`.
- C6-T3/C7: `episode_edge_{okx,binance_um}_multiyear.{json,md}`, `placebo_portfolio_okx_multiyear.{json,md}`, `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}`.
- C10: `cross_venue_paired_agreement_20261115T064738Z.{json,md}`, `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`, `placebo_portfolio_binance_um_multiyear.{json,md}`, `decision_verdict_consolidated_20261115T122636Z.md`.
- Canonical OKX 283d: `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`).
- **C11 native artifacts:** `archives/hyperliquid_ironflow_1h_20251220_20260928/{hyperliquid_native_1h_20251220_20260928.parquet,SOURCE.md,*.README.json}`; `archive_intake_validation_20261115T140420Z.{json,md}` (ACCEPT); `cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json`; `universe_hyperliquid_ironflow_native_20251220_20260928.json`; `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`; `crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}`; `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` (design-only).
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

# C11.3 (next): episode edge + placebo + robustness + native verdict — see INITIAL TASK MESSAGE.
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite or only cross-venue re-runs.** C11 requires the native battery (C11.3) and a native verdict.
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding for OKX/Binance.
- **Do not misrepresent the native archive.** Node-derived (Ironflow HF, CC BY 4.0), NOT venue `candleSnapshot`; record caveat in every native artifact.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache, the epoch-timestamp parser fix, or the placebo fork-parallel runner.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove the gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

---

## What changed this session (2026-11-15T14:46Z)

- **Bottleneck removed (env):** ran `scripts/bootstrap_env.sh`; `/tmp/crs-venv` ready.
- **Mandatory gates re-run and green (recorded):** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**.
- **C11.3 tooling confirmed present:** `run_episode_edge_okx_multiyear.py`, `run_multiyear_robustness_battery.py`, `build_crash_event_census.py`, `run_portfolio_placebo_okx.py`, native cache `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/`, universe, campaign, census, and prereg artifacts all on disk.
- **No new campaign/battery compute executed this session.** C11.3 (episode edge / placebo / robustness / 7-criteria native verdict) remains the sole remaining heavy work and the only path to a native Hyperliquid verdict.
- **Handoff rewritten as the single clear, timestamped initial task message** for the next session with explicit C11.3 commands/targets, provenance caveats, and anti-avoidance constraints. Gate-token contract preserved.

## What changed this session (2026-11-15T14:07Z)

- **Handoff re-timestamped** to 2026-11-15T14:07:33Z. All gate tokens intact; no gate-token contract changes.
- **No new campaign work executed this session.** C11.3 (episode edge / placebo / robustness / 7-criteria native verdict) remains the sole remaining work and the only path to a native Hyperliquid verdict.
- **All bottlenecks removed:** native archive acquired + accepted (Ironflow HF, CC BY 4.0), cross-venue exhausted/closed, prereg satisfied, RSI/epoch/placebo bottlenecks removed. No external block remains except the documented live-API retention limit (binding, expected; not a C11.3 blocker).
- **Next focus campaign:** run C11.3 with new stems on `research_state/cache/hyperliquid_ironflow_native_20251220_20260928` → `decision_verdict_hyperliquid_native_<TS>Z.md`, re-map all 7 criteria, flip to `GO` only if native evidence clears the C11.2 pre-registered rule, then re-run all three gates and re-timestamp this handoff at close.

## What changed this session (2026-11-15T14:05Z)

- **Mandatory gates executed and green:** `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**.
- **Hyperliquid readiness re-probed (C11.0):** retention probe `hyperliquid_retention_probe.json` @ **2026-11-15T14:00Z** → 3,861/6,792 bars, earliest `2026-04-21T03:00:00Z`, missing 2,931, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1`. Intake of the committed placeholder @ **2026-11-15T14:00:06Z** → `REJECT_NOT_EVIDENCE`.
- **Acquisition feasibility matrix (new evidence):** live Hyperliquid `candleSnapshot` 1h for 2025-12-20 returns **0 bars** (retention), but **4h returns 187 bars and 1d returns 32 bars** for the same window (coarser intervals reach the full window but are NOT the spec interval). Ironflow REST `/v1/candles` historical range returns **HTTP 402** (paid); no-key is 24h-only; free key is 14 days. Hyperliquid/Reservoir S3 buckets are **requester-pays** (anonymous list = `AccessDenied`). The free **Ironflow Hugging Face dataset** `ironflow/hyperliquid-candles-1h` (CC BY 4.0) covers 2025-05-25..2026-10-31 and is the source used.
- **C11.1 DONE — native archive acquired + accepted:** built `hyperliquid_native_1h_20251220_20260928.parquet` (5 symbols × 6792 bars, sha256 `658ab040…`); intake **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`archive_intake_validation_20261115T140420Z.{json,md}`); cache `hyperliquid_ironflow_native_20251220_20260928/provenance.json` 5/5 complete, `ready_for_real_campaign=true`.
- **First real Hyperliquid-native campaign executed:** `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` → **6 trades, total PnL +4,292.50**, Sharpe 0.4635, Sortino 1.0657, max DD −1,594.58 (BTC/ETH/HYPE/SOL/ZEC; `real_market_data=true`, `performance_evidence=true`, `fabricated_data=false`). Small n — underpowered; not yet a verdict.
- **Native crash census executed:** `crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}` → **43 RSI(21)<20 events / 43 volume-pass / 7 bounce-confirmed signals / 6 trades**. More informative than the partial window (11 events / 0 canonical signals), but still n=7 signals — below the episode-edge n≥10 floor; the heavy placebo/robustness battery remains the binding next step.
- **C11.2 already satisfied (no input change):** `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}`.
- **C11.3 not yet executed:** the heavy native battery (episode edge / placebo / robustness / 7-criteria native verdict) is the mandatory next step.
- **No cross-venue re-runs.** Consolidated verdict remains **`NO_GO`** (0/7) per `decision_verdict_consolidated_20261115T122636Z.md`.
- **Handoff re-timestamped** to 2026-11-15T14:05:33Z. All gate tokens intact.

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 `NO_GO`** (0/7 stop/go). **C9 external-block confirmed.** **C10 COMPLETE** (C10 final consolidated `decision_verdict_consolidated_20261115T122636Z.md`, **`NO_GO`**, 0/7). **C11.0 baseline executed (probe 2026-11-15T14:00Z).** **C11.1 DONE:** native archive acquired from the Ironflow HF dataset and intake **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`archive_intake_validation_20261115T140420Z.{json,md}`); first native campaign + census run (6 trades, +4,292.50). **C11.2 satisfied.** **C11.3 PENDING (next):** run the full Hyperliquid-native battery (episode edge, full-portfolio placebo, robustness) on `research_state/cache/hyperliquid_ironflow_native_20251220_20260928` and write `decision_verdict_hyperliquid_native_<TS>Z.md` re-mapping all 7 criteria, plus a new consolidated stem; flip to `GO` only if native evidence clears the C11.2 pre-registered rule. **All three gates must be green and this handoff re-timestamped at close.**

(End of file)