"""
Data Ingestion Module
Handles fetching historical and real-time market data from various APIs
Now uses Yahoo Finance (completely FREE, no API key needed) as primary source
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import config

# Try to import yfinance (free data source)
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance not installed. Install with: pip install yfinance")


class DataIngestion:
    """Class to handle data fetching from multiple sources"""

    def __init__(self):
        self.alpha_vantage_key = config.ALPHA_VANTAGE_API_KEY
        self.fmp_key = config.FINANCIAL_MODELING_PREP_API_KEY
        self.taapi_secret = config.TAAPI_SECRET
        self.use_yfinance = YFINANCE_AVAILABLE

    def get_data_yahoo_finance(self, symbol, interval="1h", bars=200):
        """
        Fetch market data from Yahoo Finance (FREE, no API key needed)

        Args:
            symbol: Trading symbol (will be converted to Yahoo format)
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 1d)
            bars: Number of bars to fetch

        Returns:
            DataFrame with OHLCV data
        """
        if not YFINANCE_AVAILABLE:
            return None

        try:
            # Convert symbol to Yahoo Finance format
            yahoo_symbol = self._convert_to_yahoo_symbol(symbol)

            if yahoo_symbol is None:
                print(f"⚠️  Symbol {symbol} not supported by Yahoo Finance")
                return None

            # Map interval to Yahoo Finance format
            interval_map = {
                "1m": "1m",
                "5m": "5m",
                "15m": "15m",
                "30m": "30m",
                "1h": "1h",
                "4h": "1h",  # Yahoo doesn't have 4h, use 1h
                "1d": "1d"
            }
            yf_interval = interval_map.get(interval, "1h")

            # Calculate period based on interval and bars needed
            period_map = {
                "1m": f"{bars}m",  # minutes
                "5m": f"{int(bars * 5 / 60 / 24) + 1}d",  # days
                "15m": f"{int(bars * 15 / 60 / 24) + 1}d",
                "30m": f"{int(bars * 30 / 60 / 24) + 1}d",
                "1h": f"{int(bars / 24) + 5}d",
                "1d": f"{bars}d"
            }

            # Use appropriate period or max available
            if yf_interval in ["1m", "5m"]:
                period = "7d"  # Yahoo limits intraday data to 7 days
            elif yf_interval in ["15m", "30m"]:
                period = "60d"
            elif yf_interval == "1h":
                period = "730d"  # 2 years
            else:
                period = "max"

            # Fetch data
            ticker = yf.Ticker(yahoo_symbol)
            df = ticker.history(period=period, interval=yf_interval)

            if df.empty:
                print(f"⚠️  No data returned for {symbol} ({yahoo_symbol})")
                return None

            # Rename columns to match our format
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })

            # Select required columns
            df = df[['open', 'high', 'low', 'close']].copy()

            # Get last N bars
            if len(df) > bars:
                df = df.tail(bars)

            print(f"✅ Fetched {len(df)} bars for {symbol} from Yahoo Finance")
            return df

        except Exception as e:
            print(f"❌ Error fetching Yahoo Finance data for {symbol}: {e}")
            return None

    def _convert_to_yahoo_symbol(self, symbol):
        """
        Convert trading symbol to Yahoo Finance format

        Args:
            symbol: Our symbol format (e.g., "EURUSD", "BTCUSD", "XAUUSD")

        Returns:
            Yahoo Finance symbol or None if not supported
        """
        # Forex pairs
        forex_map = {
            "EURUSD": "EURUSD=X",
            "GBPUSD": "GBPUSD=X",
            "USDJPY": "USDJPY=X",
            "USDCHF": "USDCHF=X",
            "AUDUSD": "AUDUSD=X",
            "NZDUSD": "NZDUSD=X",
            "USDCAD": "USDCAD=X",
            "EURGBP": "EURGBP=X",
            "EURJPY": "EURJPY=X",
            "EURAUD": "EURAUD=X",
            "GBPJPY": "GBPJPY=X",
            "AUDCAD": "AUDCAD=X",
            "AUDCHF": "AUDCHF=X",
            "AUDJPY": "AUDJPY=X",
            "AUDNZD": "AUDNZD=X",
            "CADCHF": "CADCHF=X",
            "CADJPY": "CADJPY=X",
            "CHFJPY": "CHFJPY=X",
            "EURCHF": "EURCHF=X",
            "GBPAUD": "GBPAUD=X",
            "GBPCAD": "GBPCAD=X",
            "GBPCHF": "GBPCHF=X",
            "GBPNZD": "GBPNZD=X",
            "NZDCAD": "NZDCAD=X",
            "NZDCHF": "NZDCHF=X",
            "NZDJPY": "NZDJPY=X"
        }

        # Crypto
        crypto_map = {
            "BTCUSD": "BTC-USD",
            "ETHUSD": "ETH-USD",
            "LTCUSD": "LTC-USD",
            "XRPUSD": "XRP-USD",
            "ADAUSD": "ADA-USD",
            "DOGEUSD": "DOGE-USD"
        }

        # Commodities
        commodity_map = {
            "XAUUSD": "GC=F",   # Gold futures
            "XAGUSD": "SI=F",   # Silver futures
            "XTIUSD": "CL=F"    # Crude Oil futures
        }

        # Check all maps
        if symbol in forex_map:
            return forex_map[symbol]
        elif symbol in crypto_map:
            return crypto_map[symbol]
        elif symbol in commodity_map:
            return commodity_map[symbol]
        else:
            return None

    def get_forex_data_alpha_vantage(self, symbol, interval="daily", outputsize="compact"):
        """
        Fetch forex data from Alpha Vantage (FREE tier only supports daily data)

        Args:
            symbol: Currency pair (e.g., "EURUSD")
            interval: Time interval (only "daily" is free)
            outputsize: compact (100 data points) or full (full-length time series)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert symbol format if needed (EURUSD -> EUR/USD)
            from_currency = symbol[:3]
            to_currency = symbol[3:6]

            # Free tier only supports FX_DAILY
            url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&outputsize={outputsize}&apikey={self.alpha_vantage_key}"
            time_series_key = "Time Series FX (Daily)"

            response = requests.get(url)
            data = response.json()

            if time_series_key not in data:
                print(f"❌ Alpha Vantage error for {symbol}: {data.get('Information', data.get('Error Message', 'Unknown error'))}")
                return None

            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
            })
            df = df.astype(float)
            df = df.sort_index()

            print(f"✅ Fetched {len(df)} bars for {symbol} from Alpha Vantage (daily)")
            return df

        except Exception as e:
            print(f"❌ Error in Alpha Vantage for {symbol}: {e}")
            return None

    def get_market_data(self, symbol, interval="1h", bars=200):
        """
        Universal method to fetch market data for any symbol
        Uses Yahoo Finance (FREE) as primary source

        Args:
            symbol: Trading symbol
            interval: Time interval
            bars: Number of bars to fetch

        Returns:
            DataFrame with OHLCV data
        """
        # Try Yahoo Finance first (free and reliable)
        if self.use_yfinance:
            df = self.get_data_yahoo_finance(symbol, interval, bars)
            if df is not None and len(df) >= 50:  # Need at least 50 bars for indicators
                return df
            else:
                print(f"⚠️  Yahoo Finance data insufficient, trying fallback...")

        # Fallback to Alpha Vantage (free tier = daily only)
        print(f"ℹ️  Using Alpha Vantage daily data as fallback for {symbol}")
        df = self.get_forex_data_alpha_vantage(symbol, "daily", "full")

        if df is not None and len(df) > bars:
            df = df.tail(bars)

        return df

    def get_current_price(self, symbol):
        """
        Get current price for a symbol

        Args:
            symbol: Trading symbol

        Returns:
            Current price (float)
        """
        df = self.get_market_data(symbol, bars=1)
        if df is not None and len(df) > 0:
            return df['close'].iloc[-1]
        return None


if __name__ == "__main__":
    # Test the data ingestion
    data_fetcher = DataIngestion()

    print("Testing EURUSD data fetch...")
    df = data_fetcher.get_market_data("EURUSD", interval="1h", bars=50)
    if df is not None:
        print(f"Fetched {len(df)} bars")
        print(df.tail())
    else:
        print("Failed to fetch data")

    print("\n" + "="*60)
    print("Testing BTC data fetch...")
    df_btc = data_fetcher.get_market_data("BTCUSD", interval="1h", bars=50)
    if df_btc is not None:
        print(f"Fetched {len(df_btc)} bars")
        print(df_btc.tail())
    else:
        print("Failed to fetch data")
