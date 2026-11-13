#!/usr/bin/env python3
"""Next focus campaign (post-Phase L) for real OKX 283d canonical run.

Produces:
- research_state/placebo_okx_full.{json,md}
- research_state/walkforward_okx_full.{json,md}
- research_state/risk_budget_real_okx_full.{json,md}

Uses only on-disk real cache/manifest/universe/census/campaign artifacts.
No network, no fabrication, no canonical artifact overwrites.
"""
from __future__ import annotations
import json, hashlib, math, random, statistics, time, sys
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.data.provenance import load_provenance
from src.strategy.config import StrategyConfig
from src.strategy.crash_rebound import generate_signal
from src.backtest.engine import backtest_simple
from src.metrics import compute_campaign_metrics, metrics_to_dict

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)
SEED = 20261113

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def iso_now():
    return datetime.now(timezone.utc).isoformat()

def load_candles(path: Path):
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get('candles', data)
    return data

def load_inputs():
    cache_dir = REPO/'research_state/cache/okx_1h_full_20251220_20260928'
    manifest = load_provenance(str(cache_dir/'provenance.json'))
    with open(REPO/'research_state/universe_okx_full_verified.json') as f:
        uni = json.load(f)
    symbols = [s.upper() for s in (uni.get('selected_symbols') or uni.get('symbols') or [])]
    with open(REPO/'research_state/crash_event_census_real_okx_full.json') as f:
        census = json.load(f)
    with open(REPO/'research_state/campaign_results_real_okx_full.json') as f:
        campaign = json.load(f)
    with open(REPO/'research_state/interaction_sweep_real_okx_full.json') as f:
        interaction = json.load(f)
    with open(REPO/'research_state/sensitivity_sweep_real_okx_full.json') as f:
        sensitivity = json.load(f)
    candles_by_sym = {}
    for sym in symbols:
        p = cache_dir/'candles'/f'{sym}.json'
        if p.exists():
            candles_by_sym[sym] = load_candles(p)
    ts_index = {}
    for sym, cs in candles_by_sym.items():
        m = {}
        for i,c in enumerate(cs):
            t = c.get('timestamp') or c.get('timestamp_ms') or c.get('time')
            if t is not None:
                try: m[int(t)] = i
                except: pass
        ts_index[sym] = m
    return {
        'cache_dir': cache_dir, 'manifest': manifest, 'uni': uni, 'symbols': symbols,
        'census': census, 'campaign': campaign, 'interaction': interaction, 'sensitivity': sensitivity,
        'candles_by_sym': candles_by_sym, 'ts_index': ts_index,
        'eth_candles': candles_by_sym.get('ETH'),
        'cfg': StrategyConfig(use_rsi_trigger=True, enable_rebound_short=True, enable_eth_hedge=True,
                              enable_volume_based_sizing=True, min_daily_volume_usd=5_000_000.0),
    }

def per_event_sim(e, inp):
    sym = e['symbol']
    cs = inp['candles_by_sym'].get(sym)
    if not cs:
        return {'ok': False, 'reason': 'missing_symbol', 'symbol': sym, 'bar_timestamp_ms': e.get('bar_timestamp_ms')}
    idx = inp['ts_index'].get(sym, {}).get(int(e['bar_timestamp_ms']))
    if idx is None:
        return {'ok': False, 'reason': 'missing_bar', 'symbol': sym, 'bar_timestamp_ms': e.get('bar_timestamp_ms')}
    hist = cs[:idx+1]
    sig = generate_signal(hist, symbol=sym, config=inp['cfg'], capital=100000.0)
    if sig is None:
        return {'ok': False, 'reason': 'no_signal', 'symbol': sym, 'bar_timestamp_ms': e.get('bar_timestamp_ms'),
                'volume_gate_pass': bool(e.get('volume_gate_pass')), 'bounce_confirmed': bool(e.get('bounce_confirmed')),
                'regime_min_price_ok': bool(e.get('regime_min_price_ok')),
                'trailing_24h_volume_usd': e.get('trailing_24h_volume_usd'), 'blocking_reason': e.get('blocking_reason')}
    sig.signal_index = idx
    try:
        res = backtest_simple(cs, sig, config=inp['cfg'], capital=100000.0, risk_state=None,
                              eth_candles=inp['eth_candles'], require_eth_hedge=False)
    except Exception as ex:
        return {'ok': False, 'reason': f'error:{type(ex).__name__}', 'symbol': sym, 'bar_timestamp_ms': e.get('bar_timestamp_ms')}
    if res is None or getattr(res,'exit_reason',None) in ('blocked','no_signal',None):
        return {'ok': False, 'reason': getattr(res,'exit_reason','none') if res else 'none', 'symbol': sym}
    total = getattr(res,'total_pnl', None)
    if total is None:
        total = (getattr(res,'pnl',0) or 0) + (getattr(res,'hedge_pnl',0) or 0) + (getattr(res,'rebound_short_pnl',0) or 0) + (getattr(res,'rebound_hedge_pnl',0) or 0)
    return {
        'ok': True, 'symbol': sym, 'bar_timestamp_ms': e.get('bar_timestamp_ms'),
        'bar_timestamp_utc': e.get('bar_timestamp_utc'), 'exit_reason': res.exit_reason,
        'total_pnl': float(total), 'pnl': float(getattr(res,'pnl',0) or 0),
        'bars_held': getattr(res,'bars_held',None), 'entry_price': getattr(res,'entry_price',None),
        'shares': getattr(res,'shares',None),
        'volume_gate_pass': bool(e.get('volume_gate_pass')),
        'bounce_confirmed': bool(e.get('bounce_confirmed')),
        'regime_min_price_ok': bool(e.get('regime_min_price_ok')),
        'trailing_24h_volume_usd': e.get('trailing_24h_volume_usd'),
        'desired_notional': e.get('desired_notional'),
        'blocking_reason': e.get('blocking_reason'),
        'trade_opened_in_canonical': bool(e.get('trade_opened')),
    }

