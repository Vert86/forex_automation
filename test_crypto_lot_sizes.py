"""
Test symbol-specific lot sizes for crypto
"""

from risk_management import RiskManagement
import config

print("="*60)
print("SYMBOL-SPECIFIC LOT SIZE TEST")
print("="*60)
print()

rm = RiskManagement()

# Test with different symbols
test_cases = [
    ("EURUSD", 1.16000, 1.15800, 0.01),      # Forex - should use default
    ("GBPUSD", 1.28000, 1.27500, 0.01),      # Forex - should use default
    ("XAUUSD", 2650.00, 2640.00, 0.01),      # Gold - should use default
    ("BTCUSD", 95000, 94000, 0.00001),       # Bitcoin - should use custom
    ("ETHUSD", 3000, 2950, 0.00001),         # Ethereum - should use custom
    ("LTCUSD", 100, 99, 0.0001),             # Litecoin - should use custom
]

print("Testing position size calculation:")
print("-" * 60)
print(f"{'Symbol':<10} {'Entry':<12} {'SL':<12} {'Expected':<10} {'Actual':<10} {'Status':<8}")
print("-" * 60)

all_correct = True
for symbol, entry, sl, expected_lots in test_cases:
    actual_lots = rm.calculate_position_size(entry, sl, symbol)
    status = "OK" if actual_lots == expected_lots else "FAIL"
    if actual_lots != expected_lots:
        all_correct = False
    
    print(f"{symbol:<10} {entry:<12.2f} {sl:<12.2f} {expected_lots:<10.5f} {actual_lots:<10.5f} {status:<8}")

print()
print("="*60)
if all_correct:
    print("SUCCESS: All symbols use correct lot sizes!")
else:
    print("FAILED: Some symbols have incorrect lot sizes")
print("="*60)
