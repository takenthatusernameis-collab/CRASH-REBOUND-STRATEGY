# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T08:44:00Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch/HEAD:** `main` @ `1dac654` (working tree has fresh maintenance artifacts from this session; see `git status`).
**Gate/evidence (re-verified THIS session, 2026-11-14T08:44:00Z, on FRESH artifacts):** `scripts/session_gate.py` **17/17 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation. **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** Binding constraint is **independent crash episodes**, not trades: 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Latest Hyperliquid partial window (probe re-captured THIS session **2026-11-14T08:42:49Z**): **0 trades, 0 PnL, 0 confirmed signals** across **24 complete symbols / 93,288 bars** (aligned 2026-04-20T01:00:00Z..2026-09-28T23:00:00Z, 3887 bars/symbol). **Do not declare validated. Do not allocate capital.** Campaign = `NOT_RUN` for full Hyperliquid until an operator-supplied verified archive arrives or the data block is proven with live probe counts.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T08:44:00Z)

**Inferred priority (repo name `CRASH-REBOUND-STRATEGY`):** Produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** Binding constraint is **independent crash episodes**, not trades: 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Latest Hyperliquid partial window (probe re-captured THIS session **2026-11-14T08:42:49Z**): **0 trades, 0 PnL, 0 confirmed signals** across **24 complete symbols / 93,288 bars** (aligned 2026-04-20T01:00:00Z..2026-09-28T23:00:00Z). **Retention is currently stable at the 08:42Z probe (3891/6792 max bars, 2901 missing, earliest served 2026-04-19T21:00:00Z) but still decays ~1 bar / ~10 min on the public API path; re-probe BEFORE any heavy work.** **Do not declare validated. Do not allocate capital.** Campaign = `NOT_RUN` for full Hyperliquid until an operator-supplied verified archive arrives or the data block is proven with live probe counts.

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical; window slides ~1h/hr; bars permanently lost per hour)

