# Full Automation Testing Guide

This guide explains how to test the complete forex trading automation system from signal generation to order execution.

## Overview

The automation system works in this flow:
1. **Data Ingestion** - Fetches market data for configured symbols
2. **Technical Analysis** - Calculates indicators (RSI, MACD, Bollinger Bands, etc.)
3. **Strategy Evaluation** - Checks for confluence of multiple signals
4. **Risk Management** - Calculates position size, stop loss, take profit
5. **Order Execution** - Executes via FIX API or sends Telegram notification
6. **Notification** - Sends confirmation to Telegram

## Testing Methods

### Method 1: Single Scan Test (Recommended for First Test)

This runs the bot once, scans all symbols, and exits. Best for initial testing.

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run single scan
python main.py --test
```

**What to expect:**
- Bot initializes FIX API connection
- Scans all 15 symbols (EURUSD, GBPUSD, XAUUSD, etc.)
- Shows analysis for each symbol
- Generates signals if confluence conditions are met
- Executes trades via FIX API for any signals found
- Sends Telegram notifications for executed trades
- Exits after one complete scan

**Duration:** ~2-3 minutes (2 seconds per symbol + analysis time)

---

### Method 2: Continuous Monitoring (Production Mode)

This runs the bot continuously, scanning every 60 minutes (configurable).

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run continuously
python main.py
```

**What to expect:**
- Runs first scan immediately
- Then schedules scans every 60 minutes
- Sends daily summary at midnight
- Runs until you press Ctrl+C
- Sends shutdown notification when stopped

**To stop:**
Press `Ctrl+C`

---

### Method 3: Test Specific Symbol

To test a single symbol without running the full automation:

```python
# Create a test script: test_single_symbol.py
from main import ForexTradingBot

bot = ForexTradingBot()
result = bot.analyze_symbol("EURUSD")

if result:
    print("\nSignal Generated:")
    print(f"  Symbol: {result['symbol']}")
    print(f"  Direction: {result['signal']['direction']}")
    print(f"  Entry: {result['trade_details']['entry_price']}")
    print(f"  SL: {result['trade_details']['stop_loss']}")
    print(f"  TP: {result['trade_details']['take_profit']}")
    print(f"  Size: {result['trade_details']['position_size']} lots")
else:
    print("No signal generated")
```

Then run:
```bash
python test_single_symbol.py
```

---

## Configuration Settings

Before testing, verify these settings in your config files:

### config.py
```python
# Symbols to monitor
SYMBOLS = ["ETHUSD", "BTCUSD", "EURGBP", ...]  # 15 symbols

# Scan interval
UPDATE_INTERVAL = 60  # minutes

# Risk settings
RISK_PER_TRADE_PERCENT = 1.0  # 1% per trade
ACCOUNT_BALANCE = 10000  # Your account size

# Volatility filter
MIN_VOLATILITY_THRESHOLD = 0.3  # Lower = more signals
MAX_VOLATILITY_THRESHOLD = 3.0  # Higher = fewer signals

# Confluence requirement
MIN_CONFLUENCE_SIGNALS = 2  # Minimum signals needed to trade
```

### fix_config.py / fix_config_local.py
```python
# Trading mode
AUTO_TRADING_ENABLED = True  # Enable FIX API execution
DRY_RUN_MODE = False  # False = real trades, True = simulated

# Order settings
DEFAULT_LOT_SIZE = 0.01  # Default if risk calc fails
REQUIRE_CONFIRMATION = False  # Auto-execute without confirmation
```

---

## Understanding the Output

### Normal Operation Output

