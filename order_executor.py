"""
Order Executor
Bridges trading signals with FIX API execution
"""

import time
from datetime import datetime
import fix_config as fconfig

try:
    from fix_client import FIXClient
    FIX_AVAILABLE = True
except ImportError:
    FIX_AVAILABLE = False
    print("⚠️  FIX client not available")


class OrderExecutor:
    """Execute trading orders via FIX API"""

    def __init__(self, telegram_notifier=None):
        """
        Initialize order executor

        Args:
            telegram_notifier: TelegramNotifier instance for sending alerts
        """
        self.notifier = telegram_notifier
        self.fix_client = None
        self.auto_trading_enabled = fconfig.AUTO_TRADING_ENABLED
        self.executed_orders = []

        if self.auto_trading_enabled and FIX_AVAILABLE:
            self._initialize_fix_client()
        else:
            print("ℹ️  Auto-trading disabled or FIX not available")
            print("   Bot will send signals only (no automatic execution)")

    def _initialize_fix_client(self):
        """Initialize and connect FIX client"""
        try:
            print("\n" + "="*60)
            print("Initializing FIX API Connection...")
            print("="*60)

            # Check credentials
            if not fconfig.FIX_SENDER_COMP_ID or not fconfig.FIX_PASSWORD:
                print("❌ FIX credentials not configured!")
                print("   Update fix_config.py with your credentials")
                print("   Auto-trading will be disabled")
                self.auto_trading_enabled = False
                return

            print(f"Host: {fconfig.FIX_HOST}:{fconfig.FIX_PORT}")
            print(f"Account: {fconfig.FIX_ACCOUNT_ID}")
            print(f"Dry Run: {'YES' if fconfig.DRY_RUN_MODE else 'NO (REAL TRADING!)'}")

            # Create FIX client
            self.fix_client = FIXClient()

            # Connect
            if self.fix_client.connect():
                print("✅ FIX API connected successfully")

                if self.notifier:
                    self.notifier.send_alert(
                        "SUCCESS",
                        f"FIX API Connected\n\n"
                        f"Account: {fconfig.FIX_ACCOUNT_ID}\n"
                        f"Mode: {'DRY RUN' if fconfig.DRY_RUN_MODE else '🚨 LIVE TRADING'}\n"
                        f"Max Orders/Day: {fconfig.MAX_ORDERS_PER_DAY}\n"
                        f"Max Open Positions: {fconfig.MAX_OPEN_POSITIONS}"
                    )
            else:
                print("❌ FIX API connection failed")
                self.auto_trading_enabled = False
                if self.notifier:
                    self.notifier.send_alert("ERROR", "FIX API connection failed")

        except Exception as e:
            print(f"❌ Error initializing FIX client: {e}")
            self.auto_trading_enabled = False
            if self.notifier:
                self.notifier.send_alert("ERROR", f"FIX initialization error: {e}")

    def execute_trade(self, trade_details, signal_info):
        """
        Execute trade from signal

        Args:
            trade_details: Dict from risk_management.calculate_trade_details()
            signal_info: Dict from strategy.generate_signal()

        Returns:
            Dict with execution result
        """
        result = {
            'success': False,
            'order_id': None,
            'message': '',
            'mode': 'SIGNAL_ONLY'
        }

        # Check if auto-trading is enabled
        if not self.auto_trading_enabled:
            result['message'] = "Auto-trading disabled - signal sent only"
            return result

        # Check if FIX client is available and connected
        if not self.fix_client or not self.fix_client.logged_in:
            result['message'] = "FIX client not connected"
            if self.notifier:
                self.notifier.send_alert("ERROR", "Cannot execute: FIX client not connected")
            return result

        # Confirmation check (for first trade of the session)
        if fconfig.REQUIRE_CONFIRMATION and len(self.executed_orders) == 0:
            result['message'] = "Awaiting first trade confirmation"
            if self.notifier:
                self.notifier.send_alert(
                    "WARNING",
                    "⚠️ FIRST TRADE CONFIRMATION REQUIRED\n\n"
                    "The bot wants to execute its first trade.\n"
                    "Set REQUIRE_CONFIRMATION = False in fix_config.py to allow automatic execution.\n\n"
                    f"Trade: {trade_details['direction']} {trade_details['quantity']} {trade_details['symbol']}"
                )
            return result

        # Execute order
        try:
            print(f"\n{'='*60}")
            print("EXECUTING TRADE")
            print(f"{'='*60}")
            print(f"Symbol: {trade_details['symbol']}")
            print(f"Direction: {trade_details['direction']}")
            print(f"Quantity: {trade_details['position_size']} lots")
            print(f"Stop Loss: {trade_details['stop_loss']}")
            print(f"Take Profit: {trade_details['take_profit']}")
            print(f"Mode: {'DRY RUN' if fconfig.DRY_RUN_MODE else '🚨 LIVE'}")
            print(f"{'='*60}\n")

            # Send order
            order_id = self.fix_client.send_market_order(
                symbol=trade_details['symbol'],
                side=trade_details['direction'],
                quantity=trade_details['position_size'],
                stop_loss=trade_details['stop_loss'],
                take_profit=trade_details['take_profit']
            )

            if order_id:
                result['success'] = True
                result['order_id'] = order_id
                result['mode'] = 'DRY_RUN' if fconfig.DRY_RUN_MODE else 'LIVE'
                result['message'] = f"Order executed: {order_id}"

                # Track executed order
                self.executed_orders.append({
                    'order_id': order_id,
                    'trade_details': trade_details,
                    'signal_info': signal_info,
                    'timestamp': datetime.now()
                })

                # Send confirmation
                if self.notifier:
                    self._send_execution_confirmation(trade_details, signal_info, order_id, result['mode'])

                print(f"✅ Order executed successfully: {order_id}")

            else:
                result['message'] = "Order execution failed"
                print(f"❌ Order execution failed")

                if self.notifier:
                    self.notifier.send_alert(
                        "ERROR",
                        f"Order execution failed\n\n"
                        f"{trade_details['symbol']} {trade_details['direction']}"
                    )

        except Exception as e:
            result['message'] = f"Execution error: {e}"
            print(f"❌ Execution error: {e}")

            if self.notifier:
                self.notifier.send_alert("ERROR", f"Execution error: {e}")

        return result

    def _send_execution_confirmation(self, trade_details, signal_info, order_id, mode):
        """Send execution confirmation via Telegram"""
        mode_emoji = "🧪" if mode == "DRY_RUN" else "🚨"
        mode_text = "DRY RUN (Test Mode)" if mode == "DRY_RUN" else "LIVE TRADING"

        message = f"{mode_emoji} <b>ORDER EXECUTED</b> {mode_emoji}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"<b>Mode:</b> {mode_text}\n"
        message += f"<b>Order ID:</b> {order_id}\n\n"
        message += f"<b>Symbol:</b> {trade_details['symbol']}\n"
        message += f"<b>Direction:</b> {trade_details['direction']}\n"
        message += f"<b>Quantity:</b> {trade_details['position_size']} lots\n"
        message += f"<b>Price:</b> ~{trade_details['entry_price']:.5f}\n\n"
        message += f"<b>Stop Loss:</b> {trade_details['stop_loss']:.5f}\n"
        message += f"<b>Take Profit:</b> {trade_details['take_profit']:.5f}\n\n"
        message += f"<b>Risk:</b> ${trade_details['risk_amount']:.2f}\n"
        message += f"<b>Potential Profit:</b> ${trade_details['potential_profit']:.2f}\n\n"
        message += f"<b>Confluence:</b> {signal_info['total_signals']} signals\n"
        message += f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

        if mode == "DRY_RUN":
            message += f"\n<i>⚠️ This is a test order (DRY RUN mode)</i>"

        self.notifier.send_message(message)

    def get_execution_stats(self):
        """Get execution statistics"""
        return {
            'total_orders': len(self.executed_orders),
            'orders_today': self.fix_client.order_count_today if self.fix_client else 0,
            'mode': 'DRY_RUN' if fconfig.DRY_RUN_MODE else 'LIVE',
            'auto_trading_enabled': self.auto_trading_enabled,
            'fix_connected': self.fix_client.logged_in if self.fix_client else False
        }

    def close(self):
        """Close FIX connection"""
        if self.fix_client:
            self.fix_client.disconnect()
            print("FIX client disconnected")


if __name__ == "__main__":
    # Test order executor
    print("Testing Order Executor...")

    executor = OrderExecutor()

    # Test trade details (example)
    test_trade = {
        'symbol': 'EURUSD',
        'direction': 'BUY',
        'entry_price': 1.05000,
        'position_size': 0.01,
        'stop_loss': 1.04850,
        'take_profit': 1.05300,
        'risk_amount': 100,
        'potential_profit': 200
    }

    test_signal = {
        'action': 'BUY',
        'total_signals': 2,
        'confidence': 2
    }

    if fconfig.AUTO_TRADING_ENABLED:
        print("\n⚠️  Auto-trading is ENABLED")
        print("This will execute a test order!")
        print(f"Dry Run Mode: {fconfig.DRY_RUN_MODE}")

        response = input("\nContinue? (yes/no): ")
        if response.lower() == 'yes':
            result = executor.execute_trade(test_trade, test_signal)
            print(f"\nResult: {result}")
    else:
        print("\n✅ Auto-trading is disabled (safe)")
        print("Enable in fix_config.py to test execution")

    executor.close()