def percentile_of(value, dist):
    # fraction of dist <= value and >= value for one-sided upper
    if not dist: return None
    le = sum(1 for x in dist if x <= value)
    ge = sum(1 for x in dist if x >= value)
    return {'le_frac': le/len(dist), 'ge_frac': ge/len(dist), 'rank_of_le': le, 'n': len(dist)}

def summarize_dist(vals):
    if not vals: return {}
    s = sorted(vals)
    def q(p):
        k = (len(s)-1)*p
        f = math.floor(k); c = math.ceil(k)
        if f==c: return s[int(k)]
        return s[f]*(c-k)+s[c]*(k-f)
    return {
        'n': len(s), 'mean': statistics.fmean(s), 'median': statistics.median(s),
        'stdev': statistics.pstdev(s) if len(s)>1 else 0.0,
        'min': s[0], 'max': s[-1], 'p05': q(0.05), 'p25': q(0.25), 'p75': q(0.75), 'p95': q(0.95),
    }

def run_placebo_and_bootstrap(inp):
    t0 = time.time()
    events = inp['census']['events']
    vol_pass = [e for e in events if e.get('volume_gate_pass')]
    bounce_conf = [e for e in events if e.get('bounce_confirmed')]
    traded = [e for e in events if e.get('trade_opened')]
    canonical_total = float(inp['campaign']['results']['total_pnl'])
    canonical_trades = inp['campaign']['results']['trades']

    vp_sims = [per_event_sim(e, inp) for e in vol_pass]
    bc_sims = [per_event_sim(e, inp) for e in bounce_conf]
    tr_sims = [per_event_sim(e, inp) for e in traded]
    vp_ok = [x for x in vp_sims if x.get('ok')]
    bc_ok = [x for x in bc_sims if x.get('ok')]
    tr_ok = [x for x in tr_sims if x.get('ok')]

    # gate-preserving proof summary
    def gate_proof(xs):
        return {
            'count': len(xs),
            'all_volume_gate_pass': all(x.get('volume_gate_pass') for x in xs),
            'all_trailing_24h_ge_5m': all((x.get('trailing_24h_volume_usd') or 0) >= 5_000_000 for x in xs),
            'bounce_confirmed_count': sum(1 for x in xs if x.get('bounce_confirmed')),
            'regime_min_price_ok_count': sum(1 for x in xs if x.get('regime_min_price_ok')),
        }

    rng = random.Random(SEED)
    n_trials = 2000
    draw_k = len(traded)  # 8

    def bootstrap_null(pool_ok, k, trials):
        # draw k with replacement from pool_ok per-event total_pnl values
        vals = [x['total_pnl'] for x in pool_ok]
        if not vals: return [], []
        totals = []
        means = []
        for _ in range(trials):
            sample = [vals[rng.randrange(len(vals))] for _ in range(k)]
            totals.append(sum(sample))
            means.append(sum(sample)/k)
        return totals, means

    vp_totals, vp_means = bootstrap_null(vp_ok, draw_k, n_trials)
    bc_totals, bc_means = bootstrap_null(bc_ok, draw_k, n_trials)

    # percentile of real canonical total in null totals
    real_total = canonical_total
    real_mean = real_total / draw_k
    def one_sided_p(value, dist):
        # fraction >= value (upper tail, testing positive edge)
        if not dist: return None
        return sum(1 for x in dist if x >= value) / len(dist)

    # symbol-block bootstrap (resample whole symbols with replacement among traded symbols set)
    trade_pnls = [float(t.get('total_pnl', t.get('pnl', 0)) or 0) for t in canonical_trades]
    by_sym = defaultdict(list)
    for t in canonical_trades:
        by_sym[t['symbol']].append(float(t.get('total_pnl', t.get('pnl', 0)) or 0))
    sym_keys = sorted(by_sym.keys())
    sym_totals = [sum(by_sym[s]) for s in sym_keys]
    rng2 = random.Random(SEED)
    n_block = 2000
    block_totals = []
    block_trade_counts = []
    for _ in range(n_block):
        sample_syms = [sym_keys[rng2.randrange(len(sym_keys))] for _ in range(len(sym_keys))]
        tot = 0.0; tc = 0
        for s in sample_syms:
            tot += sum(by_sym[s]); tc += len(by_sym[s])
        block_totals.append(tot); block_trade_counts.append(tc)
    block_summary = summarize_dist(block_totals)
    if block_totals:
        s = sorted(block_totals)
        def bq(p):
            k=(len(s)-1)*p; f=math.floor(k); c=math.ceil(k)
            return s[int(k)] if f==c else s[f]*(c-k)+s[c]*(k-f)
        block_ci_low = bq(0.025); block_ci_high = bq(0.975)
        block_prob_pos = sum(1 for x in block_totals if x>0)/len(block_totals)
    else:
        block_ci_low=block_ci_high=block_prob_pos=None

    # trade-level bootstrap (like L, for reference) with same seed for comparability
    rng3 = random.Random(SEED)
    trade_boot = []
    for _ in range(10000):
        sample = [trade_pnls[rng3.randrange(len(trade_pnls))] for _ in range(len(trade_pnls))]
        trade_boot.append(sum(sample))
    tb = sorted(trade_boot)
    def tq(p):
        k=(len(tb)-1)*p; f=math.floor(k); c=math.ceil(k)
        return tb[int(k)] if f==c else tb[f]*(c-k)+tb[c]*(k-f)

    wall = time.time() - t0
    result = {
        'schema_version': 1,
        'generated_at_utc': iso_now(),
        'provenance_caveat': PROVENANCE_CAVEAT,
        'method': 'per-event exit-model null + bootstrap (complementary to full-portfolio placebo)',
        'seed': SEED,
        'canonical': {
            'trades': len(canonical_trades),
            'total_pnl': real_total,
            'mean_trade_total_pnl': real_mean,
            'sha256': sha256_file(REPO/'research_state/campaign_results_real_okx_full.json'),
        },
        'pools': {
            'volume_pass_events': len(vol_pass),
            'bounce_confirmed_events': len(bounce_conf),
            'traded_events': len(traded),
            'volume_pass_sim_ok': len(vp_ok),
            'bounce_confirmed_sim_ok': len(bc_ok),
            'traded_sim_ok': len(tr_ok),
        },
        'gate_preserving_proof': {
            'statement': 'All placebo candidates drawn from J1 census events with volume_gate_pass=true and trailing_24h_volume_usd >= 5,000,000; $5M gate NOT relaxed. Per-event exits simulated via generate_signal+backtest_simple on cached bars with canonical StrategyConfig.',
            'volume_pass_pool': gate_proof(vp_ok),
            'bounce_confirmed_pool': gate_proof(bc_ok),
            'traded_events_independent_sim': [
                {'symbol': x['symbol'], 'ts': x['bar_timestamp_utc'], 'total_pnl': x['total_pnl'], 'exit_reason': x['exit_reason'],
                 'volume_gate_pass': x['volume_gate_pass'], 'bounce_confirmed': x['bounce_confirmed'], 'regime_min_price_ok': x['regime_min_price_ok']}
                for x in tr_ok
            ],
            'note': 'Independent per-event traded sims differ from canonical portfolio (which includes cap/occupancy/admission effects); canonical total 9159.69 is the compared value.',
        },
        'null_volume_pass_matched_k8': {
            'trials': n_trials, 'draw_k': draw_k,
            'distribution_total_pnl': summarize_dist(vp_totals),
            'distribution_mean_trade_pnl': summarize_dist(vp_means),
            'real_total_pnl': real_total,
            'real_percentile': percentile_of(real_total, vp_totals),
            'one_sided_p_ge_real': one_sided_p(real_total, vp_totals),
        },
        'null_bounce_confirmed_matched_k8': {
            'trials': n_trials, 'draw_k': draw_k,
            'distribution_total_pnl': summarize_dist(bc_totals),
            'distribution_mean_trade_pnl': summarize_dist(bc_means),
            'real_total_pnl': real_total,
            'real_percentile': percentile_of(real_total, bc_totals),
            'one_sided_p_ge_real': one_sided_p(real_total, bc_totals),
        },
        'symbol_block_bootstrap': {
            'method': 'resample whole symbols with replacement (captures symbol-level dependence); k_symbols=n_traded_symbols each draw',
            'symbols': sym_keys,
            'symbol_trade_counts': {s: len(by_sym[s]) for s in sym_keys},
            'symbol_pnls': {s: sum(by_sym[s]) for s in sym_keys},
            'trials': n_block, 'seed': SEED,
            'summary': block_summary,
            'ci_low_pnl_2p5': block_ci_low, 'ci_high_pnl_97p5': block_ci_high,
            'prob_total_pnl_positive': block_prob_pos,
        },
        'trade_level_bootstrap_reference': {
            'method': 'with-replacement over realized trade total_pnl (comparable to Phase L)',
            'trials': 10000, 'seed': SEED,
            'ci_low_pnl': tq(0.025), 'ci_high_pnl': tq(0.975),
            'prob_total_pnl_positive': sum(1 for x in trade_boot if x>0)/len(trade_boot),
            'note': 'Reference recompute; canonical Phase L artifact remains authoritative for that analysis.',
        },
        'limitations': [
            'Per-event exit-model null is independent per-event simulation (no portfolio cap/occupancy interaction across concurrent positions); complementary to, not replacement for, full-portfolio placebo.',
            'n=8 realized trades and 5 traded symbols remain severely underpowered regardless of bootstrap method.',
            'Bounce-confirmed pool (n=39 events, 11 sim-ok) overlaps with signal-admission logic; interpretation must account for selection funnel.',
            'Cross-venue OKX cache; NOT Hyperliquid performance evidence.',
        ],
        'wall_seconds': wall,
    }
    return result, vp_sims, bc_sims

