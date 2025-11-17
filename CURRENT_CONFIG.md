# Current Configuration Summary

## Lot Size Settings

**All trades will execute with exactly 0.01 lots (1,000 units)**

### Configuration:
- `USE_FIXED_LOT_SIZE = True` in [config.py](config.py)
- `DEFAULT_LOT_SIZE = 0.01` in [config.py](config.py)

This means:
- **EURUSD 0.01 lots** = 1,000 EUR (~$1,160 position)
- **GBPUSD 0.01 lots** = 1,000 GBP (~$1,280 position)
- **XAUUSD 0.01 lots** = 1,000 oz (~$2,650 position if gold is at $2,650/oz)
- **BTCUSD 0.01 lots** = 1,000 BTC units

### Why Fixed Lot Size?

✅ **Consistent position sizing** - Every trade uses exactly 0.01 lots  
✅ **Low risk testing** - Small positions for testing the automation  
✅ **Predictable capital usage** - Know exactly how much each trade will use  
✅ **Demo account friendly** - Works well with small demo balances  

### To Change Lot Size:

**Option 1: Change the fixed lot size**
```python
# In config.py
DEFAULT_LOT_SIZE = 0.05  # Change from 0.01 to 0.05
```

**Option 2: Enable dynamic risk-based sizing**
```python
# In config.py
USE_FIXED_LOT_SIZE = False  # Enable dynamic calculation
```
When dynamic sizing is enabled, lot size will be calculated based on:
- Account balance
- Risk per trade (1%)
- Distance to stop loss

---

## FIX API Settings

### Connection:
- **Broker:** ICMarkets cTrader
- **Server:** demo-uk-eqx-01.p.c-trader.com:5202
- **Account:** 9648234 (demo)
- **Mode:** LIVE TRADING (DRY_RUN_MODE = False)

### Execution:
- **Auto Trading:** ENABLED (AUTO_TRADING_ENABLED = True)
- **Order Type:** Market orders
- **Confirmation:** Waits up to 10 seconds for fill confirmation
- **Reconnect:** Automatic on disconnect

---

## Trading Strategy Settings

### Symbols Monitored (15 total):
```
ETHUSD, BTCUSD, EURGBP, EURAUD, AUDUSD,
GBPUSD, XAUUSD, EURUSD, XTIUSD, USDCHF,
USDJPY, LTCUSD, NZDUSD, AUDCAD, XAGUSD
```

### Signal Requirements:
- **Minimum Confluence:** 2 signals must align
- **Volatility Range:** 0.3 - 3.0 ATR multiplier
- **Timeframe:** 1 hour candles
- **Update Interval:** Every 60 minutes

### Technical Indicators Used:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Support/Resistance levels
- Moving Averages (10 & 50 period)

---

## Risk Management

### Per Trade:
- **Risk:** 1% of account balance (if dynamic sizing enabled)
- **Fixed Lot:** 0.01 lots (current setting)
- **Stop Loss:** 1.5x ATR
- **Take Profit:** 3.0x ATR (1:2 Risk/Reward ratio)

### Account Limits:
- **Max Daily Loss:** 5% of account
- **Max Weekly Loss:** 10% of account
- **Account Balance:** $10,000 (configured)

When limits are hit, trading stops automatically.

---

## Test Results

### Lot Size Verification ✅
All trades confirmed to use 0.01 lots:
```
EURUSD  -> 0.01 lots
GBPUSD  -> 0.01 lots
XAUUSD  -> 0.01 lots
BTCUSD  -> 0.01 lots
XTIUSD  -> 0.01 lots
```

### Order Execution ✅
- Connection: Working
- Authentication: Working
- Order placement: Working
- Fill price capture: Working (e.g., 1.16008)
- Execution time: < 1 second

---

## How to Test

### Quick Test (Single Scan):
```bash
python test_automation.py
# OR
python main.py --test
```

### Test Single Symbol:
```bash
python main.py --symbol EURUSD
```

### Run Continuously:
```bash
python main.py
```

### Check Results:
1. **Terminal** - Real-time output
2. **Telegram** - Trade notifications  
3. **FIX Logs** - `fix_logs/fix_client_YYYYMMDD.log`
4. **cTrader** - Positions tab

---

## Important Notes

⚠️ **Current Status:**
- ✅ FIX API fully functional
- ✅ Order execution confirmed working
- ✅ Fill prices captured correctly
- ✅ All trades use 0.01 lots
- ⚠️ Full automation not yet tested (only manual order tests run)

📝 **Next Steps:**
1. Run `python test_automation.py` to test full system
2. Monitor first few trades closely
3. Check Telegram for notifications
4. Verify trades appear in cTrader platform

🔒 **Safety:**
- Demo account (no real money at risk)
- Small lot size (0.01 = minimal exposure)
- Stop losses always set
- Daily/weekly loss limits active

---

## Configuration Files

- **[config.py](config.py)** - Main trading configuration
- **[fix_config.py](fix_config.py)** - FIX API settings
- **[fix_config_local.py](fix_config_local.py)** - Local credentials (gitignored)
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Complete testing instructions

---

Last Updated: 2025-11-17
