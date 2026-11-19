import time, json, random, math, statistics, multiprocessing as mp
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import scripts.run_c20_cross_venue_campaign as c20

REPO = Path('.')
sv = c20.load_venue('okx')
cfg = c20.spec_literal_config()

# Replicate run_campaign but write to a temp stem that does not exist
import scripts.run_portfolio as portfolio_mod
from scripts.run_c20_cross_venue_campaign import run_portfolio_simulation, compute_campaign_metrics, metrics_to_dict, iso_now, sha256_file, PROVENANCE_CAVEAT

candles = sv['candles']
eth = candles.get('ETH')
t0 = time.time()
res = run_portfolio_simulation(
    candles, config=cfg, capital=100_000.0,
    eth_candles={'ETH': eth} if eth else None,
    require_eth_hedge=bool(cfg.enable_eth_hedge),
)
metrics = metrics_to_dict(compute_campaign_metrics(
    trades=res.get('trades', []), equity_curve=res.get('equity_curve'),
    initial_capital=100_000.0,
))
print('canonical campaign: %.2fs trades=%s pnl=%.2f' % (time.time() - t0, res.get('num_trades'), res.get('total_pnl')), flush=True)

campaign = {
    'timestamp': iso_now(),
    'run_type': 'real_market_campaign_spec_literal_cross_venue',
    'venue_label': sv['venue_label'],
    'config': {},
    'results': {'num_trades': int(res.get('num_trades', 0)), 'total_pnl': float(res.get('total_pnl', 0.0)),
                'trades': res.get('trades'), 'equity_curve': res.get('equity_curve')},
}
census = c20.build_census(sv, campaign, 'c25_timing_probeX')
memo, rows, meta = c20.build_memo(sv, census, cfg)
print('memo size:', len(memo), 'rows:', len(rows), 'signal_gate:', meta.get('signal_gate_events'), flush=True)
keys = sorted({(str(r['symbol']).upper(), int(r['bar_index']))
               for r in rows if r.get('signal_gate_pass') and r.get('bar_index') is not None
               and (str(r['symbol']).upper(), int(r['bar_index'])) in memo})
print('keys:', len(keys), flush=True)
candles_active = {s: sv['candles'][s] for s in sorted({k[0] for k in keys} | {'ETH'}) if s in sv['candles']}
print('candles_active symbols:', len(candles_active), 'of', len(sv['candles']), flush=True)

# Time ONE draw with the FULL candles_active
sub = keys
t = time.time()
res1 = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
print('ONE draw FULL candles_active: %.2fs trades=%s pnl=%.2f' % (time.time() - t, res1.get('num_trades'), res1.get('total_pnl')), flush=True)

# Time ONE draw with ONLY the active symbols (as C24's exact-enum path does)
t = time.time()
res2 = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
print('ONE draw active-only: %.2fs trades=%s pnl=%.2f' % (time.time() - t, res2.get('num_trades'), res2.get('total_pnl')), flush=True)

# Check: how many symbols in candles_active vs sv['candles']
print('candles_active symbols:', len(candles_active), 'of', len(sv['candles']), flush=True)
print('all symbols:', sorted(sv['candles'].keys()), flush=True)