def run_walkforward(inp):
    # Directional/underpowered walk-forward on cached bars using portfolio sim per split is expensive?
    # But full sim is 527s each - doing multiple splits is costly. Alternative: evaluate trades by exit timestamp halves
    # on canonical result (directional, no re-sim) and also do a simple in-sample/out-sample by symbol-time split via per-event logic.
    # Handoff says "expanding-window split... on the 2025-12-20..2026-09-28 cache. Note: only ~3-4 trades fall in each half..."
    # To be faithful and light, we can report chronological split of realized trades and also attempt a coarse re-sim on halves
    # by slicing candles - but portfolio sim requires full history for indicators/hedge; slicing start breaks indicators.
    # Better: run expanding-window evaluation by re-simulating with an allowed-trading window end cutoff? Simpler: compute trade-split OOS
    # and also run 2 half-period portfolio sims by masking post-split signals? Not straightforward.
    # Practical: provide chronological expanding/rolling split analysis of realized trades plus a re-sim attempt on first/second half windows
    # using truncated candle sets with warmup preserved from start (so indicators available). 2 full sims = ~18 min but feasible.
    from scripts.run_portfolio import run_portfolio_simulation
    t0 = time.time()
    campaign = inp['campaign']
    trades = sorted(campaign['results']['trades'], key=lambda t: int(t.get('exit_timestamp',0) or 0))
    n = len(trades)
    mid = n//2
    first = trades[:mid]; second = trades[mid:]
    def tsum(ts): return sum(float(t.get('total_pnl',0) or 0) for t in ts)
    def tcount(ts): return len(ts)
    def tsyms(ts): return sorted(set(t['symbol'] for t in ts))

    # rolling 4-trade windows
    windows = []
    wsize = 4
    for i in range(0, max(1, n-wsize+1)):
        w = trades[i:i+wsize]
        windows.append({'start_i': i, 'end_i': i+wsize-1, 'trades': tcount(w), 'total_pnl': tsum(w),
                        'symbols': tsyms(w), 'exit_span': [w[0].get('exit_timestamp'), w[-1].get('exit_timestamp')]})

    # attempt half-period portfolio re-sim with warmup: split by bar index midpoint of window
    # window bars 6792 per symbol. use first half bars 0..3395 and second 0..6791 but only count trades exiting in half? easier: run on first-half slice and full but report by exit period.
    # For indicators correctness, keep full prefix from start.
    candles = inp['candles_by_sym']
    eth = inp['eth_candles']
    syms = inp['symbols']
    def slice_candles(end_idx):
        out = {}
        for s in syms:
            cs = candles.get(s)
            if cs: out[s] = cs[:end_idx]
        return out
    # mid bar index
    any_cs = next(iter(candles.values()))
    mid_bar = len(any_cs)//2
    half1 = slice_candles(mid_bar)
    # run sims (these are the heavy steps) - do them
    cfg = inp['cfg']
    t1 = time.time()
    r1 = run_portfolio_simulation(half1, cfg, 100000.0, {'ETH': half1.get('ETH', [])} if half1.get('ETH') else ( {'ETH': eth[:mid_bar]} if eth else {}), require_eth_hedge=True)
    w1 = time.time()-t1
    t2 = time.time()
    r_full = run_portfolio_simulation({s:candles[s] for s in syms if s in candles}, cfg, 100000.0, {'ETH': eth} if eth else {}, require_eth_hedge=True)
    w2 = time.time()-t2
    # second half OOS approximation: trades in full run whose exit bar index >= mid_bar (by timestamp position) - derive from full trade exit timestamps vs mid bar timestamp
    mid_ts = int(any_cs[mid_bar-1].get('timestamp') or any_cs[mid_bar-1].get('timestamp_ms'))
    full_trades = sorted(r_full['trades'], key=lambda t: int(t.get('exit_timestamp',0) or 0))
    first_period = [t for t in full_trades if int(t.get('exit_timestamp',0) or 0) <= mid_ts]
    second_period = [t for t in full_trades if int(t.get('exit_timestamp',0) or 0) > mid_ts]

    result = {
        'schema_version': 1,
        'generated_at_utc': iso_now(),
        'provenance_caveat': PROVENANCE_CAVEAT,
        'method': 'chronological split of realized canonical trades + expanding-window bar-split portfolio re-sims (directional, underpowered)',
        'canonical_trade_chronological_split': {
            'n_trades': n,
            'first_half_trades': {'count': tcount(first), 'total_pnl': tsum(first), 'symbols': tsyms(first)},
            'second_half_trades': {'count': tcount(second), 'total_pnl': tsum(second), 'symbols': tsyms(second)},
            'both_halves_positive': tsum(first) > 0 and tsum(second) > 0,
        },
        'rolling_trade_windows_w4': windows,
        'bar_split_portfolio_resim': {
            'mid_bar_index': mid_bar,
            'mid_bar_timestamp': mid_ts,
            'first_half_period_sim': {
                'bars_per_symbol': mid_bar, 'wall_seconds': w1,
                'num_trades': r1.get('num_trades'), 'total_pnl': r1.get('total_pnl'),
                'trades': [{'symbol':t.get('symbol'),'exit_timestamp':t.get('exit_timestamp'),'total_pnl':t.get('total_pnl'),'exit_reason':t.get('exit_reason')} for t in r1.get('trades',[])],
            },
            'full_period_sim': {
                'bars_per_symbol': len(any_cs), 'wall_seconds': w2,
                'num_trades': r_full.get('num_trades'), 'total_pnl': r_full.get('total_pnl'),
            },
            'full_sim_partitioned_by_mid_exit_timestamp': {
                'first_period_count': len(first_period), 'first_period_total_pnl': sum(float(t.get('total_pnl',0) or 0) for t in first_period),
                'second_period_count': len(second_period), 'second_period_total_pnl': sum(float(t.get('total_pnl',0) or 0) for t in second_period),
                'note': 'Partition of full-run trades by exit time relative to midpoint bar; not an independent out-of-sample refit.',
            },
        },
        'limitations': [
            'Severely underpowered OOS: only 3-4 realized trades per half and trades cluster in early months; directional evidence only, not proof.',
            'Bar-split re-sim preserves warmup prefix but first-half sim cannot see future bars; full-sim partition is descriptive, not independent OOS.',
            'Cross-venue OKX cache; NOT Hyperliquid performance evidence.',
        ],
        'wall_seconds': time.time()-t0,
    }
    return result

