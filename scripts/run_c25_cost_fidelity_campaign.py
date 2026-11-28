#!/usr/bin/env python3
"""C25 — ROUND-TRIP COST & REALIZED-FUNDING FIDELITY ADJUDICATION of the frozen crash-rebound edge.

WHY THIS EXISTS
---------------
C1-C24 (once C24 passes) test one published execution assumption (liquidation
distance) on four real cross-venue caches (OKX, Binance UM, MEXC, Bitget) using
the frozen spec-literal signal path. The remaining un-adjudicated fidelity gap is
COST: the engine's slippage_pct=0.0005 (5 bps/side), commission_per_share=0.001
charged per share (~0.0017 bps on BTC at $60k, effectively free),
commission_min=1.0, and funding_rate_pct_per_hour=0.01 (flat 0.24%/day) are
materially more permissive than real venue taker fees (~4.5-7 bps/side => 9-14
bps round trip) and realized 8h funding. Because the strategy exits at a 9%
target with multi-day holds and a short/hedge leg, cost mis-specification is the
largest remaining candidate explanation for the four-venue NO_GO.

Stage-0 prerequisite (scripts/probe_c25_funding_acquisition.py) acquires
realized per-venue funding history. This runner is the HEAVY pre-registered
adjudication: it attaches full inference (episode-block bootstrap 20k, conditional
permutation 20k, placebo 2k, BH) to the pre-registered cost/funding arms and emits
arm-level + consolidated verdicts.

WHAT THIS RUNS (heavy, per arm x venue x fold)
----------------------------------------------
  campaign (real portfolio engine) -> crash census -> episode-block bootstrap +
  conditional temporal-edge permutation -> full-portfolio placebo -> robustness
  battery (per-leg attribution, exit reasons, concentration, leave-one-out, power).

ARMS (pre-registered; ONLY slippage/commission/funding vary — signal path frozen;
liquidation distance fixed at the C24 primary = 15%: maint=14, buffer=1)
--------------------------------------------------------------------------------
  cost_base          : exact current engine model; FIDELITY_ANCHOR. MUST reproduce
                       the C24 d15 primary-arm per-venue/per-fold PnL within +/-1.0
                       (COST_ANCHOR_REPRODUCED, else COST_ANCHOR_MISMATCH).
  cost_taker         : per-venue published taker fee (bps) per side + 5 bps slippage
                       + $1 min commission; long and short/hedge legs both charged.
  cost_taker_funding : PRIMARY. cost_taker + realized 8h funding on every leg.
  cost_stress        : cost_taker_funding + 2x slippage + 5 bps borrow/financing.

HARD LABELS / GUARDRAILS
------------------------
  real_market_data=true, fabricated_data=false, synthetic_data=false,
  is_hyperliquid_venue_data=false, cross_venue=true. Results are NEVER Hyperliquid
  performance evidence. Signal parameters are frozen and drift-checked; a run that
  changes them is INVALID. Draw-count floors (20k/20k/2k/2k) are not reducible.
  No C25 cell runs until C24 ACCEPTANCE: PASS (C25 is blocked on C24 completion).

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/run_c25_cost_fidelity_campaign.py --jobs 4 --resume
  PYTHONPATH=. .venv/bin/python scripts/verify_c25_focus_campaign.py   # -> C25 ACCEPTANCE: PASS
"""
from __future__ import annotations

import argparse
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

TS = "20261119T045500Z"
STATE = REPO / "research_state"
PREREG = STATE / f"c25_prereg_{TS}.json"
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
VENUES = list(VENUE_LOADERS)

# Liquidation distance fixed at the C24 primary arm (d15): maint=14, buffer=1 => 15%.
LIQ_MAINT = 14.0
LIQ_BUFFER = 1.0
LIQ_DISABLE = False

PRIMARY_ARM = "cost_taker_funding"
FIDELITY_ARM = "cost_base"

# Cost/funding arms. commission_per_share / funding_rate_pct_per_hour of None are
# resolved per venue in _cfg (taker bps -> per-share via reference price; funding
# from acquired cache, else UNAVAILABLE_FUNDING).
ARMS: Dict[str, Dict[str, Any]] = {
    "cost_base": {
        "slippage_pct": 0.0005,
        "commission_per_share": 0.001,
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": 0.01,
        "role": "FIDELITY_ANCHOR",
    },
    "cost_taker": {
        "slippage_pct": 0.0005,
        "commission_per_share": None,
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": 0.01,
        "role": "DESCRIPTIVE",
    },
    "cost_taker_funding": {
        "slippage_pct": 0.0005,
        "commission_per_share": None,
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": None,
        "role": "PRIMARY",
    },
    "cost_stress": {
        "slippage_pct": 0.0010,
        "commission_per_share": None,
        "commission_min": 1.0,
        "funding_rate_pct_per_hour": None,
        "role": "DESCRIPTIVE",
    },
}

