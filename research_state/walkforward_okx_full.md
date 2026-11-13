# Walk-forward / OOS (directional, underpowered) — Real OKX 283d

**Generated (UTC):** 2026-11-13T20:54:59.286462+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Method:** chronological split and rolling windows over realized canonical trades (directional, underpowered OOS; no portfolio re-sim to keep feasible)

## Chronological split of realized canonical trades
- n=8; first half: {'count': 4, 'total_pnl': 1070.3639684015434, 'symbols': ['ETH', 'LINK', 'SOL']} ; second half: {'count': 4, 'total_pnl': 8089.327966481414, 'symbols': ['AVAX', 'BCH', 'SOL']} ; both halves positive=True

## Rolling 4-trade windows
- window 0-3: trades=4 total_pnl=1070.36 symbols=['ETH', 'LINK', 'SOL']
- window 1-4: trades=4 total_pnl=1407.77 symbols=['AVAX', 'ETH', 'LINK', 'SOL']
- window 2-5: trades=4 total_pnl=3203.14 symbols=['AVAX', 'LINK', 'SOL']
- window 3-6: trades=4 total_pnl=6359.95 symbols=['AVAX', 'BCH', 'LINK', 'SOL']
- window 4-7: trades=4 total_pnl=8089.33 symbols=['AVAX', 'BCH', 'SOL']

## Bar-split portfolio re-sim (warmup-preserving prefix)
- Full bar-split portfolio re-sim: **not run** (removed from this script to avoid the 600s shell-limit trap). Use `scripts/run_portfolio_placebo_okx.py` for the exact full-portfolio placebo.

## Limitations
- Severely underpowered OOS: only 3-4 realized trades per half and trades cluster in early months; directional evidence only, not proof.
- No independent out-of-sample parameter refit/re-sim performed; the exact full-portfolio placebo is the valid portfolio-level null (scripts/run_portfolio_placebo_okx.py).
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
