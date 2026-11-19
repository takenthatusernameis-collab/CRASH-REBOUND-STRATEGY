import time, json, random
from pathlib import Path
import scripts.run_c20_cross_venue_campaign as c20

REPO = Path('.')
sv = c20.load_venue('okx')
cfg = c20.spec_literal_config()
campaign = c20.run_campaign(sv, 'c25_timing_probe3')
census = c20.build_census(sv, campaign, 'c25_timing_probe3')
memo, rows, meta = c20.build_memo(sv, census, cfg)
print('memo size:', len(memo), 'rows:', len(rows), 'signal_gate:', meta.get('signal_gate_events'), flush=True)
keys = sorted({(str(r['symbol']).upper(), int(r['bar_index']))
               for r in rows if r.get('signal_gate_pass') and r.get('bar_index') is not None
               and (str(r['symbol']).upper(), int(r['bar_index'])) in memo})
print('keys:', len(keys), flush=True)
candles_active = {s: sv['candles'][s] for s in sorted({k[0] for k in keys} | {'ETH'}) if s in sv['candles']}

# Time the C24-style call: max_permutation_draws=20000
canonical = c20.run_memo_portfolio(candles_active, cfg, {k: memo[k] for k in keys if k in memo})
canonical_pnl = float(canonical.get('total_pnl', 0.0))
print('canonical okx 2023 pnl=%.2f' % canonical_pnl, flush=True)

t = time.time()
r = c20.conditional_permutation_null(sv, memo, rows, keys, canonical_pnl, cfg, 20000, c20.SEED, 4, max_permutation_draws=20000)
print('C24-style perm (max_permutation_draws=20000): %.2fs draws_evaluated=%s' % (time.time() - t, r.get('draws_evaluated')), flush=True)

# Time the C25-style call: draws=20000, no max_permutation_draws
t = time.time()
r2 = c20.conditional_permutation_null(sv, memo, rows, keys, canonical_pnl, cfg, 20000, c20.SEED, 4)
print('C25-style perm (no cap): %.2fs draws_evaluated=%s' % (time.time() - t, r2.get('draws_evaluated')), flush=True)