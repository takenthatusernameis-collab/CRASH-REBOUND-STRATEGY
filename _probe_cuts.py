"""Probe: confirm the top-up mechanism in apply_cap_cuts."""
from src.strategy.risk import RiskState
from src.strategy.config import StrategyConfig

cfg = StrategyConfig(gross_cap_pct=120.0)
cap = 10000 * 120.0 / 100.0  # 12000

# X=5000, A=5450 (max_live), B=2000 (requested). total=12450 > 12000.
rs = RiskState()
all_notionals = [5000, 5450, 2000]
cuts = rs.apply_cap_cuts(10000, cfg, all_notionals)
print("all_notionals:", all_notionals)
print("cuts:", cuts)
print("B's cut notional (cuts[-1]):", cuts[-1])
print("B requested 2000, got:", cuts[-1])
print("TOP-UP!" if cuts[-1] > 2000 else "OK")
print("total cuts:", sum(cuts), "<= cap:", cap, "->", sum(cuts) <= cap)