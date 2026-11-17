#!/usr/bin/env python3
"""Benchmark the C21 pipeline stages in a scratch output dir (no overwrite of real artifacts)."""
import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import scripts.run_c20_cross_venue_campaign as c20

OUT = Path(tempfile.mkdtemp(prefix="c21bench_"))
print("OUT:", OUT, flush=True)

# Point the module at the scratch output dir for writes, keep REPO for reads.
c20.REPO = REPO
c20._OUT_DIR = OUT  # type: ignore[attr-defined]

# Monkeypatch the artifact-writing helpers to write under OUT/research_state.
orig_write_text = Path.write_text


def patched_write_text(self, content, encoding=None):
    if str(self).startswith(str(REPO)):
        rel = Path(self).relative_to(REPO)
        target = OUT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        return orig_write_text(target, content, encoding=encoding)
    return orig_write_text(self, content, encoding=encoding)


Path.write_text = patched_write_text  # type: ignore[assignment]

vd = c20.load_venue("okx")
cfg = c20.spec_literal_config()

t0 = time.time()
campaign = c20.run_campaign(vd, "tmp_c21_bench")
print("campaign wall", round(time.time() - t0, 1), flush=True)

t0 = time.time()
census = c20.build_census(vd, campaign, "tmp_c21_bench_census")
print("census wall", round(time.time() - t0, 1), flush=True)

t0 = time.time()
memo, rows, meta = c20.build_memo(vd, census, cfg)
print("memo wall", round(time.time() - t0, 1), "memo_signals", meta["memo_signals"], flush=True)

keys = sorted({(str(r["symbol"]).upper(), int(r["bar_index"])) for r in rows
               if r.get("signal_gate_pass") and r.get("bar_index") is not None
               and (str(r["symbol"]).upper(), int(r["bar_index"])) in memo})
print("keys", len(keys), flush=True)

candles_active = {s: vd["candles"][s] for s in sorted({k[0] for k in memo} | {"ETH"}) if s in vd["candles"]}
t0 = time.time()
res = c20.run_memo_portfolio(candles_active, cfg, memo)
print("memo replay wall", round(time.time() - t0, 1), "trades", res.get("num_trades"), "pnl", res.get("total_pnl"), flush=True)

# Episode clustering + bootstrap timing
t0 = time.time()
episodes = c20.cluster_episodes(keys, {(str(r["symbol"]).upper(), int(r["bar_index"])): str(r["bar_timestamp_utc"]) for r in rows
                                        if r.get("bar_index") is not None and r.get("bar_timestamp_utc")}, 98.0)
print("cluster wall", round(time.time() - t0, 1), "episodes", len(episodes), flush=True)

ts = c20.trade_summary(res)
t0 = time.time()
boot = c20.episode_block_bootstrap(ts["trades"], episodes, 20000, 20261121)
print("bootstrap 20k wall", round(time.time() - t0, 1), flush=True)

# Permutation timing (1 draw)
t0 = time.time()
perm1 = c20.conditional_permutation_null(vd, memo, rows, keys, res.get("total_pnl", 0.0), cfg, 1, 20261121, 1)
print("perm 1 draw wall", round(time.time() - t0, 1), "p=", perm1["p_null_ge_canonical"], flush=True)

# Placebo timing (1 run)
t0 = time.time()
pl1 = c20.run_placebo(vd, census, campaign, cfg, "tmp_pl1", 1)
print("placebo 1 run wall", round(time.time() - t0, 1), flush=True)