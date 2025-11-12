"""
Main Forex Trading Automation Bot
Orchestrates all modules to analyze markets and send trading signals
"""

import time
import schedule
from datetime import datetime
import traceback
import config
from data_ingestion import DataIngestion
from indicators import TechnicalIndicators
from strategy import TradingStrategy
from risk_management import RiskManagement
from telegram_notifier import TelegramNotifier


class ForexTradingBot:
    """Main trading bot class"""

    def __init__(self):
        """Initialize the trading bot"""
        print("Initializing Forex Trading Bot...")

        # Initialize modules
        self.data_fetcher = DataIngestion()
        self.strategy = TradingStrategy()
        self.risk_manager = RiskManagement()
        self.notifier = TelegramNotifier()

        # Statistics
        self.signals_today = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        self.last_signals = {}  # Track last signal for each symbol to avoid duplicates

        print("✅ All modules initialized")

    def analyze_symbol(self, symbol):
        """
        Analyze a single symbol and generate signal if conditions are met

        Args:
            symbol: Trading symbol to analyze

        Returns:
            Dict with signal and trade details or None
        """
        try:
            print(f"\n{'='*60}")
            print(f"Analyzing {symbol}...")
            print(f"{'='*60}")

            # Fetch market data
            df = self.data_fetcher.get_market_data(
                symbol,
                interval=config.TIMEFRAME,
                bars=200
            )

            if df is None or len(df) < config.MA_LONG_PERIOD:
                print(f"❌ Insufficient data for {symbol}")
                return None

            # Calculate indicators
            indicators = TechnicalIndicators.calculate_all_indicators(df)

            if indicators is None:
                print(f"❌ Failed to calculate indicators for {symbol}")
                return None

            # Generate trading signal
            signal = self.strategy.generate_signal(indicators)

            # Print signal report
            report = self.strategy.format_signal_report(symbol, signal)
            print(report)

            # If signal is BUY or SELL, calculate trade details
            if signal['action'] in ['BUY', 'SELL']:
                # Check if this is a duplicate signal
                last_signal = self.last_signals.get(symbol, {})
                if (last_signal.get('action') == signal['action'] and
                    last_signal.get('price') == indicators['current_price']):
                    print(f"⚠️  Skipping duplicate signal for {symbol}")
                    return None

                # Calculate complete trade details
                trade_details = self.risk_manager.calculate_trade_details(
                    symbol=symbol,
                    direction=signal['action'],
                    entry_price=indicators['current_price'],
                    atr=indicators['atr'],
                    support_levels=indicators['support_levels'],
                    resistance_levels=indicators['resistance_levels']
                )

                if trade_details is None:
                    print(f"⚠️  Trade not allowed due to risk limits for {symbol}")
                    return None

                # Update statistics
                self.signals_today[signal['action']] += 1

                # Store this signal to avoid duplicates
                self.last_signals[symbol] = {
                    'action': signal['action'],
                    'price': indicators['current_price'],
                    'timestamp': datetime.now()
                }

                return {
                    'symbol': symbol,
                    'signal': signal,
                    'trade_details': trade_details
                }

            return None

        except Exception as e:
            print(f"❌ Error analyzing {symbol}: {e}")
            traceback.print_exc()
            return None

    def scan_all_symbols(self):
        """
        Scan all configured symbols for trading opportunities
        """
        print("\n" + "="*60)
        print(f"🔍 STARTING MARKET SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)

        signals_found = []

        for symbol in config.SYMBOLS:
            try:
                result = self.analyze_symbol(symbol)

                if result:
                    signals_found.append(result)
                    print(f"✅ Signal generated for {symbol}")

                # Rate limiting to avoid API restrictions
                time.sleep(2)  # 2 second delay between symbols

            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
                continue

        # Send signals via Telegram
        if signals_found:
            print(f"\n🎯 Found {len(signals_found)} trading signal(s)")
            self.send_signals(signals_found)
        else:
            print("\n⚠️  No trading signals found in this scan")

        print("\n" + "="*60)
        print(f"✅ SCAN COMPLETE - Next scan in {config.UPDATE_INTERVAL} minutes")
        print("="*60)

    def send_signals(self, signals):
        """
        Send trading signals via Telegram

        Args:
            signals: List of signal dicts
        """
        for signal_data in signals:
            try:
                print(f"\n📤 Sending signal for {signal_data['symbol']}...")

                response = self.notifier.send_trade_signal(
                    trade_details=signal_data['trade_details'],
                    signal_info=signal_data['signal']
                )

                if response:
                    print(f"✅ Signal sent successfully for {signal_data['symbol']}")
                else:
                    print(f"⚠️  Failed to send signal for {signal_data['symbol']}")

            except Exception as e:
                print(f"❌ Error sending signal for {signal_data['symbol']}: {e}")

    def send_daily_summary(self):
        """Send daily summary of trading activity"""
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'signals_generated': sum(self.signals_today.values()),
            'buy_signals': self.signals_today['BUY'],
            'sell_signals': self.signals_today['SELL'],
            'account_balance': self.risk_manager.account_balance,
            'daily_pnl': -self.risk_manager.daily_loss,
            'weekly_pnl': -self.risk_manager.weekly_loss
        }

        self.notifier.send_daily_summary(summary)

        # Reset daily counters
        self.signals_today = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        self.risk_manager.reset_daily_loss()

    def start(self, run_once=False):
        """
        Start the trading bot

        Args:
            run_once: If True, run only once and exit (for testing)
        """
        print("\n" + "="*60)
        print("🚀 FOREX TRADING AUTOMATION BOT")
        print("="*60)
        print(f"Version: 1.0")
        print(f"Monitoring: {len(config.SYMBOLS)} symbols")
        print(f"Timeframe: {config.TIMEFRAME}")
        print(f"Update Interval: {config.UPDATE_INTERVAL} minutes")
        print(f"Risk per Trade: {config.RISK_PER_TRADE_PERCENT}%")
        print(f"Account Balance: ${self.risk_manager.account_balance:.2f}")
        print("="*60 + "\n")

        # Send startup notification
        try:
            self.notifier.send_startup_message()
        except Exception as e:
            print(f"⚠️  Could not send startup message: {e}")

        if run_once:
            # Run once for testing
            self.scan_all_symbols()
            return

        # Schedule regular scans
        schedule.every(config.UPDATE_INTERVAL).minutes.do(self.scan_all_symbols)

        # Schedule daily summary (at midnight)
        schedule.every().day.at("00:00").do(self.send_daily_summary)

        # Run first scan immediately
        self.scan_all_symbols()

        # Main loop
        print("\n🔄 Bot is running. Press Ctrl+C to stop.\n")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down bot...")
            try:
                self.notifier.send_shutdown_message()
            except Exception as e:
                print(f"Could not send shutdown message: {e}")
            print("✅ Bot stopped successfully")

    def test_single_symbol(self, symbol):
        """
        Test the bot with a single symbol (for debugging)

        Args:
            symbol: Symbol to test
        """
        print(f"\n🧪 Testing with {symbol}...")
        result = self.analyze_symbol(symbol)

        if result:
            print("\n📤 Sending test signal...")
            self.send_signals([result])
        else:
            print("\n⚠️  No signal generated")


def main():
    """Main entry point"""
    import sys

    bot = ForexTradingBot()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            # Test mode: run once
            bot.start(run_once=True)
        elif sys.argv[1] == '--symbol':
            # Test single symbol
            if len(sys.argv) > 2:
                bot.test_single_symbol(sys.argv[2])
            else:
                print("Usage: python main.py --symbol <SYMBOL>")
        else:
            print("Usage:")
            print("  python main.py              # Run continuously")
            print("  python main.py --test       # Run once and exit")
            print("  python main.py --symbol EURUSD  # Test single symbol")
    else:
        # Normal mode: run continuously
        bot.start()


if __name__ == "__main__":
    main()
