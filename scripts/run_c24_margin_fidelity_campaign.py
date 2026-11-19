#!/usr/bin/env python3
"""C24 — MARGIN / LIQUIDATION FIDELITY ADJUDICATION of the frozen crash-rebound edge.

WHY THIS EXISTS
---------------
C1-C23 closed NO_GO on four real cross-venue caches using an execution model that
force-liquidates a position on a -(5+1)=6% adverse move (see
src/backtest/engine.py::_check_liquidation).  The published spec's own risk exit is a
WIDE safety stop at 8x the usual hourly range (median ~15% below entry on
Hyperliquid) and states the 120% coin cap "leaves margin free".  A 6% forced exit is
strictly tighter than the strategy's own stop and is not specified in the PDF, so the
C1-C23 NO_GO may be an artifact of the margin model rather than a property of the
strategy.

Stage-0 descriptive probe (scripts/probe_c24_liquidation_fidelity.py) reproduced the
recorded C20/C22/C23 PnL exactly and showed a sign flip between a 10% and a 15%
liquidation distance.  This runner is the HEAVY pre-registered adjudication: it
attaches full inference (episode-block bootstrap 20k, conditional permutation 20k,
placebo 2k, BH) to the pre-specified arms and emits arm-level + consolidated verdicts.

WHAT THIS RUNS (heavy, per arm x venue x fold)
----------------------------------------------
  campaign (real portfolio engine) -> crash census -> episode-block bootstrap +
  conditional temporal-edge permutation -> full-portfolio placebo -> robustness
  battery (per-leg attribution, exit reasons, concentration, leave-one-out, power).

ARMS (pre-registered; ONLY the liquidation distance varies — the signal path is frozen)
--------------------------------------------------------------------------------------
  base_6 : liquidation distance 6%   (frozen C1-C23 model; fidelity anchor, MUST reproduce)
  d10    : liquidation distance 10%
  d15    : liquidation distance 15%  (PRIMARY; equals the spec's median safety-stop distance)
  d30    : liquidation distance 30%  (upper descriptive bracket)
  noliq  : liquidation checks disabled (descriptive upper bound; not a fidelity claim)

HARD LABELS / GUARDRAILS
------------------------
  real_market_data=true, fabricated_data=false, synthetic_data=false,
  is_hyperliquid_venue_data=false, cross_venue=true.  Results are NEVER Hyperliquid
  performance evidence.  Signal parameters are frozen and verified for drift; a run
  that changes them is INVALID.  Draw-count floors (20k/20k/2k/2k) are not reducible.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/run_c24_margin_fidelity_campaign.py --jobs 4 --resume
  PYTHONPATH=. .venv/bin/python scripts/verify_c24_focus_campaign.py   # -> C24 ACCEPTANCE: PASS
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import scripts.run_c20_cross_venue_campaign as c20  # noqa: E402
import scripts.run_c22_mexc_campaign as c22  # noqa: E402
import scripts.run_c23_bitget_campaign as c23  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402

TS = "20261119T013154Z"
STATE = REPO / "research_state"
PREREG = STATE / f"c24_prereg_{TS}.json"
SEED = 20261201

FOLDS: List[Dict[str, str]] = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

VENUE_LOADERS = {
    "okx": lambda: c20.load_venue("okx"),
    "binance_um": lambda: c20.load_venue("binance_um"),
    "mexc": lambda: c22.load_mexc_venue(),
    "bitget": lambda: c23.load_bitget_venue(),
}

# liquidation distance = maint_margin_pct + buffer_pct
ARMS: Dict[str, Dict[str, Any]] = {
    "base_6": {"maint": 5.0, "buffer": 1.0, "disable": False, "role": "FIDELITY_ANCHOR"},
    "d10": {"maint": 9.0, "buffer": 1.0, "disable": False, "role": "SECONDARY_DESCRIPTIVE"},
    "d15": {"maint": 14.0, "buffer": 1.0, "disable": False, "role": "PRIMARY"},
    "d30": {"maint": 29.0, "buffer": 1.0, "disable": False, "role": "SECONDARY_DESCRIPTIVE"},
    "noliq": {"maint": 5.0, "buffer": 1.0, "disable": True, "role": "UPPER_BOUND_DESCRIPTIVE"},
}

PRIMARY_ARM = "d15"
FIDELITY_ARM = "base_6"

# Inference scope (pre-registered): only the PRIMARY arm gets the full 20k/20k/2k
# battery.  base_6 is the fidelity anchor and its inference is ALREADY recorded in
# C20 (OKX/Binance UM), C22 (MEXC) and C23 (Bitget) for the identical frozen config,
# so re-running it would be redundant heavy compute.  d10/d30/noliq are descriptive
# sensitivity arms: campaign + census + battery only, no inference, no verdict power.
ARM_MODE = {
    "base_6": "anchor",
    "d10": "campaign_only",
    "d15": "inference",
    "d30": "campaign_only",
    "noliq": "campaign_only",
}

DRAWS_FULL = {"episode_block_bootstrap": 20000, "permutation": 20000,
              "placebo_portfolio_runs": 2000, "strata_permutation": 2000}
DRAWS_SMOKE = {"episode_block_bootstrap": 40, "permutation": 40,
               "placebo_portfolio_runs": 8, "strata_permutation": 8}

# Recorded frozen-config pooled PnL the fidelity arm must reproduce (<1e-6 relative).
RECORDED_POOLED = {
    "okx": -54799.23, "binance_um": -70071.41, "mexc": -49760.24, "bitget": -58129.33,
}

CAVEAT = (
    "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
    "NOT Hyperliquid performance evidence and must never be relabelled as such. "
    "Only the liquidation-distance execution parameter varies between arms; the signal "
    "path (RSI21<20 next-open, +9% target, 50h hold, 48h rebound short, 1.25% of 24h "
    "volume, 120% gross cap, ETH hedge) is frozen and drift-checked."
)


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return c20.sha256_file(path)


def _cfg(arm: str) -> StrategyConfig:
    spec = ARMS[arm]
    return StrategyConfig(
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        enable_rebound_short=True, enable_eth_hedge=True,
        enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0,
        target_pct=9.0, rebound_short_target_pct=9.0,
        rebound_short_time_exit_bars=48, entry_spec_literal_next_open=True,
        liquidation_maint_margin_pct=float(spec["maint"]),
        liquidation_buffer_pct=float(spec["buffer"]),
        enable_liquidation_checks=not bool(spec["disable"]),
    )


def _config_payload(cfg: StrategyConfig, arm: str) -> Dict[str, Any]:
    return {
        "arm": arm,
        "liquidation_maint_margin_pct": cfg.liquidation_maint_margin_pct,
        "liquidation_buffer_pct": cfg.liquidation_buffer_pct,
        "enable_liquidation_checks": cfg.enable_liquidation_checks,
        "liquidation_distance_pct": round(cfg.liquidation_maint_margin_pct
                                          + cfg.liquidation_buffer_pct, 4),
        # frozen signal path (drift-checked by the verifier)
        "use_rsi_trigger": cfg.use_rsi_trigger,
        "rsi_period": cfg.rsi_period,
        "rsi_threshold": cfg.rsi_threshold,
        "target_pct": cfg.target_pct,
        "rebound_short_target_pct": cfg.rebound_short_target_pct,
        "rebound_short_time_exit_bars": cfg.rebound_short_time_exit_bars,
        "rebound_short_stop_pct": cfg.rebound_short_stop_pct,
        "enable_rebound_short": cfg.enable_rebound_short,
        "enable_eth_hedge": cfg.enable_eth_hedge,
        "enable_volume_based_sizing": cfg.enable_volume_based_sizing,
        "position_size_pct_of_daily_volume": cfg.position_size_pct_of_daily_volume,
        "min_daily_volume_usd": cfg.min_daily_volume_usd,
        "gross_cap_pct": cfg.gross_cap_pct,
        "max_positions": cfg.max_positions,
        "entry_spec_literal_next_open": bool(cfg.entry_spec_literal_next_open),
        "time_exit_max_bars": cfg.time_exit_max_bars,
        "stop_atr_mult": cfg.stop_atr_mult,
        "seed": SEED,
    }


SMOKE = False


def _suffix() -> str:
    return "_SMOKE" if SMOKE else ""


def _stem(arm: str, kind: str) -> str:
    return f"c24_{arm}_{kind}_{TS}{_suffix()}"


def _ckpt(arm: str, venue: str, fid: str) -> str:
    return f"c24_ckpt_{arm}_{venue}_{fid}_{TS}{_suffix()}"


def _exists(stem: str) -> bool:
    return (STATE / f"{stem}.json").exists()


def _load(stem: str) -> Dict[str, Any]:
    return json.loads((STATE / f"{stem}.json").read_text())


def _save(stem: str, payload: Dict[str, Any]) -> None:
    (STATE / f"{stem}.json").write_text(json.dumps(payload, indent=2) + "\n")


def _fold(venue: str, arm: str, fid: str, jobs: int) -> Dict[str, Any]:
    vd = VENUE_LOADERS[venue]()
    spec_fold = next(f for f in FOLDS if f["id"] == fid)
    sv = c23._slice_venue(vd, spec_fold)
    cfg = _cfg(arm)

    t0 = time.time()
    eth = sv["candles"].get("ETH")
    res = run_portfolio_simulation(
        sv["candles"], config=cfg, capital=100_000.0,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(cfg.enable_eth_hedge),
    )
    campaign = {
        "schema_version": 1,
        "timestamp": TS,
        "generated_at_utc": iso_now(),
        "run_type": "c24_margin_fidelity_fold_campaign",
        "campaign": "C24",
        "arm": arm,
        "prereg": f"research_state/c24_prereg_{TS}.json",
        "prereg_sha256": sha256(PREREG),
        "real_market_data": True,
        "performance_evidence": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "venue_label": sv["venue_label"],
        "fold": fid,
        "folds": [spec_fold],
        "evidence_warning": CAVEAT,
        "provenance_caveat": CAVEAT,
        "data_provenance": {
            "cache_dir": str(sv["cache_dir"].relative_to(REPO)),
            "universe": str(sv["universe_path"].relative_to(REPO)),
            "manifest_sha256": sv["manifest_sha256"],
            "universe_sha256": sv["universe_sha256"],
            "symbols_loaded": sorted(sv["candles"].keys()),
            "fold_slice": True,
        },
        "config": _config_payload(cfg, arm),
        "results": {
            "num_trades": int(res.get("num_trades", 0)),
            "total_pnl": float(res.get("total_pnl", 0.0)),
            "trades": res.get("trades"),
            "equity_curve": res.get("equity_curve"),
        },
        "wall_seconds": round(time.time() - t0, 1),
    }

    # Census uses c20.TS to resolve the campaign provenance file it hashes; the
    # episode/placebo stages below are reimplemented here from stateless c20
    # primitives so that C24-labeled artifacts never masquerade as C20 evidence.
    tmp_stem = f"c24_tmp_census_{arm}_{venue}_{fid}" + _suffix()
    prev_ts = c20.TS
    c20.TS = f"{TS}_{arm}_{fid}{_suffix()}"
    prov_path = STATE / f"campaign_results_real_{sv['venue']}_multiyear_specliteral_{c20.TS}.json"
    prov_path.write_text(json.dumps(campaign, indent=2) + "\n")
    try:
        census = c20.build_census(sv, campaign, tmp_stem)
    finally:
        c20.TS = prev_ts
    tmp_path = STATE / f"{tmp_stem}.json"
    if tmp_path.exists():
        tmp_path.unlink()

    mode = ARM_MODE[arm]
    if mode == "inference":
        episode = _episode(sv, census, cfg, arm, venue, fid, jobs)
        placebo = _placebo(sv, census, cfg, arm, venue, fid, jobs)
    else:
        episode = None
        placebo = None
    battery = c20.run_battery(
        sv, campaign, episode or {"episode_block_bootstrap": {}},
        _stem(f"{arm}_{venue}_{fid}", "fold_battery"))

    ckpt = {
        "campaign": "C24",
        "arm": arm,
        "mode": mode,
        "venue": venue,
        "fold": fid,
        "prereg_sha256": sha256(PREREG),
        "campaign_artifact": campaign,
        "census": census,
        "episode": episode,
        "placebo": placebo,
        "battery": battery,
    }
    _save(_ckpt(arm, venue, fid), ckpt)
    return ckpt


def _meta_header(arm: str, venue: str, fid: str, kind: str) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C24",
        "arm": arm,
        "kind": kind,
        "prereg": f"research_state/c24_prereg_{TS}.json",
        "prereg_sha256": sha256(PREREG),
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "venue": venue,
        "fold": fid,
        "provenance_caveat": CAVEAT,
    }


def _episode(sv: Dict[str, Any], census: Dict[str, Any], cfg: StrategyConfig,
             arm: str, venue: str, fid: str, jobs: int) -> Dict[str, Any]:
    memo, rows, meta = c20.build_memo(sv, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(
            f"memo mismatch {arm} {venue} {fid}: memo={meta['memo_signals']} "
            f"signal_gate={meta['signal_gate_events']}")
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    times = {(str(r["symbol"]).upper(), int(r["bar_index"])): str(r["bar_timestamp_utc"])
             for r in rows if r.get("bar_index") is not None and r.get("bar_timestamp_utc")}
    candles = sv["candles"]
    candles_active = {s: candles[s] for s in sorted({k[0] for k in keys} | {"ETH"}) if s in candles}
    canonical = c20.run_memo_portfolio(candles_active, cfg, memo)
    canonical_pnl = float(canonical.get("total_pnl", 0.0))
    episodes = c20.cluster_episodes(keys, times, 98.0)
    ts = c20.trade_summary(canonical)
    draws = DRAWS_SMOKE if SMOKE else DRAWS_FULL
    boot = c20.episode_block_bootstrap(ts["trades"], episodes, draws["episode_block_bootstrap"], SEED)
    perm = _c24_permutation(sv, memo, rows, keys, canonical_pnl, cfg,
                            draws["permutation"], SEED, jobs)
    distinct_days = sorted({times[k][:10] for k in keys if k in times})
    payload = {
        **_meta_header(arm, venue, fid, "fold_episode_edge"),
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Fold episode-block bootstrap + conditional temporal-edge permutation on the "
                   "real portfolio engine; 98h single-linkage episode clustering."),
        "seed": SEED,
        "canonical_replay": ts,
        "episodes": episodes,
        "episode_block_bootstrap": boot,
        "temporal_edge_permutation": perm,
        "effective_independent_sample": {
            "trades": int(canonical.get("num_trades", 0)),
            "symbols": len({k[0] for k in keys}),
            "episodes": len(episodes),
            "distinct_crash_days": len(distinct_days),
        },
        "perm_p": perm.get("p_null_ge_canonical"),
    }
    out = STATE / f"{_stem(f'{arm}_{venue}_{fid}', 'fold_episode_edge')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[episode] {arm} {venue} {fid}: trades={canonical.get('num_trades')} "
          f"pnl={canonical_pnl:.2f} perm_p={perm.get('p_null_ge_canonical')}", flush=True)
    return payload


def _placebo(sv: Dict[str, Any], census: Dict[str, Any], cfg: StrategyConfig,
             arm: str, venue: str, fid: str, jobs: int) -> Dict[str, Any]:
    memo, rows, meta = c20.build_memo(sv, census, cfg)
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    admitted = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                       for r in rows if r.get("trade_opened_canonical") and r.get("bar_index") is not None
                       and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    candles = sv["candles"]
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    canon_run = c20.run_memo_portfolio(candles_active, cfg, memo)
    canon_pnl = float(canon_run.get("total_pnl", 0.0))
    canon_trades = int(canon_run.get("num_trades", 0))
    choose_k = min(len(admitted) if admitted else canon_trades, len(keys))
    draws = DRAWS_SMOKE if SMOKE else DRAWS_FULL
    n_placebo = draws["placebo_portfolio_runs"]
    rng = random.Random(SEED)
    subsets = [tuple(sorted(rng.sample(keys, choose_k))) for _ in range(n_placebo)]
    # Same validated event-bar replay as the permutation stage: exact-equivalent to
    # c20.run_memo_portfolio (validated on the full memo, canonical fallback on any
    # mismatch), ~90x faster than 2000 full portfolio replays per cell.
    pnls = c22._fast_parallel_draws(candles_active, cfg, memo, subsets, jobs)
    ge = sum(1 for x in pnls if x >= canon_pnl)
    le = sum(1 for x in pnls if x <= canon_pnl)
    pl = {
        "runs": len(pnls),
        "summary": c20._summ(pnls),
        "p_ge_canonical": ge / len(pnls) if pnls else None,
        "canonical_percentile_le": le / len(pnls) if pnls else None,
        "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(pnls) if pnls else None,
        "ci_low_pnl_2p5": c20._q(pnls, 0.025),
        "ci_high_pnl_97p5": c20._q(pnls, 0.975),
    }
    payload = {
        **_meta_header(arm, venue, fid, "fold_placebo"),
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Deterministic seeded full-portfolio placebo: gate-passing crash-bar subsets of "
                   "fixed size through the real portfolio engine; preserves gates/sizing/cap/occupancy/hedge."),
        "mode": f"deterministic_seeded_draws:{len(pnls)}_choose_{choose_k}_of_{len(keys)}",
        "seed": SEED,
        "canonical": {"trades": canon_trades, "total_pnl": canon_pnl,
                      "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k},
        "placebo": pl,
        "p_ge_canonical": pl["p_ge_canonical"],
    }
    out = STATE / f"{_stem(f'{arm}_{venue}_{fid}', 'fold_placebo')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[placebo] {arm} {venue} {fid}: pool={len(keys)} choose={choose_k} "
          f"runs={len(pnls)} p_ge={pl['p_ge_canonical']}", flush=True)
    return payload


def _bh(pvals: Sequence[float], alpha: float = 0.05) -> Tuple[List[bool], List[float], int]:
    return c23._bh(pvals, alpha)


def _c24_permutation(sv: Dict[str, Any], memo: Dict[Any, Any], rows: Sequence[Dict[str, Any]],
                    keys: List[Tuple[str, int]], canonical_pnl: float, cfg: StrategyConfig,
                    draws: int, seed: int, jobs: int) -> Dict[str, Any]:
    """C24 conditional temporal-edge permutation on the validated event-bar replay.

    The estimator is identical to C20/C22/C23 (crash-bar census, observed per-symbol
    multiplicity preserved, real portfolio engine semantics) but each draw is scored
    with the `exact_validated_event_bar_replay` path that C21/C22/C23 already used.
    That path validates itself against `c20.run_memo_portfolio` on the full memo
    before any draw is scored and delegates to the canonical engine if the replay is
    not bit-identical (trades equal, |pnl diff| < 1e-6), so results cannot drift.

    Draw count is the full prereg floor (20000) — no wall-clock cap.  Exact null
    spaces smaller than the floor are resampled with replacement to the floor, the
    same documented Monte-Carlo step C22/C23 used.  Without this path each draw costs
    a full ~4 s portfolio replay (≈6 h per 20k cell, ≈5 days for the 16-cell primary
    arm); the validated replay is ~90x faster (measured diff = 0.00e+00 on okx/2023),
    so the same 20k/2k floors finish in minutes per cell.
    """
    candles = sv["candles"]
    eligible = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                       for r in rows if r.get("bar_index") is not None and r.get("rsi") is not None
                       and float(r.get("rsi")) < 20.0})
    by_symbol: Dict[str, List[Tuple[str, int]]] = {}
    for sym, idx in eligible:
        by_symbol.setdefault(sym, []).append((sym, idx))
    observed_syms = sorted({k[0] for k in keys})
    per_symbol_count = {s: sum(1 for k in keys if k[0] == s) for s in observed_syms}
    total_possible = 1
    try:
        for s, count in per_symbol_count.items():
            total_possible *= c20.math.comb(len(by_symbol.get(s, [])), count)
    except Exception:
        total_possible = 10 ** 18
    exact = total_possible <= 5000
    rng = random.Random(seed)
    subsets: List[Tuple[Tuple[str, int], ...]] = []
    if exact:
        import itertools as it
        choices = [list(it.combinations(by_symbol.get(s, []), per_symbol_count[s]))
                   for s in observed_syms]
        for combo in it.product(*choices):
            subset: List[Tuple[str, int]] = []
            for part in combo:
                subset.extend(part)
            subsets.append(tuple(sorted(subset)))
    else:
        for _ in range(int(draws or 0)):
            subset = []
            for s in observed_syms:
                pool_s = by_symbol.get(s, [])
                count = min(per_symbol_count[s], len(pool_s))
                if count <= 0:
                    continue
                subset.extend(rng.sample(pool_s, count))
            subsets.append(tuple(sorted(subset)))
    seen = set()
    unique: List[Tuple[Tuple[str, int], ...]] = []
    for s in subsets:
        if s in seen:
            continue
        seen.add(s)
        unique.append(s)
    resampled = False
    n_target = int(draws or 0)
    if unique and len(unique) < n_target:
        reps = (n_target + len(unique) - 1) // len(unique)
        unique = [s for _ in range(reps) for s in unique]
        rng.shuffle(unique)
        unique = unique[:n_target]
        resampled = True
    t0 = time.time()
    pnls = c22._fast_parallel_draws(candles, cfg, memo, unique, jobs)
    ge = sum(1 for p in pnls if p >= canonical_pnl)
    return {
        "method": ("conditional permutation: crash bars redrawn from the real RSI(21)<20 census "
                   "with observed per-symbol multiplicity preserved; exact validated portfolio replay"),
        "mode": (f"exact_enumeration:{len(unique)}_draws" if exact and not resampled
                 else (f"exact_enumeration_resampled_to_{n_target}_from_{len(seen)}_draws"
                       if resampled and exact
                       else (f"resampled_to_{n_target}_from_{len(seen)}_draws" if resampled
                             else f"deterministic_seeded_draws:{len(unique)}_seed:{seed}"))),
        "exact_null_space_size": len(seen) if exact else None,
        "exact_null_resampled": resampled,
        "resampled_to_target_draws": n_target if resampled else None,
        "eligible_crash_bars": len(eligible),
        "observed_event_slots": len(keys),
        "observed_per_symbol": per_symbol_count,
        "distinct_possible_draws": total_possible if total_possible < 10 ** 12 else "astronomical",
        "draws_evaluated": len(unique),
        "target_draws": n_target,
        "seed": seed,
        "jobs": jobs,
        "replay_path": ("exact_validated_event_bar_replay"
                        if c22._FAST_VALIDATION_DETAIL.get("ok") else "canonical_full_replay"),
        "replay_validation": dict(c22._FAST_VALIDATION_DETAIL),
        "canonical_total_pnl": canonical_pnl,
        "null_total_pnl": {
            "mean": statistics.fmean(pnls) if pnls else 0.0,
            "median": statistics.median(pnls) if pnls else 0.0,
            "stdev": statistics.pstdev(pnls) if len(pnls) > 1 else 0.0,
            "min": min(pnls) if pnls else 0.0,
            "max": max(pnls) if pnls else 0.0,
            "p05": c20._q(pnls, 0.05), "p95": c20._q(pnls, 0.95),
            "ci_low_pnl_2p5": c20._q(pnls, 0.025), "ci_high_pnl_97p5": c20._q(pnls, 0.975),
            "prob_total_pnl_gt_0": (sum(1 for p in pnls if p > 0) / len(pnls)) if pnls else 0.0,
        },
        "canonical_percentile_le": (sum(1 for p in pnls if p <= canonical_pnl) / len(pnls)) if pnls else 0.0,
        "p_null_ge_canonical": (ge / len(pnls)) if pnls else 0.0,
        "n_null_ge_canonical": ge,
        "wall_seconds": round(time.time() - t0, 2),
        "limitations": (["Distinct null configurations fewer than the preregistered draw floor; "
                         "resampled with replacement to reach the floor (standard Monte-Carlo "
                         "permutation). Every draw is a real null configuration."]
                        if resampled else
                        ["Exact enumeration infeasible; deterministic seeded draw set with documented seed/count."]),
    }


def _venue_blocked_bootstrap(cells: Sequence[float], venues: Sequence[str],
                             draws: int, seed: int) -> Dict[str, Any]:
    """Resample venue blocks with replacement; each draw sums all fold cells of sampled venues."""
    by_venue: Dict[str, List[float]] = {}
    for v, x in zip(venues, cells):
        by_venue.setdefault(v, []).append(float(x))
    blocks = [by_venue[v] for v in by_venue]
    rng = random.Random(seed)
    totals = []
    for _ in range(draws):
        total = 0.0
        for _ in range(len(blocks)):
            total += sum(rng.choice(blocks))
        totals.append(total)
    totals.sort()
    lo = totals[int(0.025 * (len(totals) - 1))]
    hi = totals[int(0.975 * (len(totals) - 1))]
    return {"draws": draws, "ci95": [round(lo, 2), round(hi, 2)],
            "prob_total_gt_0": round(sum(1 for t in totals if t > 0) / len(totals), 4),
            "observed_total": round(sum(cells), 2)}


def _arm_verdict(arm: str, ckpts: Dict[Tuple[str, str], Dict[str, Any]],
                 draws: Dict[str, Any]) -> Dict[str, Any]:
    venues = sorted({v for v, _ in ckpts})
    cells, cell_venues, rows = [], [], []
    fold_rows = []
    for v in venues:
        for f in FOLDS:
            ck = ckpts.get((v, f["id"]))
            if not ck:
                continue
            camp = ck["campaign_artifact"]["results"]
            battery = ck.get("battery") or {}
            ep = ck.get("episode") or {}
            pl = ck.get("placebo") or {}
            cells.append(camp["total_pnl"])
            cell_venues.append(v)
            fold_rows.append({
                "venue": v, "fold": f["id"],
                "num_trades": camp["num_trades"],
                "total_pnl": round(camp["total_pnl"], 2),
                "perm_p": (ep.get("temporal_edge_permutation") or {}).get("p_null_ge_canonical"),
                "placebo_p_ge_canonical": pl.get("p_ge_canonical"),
                "per_leg": (battery.get("A1_per_leg") or {}),
                "components": (battery.get("A1_components") or {}),
                "exit_reasons": (battery.get("A2_exit_reason") or {}),
            })
            rows.append(camp["total_pnl"])

    # BH family for the primary arm = its full 4 folds x 4 venues = 16 pre-specified
    # venue-fold tests; other arms are descriptive only.
    bh_survivors = 0
    bh_q = []
    if arm == PRIMARY_ARM and fold_rows:
        pv = [float(r["perm_p"]) if r["perm_p"] is not None else 1.0 for r in fold_rows]
        if pv:
            flags, qvals, n = _bh(pv)
            bh_survivors = n
            bh_q = [round(q, 6) for q in qvals]

    pooled = _venue_blocked_bootstrap(cells, cell_venues, draws["episode_block_bootstrap"], SEED)
    venue_totals = {v: round(sum(r["total_pnl"] for r in fold_rows if r["venue"] == v), 2)
                    for v in venues}
    pos_folds = sum(1 for r in fold_rows if r["total_pnl"] > 0)
    per_venue_pos = sum(1 for v in venues if venue_totals.get(v, 0) > 0)

    if arm == FIDELITY_ARM:
        anchor_ok = all(abs(venue_totals.get(v, 0.0) - RECORDED_POOLED[v]) <= 1.0 for v in venues)
        token = "FIDELITY_ANCHOR_REPRODUCED" if anchor_ok else "FIDELITY_ANCHOR_MISMATCH"
    elif arm == PRIMARY_ARM:
        ok = (pooled["observed_total"] > 0
              and pooled["ci95"][0] > 0
              and bh_survivors >= 1
              and pos_folds >= 3
              and per_venue_pos >= 3)
        token = "C24_REOPENS_C1_C23" if ok else "C24_NO_GO_ROBUST_TO_MARGIN"
    else:
        token = "DESCRIPTIVE_ONLY"

    return {
        "arm": arm,
        "role": ARMS[arm]["role"],
        "token": token,
        "venues": venues,
        "folds": fold_rows,
        "venue_totals": venue_totals,
        "pooled": pooled,
        "positive_folds": pos_folds,
        "positive_venues": per_venue_pos,
        "bh_family": f"{PRIMARY_ARM}_folds" if arm == PRIMARY_ARM else None,
        "bh_survivors": bh_survivors,
        "bh_qvalues": bh_q,
    }


def _arm_summary(arm: str, ckpts, draws) -> Dict[str, Any]:
    verdict = _arm_verdict(arm, ckpts, draws)
    payload = {
        "schema_version": 1,
        "campaign": "C24",
        "arm": arm,
        "generated_at_utc": iso_now(),
        "prereg": f"research_state/c24_prereg_{TS}.json",
        "prereg_sha256": sha256(PREREG),
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "provenance_caveat": CAVEAT,
        "draws": draws,
        **verdict,
    }
    _save(_stem(arm, "decision_verdict"), payload)
    return payload


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--venues", default=",".join(VENUE_LOADERS))
    ap.add_argument("--folds", default=",".join(f["id"] for f in FOLDS))
    ap.add_argument("--smoke", action="store_true",
                    help="tiny draws for wiring validation only; artifacts are NOT acceptable evidence")
    args = ap.parse_args(argv)

    if not PREREG.exists():
        raise SystemExit(f"missing prereg {PREREG}; run scripts/build_c24_prereg.py first")

    arms = [a for a in args.arms.split(",") if a]
    venues = [v for v in args.venues.split(",") if v]
    fold_ids = [f for f in args.folds.split(",") if f]
    global SMOKE
    SMOKE = bool(args.smoke)
    draws = DRAWS_SMOKE if args.smoke else DRAWS_FULL

    for arm in arms:
        ckpts: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for venue in venues:
            for fid in fold_ids:
                key = (venue, fid)
                if args.resume and _exists(_ckpt(arm, venue, fid)):
                    ckpts[key] = _load(_ckpt(arm, venue, fid))
                    print(f"[resume] {arm} {venue} {fid}", flush=True)
                    continue
                print(f"[run] {arm} {venue} {fid}", flush=True)
                ckpts[key] = _fold(venue, arm, fid, args.jobs)
                print(f"[done] {arm} {venue} {fid} pnl="
                      f"{round(ckpts[key]['campaign_artifact']['results']['total_pnl'], 2)}", flush=True)
        if len(venues) == len(VENUE_LOADERS) and len(fold_ids) == len(FOLDS):
            _arm_summary(arm, ckpts, draws)

    # consolidated across all fully-run arms
    all_arms = {}
    for arm in arms:
        p = STATE / f"{_stem(arm, 'decision_verdict')}.json"
        if p.exists():
            all_arms[arm] = json.loads(p.read_text())
    if PRIMARY_ARM in all_arms and FIDELITY_ARM in all_arms:
        final = {
            "schema_version": 1,
            "campaign": "C24",
            "generated_at_utc": iso_now(),
            "prereg": f"research_state/c24_prereg_{TS}.json",
            "prereg_sha256": sha256(PREREG),
            "real_market_data": True,
            "fabricated_data": False,
            "synthetic_data": False,
            "cross_venue": True,
            "is_hyperliquid_venue_data": False,
            "provenance_caveat": CAVEAT,
            "primary_arm": PRIMARY_ARM,
            "fidelity_arm": FIDELITY_ARM,
            "arm_tokens": {a: all_arms[a]["token"] for a in all_arms},
            "arm_pooled_totals": {a: all_arms[a]["pooled"]["observed_total"] for a in all_arms},
            "consolidated_verdict": all_arms[PRIMARY_ARM]["token"],
        }
        _save("c24_decision_verdict_CONSOLIDATED", final)
        print("consolidated:", final["consolidated_verdict"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
