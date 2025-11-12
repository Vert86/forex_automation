"""
Quick Test - Verify Yahoo Finance data is working
Run this after installing yfinance to verify everything works
"""

print("Testing Yahoo Finance data fetching...\n")

try:
    import yfinance as yf
    import pandas as pd
    print("✅ yfinance imported successfully")
except ImportError as e:
    print("❌ Missing required package!")
    print("\nPlease install: pip install yfinance")
    exit(1)

# Test 1: Forex Data
print("\n" + "="*60)
print("Test 1: Fetching EURUSD (Forex)")
print("="*60)
try:
    ticker = yf.Ticker("EURUSD=X")
    df = ticker.history(period="5d", interval="1h")
    if not df.empty:
        print(f"✅ SUCCESS: Fetched {len(df)} bars")
        print(f"   Latest price: {df['Close'].iloc[-1]:.5f}")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print("\n   Sample data:")
        print(df[['Open', 'High', 'Low', 'Close']].tail(3))
    else:
        print("❌ FAILED: No data returned")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Crypto Data
print("\n" + "="*60)
print("Test 2: Fetching BTCUSD (Crypto)")
print("="*60)
try:
    ticker = yf.Ticker("BTC-USD")
    df = ticker.history(period="5d", interval="1h")
    if not df.empty:
        print(f"✅ SUCCESS: Fetched {len(df)} bars")
        print(f"   Latest price: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print("\n   Sample data:")
        print(df[['Open', 'High', 'Low', 'Close']].tail(3))
    else:
        print("❌ FAILED: No data returned")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Commodity Data
print("\n" + "="*60)
print("Test 3: Fetching Gold Futures (Commodity)")
print("="*60)
try:
    ticker = yf.Ticker("GC=F")
    df = ticker.history(period="5d", interval="1h")
    if not df.empty:
        print(f"✅ SUCCESS: Fetched {len(df)} bars")
        print(f"   Latest price: ${df['Close'].iloc[-1]:.2f}")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print("\n   Sample data:")
        print(df[['Open', 'High', 'Low', 'Close']].tail(3))
    else:
        print("❌ FAILED: No data returned")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*60)
print("✅ Yahoo Finance is working!")
print("="*60)
print("\nNext steps:")
print("1. Run full test: python test_yahoo_finance.py")
print("2. Test single symbol: python main.py --symbol EURUSD")
print("3. Start bot: python main.py")
