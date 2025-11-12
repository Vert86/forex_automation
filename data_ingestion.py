"""
Data Ingestion Module
Handles fetching historical and real-time market data from various APIs
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import config


class DataIngestion:
    """Class to handle data fetching from multiple sources"""

    def __init__(self):
        self.alpha_vantage_key = config.ALPHA_VANTAGE_API_KEY
        self.fmp_key = config.FINANCIAL_MODELING_PREP_API_KEY
        self.taapi_secret = config.TAAPI_SECRET

    def get_forex_data_alpha_vantage(self, symbol, interval="60min", outputsize="compact"):
        """
        Fetch forex data from Alpha Vantage

        Args:
            symbol: Currency pair (e.g., "EURUSD")
            interval: Time interval (1min, 5min, 15min, 30min, 60min, daily, weekly, monthly)
            outputsize: compact (100 data points) or full (full-length time series)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert symbol format if needed (EURUSD -> EUR/USD)
            from_currency = symbol[:3]
            to_currency = symbol[3:6]

            # For intraday data
            if interval in ["1min", "5min", "15min", "30min", "60min"]:
                url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={from_currency}&to_symbol={to_currency}&interval={interval}&outputsize={outputsize}&apikey={self.alpha_vantage_key}"
                time_series_key = f"Time Series FX ({interval})"
            else:
                url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&outputsize={outputsize}&apikey={self.alpha_vantage_key}"
                time_series_key = "Time Series FX (Daily)"

            response = requests.get(url)
            data = response.json()

            if time_series_key not in data:
                print(f"Error fetching data for {symbol}: {data}")
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

            return df

        except Exception as e:
            print(f"Error in get_forex_data_alpha_vantage for {symbol}: {e}")
            return None

    def get_crypto_data_alpha_vantage(self, symbol, market="USD", interval="60min"):
        """
        Fetch cryptocurrency data from Alpha Vantage

        Args:
            symbol: Crypto symbol (e.g., "BTC", "ETH")
            market: Market currency (default: "USD")
            interval: Time interval

        Returns:
            DataFrame with OHLCV data
        """
        try:
            url = f"https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={symbol}&market={market}&interval={interval}&apikey={self.alpha_vantage_key}"

            response = requests.get(url)
            data = response.json()

            time_series_key = f"Time Series Crypto ({interval})"

            if time_series_key not in data:
                print(f"Error fetching crypto data for {symbol}: {data}")
                return None

            df = pd.DataFrame.from_dict(data[time_series_key], orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close',
                '5. volume': 'volume'
            })
            df = df.astype(float)
            df = df.sort_index()

            return df

        except Exception as e:
            print(f"Error in get_crypto_data_alpha_vantage for {symbol}: {e}")
            return None

    def get_taapi_indicator(self, symbol, indicator, interval="1h", exchange="forex"):
        """
        Fetch technical indicator from Taapi.io

        Args:
            symbol: Trading pair symbol
            indicator: Indicator name (e.g., "rsi", "atr", "macd")
            interval: Time interval
            exchange: Exchange name (forex, binance, etc.)

        Returns:
            Indicator value
        """
        try:
            # Convert symbol format for Taapi (EURUSD -> EUR/USD)
            if len(symbol) == 6 and exchange == "forex":
                formatted_symbol = f"{symbol[:3]}/{symbol[3:]}"
            else:
                formatted_symbol = symbol

            url = f"https://api.taapi.io/{indicator}"
            params = {
                "secret": self.taapi_secret,
                "exchange": exchange,
                "symbol": formatted_symbol,
                "interval": interval
            }

            response = requests.get(url, params=params)
            data = response.json()

            return data

        except Exception as e:
            print(f"Error in get_taapi_indicator for {symbol}: {e}")
            return None

    def get_market_data(self, symbol, interval="1h", bars=200):
        """
        Universal method to fetch market data for any symbol
        Automatically determines if it's forex, crypto, or commodity

        Args:
            symbol: Trading symbol
            interval: Time interval
            bars: Number of bars to fetch

        Returns:
            DataFrame with OHLCV data
        """
        # Determine asset type
        crypto_symbols = ["BTCUSD", "ETHUSD", "LTCUSD"]
        commodity_symbols = ["XAUUSD", "XAGUSD", "XTIUSD"]

        # Map interval format
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "1h": "60min",
            "4h": "60min",  # Alpha Vantage doesn't support 4h, use 1h
            "1d": "daily"
        }

        av_interval = interval_map.get(interval, "60min")
        outputsize = "full" if bars > 100 else "compact"

        if symbol in crypto_symbols:
            # Crypto data
            crypto_symbol = symbol[:3]  # BTC, ETH, LTC
            df = self.get_crypto_data_alpha_vantage(crypto_symbol, "USD", av_interval)
        elif symbol in commodity_symbols:
            # For commodities, use forex endpoint with special handling
            # XAU = Gold, XAG = Silver, XTI = Oil
            df = self.get_forex_data_alpha_vantage(symbol, av_interval, outputsize)
        else:
            # Forex data
            df = self.get_forex_data_alpha_vantage(symbol, av_interval, outputsize)

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

    print("\nTesting BTC data fetch...")
    df_btc = data_fetcher.get_market_data("BTCUSD", interval="1h", bars=50)
    if df_btc is not None:
        print(f"Fetched {len(df_btc)} bars")
        print(df_btc.tail())