```
🚀 FOREX TRADING AUTOMATION BOT
========================================
Monitoring: 15 symbols
Timeframe: 1h
Update Interval: 60 minutes
========================================

🔍 STARTING MARKET SCAN - 2025-11-17 11:30:00
========================================

============================================================
Analyzing ETHUSD...
============================================================
Fetching market data...
Calculating indicators...
Checking strategy signals...
⚠️  No strong confluence - HOLD

============================================================
Analyzing EURUSD...
============================================================
Fetching market data...
Calculating indicators...
Checking strategy signals...
✅ BUY signal detected!
   - RSI: Oversold
   - MACD: Bullish crossover
   - Price: Near support level
   Confluence: 3 signals

📊 Trade Details:
   Symbol: EURUSD
   Direction: BUY
   Entry: 1.16008
   Stop Loss: 1.15808
   Take Profit: 1.16608
   Position Size: 0.05 lots

✅ Signal generated for EURUSD

🎯 Found 1 trading signal(s)

📤 Processing signal for EURUSD...
🤖 Executing live trade via FIX API for EURUSD...
✅ Trade executed via FIX API: ORD_1763349761014 (LIVE)
📱 Sending Telegram confirmation...

✅ SCAN COMPLETE - Next scan in 60 minutes
```

### When No Signals Found

```
🔍 STARTING MARKET SCAN - 2025-11-17 11:30:00
========================================

Analyzing ETHUSD...
⚠️  No strong confluence - HOLD

Analyzing BTCUSD...
⚠️  No strong confluence - HOLD

... (scans all symbols) ...

⚠️  No trading signals found in this scan

✅ SCAN COMPLETE - Next scan in 60 minutes
```

### FIX API Error (Falls back to Telegram)

```
🤖 Executing live trade via FIX API for EURUSD...
❌ FIX API error: Connection timeout
📊 Falling back to Telegram signal...
✅ Signal sent successfully for EURUSD
```

---

## Checking Results

### 1. Terminal Output
Watch the terminal for real-time execution status.

### 2. Telegram Messages
You should receive:
- **Startup notification** when bot starts
- **Trade signals** for each signal found
- **Trade confirmations** for successful FIX API executions
- **Daily summary** at midnight
- **Shutdown notification** when stopped

### 3. FIX Logs
Check `fix_logs/fix_client_YYYYMMDD.log` for detailed FIX API messages:
```bash
tail -f fix_logs/fix_client_20251117.log
```

Look for:
- `[OK] Login accepted by server`
- `[OK] Market order sent: BUY 0.01 EURUSD`
- `Order filled: 1000.0 @ 1.16008`
- `[OK] Order ORD_xxx FILLED at 1.16008`

### 4. cTrader Platform
Log into your cTrader account:
1. Go to **Positions** tab
2. You should see open positions for executed trades
3. Check **History** for past trades

---

## Common Testing Scenarios

### Scenario 1: Test Signal Generation Only (No Real Trades)

Edit `fix_config_local.py`:
```python
DRY_RUN_MODE = True  # Simulate trades
```

Run:
```bash
python main.py --test
```

Result: Bot will generate signals but NOT execute real trades. You'll see:
```
[DRY_RUN] Would send BUY 0.05 lots of EURUSD
   SL: 1.15808, TP: 1.16608
```

---

### Scenario 2: Lower Threshold to Generate More Signals

Edit `config.py`:
```python
MIN_CONFLUENCE_SIGNALS = 1  # Require only 1 signal (instead of 2)
MIN_VOLATILITY_THRESHOLD = 0.1  # Very low volatility filter
```

This will generate more signals for testing purposes.

---

### Scenario 3: Test Specific Symbol Only

Edit `config.py`:
```python
SYMBOLS = ["EURUSD"]  # Test only EURUSD
```

Run:
```bash
python main.py --test
```

---

### Scenario 4: Test During High Volatility

Best times for testing (forex market most active):
- **London Session:** 8:00 AM - 5:00 PM GMT (3 AM - 12 PM EST)
- **New York Session:** 1:00 PM - 10:00 PM GMT (8 AM - 5 PM EST)
- **Overlap:** 1:00 PM - 5:00 PM GMT (8 AM - 12 PM EST) - Best time!

Avoid testing:
- **Weekends:** Markets closed
- **Late evenings:** Low liquidity
- **Early Asian session:** Lower volatility for major pairs

---

## Troubleshooting