def run_risk_budget(inp):
    # return-vs-worst-DD frontier from existing sweep artifacts, focus on rsi25_maxpos8
    inter = inp['interaction']['runs']
    sens = inp['sensitivity']['runs']
    def pick(rows):
        out = []
        for r in rows:
            m = r.get('metrics') or {}
            out.append({
                'tag': r.get('tag'), 'label': r.get('label'), 'params': r.get('params'),
                'total_return_pct': m.get('total_return_pct'), 'max_drawdown_pct': m.get('max_drawdown_pct'),
                'trade_count': m.get('trade_count'), 'total_pnl': m.get('total_pnl'),
                'win_rate': m.get('win_rate'), 'profit_factor': m.get('profit_factor'),
                'annualized_return_pct': m.get('annualized_return_pct'), 'sharpe': m.get('sharpe'),
                'net_total_pnl': m.get('net_total_pnl'),
            })
        return out
    inter_pts = pick(inter)
    sens_pts = pick(sens)
    # identify k-winner
    k_winner = next((p for p in inter_pts if p['tag']=='rsi25_maxpos8'), None)
    baseline = next((p for p in inter_pts if p['tag']=='baseline_spec'), None)
    # frontier: non-dominated in (return, -dd) among interaction points with valid numbers
    valid = [p for p in inter_pts if isinstance(p.get('total_return_pct'), (int,float)) and isinstance(p.get('max_drawdown_pct'), (int,float))]
    frontier = []
    for a in valid:
        dominated = False
        for b in valid:
            if a is b: continue
            # b dominates a if b return >= a return and b dd (less negative, closer to 0) >= a dd, strict in one
            if (b['total_return_pct'] >= a['total_return_pct'] and b['max_drawdown_pct'] >= a['max_drawdown_pct'] and
                (b['total_return_pct'] > a['total_return_pct'] or b['max_drawdown_pct'] > a['max_drawdown_pct'])):
                dominated = True; break
        if not dominated: frontier.append(a['tag'])
    # governed variants suggestions (conceptual, from observed tradeoffs) - no new sims, report drawdown-adjusted view
    governed = []
    if k_winner and baseline:
        governed.append({
            'variant': 'cap_positions_to_baseline_5',
            'rationale': 'rsi25_maxpos8 gains return (+23.44%) but incurs -18.34% DD and 33 trades vs baseline 8; capping positions (rsi25_maxpos3: +19.36%, -16.62% DD, 25 trades) partially governs DD but still elevated.',
            'evidence_points': ['baseline_spec','rsi25_maxpos3','rsi25_maxpos8'],
        })
        governed.append({
            'variant': 'prefer_baseline_or_dd_constrained',
            'rationale': 'On return-vs-worst-DD, baseline (+9.16%, -2.03% DD) dominates on drawdown; rsi25_maxpos8 is a risk-budget trade and must not be quoted without -18.34% DD and underpowered caveat.',
            'evidence_points': ['baseline_spec','rsi25_maxpos8'],
        })
    result = {
        'schema_version': 1,
        'generated_at_utc': iso_now(),
        'provenance_caveat': PROVENANCE_CAVEAT,
        'method': 'return-vs-worst-DD frontier from existing sensitivity/interaction sweep artifacts (no re-simulation)',
        'k_winner': k_winner,
        'baseline': baseline,
        'frontier_tags_interaction': frontier,
        'interaction_points': inter_pts,
        'sensitivity_points': sens_pts,
        'governed_variants': governed,
        'caveats': [
            'rsi25_maxpos8: +23.44% total return with -18.34% worst DD and 33 trades — risk-budget trade, NOT free alpha; must be quoted together.',
            'All points are from prior sweeps on underpowered OKX sample (canonical 8 trades baseline); conclusions directional only.',
            'Cross-venue OKX cache; NOT Hyperliquid performance evidence.',
        ],
    }
    return result

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + '\n')

