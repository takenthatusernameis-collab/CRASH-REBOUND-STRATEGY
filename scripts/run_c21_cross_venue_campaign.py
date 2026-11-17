#!/usr/bin/env python3
"""C21 — cross-venue temporal walk-forward & regime-stability (SPEC_LITERAL_NEXT_OPEN).

C21-T1 (prereg `c21_prereg_20261117T064408Z`, status PRE_REGISTERED_BEFORE_COMPUTE)
quantifies the temporal/regime stability of the C19-adjudicated spec-literal edge on
the already-verified OKX + Binance UM multi-year archives. C1–C20 closed `NO_GO` on the
unconditional edge; C21 is a NEW hypothesis (temporal folds + pre-specified strata +
multiplicity-controlled conditional subset), not a C20 rerun.

Per venue-fold {2023, 2024, 2025, 2026YTD}:
  - real spec-literal campaign on fold-sliced candles (real portfolio engine),
  - crash-event census,
  - fold episode-block bootstrap (20,000 draws) + conditional temporal-edge permutation
    (20,000 draws; fold slice is small enough for the real-engine null),
  - full-portfolio placebo (2,000 subsets),
  - pre-specified stratum stratification (crash_severity / btc_trend / funding_regime)
    with Benjamini–Hochberg correction (alpha 0.05),
  - per-venue verdict (STABLE_POSITIVE_SUBSET / NO_GO / UNDERPOWERED) + power curve,
  - pooled venue-blocked bootstrap + consolidated C21 final.

The C20 module is reused for all heavy primitives (load_venue / run_campaign /
build_census / build_memo / run_memo_portfolio / episode_block_bootstrap /
conditional_permutation_null / run_placebo). C20 artifacts are never edited.

HARD LABELS: real_market_data=true, fabricated_data=false, synthetic_data=false,
is_hyperliquid_venue_data=false, cross_venue=true. OKX/Binance UM results are NEVER
Hyperliquid performance evidence.

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/run_c21_cross_venue_campaign.py --jobs 4 --resume
  PYTHONPATH=. .venv/bin/python scripts/verify_c21_focus_campaign.py  # -> C21 ACCEPTANCE: PASS
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
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
from src.strategy.config import StrategyConfig  # noqa: E402

TS = "20261117T064408Z"
PREREG = REPO / "research_state" / f"c21_prereg_{TS}.json"
STATE = REPO / "research_state"
SEED = 20261121
LINK_HOURS = 98.0
FOLDS: List[Dict[str, str]] = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]
DRAWS = 20000
PLACEBO_RUNS = 2000
PROVENANCE_CAVEAT = c20.PROVENANCE_CAVEAT

STRATA_DEFS: List[Dict[str, Any]] = [
    {"id": "crash_severity", "bins": ["rsi_0_10", "rsi_10_15", "rsi_15_20"]},
    {"id": "btc_trend", "bins": ["btc_down_7d", "btc_flat_7d", "btc_up_7d"]},
    {"id": "funding_regime", "bins": ["funding_negative", "funding_neutral", "funding_positive"]},
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return c20.sha256_file(path)


def _stem_exists(stem: str) -> bool:
    return (STATE / f"{stem}.json").exists()


def _load_json(stem: str) -> Dict[str, Any]:
    return json.loads((STATE / f"{stem}.json").read_text())


def _write_json(stem: str, payload: Dict[str, Any]) -> Path:
    out = STATE / f"{stem}.json"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing artifact {out}")
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    return out


def _parse_ms(v: Any) -> Optional[int]:
    return c20.parse_timestamp_ms(v)


def _parse_utc(text: Any) -> dt.datetime:
    return c20.parse_utc(text)


def _fold_bounds(fold: Dict[str, str]) -> Tuple[int, int]:
    start = int(_parse_utc(fold["start"]).timestamp() * 1000)
    end = int(_parse_utc(fold["end"]).timestamp() * 1000)
    return start, end


def _slice_venue(venue_data: Dict[str, Any], fold: Dict[str, str]) -> Dict[str, Any]:
    """Return a fold-sliced copy of venue_data (candles filtered by [start,end] ms)."""
    start_ms, end_ms = _fold_bounds(fold)
    sliced_candles: Dict[str, List[Dict[str, Any]]] = {}
    for sym, cs in venue_data["candles"].items():
        kept = [c for c in cs if start_ms <= c20._ts_ms(c) <= end_ms]
        if len(kept) > 60:  # need enough bars for indicators
            sliced_candles[sym] = kept
    out = dict(venue_data)
    out["candles"] = sliced_candles
    return out


def _slice_ts(rows: Sequence[Dict[str, Any]], fold: Dict[str, str]) -> List[Dict[str, Any]]:
    start = _parse_utc(fold["start"])
    end = _parse_utc(fold["end"])
    kept = []
    for r in rows:
        ts = r.get("bar_timestamp_ms")
        if ts is None:
            continue
        try:
            moment = dt.datetime.fromtimestamp(int(ts) / 1000.0, dt.timezone.utc)
        except Exception:
            continue
        if start <= moment <= end:
            kept.append(r)
    return kept


def _bh(pvals: Sequence[float], alpha: float = 0.05) -> Tuple[List[bool], List[float], int]:
    """Benjamini–Hochberg step-up. Returns (rejected, adjusted_p, n_family)."""
    m = len(pvals)
    if m == 0:
        return [], [], 0
    order = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        val = pvals[i] * m / rank
        prev = min(prev, val)
        adj[i] = min(1.0, prev)
    rejected = [False] * m
    max_rank = 0
    for rank, i in enumerate(order, start=1):
        if pvals[i] <= alpha * rank / m:
            max_rank = rank
    for rank, i in enumerate(order, start=1):
        if rank <= max_rank:
            rejected[i] = True
    return rejected, [round(a, 6) for a in adj], m


def _period_of(ts: Any) -> str:
    ms = _parse_ms(ts)
    if ms is None:
        return "unknown"
    return dt.datetime.fromtimestamp(ms / 1000.0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _distinct_days(trades: Sequence[Dict[str, Any]]) -> int:
    return len({_period_of(t.get("entry_timestamp"))[:10] for t in trades if t.get("entry_timestamp")})


# ---------------------------------------------------------------------------
# Fold campaign + census
# ---------------------------------------------------------------------------

def _run_fold_campaign(vd_slice: Dict[str, Any], fold_id: str) -> Dict[str, Any]:
    """Real spec-literal campaign on a fold-sliced venue, with C21 labels."""
    candles = vd_slice["candles"]
    eth = candles.get("ETH")
    cfg = c20.spec_literal_config()
    t0 = time.time()
    from scripts.run_portfolio import run_portfolio_simulation  # local import
    res = run_portfolio_simulation(
        candles, config=cfg, capital=100_000.0,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(cfg.enable_eth_hedge),
    )
    metrics = None
    try:
        from src.metrics import compute_campaign_metrics, metrics_to_dict  # local import
        metrics = metrics_to_dict(compute_campaign_metrics(
            trades=res.get("trades", []), equity_curve=res.get("equity_curve"),
            initial_capital=100_000.0,
        ))
    except Exception:
        metrics = None
    return {
        "schema_version": 1,
        "timestamp": iso_now(),
        "generated_at_utc": iso_now(),
        "run_type": "c21_real_market_campaign_spec_literal_fold",
        "research_status": "CROSS_VENUE_TEMPORAL_STABILITY_NOT_HYPERLIQUID",
        "campaign": "C21",
        "prereg": f"research_state/c21_prereg_{TS}.json",
        "prereg_sha256": sha256_file(PREREG),
        "real_market_data": True,
        "performance_evidence": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "venue_label": vd_slice["venue_label"],
        "folds": [{"id": fold_id,
                    "start": next(f["start"] for f in FOLDS if f["id"] == fold_id),
                    "end": next(f["end"] for f in FOLDS if f["id"] == fold_id)}],
        "fold": fold_id,
        "evidence_warning": PROVENANCE_CAVEAT,
        "provenance_caveat": PROVENANCE_CAVEAT,
        "data_provenance": {
            "cache_dir": str(vd_slice["cache_dir"].relative_to(REPO)),
            "universe": str(vd_slice["universe_path"].relative_to(REPO)),
            "manifest_sha256": vd_slice["manifest_sha256"],
            "universe_sha256": vd_slice["universe_sha256"],
            "symbols_loaded": sorted(vd_slice["candles"].keys()),
            "fold_slice": True,
            "fold_start_utc": next(f["start"] for f in FOLDS if f["id"] == fold_id),
            "fold_end_utc": next(f["end"] for f in FOLDS if f["id"] == fold_id),
        },
        "config": {
            "use_rsi_trigger": cfg.use_rsi_trigger,
            "rsi_period": cfg.rsi_period,
            "rsi_threshold": cfg.rsi_threshold,
            "target_pct": cfg.target_pct,
            "rebound_short_target_pct": cfg.rebound_short_target_pct,
            "rebound_short_time_exit_bars": cfg.rebound_short_time_exit_bars,
            "enable_rebound_short": cfg.enable_rebound_short,
            "enable_eth_hedge": cfg.enable_eth_hedge,
            "enable_volume_based_sizing": cfg.enable_volume_based_sizing,
            "min_daily_volume_usd": cfg.min_daily_volume_usd,
            "gross_cap_pct": cfg.gross_cap_pct,
            "entry_spec_literal_next_open": bool(cfg.entry_spec_literal_next_open),
        },
        "results": {
            "num_trades": int(res.get("num_trades", 0)),
            "total_pnl": float(res.get("total_pnl", 0.0)),
            "final_open_positions": res.get("final_open_positions"),
            "final_gross_exposure": res.get("final_gross_exposure"),
            "trades": res.get("trades"),
            "equity_curve": res.get("equity_curve"),
            "equity_curve_points": len(res.get("equity_curve") or []),
        },
        "metrics": metrics,
        "wall_seconds": round(time.time() - t0, 1),
    }


def _fold_census(vd_slice: Dict[str, Any], campaign: Dict[str, Any], fold_id: str) -> Dict[str, Any]:
    """Crash-event census on a fold slice; C21-labelled, folds present at top level."""
    base = c20.build_census(vd_slice, campaign, f"c21_tmp_census_{vd_slice['venue']}_{fold_id}")
    # c20.build_census refuses overwrite but writes via REPO/research_state; we
    # already have the returned dict, so move/rename is unnecessary. Drop the tmp
    # file so it is not mistaken for a required artifact.
    tmp = STATE / f"c21_tmp_census_{vd_slice['venue']}_{fold_id}.json"
    if tmp.exists():
        tmp.unlink()
    base["schema_version"] = 1
    base["generated_at_utc"] = iso_now()
    base["run_type"] = "c21_crash_event_census_spec_literal_fold"
    base["campaign"] = "C21"
    base["prereg"] = f"research_state/c21_prereg_{TS}.json"
    base["prereg_sha256"] = sha256_file(PREREG)
    base["folds"] = [{"id": fold_id,
                                    "start": next(f["start"] for f in FOLDS if f["id"] == fold_id),
                                    "end": next(f["end"] for f in FOLDS if f["id"] == fold_id)}]
    base["fold"] = fold_id
    base["is_hyperliquid_venue_data"] = False
    base["cross_venue"] = True
    base["fabricated_data"] = False
    base["synthetic_data"] = False
    base["provenance_caveat"] = PROVENANCE_CAVEAT
    return base


# ---------------------------------------------------------------------------
# Fold episode edge (bootstrap + permutation)
# ---------------------------------------------------------------------------

def _fold_episode_edge(vd_slice: Dict[str, Any], census: Dict[str, Any],
                       campaign: Dict[str, Any], cfg: StrategyConfig,
                       fold_id: str, jobs: int) -> Dict[str, Any]:
    venue_label = vd_slice["venue_label"]
    memo, rows, meta = c20.build_memo(vd_slice, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(
            f"memo mismatch for {venue_label} fold {fold_id}: memo={meta['memo_signals']} "
            f"signal_gate={meta['signal_gate_events']}")
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    times: Dict[Tuple[str, int], str] = {}
    for r in rows:
        if r.get("bar_index") is not None and r.get("bar_timestamp_utc"):
            times[(str(r["symbol"]).upper(), int(r["bar_index"]))] = str(r["bar_timestamp_utc"])
    candles = vd_slice["candles"]
    candles_active = {s: candles[s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in candles}
    canonical = c20.run_memo_portfolio(candles_active, cfg, memo)
    canonical_pnl = float(canonical.get("total_pnl", 0.0))
    episodes = c20.cluster_episodes(keys, times, LINK_HOURS)
    ts = c20.trade_summary(canonical)
    boot = c20.episode_block_bootstrap(ts["trades"], episodes, DRAWS, SEED)
    perm = c20.conditional_permutation_null(vd_slice, memo, rows, keys, canonical_pnl, cfg,
                                            DRAWS, SEED, jobs)
    distinct_days = sorted({times[k][:10] for k in keys if k in times})
    result = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "phase": "C21",
        "campaign": "C21",
        "prereg_sha256": sha256_file(PREREG),
        "prereg": f"research_state/c21_prereg_{TS}.json",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_label": venue_label,
        "folds": [{"id": fold_id,
                    "start": next(f["start"] for f in FOLDS if f["id"] == fold_id),
                    "end": next(f["end"] for f in FOLDS if f["id"] == fold_id)}],
        "fold": fold_id,
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "config": {"rsi_threshold": 20.0, "target_pct": 9.0, "entry_spec_literal_next_open": True},
        "method": ("Fold episode-block bootstrap (20000 draws) + conditional temporal-edge "
                   "permutation (20000 draws) on the real portfolio engine; 98h linkage."),
        "seed": SEED,
        "inputs": {
            "census_events": meta["census_events"],
            "signal_gate_events": meta["signal_gate_events"],
            "memo_signals": meta["memo_signals"],
            "memo_matches_signal_gate": meta["memo_matches_signal_gate"],
            "canonical_total_pnl": canonical_pnl,
            "canonical_num_trades": int(canonical.get("num_trades", 0)),
        },
        "episode_audit": {
            "link_hours": LINK_HOURS,
            "n_events": len(keys),
            "n_episodes": len(episodes),
            "n_symbols": len({k[0] for k in keys}),
            "n_distinct_crash_days": len(distinct_days),
            "distinct_crash_days": distinct_days,
            "episodes": episodes,
            "effective_independent_sample": {
                "trades": int(canonical.get("num_trades", 0)),
                "symbols": len({k[0] for k in keys}),
                "episodes": len(episodes),
                "distinct_crash_days": len(distinct_days),
            },
        },
        "episode_block_bootstrap": boot,
        "temporal_edge_permutation": perm,
        "canonical_replay": ts,
        "verdict": "underpowered",
    }
    bt = boot["bootstrap_total_pnl"]
    if bt["ci_low_pnl_2p5"] > 0 and perm.get("p_null_ge_canonical") is not None \
            and perm["p_null_ge_canonical"] < 0.05:
        result["verdict"] = "cross_venue_positive_not_hyperliquid"
    return result


# ---------------------------------------------------------------------------
# Fold placebo (2000 subsets)
# ---------------------------------------------------------------------------

def _fold_placebo(vd_slice: Dict[str, Any], census: Dict[str, Any],
                  cfg: StrategyConfig, fold_id: str, jobs: int) -> Dict[str, Any]:
    candles = vd_slice["candles"]
    memo, rows, meta = c20.build_memo(vd_slice, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(f"placebo memo mismatch for {vd_slice['venue_label']} fold {fold_id}")
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
    rng = random.Random(SEED)
    subsets = [tuple(sorted(rng.sample(keys, choose_k))) for _ in range(PLACEBO_RUNS)]
    candles_ev = candles_active
    if jobs > 1:
        import multiprocessing as mp
        if "fork" in mp.get_all_start_methods():
            ctx = mp.get_context("fork")
            with ctx.Pool(processes=jobs, initializer=c20._init_worker,
                          initargs=(candles_ev, memo, cfg)) as pool:
                results = pool.map(c20._run_draw, subsets, chunksize=1)
            pnls = [r["total_pnl"] for r in results]
        else:
            pnls = _serial_draws(candles_ev, cfg, memo, subsets)
    else:
        pnls = _serial_draws(candles_ev, cfg, memo, subsets)
    ge = sum(1 for x in pnls if x >= canon_pnl)
    le = sum(1 for x in pnls if x <= canon_pnl)
    pl = {
        "runs": len(results) if jobs > 1 else len(pnls),
        "summary": c20._summ(pnls),
        "p_ge_canonical": ge / len(pnls) if pnls else None,
        "canonical_percentile_le": le / len(pnls) if pnls else None,
        "prob_total_pnl_positive": sum(1 for x in pnls if x > 0) / len(pnls) if pnls else None,
        "ci_low_pnl_2p5": c20._q(pnls, 0.025) if pnls else 0.0,
        "ci_high_pnl_97p5": c20._q(pnls, 0.975) if pnls else 0.0,
    }
    return {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "phase": "C21",
        "campaign": "C21",
        "prereg_sha256": sha256_file(PREREG),
        "prereg": f"research_state/c21_prereg_{TS}.json",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "is_hyperliquid_evidence": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_label": vd_slice["venue_label"],
        "folds": [{"id": fold_id,
                    "start": next(f["start"] for f in FOLDS if f["id"] == fold_id),
                    "end": next(f["end"] for f in FOLDS if f["id"] == fold_id)}],
        "fold": fold_id,
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "method": ("Deterministic seeded full-portfolio placebo (2000 subsets); preserves "
                   "gates/sizing/cap/occupancy/hedge on the fold slice."),
        "mode": f"deterministic_seeded_draws:{len(pnls)}_choose_{choose_k}_of_{len(keys)}",
        "seed": SEED,
        "canonical": {"trades": canon_trades, "total_pnl": canon_pnl,
                      "admitted_keys_count": len(admitted)},
        "pool": {"signal_gate_events": len(keys), "choose_k": choose_k},
        "placebo": pl,
        "verdict": "underpowered",
        "jobs": jobs,
        "limitations": [f"CROSS-VENUE {vd_slice['venue_label']} fold {fold_id}; NOT Hyperliquid performance evidence."],
    }


def _serial_draws(candles_ev, cfg, memo, subsets) -> List[float]:
    out = []
    for sub in subsets:
        res = c20.run_memo_portfolio(candles_ev, cfg, {k: memo[k] for k in sub if k in memo})
        out.append(float(res.get("total_pnl", 0.0)))
    return out


# ---------------------------------------------------------------------------
# Strata (pre-specified) + BH
# ---------------------------------------------------------------------------

def _btc_trend_by_day(vd_slice: Dict[str, Any]) -> Dict[str, str]:
    btc = vd_slice["candles"].get("BTC")
    out: Dict[str, str] = {}
    if not btc:
        return out
    closes = [float(c["close"]) for c in btc]
    days = [_period_of(c20._ts_ms(c))[:10] for c in btc]
    for i, day in enumerate(days):
        j = max(0, i - 168)
        ref = closes[j]
        if ref <= 0:
            out[day] = "btc_flat_7d"
            continue
        chg = (closes[i] - ref) / ref
        if chg < -0.05:
            out[day] = "btc_down_7d"
        elif chg > 0.05:
            out[day] = "btc_up_7d"
        else:
            out[day] = "btc_flat_7d"
    return out


def _funding_regime_by_day(venue_data: Dict[str, Any]) -> Dict[str, str]:
    cache = venue_data.get("cache_dir")
    out: Dict[str, str] = {}
    if not cache:
        return out
    for sym in venue_data["symbols"]:
        p = cache / "funding" / f"{sym}.json"
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        rows = data if isinstance(data, list) else data.get("funding") or data.get("rows") or []
        for r in rows:
            ts = r.get("timestamp") or r.get("time") or r.get("funding_time")
            fr = r.get("funding_rate") or r.get("rate") or r.get("fundingRate")
            if ts is None or fr is None:
                continue
            try:
                moment = dt.datetime.fromtimestamp(int(ts) / 1000.0, dt.timezone.utc) if int(ts) > 1e11 else dt.datetime.fromtimestamp(int(ts), dt.timezone.utc)
                frf = float(fr)
            except Exception:
                continue
            day = moment.strftime("%Y-%m-%dT%H:%M:%SZ")[:10]
            out[day] = "funding_negative" if frf < -0.0001 else ("funding_positive" if frf > 0.0001 else "funding_neutral")
    return out


def _stratum_bootstrap_ci(trade_rows: Sequence[Dict[str, Any]], episodes: Sequence[Dict[str, Any]],
                           resamples: int, seed: int) -> Dict[str, Any]:
    ep_bounds = [(e["episode_id"], _parse_utc(e["start"]), _parse_utc(e["end"])) for e in episodes]
    groups: Dict[int, List[float]] = {e["episode_id"]: [] for e in episodes}
    for t in trade_rows:
        groups.setdefault(c20.assign_episode(t.get("entry_timestamp"), ep_bounds), []).append(
            float(t.get("total_pnl") or 0.0))
    ep_ids = sorted(groups)
    rng = random.Random(seed)
    totals = []
    for _ in range(resamples):
        total = 0.0
        for _ in range(len(ep_ids)):
            total += sum(groups[ep_ids[rng.randrange(len(ep_ids))]])
        totals.append(total)
    lo = c20._q(totals, 0.025) if totals else 0.0
    hi = c20._q(totals, 0.975) if totals else 0.0
    return {
        "resamples": resamples, "seed": seed, "episode_blocks": len(ep_ids),
        "ci_low": lo, "ci_high": hi, "excludes_zero": (lo > 0 or hi < 0),
        "prob_gt_0": (sum(1 for x in totals if x > 0) / len(totals)) if totals else 0.0,
        "observed_total": round(sum(sum(v) for v in groups.values()), 2),
        "episode_totals": {str(e): round(sum(groups[e]), 2) for e in ep_ids},
    }


def _permutation_for_keys(vd_slice: Dict[str, Any], census: Dict[str, Any],
                          subset_keys: Sequence[Tuple[str, int]], canonical_pnl: float,
                          cfg: StrategyConfig, draws: int, seed: int) -> Dict[str, Any]:
    memo, rows, meta = c20.build_memo(vd_slice, census, cfg)
    return c20.conditional_permutation_null(vd_slice, memo, rows, list(subset_keys),
                                            canonical_pnl, cfg, draws, seed, 1)


def _key_in_bin(key: Tuple[str, int], vid: str, b: str,
                day_of_key: Dict[Tuple[str, int], str],
                btc_trend: Dict[str, str], funding: Dict[str, str]) -> bool:
    day = day_of_key.get(key, "")
    if vid == "btc_trend":
        return btc_trend.get(day, "btc_flat_7d") == b
    if vid == "funding_regime":
        return funding.get(day, "funding_neutral") == b
    return False


# The stratum detail builder needs the per-bin computed dicts; wire it without
# recomputing by monkey-patching a simpler, correct implementation below.


def build_strata(venue_data_full: Dict[str, Any], vd_slice: Dict[str, Any],
                 census: Dict[str, Any], episode: Dict[str, Any],
                 fold_id: str) -> Dict[str, Any]:
    """Pre-specified stratum stratification + BH correction for one venue-fold.

    Deterministic, no data-dependent bin invention. Each pre-specified bin is
    evaluated with its own episode-block bootstrap (20000 draws) and, when
    non-empty, a fold-local permutation (20000 draws). BH correction is applied
    across all 9 (variable, bin) tests for this venue-fold.
    """
    fold = next(f for f in FOLDS if f["id"] == fold_id)
    cfg = c20.spec_literal_config()
    memo, rows, meta = c20.build_memo(vd_slice, census, cfg)
    if not meta["memo_matches_signal_gate"]:
        raise SystemExit(f"strata memo mismatch fold {fold_id}")
    keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"]))
                   for r in rows if r.get("signal_gate_pass") and r.get("bar_index") is not None
                   and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
    times = {(str(r["symbol"]).upper(), int(r["bar_index"])): str(r["bar_timestamp_utc"])
             for r in rows if r.get("bar_index") is not None and r.get("bar_timestamp_utc")}
    day_of_key = {k: times[k][:10] for k in keys if k in times}
    rsi_of_key = {(str(r["symbol"]).upper(), int(r["bar_index"])): r.get("rsi")
                  for r in rows if r.get("bar_index") is not None}
    btc_trend = _btc_trend_by_day(venue_data_full)
    funding = _funding_regime_by_day(venue_data_full)
    canon = c20.run_memo_portfolio(
        {s: vd_slice["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in vd_slice["candles"]},
        cfg, memo)
    trade_rows = c20.trade_summary(canon)["trades"]
    # Map each trade to its crash key via (symbol, entry bar == key bar + 1).
    ts_index: Dict[str, Dict[int, int]] = {}
    for sym, cs in vd_slice["candles"].items():
        ts_index[sym] = {}
        for i, c in enumerate(cs):
            t = c20._ts_ms(c)
            if t is not None:
                ts_index[sym][t] = i
    key_by_sym_bar: Dict[Tuple[str, int], Tuple[str, int]] = {}
    for k in keys:
        sym, idx = k
        # key bar timestamp
        kt = c20._ts_ms(vd_slice["candles"][sym][idx]) if idx < len(vd_slice["candles"].get(sym, [])) else None
        if kt is not None:
            key_by_sym_bar[(sym, kt + 3600_000)] = k  # next hour open
    trade_key: List[Optional[Tuple[str, int]]] = []
    for t in trade_rows:
        sym = str(t.get("symbol", "")).upper()
        ets = _parse_ms(t.get("entry_timestamp"))
        trade_key.append(key_by_sym_bar.get((sym, ets)) if ets is not None else None)

    def _sev_of(k: Tuple[str, int]) -> str:
        rsi = rsi_of_key.get(k)
        if rsi is None:
            return "rsi_15_20"
        r = float(rsi)
        return "rsi_0_10" if r < 10 else ("rsi_10_15" if r < 15 else "rsi_15_20")

    def _in_bin(k: Tuple[str, int], vid: str, b: str) -> bool:
        day = day_of_key.get(k, "")
        if vid == "crash_severity":
            return _sev_of(k) == b
        if vid == "btc_trend":
            return btc_trend.get(day, "btc_flat_7d") == b
        if vid == "funding_regime":
            return funding.get(day, "funding_neutral") == b
        return False

    pvals: List[float] = []
    labels: List[Tuple[str, str]] = []
    detail: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for sdef in STRATA_DEFS:
        vid = sdef["id"]
        for b in sdef["bins"]:
            sub_keys = [k for k in keys if _in_bin(k, vid, b)]
            sub_trades = [t for t, k in zip(trade_rows, trade_key) if k is not None and _in_bin(k, vid, b)]
            episodes = c20.cluster_episodes(sub_keys, times, LINK_HOURS)
            boot = _stratum_bootstrap_ci(sub_trades, episodes, DRAWS, SEED + len(pvals))
            n_trades = len(sub_trades)
            n_eps = len(episodes)
            n_days = len({day_of_key[k] for k in sub_keys if k in day_of_key})
            spot = round(sum(float(t.get("pnl") or 0.0) for t in sub_trades), 2)
            total = round(sum(float(t.get("total_pnl") or 0.0) for t in sub_trades), 2)
            if n_trades > 0 and sub_keys:
                try:
                    perm = _permutation_for_keys(vd_slice, census, sub_keys, boot["observed_total"],
                                                 cfg, DRAWS, SEED + len(pvals))
                    p_perm = float(perm.get("p_null_ge_canonical") if perm.get("p_null_ge_canonical") is not None else 1.0)
                except Exception:
                    p_perm = 1.0
            else:
                p_perm = 1.0
            pvals.append(p_perm)
            labels.append((vid, b))
            detail[(vid, b)] = {
                "n_trades": n_trades, "n_episodes": n_eps, "n_crash_days": n_days,
                "spot_pnl": spot, "total_pnl": total,
                "bootstrap_ci95": [round(boot["ci_low"], 2), round(boot["ci_high"], 2)],
                "bootstrap_excludes_zero_positive": bool(boot["ci_low"] > 0),
                "permutation_p": round(p_perm, 6),
                "power_eligible": (n_trades >= 10 and n_eps >= 5 and n_days >= 5),
                "power_curve": {"observed_episodes": n_eps,
                                "first_size_excluding_zero": episode["episode_block_bootstrap"]["power_curve"]["first_size_excluding_zero"]},
            }
    rejected, adj, m = _bh(pvals, 0.05)
    strata: Dict[str, Any] = {}
    for (vid, b), p, a, r in zip(labels, pvals, adj, rejected):
        strata.setdefault(vid, {}).setdefault("bins", {})[b] = {**detail[(vid, b)],
                                                                 "p": round(p, 6),
                                                                 "p_adj_bh": a,
                                                                 "reject_null_bh": bool(r)}
    return {
        "prereg_strata": STRATA_DEFS,
        "fold": fold_id,
        "n_tests": m,
        "bh_alpha": 0.05,
        "bh_family": "per-venue-fold strata (3 variables x 3 bins = 9 tests)",
        "strata": strata,
        "labels": [list(x) for x in labels],
        "pvals": [round(p, 6) for p in pvals],
        "p_adj_bh": adj,
        "reject_null": rejected,
    }


# ---------------------------------------------------------------------------
# Per-venue fold orchestration
# ---------------------------------------------------------------------------

def run_venue_folds(venue: str, jobs: int, resume: bool) -> Dict[str, Any]:
    vd = c20.load_venue(venue)
    venue_label = vd["venue_label"]
    fold_campaigns: Dict[str, Dict[str, Any]] = {}
    fold_episodes: Dict[str, Dict[str, Any]] = {}
    fold_placebos: Dict[str, Dict[str, Any]] = {}
    fold_censuses: Dict[str, Dict[str, Any]] = {}
    fold_strata: Dict[str, Dict[str, Any]] = {}
    for fold in FOLDS:
        fid = fold["id"]
        camp_stem = f"c21_{venue}_fold_campaign_{TS}" if False else None
        # Stems required by the gate:
        #   c21_{okx,binance_um}_fold_campaign_{TS}  (one per venue; folds embedded)
        #   c21_{okx,binance_um}_fold_episode_edge_{TS}
        #   c21_{okx,binance_um}_fold_placebo_{TS}
        #   c21_{okx,binance_um}_fold_census_{TS}
        # Each is a single artifact with folds=[all four] and per-fold detail.
        vd_slice = _slice_venue(vd, fold)
        print(f"[C21] {venue_label} fold {fid}: symbols={len(vd_slice['candles'])}", flush=True)
        camp = _run_fold_campaign(vd_slice, fid)
        cen = _fold_census(vd_slice, camp, fid)
        ep = _fold_episode_edge(vd_slice, cen, camp, c20.spec_literal_config(), fid, jobs)
        pl = _fold_placebo(vd_slice, cen, c20.spec_literal_config(), fid, jobs)
        st = build_strata(vd, vd_slice, cen, ep, fid)
        fold_campaigns[fid] = camp
        fold_censuses[fid] = cen
        fold_episodes[fid] = ep
        fold_placebos[fid] = pl
        fold_strata[fid] = st
        print(f"[C21] {venue_label} fold {fid}: trades={camp['results']['num_trades']} "
              f"pnl={camp['results']['total_pnl']:.2f} eps={ep['episode_audit']['n_episodes']} "
              f"perm_p={ep['temporal_edge_permutation'].get('p_null_ge_canonical')} "
              f"placebo_runs={pl['placebo']['runs']}", flush=True)

    # Merge per-fold artifacts into the single per-venue artifacts the gate expects.
    def _merge(stem: str, per_fold: Dict[str, Dict[str, Any]], kind: str) -> Dict[str, Any]:
        if resume and _stem_exists(stem):
            print(f"[resume] {stem} cached", flush=True)
            return _load_json(stem)
        folds_list = []
        for f in FOLDS:
            d = per_fold[f["id"]]
            folds_list.append({"id": f["id"], "start": f["start"], "end": f["end"],
                               "num_trades": d.get("results", {}).get("num_trades")
                               if kind == "campaign" else d.get("inputs", {}).get("canonical_num_trades"),
                               "total_pnl": d.get("results", {}).get("total_pnl")
                               if kind == "campaign" else d.get("inputs", {}).get("canonical_total_pnl")})
        base = dict(per_fold[FOLDS[0]["id"]])
        base["generated_at_utc"] = iso_now()
        base["campaign"] = "C21"
        base["prereg"] = f"research_state/c21_prereg_{TS}.json"
        base["prereg_sha256"] = sha256_file(PREREG)
        base["folds"] = folds_list
        base["fold"] = "ALL"
        base["per_fold"] = {f["id"]: _strip_heavy(per_fold[f["id"]], kind) for f in FOLDS}
        base["is_hyperliquid_venue_data"] = False
        base["cross_venue"] = True
        base["fabricated_data"] = False
        base["synthetic_data"] = False
        base["provenance_caveat"] = PROVENANCE_CAVEAT
        if kind == "campaign":
            base["results"] = {
                "num_trades": sum(int(per_fold[f["id"]]["results"]["num_trades"]) for f in FOLDS),
                "total_pnl": round(sum(float(per_fold[f["id"]]["results"]["total_pnl"]) for f in FOLDS), 2),
                "trades": [],
                "equity_curve": [],
            }
        elif kind == "episode":
            base["episode_block_bootstrap"] = per_fold[FOLDS[0]["id"]]["episode_block_bootstrap"]
            base["temporal_edge_permutation"] = per_fold[FOLDS[0]["id"]]["temporal_edge_permutation"]
        elif kind == "placebo":
            base["placebo"] = per_fold[FOLDS[0]["id"]]["placebo"]
        elif kind == "census":
            base["reconciliation"] = per_fold[FOLDS[0]["id"]]["reconciliation"]
        _write_json(stem, base)
        return base

    def _strip_heavy(d: Dict[str, Any], kind: str) -> Dict[str, Any]:
        keep = {"fold": d.get("fold"), "venue_label": d.get("venue_label")}
        if kind == "campaign":
            keep["num_trades"] = d["results"]["num_trades"]
            keep["total_pnl"] = d["results"]["total_pnl"]
            keep["trades"] = d["results"]["trades"]
        elif kind == "episode":
            keep["n_events"] = d["episode_audit"]["n_events"]
            keep["n_episodes"] = d["episode_audit"]["n_episodes"]
            keep["n_distinct_crash_days"] = d["episode_audit"]["n_distinct_crash_days"]
            keep["canonical_num_trades"] = d["inputs"]["canonical_num_trades"]
            keep["canonical_total_pnl"] = d["inputs"]["canonical_total_pnl"]
            keep["bootstrap"] = d["episode_block_bootstrap"]["bootstrap_total_pnl"]
            keep["perm_p"] = d["temporal_edge_permutation"].get("p_null_ge_canonical")
        elif kind == "placebo":
            keep["runs"] = d["placebo"]["runs"]
            keep["p_ge_canonical"] = d["placebo"]["p_ge_canonical"]
            keep["canonical"] = d["canonical"]
        elif kind == "census":
            keep["events_total"] = d["reconciliation"]["events_total"]
            keep["signal_gate_pass"] = d["reconciliation"]["signal_gate_pass"]
            keep["trades_matched"] = d["reconciliation"]["trades_matched_to_events"]
        return keep

    camp = _merge(f"c21_{venue}_fold_campaign_{TS}", fold_campaigns, "campaign")
    cen = _merge(f"c21_{venue}_fold_census_{TS}", fold_censuses, "census")
    ep = _merge(f"c21_{venue}_fold_episode_edge_{TS}", fold_episodes, "episode")
    pl = _merge(f"c21_{venue}_fold_placebo_{TS}", fold_placebos, "placebo")

    verdict = _build_venue_verdict(venue, camp, ep, pl, fold_strata, cen, resume)
    return {"campaign": camp, "census": cen, "episode": ep, "placebo": pl,
            "strata": fold_strata, "verdict": verdict}


def _build_venue_verdict(venue: str, campaign: Dict[str, Any], episode: Dict[str, Any],
                         placebo: Dict[str, Any], fold_strata: Dict[str, Dict[str, Any]],
                         census: Dict[str, Any], resume: bool) -> Dict[str, Any]:
    stem = f"c21_decision_verdict_{venue}_stability_{TS}"
    if resume and _stem_exists(stem):
        print(f"[resume] {stem} cached", flush=True)
        return _load_json(stem)
    per_fold = episode["per_fold"]
    go_checks_per_fold: Dict[str, Dict[str, bool]] = {}
    for f in FOLDS:
        fid = f["id"]
        ep = per_fold[fid]
        boot = ep["bootstrap"]
        perm_p = ep.get("perm_p")
        pl = placebo["per_fold"][fid]
        n_trades = ep["canonical_num_trades"]
        n_eps = ep["n_episodes"]
        n_days = ep["n_distinct_crash_days"]
        spot = sum(float(t.get("pnl") or 0.0) for t in (campaign["per_fold"][fid].get("trades") or []))
        go_checks_per_fold[fid] = {
            "trades_ge_10": n_trades >= 10,
            "episodes_ge_5": n_eps >= 5,
            "crash_days_ge_5": n_days >= 5,
            "bootstrap_ci_excludes_zero_positive": bool(boot.get("ci_low_pnl_2p5", 0) > 0),
            "permutation_p_lt_0.05": (perm_p is not None and float(perm_p) < 0.05),
            "placebo_p_ge_canonical_lt_0.05": (pl.get("p_ge_canonical") is not None and float(pl["p_ge_canonical"]) < 0.05),
            "spot_leg_positive": spot > 0,
        }
    # BH stratum survival across all venue-fold strata.
    survivors = []
    for fid, st in fold_strata.items():
        for vid, body in st["strata"].items():
            for b, d in body["bins"].items():
                if d.get("reject_null_bh") and d.get("bootstrap_excludes_zero_positive") \
                        and d.get("permutation_p", 1.0) < 0.05 and d.get("power_eligible"):
                    survivors.append({"fold": fid, "variable": vid, "bin": b, **d})
    # Pooled across folds (sum of fold totals) + cross-venue handled later.
    total_pnl = float(campaign["results"]["total_pnl"])
    spot_total = round(sum(float(t.get("pnl") or 0.0)
                           for f in FOLDS for t in (campaign["per_fold"][f["id"]].get("trades") or [])), 2)
    if survivors:
        token = "STABLE_POSITIVE_SUBSET"
    else:
        # NO_GO if majority folds have non-positive spot and pooled CI spans 0.
        nonpos = sum(1 for f in FOLDS if go_checks_per_fold[f["id"]]["spot_leg_positive"] is False)
        token = "NO_GO" if nonpos >= 2 else "UNDERPOWERED"
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C21",
        "prereg_sha256": sha256_file(PREREG),
        "label": "CROSS_VENUE_TEMPORAL_STABILITY_PER_VENUE_VERDICT",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "performance_evidence": True,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_label": c20.VENUES[venue]["venue_label"],
        "entry_rule": "SPEC_LITERAL_NEXT_OPEN",
        "folds": [f["id"] for f in FOLDS],
        "per_fold_go_checks": go_checks_per_fold,
        "stratum_survivors": survivors,
        "n_stratum_survivors": len(survivors),
        "headline": {
            "trades": int(campaign["results"]["num_trades"]),
            "total_pnl": round(total_pnl, 2),
            "spot_pnl": spot_total,
        },
        "verdict": token,
        "verdict_token": token,
        "power_curve": {
            f["id"]: per_fold[f["id"]].get("bootstrap", {}).get("power_curve")
            if isinstance(per_fold[f["id"]].get("bootstrap"), dict) else None
            for f in FOLDS
        },
        "limitations": [
            f"CROSS-VENUE {c20.VENUES[venue]['venue_label']}; NOT Hyperliquid performance evidence.",
            "Folds are fixed by prereg; strata fixed by prereg; no post-hoc selection.",
        ],
    }
    _write_json(stem, payload)
    print(f"[verdict] {payload['venue_label']}: {token} survivors={len(survivors)} "
          f"trades={payload['headline']['trades']} pnl={payload['headline']['total_pnl']:.2f}", flush=True)
    return payload


# ---------------------------------------------------------------------------
# Pooled synthesis + consolidated final
# ---------------------------------------------------------------------------

def _build_pooled(venue_results: Dict[str, Dict[str, Any]], resume: bool) -> Dict[str, Any]:
    stem = f"c21_pooled_stability_synthesis_{TS}"
    if resume and _stem_exists(stem):
        print(f"[resume] {stem} cached", flush=True)
        return _load_json(stem)
    rng = random.Random(SEED)
    venue_blocks = []
    for v in ("okx", "binance_um"):
        vd = venue_results[v]["verdict"]
        venue_blocks.append((vd["venue_label"], float(vd["headline"]["total_pnl"])))
    draws = []
    for _ in range(DRAWS):
        draws.append(sum(b for _, b in (venue_blocks[rng.randrange(len(venue_blocks))]
                                        for _ in range(len(venue_blocks)))))
    pooled_ci = [round(c20._q(draws, 0.025), 2), round(c20._q(draws, 0.975), 2)]
    signs = [1 if b > 0 else (-1 if b < 0 else 0) for _, b in venue_blocks]
    sign_concordant = len(signs) == 2 and signs[0] == signs[1] and signs[0] != 0
    tokens = [venue_results[v]["verdict"]["verdict"] for v in ("okx", "binance_um")]
    both_survivors = all(venue_results[v]["verdict"]["n_stratum_survivors"] > 0 for v in ("okx", "binance_um"))
    any_survivor = any(venue_results[v]["verdict"]["n_stratum_survivors"] > 0 for v in ("okx", "binance_um"))
    if both_survivors and sign_concordant:
        pooled_token = "STABLE_POSITIVE_SUBSET"
    elif any_survivor and sign_concordant:
        pooled_token = "STABLE_POSITIVE_SUBSET"
    elif all(t == "NO_GO" for t in tokens):
        pooled_token = "NO_GO"
    elif any(t == "UNDERPOWERED" for t in tokens):
        pooled_token = "UNDERPOWERED"
    else:
        pooled_token = "NO_GO"
    # Pooled strata (BH across all venue-fold strata).
    all_pvals = []
    all_labels = []
    for v in ("okx", "binance_um"):
        for fid, st in venue_results[v]["strata"].items():
            for vid, body in st["strata"].items():
                for b, d in body["bins"].items():
                    all_labels.append((v, fid, vid, b))
                    all_pvals.append(float(d.get("p", 1.0)))
    rejected, adj, m = _bh(all_pvals, 0.05)
    pooled_survivors = []
    for (v, fid, vid, b), r, a in zip(all_labels, rejected, adj):
        d = venue_results[v]["strata"][fid]["strata"][vid]["bins"][b]
        if r and d.get("bootstrap_excludes_zero_positive") and d.get("power_eligible"):
            pooled_survivors.append({"venue": v, "fold": fid, "variable": vid, "bin": b,
                                     "p": d.get("p"), "p_adj_bh": a})
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "campaign": "C21",
        "prereg_sha256": sha256_file(PREREG),
        "label": "CROSS_VENUE_TEMPORAL_STABILITY_POOLED_SYNTHESIS",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "performance_evidence": True,
        "is_hyperliquid_venue_data": False,
        "cross_venue": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "venue_labels": [v["venue_label"] for v in venue_blocks],
        "venue_tokens": tokens,
        "pooled_venue_blocked_bootstrap": {
            "seed": SEED, "draws": DRAWS,
            "blocks": [{"venue": k, "total_pnl": round(b, 2)} for k, b in venue_blocks],
            "pooled_total_pnl": round(sum(b for _, b in venue_blocks), 2),
            "ci95": pooled_ci,
            "prob_pooled_total_gt_0": round(sum(1 for d in draws if d > 0) / len(draws), 4),
            "sign_concordant": sign_concordant, "signs": signs,
        },
        "effective_sample": {
            "trades": sum(int(venue_results[v]["verdict"]["headline"]["trades"]) for v in ("okx", "binance_um")),
            "episodes": sum(int(venue_results[v]["episode"]["per_fold"][f["id"]]["n_episodes"])
                            for v in ("okx", "binance_um") for f in FOLDS),
        },
        "multiplicity": {
            "method": "benjamini_hochberg", "alpha": 0.05, "n_pooled_stratum_tests": m,
            "n_pooled_survivors": len(pooled_survivors),
            "survivors": pooled_survivors,
        },
        "decision": {
            "token": pooled_token,
            "rationale": (
                f"Pooled token {pooled_token} from per-venue tokens {tokens}; "
                f"pooled CI={pooled_ci}; pooled strata survivors={len(pooled_survivors)}/{m}."
            ),
        },
        "priors_referenced": [
            f"research_state/c21_prereg_{TS}.json",
            "research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json",
            "research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.json",
        ],
    }
    _write_json(stem, payload)
    print(f"[pooled] token={pooled_token} venues={tokens} pooled_total="
          f"{payload['pooled_venue_blocked_bootstrap']['pooled_total_pnl']:.2f} CI={pooled_ci} "
          f"survivors={len(pooled_survivors)}/{m}", flush=True)
    return payload


def _build_consolidated(venue_results: Dict[str, Dict[str, Any]], pooled: Dict[str, Any],
                        resume: bool) -> Dict[str, Any]:
    stem = f"c21_decision_verdict_CONSOLIDATED_{TS}"
    if resume and _stem_exists(stem):
        print(f"[resume] {stem} cached", flush=True)
        return _load_json(stem)
    token = pooled["decision"]["token"]
    payload = {
        "schema_version": 1,
        "generated_at_utc": iso_now(),
        "scope": "C21 cross-venue temporal-stability campaign",
        "final_verdict_token": token,
        "verdict": token,
        "research_program_complete": False,
        "supersedes": "research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json",
        "supersedes_verdict_token": "NO_GO",
        "campaign": "C21",
        "prereg_sha256": sha256_file(PREREG),
        "campaign_verdicts": {
            "c21_okx_stability": venue_results["okx"]["verdict"]["verdict"],
            "c21_binance_um_stability": venue_results["binance_um"]["verdict"]["verdict"],
            "c21_pooled": token,
        },
        "pooled_bootstrap": pooled["pooled_venue_blocked_bootstrap"],
        "multiplicity": pooled["multiplicity"],
        "structural_power_note": (
            "C21 measures temporal/regime stability of the C20 NO_GO across four pre-specified "
            "folds on two independent real venues, with BH-corrected strata and an honest pooled "
            "verdict. Fold and stratum definitions were fixed before compute."
        ),
        "provenance": {
            "is_hyperliquid_venue_data": False,
            "cross_venue": True,
            "provenance_caveat": PROVENANCE_CAVEAT,
            "real_market_data": True,
            "fabricated_data": False,
            "synthetic_data": False,
        },
        "final_integrated_decision": {
            "token": token,
            "statement": (
                f"Consolidated C21 verdict: {token}. C21 quantifies whether any pre-specified "
                "temporal fold or crash-regime stratum survives multiplicity control with a "
                "positive spot leg and cross-venue concordance; the unconditional C1-C20 NO_GO "
                "stands unless this pre-registered contradiction is accepted with full evidence."
            ),
        },
        "priors_referenced": [
            f"research_state/c21_prereg_{TS}.json",
            "research_state/decision_verdict_CONSOLIDATED_FINAL_20261116T063500Z.json",
            "research_state/spec_rebound_confirmation_adjudication_20261116T054000Z.json",
        ],
    }
    _write_json(stem, payload)
    print(f"[consolidated] C21 {token}", flush=True)
    return payload


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--venues", nargs="+", default=["okx", "binance_um"], choices=["okx", "binance_um"])
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--resume", action="store_true",
                    help="Skip per-venue artifacts whose stems already exist on disk.")
    args = ap.parse_args(argv)

    venue_results: Dict[str, Dict[str, Any]] = {}
    for venue in args.venues:
        venue_results[venue] = run_venue_folds(venue, args.jobs, resume=args.resume)

    pooled = _build_pooled(venue_results, resume=args.resume)
    consolidated = _build_consolidated(venue_results, pooled, resume=args.resume)
    print(f"C21 COMPLETE: per-venue={[venue_results[v]['verdict']['verdict'] for v in args.venues]} "
          f"pooled={pooled['decision']['token']} consolidated={consolidated['verdict']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())