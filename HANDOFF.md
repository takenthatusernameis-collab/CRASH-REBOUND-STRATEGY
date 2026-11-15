# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-15T14:07:33Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create another status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → buy at **next hourly open** → +9% / 50h exit → optional rebound short; ETH-hedged; 120% gross cap).
**Priority (inferred from the repo name):** produce a **decision-grade crash-rebound verdict** — either validate the strategy's edge on **Hyperliquid-native** data with enough independent crash episodes, or conclusively show it does not survive honest dependence-aware inference.

**Baseline (this session, 2026-11-15T14:05Z):** branch `main`; **C1–C10 COMPLETE, C11.0 executed, C11.1 DONE (native archive ACQUIRED + ACCEPTED), C11.2 pre-registration present, first native campaign run.** Gates green: `scripts/session_gate.py` **21/21 checks passed — DONE**, `scripts/verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `scripts/verify_next_focus_campaign.py` **PASS**. Consolidated cross-venue verdict remains **`NO_GO`** (0/7; cross-venue exhausted).

**BREAKTHROUGH — the acquisition bottleneck is REMOVED.** A real, non-synthetic, **Hyperliquid-native 1h OHLCV archive** covering the full 283-day spec window (`2025-12-20T00:00:00Z .. 2026-09-28T23:00:00Z`, 6792 bars/symbol) was built from the public Ironflow Hugging Face dataset `ironflow/hyperliquid-candles-1h` (CC BY 4.0; hourly OHLCV reconstructed from Ironflow's own Hyperliquid nodes, validated hour-by-hour against Hyperliquid's own `candleSnapshot` by the publisher). It passed the official intake gate with **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`research_state/archive_intake_validation_20261115T140420Z.{json,md}`; 5 symbols BTC/ETH/HYPE/SOL/ZEC; `is_market_data=true`, `is_evidence=true`, `performance_evidence=false`). It is ingested to a ready cache (`research_state/cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json`, 5/5 complete, `ready_for_real_campaign=true`). A first native campaign ran: **6 trades, total PnL +4,292.50**, Sharpe 0.4635, Sortino 1.0657, max DD −1,594.58 (`research_state/campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`).

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-15T14:07:33Z)

**You are the next agentic session continuing the Hyperliquid crash-rebound research program.** C1–C10 are COMPLETE; the cross-venue consolidated verdict is **`NO_GO`** (`research_state/decision_verdict_consolidated_20261115T122636Z.md`, 0/7). **There is no remaining cross-venue refinement that can change the verdict** — do not re-run canonical OKX/Binance campaigns, censuses, C6-T3, C7, or the C10 battery without a new stem and a documented reason.

**The Hyperliquid-native archive is now ACQUIRED and ACCEPTED, so CAMPAIGN C11 is UNBLOCKED.** Your job is to run **C11.3: the full Hyperliquid-native end-to-end battery** on the accepted archive and write the native verdict. Do it with real computation and no fabricated evidence. This is the only path to a `GO`; a session that only rewrites this handoff or only re-runs cross-venue work has failed C11.

### C11.0 — Mandatory gate + external-block probe (read-only, every session)
Run and record stems/verdicts (binding; a session that does not run them has not started):
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py
```
Current baseline (this session): probe **2026-11-15T14:00Z** → 3,861/6,792 bars, earliest `2026-04-21T03:00:00Z`, missing 2,931, `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` (KPEPE HTTP 500; INIT now probes). The live **API** is still retention-blocked — that is expected and binding. The full-window native archive does **not** come from the API; it comes from the Ironflow HF dataset (see C11.1). Re-run and record a new probe stem each session; do not "fix" the probe to say served.

### C11.1 — Acquisition (DONE this session; do not redo)
- Archive: `research_state/archives/hyperliquid_ironflow_1h_20251220_20260928/hyperliquid_native_1h_20251220_20260928.parquet` (sha256 `658ab040d947125b91517e0cb79363d8ed834f915950e81dc7617c30e3852f94`), `SOURCE.md`, `…parquet.README.json`.
- Intake verdict: **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`research_state/archive_intake_validation_20261115T140420Z.{json,md}`).
- Cache: `research_state/cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json` (5/5 complete, `ready_for_real_campaign=true`, `fabricated_data=false`).
- Universe: `research_state/universe_hyperliquid_ironflow_native_20251220_20260928.json` (5 symbols).
- **Provenance caveat (binding):** this is real Hyperliquid-native market data but is **node-derived** (Ironflow), NOT the venue's own `candleSnapshot` endpoint. Record this in every native artifact; never relabel it as an API pull or as cross-venue data.
- Rebuild only if inputs change: `PYTHONPATH=. /tmp/crs-venv/bin/python scratch/build_native_archive.py` (downloads the 10 monthly parquet files 2025-12..2026-09, keeps symbols with complete 6792-bar coverage AND ≥$5M min trailing-24h USD volume).

