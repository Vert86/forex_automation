"""
Full Automation Test Script
Tests the complete system with a single scan
"""

from main import ForexTradingBot

print("="*60)
print("FULL AUTOMATION TEST")
print("="*60)
print()
print("This will:")
print("  1. Initialize FIX API connection")
print("  2. Scan all configured symbols")
print("  3. Generate signals if conditions met")
print("  4. Execute trades via FIX API")
print("  5. Send Telegram notifications")
print()
print("Mode: LIVE TRADING (if AUTO_TRADING_ENABLED=True)")
print()

# Import config to show current settings
import config
import fix_config

print("Current Settings:")
print(f"  Symbols: {len(config.SYMBOLS)} symbols")
print(f"  Timeframe: {config.TIMEFRAME}")
print(f"  Risk per Trade: {config.RISK_PER_TRADE_PERCENT}%")
print(f"  Min Confluence: {config.MIN_CONFLUENCE_SIGNALS} signals")
print(f"  Volatility Range: {config.MIN_VOLATILITY_THRESHOLD} - {config.MAX_VOLATILITY_THRESHOLD}")
print()

try:
    from fix_config_local import DRY_RUN_MODE, AUTO_TRADING_ENABLED
    print(f"  Auto Trading: {'ENABLED' if AUTO_TRADING_ENABLED else 'DISABLED'}")
    print(f"  Dry Run Mode: {'YES (Simulated)' if DRY_RUN_MODE else 'NO (Real Trades)'}")
except ImportError:
    print(f"  Auto Trading: {'ENABLED' if fix_config.AUTO_TRADING_ENABLED else 'DISABLED'}")
    print(f"  Dry Run Mode: {'YES (Simulated)' if fix_config.DRY_RUN_MODE else 'NO (Real Trades)'}")

print()
response = input("Continue with test? (yes/no): ")

if response.lower() != 'yes':
    print("Test cancelled.")
    exit()

print()
print("="*60)
print("Starting Test...")
print("="*60)
print()

try:
    # Create bot instance
    bot = ForexTradingBot()

    # Run single scan
    bot.start(run_once=True)

    print()
    print("="*60)
    print("Test Complete!")
    print("="*60)
    print()
    print("Check:")
    print("  1. Terminal output above for signal generation")
    print("  2. Telegram for notifications")
    print("  3. fix_logs/ for FIX API execution details")
    print("  4. cTrader platform for executed trades")
    print()

except KeyboardInterrupt:
    print("\n\nTest interrupted by user")
except Exception as e:
    print(f"\n\nTest failed with error: {e}")
    import traceback
    traceback.print_exc()
