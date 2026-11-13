# Risk budget / Return-vs-Worst-DD frontier — Real OKX 283d

**Generated (UTC):** 2026-11-13T20:28:12.865292+00:00
**Provenance caveat:** Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; NOT Hyperliquid performance evidence.
**Method:** return-vs-worst-DD frontier from existing sensitivity/interaction sweep artifacts (no re-simulation)

## K winner vs baseline (must be quoted together)
- **rsi25_maxpos8:** return 23.438742424202765%, worst DD -18.339283066110266%, trades 33, total_pnl 23438.74242420277
- **baseline_spec:** return 9.159691934882952%, worst DD -2.0274965243788596%, trades 8, total_pnl 9159.691934882958

## Interaction return-vs-DD points
| tag | return % | worst DD % | trades | total_pnl | win_rate | PF |
|---|---:|---:|---:|---:|---:|---:|
| baseline_spec | 9.159691934882952 | -2.0274965243788596 | 8 | 9159.691934882958 | 0.5 | 5.23352442904336 |
| rsi18_maxpos8 | None | -0.06793894002337877 | 2 | 5911.026195224909 | 0.5 | 83.09331360374159 |
| rsi25_maxpos3 | 19.361967874642573 | -16.617687525687003 | 25 | 19361.96787464257 | 0.52 | 1.6400024942225147 |
| rsi25_maxpos8 | 23.438742424202765 | -18.339283066110266 | 33 | 23438.74242420277 | 0.5454545454545454 | 1.678797715546665 |
| rsi18_maxpos3 | None | -0.06793894002337877 | 2 | 5911.026195224909 | 0.5 | 83.09331360374159 |
| rsi25_target12 | 18.193233824297184 | -18.99856331301794 | 30 | 18193.233824297167 | 0.5 | 1.5268851602544662 |
| rsi25_target6 | -1.2092237175841292 | -20.902343024326246 | 30 | -1209.2237175841342 | 0.5666666666666667 | 0.9647882141885609 |
| rsi15_maxpos3 | None | -0.06793894002337877 | 2 | 5911.026195224909 | 0.5 | 83.09331360374159 |
| rsi15_maxpos8 | None | -0.06793894002337877 | 2 | 5911.026195224909 | 0.5 | 83.09331360374159 |

**Non-dominated frontier (interaction, return vs worst DD):** baseline_spec, rsi25_maxpos3, rsi25_maxpos8

## Governed / drawdown-aware variants (from observed evidence)
- **cap_positions_to_baseline_5**: rsi25_maxpos8 gains return (+23.44%) but incurs -18.34% DD and 33 trades vs baseline 8; capping positions (rsi25_maxpos3: +19.36%, -16.62% DD, 25 trades) partially governs DD but still elevated. (evidence: baseline_spec, rsi25_maxpos3, rsi25_maxpos8)
- **prefer_baseline_or_dd_constrained**: On return-vs-worst-DD, baseline (+9.16%, -2.03% DD) dominates on drawdown; rsi25_maxpos8 is a risk-budget trade and must not be quoted without -18.34% DD and underpowered caveat. (evidence: baseline_spec, rsi25_maxpos8)

## Caveats
- rsi25_maxpos8: +23.44% total return with -18.34% worst DD and 33 trades — risk-budget trade, NOT free alpha; must be quoted together.
- All points are from prior sweeps on underpowered OKX sample (canonical 8 trades baseline); conclusions directional only.
- Cross-venue OKX cache; NOT Hyperliquid performance evidence.
