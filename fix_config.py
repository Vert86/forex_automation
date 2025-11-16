"""
ICMarkets cTrader FIX API Configuration
Add your FIX API credentials here
"""

# ========================================
# FIX API Configuration for ICMarkets cTrader
# ========================================

# Enable/Disable Automatic Trading
AUTO_TRADING_ENABLED = False  # SET TO True TO ENABLE AUTO-TRADING (start with False for safety!)

# FIX API Connection Details - ICMarkets Demo Account
FIX_HOST = "demo-uk-eqx-01.p.c-trader.com"  # ICMarkets UK Demo server
FIX_PORT = 5202  # Plain text connection (5212 for SSL)

# FIX API Credentials - YOUR DEMO ACCOUNT
FIX_SENDER_COMP_ID = "demo.icmarkets.9648234"  # Your demo account sender ID
FIX_TARGET_COMP_ID = "CSERVER"  # cTrader FIX server ID (MUST be uppercase per cTrader spec)
FIX_PASSWORD = "MkSPxC#Vej4Kq$m"  # FIX API password for account 9648234
FIX_ACCOUNT_ID = "9648234"  # Your demo account number
FIX_SENDER_SUB_ID = "TRADE"  # Trade connection (use "QUOTE" for price feed)

# FIX Protocol Version
FIX_VERSION = "FIX.4.4"  # cTrader uses FIX 4.4

# Order Execution Settings
DEFAULT_ORDER_TYPE = "MARKET"  # MARKET, LIMIT, STOP
DEFAULT_TIME_IN_FORCE = "GTC"  # GTC (Good Till Cancel), IOC (Immediate or Cancel), FOK (Fill or Kill)

# Safety Controls
MAX_ORDERS_PER_DAY = 20  # Maximum orders per day
MAX_OPEN_POSITIONS = 5  # Maximum concurrent open positions
REQUIRE_CONFIRMATION = True  # Require manual confirmation before first trade
DRY_RUN_MODE = True  # Test mode - logs orders but doesn't execute (DISABLE FOR REAL TRADING)

# Order Execution Delays
ORDER_RETRY_ATTEMPTS = 3  # Number of retry attempts for failed orders
ORDER_RETRY_DELAY = 2  # Seconds between retries
ORDER_TIMEOUT = 30  # Seconds to wait for order confirmation

# Slippage Protection
MAX_SLIPPAGE_PIPS = 5  # Maximum allowed slippage in pips
ENABLE_SLIPPAGE_PROTECTION = True

# Emergency Controls
EMERGENCY_CLOSE_ALL = False  # Set to True to close all positions immediately
TRADING_HOURS_CHECK = True  # Only trade during market hours

# Logging
FIX_LOG_DIRECTORY = "fix_logs"  # Directory for FIX protocol logs
ENABLE_FIX_LOGGING = True  # Log all FIX messages for debugging

# ========================================
# How to Get Your FIX API Credentials
# ========================================
"""
1. Log into your ICMarkets cTrader account
2. Go to Settings/Profile → FIX API
3. Enable FIX API access
4. Copy your credentials:
   - Sender Comp ID (usually your account username)
   - Password (FIX API specific password, not your login password)
   - Account ID (your trading account number)

5. For DEMO account, credentials are different from LIVE
   - Always test on DEMO first!

6. Update this config file with your credentials
7. Set AUTO_TRADING_ENABLED = True when ready
8. Set DRY_RUN_MODE = False for real execution

IMPORTANT SAFETY:
- Start with DRY_RUN_MODE = True to test without real trades
- Use DEMO account first
- Start with small positions
- Monitor the bot closely for the first few days
"""
