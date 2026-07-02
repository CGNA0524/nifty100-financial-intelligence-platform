from src.analytics.ratios import free_cash_flow

print(free_cash_flow(120, -40))
print(free_cash_flow(50, -120))


from src.analytics.ratios import cfo_quality_score

print(cfo_quality_score(120, 100))
print(cfo_quality_score(70, 100))
print(cfo_quality_score(30, 100))
print(cfo_quality_score(100, 0))


from src.analytics.ratios import capex_intensity

print(capex_intensity(-20, 1000))
print(capex_intensity(-50, 1000))
print(capex_intensity(-150, 1000))
print(capex_intensity(-100, 0))

from src.analytics.ratios import fcf_conversion_rate

print(fcf_conversion_rate(80, 100))
print(fcf_conversion_rate(-20, 100))
print(fcf_conversion_rate(100, 0))

from src.analytics.ratios import capital_allocation_pattern

print(capital_allocation_pattern(100, -50, -30, 1.2))
print(capital_allocation_pattern(100, -50, -30, 0.8))
print(capital_allocation_pattern(100, 20, -10))
print(capital_allocation_pattern(-100, 50, 60))
print(capital_allocation_pattern(-100, -20, 30))
print(capital_allocation_pattern(50, 20, 10))
print(capital_allocation_pattern(-10, -20, -30))
print(capital_allocation_pattern(50, -20, 30))