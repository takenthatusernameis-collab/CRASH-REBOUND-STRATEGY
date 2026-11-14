# CRASH-REBOUND-STRATEGY — Durable Handoff (single source of truth)

**Handoff updated (UTC):** 2026-11-14T08:53:30Z
**Supersedes:** all earlier handoffs. **This file is the only durable handoff.** Do not create a second status/handoff file.

**Repo:** `CRASH-REBOUND-STRATEGY` — Hyperliquid crash-rebound strategy research/backtest (RSI(21)<20 crash → rebound buy → optional rebound short, ETH-hedged, portfolio/gross-cap simulation).
**Branch/HEAD:** `main` @ `1dac654` (working tree includes fresh maintenance artifacts from this session).
**Gate/evidence (re-verified THIS session, 2026-11-14T08:53:30Z, on FRESH artifacts):** `scripts/session_gate.py` **17/17 checks passed — DONE**; `scripts/verify_campaign_evidence.py` **4/4 — EVIDENCE VERIFIED**. Green gate = evidence-chain completeness, **not** profitability/validation. **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** Binding constraint is **independent crash episodes**, not trades: 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Latest Hyperliquid partial window (probe re-captured THIS session **2026-11-14T08:49:51Z**): **0 trades, 0 PnL, 0 confirmed signals** across **24 complete symbols / 93,288 bars** (aligned 2026-04-20T01:00:00Z..2026-09-28T23:00:00Z, 3887 bars/symbol). **Retention is a decaying public-API window (~1 bar / ~10 min observed); re-probe BEFORE any heavy work.** **Do not declare validated. Do not allocate capital.** Campaign = `NOT_RUN` for full Hyperliquid until an operator-supplied verified archive arrives or the data block is proven with live probe counts.

---

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-11-14T08:53:30Z)

**Inferred priority (repo name `CRASH-REBOUND-STRATEGY`):** Produce a **decision-grade Hyperliquid-native crash-rebound verdict**, or prove the data block with a reproducible live probe. **OKX is cross-venue, `underpowered`, and NOT Hyperliquid performance evidence.** Binding constraint is **independent crash episodes**, not trades: 11 gate-passing OKX events = **4 crash episodes / 5 crash days**; two episodes lost money; crash-day-conditioned temporal-edge permutation **p(placebo >= canonical)=0.1500**; episode-block bootstrap CI **[−4,083.95, 24,411.99]**. Latest Hyperliquid partial window (probe re-captured THIS session **2026-11-14T08:49:51Z**): **0 trades, 0 PnL, 0 confirmed signals** across **24 complete symbols / 93,288 bars** (aligned 2026-04-20T01:00:00Z..2026-09-28T23:00:00Z). **Full 283-day window is API-retention-blocked; re-probe NOW — served bars are permanently lost from the public path as the window slides.** **Do not declare validated. Do not allocate capital.**

### FIRST ACTION — EXECUTE IMMEDIATELY (time-critical; window slides)

Re-probe before any heavy work:
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
```
→ refresh `research_state/hyperliquid_retention_probe.json`; record live `earliest_served_start_utc`, max/missing bars, probed/gate-pass counts, unprobeable/empty symbols. Must produce a NEW artifact with `generated_at_utc >= session start`.

### BOTTLENECK REMOVAL — EXECUTE IN ORDER, NO EARLY STOP (no planning-only turn)

**External:** Full 283-day Hyperliquid window blocked by API retention — only operator-supplied verified archive can unblock (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
**Statistical:** OKX underpowered (4 episodes, p=0.15, CI spans 0).
**Maintenance (URGENT):** partial public-API window decays; re-probe/re-capture each session before heavy work.

1. **Probe retention NOW** (command above) → NEW `hyperliquid_retention_probe.json`.
2. **Fetch full qualifying served universe (partial snapshot):** pick `<live-earliest>` from probe; new timestamped cache.
   ```bash
   TS=$(date -u +"%Y%m%dT%H%M%SZ"); mkdir -p "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/fetch_hyperliquid_candles.py --source hyperliquid_api --allow-partial --min-daily-volume-usd 5000000 --start <live-earliest> --end 2026-09-28T23:00:00Z --cache-dir "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
