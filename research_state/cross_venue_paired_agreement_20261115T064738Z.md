# C10.1 — Cross-Venue Paired Symbol/Date Agreement (20261115T064738Z)

**Generated (UTC):** 2026-11-15T06:47:38Z
**Verdict:** `DIRECTION_REPLICATES_MAJORITY`
**Provenance:** Real OKX/Binance UM exchange data, non-synthetic; CROSS-VENUE vs Hyperliquid spec; NOT Hyperliquid performance evidence. Paired comparison across independent venues only.
**is_hyperliquid_venue_data:** false

## Pairing
- Key: (symbol, entry_date_utc, leg)
- OKX trades: 42, Binance trades: 42
- Matched 1:1 pairs: **32**, ambiguous excluded: 0
- OKX-only: 10, Binance-only: 10

## Overall paired agreement
- Same-sign rate: **1.0000** (32/32)
- Both positive: 15, both nonpositive: 17
- OKX+ / Binance-: 0, OKX- / Binance+: 0
- OKX positive rate: 0.4688, Binance positive rate: 0.4688
- Mean diff (OKX−Binance): **-454.0297**, 95% bootstrap CI: [-1057.0904098857395, 11.001007796665794]
- Sign test on paired diff (two-sided, exact binomial): p=0.596615 (OKX>Bin 18, Bin>OKX 14, nonzero 32)

## By leg
- **buy**: n=23, same_sign_rate=1.0, mean_diff=-207.52268368674112, 95% CI=[-669.6208407222064, 76.3254309548274], okx_pos=0.30434782608695654, bin_pos=0.30434782608695654
- **short**: n=9, same_sign_rate=1.0, mean_diff=-1083.9920579570519, 95% CI=[-2681.1109841968787, 151.10698072242175], okx_pos=0.8888888888888888, bin_pos=0.8888888888888888

## Verdict
- `DIRECTION_REPLICATES_MAJORITY` — n_pairs=32, same_sign_rate=1.0000, mean_diff_okx-bin=-454.029695200266, mean_diff_95CI=[-1057.0904098857395, 11.001007796665794], okx_pos_rate=0.46875, bin_pos_rate=0.46875

## Limitations
- Pairs matched on (symbol, entry_date_utc, leg); same calendar-day entry is a proxy for same crash episode, not identical bar identity.
- Unpaired trades reflect venue-specific signal/admission differences and are reported but excluded from paired stats.
- CROSS-VENUE (OKX/Binance UM), is_hyperliquid_venue_data=false; NOT Hyperliquid performance evidence.
- Bootstrap on paired differences (seeded, >=10k) without scipy; sign test exact binomial two-sided.

## Reproduction
```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/cross_venue_paired_agreement.py --seed 20261115 --boot 10000
```
