# Walk-forward / OOS (directional, underpowered) — Real OKX 283d

**Generated (UTC):** 2026-11-13T20:28:12.867715+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Method:** chronological split and rolling windows over realized canonical trades (directional, underpowered OOS; no portfolio re-sim to keep feasible)

## Chronological split of realized canonical trades
- n=8; first half: count=4 pnl=1070.363968 symbols=['ETH', 'LINK', 'SOL']
- second half: count=4 pnl=8089.327966 symbols=['AVAX', 'BCH', 'SOL']
- both halves positive: True

## Rolling 4-trade windows
- window 0-3: trades=4 total_pnl=1070.363968 symbols=['ETH', 'LINK', 'SOL']
- window 1-4: trades=4 total_pnl=1407.768449 symbols=['AVAX', 'ETH', 'LINK', 'SOL']
- window 2-5: trades=4 total_pnl=3203.136011 symbols=['AVAX', 'LINK', 'SOL']
- window 3-6: trades=4 total_pnl=6359.954768 symbols=['AVAX', 'BCH', 'LINK', 'SOL']
- window 4-7: trades=4 total_pnl=8089.327966 symbols=['AVAX', 'BCH', 'SOL']

## Monthly realized (canonical trades)
- 2026-01: trades=4 total_pnl=1070.363968 symbols=['ETH', 'LINK', 'SOL']
- 2026-02: trades=3 total_pnl=8161.331714 symbols=['AVAX', 'BCH', 'SOL']
- 2026-05: trades=1 total_pnl=-72.003747 symbols=['BCH']

**Note:** Full bar-split portfolio re-sim deferred due measured cost (527s/run); trade-chronology split provided as feasible directional OOS evidence per handoff allowance for underpowered reporting.

## Limitations
- Severely underpowered OOS: only 3-4 realized trades per half, clustered in few months with long no-trade tail; directional evidence only, not proof.
- No independent out-of-sample parameter refit/re-sim performed (each full portfolio sim ~527s; right-sized campaign prioritized placebo/bootstrap); results are realized-trade chronological splits on canonical run.
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