3. **Derive deterministic aligned complete slice:**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/derive_hyperliquid_aligned_slice.py --src "research_state/cache/hyperliquid_universe_snapshot_${TS}"
   ```
4. **Census over FULL aligned complete set (critical trap):** `run_hyperliquid_partial_census.py` **refuses without `--symbols`** (hardcoded default removed; never run without full set):
   ```bash
   ALIGNED="research_state/cache/hyperliquid_universe_snapshot_${TS}_aligned_<start>"
   SYMS=$(python3 -c "import json;d=json.load(open('$ALIGNED/provenance.json'));print(' '.join(d['summary']['complete_symbols']))")
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_hyperliquid_partial_census.py --cache-dir "$ALIGNED" --symbols $SYMS --output "research_state/hyperliquid_universe_snapshot_census_${TS}.json"
   ```
5. **Partial campaign artifact (NOT evidence):** flag is **`--allow-partial-not-evidence`** (hyphens; underscore form errors).
   ```bash
   PREFIX="research_state/campaign_results_real_hyperliquid_universe_snapshot_${TS}"
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/run_real_campaign.py --manifest "$ALIGNED/provenance.json" --allow-partial-not-evidence --window-start <aligned_start> --window-end 2026-09-28T23:00:00Z --min-daily-volume-usd 5000000 --output-prefix "$PREFIX"
   ```
   Must remain `performance_evidence=false` / NOT_EVIDENCE.
6. **Refresh gate-checked coverage:** update `research_state/hyperliquid_universe_coverage.json` to reference new probe/snapshot/aligned/census/campaign artifacts, hashes, counts, and verdict (`PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` unless facts change). Coverage gate requires: probe with perps/passing/probed, snapshot ≥12 complete + `complete_symbols`, census matching complete set, partial campaign `performance_evidence=false`, verdict containing `BLOCKED` and `UNDERPOWERED`.
7. **Verify chain (must pass before session close):**
   ```bash
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py                # expect 17/17 — DONE
   PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py     # expect 4/4 — EVIDENCE VERIFIED
   ```
8. **If operator-supplied verified Hyperliquid-native 283-day archive arrives:** follow `research_state/DATA_REQUEST_283D_HYPERLIQUID.md` (verify provenance/non-flat, ingest, derive verified universe, run canonical full-window campaign, run exact full-portfolio placebo adapted to Hyperliquid, episode-aware audit). Produce `campaign_results_real_hyperliquid_full*.json` and `placebo_portfolio_hyperliquid_full.{json,md}`. **Never** use `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat synthetic placeholder).
9. **Episode-aware audit for any new Hyperliquid run:** independent crash episodes/distinct crash days (not trades); episode-block bootstrap and, if sample permits, crash-day-conditioned temporal-edge permutation. Record `research_state/episode_edge_hyperliquid_*.{json,md}`. Do not promote to evidence until **≥10 independent crash episodes with positive episode-level bootstrap CI excluding 0**.
10. **Update `research_state/decision_memo_okx_full.md`** with fresh partial/data-block facts and power-based sample-size target. Keep verdict `underpowered` until every GO criterion is met (full window + ≥10 independent episodes with positive bootstrap CI + trade bootstrap CI excludes 0 + episode-block CI excludes 0 + crash-day permutation p<0.05 + full-portfolio placebo p<0.05 + DD within mandate).

**NEXT FOCUS CAMPAIGN (unavoidable heavy work):** Every session must: (a) re-probe retention before any other work; (b) capture the partial snapshot before retention slides further; (c) run census over the full aligned symbol set (not a 12-symbol default); (d) run the gated campaign marked `performance_evidence=false` using `--allow-partial-not-evidence`; (e) verify the 17/17 + 4/4 chain. **No session may close without steps 1-7 complete and artifacts on disk. Planning-only turns are prohibited.**