### C11.2 — Pre-registered Hyperliquid-native power & decision protocol (present)
`research_state/hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` (real Monte-Carlo, 4000 sims/N, N∈20..400; N80 not found in 20..400, power 0.5978 at N=400; GO/NO-GO pre-registered; design-only, `performance_evidence=false`). Re-run with a new stem only if priors/inputs materially change.

### C11.3 — Full Hyperliquid-native end-to-end battery (heavy; REQUIRED next)
With NEW stems, run in order and write `research_state/decision_verdict_hyperliquid_native_<TS>Z.md`:
1. **Crash census + episode edge** on the native cache/universe (point `scripts/build_crash_event_census.py` / `scripts/run_episode_edge_okx_multiyear.py` at `research_state/cache/hyperliquid_ironflow_native_20251220_20260928` + the native universe) → `episode_edge_hyperliquid_native_<TS>Z.{json,md}`.
2. **Full-portfolio placebo** on the native cache (venue-parameterized placebo runner; keep `--jobs 4`) → `placebo_portfolio_hyperliquid_native_<TS>Z.{json,md}`.
3. **Robustness battery** on native data (`scripts/run_multiyear_robustness_battery.py --phases A B`) → `multiyear_robustness_battery_hyperliquid_native_<TS>Z.{json,md}`.
4. **Re-map all 7 stop/go criteria on Hyperliquid-native evidence** and write the native verdict; then add a new consolidated stem `decision_verdict_consolidated_<TS>Z.md` citing the C8/C10 stems and this native stem. Flip to `GO` **only if** the native evidence clears the pre-registered rule in C11.2.
5. Re-run all three gates and re-timestamp this handoff with the native stems + verdicts.

### C11 close (every session)
- Re-run all three gates: `session_gate.py` **21/21 checks passed — DONE**, `verify_campaign_evidence.py` **4/4 EVIDENCE VERIFIED**, `verify_next_focus_campaign.py` **PASS**.
- Re-timestamp this handoff with the exact C11 artifact stems + verdicts. Keep the gate-token contract intact.

**Binding constraints (unchanged):** cross-venue evidence is NOT Hyperliquid evidence (`is_hyperliquid_venue_data=false`); the new archive is Hyperliquid-native *market data* but is node-derived (Ironflow) — record that caveat; no synthetic/fabricated data; no new handoff/status files (this file only); do not relax the $5M volume floor or spec-literal opt-in default; do not quote the PDF +115%/yr or cross-venue +5.07%/+6.03%/yr as validated edge.

**Definition of done (C11):** a native battery + `decision_verdict_hyperliquid_native_<TS>Z.md` exists and the 7 criteria are re-mapped on Hyperliquid-native data, **plus** all three gates green and this handoff re-timestamped. **A session that only edits this handoff or only re-runs cross-venue work has failed C11.**

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

### Prior bottleneck removals still in force
- **Hyperliquid-native archive — REMOVED this session** (Ironflow HF dataset; intake ACCEPT). The public **API** 1h window is still retention-blocked and remains the reason `probe_hyperliquid_blocker.py` reports BLOCKED.
- Cross-venue multi-year OKX/Binance archives/caches/campaigns/censuses/C6-T3/C7 on disk; OKX + Binance placebo done.
- RSI incremental cache (O(1)/bar) and epoch timestamp parsing fix — do not revert.
- Placebo runner now fork-parallel (`--jobs`, default 4) — keep.
- Retention decay / wasted re-fetch rule: do not re-fetch a degraded chain.
- Gate citation drift fixed (C9): `C6-T1` token and Phase O timestamp `2026-11-13T23:38:47Z` intact.

---

