import time, json, random
from pathlib import Path
import scripts.run_c20_cross_venue_campaign as c20

REPO = Path('.')
sv = c20.load_venue('okx')
print('symbols:', len(sv['candles']), flush=True)
cfg = c20.spec_literal_config()

t = time.time()
full = c20.run_memo_portfolio(sv['candles'], cfg, {(k, len(sv['candles'][k]) - 1): 1 for k in sv['candles']})
print('FULL canonical okx: %.2fs trades=%s pnl=%.2f' % (time.time() - t, full.get('num_trades'), full.get('total_pnl')), flush=True)

# census + memo
t = time.time()
campaign = c20.run_campaign(sv, 'c25_timing_probe')
print('run_campaign: %.2fs' % (time.time() - t), flush=True)
census = c20.build_census(sv, campaign, 'c25_timing_probe')
memo, rows, meta = c20.build_memo(sv, census, cfg)
print('memo size:', len(memo), 'rows:', len(rows), 'signal_gate:', meta.get('signal_gate_events'), flush=True)
keys = sorted({(str(r['symbol']).upper(), int(r['bar_index']))
               for r in rows if r.get('signal_gate_pass') and r.get('bar_index') is not None
               and (str(r['symbol']).upper(), int(r['bar_index'])) in memo})
print('keys:', len(keys), flush=True)

# time ONE permutation draw
candles_active = {s: sv['candles'][s] for s in sorted({k[0] for k in keys} | {'ETH'}) if s in sv['candles']}
sub = keys  # observed subset
t = time.time()
res = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub if k in memo})
print('ONE permutation draw (observed subset): %.2fs trades=%s pnl=%.2f' % (time.time() - t, res.get('num_trades'), res.get('total_pnl')), flush=True)

# time 5 draws sequentially to get per-draw rate
t0 = time.time()
rng = random.Random(c20.SEED)
eligible = sorted({(str(r['symbol']).upper(), int(r['bar_index']))
                   for r in rows if r.get('bar_index') is not None and r.get('rsi') is not None
                   and float(r.get('rsi')) < 20.0})
by_symbol = {}
for sym, idx in eligible:
    by_symbol.setdefault(sym, []).append((sym, idx))
observed_syms = sorted({k[0] for k in keys})
per_symbol_count = {s: sum(1 for k in keys if k[0] == s) for s in observed_syms}
n = 0
for i in range(5):
    subset = []
    for s in observed_syms:
        pool_s = by_symbol.get(s, [])
        count = min(per_symbol_count[s], len(pool_s))
        if count <= 0:
            continue
        subset.extend(rng.sample(pool_s, count))
    sub2 = tuple(sorted(subset))
    res2 = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in sub2 if k in memo})
    n += 1
dt = time.time() - t0
print('5 permutation draws: %.2fs -> %.2fs/draw' % (dt, dt / max(n, 1)), flush=True)

# extrapolate full cost
per_draw = dt / max(n, 1)
print('ESTIMATED full cell cost (canonical + 20000 boot + 20000 perm + 2000 placebo):', flush=True)
print('  canonical: %.1fs' % (time.time() - t), flush=True)
print('  20000 permutation draws @ %.2fs: %.1fs = %.1f hours' % (per_draw, per_draw * 20000, per_draw * 20000 / 3600), flush=True)