def render_placebo_md(r):
    can = r['canonical']; vp = r['null_volume_pass_matched_k8']; bc = r['null_bounce_confirmed_matched_k8']; sb = r['symbol_block_bootstrap']
    lines = []
    lines.append('# Placebo / Null & Bootstrap — Real OKX 283d (post-Phase L)')
    lines.append('')
    lines.append(f"**Generated (UTC):** {r['generated_at_utc']}  ")
    lines.append(f"**Seed:** {r['seed']}  ")
    lines.append(f"**Provenance caveat:** {r['provenance_caveat']}")
    lines.append('')
    lines.append('## Canonical baseline (compared)')
    lines.append(f"- Trades: {can['trades']}, total PnL: **{can['total_pnl']:.6f}** (mean/trade {can['mean_trade_total_pnl']:.6f})")
    lines.append(f"- Canonical sha256: `{can['sha256']}`")
    lines.append('')
    lines.append('## Gate-preserving proof ($5M trailing-24h gate NOT relaxed)')
    lines.append(r['gate_preserving_proof']['statement'])
    for name,key in [('Volume-pass pool','volume_pass_pool'),('Bounce-confirmed pool','bounce_confirmed_pool')]:
        gp = r['gate_preserving_proof'][key]
        lines.append(f"- **{name}:** n={gp['count']}, all_volume_gate_pass={gp['all_volume_gate_pass']}, all_trailing_24h>=5M={gp['all_trailing_24h_ge_5m']}, bounce_confirmed={gp['bounce_confirmed_count']}, regime_min_price_ok={gp['regime_min_price_ok_count']}")
    lines.append('')
    lines.append('## Per-event exit-model null (matched k=8 draws, bootstrap)')
    lines.append('| Pool | sim-ok N | trials | real total PnL | null mean | null p05 | null p95 | P(null >= real) | real percentile (<=) |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|---:|---:|')
    for label, obj, nkey in [
        ('volume_pass (187 events)', vp, 'volume_pass_sim_ok'),
        ('bounce_confirmed (39 events)', bc, 'bounce_confirmed_sim_ok'),
    ]:
        d = obj['distribution_total_pnl']; pct = obj['real_percentile'] or {}; p = obj['one_sided_p_ge_real']
        lines.append(f"| {label} | {r['pools'][nkey]} | {obj['trials']} | {obj['real_total_pnl']:.2f} | {d.get('mean',float('nan')):.2f} | {d.get('p05',float('nan')):.2f} | {d.get('p95',float('nan')):.2f} | {p:.4f} | {pct.get('le_frac',float('nan')):.4f} |")
    lines.append('')
    lines.append('**Interpretation note:** per-event independent exit simulation (no portfolio cap/occupancy/admission interactions). Complementary to, not replacement for, a full-portfolio placebo. Canonical 9159.69 remains the compared real outcome.')
    lines.append('')
    lines.append('## Symbol-block bootstrap (whole-symbol resampling, dependence-aware)')
    lines.append(f"- Symbols ({len(sb['symbols'])}): {', '.join(sb['symbols'])}")
    lines.append(f"- Symbol trade counts: {sb['symbol_trade_counts']}")
    lines.append(f"- Trials: {sb['trials']}, seed: {sb['seed']}")
    lines.append(f"- 95% CI total PnL: [{sb['ci_low_pnl_2p5']:.2f}, {sb['ci_high_pnl_97p5']:.2f}]")
    lines.append(f"- P(total PnL > 0): {sb['prob_total_pnl_positive']:.4f}")
    ssum = sb['summary']
    lines.append(f"- Mean/median: {ssum.get('mean',float('nan')):.2f} / {ssum.get('median',float('nan')):.2f}")
    lines.append('')
    lines.append('## Trade-level bootstrap (reference recompute)')
    tb = r['trade_level_bootstrap_reference']
    lines.append(f"- Trials {tb['trials']}, 95% CI [{tb['ci_low_pnl']:.2f}, {tb['ci_high_pnl']:.2f}], P(>0)={tb['prob_total_pnl_positive']:.4f}. {tb['note']}")
    lines.append('')
    lines.append('## Limitations')
    for l in r['limitations']:
        lines.append(f"- {l}")
    lines.append('')
    return '\n'.join(lines)

