"""
Telegram Notification Module
Sends trading signals and alerts via Telegram
"""

import requests
import config
from datetime import datetime


class TelegramNotifier:
    """Class to send notifications via Telegram"""

    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize Telegram Notifier

        Args:
            bot_token: Telegram bot token (uses config if None)
            chat_id: Telegram chat ID (uses config if None)
        """
        self.bot_token = bot_token or config.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, message, parse_mode='HTML'):
        """
        Send a message via Telegram

        Args:
            message: Message text to send
            parse_mode: Parse mode (HTML, Markdown, or None)

        Returns:
            Response from Telegram API
        """
        if not self.bot_token or not self.chat_id:
            print("Telegram bot token or chat ID not configured. Message not sent.")
            print(f"Message: {message}")
            return None

        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }

        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return None

    def format_trade_signal(self, trade_details, signal_info):
        """
        Format a trading signal for Telegram

        Args:
            trade_details: Dict from risk_management.calculate_trade_details()
            signal_info: Dict from strategy.generate_signal()

        Returns:
            Formatted message string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"🚨 <b>FOREX TRADING SIGNAL</b> 🚨\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"

        # Trade Details
        message += f"📊 <b>Symbol:</b> {trade_details['symbol']}\n"
        message += f"📈 <b>Action:</b> {trade_details['direction']}\n"
        message += f"💰 <b>Current Price:</b> {trade_details['entry_price']:.5f} <i>(indicative)</i>\n\n"

        # Order Details for MT5
        message += f"<b>📋 MT5 ORDER DETAILS:</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"<b>Order Type:</b> Market Execution\n"
        message += f"<b>Symbol:</b> {trade_details['symbol']}\n"
        message += f"<b>Direction:</b> {trade_details['direction']}\n"
        message += f"<b>Quantity:</b> {trade_details['position_size']} lots\n"
        message += f"<i>Note: Market orders execute at best available price</i>\n\n"

        # Stop Loss & Take Profit
        # Determine if we should show "pips" or "points"
        symbol = trade_details['symbol']
        unit_label = "Points" if symbol in ["XAUUSD", "XAGUSD", "XTIUSD"] else "Pips"

        message += f"<b>🛡️ Stop Loss:</b>\n"
        message += f"  Price: {trade_details['stop_loss']:.5f}\n"
        message += f"  {unit_label}: {trade_details['sl_pips']:.1f}\n"
        message += f"  Trailing SL: Disable\n\n"

        message += f"<b>🎯 Take Profit:</b>\n"
        message += f"  Price: {trade_details['take_profit']:.5f}\n"
        message += f"  {unit_label}: {trade_details['tp_pips']:.1f}\n\n"

        # Risk Management
        message += f"<b>⚖️ RISK MANAGEMENT:</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"<b>Risk/Reward:</b> 1:{trade_details['risk_reward_ratio']}\n"
        message += f"<b>Risk Amount:</b> ${trade_details['risk_amount']:.2f}\n"
        message += f"<b>Potential Profit:</b> ${trade_details['potential_profit']:.2f}\n"
        message += f"<b>ATR:</b> {trade_details['atr']:.5f}\n\n"

        # Signal Confluence
        message += f"<b>🎲 CONFLUENCE SIGNALS ({signal_info['total_signals']}):</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        for i, sig in enumerate(signal_info['signals'], 1):
            message += f"{i}. <b>{sig['name'].replace('_', ' ').title()}:</b>\n"
            message += f"   {sig['reason']}\n"

        message += f"\n<b>⏰ Time:</b> {timestamp}\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n"
        message += f"<i>Volatility: {trade_details['volatility_status']}</i>\n"

        return message

    def send_trade_signal(self, trade_details, signal_info):
        """
        Send a formatted trading signal via Telegram

        Args:
            trade_details: Dict from risk_management.calculate_trade_details()
            signal_info: Dict from strategy.generate_signal()

        Returns:
            Response from Telegram API
        """
        message = self.format_trade_signal(trade_details, signal_info)
        return self.send_message(message)

    def send_alert(self, alert_type, message):
        """
        Send an alert message

        Args:
            alert_type: Type of alert (INFO, WARNING, ERROR)
            message: Alert message

        Returns:
            Response from Telegram API
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        emoji_map = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'SUCCESS': '✅'
        }

        emoji = emoji_map.get(alert_type, 'ℹ️')
        formatted_message = f"{emoji} <b>{alert_type}</b>\n\n{message}\n\n<i>{timestamp}</i>"

        return self.send_message(formatted_message)

    def send_daily_summary(self, summary_data):
        """
        Send a daily trading summary

        Args:
            summary_data: Dict with daily statistics

        Returns:
            Response from Telegram API
        """
        message = f"📊 <b>DAILY TRADING SUMMARY</b>\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        message += f"<b>Date:</b> {summary_data.get('date', datetime.now().strftime('%Y-%m-%d'))}\n\n"
        message += f"<b>Signals Generated:</b> {summary_data.get('signals_generated', 0)}\n"
        message += f"<b>Buy Signals:</b> {summary_data.get('buy_signals', 0)}\n"
        message += f"<b>Sell Signals:</b> {summary_data.get('sell_signals', 0)}\n\n"
        message += f"<b>Account Status:</b>\n"
        message += f"  Balance: ${summary_data.get('account_balance', 0):.2f}\n"
        message += f"  Daily P/L: ${summary_data.get('daily_pnl', 0):.2f}\n"
        message += f"  Weekly P/L: ${summary_data.get('weekly_pnl', 0):.2f}\n\n"
        message += f"━━━━━━━━━━━━━━━━━━━━━━\n"

        return self.send_message(message)

    def send_startup_message(self):
        """Send a message when the bot starts"""
        message = f"🤖 <b>FOREX AUTOMATION BOT STARTED</b>\n\n"
        message += f"<b>Monitoring {len(config.SYMBOLS)} symbols:</b>\n"
        message += f"{', '.join(config.SYMBOLS[:5])}\n"
        message += f"and {len(config.SYMBOLS) - 5} more...\n\n"
        message += f"<b>Update Interval:</b> {config.UPDATE_INTERVAL} minutes\n"
        message += f"<b>Risk per Trade:</b> {config.RISK_PER_TRADE_PERCENT}%\n"
        message += f"<b>Min Confluence:</b> {config.MIN_CONFLUENCE_SIGNALS} signals\n\n"
        message += f"✅ Bot is now active and monitoring markets!"

        return self.send_message(message)

    def send_shutdown_message(self):
        """Send a message when the bot stops"""
        message = f"🛑 <b>FOREX AUTOMATION BOT STOPPED</b>\n\n"
        message += f"Bot has been shut down.\n"
        message += f"<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"

        return self.send_message(message)


if __name__ == "__main__":
    # Test Telegram notifier
    notifier = TelegramNotifier()

    # Test simple message
    print("Testing Telegram connection...")
    test_message = "🧪 <b>Test Message</b>\n\nForex Automation Bot is configured correctly!"

    if notifier.bot_token and notifier.chat_id:
        response = notifier.send_message(test_message)
        print(f"Response: {response}")
    else:
        print("Please configure TELEGRAM_BOT_TOKEN in config.py")
        print(f"Message that would be sent:\n{test_message}")
