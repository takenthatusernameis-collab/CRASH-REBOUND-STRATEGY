# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T13:57:12Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation). Priority: produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. OKX is cross-venue, underpowered, and **never** Hyperliquid performance evidence.

**Branch/HEAD (session start):** `b0df433` (2026-11-14T13:43Z). Working tree is **dirty on purpose**: this session added a live re-probe, a fresh (degraded) fetch, a refreshed coverage file, and a new signal-funnel reconciliation script/artifact (see below). Do not reset or delete them; commit only if explicitly requested.

**Gate/evidence (re-verified this session 2026-11-14T13:57Z):** `scripts/session_gate.py` **17/17 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation.

**Binding facts:** **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]** (canonical unchanged: 8 trades, net PnL 8141.29 / total PnL 9159.691934882958). **Latest live Hyperliquid probe (this session 2026-11-14T13:40:15Z):** earliest served **2026-04-20T02:00:00Z**, **3886/6792 bars** (2906 missing), **235 perps / 27 pass $5M gate / 27 probed**, unprobeable/empty **['KPEPE']**; full 283-day window **API-retention-blocked**. **Fresh full-universe fetch this session (20261114T134000Z) was DEGRADED:** raw snapshot had only **1 complete symbol (ALGO)**; its derived aligned slice `20261114T134000Z_aligned_20260621T1400Z` has 24 complete symbols but only **2386 bars** from 2026-06-21T14:00:00Z. Per handoff step 2 the **largest valid aligned complete slice was retained**: `20261114T104210Z_aligned_20260420T0300Z` (24 complete × 3885 bars, 2026-04-20T03:00:00Z..2026-09-28T23:00:00Z). **Latest census (retained chain):** 24 symbols / 93,240 bars / 11 RSI crash events / 0 confirmed signals (`hyperliquid_universe_snapshot_census_20261114T125249Z.json`). **Latest partial campaign:** 0 trades, 0.0 PnL, `performance_evidence=false`, `real_market_data=true`, `NOT_EVIDENCE_PARTIAL_UNIVERSE`. **NEW ROOT-CAUSE FINDING — partial-window signal funnel (this session 2026-11-14T13:55Z):** `scripts/reconcile_hyperliquid_signal_funnel.py` on the retained chain shows **29 RSI(21)<20 hours → 11 pass the trailing-24h ≥$5M volume floor (an upper bound of 11 spec-literal next-open entries before portfolio caps) → 0 have a same-bar rebound-confirmation candle → 5 have a next-bar confirmation → 0 `generate_signal` confirmations** (`research_state/hyperliquid_signal_funnel_20261114T104210Z.{json,md}`). The implementation requires a **same-bar** `confirm_rebound` candle before entry; the PDF spec says **buy at the next hourly open after RSI closes below 20** and does not require a same-bar confirmation candle. This is the structural reason the partial window yields zero trades, and it is now the primary statistical bottleneck to adjudicate. **Do not declare validated. Do not allocate capital.**

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T13:55:27Z)

**Priority (repo `CRASH-REBOUND-STRATEGY`):** Produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. OKX is cross-venue/underpowered and **never** Hyperliquid evidence. Full 283-day Hyperliquid is retention-blocked; the partial window **decays continuously** and any NOT_EVIDENCE result is not validation. The partial window currently produces **zero trades**, so the next session must **adjudicate the crash→entry funnel** (same-bar confirmation vs spec's next-open entry) before more partial campaigns can teach anything.

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical)

Re-probe before any heavy work:
```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
```
Refresh `research_state/hyperliquid_retention_probe.json`; record live `earliest_served_start_utc`, max/missing bars, probed/gate-pass counts, unprobeable/empty symbols. Produce a NEW artifact with `generated_at_utc >= session start`.

### BOTTLENECK REMOVAL — EXECUTE IN ORDER, NO EARLY STOP (planning-only turns prohibited)

