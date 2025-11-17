"""
Risk Management Engine
Handles position sizing, stop loss, and take profit calculations
"""

import config
import numpy as np


class RiskManagement:
    """Class to manage risk and calculate position sizes"""

    def __init__(self, account_balance=None):
        """
        Initialize Risk Management

        Args:
            account_balance: Current account balance (uses config default if None)
        """
        self.account_balance = account_balance or config.ACCOUNT_BALANCE
        self.daily_loss = 0
        self.weekly_loss = 0

    def update_account_balance(self, new_balance):
        """Update account balance"""
        self.account_balance = new_balance

    def update_daily_loss(self, loss):
        """Update daily loss tracker"""
        self.daily_loss += loss

    def update_weekly_loss(self, loss):
        """Update weekly loss tracker"""
        self.weekly_loss += loss

    def reset_daily_loss(self):
        """Reset daily loss counter (call at start of new day)"""
        self.daily_loss = 0

    def reset_weekly_loss(self):
        """Reset weekly loss counter (call at start of new week)"""
        self.weekly_loss = 0

    def check_trading_allowed(self):
        """
        Check if trading is allowed based on loss limits

        Returns:
            Tuple (allowed: bool, reason: str)
        """
        max_daily_loss = self.account_balance * (config.MAX_DAILY_LOSS_PERCENT / 100)
        max_weekly_loss = self.account_balance * (config.MAX_WEEKLY_LOSS_PERCENT / 100)

        if abs(self.daily_loss) >= max_daily_loss:
            return False, f"Daily loss limit reached: ${abs(self.daily_loss):.2f} / ${max_daily_loss:.2f}"

        if abs(self.weekly_loss) >= max_weekly_loss:
            return False, f"Weekly loss limit reached: ${abs(self.weekly_loss):.2f} / ${max_weekly_loss:.2f}"

        return True, "Trading allowed"

    def calculate_position_size(self, entry_price, stop_loss_price, symbol):
        """
        Calculate position size based on risk per trade

        Args:
            entry_price: Entry price for the trade
            stop_loss_price: Stop loss price
            symbol: Trading symbol

        Returns:
            Position size in lots
        """
        # If fixed lot size is enabled, check for symbol-specific lot size first
        if config.USE_FIXED_LOT_SIZE:
            # Check if this symbol has a custom lot size
            if hasattr(config, 'SYMBOL_LOT_SIZES') and symbol in config.SYMBOL_LOT_SIZES:
                return config.SYMBOL_LOT_SIZES[symbol]
            # Otherwise use default
            return config.DEFAULT_LOT_SIZE

        # Calculate risk amount in account currency
        risk_amount = self.account_balance * (config.RISK_PER_TRADE_PERCENT / 100)

        # Calculate pip value and risk in pips
        pip_risk = abs(entry_price - stop_loss_price)

        if pip_risk == 0:
            return config.DEFAULT_LOT_SIZE

        # For forex pairs, calculate lot size
        # Standard lot = 100,000 units
        # Mini lot = 10,000 units
        # Micro lot = 1,000 units

        # Get pip value per lot (varies by pair)
        pip_value_per_lot = self._get_pip_value(symbol, entry_price)

        # Calculate position size
        # risk_amount = pip_risk * pip_value_per_lot * lot_size
        # lot_size = risk_amount / (pip_risk * pip_value_per_lot)

        lot_size = risk_amount / (pip_risk * pip_value_per_lot)

        # Ensure lot size is within limits
        lot_size = max(config.MIN_LOT_SIZE, min(lot_size, config.MAX_LOT_SIZE))

        # Round to 2 decimal places
        lot_size = round(lot_size, 2)

        return lot_size

    def _get_pip_value(self, symbol, current_price):
        """
        Get pip value per standard lot for a symbol

        Args:
            symbol: Trading symbol
            current_price: Current market price

        Returns:
            Pip value in account currency
        """
        # For most forex pairs, 1 pip = 0.0001
        # For JPY pairs, 1 pip = 0.01
        # Standard lot = 100,000 units

        # Simplification: assuming account currency is USD
        if "JPY" in symbol:
            # For JPY pairs, pip = 0.01
            pip_size = 0.01
        else:
            # For other pairs, pip = 0.0001
            pip_size = 0.0001

        # For pairs where USD is the quote currency (e.g., EURUSD)
        # Pip value = (pip size / exchange rate) * lot size
        # For standard lot: pip value ≈ $10

        if symbol.endswith("USD"):
            # USD is quote currency
            pip_value = 10.0  # $10 per pip for standard lot
        elif symbol.startswith("USD"):
            # USD is base currency
            pip_value = 10.0 / current_price
        else:
            # Cross currency pair - simplified to $10
            pip_value = 10.0

        return pip_value

    def calculate_stop_loss_take_profit(self, symbol, entry_price, direction, atr,
                                       support_levels, resistance_levels):
        """
        Calculate dynamic stop loss and take profit levels

        Args:
            symbol: Trading symbol (for pip calculation)
            entry_price: Entry price for the trade
            direction: 'BUY' or 'SELL'
            atr: Current ATR value
            support_levels: List of support levels
            resistance_levels: List of resistance levels

        Returns:
            Dict with stop_loss, take_profit, sl_pips, tp_pips
        """
        if direction == 'BUY':
            # For long positions
            # Stop Loss: entry - (ATR * multiplier) or below nearest support
            atr_sl = entry_price - (atr * config.ATR_SL_MULTIPLIER)

            # Find nearest support below entry
            supports_below = [s for s in support_levels if s < entry_price]
            if supports_below:
                nearest_support = max(supports_below)
                # Place SL slightly below support
                support_sl = nearest_support - (atr * 0.5)
                # Use the one that's closer to entry (less risk)
                stop_loss = max(atr_sl, support_sl)
            else:
                stop_loss = atr_sl

            # Take Profit: entry + (ATR * multiplier) or below nearest resistance
            atr_tp = entry_price + (atr * config.ATR_TP_MULTIPLIER)

            # Find nearest resistance above entry
            resistances_above = [r for r in resistance_levels if r > entry_price]
            if resistances_above:
                nearest_resistance = min(resistances_above)
                # Place TP slightly below resistance
                resistance_tp = nearest_resistance - (atr * 0.3)
                # Use the one that gives better R:R but is logical
                take_profit = min(atr_tp, resistance_tp)
            else:
                take_profit = atr_tp

        else:  # SELL
            # For short positions
            # Stop Loss: entry + (ATR * multiplier) or above nearest resistance
            atr_sl = entry_price + (atr * config.ATR_SL_MULTIPLIER)

            # Find nearest resistance above entry
            resistances_above = [r for r in resistance_levels if r > entry_price]
            if resistances_above:
                nearest_resistance = min(resistances_above)
                # Place SL slightly above resistance
                resistance_sl = nearest_resistance + (atr * 0.5)
                # Use the one that's closer to entry (less risk)
                stop_loss = min(atr_sl, resistance_sl)
            else:
                stop_loss = atr_sl

            # Take Profit: entry - (ATR * multiplier) or above nearest support
            atr_tp = entry_price - (atr * config.ATR_TP_MULTIPLIER)

            # Find nearest support below entry
            supports_below = [s for s in support_levels if s < entry_price]
            if supports_below:
                nearest_support = max(supports_below)
                # Place TP slightly above support
                support_tp = nearest_support + (atr * 0.3)
                # Use the one that gives better R:R but is logical
                take_profit = max(atr_tp, support_tp)
            else:
                take_profit = atr_tp

        # Calculate pips
        sl_pips = abs(entry_price - stop_loss)
        tp_pips = abs(take_profit - entry_price)

        # Ensure minimum R:R ratio of 1:2
        if tp_pips < (sl_pips * 2):
            if direction == 'BUY':
                take_profit = entry_price + (sl_pips * 2)
            else:
                take_profit = entry_price - (sl_pips * 2)
            tp_pips = abs(take_profit - entry_price)

        # Convert to pips/points for display
        # Different multipliers for different asset types
        if symbol in ["XAUUSD", "XAGUSD", "XTIUSD"]:
            # Commodities (Gold, Silver, Oil): 1 point = $0.01
            pip_multiplier = 100
        elif any(crypto in symbol for crypto in ["BTC", "ETH", "LTC"]):
            # Crypto: Show actual price difference (no pip conversion)
            pip_multiplier = 1
        elif "JPY" in symbol:
            # JPY pairs: 1 pip = 0.01
            pip_multiplier = 100
        else:
            # Most forex pairs: 1 pip = 0.0001
            pip_multiplier = 10000

        return {
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'sl_pips': round(sl_pips * pip_multiplier, 1),
            'tp_pips': round(tp_pips * pip_multiplier, 1),
            'risk_reward_ratio': round(tp_pips / sl_pips, 2) if sl_pips > 0 else 0
        }

    def check_volatility_filter(self, atr, current_price):
        """
        Check if current volatility is within acceptable range

        Args:
            atr: Current ATR value
            current_price: Current market price

        Returns:
            Tuple (allowed: bool, reason: str)
        """
        # Calculate ATR as percentage of price
        atr_percent = (atr / current_price) * 100

        if atr_percent > config.MAX_VOLATILITY_THRESHOLD:
            return False, f"Volatility too high: {atr_percent:.2f}%"

        if atr_percent < config.MIN_VOLATILITY_THRESHOLD:
            return False, f"Volatility too low: {atr_percent:.2f}%"

        return True, f"Volatility acceptable: {atr_percent:.2f}%"

    def calculate_trade_details(self, symbol, direction, entry_price, atr,
                               support_levels, resistance_levels):
        """
        Calculate complete trade details including position size, SL, TP

        Args:
            symbol: Trading symbol
            direction: 'BUY' or 'SELL'
            entry_price: Entry price
            atr: Current ATR value
            support_levels: List of support levels
            resistance_levels: List of resistance levels

        Returns:
            Dict with complete trade details or None if trading not allowed
        """
        # Check if trading is allowed
        allowed, reason = self.check_trading_allowed()
        if not allowed:
            return None

        # Check volatility filter - REJECT trades outside acceptable range
        vol_allowed, vol_reason = self.check_volatility_filter(atr, entry_price)
        if not vol_allowed:
            print(f"❌ Trade rejected - {vol_reason}")
            return None

        # Calculate SL and TP
        sl_tp = self.calculate_stop_loss_take_profit(
            symbol, entry_price, direction, atr, support_levels, resistance_levels
        )

        # Calculate position size
        position_size = self.calculate_position_size(
            entry_price, sl_tp['stop_loss'], symbol
        )

        # Calculate potential profit/loss
        risk_amount = self.account_balance * (config.RISK_PER_TRADE_PERCENT / 100)
        potential_profit = risk_amount * sl_tp['risk_reward_ratio']

        return {
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'stop_loss': sl_tp['stop_loss'],
            'take_profit': sl_tp['take_profit'],
            'sl_pips': sl_tp['sl_pips'],
            'tp_pips': sl_tp['tp_pips'],
            'position_size': position_size,
            'risk_reward_ratio': sl_tp['risk_reward_ratio'],
            'risk_amount': round(risk_amount, 2),
            'potential_profit': round(potential_profit, 2),
            'atr': round(atr, 5),
            'volatility_status': vol_reason
        }


if __name__ == "__main__":
    # Test risk management
    rm = RiskManagement(account_balance=10000)

    # Test trade calculation
    trade = rm.calculate_trade_details(
        symbol="EURUSD",
        direction="BUY",
        entry_price=1.1000,
        atr=0.0015,
        support_levels=[1.0950, 1.0980],
        resistance_levels=[1.1050, 1.1100]
    )

    if trade:
        print("Trade Details:")
        for key, value in trade.items():
            print(f"{key}: {value}")
