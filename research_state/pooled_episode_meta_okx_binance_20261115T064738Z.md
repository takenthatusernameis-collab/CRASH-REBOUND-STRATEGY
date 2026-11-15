# C10.3 — Pooled Episode Meta-Analysis OKX+Binance (20261115T064738Z)

**Generated (UTC):** 2026-11-15T06:47:38Z
**Verdict:** `underpowered`
**Provenance:** Real OKX/Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence. Pooling is across independent venues only.
**is_hyperliquid_venue_data:** false

## Independence assumption
OKX and Binance UM are independent venues with distinct matching engines, liquidity, and microstructure; their per-episode PnL paths are treated as independent draws. Pooling combines episode blocks across these independent venues only — NO same-venue duplicates pooled. Crash episodes may be temporally aligned across venues (common market shocks) while per-trade execution/PnL remains venue-specific; this is stated, not hidden.

## By venue
- **okx**: episodes=19, total_pnl=18220.8558, mean_ep=958.9924, +ep=9, -ep=10
- **binance_um**: episodes=19, total_pnl=21994.0644, mean_ep=1157.5823, +ep=7, -ep=12

## Pooled dependence-aware inference
- Pooled episodes (blocks): **38** (OKX 19 + Binance 19)
- Observed pooled total: **40214.9202**
- Episode-block bootstrap (seed=20261115, n=20000): mean=40397.7619, median=37189.0629, 95% CI=[-69065.0342, 168946.8694], P(total>0)=0.74095
- CI excludes zero: **False**; approx episodes needed for CI>0: 327
- Permutation null sign-flip (seed=20261116, n=20000): p_null_ge_canonical(one-sided)=0.26955, p_abs(two-sided)=0.53560, null_mean=154.4590

## Verdict
- `underpowered` — pooled_episodes=38, observed_total=40214.9202, bootstrap_95CI=[-69065.0342,168946.8694], P(total>0)=0.74095, perm_p_null_ge_canonical=0.26955, perm_p_two_sided_abs=0.53560

## Limitations
- Pooling is across independent venues (OKX, Binance UM) only; no same-venue duplicates. Cross-venue episodes may be temporally correlated via common market shocks though PnL paths differ.
- Episode totals are taken from prior C6-T3 dependence-aware artifacts (98h linkage) as the unit of inference; no re-simulation performed.
- Sign-flip permutation tests directional edge of episode totals, not the full temporal-admission null; interpret alongside per-venue temporal permutation p-values.
- CROSS-VENUE, is_hyperliquid_venue_data=false; NOT Hyperliquid performance evidence.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/pooled_episode_meta_okx_binance.py --seed 20261115 --boot 20000 --perm 20000
```