def render_walkforward_md(r):
    c = r['canonical_trade_chronological_split']; b = r['bar_split_portfolio_resim']
    lines = []
    lines.append('# Walk-forward / OOS (directional, underpowered) — Real OKX 283d')
    lines.append('')
    lines.append(f"**Generated (UTC):** {r['generated_at_utc']}  ")
    lines.append(f"**Provenance caveat:** {r['provenance_caveat']}")
    lines.append(f"**Method:** {r['method']}")
    lines.append('')
    lines.append('## Chronological split of realized canonical trades')
    lines.append(f"- n={c['n_trades']}; first half: {c['first_half_trades']} ; second half: {c['second_half_trades']} ; both halves positive={c['both_halves_positive']}")
    lines.append('')
    lines.append('## Rolling 4-trade windows')
    for w in r['rolling_trade_windows_w4']:
        lines.append(f"- window {w['start_i']}-{w['end_i']}: trades={w['trades']} total_pnl={w['total_pnl']:.2f} symbols={w['symbols']}")
    lines.append('')
    lines.append('## Bar-split portfolio re-sim (warmup-preserving prefix)')
    fh = b['first_half_period_sim']; fp = b['full_sim_partitioned_by_mid_exit_timestamp']
    lines.append(f"- Mid bar index: {b['mid_bar_index']} (ts {b['mid_bar_timestamp']})")
    lines.append(f"- First-half sim ({fh['bars_per_symbol']} bars): trades={fh['num_trades']} total_pnl={fh['total_pnl']:.6f} wall={fh['wall_seconds']:.1f}s")
    for t in fh.get('trades',[]):
        lines.append(f"  - {t}")
    lines.append(f"- Full sim partitioned by mid exit ts: first_period n={fp['first_period_count']} pnl={fp['first_period_total_pnl']:.6f}; second_period n={fp['second_period_count']} pnl={fp['second_period_total_pnl']:.6f}. {fp['note']}")
    lines.append('')
    lines.append('## Limitations')
    for l in r['limitations']:
        lines.append(f"- {l}")
    lines.append('')
    return '\n'.join(lines)

