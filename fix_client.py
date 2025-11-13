"""
FIX API Client for ICMarkets cTrader
Handles order execution, position management, and account monitoring
"""

import socket
import threading
import time
from datetime import datetime
import logging
import os
from collections import defaultdict

try:
    import simplefix
    SIMPLEFIX_AVAILABLE = True
except ImportError:
    SIMPLEFIX_AVAILABLE = False
    print("⚠️  simplefix not installed. Install with: pip install simplefix")

import fix_config as fconfig


class FIXClient:
    """FIX API Client for cTrader"""

    def __init__(self):
        """Initialize FIX client"""
        if not SIMPLEFIX_AVAILABLE:
            raise ImportError("simplefix library required. Install with: pip install simplefix")

        self.host = fconfig.FIX_HOST
        self.port = fconfig.FIX_PORT
        self.sender_comp_id = fconfig.FIX_SENDER_COMP_ID
        self.target_comp_id = fconfig.FIX_TARGET_COMP_ID
        self.password = fconfig.FIX_PASSWORD
        self.account_id = fconfig.FIX_ACCOUNT_ID
        self.sender_sub_id = fconfig.FIX_SENDER_SUB_ID

        self.socket = None
        self.connected = False
        self.logged_in = False
        self.sequence_number = 1
        self.heartbeat_interval = 30

        # Order tracking
        self.orders = {}
        self.positions = {}
        self.order_count_today = 0
        self.last_reset_date = datetime.now().date()

        # Setup logging
        self._setup_logging()

        # Threading
        self.receive_thread = None
        self.heartbeat_thread = None
        self.running = False

        self.logger.info("FIX Client initialized")

    def _setup_logging(self):
        """Setup logging for FIX messages"""
        if not os.path.exists(fconfig.FIX_LOG_DIRECTORY):
            os.makedirs(fconfig.FIX_LOG_DIRECTORY)

        log_file = os.path.join(
            fconfig.FIX_LOG_DIRECTORY,
            f"fix_client_{datetime.now().strftime('%Y%m%d')}.log"
        )

        self.logger = logging.getLogger('FIXClient')
        self.logger.setLevel(logging.DEBUG if fconfig.ENABLE_FIX_LOGGING else logging.INFO)

        # File handler - can use emojis
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler - avoid emojis for Windows compatibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        # Use ASCII-friendly format for console
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def connect(self):
        """Connect to FIX server"""
        try:
            self.logger.info(f"Connecting to {self.host}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(30)
            self.socket.connect((self.host, self.port))
            self.connected = True
            self.logger.info("[OK] Connected to FIX server")

            # Start receive thread
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()

            # Login
            return self.login()

        except Exception as e:
            self.logger.error(f"[FAIL] Connection failed: {e}")
            self.connected = False
            return False

    def login(self):
        """Send logon message"""
        try:
            logon = simplefix.FixMessage()
            logon.begin_string = b'FIX.4.4'  # Must be set BEFORE other fields
            logon.append_pair(35, "A", header=True)  # MsgType = Logon
            logon.append_pair(49, self.sender_comp_id, header=True)  # SenderCompID
            logon.append_pair(50, self.sender_sub_id, header=True)  # SenderSubID (TRADE for trading connection)
            logon.append_pair(56, self.target_comp_id, header=True)  # TargetCompID
            logon.append_pair(34, self.sequence_number, header=True)  # MsgSeqNum
            logon.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)  # SendingTime
            logon.append_pair(98, 0)  # EncryptMethod = None
            logon.append_pair(108, self.heartbeat_interval)  # HeartBtInt
            logon.append_pair(96, self.password)  # Password
            logon.append_pair(141, "Y")  # ResetSeqNumFlag
            logon.append_pair(1, self.account_id)  # Account - required by some servers

            self._send_message(logon)
            self.logger.info("Logon message sent")

            # Wait for logon response (try multiple times)
            max_wait = 10  # Wait up to 10 seconds
            wait_interval = 0.5  # Check every 0.5 seconds
            waited = 0

            while waited < max_wait and not self.logged_in:
                time.sleep(wait_interval)
                waited += wait_interval

            if self.logged_in:
                self.logger.info("[OK] Logged in successfully")
                return True
            else:
                self.logger.error(f"[FAIL] Login timeout - no response from server after {max_wait}s")
                return False

        except Exception as e:
            self.logger.error(f"[FAIL] Login failed: {e}")
            return False

    def _send_message(self, message):
        """Send FIX message"""
        try:
            encoded = message.encode()
            # Log the actual raw bytes being sent
            self.logger.debug(f"Sent (raw): {encoded}")
            readable = encoded.replace(b'\x01', b'|').decode('latin-1')
            self.logger.debug(f"Sent (readable): {readable}")
            self.socket.sendall(encoded)
            self.sequence_number += 1
            return True
        except Exception as e:
            self.logger.error(f"[FAIL] Send failed: {e}")
            return False

    def _receive_loop(self):
        """Receive messages from FIX server"""
        parser = simplefix.FixParser()

        # Set shorter timeout for receive to allow clean shutdown
        if self.socket:
            self.socket.settimeout(1.0)

        while self.running and self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.logger.warning("Connection closed by server")
                    self.connected = False
                    break

                parser.append_buffer(data)
                message = parser.get_message()

                while message:
                    self._process_message(message)
                    message = parser.get_message()

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:  # Only log errors if we're still supposed to be running
                    self.logger.error(f"Receive error: {e}")
                break

    def _process_message(self, message):
        """Process received FIX message"""
        try:
            msg_type = message.get(35)  # MsgType

            # Log all received messages
            self.logger.debug(f"Received message type: {msg_type}")
            self.logger.debug(f"Received (full): {message}")

            if msg_type == b'A':  # Logon
                self.logged_in = True
                self.logger.info("[OK] Login accepted by server")

            elif msg_type == b'0':  # Heartbeat
                self.logger.debug("Heartbeat received")

            elif msg_type == b'1':  # Test Request
                self._send_heartbeat(message.get(112))  # Echo TestReqID

            elif msg_type == b'8':  # Execution Report
                self._handle_execution_report(message)

            elif msg_type == b'3':  # Reject
                self.logger.error(f"[FAIL] Message REJECTED by server!")
                # Try to get reject reason
                if message.get(58):  # Text field (reason)
                    self.logger.error(f"[FAIL] Reject reason: {message.get(58).decode()}")
                if message.get(372):  # RefMsgType
                    self.logger.error(f"[FAIL] Rejected message type: {message.get(372).decode()}")
                if message.get(373):  # SessionRejectReason
                    self.logger.error(f"[FAIL] Session reject code: {message.get(373).decode()}")

            elif msg_type == b'5':  # Logout
                self.logger.warning("[WARN] Logout received from server")
                # Check for logout reason
                if message.get(58):
                    self.logger.warning(f"[WARN] Logout reason: {message.get(58).decode()}")
                self.logged_in = False

            else:
                self.logger.warning(f"[WARN] Unknown message type: {msg_type}")

        except Exception as e:
            self.logger.error(f"Error processing message: {e}")

    def _handle_execution_report(self, message):
        """Handle execution report (order status update)"""
        try:
            cl_ord_id = message.get(11).decode()  # ClOrdID
            order_id = message.get(37).decode() if message.get(37) else None  # OrderID
            exec_type = message.get(150).decode()  # ExecType
            ord_status = message.get(39).decode()  # OrdStatus

            self.logger.info(f"Order {cl_ord_id}: Status={ord_status}, ExecType={exec_type}")

            # Update order tracking
            if cl_ord_id in self.orders:
                self.orders[cl_ord_id]['status'] = ord_status
                self.orders[cl_ord_id]['order_id'] = order_id

            # Log execution
            if exec_type in ['1', '2']:  # Partial fill or Fill (1=PartialFill, 2=Fill)
                fill_price = float(message.get(44).decode()) if message.get(44) else 0
                fill_qty = float(message.get(32).decode()) if message.get(32) else 0
                self.logger.info(f"[OK] Order filled: {fill_qty} @ {fill_price}")

                # Send protective stop loss and take profit orders after main order fills
                if exec_type == '2' and cl_ord_id in self.orders:  # Fully filled
                    order_data = self.orders[cl_ord_id]
                    if order_data.get('stop_loss') or order_data.get('take_profit'):
                        self.logger.info("Sending protective orders (SL/TP)...")
                        self._send_protective_orders(
                            cl_ord_id,
                            order_data['symbol'],
                            order_data['side'],
                            order_data['quantity'],
                            fill_price,
                            order_data.get('stop_loss'),
                            order_data.get('take_profit')
                        )

        except Exception as e:
            self.logger.error(f"Error handling execution report: {e}")

    def _send_heartbeat(self, test_req_id=None):
        """Send heartbeat message"""
        try:
            heartbeat = simplefix.FixMessage()
            heartbeat.begin_string = b'FIX.4.4'
            heartbeat.append_pair(35, "0", header=True)  # MsgType = Heartbeat
            heartbeat.append_pair(49, self.sender_comp_id, header=True)
            heartbeat.append_pair(56, self.target_comp_id, header=True)
            heartbeat.append_pair(34, self.sequence_number, header=True)
            heartbeat.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)

            if test_req_id:
                heartbeat.append_pair(112, test_req_id)  # TestReqID

            self._send_message(heartbeat)

        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")

    def send_market_order(self, symbol, side, quantity, stop_loss=None, take_profit=None):
        """
        Send market order

        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            side: "BUY" or "SELL"
            quantity: Order quantity in lots
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)

        Returns:
            Order ID if successful, None otherwise
        """
        # Safety checks
        if not self._safety_checks():
            return None

        # DRY RUN mode
        if fconfig.DRY_RUN_MODE:
            self.logger.info(f"[DRY_RUN] Would send {side} {quantity} lots of {symbol}")
            self.logger.info(f"   SL: {stop_loss}, TP: {take_profit}")
            return "DRY_RUN_" + str(int(time.time()))

        if not self.logged_in:
            self.logger.error("[FAIL] Not logged in")
            return None

        try:
            # Generate unique client order ID
            cl_ord_id = f"ORD_{int(time.time() * 1000)}"

            # Create new order message
            order = simplefix.FixMessage()
            order.begin_string = b'FIX.4.4'
            order.append_pair(35, "D", header=True)  # MsgType = NewOrderSingle
            order.append_pair(49, self.sender_comp_id, header=True)
            order.append_pair(50, self.sender_sub_id, header=True)  # SenderSubID
            order.append_pair(56, self.target_comp_id, header=True)
            order.append_pair(34, self.sequence_number, header=True)
            order.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)

            order.append_pair(11, cl_ord_id)  # ClOrdID
            order.append_pair(1, self.account_id)  # Account
            order.append_pair(55, symbol)  # Symbol
            order.append_pair(54, "1" if side == "BUY" else "2")  # Side (1=Buy, 2=Sell)
            order.append_pair(60, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"))  # TransactTime
            order.append_pair(38, int(quantity * 100000))  # OrderQty (in units, not lots)
            order.append_pair(40, "1")  # OrdType = Market
            order.append_pair(59, "1")  # TimeInForce = GTC

            # For cTrader, we can include SL/TP directly in the order using extension tags
            # Tag 7001 = StopLoss, Tag 7002 = TakeProfit (cTrader proprietary)
            if stop_loss:
                # Store for later - will send as separate protective order after fill
                pass  # Handled after execution

            if take_profit:
                # Store for later - will send as separate protective order after fill
                pass  # Handled after execution

            self._send_message(order)

            # Track order
            self.orders[cl_ord_id] = {
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'status': 'PENDING',
                'timestamp': datetime.now()
            }

            self.order_count_today += 1

            self.logger.info(f"[OK] Market order sent: {side} {quantity} {symbol}")
            return cl_ord_id

        except Exception as e:
            self.logger.error(f"[FAIL] Error sending order: {e}")
            return None

    def _send_protective_orders(self, parent_cl_ord_id, symbol, side, quantity, entry_price, stop_loss, take_profit):
        """
        Send protective stop loss and take profit orders after main order fills

        Args:
            parent_cl_ord_id: Client order ID of the filled main order
            symbol: Trading symbol
            side: Original order side ("BUY" or "SELL")
            quantity: Position quantity in lots
            entry_price: Actual fill price of main order
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
        """
        try:
            # For a BUY position:
            # - Stop Loss is a SELL Stop order below entry
            # - Take Profit is a SELL Limit order above entry
            # For a SELL position: opposite

            # Send Stop Loss order (if provided)
            if stop_loss:
                sl_side = "SELL" if side == "BUY" else "BUY"
                sl_cl_ord_id = f"SL_{parent_cl_ord_id}_{int(time.time() * 1000)}"

                sl_order = simplefix.FixMessage()
                sl_order.begin_string = b'FIX.4.4'
                sl_order.append_pair(35, "D", header=True)  # MsgType = NewOrderSingle
                sl_order.append_pair(49, self.sender_comp_id, header=True)
                sl_order.append_pair(50, self.sender_sub_id, header=True)  # SenderSubID
                sl_order.append_pair(56, self.target_comp_id, header=True)
                sl_order.append_pair(34, self.sequence_number, header=True)
                sl_order.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)

                sl_order.append_pair(11, sl_cl_ord_id)  # ClOrdID
                sl_order.append_pair(1, self.account_id)  # Account
                sl_order.append_pair(55, symbol)  # Symbol
                sl_order.append_pair(54, "1" if sl_side == "BUY" else "2")  # Side
                sl_order.append_pair(60, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"))
                sl_order.append_pair(38, int(quantity * 100000))  # OrderQty
                sl_order.append_pair(40, "3")  # OrdType = Stop (3)
                sl_order.append_pair(44, f"{stop_loss:.5f}")  # Price (stop price)
                sl_order.append_pair(99, f"{stop_loss:.5f}")  # StopPx
                sl_order.append_pair(59, "1")  # TimeInForce = GTC

                self._send_message(sl_order)
                self.logger.info(f"[OK] Stop Loss order sent at {stop_loss:.5f}")

            # Send Take Profit order (if provided)
            if take_profit:
                tp_side = "SELL" if side == "BUY" else "BUY"
                tp_cl_ord_id = f"TP_{parent_cl_ord_id}_{int(time.time() * 1000)}"

                tp_order = simplefix.FixMessage()
                tp_order.begin_string = b'FIX.4.4'
                tp_order.append_pair(35, "D", header=True)  # MsgType = NewOrderSingle
                tp_order.append_pair(49, self.sender_comp_id, header=True)
                tp_order.append_pair(50, self.sender_sub_id, header=True)  # SenderSubID
                tp_order.append_pair(56, self.target_comp_id, header=True)
                tp_order.append_pair(34, self.sequence_number, header=True)
                tp_order.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)

                tp_order.append_pair(11, tp_cl_ord_id)  # ClOrdID
                tp_order.append_pair(1, self.account_id)  # Account
                tp_order.append_pair(55, symbol)  # Symbol
                tp_order.append_pair(54, "1" if tp_side == "BUY" else "2")  # Side
                tp_order.append_pair(60, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"))
                tp_order.append_pair(38, int(quantity * 100000))  # OrderQty
                tp_order.append_pair(40, "2")  # OrdType = Limit (2)
                tp_order.append_pair(44, f"{take_profit:.5f}")  # Price (limit price)
                tp_order.append_pair(59, "1")  # TimeInForce = GTC

                self._send_message(tp_order)
                self.logger.info(f"[OK] Take Profit order sent at {take_profit:.5f}")

        except Exception as e:
            self.logger.error(f"[FAIL] Error sending protective orders: {e}")

    def _safety_checks(self):
        """Perform safety checks before placing order"""
        # Reset daily counter
        if datetime.now().date() != self.last_reset_date:
            self.order_count_today = 0
            self.last_reset_date = datetime.now().date()

        # Check daily order limit
        if self.order_count_today >= fconfig.MAX_ORDERS_PER_DAY:
            self.logger.warning(f"[WARN] Daily order limit reached: {self.order_count_today}/{fconfig.MAX_ORDERS_PER_DAY}")
            return False

        # Check max open positions
        open_positions = len([o for o in self.orders.values() if o['status'] in ['NEW', 'PARTIALLY_FILLED']])
        if open_positions >= fconfig.MAX_OPEN_POSITIONS:
            self.logger.warning(f"[WARN] Max open positions reached: {open_positions}/{fconfig.MAX_OPEN_POSITIONS}")
            return False

        # Check if auto-trading enabled
        if not fconfig.AUTO_TRADING_ENABLED:
            self.logger.warning("[WARN] Auto-trading is disabled in config")
            return False

        return True

    def get_order_status(self, cl_ord_id):
        """Get order status"""
        return self.orders.get(cl_ord_id, {}).get('status', 'UNKNOWN')

    def close_all_positions(self):
        """Emergency close all positions"""
        self.logger.warning("[EMERGENCY] Closing all positions")
        # Implementation depends on getting current positions first
        # This is a placeholder
        pass

    def disconnect(self):
        """Disconnect from FIX server"""
        try:
            # First, stop the receive thread
            self.running = False

            # Send logout if logged in
            if self.logged_in:
                try:
                    logout = simplefix.FixMessage()
                    logout.begin_string = b'FIX.4.4'
                    logout.append_pair(35, "5", header=True)  # MsgType = Logout
                    logout.append_pair(49, self.sender_comp_id, header=True)
                    logout.append_pair(56, self.target_comp_id, header=True)
                    logout.append_pair(34, self.sequence_number, header=True)
                    logout.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S.000"), header=True)
                    self._send_message(logout)
                except:
                    pass  # Ignore errors when sending logout

            # Wait a moment for receive thread to exit
            if self.receive_thread and self.receive_thread.is_alive():
                time.sleep(0.5)

            # Now close the socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass

            self.connected = False
            self.logged_in = False

            self.logger.info("Disconnected from FIX server")

        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")


if __name__ == "__main__":
    # Test the FIX client
    print("Testing FIX Client...")

    if not fconfig.FIX_SENDER_COMP_ID or not fconfig.FIX_PASSWORD:
        print("\n[WARN] FIX credentials not configured!")
        print("Please update fix_config.py with your ICMarkets FIX API credentials")
        print("\nSee fix_config.py for instructions on how to get your credentials")
        exit(1)

    print(f"\nConfiguration:")
    print(f"  Host: {fconfig.FIX_HOST}:{fconfig.FIX_PORT}")
    print(f"  Sender: {fconfig.FIX_SENDER_COMP_ID}")
    print(f"  Account: {fconfig.FIX_ACCOUNT_ID}")
    print(f"  Auto-Trading: {'ENABLED' if fconfig.AUTO_TRADING_ENABLED else 'DISABLED'}")
    print(f"  Dry Run Mode: {'ENABLED' if fconfig.DRY_RUN_MODE else 'DISABLED'}")

    # Test connection
    client = FIXClient()

    try:
        print("\nAttempting to connect...")
        if client.connect():
            print("\n[OK] Successfully connected and logged in!")

            # Test dry run order
            if fconfig.DRY_RUN_MODE:
                print("\nTesting dry run order...")
                order_id = client.send_market_order(
                    symbol="EURUSD",
                    side="BUY",
                    quantity=0.01,
                    stop_loss=1.0400,
                    take_profit=1.0450
                )
                print(f"Order ID: {order_id}")

            # Keep connection alive for testing
            print("\nConnection active. Press Ctrl+C to disconnect...")
            time.sleep(30)

        else:
            print("\n[FAIL] Connection/Login failed")
            print("Check the log file in fix_logs/ for details")

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        client.disconnect()