**ANTI-AVOIDANCE (hard):** execute steps 1-7 and produce real gate-relevant artifacts first; no planning-only turn; no validation/parity claims; no per-event-null as portfolio test; no 10,000-sim theater (exact 165-subset enumeration standard); no second handoff; no fabricated data; never relax $5M gate; no "data unavailable" without live probe artifact + full-universe counts; never run `run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice; never use `--allow-partial_not_evidence` (underscores) — use `--allow-partial-not-evidence`.

---

## Verified state (2026-11-14T08:53:30Z, artifacts produced THIS session)

| Check | Result | Evidence |
|---|---|---|
| Git | `main` @ `1dac654`; fresh maintenance artifacts this session | `git rev-parse --short HEAD` |
| Durable handoff | Single: `./HANDOFF.md` | repo root |
| Env | `/tmp/crs-venv` present | `test -x` |
| Session gate | **17/17 — DONE** (re-verified THIS session) | `scripts/session_gate.py` |
| Evidence verifier | **4/4 — EVIDENCE VERIFIED** (re-verified THIS session) | `scripts/verify_campaign_evidence.py` |
| Retention probe (THIS session) | 3890/6792 bars; 2902 missing; earliest 2026-04-19T22:00:00Z; 235 perps / 28 pass $5M / 28 probed; `symbols_empty_or_error=[KPEPE]`; generated **2026-11-14T08:49:51Z** (**re-probe before next heavy work**) | `hyperliquid_retention_probe.json` (sha `4b85bfcd…`) |
| Latest raw snapshot | fetch-produced provenance, 26 symbols (2 error: MATIC,FTM) | `cache/hyperliquid_universe_snapshot_20261114T084957Z/provenance.json` (sha `e84d4847…`) |
| Latest aligned partial slice | 24 complete symbols × 3887 bars (2026-04-20T01:00:00Z..2026-09-28T23:00:00Z), synthetic checks ok | `..._aligned_20260420T0100Z/provenance.json` (sha `6906fa7e…`) |
| Latest aligned census (full set) | 24 symbols / 93,288 bars / 11 RSI crashes / 0 confirmed signals | `hyperliquid_universe_snapshot_census_20261114T084957Z.json` (sha `61ae9c97…`) |
| Latest partial campaign | `performance_evidence=false` / NOT_EVIDENCE, 0 trades, 0 PnL | `campaign_results_real_hyperliquid_universe_snapshot_20261114T084957Z.json` (sha `82727384…`) |
| Gate-checked coverage | points to 08:49:57Z artifacts; `PARTIAL_WINDOW_DECAYING; FULL_283D_BLOCKED_BY_API_RETENTION; STRATEGY_UNDERPOWERED` | `hyperliquid_universe_coverage.json` |
| Phase O (OKX) | 4 episodes / 11 events / 5 crash days; p=0.1500; bootstrap CI [-4083.95,24411.99] (2026-11-13T23:38:47Z) | `episode_edge_okx_full.json` |
| Canonical OKX baseline | 8 trades, total PnL **9159.691934882958** (unchanged, cross-venue) | `campaign_results_real_okx_full.json` |

---

## Bottlenecks (current)

1. **External/data block:** Full 283-day Hyperliquid window API-blocked (retention-limited). Only operator-supplied verified Hyperliquid-native archive can provide missing early history (`research_state/DATA_REQUEST_283D_HYPERLIQUID.md`).
2. **Maintenance (decaying):** partial public-API window slides; re-probe and re-capture before heavy work each session (probe 2026-11-14T08:49:51Z).
3. **Statistical:** OKX evidence underpowered / few independent episodes; no Hyperliquid-native performance evidence yet.
4. **Resolved traps (do not reintroduce):** census requires `--symbols`; campaign flag is `--allow-partial-not-evidence` (hyphens); `derive_hyperliquid_aligned_slice.py` removes manual aligned-slice bottleneck.

---

## Canonical artifacts (do not re-acquire/re-run/overwrite)

- OKX data: `research_state/archives/okx_1h_full_20251220_20260928/` (63), `2025-12-20T00:00:00Z..2026-09-28T23:00:00Z`, 6792 bars/symbol. Manifest `research_state/cache/okx_1h_full_20251220_20260928/provenance.json`.
- Universe: `research_state/universe_okx_full_verified.json` (54). Campaign: `research_state/campaign_results_real_okx_full.json` — 100k→109,159.69, net PnL 8141.29, 8 trades (4W/4L). **OKX cross-venue, not Hyperliquid evidence.**
- Placeholder `research_state/archives/hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` — **NEVER evidence**.

---

## Reproduction

```bash
test -x /tmp/crs-venv/bin/python || bash scripts/bootstrap_env.sh
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/session_gate.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/verify_campaign_evidence.py
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/probe_hyperliquid_blocker.py --limit 30
```

---

## Hard prohibitions

- No fabricated/synthetic data; no relabeling OKX, partial snapshots, or partial campaigns as full Hyperliquid/performance evidence.
- Never use `hyperliquid_btc_eth_1h_20251220_20260928_verified.parquet` as evidence (flat placeholder).
- No removal/relaxation of `volume_filter_ok` or trailing-24h ≥$5M gate.
- No unnecessary re-acquisition/reruns of canonical OKX artifacts (new stems only). No 10,000-sim theater (exact 165-subset enumeration). No duplicate sensitivity sweep while lock held.
- No per-event null as portfolio test; no validation/capital-allocation claims (`underpowered`).
- Never run `run_hyperliquid_partial_census.py` without `--symbols` on a >12-symbol slice. Never use `--allow-partial_not_evidence` (underscores).
- No additional handoff/status files. This file is the single durable handoff.

---

## Definition of done

Evidence chain **17/17 achieved** (completeness). **Decision-grade validation NOT achieved.** Required: full 283-day Hyperliquid-native campaign (or documented operator-data block with exact live probe counts) + full-portfolio placebo + episode-aware audit + updated decision memo with stop/go criteria and power-based sample-size target (≥10 independent crash episodes with positive episode-level bootstrap CI).
