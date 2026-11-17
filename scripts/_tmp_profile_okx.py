import json, sys, time
sys.path.insert(0, '.')
from scripts.run_c20_cross_venue_campaign import (
    load_venue, spec_literal_config, build_memo, run_memo_portfolio,
    run_campaign, build_census,
)

vd = load_venue('okx')
t0 = time.time(); camp = run_campaign(vd, 'tmp_smoke_c21')
print('campaign wall', round(time.time() - t0, 1), flush=True)
t0 = time.time(); cen = build_census(vd, camp, 'tmp_smoke_c21c')
print('census wall', round(time.time() - t0, 1), flush=True)
cfg = spec_literal_config()
t0 = time.time(); memo, rows, meta = build_memo(vd, cen, cfg)
print('memo wall', round(time.time() - t0, 1), 'memo_signals', meta['memo_signals'], flush=True)
t0 = time.time(); res = run_memo_portfolio(vd['candles'], cfg, memo)
print('canonical memo replay wall', round(time.time() - t0, 1),
      'trades', res.get('num_trades'), 'pnl', res.get('total_pnl'), flush=True)