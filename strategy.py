"""
Strategy Logic Module
Generates trading signals based on confluence of multiple indicators
"""

import config
from indicators import TechnicalIndicators


class TradingStrategy:
    """Class to generate trading signals based on confluence"""

    def __init__(self):
        self.min_confluence = config.MIN_CONFLUENCE_SIGNALS

    def analyze_ma_crossover_signal(self, indicators):
        """
        Analyze Moving Average crossover signal

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        ma_crossover = indicators.get('ma_crossover', 0)

        if ma_crossover == 1:
            return {
                'signal': 'BUY',
                'strength': 1,
                'reason': f"Bullish MA crossover: {indicators['short_ma']:.5f} > {indicators['long_ma']:.5f}"
            }
        elif ma_crossover == -1:
            return {
                'signal': 'SELL',
                'strength': 1,
                'reason': f"Bearish MA crossover: {indicators['short_ma']:.5f} < {indicators['long_ma']:.5f}"
            }

        return {'signal': None, 'strength': 0, 'reason': 'No MA crossover'}

    def analyze_support_resistance_signal(self, indicators):
        """
        Analyze price action at support/resistance levels

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        current_price = indicators['current_price']
        support_levels = indicators['support_levels']
        resistance_levels = indicators['resistance_levels']

        # Check if price is near support (potential bounce/buy)
        for support in support_levels:
            price_diff_pct = abs(current_price - support) / current_price * 100
            if price_diff_pct < 0.5:  # Within 0.5% of support
                return {
                    'signal': 'BUY',
                    'strength': 1,
                    'reason': f"Price near support level: {support:.5f}"
                }

        # Check if price is near resistance (potential rejection/sell)
        for resistance in resistance_levels:
            price_diff_pct = abs(current_price - resistance) / current_price * 100
            if price_diff_pct < 0.5:  # Within 0.5% of resistance
                return {
                    'signal': 'SELL',
                    'strength': 1,
                    'reason': f"Price near resistance level: {resistance:.5f}"
                }

        return {'signal': None, 'strength': 0, 'reason': 'No S/R signal'}

    def analyze_fibonacci_signal(self, indicators):
        """
        Analyze price action at Fibonacci levels

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        current_price = indicators['current_price']
        fib = indicators['fibonacci']

        # Check if price is near a key Fibonacci retracement level
        for level_name, level_price in fib['retracements'].items():
            price_diff_pct = abs(current_price - level_price) / current_price * 100
            if price_diff_pct < 0.5:  # Within 0.5% of Fib level
                # If uptrend, Fib retracement can be a buy signal
                if fib['trend'] == 'up':
                    return {
                        'signal': 'BUY',
                        'strength': 1,
                        'reason': f"Price at Fib {level_name} in uptrend: {level_price:.5f}"
                    }
                else:
                    return {
                        'signal': 'SELL',
                        'strength': 1,
                        'reason': f"Price at Fib {level_name} in downtrend: {level_price:.5f}"
                    }

        return {'signal': None, 'strength': 0, 'reason': 'No Fibonacci signal'}

    def analyze_rsi_signal(self, indicators):
        """
        Analyze RSI for overbought/oversold conditions

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        rsi = indicators.get('rsi')

        if rsi is None:
            return {'signal': None, 'strength': 0, 'reason': 'RSI not available'}

        if rsi < 30:
            return {
                'signal': 'BUY',
                'strength': 1,
                'reason': f"RSI oversold: {rsi:.2f}"
            }
        elif rsi > 70:
            return {
                'signal': 'SELL',
                'strength': 1,
                'reason': f"RSI overbought: {rsi:.2f}"
            }

        return {'signal': None, 'strength': 0, 'reason': f'RSI neutral: {rsi:.2f}'}

    def analyze_macd_signal(self, indicators):
        """
        Analyze MACD for trend confirmation

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        macd_data = indicators.get('macd', {})
        macd = macd_data.get('macd')
        signal = macd_data.get('signal')
        histogram = macd_data.get('histogram')

        if macd is None or signal is None:
            return {'signal': None, 'strength': 0, 'reason': 'MACD not available'}

        # Bullish: MACD above signal line and histogram positive
        if macd > signal and histogram > 0:
            return {
                'signal': 'BUY',
                'strength': 1,
                'reason': f"MACD bullish: {macd:.5f} > {signal:.5f}"
            }
        # Bearish: MACD below signal line and histogram negative
        elif macd < signal and histogram < 0:
            return {
                'signal': 'SELL',
                'strength': 1,
                'reason': f"MACD bearish: {macd:.5f} < {signal:.5f}"
            }

        return {'signal': None, 'strength': 0, 'reason': 'MACD neutral'}

    def analyze_trend_signal(self, indicators):
        """
        Analyze overall trend based on MAs

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with signal details
        """
        short_ma = indicators.get('short_ma')
        long_ma = indicators.get('long_ma')
        current_price = indicators.get('current_price')

        if short_ma is None or long_ma is None:
            return {'signal': None, 'strength': 0, 'reason': 'MA not available'}

        # Strong uptrend: price above both MAs and short MA above long MA
        if current_price > short_ma > long_ma:
            return {
                'signal': 'BUY',
                'strength': 1,
                'reason': f"Strong uptrend: Price {current_price:.5f} > MA{config.MA_SHORT_PERIOD} > MA{config.MA_LONG_PERIOD}"
            }
        # Strong downtrend: price below both MAs and short MA below long MA
        elif current_price < short_ma < long_ma:
            return {
                'signal': 'SELL',
                'strength': 1,
                'reason': f"Strong downtrend: Price {current_price:.5f} < MA{config.MA_SHORT_PERIOD} < MA{config.MA_LONG_PERIOD}"
            }

        return {'signal': None, 'strength': 0, 'reason': 'No clear trend'}

    def generate_signal(self, indicators):
        """
        Generate trading signal based on confluence of multiple indicators

        Args:
            indicators: Dict of calculated indicators

        Returns:
            Dict with trading signal and details
        """
        if indicators is None:
            return None

        # Analyze all signals
        signals = {
            'ma_crossover': self.analyze_ma_crossover_signal(indicators),
            'support_resistance': self.analyze_support_resistance_signal(indicators),
            'fibonacci': self.analyze_fibonacci_signal(indicators),
            'rsi': self.analyze_rsi_signal(indicators),
            'macd': self.analyze_macd_signal(indicators),
            'trend': self.analyze_trend_signal(indicators)
        }

        # Count BUY and SELL signals
        buy_signals = []
        sell_signals = []

        for signal_name, signal_data in signals.items():
            if signal_data['signal'] == 'BUY':
                buy_signals.append({
                    'name': signal_name,
                    'reason': signal_data['reason'],
                    'strength': signal_data['strength']
                })
            elif signal_data['signal'] == 'SELL':
                sell_signals.append({
                    'name': signal_name,
                    'reason': signal_data['reason'],
                    'strength': signal_data['strength']
                })

        # Calculate total strength
        buy_strength = sum(s['strength'] for s in buy_signals)
        sell_strength = sum(s['strength'] for s in sell_signals)

        # Determine final signal based on confluence
        if buy_strength >= self.min_confluence and buy_strength > sell_strength:
            return {
                'action': 'BUY',
                'confidence': buy_strength,
                'signals': buy_signals,
                'total_signals': len(buy_signals),
                'indicators': indicators
            }
        elif sell_strength >= self.min_confluence and sell_strength > buy_strength:
            return {
                'action': 'SELL',
                'confidence': sell_strength,
                'signals': sell_signals,
                'total_signals': len(sell_signals),
                'indicators': indicators
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'signals': [],
                'total_signals': 0,
                'reason': f'Insufficient confluence (BUY: {buy_strength}, SELL: {sell_strength}, Required: {self.min_confluence})',
                'indicators': indicators
            }

    def format_signal_report(self, symbol, signal):
        """
        Format signal report for display/logging

        Args:
            symbol: Trading symbol
            signal: Signal dict from generate_signal()

        Returns:
            Formatted string report
        """
        if signal is None:
            return f"{symbol}: No data available"

        report = f"\n{'='*60}\n"
        report += f"SIGNAL REPORT: {symbol}\n"
        report += f"{'='*60}\n"
        report += f"Action: {signal['action']}\n"
        report += f"Confidence: {signal['confidence']}\n"
        report += f"Total Signals: {signal['total_signals']}\n"

        if signal['action'] in ['BUY', 'SELL']:
            report += f"\nConfluence Signals:\n"
            for i, sig in enumerate(signal['signals'], 1):
                report += f"  {i}. [{sig['name']}] {sig['reason']}\n"

            indicators = signal['indicators']
            report += f"\nMarket Data:\n"
            report += f"  Current Price: {indicators['current_price']:.5f}\n"
            report += f"  ATR: {indicators['atr']:.5f}\n"
            report += f"  RSI: {indicators['rsi']:.2f}\n"
            report += f"  MA{config.MA_SHORT_PERIOD}: {indicators['short_ma']:.5f}\n"
            report += f"  MA{config.MA_LONG_PERIOD}: {indicators['long_ma']:.5f}\n"

            if indicators['support_levels']:
                report += f"  Support Levels: {', '.join([f'{s:.5f}' for s in indicators['support_levels']])}\n"
            if indicators['resistance_levels']:
                report += f"  Resistance Levels: {', '.join([f'{r:.5f}' for r in indicators['resistance_levels']])}\n"
        else:
            report += f"\nReason: {signal.get('reason', 'No clear signal')}\n"

        report += f"{'='*60}\n"

        return report


if __name__ == "__main__":
    # Test strategy
    from data_ingestion import DataIngestion

    data_fetcher = DataIngestion()
    strategy = TradingStrategy()

    symbol = "EURUSD"
    df = data_fetcher.get_market_data(symbol, interval="1h", bars=200)

    if df is not None:
        indicators = TechnicalIndicators.calculate_all_indicators(df)
        signal = strategy.generate_signal(indicators)
        report = strategy.format_signal_report(symbol, signal)
        print(report)
