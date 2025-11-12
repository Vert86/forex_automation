# Forex Trading Automation Bot

A sophisticated automated forex trading system that analyzes market data, generates trading signals based on confluence of multiple technical indicators, and sends detailed trade recommendations via Telegram.

## Features

- **Multi-Indicator Analysis**: Combines ATR, Moving Averages, Support/Resistance, Fibonacci levels, RSI, and MACD
- **Confluence-Based Signals**: Only generates signals when multiple indicators agree
- **Dynamic Risk Management**: Calculates optimal position sizes, stop loss, and take profit levels
- **ATR-Based SL/TP**: Uses Average True Range for volatility-adjusted stop loss and take profit
- **Support/Resistance Detection**: Automatically identifies key market levels
- **Telegram Notifications**: Sends formatted trading signals with complete order details
- **Risk Controls**: Daily and weekly loss limits, position sizing, volatility filters
- **Multi-Symbol Support**: Monitors 15+ forex pairs, crypto, and commodities

## Trading Methodology

The bot implements a robust trading methodology based on:

1. **Volatility Analysis (ATR)**: Stop loss at 1.5-2x ATR, Take profit maintains 1:2+ R:R ratio
2. **Market Structure**: Places SL/TP at logical support/resistance levels
3. **Fibonacci Levels**: Identifies potential reversal and extension points
4. **Moving Average Crossovers**: 10/50 period MA for trend identification
5. **Confluence Trading**: Requires minimum 2 confirming signals before generating trade
6. **Risk Management**: Risks only 1% of capital per trade, max 5% daily loss

## Symbols Monitored

- **Forex**: EURUSD, GBPUSD, USDJPY, USDCHF, AUDUSD, NZDUSD, EURGBP, EURAUD, AUDCAD
- **Crypto**: BTCUSD, ETHUSD, LTCUSD
- **Commodities**: XAUUSD (Gold), XAGUSD (Silver), XTIUSD (Oil)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Telegram account (for notifications)

### Step 1: Clone or Download

```bash
cd /home/user/forex_automation
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Note: If you encounter issues with `ta-lib`, install it using:

**On Ubuntu/Debian:**
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

**On macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**On Windows:**
Download the appropriate wheel file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib) and install it.

If TA-Lib installation fails, the bot will still work using pure Python implementations.

### Step 3: Configure Telegram Bot

1. **Create a Telegram Bot:**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Copy the bot token provided

2. **Get Your Chat ID:**
   - Start a chat with your new bot
   - Send any message to the bot
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your `chat_id` in the response

3. **Update Configuration:**
   Open `config.py` and add your Telegram credentials:
   ```python
   TELEGRAM_BOT_TOKEN = "your_bot_token_here"
   TELEGRAM_CHAT_ID = "990175094"  # Your chat ID
   ```

### Step 4: Configure Account Settings

Edit `config.py` to set your account balance and risk preferences:

```python
ACCOUNT_BALANCE = 10000  # Your account balance
RISK_PER_TRADE_PERCENT = 1.0  # Risk 1% per trade
MAX_DAILY_LOSS_PERCENT = 5.0  # Max 5% daily loss
```

## Usage

### Run the Bot Continuously

```bash
python main.py
```

The bot will:
- Scan all symbols every 60 minutes (configurable)
- Send Telegram notifications when signals are found
- Continue running 24/7 until stopped (Ctrl+C)

### Test Mode (Single Scan)

```bash
python main.py --test
```

Runs one complete scan of all symbols and exits.

### Test Single Symbol

```bash
python main.py --symbol EURUSD
```

Analyzes a single symbol and generates signal if conditions are met.

## Signal Format

When a trading opportunity is found, you'll receive a Telegram message with:

```
🚨 FOREX TRADING SIGNAL 🚨
━━━━━━━━━━━━━━━━━━━━━━

📊 Symbol: EURUSD
📈 Action: BUY
💰 Entry Price: 1.10000

📋 MT5 ORDER DETAILS:
━━━━━━━━━━━━━━━━━━━━━━
Order Type: Market
Symbol: EURUSD
Direction: BUY
Quantity: 0.15 lots
Entry Price: 1.10000

🛡️ Stop Loss:
  Price: 1.09775
  Pips: 22.5
  Trailing SL: Disable

🎯 Take Profit:
  Price: 1.10450
  Pips: 45.0

⚖️ RISK MANAGEMENT:
━━━━━━━━━━━━━━━━━━━━━━
Risk/Reward: 1:2.0
Risk Amount: $100.00
Potential Profit: $200.00
ATR: 0.00150

🎲 CONFLUENCE SIGNALS (3):
━━━━━━━━━━━━━━━━━━━━━━
1. MA Crossover:
   Bullish MA crossover: 1.10050 > 1.09980
2. Support Resistance:
   Price near support level: 1.09950