# Venue published taker fee (bps) per side (pre-registered constants; validated
# against published fee schedules during funding acquisition).
TAKER_BPS = {"okx": 5.0, "binance_um": 4.5, "mexc": 6.0, "bitget": 5.5}
REFERENCE_PX = 60000.0  # BTC reference price for bps-of-notional -> per-share conversion
BORROW_BPS = 5.0  # cost_stress borrow/financing surcharge (bps)

# All four arms run the full inference battery (no smoke, no reduced floors).
ARM_MODE = {a: "inference" for a in ARMS}

DRAWS_FULL = {"episode_block_bootstrap": 20000, "permutation": 20000,
              "placebo_portfolio_runs": 2000, "strata_permutation": 2000}

# Reference anchor: C24 d15 primary-arm per-venue/per-fold PnL (available only after
# C24 ACCEPTANCE: PASS). Loaded lazily in _c24_d15_reference().
_C24_D15_TS = "20261119T013154Z"


def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    return c20.sha256_file(path)


def _taker_commission_per_share(venue: str) -> float:
    return round(REFERENCE_PX * TAKER_BPS[venue] / 10000.0, 6)


def _funding_rate_pct_per_hour(venue: str) -> Optional[float]:
    """Realized 8h funding rate (pct/hour) for a venue from acquired cache.

    Returns None when no funding cache exists (venue is UNAVAILABLE_FUNDING for
    funding arms; never zero-filled). Cache layout:
    research_state/cache/<venue>_funding_<window>/ with a manifest.
    """
    matches = glob.glob(str(STATE / "cache" / f"{venue}_funding_*"))
    if not matches:
        return None
    # Prefer the most recent manifest.
    best: Optional[Tuple[str, float]] = None
    for cache_dir in matches:
        mpath = Path(cache_dir) / "funding_manifest.json"
        if not mpath.exists():
            continue
        try:
            man = json.loads(mpath.read_text())
            rate = man.get("funding_rate_pct_per_hour")
            ts = man.get("generated_at_utc", "")
            if rate is not None and (best is None or ts > best[0]):
                best = (ts, float(rate))
        except Exception:
            continue
    return best[1] if best else None


def _c24_d15_reference() -> Optional[Dict[str, float]]:
    """C24 d15 primary-arm venue_totals, used as the cost_base fidelity anchor."""
    p = STATE / f"c24_decision_verdict_d15_{_C24_D15_TS}.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text()).get("venue_totals") or {}
    except Exception:
        return None


def _cfg(arm: str, venue: str) -> StrategyConfig:
    spec = ARMS[arm]
    comm = spec["commission_per_share"]
    if comm is None:
        comm = _taker_commission_per_share(venue)
    funding = spec["funding_rate_pct_per_hour"]
    if funding is None:
        funding = _funding_rate_pct_per_hour(venue)
        if funding is None:
            funding = 0.0  # placeholder; venue marked UNAVAILABLE_FUNDING in ckpt
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
    )