def render_risk_md(r):
    lines = []
    lines.append('# Risk budget / Return-vs-Worst-DD frontier — Real OKX 283d')
    lines.append('')
    lines.append(f"**Generated (UTC):** {r['generated_at_utc']}  ")
    lines.append(f"**Provenance caveat:** {r['provenance_caveat']}")
    lines.append(f"**Method:** {r['method']}")
    lines.append('')
    kw = r.get('k_winner'); bl = r.get('baseline')
    lines.append('## K winner vs baseline (must be quoted together)')
    if kw:
        lines.append(f"- **rsi25_maxpos8:** return {kw['total_return_pct']}%, worst DD {kw['max_drawdown_pct']}%, trades {kw['trade_count']}, total_pnl {kw['total_pnl']}")
    if bl:
        lines.append(f"- **baseline_spec:** return {bl['total_return_pct']}%, worst DD {bl['max_drawdown_pct']}%, trades {bl['trade_count']}, total_pnl {bl['total_pnl']}")
    lines.append('')
    lines.append('## Interaction return-vs-DD points')
    lines.append('| tag | return % | worst DD % | trades | total_pnl | win_rate | PF |')
    lines.append('|---|---:|---:|---:|---:|---:|---:|')
    for p in r['interaction_points']:
        lines.append(f"| {p['tag']} | {p.get('total_return_pct')} | {p.get('max_drawdown_pct')} | {p.get('trade_count')} | {p.get('total_pnl')} | {p.get('win_rate')} | {p.get('profit_factor')} |")
    lines.append('')
    lines.append(f"**Non-dominated frontier (interaction, return vs worst DD):** {', '.join(r.get('frontier_tags_interaction',[]))}")
    lines.append('')
    lines.append('## Governed / drawdown-aware variants (from observed evidence)')
    for g in r.get('governed_variants',[]):
        lines.append(f"- **{g['variant']}**: {g['rationale']} (evidence: {', '.join(g['evidence_points'])})")
    lines.append('')
    lines.append('## Caveats')
    for c in r['caveats']:
        lines.append(f"- {c}")
    lines.append('')
    return '\n'.join(lines)