**External:** Full 283-day Hyperliquid window blocked by API retention — only an operator-supplied **verified Hyperliquid-native archive** can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`). Pipeline bottleneck removed this session: probe→fetch→derive→census→campaign ran end-to-end green; retained chain 20261114T104210Z (24 complete × 3885 bars) is valid on disk. **New:** a fresh fetch can be severely degraded (this session's 134000Z fetch produced only 1 complete raw symbol / 2386 aligned bars); never adopt a degraded slice over the retained chain.
**Statistical:** OKX underpowered (4 episodes, p=0.15, CI spans 0); no Hyperliquid-native performance evidence. **New:** partial Hyperliquid yields 0 trades because `confirm_rebound` requires a same-bar bullish candle, while the spec entry is the next hourly open after the RSI crash close — adjudicate this with artifacts, do not silently change the baseline.
**Maintenance:** partial public-API window decays; re-probe and re-capture before heavy work each session, but only adopt a new aligned chain if it is **at least as long and starts no later** than the retained chain.

1. **Probe retention NOW** (command above) → NEW `hyperliquid_retention_probe.json`.
2. **Fetch full qualifying served universe (partial snapshot):** set `<live-earliest>` from probe; use a new timestamped cache. Prefer the largest valid aligned complete slice; do not let gate coverage point at a degraded/smaller chain.
   ```bash
   TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
3. **Derive deterministic aligned complete slice:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
4. **ADOPT-OR-KEEP CHECK (new, mandatory):** compare the new aligned slice's `summary.complete_symbols` count, bar count, and `aligned_window.start` against `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/provenance.json` (24 complete × 3885 bars, start 2026-04-20T03:00:00Z). **Only** point coverage/census/campaign at the new slice if it has **≥3885 bars and start ≤ 2026-04-20T03:00:00Z**; otherwise keep the retained chain and record the comparison in `research_state/hyperliquid_universe_coverage.json`. This session's 134000Z slice (2386 bars, start 2026-06-21T14:00:00Z) **fails** this check and must not replace the retained chain.
5. **Census over FULL aligned complete set (critical trap):** `run_hyperliquid_partial_census.py` **refuses without `--symbols`** — never run without full set.
   ```bash
   ALIGNED="research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z"
   SYMS=$(python3 -c "import json;d=json.load(open('$ALIGNED/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir "$ALIGNED" --symbols $SYMS --output "research_state/hyperliquid_universe_snapshot_census_${TS}.json"
   ```
6. **Partial campaign artifact (NOT evidence):** flag is **`--allow-partial-not-evidence`** (hyphens).
   ```bash
   PREFIX="research_state/campaign_results_real_hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest "$ALIGNED/provenance.json" --allow-partial-not-evidence --window-start 2026-04-20T03:00:00Z --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix "$PREFIX"
   ```
   Must remain `performance_evidence=false` / NOT_EVIDENCE.
7. **FUNNEL ADJUDICATION (new, heavy, mandatory):** re-run the funnel on whichever chain was adopted, then quantify the spec-literal entry path without touching the canonical baseline:
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/reconcile_hyperliquid_signal_funnel.py \
     --cache-dir "$ALIGNED" \
     --output "research_state/hyperliquid_signal_funnel_${TS}.json" \
     --md-output "research_state/hyperliquid_signal_funnel_${TS}.md"
   ```
   Then produce an **exploratory** variant artifact that counts entries when the RSI crash hour is followed by the **next hourly open** (spec-literal, no same-bar `confirm_rebound`), and compares trade counts vs the implementation path. Label it `NOT_EVIDENCE_EXPLORATORY_FANOUT`; do not overwrite the canonical campaign, do not claim validation, do not allocate capital. Record whether the zero-trade result is structural (confirmation filter) and quantify how many additional crash hours the spec-literal path would admit.
8. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to reference the new probe/snapshot/aligned/census/campaign/funnel artifacts, SHA256 hashes, integer counts (symbols/bars/rsi_crash_events/confirmed_signals, num_trades/total_pnl), the adopt-or-keep decision, and verdict (`PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED; PARTIAL_ENTRY_FUNNEL_BLOCKED_BY_SAME_BAR_CONFIRMATION` unless facts change). Map probe fields correctly (`universe.perps_total/perps_passing_volume_gate/probed`, `probe_summary.*`). Gate requires probe with perps/passing/probed, snapshot ≥12 complete + `complete_symbols`, census matching complete set with sufficient bars, partial campaign `performance_evidence=false`.
9. **Verify chain before close:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
   ```
