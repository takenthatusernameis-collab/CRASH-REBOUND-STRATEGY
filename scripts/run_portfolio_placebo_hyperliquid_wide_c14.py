#!/usr/bin/env python3
"""C14 config-matched full-portfolio placebo for wide Hyperliquid-native run."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math, random, statistics, sys, time
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance  # noqa: E402
from src.strategy.config import StrategyConfig  # noqa: E402
from src.strategy.crash_rebound import generate_signal as real_generate_signal  # noqa: E402
import scripts.run_portfolio as portfolio_mod  # noqa: E402


def iso_now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path: Path):
    data = json.loads(path.read_text())
    if isinstance(data, dict):
        data = data.get('candles', data)
    return data


def parse_ts_ms(v):
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return int(v)
    s = str(v).strip()
    if not s:
        return None
    if s.lstrip('-').isdigit():
        try:
            iv = int(s)
            return iv if iv > 10**12 else iv * 1000
        except Exception:
            return None
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    try:
        d = dt.datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=dt.timezone.utc)
        return int(d.timestamp() * 1000)
    except Exception:
        return None


def quantile(s, p):
    if not s: return float('nan')
    k=(len(s)-1)*p; f=math.floor(k); c=math.ceil(k)
    return float(s[int(k)] if f==c else s[f]*(c-k)+s[c]*(k-f))


def summarize(vals):
    s=sorted(float(v) for v in vals)
    return {"n":len(s),"mean":statistics.fmean(s),"median":statistics.median(s),
            "stdev":statistics.pstdev(s) if len(s)>1 else 0.0,
            "min":s[0],"max":s[-1],"p05":quantile(s,0.05),"p25":quantile(s,0.25),
            "p75":quantile(s,0.75),"p95":quantile(s,0.95)}


def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument('--draws', type=int, default=2000)
    ap.add_argument('--seed', type=int, default=20261116)
    ap.add_argument('--out', required=True)
    ap.add_argument('--cache-dir', required=True)
    ap.add_argument('--universe', required=True)
    ap.add_argument('--census', required=True)
    ap.add_argument('--campaign', required=True)
    ap.add_argument('--venue-label', default='Hyperliquid (Ironflow node-derived, native)')
    ap.add_argument('--rsi-threshold', type=float, default=20.0)
    ap.add_argument('--target-pct', type=float, default=9.0)
    args=ap.parse_args(argv)

    cache_dir=Path(args.cache_dir); universe_p=Path(args.universe); census_p=Path(args.census); campaign_p=Path(args.campaign)
    manifest=load_provenance(str(cache_dir/'provenance.json'))
    universe=json.loads(universe_p.read_text())
    symbols=[str(s).upper() for s in (universe.get('selected_symbols') or universe.get('symbols') or [])]
    census=json.loads(census_p.read_text())
    campaign=json.loads(campaign_p.read_text())
    candles={}
    missing=[]
    for sym in symbols:
        p=cache_dir/'candles'/f'{sym}.json'
        if not p.exists(): missing.append(sym); continue
        candles[sym]=load_candles(p)
    cfg=StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                       enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0,
                       rsi_threshold=float(args.rsi_threshold), target_pct=float(args.target_pct))
    ts_index={}
    for sym,cs in candles.items():
        m={}
        for i,c in enumerate(cs):
            ts=parse_ts_ms(c.get('timestamp') or c.get('timestamp_ms') or c.get('time'))
            if ts is not None:
                m[int(ts)]=i
        ts_index[sym]=m
    memo:Dict[Tuple[str,int],Any]={}; rows=[]
    for e in census.get('events',[]):
        sym=str(e.get('symbol','')).upper(); ts=e.get('bar_timestamp_ms')
        if ts is None: continue
        cs=candles.get(sym); idx=ts_index.get(sym,{}).get(int(ts)) if cs else None
        rec={"symbol":sym,"bar_index":idx,"bar_timestamp_ms":int(ts),
             "signal_gate_pass":bool(e.get('signal_gate_pass')),"trade_opened_canonical":bool(e.get('trade_opened'))}
        if idx is not None:
            sig=real_generate_signal(cs[:idx+1], symbol=sym, config=cfg, capital=100000.0)
            rec["signal"]=sig is not None
            if sig is not None: memo[(sym,idx)]=sig
        else:
            rec["signal"]=False
        rows.append(rec)
    keys=sorted({(str(r['symbol']).upper(),int(r['bar_index'])) for r in rows if r.get('signal_gate_pass') and r.get('bar_index') is not None and (str(r['symbol']).upper(),int(r['bar_index'])) in memo})
    admitted=sorted({(str(r['symbol']).upper(),int(r['bar_index'])) for r in rows if r.get('trade_opened_canonical') and r.get('bar_index') is not None and (str(r['symbol']).upper(),int(r['bar_index'])) in memo})
    meta={"census_events":len(census.get('events',[])),"rows":len(rows),"memo_signals":len(memo),
          "signal_gate_events":sum(1 for r in rows if r.get('signal_gate_pass')),
          "memo_matches_signal_gate":len(memo)==sum(1 for r in rows if r.get('signal_gate_pass')),
          "admitted_trade_keys":len(admitted)}
    candles_active={s:candles[s] for s in sorted({k[0] for k in memo}|{'ETH'}) if s in candles}

    def run_portfolio(active_keys):
        active={k:memo[k] for k in active_keys if k in memo}
        def mg(candles_arg, symbol='TEST', config=None, capital=100000.0, risk_state=None, cache=None):
            return active.get((symbol,len(candles_arg)-1))
        orig=portfolio_mod.generate_signal; portfolio_mod.generate_signal=mg
        try:
            return portfolio_mod.run_portfolio_simulation(candles_active, cfg, 100000.0, {"ETH": candles["ETH"]} if "ETH" in candles else {}, require_eth_hedge=True)
        finally:
            portfolio_mod.generate_signal=orig

    def tsum(res):
        trades=res.get('trades',[]) or []
        return {"num_trades":int(res.get('num_trades',len(trades))),"total_pnl":float(res.get('total_pnl',0.0))}

    t0=time.time()
    canon_summary={"num_trades":int(campaign.get('num_trades',len(campaign.get('trades',[])))), "total_pnl":float(campaign.get('total_pnl',0.0))}
    choose_k=len(admitted) if admitted else canon_summary['num_trades']
    replay = tsum(run_portfolio(admitted)) if admitted else canon_summary
    rng=random.Random(args.seed)
    n=len(keys); k=min(choose_k,n)
    from math import comb
    total_comb = comb(n,k) if 0<=k<=n else 0
    exact = 0 < total_comb <= 5000
    pnls=[]; trade_counts=[]
    if exact:
        import itertools
        for subset in itertools.combinations(keys,k):
            r=tsum(run_portfolio(subset)); pnls.append(r['total_pnl']); trade_counts.append(r['num_trades'])
        mode='exact_enumeration'
    else:
        seen=set()
        draws=min(args.draws, total_comb if total_comb>0 else args.draws)
        while len(pnls)<draws:
            subset=tuple(sorted(rng.sample(keys,k))) if k>0 and n>=k else tuple()
            if subset in seen:
                if total_comb and len(seen)>=total_comb: break
                continue
            seen.add(subset)
            r=tsum(run_portfolio(list(subset))); pnls.append(r['total_pnl']); trade_counts.append(r['num_trades'])
        mode='seeded_random_subsets'
    svals=sorted(pnls) if pnls else []
    ge=sum(1 for x in pnls if x>=canon_summary['total_pnl']-1e-9)
    le=sum(1 for x in pnls if x<=canon_summary['total_pnl']+1e-9)
    result={
        "schema_version":1,
        "generated_at_utc":iso_now(),
        "run_type":"portfolio_placebo_c14_wide",
        "seed":args.seed,
        "draws_requested":args.draws,
        "config":{"rsi_threshold":float(args.rsi_threshold),"target_pct":float(args.target_pct),"config_matched":True},
        "provenance_caveat":f"Real {args.venue_label} data, non-synthetic; node-derived (Ironflow HF, CC BY 4.0), NOT the venue's own candleSnapshot; Hyperliquid-native evidence (not cross-venue).",
        "venue_label":args.venue_label,
        "is_hyperliquid_evidence":True,
        "fabricated_data":False,
        "synthetic_data":False,
        "inputs":{
            "cache_dir":str(cache_dir),"manifest":str(cache_dir/'provenance.json'),
            "universe":str(universe_p),"census":str(census_p),"campaign":str(campaign_p),
            "manifest_sha256":sha256_file(cache_dir/'provenance.json'),
            "universe_sha256":sha256_file(universe_p),"census_sha256":sha256_file(census_p),"campaign_sha256":sha256_file(campaign_p),
        },
        "canonical":{**canon_summary,"replay":replay},
        "memo":meta,"missing_symbols":missing,
        "pool":{"signal_gate_events":len(keys),"choose_k":k,"total_combinations":int(total_comb),"mode":mode},
        "placebo":{"runs":len(pnls),"summary":summarize(pnls) if pnls else {},
                   "trade_count_summary":summarize([float(x) for x in trade_counts]) if trade_counts else {},
                   "p_ge_canonical": ge/len(pnls) if pnls else None,
                   "p_le_canonical": le/len(pnls) if pnls else None,
                   "canonical_percentile_le": le/len(pnls) if pnls else None,
                   "prob_total_pnl_positive": sum(1 for x in pnls if x>0)/len(pnls) if pnls else None},
        "wall_seconds":time.time()-t0,
        "limitations":[
            "Hyperliquid-native (Ironflow node-derived) wide cache; NOT cross-venue.",
            "Tests admission/cap/occupancy selection within observed gate-passing pool, not detector existence.",
            "Preserves all gates, sizing, cap, hedge, fees, funding, liquidation; no synthetic data.",
        ],
    }
    out_base=Path(args.out)
    if not out_base.is_absolute(): out_base=REPO/'research_state'/out_base
    out_base.with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
    s=result['placebo'].get('summary') or {}
    md=[f"# C14 Full-Portfolio Placebo — Hyperliquid-native wide","",f"**Generated:** {result['generated_at_utc']}","",
        f"**Mode:** {mode} (runs={len(pnls)}, choose {k} of {len(keys)}, total_comb={total_comb})","",
        f"**Canonical:** trades={canon_summary['num_trades']} pnl={canon_summary['total_pnl']:.6f} replay={replay}","",
        f"**Placebo summary:** {json.dumps(s)}","",
        f"**p_ge_canonical:** {result['placebo'].get('p_ge_canonical')}  **P(total>0):** {result['placebo'].get('prob_total_pnl_positive')}","",
        f"**Provenance:** {result['provenance_caveat']}",""]
    out_base.with_suffix('.md').write_text('\n'.join(md)+'\n')
    print(f"placebo_c14: mode={mode} runs={len(pnls)} k={k} n={len(keys)} canon_pnl={canon_summary['total_pnl']:.4f} p_ge={result['placebo'].get('p_ge_canonical')} wall={result['wall_seconds']:.1f}s")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