3. Trend:
   Strong uptrend: Price > MA10 > MA50

⏰ Time: 2025-01-15 14:30:00
━━━━━━━━━━━━━━━━━━━━━━
Volatility: Volatility acceptable: 1.36%
```

## Configuration Options

All settings can be adjusted in `config.py`:

### Risk Management
```python
RISK_PER_TRADE_PERCENT = 1.0      # Risk per trade (%)
MAX_DAILY_LOSS_PERCENT = 5.0      # Max daily loss (%)
MAX_WEEKLY_LOSS_PERCENT = 10.0    # Max weekly loss (%)
ACCOUNT_BALANCE = 10000           # Account balance
```

### Technical Indicators
```python
ATR_PERIOD = 14                   # ATR calculation period
ATR_SL_MULTIPLIER = 1.5          # Stop loss distance (x ATR)
ATR_TP_MULTIPLIER = 3.0          # Take profit distance (x ATR)
MA_SHORT_PERIOD = 10             # Short MA period
MA_LONG_PERIOD = 50              # Long MA period
```

### Trading Parameters
```python
TIMEFRAME = "1h"                  # Chart timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
MIN_CONFLUENCE_SIGNALS = 2        # Minimum signals required
UPDATE_INTERVAL = 60              # Scan interval (minutes)
```

## Project Structure

```
forex_automation/
├── main.py                    # Main bot orchestrator
├── config.py                  # Configuration settings
├── data_ingestion.py         # Market data fetching
├── indicators.py             # Technical indicators
├── strategy.py               # Signal generation logic
├── risk_management.py        # Position sizing & SL/TP
├── telegram_notifier.py      # Telegram notifications
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── Forex Automation.pdf      # Trading methodology documentation
```

## API Keys

The bot uses the following APIs (already configured):

- **Alpha Vantage**: For forex and crypto market data
- **Financial Modeling Prep**: Backup data source
- **Taapi**: For technical indicators (optional)

API keys are pre-configured in `config.py`. Free tier limits apply:
- Alpha Vantage: 5 requests per minute, 500 per day
- Due to rate limits, the bot includes 2-second delays between symbol scans

## How It Works

1. **Data Collection**: Fetches recent OHLC data for each symbol
2. **Indicator Calculation**: Computes ATR, MAs, RSI, MACD, S/R levels, Fibonacci
3. **Signal Generation**: Analyzes indicators for confluence
4. **Risk Calculation**: Determines position size, SL, and TP based on ATR and market structure
5. **Notification**: Sends formatted signal to Telegram with complete trade details
6. **Repeat**: Scans again after configured interval

## Risk Warning

**IMPORTANT**: This is an automated trading signal generator. While it uses sophisticated analysis:

- Past performance does not guarantee future results
- Always verify signals manually before placing trades
- Start with small position sizes
- Use a demo account first to test the system
- Never risk more than you can afford to lose
- The bot generates signals only - YOU must execute trades manually

## Troubleshooting

### No Telegram messages received
- Verify `TELEGRAM_BOT_TOKEN` is correct in `config.py`
- Verify `TELEGRAM_CHAT_ID` is correct
- Make sure you've started a conversation with your bot
- Check console output for error messages

### API Rate Limit Errors
- The free Alpha Vantage API has limits (5 req/min, 500/day)
- Reduce the number of symbols in `SYMBOLS` list
- Increase `UPDATE_INTERVAL` to scan less frequently
- Consider upgrading to a paid API plan

### Insufficient Data Errors
- Some symbols may not be available via Alpha Vantage
- Try a different timeframe
- Check symbol format (should be like "EURUSD", not "EUR/USD")

### TA-Lib Installation Issues
- The bot uses pure Python implementations as fallback
- TA-Lib is optional but recommended for performance
- See installation instructions above for your platform

## Advanced Usage

### Running as a Background Service

**Using screen (Linux):**
```bash
screen -S forex_bot
python main.py
# Press Ctrl+A then D to detach
# Reconnect with: screen -r forex_bot
```

**Using systemd (Linux):**
Create `/etc/systemd/system/forex-bot.service`:
```ini
[Unit]
Description=Forex Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/user/forex_automation
ExecStart=/usr/bin/python3 /home/user/forex_automation/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable forex-bot
sudo systemctl start forex-bot
sudo systemctl status forex-bot
```

### Customizing Trading Strategy

Edit `strategy.py` to modify signal generation logic:
- Add new indicator analysis functions
- Adjust confluence requirements
- Modify signal strength calculations
- Add custom filters

## Support

For issues, questions, or improvements:
- Check console output for error messages
- Review configuration settings
- Verify API keys and Telegram credentials
- Test with a single symbol first using `--symbol` flag

## License

This project is for educational and personal use only. Use at your own risk.

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any financial losses incurred from using this software. Always consult with a licensed financial advisor before making trading decisions.

---

**Happy Trading! 📈💰**
