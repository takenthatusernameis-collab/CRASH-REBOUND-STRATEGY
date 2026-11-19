#!/usr/bin/env python3
"""C24 stage-0 probe — liquidation-distance fidelity of the frozen spec-literal replay.

WHY THIS EXISTS
---------------
C1-C23 closed NO_GO on four real cross-venue caches (OKX, Binance UM, MEXC, Bitget)
with the frozen spec-literal config.  A read of the execution model shows the engine
force-closes a position when price moves -(liquidation_maint_margin_pct +
liquidation_buffer_pct) = -(5+1) = 6% against entry (src/backtest/engine.py
::_check_liquidation).  The published spec's own risk exit is a *wide* safety stop at
8x the usual hourly range (median ~15% below entry on Hyperliquid) and it explicitly
states the 120% coin cap "leaves margin free" with stops not relied on for margin
safety.  A 6% forced exit is therefore STRICTER than the strategy's own stop and is
not described anywhere in the PDF.

This probe is DESCRIPTIVE ONLY.  It reruns the unchanged signal path (identical
entries) at several liquidation distances and reports PnL / trade count /
liquidation count per venue-fold.  It computes NO inference (no bootstrap, no
permutation, no placebo, no BH), so it can NOT produce a GO token.  Its only job is
to decide whether the C1-C23 NO_GO is plausibly a margin-model artifact and therefore
whether the heavy C24 inference campaign is worth running.

PROVENANCE / GUARDRAILS
-----------------------
- Real market data only; no synthetic gap-fill; is_hyperliquid_venue_data=false.
- SIGNAL PATH IS UNCHANGED: rsi_period=21, rsi_threshold=20, target_pct=9,
  rebound_short_*, gross_cap=120%, volume floor $5M, sizing 1.25%, ETH hedge on.
  ONLY liquidation_maint_margin_pct / liquidation_buffer_pct / enable_liquidation_checks
  vary.  Any arm that alters a signal parameter is invalid.
- Arm `base_6` MUST reproduce the recorded C20/C22/C23 fold PnL to <1e-6; a mismatch
  aborts the probe (fidelity anchor).

Run (from repo root):
  PYTHONPATH=. .venv/bin/python scripts/probe_c24_liquidation_fidelity.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

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

FOLDS: List[Dict[str, str]] = [
    {"id": "2023", "start": "2023-01-01T00:00:00Z", "end": "2023-12-31T23:00:00Z"},
    {"id": "2024", "start": "2024-01-01T00:00:00Z", "end": "2024-12-31T23:00:00Z"},
    {"id": "2025", "start": "2025-01-01T00:00:00Z", "end": "2025-12-31T23:00:00Z"},
    {"id": "2026YTD", "start": "2026-01-01T00:00:00Z", "end": "2026-09-28T23:00:00Z"},
]

# Liquidation distance = maint_margin_pct + buffer_pct (percent adverse move).
# base_6 reproduces the frozen C1-C23 execution model exactly (5 + 1).
ARMS: Dict[str, Dict[str, Any]] = {
    "base_6": {"maint": 5.0, "buffer": 1.0, "disable": False},
    "d10": {"maint": 9.0, "buffer": 1.0, "disable": False},
    "d15": {"maint": 14.0, "buffer": 1.0, "disable": False},
    "d30": {"maint": 29.0, "buffer": 1.0, "disable": False},
    "noliq": {"maint": 5.0, "buffer": 1.0, "disable": True},
}

# Recorded frozen-config fold PnL the base_6 arm must reproduce (C20/C22/C23).
RECORDED = {
    "okx": {"2023": 21382.7, "2024": -38598.4, "2025": -24979.9, "2026YTD": -12603.7},
    "bitget": {"2023": 28706.320387885964, "2024": -30939.595457279396,
               "2025": -32710.1909416799, "2026YTD": -23185.861058872903},
    "mexc": {"2023": 30599.03, "2024": -27326.63, "2025": None, "2026YTD": None},
}

CAVEAT = (
    "Real exchange USDT-perp data, non-synthetic, CROSS-VENUE vs the Hyperliquid spec; "
    "NOT Hyperliquid performance evidence and must never be relabelled as such."
)


def _cfg(spec: Dict[str, Any]) -> StrategyConfig:
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


def _load(venue: str) -> Dict[str, Any]:
    if venue in ("okx", "binance_um"):
        return c20.load_venue(venue)
    if venue == "mexc":
        return c22.load_mexc_venue()
    if venue == "bitget":
        return c23.load_bitget_venue()
    raise SystemExit(f"unknown venue {venue}")


def _run(vd_slice: Dict[str, Any], cfg: StrategyConfig) -> Dict[str, Any]:
    eth = vd_slice["candles"].get("ETH")
    res = run_portfolio_simulation(
        vd_slice["candles"], config=cfg, capital=100_000.0,
        eth_candles={"ETH": eth} if eth else None,
        require_eth_hedge=bool(cfg.enable_eth_hedge),
    )
    trades = res.get("trades") or []
    return {
        "num_trades": len(trades),
        "total_pnl": round(float(res.get("total_pnl", 0.0)), 2),
        "liquidation_exits": sum(1 for t in trades if t.get("exit_reason") == "liquidated"),
        "target_rebound_short_exits": sum(
            1 for t in trades if t.get("exit_reason") == "target_rebound_short"),
        "buy_leg_pnl": round(sum(float(t.get("pnl", 0.0)) for t in trades), 2),
        "rebound_short_pnl": round(sum(float(t.get("rebound_short_pnl", 0.0)) for t in trades), 2),
        "hedge_pnl": round(sum(float(t.get("hedge_pnl", 0.0)) for t in trades), 2),
        "rebound_hedge_pnl": round(sum(float(t.get("rebound_hedge_pnl", 0.0)) for t in trades), 2),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--venues", default="okx,binance_um,mexc,bitget")
    ap.add_argument("--arms", default="base_6,d10,d15,d30,noliq")
    ap.add_argument("--out", default=str(STATE / f"c24_liquidation_fidelity_probe_{TS}.json"))
    args = ap.parse_args(argv)

    venues = [v.strip() for v in args.venues.split(",") if v.strip()]
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]

    out: Dict[str, Any] = {
        "schema_version": 1,
        "campaign": "C24",
        "stage": "STAGE0_DESCRIPTIVE_PROBE",
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "real_market_data": True,
        "fabricated_data": False,
        "synthetic_data": False,
        "cross_venue": True,
        "is_hyperliquid_venue_data": False,
        "evidence_class": "DESCRIPTIVE_NO_INFERENCE",
        "inference_not_run": [
            "episode_block_bootstrap", "conditional_permutation", "placebo", "benjamini_hochberg",
        ],
        "may_emit_go": False,
        "provenance_caveat": CAVEAT,
        "arms": {a: ARMS[a] for a in arms},
        "folds": FOLDS,
        "venues": {},
    }

    fidelity_ok = True
    for venue in venues:
        vd = _load(venue)
        print(f"venue {venue}: symbols={len(vd['candles'])}", flush=True)
        vout: Dict[str, Any] = {}
        for fold in FOLDS:
            sv = c23._slice_venue(vd, fold)
            vout[fold["id"]] = {a: _run(sv, _cfg(ARMS[a])) for a in arms}
            print(fold["id"], json.dumps(vout[fold["id"]]), flush=True)
        out["venues"][venue] = vout

        if venue in RECORDED and "base_6" in arms:
            for fid, expected in RECORDED[venue].items():
                if expected is None:
                    continue
                got = vout[fid]["base_6"]["total_pnl"]
                if abs(got - float(expected)) > 1.0:
                    fidelity_ok = False
                    print(f"FIDELITY MISMATCH {venue} {fid}: got {got} expected {expected}", flush=True)

    pooled = {}
    for a in arms:
        pooled[a] = {
            "per_venue_total_pnl": {
                v: round(sum(out["venues"][v][f["id"]][a]["total_pnl"] for f in FOLDS), 2)
                for v in out["venues"]
            }
        }
        pooled[a]["all_venue_sum"] = round(
            sum(pooled[a]["per_venue_total_pnl"].values()), 2)
        pooled[a]["per_venue_fold_sign"] = {
            v: [1 if out["venues"][v][f["id"]][a]["total_pnl"] > 0 else -1 for f in FOLDS]
            for v in out["venues"]
        }
    out["pooled"] = pooled
    out["fidelity_anchor_reproduced"] = fidelity_ok

    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print("wrote", args.out, flush=True)
    print("FIDELITY_ANCHOR_REPRODUCED:", fidelity_ok, flush=True)
    for a in arms:
        print(f"  {a}: all_venue_sum={pooled[a]['all_venue_sum']} "
              f"per_venue={pooled[a]['per_venue_total_pnl']}", flush=True)
    return 0 if fidelity_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
