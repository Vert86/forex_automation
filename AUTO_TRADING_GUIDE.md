# 🤖 Auto-Trading Guide - ICMarkets cTrader FIX API

Complete guide to enabling automatic order execution with your forex trading bot.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Getting FIX API Credentials](#getting-fix-api-credentials)
4. [Configuration](#configuration)
5. [Safety Features](#safety-features)
6. [Testing with Dry Run](#testing-with-dry-run)
7. [Going Live](#going-live)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The bot now supports **automatic trade execution** via FIX API (Financial Information eXchange protocol) with ICMarkets cTrader platform.

###  Modes:

1. **Signals Only** (Default):
   - Bot analyzes markets and sends Telegram alerts
   - You manually place trades in MT5/cTrader
   - ✅ Safe, recommended for beginners

2. **Auto-Trading** (Optional):
   - Bot automatically executes trades via FIX API
   - Orders sent directly to ICMarkets cTrader
   - ⚠️ Requires careful setup and monitoring

---

## Prerequisites

### 1. ICMarkets cTrader Account

- Live or Demo account with ICMarkets
- cTrader platform (not MT4/MT5)
- FIX API access enabled

### 2. Python Dependencies

Install the FIX protocol library:

```bash
pip install simplefix==1.0.16
```

Or reinstall all requirements:

```bash
pip install -r requirements-windows.txt
```

###  3. Understanding of FIX Protocol

- FIX is a real-time trading protocol
- Direct market access
- Professional-grade infrastructure
- Requires stable internet connection

---

## Getting FIX API Credentials

### Step 1: Log into ICMarkets cTrader

Visit: https://ct.icmarkets.com/ (for live) or demo platform

### Step 2: Enable FIX API

1. Go to **Settings** → **Profile** → **FIX API**
2. Click **Enable FIX API**
3. Accept the terms and conditions

### Step 3: Get Your Credentials

You'll need these 4 values:

| Field | Description | Example |
|-------|-------------|---------|
| **Sender Comp ID** | Your username/login | `demo.icmarkets.12345` |
| **Target Comp ID** | Server ID | `CSERVER` (usually this) |
| **Password** | FIX API password | Different from login password |
| **Account ID** | Trading account number | `12345678` |

**IMPORTANT:**
- FIX API password ≠ Login password
- Demo and Live accounts have different credentials
- Keep credentials secure!

### Step 4: Copy Credentials

Save these to `fix_config.py` (see Configuration section below)

---

## Configuration

### 1. Edit `fix_config.py`

Open the file and add your credentials:

```python
# FIX API Credentials
FIX_SENDER_COMP_ID = "demo.icmarkets.12345"  # Your username
FIX_TARGET_COMP_ID = "CSERVER"  # cTrader server
FIX_PASSWORD = "your_fix_api_password_here"  # FIX password
FIX_ACCOUNT_ID = "12345678"  # Your account number
```

### 2. Safety Configuration

```python
# Safety Controls
AUTO_TRADING_ENABLED = False  # Change to True to enable
DRY_RUN_MODE = True  # Test mode (change to False for real trades)
MAX_ORDERS_PER_DAY = 20  # Maximum orders per day
MAX_OPEN_POSITIONS = 5  # Maximum concurrent positions
REQUIRE_CONFIRMATION = True  # Manual confirmation for first trade
```

### 3. Risk Controls

```python
# Slippage Protection
MAX_SLIPPAGE_PIPS = 5  # Maximum allowed slippage
ENABLE_SLIPPAGE_PROTECTION = True
```

---

## Safety Features

The bot includes multiple safety layers:

### 1. **Dry Run Mode** (Default)

```python
DRY_RUN_MODE = True
```

- Logs orders but doesn't execute
- Perfect for testing
- No real money at risk
- ✅ **Always test here first!**

### 2. **Daily Order Limits**

```python
MAX_ORDERS_PER_DAY = 20
```

- Prevents excessive trading
- Resets at midnight
- Bot stops if limit reached

### 3. **Position Limits**

```python
MAX_OPEN_POSITIONS = 5
```

- Limits concurrent open trades
- Prevents overexposure
- Bot won't open new trades if max reached

### 4. **Confirmation Required**

```python
REQUIRE_CONFIRMATION = True
```

- First trade requires manual approval
- Set to `False` for fully autonomous trading
- Safety for initial deployment

### 5. **Volatility Filters**

Built into the bot:
- Rejects trades with volatility < 0.5%
- Rejects trades with volatility > 3.0%
- Only trades in optimal conditions

### 6. **Emergency Stop**

```python
EMERGENCY_CLOSE_ALL = True  # Set to True to close everything
```

- Emergency kill switch
- Closes all open positions
- Use if something goes wrong

---

## Testing with Dry Run

### Step 1: Enable Dry Run Mode

```python
# In fix_config.py
AUTO_TRADING_ENABLED = True  # Enable auto-trading
DRY_RUN_MODE = True  # BUT keep in test mode
```

### Step 2: Test Connection

```bash
python fix_client.py
```

**Expected output:**
```
Testing FIX Client...
Configuration:
  Host: h51.p.ctrader.com:5201
  Sender: demo.icmarkets.12345
  Account: 12345678
  Auto-Trading: ENABLED
  Dry Run Mode: ENABLED

✅ Successfully connected and logged in!
🧪 This is a test order (DRY RUN mode)
Order ID: DRY_RUN_1234567890
```

### Step 3: Test with Bot

```bash
python main.py --symbol EURUSD
```

Watch for:
```
🤖 Auto-trading mode: ENABLED
✅ FIX API connected successfully
🧪 DRY RUN: Would send BUY 0.01 lots of EURUSD
   SL: 1.04850, TP: 1.05300
```

### Step 4: Run for 24 Hours

```bash
python main.py
```

Monitor:
- Are signals being generated?
- Are "dry run" orders logged correctly?
- Is the FIX connection stable?
- Any errors in `fix_logs/` directory?

---

##  Going Live

### ⚠️ CRITICAL WARNING ⚠️

**Going live means REAL MONEY. Double-check everything!**

### Pre-Flight Checklist

- [ ] Tested in Dry Run mode for 24+ hours
- [ ] No errors in logs
- [ ] FIX connection is stable
- [ ] Using DEMO account first (not live!)
- [ ] Position sizing is correct
- [ ] Stop loss/take profit levels are reasonable
- [ ] Risk per trade is acceptable (1%)
- [ ] Daily loss limits are set
- [ ] Emergency stop is configured
- [ ] Telegram notifications working
- [ ] You understand the risks

### Step 1: Demo Account First

```python
# In fix_config.py
AUTO_TRADING_ENABLED = True
DRY_RUN_MODE = False  # Real execution
# But use DEMO account credentials!
```

### Step 2: Start with Minimum Size

```python
# In config.py
RISK_PER_TRADE_PERCENT = 0.5  # Even lower than default 1%
```

### Step 3: Start the Bot

```bash
python main.py
```

**You should see:**
```
🤖 Auto-trading mode: ENABLED
✅ FIX API connected successfully
🚨 LIVE TRADING MODE 🚨
```

**And in Telegram:**
```
🚨 ORDER EXECUTED 🚨
Mode: LIVE TRADING
Order ID: 123456789
Symbol: EURUSD
Direction: BUY
...
```

### Step 4: Monitor Closely

For the first week:
- Check every 2-4 hours
- Review all executed trades
- Monitor profit/loss
- Watch for any errors
- Be ready to shut down if needed

### Step 5: Going Live (Real Account)

Only after successful demo trading:

1. Get LIVE account FIX credentials
2. Update `fix_config.py` with live credentials
3. Start with smallest possible positions
4. Monitor 24/7 for first few days
5. Gradually increase position sizes

---

## Troubleshooting

### Connection Issues

**Problem:** `❌ Connection failed`

**Solutions:**
- Check internet connection
- Verify FIX_HOST and FIX_PORT are correct
- Check firewall isn't blocking port 5201
- Try different network (VPN might interfere)

### Authentication Issues

**Problem:** `❌ Login failed`

**Solutions:**
- Double-check FIX_SENDER_COMP_ID
- Verify FIX_PASSWORD (not login password!)
- Confirm FIX API is enabled in cTrader settings
- Check if using demo vs live credentials correctly

### Order Rejected

**Problem:** `Order execution failed`

**Solutions:**
- Check account has sufficient balance
- Verify symbol name is correct (use cTrader format)
- Check market is open
- Ensure lot size meets broker minimums
- Review cTrader order logs

### No Orders Executing

**Problem:** Bot generates signals but doesn't trade

**Check:**
```python
AUTO_TRADING_ENABLED = True  # Must be True
DRY_RUN_MODE = False  # Must be False for real trades
REQUIRE_CONFIRMATION = False  # Or manually approve first trade
```

### High Slippage

**Problem:** Orders executing far from expected price

**Solutions:**
- Enable slippage protection
- Reduce MAX_SLIPPAGE_PIPS
- Avoid trading during news events
- Use limit orders instead of market orders

---

## Files Overview

| File | Purpose |
|------|---------|
| `fix_config.py` | FIX API credentials and settings |
| `fix_client.py` | Low-level FIX protocol handler |
| `order_executor.py` | High-level order execution logic |
| `main.py` | Main bot (updated with FIX integration) |
| `fix_logs/` | Directory with FIX message logs |

---

## Command Reference

### Test FIX Connection
```bash
python fix_client.py
```

### Test Order Executor
```bash
python order_executor.py
```

### Run Bot (Signals Only)
```bash
# AUTO_TRADING_ENABLED = False in fix_config.py
python main.py
```

### Run Bot (Auto-Trading, Dry Run)
```bash
# AUTO_TRADING_ENABLED = True, DRY_RUN_MODE = True
python main.py
```

### Run Bot (Auto-Trading, LIVE)
```bash
# AUTO_TRADING_ENABLED = True, DRY_RUN_MODE = False
python main.py
```

---

## Best Practices

### 1. Start Conservative

- Use demo account
- Small position sizes
- Dry run first
- Monitor closely

### 2. Risk Management

- Never risk more than 1-2% per trade
- Set daily/weekly loss limits
- Respect position limits
- Use stop losses always

### 3. Monitoring

- Check bot daily
- Review trades weekly
- Monitor error logs
- Keep FIX logs for audit

### 4. Internet & Server

- Stable internet connection required
- Consider VPS for 24/7 operation
- Have backup connection ready
- Monitor connection drops

### 5. Emergency Procedures

- Know how to stop the bot (Ctrl+C)
- Have manual access to cTrader ready
- Set EMERGENCY_CLOSE_ALL if needed
- Keep broker support number handy

---

## FAQ

**Q: Can I use MT5 instead of cTrader?**
A: No, this FIX implementation is for cTrader only. MT5 has different API.

**Q: Is there a free demo?**
A: Yes! ICMarkets offers free cTrader demo accounts.

**Q: What's the difference between DRY_RUN and signals-only?**
A:
- Signals-only: No FIX connection, no order logic runs
- Dry run: FIX connected, orders logged but not sent to broker

**Q: Can I trade multiple accounts?**
A: Not simultaneously with one bot. You'd need multiple bot instances.

**Q: What if my internet disconnects?**
A: Bot will try to reconnect. Open positions remain on broker side. Consider VPS hosting.

**Q: How do I close all positions manually?**
A: Set `EMERGENCY_CLOSE_ALL = True` in fix_config.py and restart bot, or use cTrader platform.

---

## Support & Resources

- **ICMarkets Support:** https://www.icmarkets.com/support
- **cTrader FIX API Docs:** https://spotware.github.io/openapi/
- **FIX Protocol Specs:** https://www.fixtrading.org/

---

## Disclaimer

**IMPORTANT LEGAL DISCLAIMER:**

- Automated trading carries significant risk
- Past performance does not guarantee future results
- You can lose all your invested capital
- This software is provided "as is" without warranty
- The authors are not responsible for trading losses
- Always consult a licensed financial advisor
- Start with demo accounts and small positions
- Never trade with money you can't afford to lose

**YOU ARE FULLY RESPONSIBLE FOR YOUR TRADING DECISIONS**

---

**Ready to enable auto-trading? Follow the guide step-by-step and never skip the testing phase!** 🚀
