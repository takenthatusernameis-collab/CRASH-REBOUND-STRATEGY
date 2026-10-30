# DURABLE HANDOFF | CRASH-REBOUND-STRATEGY | 2026-10-30T01:43:44Z

## Context
- **Repo:** CRASH-REBOUND-STRATEGY (crash/rebound trading strategy)
- **Key artifacts:** `crash-rebound-strategy.pdf` (primary spec), `src/{backtest,data,strategy}/`, `tests/`, `research_state/`, `scripts/`
- **Git:** recent kilo checkpoint commits only (no explicit task trail). No README/SESSION/HANDOFF files exist.

## Bottlenecks identified (to remove)
1. **Unknown strategy specification** - The rules, triggers, universe, entry/exit, sizing, costs, and assumptions are not obvious from code alone. The PDF is almost certainly the source of truth.
2. **Unclear implementation state** - Need to map existing code vs intended behavior to avoid duplicating work or guessing.
3. **No explicit next action** - This handoff forces a concrete starting point so future sessions cannot avoid doing heavy work.

## MANDATORY FIRST TASK (do this before anything else)
Extract and operationalize the strategy from the PDF. Treat this as blocking work.

### Step 1: Extract the spec (heavy)
- Read `crash-rebound-strategy.pdf` in full. Extract all concrete rules:
  - **Crash definition/trigger** (thresholds, indicators, timeframes, filters)
  - **Universe** (assets, markets, liquidity filters)
  - **Entry conditions** (timing, confirmation, sizing logic)
  - **Exit conditions** (targets/stops/time-based/reversion rules)
  - **Risk management** (position sizing, max drawdown, diversification)
  - **Transaction costs/slippage** (commissions, fees, assumptions)
  - **Data requirements** (OHLCV, volatility, breadth, etc.)
- Write a clean, implementation-ready spec to `research_state/strategy_spec.md` with sections, bullet rules, and explicit parameters (numbers where present).

### Step 2: Map to codebase (heavy)
- Review `src/strategy/`, `src/data/`, `src/backtest/` against the extracted spec.
- Review `tests/` to see what behavior is expected/assumed.
- Write a gap analysis to `research_state/gap_analysis.md` listing: implemented vs missing, ambiguous, and what needs to change.

### Step 3: Make it runnable (heavy)
- Identify the minimal path to run an end-to-end backtest with available data/scripts.
- If critical pieces are missing but the spec is clear, implement them. If data loading is the blocker, add minimal adapters to use what's available.
- Run tests (`pytest` if present) and capture results. Fix obvious failures or document them with concrete next steps.

## FOCUS CAMPAIGN (do not deviate until Step 1 is complete)
1. **Campaign A (blocking):** PDF extraction → `research_state/strategy_spec.md`
2. **Campaign B:** Code mapping + gaps → `research_state/gap_analysis.md`
3. **Campaign C:** Get a backtest running (or fix to run) against real/available data; make progress on highest-priority gaps from B

## Success Criteria
- [ ] `research_state/strategy_spec.md` exists with concrete, testable rules/params
- [ ] `research_state/gap_analysis.md` exists with prioritized gaps + estimated effort
- [ ] Either (a) existing tests pass, or (b) there is a concrete plan + partial implementation to get them passing
- [ ] At least one end-to-end backtest path is executable (document how to run it)

## Notes
- Prioritize based on repo name: this is the crash-rebound strategy. Extract the spec first - it's the highest leverage action and will unblock all other work.
- Do not ask clarifying questions. Infer from the PDF and codebase. Document assumptions in the spec/gap analysis if anything is ambiguous.
- Keep changes minimal and testable. Focus on getting something runnable before over-engineering.
