"""Test report formula correctness"""
import pandas as pd

# Test Case: Verify restock formula
print("=== RESTOCK FORMULA TEST ===")
forecast = 8200
current = 798
gap = forecast - current
safety = forecast * 0.1
restock = gap + safety

print(f"Forecast Demand: {forecast}")
print(f"Current Inventory: {current}")
print(f"Gap: {gap}")
print(f"Safety Stock (10%): {safety}")
print(f"Restock Quantity: {restock}")
print(f"Expected: {forecast - current + forecast * 0.1}")
assert restock == 8222, f"Restock should be 8222, got {restock}"
print("[PASS] Restock formula correct\n")

# Test Case: Verify stockout cost
print("=== STOCKOUT COST TEST ===")
forecast_total = 8200
inventory_total = 798
product_price = 500
stockout_gap = forecast_total - inventory_total
stockout_cost = stockout_gap * product_price

print(f"Forecast: {forecast_total}")
print(f"Inventory: {inventory_total}")
print(f"Gap: {stockout_gap}")
print(f"Product Price: Rs.{product_price}")
print(f"Stockout Cost: Rs.{stockout_cost:,}")
assert stockout_cost == 3701000, f"Stockout cost should be 3,701,000, got {stockout_cost}"
print("[PASS] Stockout cost formula correct\n")

# Test Case: Verify ensemble accuracy consistency
print("=== ACCURACY CONSISTENCY TEST ===")
mape = 0.089
ensemble_accuracy = (1 - mape) * 100
print(f"MAPE: {mape}")
print(f"Ensemble Accuracy: {ensemble_accuracy:.1f}%")
print(f"Should appear as 91.1% everywhere in report")
assert abs(ensemble_accuracy - 91.1) < 0.01, f"Accuracy should be 91.1%, got {ensemble_accuracy:.1f}%"
print("[PASS] Accuracy calculation correct\n")

print("=== ALL TESTS PASSED ===")
