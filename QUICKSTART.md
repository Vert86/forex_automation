# Quick Start Guide

Get your Forex Trading Automation Bot running in 5 minutes!

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

If you get errors with `ta-lib`, you can skip it - the bot has fallback implementations.

## Step 2: Set Up Telegram Bot

1. Open Telegram and find `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy your bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
4. Start a chat with your new bot (send any message)
5. Get your chat ID by visiting:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
   Look for `"chat":{"id":123456789}` in the response

## Step 3: Configure the Bot

Open `config.py` and update these two lines:

```python
TELEGRAM_BOT_TOKEN = "paste_your_bot_token_here"
TELEGRAM_CHAT_ID = "paste_your_chat_id_here"
```

Also set your account balance:

```python
ACCOUNT_BALANCE = 10000  # Your actual account balance
```

## Step 4: Test the Bot

Run a test to make sure everything works:

```bash
python main.py --symbol EURUSD
```

You should see:
- Market data being fetched
- Indicators being calculated
- Signal analysis printed to console
- A Telegram message (if a signal is generated)

## Step 5: Run the Bot

Start the bot in continuous mode:

```bash
python main.py
```

The bot will:
- Scan all 15 symbols every 60 minutes
- Send you Telegram alerts when signals are found
- Show you complete trade details including:
  - Symbol, Direction (BUY/SELL)
  - Entry price
  - Stop loss and take profit (both price and pips)
  - Position size in lots
  - Risk/reward ratio
  - Confluence signals that triggered the trade

## What You'll Receive

When a signal is found, you'll get a Telegram message like:

```
🚨 FOREX TRADING SIGNAL 🚨

📊 Symbol: EURUSD
📈 Action: BUY
💰 Entry Price: 1.10000

📋 MT5 ORDER DETAILS:
Order Type: Market
Symbol: EURUSD
Direction: BUY
Quantity: 0.15 lots
Entry Price: 1.10000

🛡️ Stop Loss:
  Price: 1.09775
  Pips: 22.5

🎯 Take Profit:
  Price: 1.10450
  Pips: 45.0

⚖️ RISK MANAGEMENT:
Risk/Reward: 1:2.0
Risk Amount: $100.00
Potential Profit: $200.00
```

## Using the Signals in MT5

To place the trade in MT5 ICMarket:

1. Click "New Order" in MT5
2. Select "Market Execution"
3. Enter the details from the Telegram message:
   - Symbol: (from message)
   - Type: Buy/Sell (from message)
   - Volume: (Quantity in lots)
   - Stop Loss: (Price from message)
   - Take Profit: (Price from message)
4. Click "Buy" or "Sell"

## Customization

Want to adjust the bot's behavior? Edit `config.py`:

- **Scan frequency**: Change `UPDATE_INTERVAL` (default: 60 minutes)
- **Risk per trade**: Change `RISK_PER_TRADE_PERCENT` (default: 1%)
- **Timeframe**: Change `TIMEFRAME` (options: 1m, 5m, 15m, 30m, 1h, 4h, 1d)
- **Symbols**: Add/remove from `SYMBOLS` list
- **Signal sensitivity**: Change `MIN_CONFLUENCE_SIGNALS` (default: 2)

## Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

## Tips for Success

1. **Start with paper trading** - Test the signals on a demo account first
2. **Monitor the console** - Watch the analysis to understand why signals are generated
3. **Respect the signals** - The bot calculates position sizes based on your risk settings
4. **Don't override SL/TP** - They're calculated based on ATR and market structure
5. **Keep the bot running** - Consider using `screen` or running on a VPS for 24/7 operation

## Troubleshooting

**No signals?**
- This is normal! The bot requires confluence (2+ indicators agreeing)
- Try lowering `MIN_CONFLUENCE_SIGNALS` to 1 in config.py (not recommended for real trading)
- Wait longer - good setups don't happen every hour

**No Telegram messages?**
- Check your bot token and chat ID in config.py
- Make sure you started a chat with your bot
- Look for error messages in the console

**API errors?**
- Free API has limits (5 requests/min, 500/day)
- Reduce the number of symbols or increase scan interval
- The bot includes automatic delays to help with rate limits

## Getting Help

Check the full README.md for:
- Detailed installation instructions
- Complete feature documentation
- Advanced configuration options
- Running as a background service

---

**You're all set! Happy trading! 📈**