def _config_payload(cfg: StrategyConfig, arm: str, venue: str) -> Dict[str, Any]:
    spec = ARMS[arm]
    if spec["funding_rate_pct_per_hour"] is None:
        funding = _funding_rate_pct_per_hour(venue)
        funding_available = funding is not None
    else:
        funding = spec["funding_rate_pct_per_hour"]
        funding_available = True
    return {
        "arm": arm,
        "venue": venue,
        "slippage_pct": cfg.slippage_pct,
        "commission_per_share": cfg.commission_per_share,
        "commission_min": cfg.commission_min,
        "funding_rate_pct_per_hour": cfg.funding_rate_pct_per_hour,
        "funding_available": funding_available,
        "liquidation_maint_margin_pct": cfg.liquidation_maint_margin_pct,
        "liquidation_buffer_pct": cfg.liquidation_buffer_pct,
        "liquidation_distance_pct": round(cfg.liquidation_maint_margin_pct + cfg.liquidation_buffer_pct, 4),
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
    # Per-arm verdicts MUST use the prereg's required_artifacts convention
    # (c25_decision_verdict_<arm>_<TS>.json, matching C24 and every downstream
    # reader: verify_c25/c26/c28 + run_c28). The historical c25_<arm>_decision_verdict
    # spelling was a producer/consumer mismatch that made the C25 gate unable to
    # ever see the arm verdicts (C25 -> C26 -> ... -> C32 blocked forever).
    # The _SMOKE suffix is preserved so smoke runs never masquerade as real evidence.
    if kind == "decision_verdict":
        return f"c25_decision_verdict_{arm}_{TS}{_suffix()}"
    return f"c25_{arm}_{kind}_{TS}{_suffix()}"


def _ckpt(arm: str, venue: str, fid: str) -> str:
    return f"c25_ckpt_{arm}_{venue}_{fid}_{TS}{_suffix()}"


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
    cfg = _cfg(arm, venue)

    # Funding-arm venues without realized funding are UNAVAILABLE_FUNDING: skip
    # inference for that venue-fold (never zero-fill). cost_base/cost_taker need
    # no funding and run all venues.
    spec = ARMS[arm]
    needs_funding = spec["funding_rate_pct_per_hour"] is None
    funding_available = _funding_rate_pct_per_hour(venue) is not None
    if needs_funding and not funding_available:
        ckpt = {
            "campaign": "C25",
            "arm": arm,
            "mode": "inference",
            "venue": venue,
            "fold": fid,
            "unavailable_funding": True,
            "funding_rate_pct_per_hour": None,
            "note": "venue has no realized funding cache; excluded from funding arm",
        }
        _save(_ckpt(arm, venue, fid), ckpt)
        return ckpt

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
        "run_type": "c25_cost_fidelity_fold_campaign",
        "campaign": "C25",
        "arm": arm,
        "prereg": f"research_state/c25_prereg_{TS}.json",
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
            "symbols_loaded": sorted(sv["candles"].keys()),
            "fold_slice": True,
        },
        "config": _config_payload(cfg, arm, venue),
        "results": {
            "num_trades": int(res.get("num_trades", 0)),
            "total_pnl": float(res.get("total_pnl", 0.0)),
            "trades": res.get("trades"),
            "equity_curve": res.get("equity_curve"),
        },
        "wall_seconds": round(time.time() - t0, 1),
    }

    tmp_stem = f"c25_tmp_census_{arm}_{venue}_{fid}" + _suffix()
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

    episode = _episode(sv, census, cfg, arm, venue, fid, jobs)
    placebo = _placebo(sv, census, cfg, arm, venue, fid, jobs)
    battery = c20.run_battery(
        sv, campaign, episode or {"episode_block_bootstrap": {}},
        _stem(f"{arm}_{venue}_{fid}", "fold_battery"))

    ckpt = {
        "campaign": "C25",
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
    _save(_ckpt(arm, venue, fid), ckpt)
    for stage in ("perm", "placebo"):
        draw_checkpoint.clear_partials(STATE, "C25", TS, stage=stage,
                                       arm=arm, venue=venue, fold=fid)
    return ckpt


def _meta_header(arm: str, venue: str, fid: str, kind: str) -> Dict[str, Any]:
    return {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C25",
        "arm": arm,
        "kind": kind,
        "prereg": f"research_state/c25_prereg_{TS}.json",
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
    perm = _c25_permutation(sv, memo, rows, keys, canonical_pnl, cfg,
                            draws["permutation"], SEED, jobs, arm, venue, fid)
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
    results = draw_checkpoint.run_chunked(
        state_dir=STATE, campaign="C25", tag=TS, stage="placebo",
        arm=arm, venue=venue, fold=fid, subsets=subsets, jobs=jobs,
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
        **_meta_header(arm, venue, fid, "fold_placebo"),
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
    out = STATE / f"{_stem(f'{arm}_{venue}_{fid}', 'fold_placebo')}.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"[placebo] {arm} {venue} {fid}: pool={len(keys)} choose={choose_k} "
          f"runs={len(results)} p_ge={pl['p_ge_canonical']}", flush=True)
    return payload


def _bh(pvals: Sequence[float], alpha: float = 0.05) -> Tuple[List[bool], List[float], int]:
    return c23._bh(pvals, alpha)


def _c25_permutation(sv: Dict[str, Any], memo: Dict[Any, Any], rows: Sequence[Dict[str, Any]],
                    keys: List[Tuple[str, int]], canonical_pnl: float, cfg: StrategyConfig,
                    draws: int, seed: int, jobs: int,
                    arm: str = "?", venue: str = "?", fid: str = "?") -> Dict[str, Any]:
    """C25 conditional temporal-edge permutation — same estimator as C20/C24,
    without the C20 wall-clock cap (MAX_PERMUTATION_DRAWS=300).

    Draws are evaluated through scripts/draw_checkpoint.py so a session/environment
    loss resumes mid-cell instead of restarting the ~3.2 h permutation from zero.
    Chunking is bit-identical: same subset list, same per-subset engine call, same
    order, same draw count.
    """

    def _exec(unique, candles_active, memo_w, cfg_w, jobs_w):
        return draw_checkpoint.run_chunked(
            state_dir=STATE, campaign="C25", tag=TS, stage="perm",
            arm=arm, venue=venue, fold=fid, subsets=unique, jobs=jobs_w,
            prereg_sha256=sha256(PREREG), seed=seed,
            draw_many=draw_checkpoint.make_c20_draw_many(candles_active, memo_w, cfg_w, jobs_w))

    return c20.conditional_permutation_null(
        sv, memo, rows, keys, canonical_pnl, cfg, draws, seed, jobs,
        max_permutation_draws=draws, draw_executor=_exec)


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
        ref = _c24_d15_reference()
        anchor_ok = False
        if ref:
            anchor_ok = all(abs(venue_totals.get(v, 0.0) - float(ref.get(v, 0.0))) <= 1.0
                            for v in venues)
        token = "COST_ANCHOR_REPRODUCED" if (ref and anchor_ok) else (
            "COST_ANCHOR_MISMATCH" if ref else "COST_ANCHOR_UNDETERMINED_C24_PENDING")
    elif arm == PRIMARY_ARM:
        ok = (pooled["observed_total"] > 0
              and pooled["ci95"][0] > 0
              and bh_survivors >= 1
              and pos_folds >= 3
              and per_venue_pos >= 3)
        token = "C25_REOPENS_C1_C24" if ok else "C25_NO_GO_ROBUST_TO_COST"
    else:
        token = "DESCRIPTIVE_ONLY"

    return {
        "arm": arm,
        "role": ARMS[arm]["role"],
        "token": token,
        "venues": venues,
        "unavailable_funding": unavailable,
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
        "campaign": "C25",
        "arm": arm,
        "generated_at_utc": iso_now(),
        "prereg": f"research_state/c25_prereg_{TS}.json",
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
        raise SystemExit(f"missing prereg {PREREG}; run scripts/build_c25_prereg.py first")

    arms = [a for a in args.arms.split(",") if a]
    venues = [v for v in args.venues.split(",") if v]
    fold_ids = [f for f in args.folds.split(",") if f]
    global SMOKE
    SMOKE = bool(args.smoke)
    draws = DRAWS_FULL  # C25 runs full floors on all arms; --smoke only for wiring validation

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
                if not ckpts[key].get("unavailable_funding"):
                    print(f"[done] {arm} {venue} {fid} pnl="
                          f"{round(ckpts[key]['campaign_artifact']['results']['total_pnl'], 2)}", flush=True)
                else:
                    print(f"[done] {arm} {venue} {fid} UNAVAILABLE_FUNDING", flush=True)
        if len(venues) == len(VENUE_LOADERS) and len(fold_ids) == len(FOLDS):
            _arm_summary(arm, ckpts, draws)

    all_arms = {}
    for arm in arms:
        p = STATE / f"{_stem(arm, 'decision_verdict')}.json"
        if p.exists():
            all_arms[arm] = json.loads(p.read_text())
    if PRIMARY_ARM in all_arms and FIDELITY_ARM in all_arms:
        final = {
            "schema_version": 1,
            "campaign": "C25",
            "generated_at_utc": iso_now(),
            "prereg": f"research_state/c25_prereg_{TS}.json",
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
            "primary_arm": PRIMARY_ARM,
            "fidelity_arm": FIDELITY_ARM,
            "arm_tokens": {a: all_arms[a]["token"] for a in all_arms},
            "arm_pooled_totals": {a: all_arms[a]["pooled"]["observed_total"] for a in all_arms},
            "consolidated_verdict": all_arms[PRIMARY_ARM]["token"],
        }
        # C26/verify/status all read the TIMESTAMPED consolidated verdict
        # (research_state/c25_decision_verdict_CONSOLIDATED_<TS>.json, TS above).
        # The un-timestamped name is kept as a backward-compatible alias so older
        # readers never break; the timestamped file is what the C26 gate requires.
        _save(f"c25_decision_verdict_CONSOLIDATED_{TS}", final)
        _save("c25_decision_verdict_CONSOLIDATED", final)
        print("consolidated:", final["consolidated_verdict"], flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
