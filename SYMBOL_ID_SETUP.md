# How to Find cTrader Symbol IDs

## Problem
cTrader's FIX API requires **numeric symbol IDs** instead of symbol names like "EURUSD" or "XAUUSD". These IDs are **broker-specific**, meaning ICMarkets has different IDs than other brokers.

## How to Find Your Symbol IDs

### Method 1: Using cTrader Platform (Recommended)

1. Open your ICMarkets cTrader platform
2. Find the symbol you want to trade in the Market Watch
3. Right-click on the symbol → "Symbol Info" (or click the "i" icon)
4. In the Symbol Info window, scroll down until you find **"FIX Symbol ID"**
5. The number shown is your numeric ID for that symbol

### Method 2: Using FIX API Logs

1. Try to place an order with a symbol
2. Check the error message in `fix_logs/fix_client_YYYYMMDD.log`
3. The server will tell you what the symbol ID should be

## Update the Symbol Mapping

Once you have the symbol IDs, update the `SYMBOL_ID_MAP` dictionary in `fix_client.py`:

```python
SYMBOL_ID_MAP = {
    # Forex pairs
    'EURUSD': '1',  # Replace with actual ID from cTrader
    'GBPUSD': '2',  # Replace with actual ID from cTrader

    # Commodities
    'XAUUSD': '???',  # Find this in cTrader Symbol Info
    'XAGUSD': '???',  # Find this in cTrader Symbol Info
    'XTIUSD': '???',  # Find this in cTrader Symbol Info

    # Crypto
    'BTCUSD': '???',  # Find this in cTrader Symbol Info
    'ETHUSD': '???',  # Find this in cTrader Symbol Info
    'LTCUSD': '???',  # Find this in cTrader Symbol Info
}
```

## Example

If cTrader shows:
- EURUSD → FIX Symbol ID: 1
- XAUUSD → FIX Symbol ID: 45
- BTCUSD → FIX Symbol ID: 123

Update the mapping:
```python
SYMBOL_ID_MAP = {
    'EURUSD': '1',
    'XAUUSD': '45',
    'BTCUSD': '123',
}
```

## Important Notes

- Symbol IDs are **different for each broker**
- Symbol IDs might be **different for demo vs live accounts**
- You must update ALL symbols you plan to trade
- If a symbol is not in the mapping, orders will fail with "Symbol(55) must be numeric"