The partial Hyperliquid public-API window **decays ~1h/hr**. Probe re-captured THIS session (**2026-11-14T08:42:49Z**, `research_state/hyperliquid_retention_probe.json`) showed `earliest_served_start_utc=2026-04-19T21:00:00Z`, max **3891/6792** bars, missing **2901**, perps **235** / **28 pass $5M gate** / **28 probed**, `symbols_empty_or_error=[KPEPE]`, verdict `FULL_283D_BLOCKED_BY_API_RETENTION`. **Re-probe NOW before heavy work (served bars are permanently lost from the public API path as the window slides):**
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
```
→ refresh `research_state/hyperliquid_retention_probe.json`; record live `earliest_served_start_utc`, max bars, missing bars, probed/gate-pass counts, unprobeable/empty symbols. **This must produce a NEW artifact with generated_at_utc >= current session start.**

### BOTTLENECK REMOVAL — EXECUTE IN ORDER, NO EARLY STOP (no planning-only turn)

**External bottleneck:** Full 283-day Hyperliquid window blocked by API retention. Only operator-supplied verified archive (see `research_state/DATA_REQUEST_283D_HYPERLIQUID.md`) can unblock.
**Statistical bottleneck:** OKX evidence underpowered (4 episodes, p=0.15, CI includes zero).
**Maintenance bottleneck (URGENT):** Partial public-API window decays ~1h/hr; re-probe and re-capture before heavy work each session.

1. **Probe retention NOW (time-critical):** (command above) → produces NEW `hyperliquid_retention_probe.json` with `generated_at_utc >= session start`.

2. **Fetch full qualifying served universe (partial snapshot):** pick `<live-earliest>` from probe; create new timestamped cache.
   ```bash
   TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```

3. **Derive deterministic aligned complete slice** (with fetch provenance linkage — removes the old manual-bottleneck):
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
   → writes `<src>_aligned_<start>/provenance.json`. Use the returned aligned dir (its `summary.complete_symbols` is the authoritative set).

4. **Census over the FULL aligned complete set (critical script trap):** `scripts/run_hyperliquid_partial_census.py` **refuses to run without `--symbols`** (a hardcoded 12-symbol default was removed because it silently undercounted). Always pass the full set:
   ```bash
   ALIGNED="research_state/cache/hyperliquid_universe_snapshot_${TS}_aligned_<start>"
   SYMS=$(python3 -c "import json;d=json.load(open('$ALIGNED/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir "$ALIGNED" --symbols $SYMS --output "research_state/hyperliquid_universe_snapshot_census_${TS}.json"
   ```

5. **Partial campaign artifact (NOT evidence):** **NOTE the exact flag is `--allow-partial-not-evidence` (hyphens), NOT `--allow-partial_not_evidence` (underscores) — the underscore form errors out.** (This corrected the prior handoff's wrong command.)
   ```bash
   PREFIX="research_state/campaign_results_real_hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest "$ALIGNED/provenance.json" --allow-partial-not-evidence --window-start <aligned_start> --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix "$PREFIX"
   ```
   Must remain `performance_evidence=false` / NOT_EVIDENCE; never relabel partial as performance evidence.

6. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to point to the new probe/snapshot/aligned/census/campaign artifacts, hashes, counts, and status (`PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` unless facts change). The coverage gate (`phase_q_universe_coverage`) requires: `api_retention_probe` with perps/passing/probed, `universe_snapshot` with ≥12 complete symbols + complete_symbols list, `crash_census` with symbols==complete/bars/crashes/signals, `partial_campaign` with `performance_evidence=false`, and `verdict` containing `BLOCKED` and `UNDERPOWERED`.

7. **Verify chain (agent cannot close session without these passing):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
   ```

8. **If operator-supplied verified Hyperliquid-native 283-day archive becomes available:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` to verify provenance/non-flat data, ingest to `research_state/cache/hyperliquid_1h_full_20251220_20260928`, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, and run episode-aware audit. Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).

9. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0** (Phase O refinement supersedes the 23-trade target; 23 trades from 4 episodes would NOT satisfy this).

10. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met (full window + ≥10 independent episodes with positive bootstrap CI + trade bootstrap CI excludes 0 + episode-block CI excludes 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05 + DD within mandate).

**NEXT FOCUS CAMPAIGN (unavoidable heavy work):** The repo name mandates crash-rebound strategy validation on Hyperliquid-native data. Every session must: (a) re-probe retention before any other work; (b) capture the partial snapshot before retention slides further; (c) run census over the full aligned symbol set (not a 12-symbol default); (d) run the gated campaign marked `performance_evidence=false` using `--allow-partial-not-evidence`; (e) verify the 17/17 + 4/4 chain. **No session may close without steps 1-7 complete and artifacts on disk. Planning-only turns are prohibited.**

**ANTI-AVOIDANCE (hard):** execute steps 1-7 and produce real gate-relevant artifacts first; no planning-only turn; no validation/parity claims; no per-event-null as portfolio test; no 10,000-sim theater (exact 165-subset enumeration standard); no second handoff; no fabricated data; never relax $5M gate; no "data unavailable" without live probe artifact + full-universe counts; never run `run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice; never use `--allow-partial_not_evidence` (wrong flag; use `--allow-partial-not-evidence`).

---

## Verified state (current: 2026-11-14T08:44:00Z, on artifacts produced THIS session)

| Check | Result | Evidence |
|---|---|---|
| Git | `main` @ `1dac654`; fresh maintenance artifacts this session | `git rev-parse --short HEAD`, `git status --short` |
| Durable handoff | Single: `./HANDOFF.md` | repo root scan |
| Env | `/tmp/crs-venv` present | `test -x` |
| Session gate | **17/17 — DONE** (re-verified THIS session) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 PASS — EVIDENCE VERIFIED** (re-verified THIS session) | `scripts/verify_campaign_evidence.py` |
| Retention probe (THIS session) | 3891/6792 bars; 2901 missing; earliest 2026-04-19T21:00:00Z; 235 perps / 28 pass $5M / 28 probed; `symbols_empty_or_error=[KPEPE]`; generated **2026-11-14T08:42:49Z** (**re-probe before next heavy work**) | `hyperliquid_retention_probe.json` (sha `c27c92bd…`) |
| Latest gate-compliant raw snapshot | fetch-produced provenance THIS session 08:43:10Z | `cache/hyperliquid_universe_snapshot_20261114T084310Z/provenance.json` (sha `93d5c2fb…`) |
| Latest aligned partial slice | 24 complete symbols × 3887 bars (2026-04-20T01:00:00Z..2026-09-28T23:00:00Z), synthetic checks ok | `..._aligned_20260420T0100Z/provenance.json` (sha `f5b03ac7…`) |
| Latest aligned census (full set) | 24 symbols / 93288 bars / 11 RSI crashes / 0 confirmed signals | `hyperliquid_universe_snapshot_census_20261114T084310Z.json` (sha `72c733b4…`) |
| Latest partial campaign | `performance_evidence=false` / NOT_EVIDENCE, 0 trades, 0 PnL (consistent with 0 signals) | `campaign_results_real_hyperliquid_universe_snapshot_20261114T084310Z.json` (sha `27d8ff0c…`) |
| Gate-checked coverage | points to 08:43:10Z artifacts; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` | `hyperliquid_universe_coverage.json` |
| Phase O artifact (`episode_edge_okx_full.json`, generated_at_utc) | 2026-11-13T23:38:47Z | `episode_edge_okx_full.json` |
| Phase O (OKX) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99] | `episode_edge_okx_full.json` |
| Canonical OKX baseline | 8 trades, total PnL **9159.691934882958** (unchanged) | `campaign_results_real_okx_full.json` |

---

## Bottlenecks (current)

1. **External/data block:** Full 283-day Hyperliquid window API-blocked (retention-limited). Only operator-supplied verified Hyperliquid-native archive can provide missing early history (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. **Maintenance (decaying):** partial public-API window decays ~1h/hr; re-probe and re-capture before heavy work each session (currently stable at 08:42:49Z probe).
3. **Statistical:** OKX evidence underpowered / few independent episodes; no Hyperliquid-native performance evidence yet.
4. **RESOLVED traps (do not reintroduce):** (a) `run_hyperliquid_partial_census.py` now refuses to run without `--symbols`; (b) campaign flag is `--allow-partial-not-evidence` (hyphens); (c) `derive_hyperliquid_aligned_slice.py` removes the old manual aligned-slice bottleneck.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- OKX data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), window `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54 symbols pass ≥$5M).
- Campaign: `research_state/campaign_results_real_okx_full.json` — 100k→109,159.69, net PnL 8141.29, +9.1597% / +22.5995% ann., DD −2.0275%, 8 trades (4W/4L), 5/54 symbols. **OKX cross-venue, not Hyperliquid evidence.**
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py   # expect 4/4 — EVIDENCE VERIFIED
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30  # live retention/probe
```

---

## Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX campaign/J1/J2/K/L or overwrite of canonical artifacts (new stems only).
- No 10,000-sim theater; exact 165-subset enumeration is the placebo standard. No old 527s placebo path.
- No duplicate sensitivity sweep while `.sensitivity_sweep.lock` held.
- No per-event null presented as portfolio test; no validation/capital-allocation claims (`underpowered`).
- Never run `run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice.
- Never use `--allow-partial_not_evidence` (underscores) — use `--allow-partial-not-evidence` (hyphens).
- No additional handoff/status files. This file is the single durable handoff.

---

## Definition of done

Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI).

(End of file - total 127 lines)