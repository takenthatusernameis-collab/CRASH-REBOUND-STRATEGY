#!/usr/bin/env python3
"""C30 — NEXT FOCUS CAMPAIGN scaffold for the crash-rebound edge fidelity frontier.

C30 is the mandatory same-session successor on C29 ACCEPTANCE: PASS in the
`C24 -> C25 -> C26 -> C27 -> C28 -> C29 -> C30+` heavy queue. Per the HANDOFF no-avoidance
rule, no session may idle, declare "no authorized work", substitute a frozen-signal
parameter search, retry closed data acquisitions, zero-fill funding, reduce draw
counts (20k/20k/2k/2k floors), or relaunch a finished campaign. C30 opens the
execution-realism stress axis:

  C30-A execution_realism_stress : 3x empirical slippage + venue taker
      commission (exec_base FIDELITY_ANCHOR / exec_stress PRIMARY).

Common invariants across all directions:
  - real market data only, cross_venue=true, is_hyperliquid_venue_data=false
  - signal path frozen to C24/C25/C26 sentinel (drift-checked)
  - liquidation distance fixed at C24 primary d15 (maint=14, buffer=1 => 15%)
  - draw floors 20k bootstrap / 20k permutation / 2k placebo / 2k strata
  - anchor verification against the prior primary arm BEFORE inference
  - BH correction per venue-fold family; terminal tokens only
  - no same-data rerun, no parameter search, no reduced draws

C30 may NOT launch until C29 ACCEPTANCE: PASS (sequential adjudication chain).
This runner prints a warning and refuses heavy compute until that gate exists.

Run (from repo root, after C29 ACCEPTANCE: PASS):
  PYTHONPATH=. .venv/bin/python scripts/run_c30_campaign.py --direction c30-a --jobs 4 --resume
  PYTHONPATH=. .venv/bin/python scripts/verify_c30_focus_campaign.py --direction c30-a   # -> C30 ACCEPTANCE: PASS
  bash scripts/status_c30.sh --direction c30-a
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import json
import random
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
from scripts import draw_checkpoint  # noqa: E402
from scripts.run_portfolio import run_portfolio_simulation  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402

TS = "20261121T051754Z"
STATE = REPO / "research_state"
PREREG = STATE / f"c30_prereg_{TS}.json"
SEED = 20261201

FOLDS = [
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
VENUES = list(VENUE_LOADERS)

LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISABLE = False

DIRECTION_ARM_CONFIG: Dict[str, Dict[str, Dict[str, Any]]] = {
    "c30-a": {
        "exec_base": {
            "slippage_pct": 0.0005,
            "commission_per_share": 0.001,
            "commission_min": 1.0,
            "funding_rate_pct_per_hour": 0.01,
            "gross_cap_pct": 120.0,
            "role": "FIDELITY_ANCHOR",
        },
        "exec_stress": {
            # 3x empirical slippage stress; slippage_pct is consumed per side by
            # the hourly engine (src/backtest/engine.py). Taker commission is
            # resolved per venue from TAKER_BPS when commission_per_share is None.
            "slippage_pct": 0.0015,
            "commission_per_share": None,
            "commission_min": 1.0,
            "funding_rate_pct_per_hour": 0.01,
            "gross_cap_pct": 120.0,
            "role": "PRIMARY",
        },
    },
}

TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0
BORROW_BPS = 5.0

ARM_MODE = "inference"
DRAWS_FULL = {"episode_block_bootstrap": 20000, "permutation": 20000,
              "placebo_portfolio_runs": 2000, "strata_permutation": 2000}

SMOKE = False


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return c20.sha256_file(path)


def _taker_commission_per_share(venue: str) -> float:
    return round(REFERENCE_PX * TAKER_BPS[venue] / 10000.0, 6)


_FUNDING_LOOKUP_CACHE: Dict[str, Optional[Dict[Tuple[str, int], float]]] = {}


def _funding_csv_path(venue: str) -> Optional[Path]:
    matches = glob.glob(str(STATE / "cache" / f"{venue}_funding_*"))
    if not matches:
        return None
    return Path(matches[0]) / "funding_history.csv"


def _load_funding_lookup(venue: str) -> Optional[Dict[Tuple[str, int], float]]:
    if venue in _FUNDING_LOOKUP_CACHE:
        return _FUNDING_LOOKUP_CACHE[venue]
    p = _funding_csv_path(venue)
    if p is None or not p.exists():
        _FUNDING_LOOKUP_CACHE[venue] = None
        return None
    lookup: Dict[Tuple[str, int], float] = {}
    try:
        with p.open(newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sym = row["symbol"].upper()
                ts_ms = int(row["funding_time_ms"])
                rate = float(row["funding_rate"])
                lookup[(sym, ts_ms)] = rate * 100.0 / 8.0
    except Exception:  # noqa: BLE001
        _FUNDING_LOOKUP_CACHE[venue] = None
        return None
    _FUNDING_LOOKUP_CACHE[venue] = lookup
    return lookup


def _enrich_candles_with_funding(candles: Dict[str, List[Dict[str, Any]]],
                                 lookup: Dict[Tuple[str, int], float]) -> Dict[str, List[Dict[str, Any]]]:
    enriched: Dict[str, List[Dict[str, Any]]] = {}
    for sym, clist in candles.items():
        new_list = []
        for c in clist:
            cc = dict(c)
            key = (sym, int(c.get("timestamp_ms", c.get("timestamp", 0))))
            rate = lookup.get(key)
            if rate is not None:
                cc["funding_rate_pct_per_hour"] = rate
            new_list.append(cc)
        enriched[sym] = new_list
    return enriched


def _prereg() -> Dict[str, Any]:
    if not PREREG.exists():
        raise SystemExit(f"missing prereg {PREREG}; run scripts/build_c30_prereg.py first")
    return json.loads(PREREG.read_text())


def _direction() -> str:
    return _prereg()["direction"]


def _arms_for(direction: str) -> Dict[str, Dict[str, Any]]:
    # Per-arm execution params (slippage/commission/funding/gross_cap + role) live
    # in DIRECTION_ARM_CONFIG; the prereg `arms` block carries only {role, why}
    # for human-readable pre-registration. Resolving through the prereg here was a
    # latent KeyError that made the runner crash before any cell ran.
    return DIRECTION_ARM_CONFIG[direction]


def _cfg(direction: str, arm: str, venue: str,
         funding_lookup: Optional[Dict[Tuple[str, int], float]]) -> StrategyConfig:
    spec = _arms_for(direction)[arm]
    comm = spec["commission_per_share"]
    if comm is None:
        comm = _taker_commission_per_share(venue)
    funding = spec["funding_rate_pct_per_hour"]
    return StrategyConfig(
        use_rsi_trigger=True, rsi_period=21, rsi_threshold=20.0,
        enable_rebound_short=True, enable_eth_hedge=True,
        enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0,
        target_pct=9.0, rebound_short_target_pct=9.0,
        rebound_short_time_exit_bars=48, entry_spec_literal_next_open=True,
        liquidation_maint_margin_pct=LIQ_MAINT,
        liquidation_buffer_pct=LIQ_BUFFER,
        enable_liquidation_checks=not LIQ_DISABLE,
        slippage_pct=float(spec["slippage_pct"]),
        commission_per_share=float(comm),
        commission_min=float(spec["commission_min"]),
        funding_rate_pct_per_hour=float(funding),
        intrabar_adverse_first=False,
        per_trade_funding=False,
        gross_cap_pct=float(spec.get("gross_cap_pct", 120.0)),
    )


def _config_payload(cfg: StrategyConfig, arm: str, venue: str,
                    direction: str, funding_available: bool) -> Dict[str, Any]:
    spec = _arms_for(direction)[arm]
    return {
        "arm": arm,
        "direction": direction,
        "venue": venue,
        "slippage_pct": cfg.slippage_pct,
        "commission_per_share": cfg.commission_per_share,
        "commission_min": cfg.commission_min,
        "funding_rate_pct_per_hour": cfg.funding_rate_pct_per_hour,
        "funding_available": funding_available,
        "gross_cap_pct": cfg.gross_cap_pct,
        "per_venue_cap_pct": spec.get("per_venue_cap_pct"),  # descriptive only; hourly engine enforces gross_cap_pct
        "liquidation_maint_margin_pct": cfg.liquidation_maint_margin_pct,
        "liquidation_buffer_pct": cfg.liquidation_buffer_pct,
        "liquidation_distance_pct": round(cfg.liquidation_maint_margin_pct + cfg.liquidation_buffer_pct, 4),
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
        "prereg_sha256": sha256(PREREG),
    }


def _suffix() -> str:
    return "_SMOKE" if SMOKE else ""


def _stem(direction: str, arm: str, kind: str) -> str:
    return f"c30_{direction}_{arm}_{kind}_{TS}{_suffix()}"


def _ckpt(direction: str, arm: str, venue: str, fid: str) -> str:
    return f"c30_ckpt_{direction}_{arm}_{venue}_{fid}_{TS}{_suffix()}"


def _exists(stem: str) -> bool:
    return (STATE / f"{stem}.json").exists()


def _load(stem: str) -> Dict[str, Any]:
    return json.loads((STATE / f"{stem}.json").read_text())


def _save(stem: str, payload: Dict[str, Any]) -> None:
    (STATE / f"{stem}.json").write_text(json.dumps(payload, indent=2) + "\n")


def _fold(direction: str, venue: str, arm: str, fid: str, jobs: int,
          funding_lookup: Optional[Dict[Tuple[str, int], float]]) -> Dict[str, Any]:
    vd = VENUE_LOADERS[venue]()
    spec_fold = next(f for f in FOLDS if f["id"] == fid)
    sv = c23._slice_venue(vd, spec_fold)

    spec = _arms_for(direction)[arm]
    if spec.get("holdout_window"):
        holdout = STATE / f"c30_holdout_manifest_{venue}_{fid}.json"
        if not holdout.exists():
            ckpt = {
                "campaign": "C30",
                "direction": direction,
                "arm": arm,
                "mode": "inference",
                "venue": venue,
                "fold": fid,
                "unavailable_funding": True,
                "holdout_window_missing": True,
                "note": "strict temporal OOS holdout requires a new never-scored data "
                        "manifest; no same-data rerun permitted",
            }
            _save(_ckpt(direction, arm, venue, fid), ckpt)
            return ckpt

    candles = sv["candles"]
    cfg = _cfg(direction, arm, venue, funding_lookup)

    t0 = time.time()
    eth = sv["candles"].get("ETH")
    res = run_portfolio_simulation(
        candles, config=cfg, capital=100_000.0,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(cfg.enable_eth_hedge),
    )
    campaign = {
        "schema_version": 1,
        "timestamp": TS,
        "generated_at_utc": iso_now(),
        "run_type": "c30_next_focus_campaign",
        "campaign": "C30",
        "direction": direction,
        "arm": arm,
        "prereg": f"research_state/c30_prereg_{TS}.json",
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
        "evidence_warning": (
            "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
            "NOT Hyperliquid performance evidence and must never be relabelled as such."
        ),
        "provenance_caveat": (
            "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
            "NOT Hyperliquid performance evidence and must never be relabelled as such."
        ),
        "data_provenance": {
            "cache_dir": str(sv["cache_dir"].relative_to(REPO)),
            "universe": str(sv["universe_path"].relative_to(REPO)),
            "manifest_sha256": sv["manifest_sha256"],
            "universe_sha256": sv["universe_sha256"],
            "symbols_loaded": sorted(candles.keys()),
            "fold_slice": True,
        },
        "config": _config_payload(cfg, arm, venue, direction, funding_lookup is not None),
        "results": {
            "num_trades": int(res.get("num_trades", 0)),
            "total_pnl": float(res.get("total_pnl", 0.0)),
            "trades": res.get("trades"),
            "equity_curve": res.get("equity_curve"),
        },
        "wall_seconds": round(time.time() - t0, 1),
    }

    tmp_stem = f"c30_tmp_census_{direction}_{arm}_{venue}_{fid}" + _suffix()
    prev_ts = c20.TS
    c20.TS = f"{TS}_{direction}_{arm}_{fid}{_suffix()}"
    prov_path = STATE / f"campaign_results_real_{sv['venue']}_multiyear_specliteral_{c20.TS}.json"
    prov_path.write_text(json.dumps(campaign, indent=2) + "\n")
    try:
        census = c20.build_census(sv, campaign, tmp_stem)
    finally:
        c20.TS = prev_ts
    tmp_path = STATE / f"{tmp_stem}.json"
    if tmp_path.exists():
        tmp_path.unlink()

    episode = _episode(sv, census, cfg, arm, venue, fid, jobs, candles, direction)
    placebo = _placebo(sv, census, cfg, arm, venue, fid, jobs, candles, direction)
    battery = c20.run_battery(
        sv, campaign, episode or {"episode_block_bootstrap": {}},
        _stem(f"{direction}_{arm}_{venue}_{fid}", "fold_battery"))

    ckpt = {
        "campaign": "C30",
        "direction": direction,
        "arm": arm,
        "mode": "inference",
        "venue": venue,
        "fold": fid,
        "unavailable_funding": False,
        "funding_rate_pct_per_hour": cfg.funding_rate_pct_per_hour,
        "prereg_sha256": sha256(PREREG),
        "campaign_artifact": campaign,
        "census": census,
        "episode": episode,
        "placebo": placebo,
        "battery": battery,
    }
    _save(_ckpt(direction, arm, venue, fid), ckpt)
    for stage in ("perm", "placebo"):
        draw_checkpoint.clear_partials(STATE, "C30", TS, stage=stage,
                                       direction=direction, arm=arm, venue=venue, fold=fid)
    return ckpt


def _meta_header(direction: str, arm: str, venue: str, fid: str, kind: str) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C30",
        "direction": direction,
        "arm": arm,
        "kind": kind,
        "prereg": f"research_state/c30_prereg_{TS}.json",
        "prereg_sha256": sha256(PREREG),
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "venue": venue,
        "fold": fid,
        "provenance_caveat": (
            "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
            "NOT Hyperliquid performance evidence and must never be relabelled as such."
        ),
    }


def _episode(sv: Dict[str, Any], census: Dict[str, Any], cfg: StrategyConfig,
             arm: str, venue: str, fid: str, jobs: int,
             candles: Dict[str, List[Dict[str, Any]]], direction: str) -> Dict[str, Any]:
    memo, rows, meta = c20.build_memo(sv, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(
            f"memo mismatch {direction} {arm} {venue} {fid}: memo={meta['memo_signals']} "
            f"signal_gate={meta['signal_gate_events']}")
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    times = {(str(r["symbol"]).upper(), int(r["bar_index"])): str(r["bar_timestamp_utc"])
             for r in rows if r.get("bar_index") is not None and r.get("bar_timestamp_utc")}
    candles_active = {s: candles[s] for s in sorted({k[0] for k in keys} | {"ETH"}) if s in candles}
    canonical = c20.run_memo_portfolio(candles_active, cfg, memo)
    canonical_pnl = float(canonical.get("total_pnl", 0.0))
    episodes = c20.cluster_episodes(keys, times, 98.0)
    ts = c20.trade_summary(canonical)
    draws = DRAWS_FULL
    boot = c20.episode_block_bootstrap(ts["trades"], episodes, draws["episode_block_bootstrap"], SEED)
    perm = _c30_permutation(sv, memo, rows, keys, canonical_pnl, cfg,
                            draws["permutation"], SEED, jobs, arm, venue, fid, direction)
    distinct_days = sorted({times[k][:10] for k in keys if k in times})
    payload = {
        **_meta_header(direction, arm, venue, fid, "fold_episode_edge"),
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
    out = STATE / f"{_stem(f'{direction}_{arm}_{venue}_{fid}', 'fold_episode_edge')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[episode] {direction} {arm} {venue} {fid}: trades={canonical.get('num_trades')} "
          f"pnl={canonical_pnl:.2f} perm_p={perm.get('p_null_ge_canonical')}", flush=True)
    return payload


def _placebo(sv: Dict[str, Any], census: Dict[str, Any], cfg: StrategyConfig,
             arm: str, venue: str, fid: str, jobs: int,
             candles: Dict[str, List[Dict[str, Any]]], direction: str) -> Dict[str, Any]:
    memo, rows, meta = c20.build_memo(sv, census, cfg)
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    admitted = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                       for r in rows if r.get("trade_opened_canonical") and r.get("bar_index") is not None
                       and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    canon_run = c20.run_memo_portfolio(candles_active, cfg, memo)
    canon_pnl = float(canon_run.get("total_pnl", 0.0))
    canon_trades = int(canon_run.get("num_trades", 0))
    choose_k = min(len(admitted) if admitted else canon_trades, len(keys))
    draws = DRAWS_FULL
    n_placebo = draws["placebo_portfolio_runs"]
    rng = random.Random(SEED)
    subsets = [tuple(sorted(rng.sample(keys, choose_k))) for _ in range(n_placebo)]
    results = draw_checkpoint.run_chunked(
        state_dir=STATE, campaign="C30", tag=TS, stage="placebo",
        direction=direction, arm=arm, venue=venue, fold=fid, subsets=subsets, jobs=jobs,
        prereg_sha256=sha256(PREREG), seed=SEED,
        draw_many=draw_checkpoint.make_c20_draw_many(candles_active, memo, cfg, jobs))
    pnls = [r["total_pnl"] for r in results]
    ge = sum(1 for x in pnls if x >= canon_pnl)
    le = sum(1 for x in pnls if x <= canon_pnl)
    pl = {
        "runs": len(results),
        "summary": c20._summ(pnls),
        "p_ge_canonical": ge / len(results) if results else None,
        "canonical_percentile_le": le / len(results) if results else None,
        "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(results) if results else None,
        "ci_low_pnl_2p5": c20._q(pnls, 0.025),
        "ci_high_pnl_97p5": c20._q(pnls, 0.975),
    }
    payload = {
        **_meta_header(direction, arm, venue, fid, "fold_placebo"),
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Deterministic seeded full-portfolio placebo: gate-passing crash-bar subsets of "
                   "fixed size through the real portfolio engine; preserves gates/sizing/cap/occupancy/hedge."),
        "mode": f"deterministic_seeded_draws:{len(results)}_choose_{choose_k}_of_{len(keys)}",
        "seed": SEED,
        "canonical": {"trades": canon_trades, "total_pnl": canon_pnl,
                      "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k},
        "placebo": pl,
        "p_ge_canonical": pl["p_ge_canonical"],
    }
    out = STATE / f"{_stem(f'{direction}_{arm}_{venue}_{fid}', 'fold_placebo')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[placebo] {direction} {arm} {venue} {fid}: pool={len(keys)} choose={choose_k} "
          f"runs={len(results)} p_ge={pl['p_ge_canonical']}", flush=True)
    return payload


def _bh(pvals: Sequence[float], alpha: float = 0.05) -> Tuple[List[bool], List[float], int]:
    return c23._bh(pvals, alpha)


def _c30_permutation(sv: Dict[str, Any], memo: Dict[Any, Any], rows: Sequence[Dict[str, Any]],
                    keys: List[Tuple[str, int]], canonical_pnl: float, cfg: StrategyConfig,
                    draws: int, seed: int, jobs: int,
                    arm: str = "?", venue: str = "?", fid: str = "?", direction: str = "?") -> Dict[str, Any]:

    def _exec(unique, candles_active, memo_w, cfg_w, jobs_w):
        return draw_checkpoint.run_chunked(
            state_dir=STATE, campaign="C30", tag=TS, stage="perm",
            direction=direction, arm=arm, venue=venue, fold=fid, subsets=unique, jobs=jobs_w,
            prereg_sha256=sha256(PREREG), seed=seed,
            draw_many=draw_checkpoint.make_c20_draw_many(candles_active, memo_w, cfg_w, jobs_w))

    return c20.conditional_permutation_null(
        sv, memo, rows, keys, canonical_pnl, cfg, draws, seed, jobs,
        max_permutation_draws=draws, draw_executor=_exec)


def _venue_blocked_bootstrap(cells: Sequence[float], venues: Sequence[str],
                             draws: int, seed: int) -> Dict[str, Any]:
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


def _anchor_reference(direction: str) -> Optional[Dict[str, float]]:
    """Prior primary-arm per-venue/per-fold PnL used as the C30 fidelity anchor.

    C30-A anchors on C29 primary-arm (holdout_primary) venue_totals.
    Returns None until the reference exists (i.e. until C29 has produced it).
    """
    ref_path = STATE / "c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json"
    if ref_path.exists():
        try:
            return json.loads(ref_path.read_text()).get("venue_totals") or {}
        except Exception:  # noqa: BLE001
            return None
    return None


def _arm_verdict(direction: str, arm: str, ckpts: Dict[Tuple[str, str], Dict[str, Any]],
                 draws: Dict[str, Any]) -> Dict[str, Any]:
    prereg = _prereg()
    arms_cfg = _arms_for(direction)
    venues = sorted({v for v, _ in ckpts})
    cells, cell_venues, rows = [], [], []
    fold_rows = []
    unavailable = [f"{v}/{f['id']}" for v in venues for f in FOLDS
                   if ckpts.get((v, f["id"]), {}).get("unavailable_funding")]
    for v in venues:
        for f in FOLDS:
            ck = ckpts.get((v, f["id"]))
            if not ck:
                continue
            if ck.get("unavailable_funding"):
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

    bh_survivors = 0
    bh_q = []
    is_primary = arms_cfg[arm]["role"] == "PRIMARY"
    if is_primary and fold_rows:
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

    anchor_ref = _anchor_reference(direction)
    anchor_ok = False
    if anchor_ref:
        anchor_ok = all(abs(venue_totals.get(v, 0.0) - float(anchor_ref.get(v, 0.0))) <= 1.0
                        for v in venues)
    fidelity_arm = next(a for a, cfg_ in arms_cfg.items() if cfg_["role"] == "FIDELITY_ANCHOR")
    token_ok = prereg["anchor_rule"]["token_ok"]

    if arm == fidelity_arm:
        if anchor_ref and anchor_ok:
            token = token_ok
        elif anchor_ref and not anchor_ok:
            token = "PATH_ANCHOR_MISMATCH"
        else:
            token = "ANCHOR_UNDETERMINED_PRIOR_PENDING"
    elif is_primary:
        ok = (pooled["observed_total"] > 0
              and pooled["ci95"][0] > 0
              and bh_survivors >= 1
              and pos_folds >= 3
              and per_venue_pos >= 3
              and anchor_ok)
        token = "C30_REOPENS_C1_C29" if ok else "C30_NO_GO_ROBUST_TO_EXECUTION"
    else:
        token = "DESCRIPTIVE_ONLY"

    return {
        "arm": arm,
        "direction": direction,
        "role": arms_cfg[arm]["role"],
        "token": token,
        "venues": venues,
        "unavailable_funding": unavailable,
        "folds": fold_rows,
        "venue_totals": venue_totals,
        "pooled": pooled,
        "positive_folds": pos_folds,
        "positive_venues": per_venue_pos,
        "bh_family": f"{arm}_folds" if is_primary else None,
        "bh_survivors": bh_survivors,
        "bh_qvalues": bh_q,
        "anchor_reproduced": anchor_ok,
    }


def _arm_summary(direction: str, arm: str, ckpts, draws) -> Dict[str, Any]:
    verdict = _arm_verdict(direction, arm, ckpts, draws)
    payload = {
        "schema_version": 1,
        "campaign": "C30",
        "direction": direction,
        "arm": arm,
        "generated_at_utc": iso_now(),
        "prereg": f"research_state/c30_prereg_{TS}.json",
        "prereg_sha256": sha256(PREREG),
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "provenance_caveat": (
            "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
            "NOT Hyperliquid performance evidence and must never be relabelled as such."
        ),
        "draws": draws,
        **verdict,
    }
    _save(_stem(direction, arm, "decision_verdict"), payload)
    return payload


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="C30 next-focus campaign runner")
    ap.add_argument("--direction", required=True, choices=sorted(DIRECTION_ARM_CONFIG),
                    help="C30 direction to run (c30-a)")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny draws for wiring validation only; artifacts are NOT acceptable evidence")
    args = ap.parse_args(argv)

    if not PREREG.exists():
        raise SystemExit(f"missing prereg {PREREG}; run scripts/build_c30_prereg.py first")

    prereg = _prereg()
    if prereg.get("prereg_status") != "PRE_REGISTERED_BEFORE_COMPUTE":
        raise SystemExit("C30 prereg is not PRE_REGISTERED_BEFORE_COMPUTE; refusing to run")

    # C30 is blocked on C29 completion (primary-arm anchor must exist).
    c29_passed = (STATE / "c29_decision_verdict_CONSOLIDATED_20261121T031907Z.json").exists()
    if not c29_passed:
        raise SystemExit(
            "C29 ACCEPTANCE: not yet PASS; C30 may not run until C29 completes "
            "(sequential adjudication chain C25 -> C26 -> C27 -> C28 -> C29 -> C30). "
            "Anchor reference (C29 primary-arm venue_totals) is not yet available. "
            "Re-run this campaign only after C29 ACCEPTANCE: PASS."
        )

    direction = args.direction
    arms = list(_arms_for(direction).keys())
    venues = list(VENUE_LOADERS)
    fold_ids = [f["id"] for f in FOLDS]
    global SMOKE
    SMOKE = bool(args.smoke)
    draws = DRAWS_FULL

    funding_lookups: Dict[str, Optional[Dict[Tuple[str, int], float]]] = {}
    for v in venues:
        funding_lookups[v] = _load_funding_lookup(v)

    for arm in arms:
        ckpts: Dict[Tuple[str, str], Dict[str, Any]] = {}
        for venue in venues:
            for fid in fold_ids:
                key = (venue, fid)
                if args.resume and _exists(_ckpt(direction, arm, venue, fid)):
                    ckpts[key] = _load(_ckpt(direction, arm, venue, fid))
                    print(f"[resume] {direction} {arm} {venue} {fid}", flush=True)
                    continue
                print(f"[run] {direction} {arm} {venue} {fid}", flush=True)
                ckpts[key] = _fold(direction, venue, arm, fid, args.jobs,
                                   funding_lookups.get(venue))
                if not ckpts[key].get("unavailable_funding"):
                    print(f"[done] {direction} {arm} {venue} {fid} pnl="
                          f"{round(ckpts[key]['campaign_artifact']['results']['total_pnl'], 2)}", flush=True)
                else:
                    print(f"[done] {direction} {arm} {venue} {fid} UNAVAILABLE_FUNDING", flush=True)
        _arm_summary(direction, arm, ckpts, draws)

    all_arms = {}
    for arm in arms:
        p = STATE / f"{_stem(direction, arm, 'decision_verdict')}.json"
        if p.exists():
            all_arms[arm] = json.loads(p.read_text())
    primary_arm = next(a for a, cfg_ in _arms_for(direction).items() if cfg_["role"] == "PRIMARY")
    fidelity_arm = next(a for a, cfg_ in _arms_for(direction).items() if cfg_["role"] == "FIDELITY_ANCHOR")
    if primary_arm in all_arms and fidelity_arm in all_arms:
        final = {
            "schema_version": 1,
            "campaign": "C30",
            "direction": direction,
            "generated_at_utc": iso_now(),
            "prereg": f"research_state/c30_prereg_{TS}.json",
            "prereg_sha256": sha256(PREREG),
            "real_market_data": True,
            "fabricated_data": False,
            "synthetic_data": False,
            "cross_venue": True,
            "is_hyperliquid_venue_data": False,
            "provenance_caveat": (
                "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
                "NOT Hyperliquid performance evidence and must never be relabelled as such."
            ),
            "primary_arm": primary_arm,
            "fidelity_arm": fidelity_arm,
            "arm_tokens": {a: all_arms[a]["token"] for a in all_arms},
            "arm_pooled_totals": {a: all_arms[a]["pooled"]["observed_total"] for a in all_arms},
            "consolidated_verdict": all_arms[primary_arm]["token"],
        }
        _save(f"c30_decision_verdict_CONSOLIDATED_{TS}", final)
        print("consolidated:", final["consolidated_verdict"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
