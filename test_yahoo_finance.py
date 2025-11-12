"""
Test Script for Yahoo Finance Data Integration
Tests data fetching and technical indicator calculations for all symbol types
"""

import sys
sys.path.append('.')

from data_ingestion import DataIngestion
from indicators import TechnicalIndicators
from strategy import TradingStrategy

def test_symbol(symbol, interval="1h"):
    """Test a single symbol"""
    print(f"\n{'='*80}")
    print(f"Testing: {symbol} ({interval} timeframe)")
    print('='*80)

    try:
        # Fetch data
        data_fetcher = DataIngestion()
        df = data_fetcher.get_market_data(symbol, interval=interval, bars=200)

        if df is None or len(df) == 0:
            print(f"❌ FAILED: No data returned for {symbol}")
            return False

        print(f"✅ Data fetched: {len(df)} bars")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Latest close: {df['close'].iloc[-1]:.5f}")

        # Check data quality
        if df.isnull().any().any():
            print(f"⚠️  WARNING: Data contains null values")

        # Calculate technical indicators
        print(f"\n📊 Calculating Technical Indicators...")
        indicators = TechnicalIndicators.calculate_all_indicators(df)

        if indicators is None:
            print(f"❌ FAILED: Could not calculate indicators for {symbol}")
            return False

        print(f"✅ Indicators calculated successfully:")
        print(f"   ATR: {indicators['atr']:.5f}")
        print(f"   MA10: {indicators['short_ma']:.5f}")
        print(f"   MA50: {indicators['long_ma']:.5f}")
        print(f"   RSI: {indicators['rsi']:.2f}")
        print(f"   Support levels: {len(indicators['support_levels'])} found")
        print(f"   Resistance levels: {len(indicators['resistance_levels'])} found")

        # Test signal generation
        print(f"\n🎯 Testing Signal Generation...")
        strategy = TradingStrategy()
        signal = strategy.generate_signal(indicators)

        if signal:
            print(f"✅ Signal generated: {signal['action']}")
            if signal['action'] != 'HOLD':
                print(f"   Confidence: {signal['confidence']}")
                print(f"   Signals: {signal['total_signals']}")
                print(f"   Reasons:")
                for sig in signal['signals']:
                    print(f"      - {sig['name']}: {sig['reason']}")
        else:
            print(f"❌ FAILED: Could not generate signal")
            return False

        print(f"\n✅ SUCCESS: {symbol} passed all tests!")
        return True

    except Exception as e:
        print(f"❌ ERROR testing {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run comprehensive tests"""
    print("\n" + "="*80)
    print("YAHOO FINANCE DATA & TECHNICAL ANALYSIS TEST")
    print("="*80)

    # Test symbols from each category
    test_symbols = {
        "Forex": ["EURUSD", "GBPUSD", "USDJPY"],
        "Crypto": ["BTCUSD", "ETHUSD"],
        "Commodities": ["XAUUSD", "XTIUSD"]
    }

    results = {}

    for category, symbols in test_symbols.items():
        print(f"\n\n{'#'*80}")
        print(f"# Testing {category}")
        print(f"{'#'*80}")

        for symbol in symbols:
            success = test_symbol(symbol)
            results[symbol] = success

    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for symbol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}  {symbol}")

    print(f"\n{'='*80}")
    print(f"Results: {passed}/{total} tests passed")
    print(f"{'='*80}")

    if passed == total:
        print("\n🎉 All tests passed! Yahoo Finance integration is working perfectly!")
        print("\nThe bot can successfully:")
        print("  ✅ Fetch OHLC data for forex, crypto, and commodities")
        print("  ✅ Calculate all technical indicators (ATR, MA, RSI, S/R, etc.)")
        print("  ✅ Generate trading signals with confluence")
        print("\n🚀 Ready to run: python main.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