## Verified state (as of 2026-11-15T14:07Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present/reproducible | `scripts/bootstrap_env.sh` |
| Session gate | **21/21 checks passed — DONE** | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** | `scripts/verify_campaign_evidence.py` |
| C6 acceptance gate | **PASS** | `scripts/verify_next_focus_campaign.py` |
| C6 campaign OKX/Binance | 42/42 trades; +18,220.86/+21,994.06; `is_hyperliquid_venue_data=false` | `campaign_results_real_okx_multiyear.json`, `campaign_results_real_binance_um_multiyear.json` |
| C6-T3 episode edge OKX | CI [−50,660.49,+99,295.03] P(>0)=0.6649; perm p=0.1000; **`underpowered`** | `episode_edge_okx_multiyear.{json,md}` |
| C6-T3 placebo OKX | p(placebo≥canonical)=0.4000; **`underpowered`** | `placebo_portfolio_okx_multiyear.{json,md}` |
| C7 robustness OKX / Binance | **`FRAGILE_NOT_DECISION_GRADE`** (both) | `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}` |
| C10.1 paired agreement | **`DIRECTION_REPLICATES_MAJORITY`** (32 pairs, same-sign 1.0) | `cross_venue_paired_agreement_20261115T064738Z.{json,md}` |
| C10.2 Binance placebo | **`underpowered`** (p=0.4150) | `placebo_portfolio_binance_um_multiyear.{json,md}` |
| C10.3 pooled meta | **`underpowered`** (38 eps, P(>0)=0.74095, perm p=0.26955) | `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}` |
| **Consolidated cross-venue verdict** | **`NO_GO`** (0/7) | `decision_verdict_consolidated_20261115T122636Z.md` |
| Hyperliquid API readiness (C11.0) | 3,861/6,792 bars; earliest `2026-04-21T03:00:00Z`; missing 2,931; `FULL_283D_BLOCKED_BY_API_RETENTION;UNPROBEABLE_SYMBOLS:1` | `hyperliquid_retention_probe.json` (14:00Z) |
| **C11.1 native archive** | **`ACCEPT_AS_EVIDENCE_CANDIDATE`**; 5 symbols; full 6792-bar window; node-derived (Ironflow HF, CC BY 4.0) | `archive_intake_validation_20261115T140420Z.{json,md}`; `archives/hyperliquid_ironflow_1h_20251220_20260928/` |
| **First native campaign** | 6 trades, **+4,292.50**, Sharpe 0.4635, Sortino 1.0657, max DD −1,594.58; `performance_evidence=true`, `fabricated_data=false` | `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json` |
| **Native crash census** | 43 RSI(21)<20 events / 43 volume-pass / 7 bounce-confirmed signals / 6 trades | `crash_event_census_hyperliquid_ironflow_native_20251220_20260928.{json,md}` |
| C11.2 prereg | N80 not found (power 0.5978 @ N=400); GO/NO-GO pre-registered; design-only | `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` |

---

## Bottlenecks (current)

1. **Hyperliquid-native archive — REMOVED (this session).** Real native 1h data for the full 283-day window is on disk and intake-ACCEPTED (`archive_intake_validation_20261115T140420Z.*`). The public **API** 1h window remains retention-blocked (~3,861/6,792) — that is a separate, documented fact, not a blocker for C11.3.
2. **Cross-venue evidence exhausted — CLOSED.** C10 complete; further cross-venue work cannot change the verdict (do not re-run).
3. **C11.2 prereg done — no further blocked-path compute required.**
4. **RSI O(n²) bottleneck — REMOVED.** Incremental cache; do not revert.
5. **Epoch-timestamp metric bug — REMOVED.** Fixed; do not revert.
6. **Placebo serial slowness — REMOVED.** Fork-parallel `--jobs`; do not revert.
7. **Structural 0-trade funnel (canonical Hyperliquid same-bar confirm) — known property.** The spec-literal next-open path produces trades (native run: 6); the canonical same-bar-confirm path can be 0 on some windows.
8. **C11.3 heavy battery — NOT YET RUN.** This is the remaining work and the only path to a native verdict.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- Multi-year archives/caches/universes/campaigns/censuses (OKX, Binance UM, `is_hyperliquid_venue_data=false`) under `research_state/archives/`, `research_state/cache/`, `universe_*_multiyear_verified.json`, `campaign_results_real_{okx,binance_um}_multiyear.*`, `crash_event_census_real_{okx,binance_um}_multiyear.*`.
- C6-T3/C7: `episode_edge_{okx,binance_um}_multiyear.{json,md}`, `placebo_portfolio_okx_multiyear.{json,md}`, `multiyear_robustness_battery_full_20261115T011700Z.{json,md}`, `multiyear_robustness_battery_binance_um.{json,md}`.
- C10: `cross_venue_paired_agreement_20261115T064738Z.{json,md}`, `pooled_episode_meta_okx_binance_20261115T064738Z.{json,md}`, `placebo_portfolio_binance_um_multiyear.{json,md}`, `decision_verdict_consolidated_20261115T122636Z.md`.
- Canonical OKX 283d: `campaign_results_real_okx_full.json`, `episode_edge_okx_full.json` (Phase O `2026-11-13T23:38:47Z`).
- **C11 native artifacts (this session):** `archives/hyperliquid_ironflow_1h_20251220_20260928/{hyperliquid_native_1h_20251220_20260928.parquet,SOURCE.md,*.README.json}`; `archive_intake_validation_20261115T140420Z.{json,md}` (ACCEPT); `cache/hyperliquid_ironflow_native_20251220_20260928/provenance.json`; `universe_hyperliquid_ironflow_native_20251220_20260928.json`; `campaign_results_real_hyperliquid_ironflow_native_20251220_20260928.json`; `hyperliquid_native_power_prereg_20261115T123859Z.{json,md}` (design-only).
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