10. **If operator-supplied verified Hyperliquid-native 283-day archive arrives:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).
11. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0**.
12. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts, the funnel finding, and a power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met (full window + ≥10 independent episodes with positive bootstrap CI + trade bootstrap CI excludes 0 + episode-block CI excludes 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05 + DD within mandate).

**NEXT FOCUS CAMPAIGN (unavoidable heavy work, every session):** (a) re-probe retention; (b) capture a valid partial snapshot and apply the adopt-or-keep check against the retained chain; (c) census over full aligned symbol set; (d) gated NOT_EVIDENCE campaign via `--allow-partial-not-evidence`; (e) signal-funnel reconciliation + spec-literal entry adjudication; (f) refresh `hyperliquid_universe_coverage.json` with correct schema/counts; (g) verify 17/17 + 4/4. **No session may close without steps 1-9 complete, gates green, and artifacts on disk.**

**ANTI-AVOIDANCE (hard):** execute 1-9 and produce real gate-relevant artifacts first; no planning-only turn; no validation/parity/capital-allocation claims; no per-event-null as portfolio test; no 10,000-sim theater (exact 165-subset enumeration); no second handoff; no fabricated data; never relax $5M gate; no "data unavailable" without live probe artifact + counts; never run census without `--symbols` on >12-symbol slice; flag is `--allow-partial-not-evidence` (hyphens); never replace the retained 104210Z chain with the degraded 134000Z chain. If a fresh fetch is degraded, resolve it (retry/diagnose) — not a reason to stop.

---

## Verified state (2026-11-14T13:55:27Z)

| Check | Result | Evidence |
|---|---|---|
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present | `test -x` |
| Session gate | **17/17 — DONE** (this session 2026-11-14T13:44Z) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (this session 2026-11-14T13:44Z) | `scripts/verify_campaign_evidence.py` |
| Retention probe (this session) | 3886/6792 bars; 2906 missing; earliest 2026-04-20T02:00:00Z; 235 perps / 27 pass $5M / 27 probed; unprobeable/empty=['KPEPE']; 2026-11-14T13:40:15Z (**re-probe before next heavy work**) | `research_state/hyperliquid_retention_probe.json` |
| Fresh fetch this session | **DEGRADED:** raw 1 complete symbol (ALGO); aligned `20261114T134000Z_aligned_20260621T1400Z` = 24 complete × 2386 bars (start 2026-06-21T14:00:00Z) — **fails adopt-or-keep** | `research_state/cache/hyperliquid_universe_snapshot_20261114T134000Z*` |
| Latest raw snapshot (gate chain) | `hyperliquid_universe_snapshot_20261114T104210Z` (fetch-produced provenance) | cache snapshot |
| Latest aligned slice (gate chain) | `hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z` — 24 complete × 3885 bars (2026-04-20T03:00:00Z..2026-09-28T23:00:00Z) | aligned provenance |
| Latest aligned census (gate chain) | 24 symbols / 93,240 bars / 11 RSI crashes / 0 confirmed signals | `research_state/hyperliquid_universe_snapshot_census_20261114T125249Z.json` |
| Latest partial campaign (gate chain) | `performance_evidence=false` / NOT_EVIDENCE_PARTIAL_UNIVERSE, 0 trades, 0.0 PnL, real_market_data=true | `research_state/campaign_results_real_hyperliquid_universe_snapshot_20261114T125249Z.json` |
| **Signal funnel (new)** | **29 RSI<20 hours → 11 pass $5M volume (upper bound 11 spec-literal entries) → 0 same-bar rebound confirm → 5 next-bar confirm → 0 generate_signal** | `research_state/hyperliquid_signal_funnel_20261114T104210Z.{json,md}` |
| Phase O Hyperliquid partial episode audit | NOT_APPLICABLE_NO_EPISODES (0 signals ⇒ 0 trades ⇒ 0 episodes); permutation/audit recorded not_run, no fabricated p-value | `research_state/episode_edge_hyperliquid_partial.{json,md}` |
| Gate-checked coverage | updated this session to reference probe (2026-11-14T13:40:15Z) + retained 20261114T104210Z chain; `PARTIAL_WINDOW_DECAYING;FULL_283D_BLOCKED_BY_API_RETENTION;STRATEGY_UNDERPOWERED` | `research_state/hyperliquid_universe_coverage.json` |
| Phase O (OKX, artifact 2026-11-13T23:38:47Z) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99] | `research_state/episode_edge_okx_full.json` |
| Canonical OKX baseline | 8 trades, total PnL **9159.691934882958** (unchanged, cross-venue) | `research_state/campaign_results_real_okx_full.json` |

