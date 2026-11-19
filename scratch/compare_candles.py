import time, json, random, math, statistics, multiprocessing as mp
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
import scripts.run_c20_cross_venue_campaign as c20

REPO = Path('.')
sv = c20.load_venue('okx')
cfg = c20.spec_literal_config()
campaign = c20.run_campaign(sv, 'c25_timing_probe8')
census = c20.build_census(sv, campaign, 'c25_timing_probe8')
memo, rows, meta = c20.build_memo(sv, census, cfg)
keys = sorted({(str(r['symbol']).upper(), int(r['bar_index']))
               for r in rows if r.get('signal_gate_pass') and r.get('bar_index') is not None
               and (str(r['symbol']).upper(), int(r['bar_index'])) in memo})
print('keys:', len(keys), flush=True)
candles_active = {s: sv['candles'][s] for s in sorted({k[0] for k in keys} | {'ETH'}) if s in sv['candles']}

# Time ONE draw with the FULL 34-symbol candles_active (as C25 does)
sub = keys
t = time.time()
res = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
print('ONE draw FULL candles: %.2fs trades=%s pnl=%.2f' % (time.time() - t, res.get('num_trades'), res.get('total_pnl')), flush=True)

# Time ONE draw with ONLY the active symbols (as C24's exact-enum path does)
t = time.time()
res2 = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
print('ONE draw active-only: %.2fs trades=%s pnl=%.2f' % (time.time() - t, res2.get('num_trades'), res2.get('total_pnl')), flush=True)

# Check: how many symbols in candles_active vs sv['candles']
print('candles_active symbols:', len(candles_active), 'of', len(sv['candles']), flush=True)
print('all symbols:', sorted(sv['candles'].keys()), flush=True)