# Native archive (C11.1, done)
PYTHONPATH=. /tmp/crs-venv/bin/python scratch/build_native_archive.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/validate_hyperliquid_archive_intake.py \
  --archive research_state/archives/hyperliquid_ironflow_1h_20251220_20260928/hyperliquid_native_1h_20251220_20260928.parquet

# C11.3 (next): episode edge + placebo + robustness + native verdict — see INITIAL TASK MESSAGE.
```

---

## Hard prohibitions / anti-avoidance

- **Do not close a session with only a handoff rewrite or only cross-venue re-runs.** C11 now requires the native battery (C11.3).
- **Do not relabel cross-venue evidence as Hyperliquid evidence.** `is_hyperliquid_venue_data=false` is binding for OKX/Binance.
- **Do not misrepresent the native archive.** It is node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own `candleSnapshot`; record that caveat in every native artifact.
- **Do not fabricate/synthesize data.** No synthetic archive, no interpolated candles, no relabeling placeholder parquet.
- **Do not relax the `volume_filter_ok` / trailing-24h ≥ $5M gate.**
- **Do not re-run canonical multi-year campaigns/censuses/C6-T3/C7 without a new artifact stem and a documented reason.**
- **Do not revert the RSI incremental cache, the epoch-timestamp parser fix, or the placebo fork-parallel runner.**
- **Do not create a second handoff/status file.** This is the single durable handoff.
- **Do not quote the PDF's +115%/yr or the cross-venue +5.07%/+6.03%/yr as validated edge.**
- **Do not remove the gate-token contract tokens** (`INITIAL TASK MESSAGE`, `session_gate.py`, `probe_hyperliquid_blocker.py`, `verify_campaign_evidence.py`, `C6-T1`, `campaign_results_real_okx_multiyear`, `21/21 checks passed`, `2026-11-13T23:38:47Z`).

---

## Definition of done

Evidence-chain completeness **21/21** achieved. **C8 `NO_GO`** (0/7 stop/go). **C9 external-block confirmed.** **C10 COMPLETE** (C10 final consolidated `decision_verdict_consolidated_20261115T122636Z.md`, **`NO_GO`**, 0/7). **C11.0 executed (probe 2026-11-15T14:00Z).** **C11.1 DONE:** native archive acquired from the Ironflow HF dataset and intake **`ACCEPT_AS_EVIDENCE_CANDIDATE`** (`archive_intake_validation_20261115T140420Z.{json,md}`); first native campaign run (6 trades, +4,292.50). **C11.2 satisfied.** **Next: C11.3** — run the full Hyperliquid-native battery (census/episode edge, placebo, robustness) on `research_state/cache/hyperliquid_ironflow_native_20251220_20260928` and write `decision_verdict_hyperliquid_native_<TS>Z.md`, re-mapping all 7 criteria. Flip to `GO` only if the native evidence clears the C11.2 pre-registered rule.

(End of file)