## Bottlenecks (current)

1. **External/data block:** Full 283-day Hyperliquid window API-blocked (retention-limited). Only operator-supplied verified Hyperliquid-native archive can provide missing early history. Pipeline maintenance bottleneck **resolved** this session: probe→fetch→derive→census→campaign green; retained chain on disk.
2. **Maintenance (decaying):** partial public-API window slides; re-probe and re-capture before heavy work each session. **New:** fresh fetches can be severely degraded (this session: 1 complete raw symbol / 2386 aligned bars) — apply the adopt-or-keep check and never point coverage at a degraded chain.
3. **Statistical / signal funnel (new primary):** partial Hyperliquid yields **0 trades** because the implementation requires a **same-bar** `confirm_rebound` candle, while the spec entry is the **next hourly open after the RSI crash close**. Funnel: 29 RSI<20 hours → 11 pass $5M volume → 0 same-bar confirmations. Adjudicate with the exploratory artifact; do not silently change the baseline.
4. **Statistical:** OKX evidence underpowered / few independent episodes; no Hyperliquid-native performance evidence yet.
5. **Resolved traps (do not reintroduce):** census requires `--symbols`; campaign flag is `--allow-partial-not-evidence` (hyphens); `derive_hyperliquid_aligned_slice.py` removes manual aligned-slice bottleneck; gate coverage requires integer aggregate counts for census/campaign.

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- OKX data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54). Campaign: `research_state/campaign_results_real_okx_full.json` — 100k→109,159.69, net PnL 8141.29, 8 trades (4W/4L). **OKX cross-venue, not Hyperliquid evidence.**
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.
- Retained Hyperliquid partial chain (do not overwrite): `research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z/` (24 complete × 3885 bars).
- Signal funnel tool: `scripts/reconcile_hyperliquid_signal_funnel.py`; latest artifact `research_state/hyperliquid_signal_funnel_20261114T104210Z.{json,md}`.

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/reconcile_hyperliquid_signal_funnel.py \
  --cache-dir research_state/cache/hyperliquid_universe_snapshot_20261114T104210Z_aligned_20260420T0300Z \
  --output research_state/hyperliquid_signal_funnel_repro.json
```

## Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence.
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater. No duplicate sensitivity sweep while lock held.
- No per-event-null as portfolio test; no validation/capital-allocation claims (`underpowered`).
- Never run census without `--symbols` on >12-symbol slice. Never use `--allow-partial_not_evidence` (underscores).
- Do not replace the retained 20261114T104210Z chain with the degraded 20261114T134000Z chain.
- No additional handoff/status files. This file is the single durable handoff.

## Definition of done

Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI) + a documented adjudication of the partial-window entry funnel (same-bar confirmation vs spec next-open entry).