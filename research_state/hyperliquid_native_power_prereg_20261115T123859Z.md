# C11.2 — Hyperliquid-Native Power & Decision Pre-Registration

**Generated (UTC):** 2026-11-15T12:38:20Z
**Schema version:** 1
**Verdict:** `PRE_REGISTRATION_DESIGN_ARTIFACT_NOT_VERDICT`
**is_hyperliquid_venue_data:** False
**performance_evidence:** False

## Status
- This is a **design / power pre-registration artifact only**.
- It is **NOT** Hyperliquid performance evidence.
- It is **NOT** a GO/NO-GO verdict.
- It pre-specifies the eventual Hyperliquid-native campaign so it cannot be faked or avoided.

## Inputs

### Hyperliquid partial chain (observed crash-episode rate)
- Source: `research_state/hyperliquid_partial_crash_census_20260419_20260928.json` (sha256: 8b0f9d9e5421ed14...)
- Window: 2026-04-19T12:00:00+00:00 .. 2026-09-28T23:00:00+00:00
- Days observed: 162.5
- Symbols: 12, bars: 46800
- RSI(21)<20 crash events: 8
- Confirmed signals: 0
- Crash events per day: 0.0492
- Expected episodes over 283-day spec window: 13.9

### Cross-venue effect-size priors (OKX + Binance)
- OKX: 19 episodes, 23 distinct crash days, canonical PnL 18220.86, verdict `underpowered`
  Source: `research_state/episode_edge_okx_multiyear.json` (sha256: 8ff3b033f128eed2...)
- Binance: 19 episodes, 23 distinct crash days, canonical PnL 21994.06, verdict `underpowered`
  Source: `research_state/episode_edge_binance_um_multiyear.json` (sha256: 318ed43a32cf4bf5...)

## Power grid results
- Alpha: 0.05, power target: 80%
- N grid tested: 39 values (20..400, step 10)
- Simulations per N: 4000
- **N80 (episodes for >=80% power): None**
- Power at max N tested: 0.5978

| N episodes | Power | CI excludes zero | Mean CI low | Mean CI high | Mean total PnL |
|---|---:|---:|---:|---:|---:|
| 20 | 0.0673 | 269/4000 | -2871.68 | 5120.86 | 1124.59 |
| 30 | 0.0675 | 270/4000 | -2301.43 | 4340.23 | 1019.40 |
| 40 | 0.0760 | 304/4000 | -1871.41 | 3961.30 | 1044.95 |
| 50 | 0.0820 | 328/4000 | -1586.61 | 3677.75 | 1045.57 |
| 60 | 0.1047 | 419/4000 | -1341.20 | 3510.24 | 1084.52 |
| 70 | 0.1158 | 463/4000 | -1183.50 | 3293.08 | 1054.79 |
| 80 | 0.1215 | 486/4000 | -1050.84 | 3146.82 | 1047.99 |
| 90 | 0.1405 | 562/4000 | -919.63 | 3076.26 | 1078.31 |
| 100 | 0.1618 | 647/4000 | -830.04 | 2950.09 | 1060.03 |
| 110 | 0.1688 | 675/4000 | -745.18 | 2859.41 | 1057.11 |
| 120 | 0.1878 | 751/4000 | -662.55 | 2804.28 | 1070.86 |
| 130 | 0.2018 | 807/4000 | -593.97 | 2736.06 | 1071.05 |
| 140 | 0.2127 | 851/4000 | -549.19 | 2665.43 | 1058.12 |
| 150 | 0.2462 | 985/4000 | -465.30 | 2645.94 | 1090.32 |
| 160 | 0.2323 | 929/4000 | -461.39 | 2543.24 | 1040.92 |
| 170 | 0.2602 | 1041/4000 | -410.66 | 2506.79 | 1048.06 |
| 180 | 0.2782 | 1113/4000 | -366.44 | 2463.58 | 1048.57 |
| 190 | 0.2958 | 1183/4000 | -322.83 | 2440.86 | 1059.02 |
| 200 | 0.3167 | 1267/4000 | -277.80 | 2413.24 | 1067.72 |
| 210 | 0.3300 | 1320/4000 | -247.89 | 2385.44 | 1068.78 |
| 220 | 0.3355 | 1342/4000 | -238.69 | 2333.66 | 1047.49 |
| 230 | 0.3600 | 1440/4000 | -205.68 | 2306.86 | 1050.59 |
| 240 | 0.3772 | 1509/4000 | -173.08 | 2290.75 | 1058.83 |
| 250 | 0.3980 | 1592/4000 | -141.10 | 2270.60 | 1064.75 |
| 260 | 0.3927 | 1571/4000 | -132.24 | 2232.54 | 1050.15 |
| 270 | 0.4185 | 1674/4000 | -91.52 | 2236.32 | 1072.40 |
| 280 | 0.4353 | 1741/4000 | -74.32 | 2208.77 | 1067.22 |
| 290 | 0.4395 | 1758/4000 | -64.62 | 2176.48 | 1055.93 |
| 300 | 0.4640 | 1856/4000 | -36.09 | 2173.37 | 1068.64 |
| 310 | 0.4713 | 1885/4000 | -28.38 | 2140.48 | 1056.05 |
| 320 | 0.4900 | 1960/4000 | -5.02 | 2131.15 | 1063.06 |
| 330 | 0.5108 | 2043/4000 | 23.70 | 2128.50 | 1076.10 |
| 340 | 0.5222 | 2089/4000 | 37.27 | 2113.11 | 1075.19 |
| 350 | 0.5255 | 2102/4000 | 33.84 | 2077.34 | 1055.59 |
| 360 | 0.5417 | 2167/4000 | 53.54 | 2067.55 | 1060.55 |
| 370 | 0.5480 | 2192/4000 | 60.83 | 2052.53 | 1056.68 |
| 380 | 0.5563 | 2225/4000 | 71.05 | 2032.87 | 1051.96 |
| 390 | 0.5707 | 2283/4000 | 94.08 | 2033.70 | 1063.89 |
| 400 | 0.5978 | 2391/4000 | 107.36 | 2021.72 | 1064.54 |

## Minimum detectable effect (MDE)
- N80: NOT FOUND in grid
- Observed mean episode PnL (cross-venue prior): N/A
- **MDE mean episode PnL: None**
- MDE as multiplier of observed mean: N/A

## Pre-registered GO/NO-GO decision rule
- Alpha: 0.05, power target: 80%
- N80 required: None episodes
- Expected HL episodes over 283d: 13.9
- Episode gap (N80 - expected): None

### GO requires (all):
  - is_hyperliquid_venue_data == true
  - performance_evidence == true
  - native archive covers full 283-day spec window (2025-12-20 .. 2026-09-28)
  - C6-T3 episode-edge test: bootstrap 95% CI of total PnL excludes zero at alpha=0.05
  - episode count >= N80 (>= 80% power)
  - conditional permutation p(null >= canonical) < 0.05
  - placebo portfolio: canonical PnL exceeds placebo distribution at alpha=0.05
  - volume_filter_ok gate holds (trailing-24h >= $5M)

### NO-GO if (any):
  - any GO requirement fails
  - native archive not obtained (REJECT_NOT_EVIDENCE persists)
  - N < N80 (underpowered)
  - CI includes zero
  - permutation p >= 0.05

### Flip to GO only if:
  Hyperliquid-native evidence clears every pre-registered requirement above

## Caveat
- This pre-registration is a design artifact. It does not constitute evidence, performance, or a verdict.

## Reproduction

```bash
PYTHONPATH=. /tmp/crs-venv/bin/python scripts/build_hyperliquid_native_power_prereg.py
```