### No Signals Generated

**Possible causes:**
1. **Low volatility** - Markets are quiet
2. **No confluence** - Signals don't align
3. **Risk limits hit** - Daily/weekly loss limit reached

**Solutions:**
- Lower `MIN_CONFLUENCE_SIGNALS` to 1
- Lower `MIN_VOLATILITY_THRESHOLD` to 0.1
- Test during London/NY overlap hours
- Check risk limits in output

### FIX API Not Connecting

**Check:**
1. Internet connection
2. Markets are open (Monday-Friday)
3. Credentials in `fix_config_local.py` are correct
4. FIX logs: `tail -f fix_logs/fix_client_*.log`

### Orders Not Executing

**Check:**
1. `AUTO_TRADING_ENABLED = True` in `fix_config_local.py`
2. `DRY_RUN_MODE = False` in `fix_config_local.py`
3. Markets are open (not weekend)
4. FIX logs show `[OK] Order filled`
5. Sufficient margin in account

### No Telegram Notifications

**Check:**
1. `TELEGRAM_BOT_TOKEN` in `config.py` is correct
2. `TELEGRAM_CHAT_ID` in `config.py` is correct
3. Internet connection
4. Bot has been started with `/start` command in Telegram

---

## Expected Test Results

### Successful Full Test:
✅ Bot initializes FIX API
✅ Scans 15 symbols
✅ Generates 1-3 signals (depending on market conditions)
✅ Executes trades via FIX API
✅ Shows fill prices (e.g., 1.16008)
✅ Sends Telegram confirmations
✅ Trades visible in cTrader platform

### Time Required:
- **Single scan:** 2-3 minutes
- **Signal generation:** Varies (0-5 signals typical)
- **Order execution:** <1 second per order
- **Total test time:** 3-5 minutes

---

## Next Steps After Testing

1. **Review Results**
   - Check executed trades in cTrader
   - Verify Telegram notifications
   - Review FIX logs for errors

2. **Adjust Parameters** (if needed)
   - Increase/decrease `MIN_CONFLUENCE_SIGNALS`
   - Adjust `RISK_PER_TRADE_PERCENT`
   - Modify volatility thresholds

3. **Production Deployment**
   - Set `DRY_RUN_MODE = False`
   - Set `AUTO_TRADING_ENABLED = True`
   - Run continuously: `python main.py`
   - Monitor via Telegram and logs

4. **Monitor Performance**
   - Daily Telegram summaries
   - Check `fix_logs/` regularly
   - Review trade history in cTrader
   - Track P&L and win rate

---

## Safety Reminders

⚠️ **Before Running Live:**
- Test with small `DEFAULT_LOT_SIZE = 0.01`
- Verify `ACCOUNT_BALANCE` matches your actual balance
- Keep `RISK_PER_TRADE_PERCENT` at 1% or lower
- Test during demo mode first (`DRY_RUN_MODE = True`)
- Have sufficient margin in your account

⚠️ **Risk Management:**
- Bot will auto-stop if daily loss limit hit (5%)
- Bot will auto-stop if weekly loss limit hit (10%)
- Each trade risks only 1% of capital (configurable)
- Stop loss is always set on every trade

⚠️ **Monitoring:**
- Check Telegram regularly for notifications
- Monitor `fix_logs/` for errors
- Review daily summaries
- Keep bot running in background or screen session

---

## Quick Reference Commands

```bash
# Test once (recommended first test)
python main.py --test

# Run continuously
python main.py

# Check FIX logs (real-time)
tail -f fix_logs/fix_client_$(date +%Y%m%d).log

# Check specific log file
tail -50 fix_logs/fix_client_20251117.log

# Test order execution only
python test_order_simple.py

# Test FIX connection only
python test_fix_connection.py
```

---

## Support

If you encounter issues:
1. Check the logs in `fix_logs/`
2. Verify configuration in `config.py` and `fix_config_local.py`
3. Test individual components (connection, single symbol, etc.)
4. Review Telegram for error notifications
