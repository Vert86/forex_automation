"""
Configuration file for Forex Trading Automation
Contains API keys, trading parameters, and risk management settings
"""

# API Keys
ALPHA_VANTAGE_API_KEY = "5V6HYNTMB7EBLJQC"
FINANCIAL_MODELING_PREP_API_KEY = "BmvA6eJb4ElmfgwtxmcmWgC1rvnElmvy"
TAAPI_SECRET = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjhlNGY1ZWM4MDZmZjE2NTFlYmExMGYzIiwiaWF0IjoxNzU5ODM1NjI5LCJleHAiOjMzMjY0Mjk5NjI5fQ.X-lX8VCc1I13SKjJbx_tJxAthoAFVYELLlO9hf-Enbg"

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8413003232:AAGAIbyhqvowrueZEo63p2SUqsglk345dg8"
TELEGRAM_CHAT_ID = "990175094"

# Trading Symbols
SYMBOLS = [
    "ETHUSD", "BTCUSD", "EURGBP", "EURAUD", "AUDUSD",
    "GBPUSD", "XAUUSD", "EURUSD", "XTIUSD", "USDCHF",
    "USDJPY", "LTCUSD", "NZDUSD", "AUDCAD", "XAGUSD"
]

# Risk Management Parameters
RISK_PER_TRADE_PERCENT = 1.0  # Risk 1% of capital per trade
MAX_DAILY_LOSS_PERCENT = 5.0  # Stop trading if daily loss reaches 5%
MAX_WEEKLY_LOSS_PERCENT = 10.0  # Stop trading if weekly loss reaches 10%
ACCOUNT_BALANCE = 10000  # Default account balance (update as needed)

# ATR Parameters
ATR_PERIOD = 14
ATR_SL_MULTIPLIER = 1.5  # Stop loss at 1.5x ATR
ATR_TP_MULTIPLIER = 3.0  # Take profit at 3x ATR (1:2 R:R)

# Moving Average Parameters
MA_SHORT_PERIOD = 10
MA_LONG_PERIOD = 50

# Support/Resistance Parameters
LOOKBACK_PERIOD = 100  # Number of bars to look back for S/R levels
SWING_THRESHOLD = 5  # Number of bars on each side for swing high/low

# Fibonacci Levels
FIBONACCI_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
FIBONACCI_EXTENSIONS = [1.272, 1.618, 2.618]

# Time Frame
TIMEFRAME = "1h"  # Options: 1m, 5m, 15m, 30m, 1h, 4h, 1d

# Confluence Requirements (minimum number of signals needed)
MIN_CONFLUENCE_SIGNALS = 1  # Lowered from 2 to get more trades

# Trading Hours (24/7 for crypto, specific hours for forex)
TRADING_ENABLED = True

# Volatility Filter
MAX_VOLATILITY_THRESHOLD = 3.0  # Maximum ATR multiplier for volatility filter
MIN_VOLATILITY_THRESHOLD = 0.2  # Minimum ATR multiplier for volatility filter

# Position Sizing
USE_FIXED_LOT_SIZE = True  # If True, always use DEFAULT_LOT_SIZE instead of risk-based calculation
DEFAULT_LOT_SIZE = 0.01  # Fixed lot size when USE_FIXED_LOT_SIZE=True, or fallback if calculation fails
MIN_LOT_SIZE = 0.01
MAX_LOT_SIZE = 1.0

# Symbol-specific lot sizes (overrides DEFAULT_LOT_SIZE for specific symbols)
# Used when USE_FIXED_LOT_SIZE = True
SYMBOL_LOT_SIZES = {
    'BTCUSD': 0.00001,  # Max 10 units for BTC (broker limit)
    'ETHUSD': 0.00001,  # Max 10 units for ETH (broker limit)
    'LTCUSD': 0.0001,   # Litecoin - smaller size
    # Forex and commodities will use DEFAULT_LOT_SIZE (0.01)
}

# Update Interval (in minutes)
UPDATE_INTERVAL = 60  # Check for signals every 60 minutes

# Backtesting Parameters
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2024-12-31"