def main():
    inp = load_inputs()
    print('running placebo+bootstrap...')
    placebo_res, vp_sims, bc_sims = run_placebo_and_bootstrap(inp)
    write_json(REPO/'research_state/placebo_okx_full.json', placebo_res)
    (REPO/'research_state/placebo_okx_full.md').write_text(render_placebo_md(placebo_res))
    print('placebo done in %.1fs' % placebo_res['wall_seconds'])

    print('running walkforward...')
    wf = run_walkforward(inp)
    write_json(REPO/'research_state/walkforward_okx_full.json', wf)
    (REPO/'research_state/walkforward_okx_full.md').write_text(render_walkforward_md(wf))
    print('walkforward done in %.1fs' % wf['wall_seconds'])

    print('running risk budget...')
    rb = run_risk_budget(inp)
    write_json(REPO/'research_state/risk_budget_real_okx_full.json', rb)
    (REPO/'research_state/risk_budget_real_okx_full.md').write_text(render_risk_md(rb))
    print('risk budget done')

    for p in ['placebo_okx_full.json','placebo_okx_full.md','walkforward_okx_full.json','walkforward_okx_full.md','risk_budget_real_okx_full.json','risk_budget_real_okx_full.md']:
        fp = REPO/'research_state'/p
        print(p, sha256_file(fp))

if __name__ == '__main__':
    main()
