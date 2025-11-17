"""
Test that lot size is always 0.01
"""

from risk_management import RiskManagement
import config

print("="*60)
print("LOT SIZE CONFIGURATION TEST")
print("="*60)
print()
print(f"USE_FIXED_LOT_SIZE: {config.USE_FIXED_LOT_SIZE}")
print(f"DEFAULT_LOT_SIZE: {config.DEFAULT_LOT_SIZE}")
print()

rm = RiskManagement()

# Test with different entry/SL combinations
test_cases = [
    ("EURUSD", 1.16000, 1.15800),  # 200 pip SL
    ("EURUSD", 1.16000, 1.15950),  # 50 pip SL
    ("GBPUSD", 1.28000, 1.27500),  # 500 pip SL
    ("XAUUSD", 2650.00, 2640.00),  # 1000 pip SL
    ("BTCUSD", 95000, 94000),      # Large price difference
]

print("Testing position size calculation:")
print("-" * 60)

for symbol, entry, sl in test_cases:
    lot_size = rm.calculate_position_size(entry, sl, symbol)
    print(f"{symbol:10s} | Entry: {entry:10.5f} | SL: {sl:10.5f} | Lot Size: {lot_size}")

print()
print("="*60)
if all(rm.calculate_position_size(e, s, sym) == 0.01 for sym, e, s in test_cases):
    print("✅ SUCCESS: All trades use 0.01 lot size!")
else:
    print("❌ FAILED: Some trades have different lot sizes")
print("="*60)
