"""
Technical Indicators Module
Implements ATR, Moving Averages, Support/Resistance, Fibonacci levels
"""

import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import config


class TechnicalIndicators:
    """Class to calculate various technical indicators"""

    @staticmethod
    def calculate_atr(df, period=14):
        """
        Calculate Average True Range (ATR)

        Args:
            df: DataFrame with high, low, close columns
            period: ATR period (default: 14)

        Returns:
            Series with ATR values
        """
        high = df['high']
        low = df['low']
        close = df['close']

        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # ATR is the moving average of True Range
        atr = tr.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_moving_averages(df, short_period=10, long_period=50):
        """
        Calculate Simple Moving Averages

        Args:
            df: DataFrame with close column
            short_period: Short MA period
            long_period: Long MA period

        Returns:
            Tuple of (short_ma, long_ma)
        """
        short_ma = df['close'].rolling(window=short_period).mean()
        long_ma = df['close'].rolling(window=long_period).mean()

        return short_ma, long_ma

    @staticmethod
    def calculate_ema(df, period=20):
        """
        Calculate Exponential Moving Average

        Args:
            df: DataFrame with close column
            period: EMA period

        Returns:
            Series with EMA values
        """
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def identify_swing_points(df, order=5):
        """
        Identify swing highs and swing lows

        Args:
            df: DataFrame with high and low columns
            order: Number of bars on each side to compare

        Returns:
            Tuple of (swing_highs_df, swing_lows_df)
        """
        # Find local maxima (swing highs)
        highs = df['high'].values
        swing_high_indices = argrelextrema(highs, np.greater, order=order)[0]

        # Find local minima (swing lows)
        lows = df['low'].values
        swing_low_indices = argrelextrema(lows, np.less, order=order)[0]

        swing_highs = df.iloc[swing_high_indices][['high']].copy()
        swing_highs['type'] = 'swing_high'

        swing_lows = df.iloc[swing_low_indices][['low']].copy()
        swing_lows['type'] = 'swing_low'

        return swing_highs, swing_lows

    @staticmethod
    def find_support_resistance(df, lookback=100, num_levels=3):
        """
        Find support and resistance levels

        Args:
            df: DataFrame with high, low, close columns
            lookback: Number of bars to look back
            num_levels: Number of S/R levels to identify

        Returns:
            Dict with support and resistance levels
        """
        df_recent = df.tail(lookback)

        # Identify swing points
        swing_highs, swing_lows = TechnicalIndicators.identify_swing_points(
            df_recent, order=config.SWING_THRESHOLD
        )

        # Get resistance levels from swing highs
        if len(swing_highs) > 0:
            resistance_levels = swing_highs['high'].nlargest(num_levels).tolist()
        else:
            resistance_levels = []

        # Get support levels from swing lows
        if len(swing_lows) > 0:
            support_levels = swing_lows['low'].nsmallest(num_levels).tolist()
        else:
            support_levels = []

        return {
            'support': sorted(support_levels),
            'resistance': sorted(resistance_levels, reverse=True)
        }

    @staticmethod
    def calculate_fibonacci_levels(df, lookback=100):
        """
        Calculate Fibonacci retracement and extension levels

        Args:
            df: DataFrame with high and low columns
            lookback: Number of bars to look back

        Returns:
            Dict with Fibonacci levels
        """
        df_recent = df.tail(lookback)

        # Find the highest high and lowest low
        highest_high = df_recent['high'].max()
        lowest_low = df_recent['low'].min()

        # Determine if trend is up or down
        if df_recent['close'].iloc[-1] > df_recent['close'].iloc[0]:
            # Uptrend: retracements from high
            trend = 'up'
            diff = highest_high - lowest_low
            retracement_levels = {
                f"fib_{level}": highest_high - (diff * level)
                for level in config.FIBONACCI_LEVELS
            }
            extension_levels = {
                f"ext_{level}": highest_high + (diff * (level - 1))
                for level in config.FIBONACCI_EXTENSIONS
            }
        else:
            # Downtrend: retracements from low
            trend = 'down'
            diff = highest_high - lowest_low
            retracement_levels = {
                f"fib_{level}": lowest_low + (diff * level)
                for level in config.FIBONACCI_LEVELS
            }
            extension_levels = {
                f"ext_{level}": lowest_low - (diff * (level - 1))
                for level in config.FIBONACCI_EXTENSIONS
            }

        return {
            'trend': trend,
            'high': highest_high,
            'low': lowest_low,
            'retracements': retracement_levels,
            'extensions': extension_levels
        }

    @staticmethod
    def calculate_rsi(df, period=14):
        """
        Calculate Relative Strength Index (RSI)

        Args:
            df: DataFrame with close column
            period: RSI period

        Returns:
            Series with RSI values
        """
        delta = df['close'].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with close column
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Dict with macd, signal, and histogram
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return {
            'macd': macd,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def detect_ma_crossover(short_ma, long_ma):
        """
        Detect Moving Average crossover

        Args:
            short_ma: Short period MA series
            long_ma: Long period MA series

        Returns:
            1 for bullish crossover, -1 for bearish crossover, 0 for no crossover
        """
        if len(short_ma) < 2 or len(long_ma) < 2:
            return 0

        # Current values
        short_current = short_ma.iloc[-1]
        long_current = long_ma.iloc[-1]

        # Previous values
        short_prev = short_ma.iloc[-2]
        long_prev = long_ma.iloc[-2]

        # Bullish crossover: short MA crosses above long MA
        if short_prev <= long_prev and short_current > long_current:
            return 1

        # Bearish crossover: short MA crosses below long MA
        if short_prev >= long_prev and short_current < long_current:
            return -1

        return 0

    @staticmethod
    def calculate_all_indicators(df):
        """
        Calculate all technical indicators for a DataFrame

        Args:
            df: DataFrame with OHLC data

        Returns:
            Dict with all calculated indicators
        """
        if df is None or len(df) < config.MA_LONG_PERIOD:
            return None

        # Calculate ATR
        atr = TechnicalIndicators.calculate_atr(df, config.ATR_PERIOD)

        # Calculate Moving Averages
        short_ma, long_ma = TechnicalIndicators.calculate_moving_averages(
            df, config.MA_SHORT_PERIOD, config.MA_LONG_PERIOD
        )

        # Detect MA Crossover
        ma_crossover = TechnicalIndicators.detect_ma_crossover(short_ma, long_ma)

        # Find Support/Resistance
        sr_levels = TechnicalIndicators.find_support_resistance(
            df, config.LOOKBACK_PERIOD, num_levels=3
        )

        # Calculate Fibonacci levels
        fib_levels = TechnicalIndicators.calculate_fibonacci_levels(
            df, config.LOOKBACK_PERIOD
        )

        # Calculate RSI
        rsi = TechnicalIndicators.calculate_rsi(df)

        # Calculate MACD
        macd_data = TechnicalIndicators.calculate_macd(df)

        return {
            'atr': atr.iloc[-1] if not atr.empty else None,
            'short_ma': short_ma.iloc[-1] if not short_ma.empty else None,
            'long_ma': long_ma.iloc[-1] if not long_ma.empty else None,
            'ma_crossover': ma_crossover,
            'support_levels': sr_levels['support'],
            'resistance_levels': sr_levels['resistance'],
            'fibonacci': fib_levels,
            'rsi': rsi.iloc[-1] if not rsi.empty else None,
            'macd': {
                'macd': macd_data['macd'].iloc[-1] if not macd_data['macd'].empty else None,
                'signal': macd_data['signal'].iloc[-1] if not macd_data['signal'].empty else None,
                'histogram': macd_data['histogram'].iloc[-1] if not macd_data['histogram'].empty else None
            },
            'current_price': df['close'].iloc[-1],
            'current_high': df['high'].iloc[-1],
            'current_low': df['low'].iloc[-1]
        }


if __name__ == "__main__":
    # Test indicators
    from data_ingestion import DataIngestion

    data_fetcher = DataIngestion()
    df = data_fetcher.get_market_data("EURUSD", interval="1h", bars=200)

    if df is not None:
        indicators = TechnicalIndicators.calculate_all_indicators(df)
        print("Calculated Indicators:")
        for key, value in indicators.items():
            print(f"{key}: {value}")
