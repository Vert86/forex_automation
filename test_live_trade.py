"""
Test Live Trade Execution
Tests the complete flow: connect → send order → wait for confirmation
"""

import sys
from fix_client import FIXClient
import fix_config as fconfig

def test_live_trade():
    """Test a small live trade with EURUSD"""

    print("=" * 60)
    print("LIVE TRADE TEST")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will place a REAL trade on your account!")
    print(f"Account: {fconfig.FIX_ACCOUNT_ID}")
    print(f"Mode: {'DRY RUN' if fconfig.DRY_RUN_MODE else 'LIVE TRADING'}")
    print()
    print("Test Trade Details:")
    print("  Symbol: EURUSD (ID: 1)")
    print("  Side: BUY")
    print("  Quantity: 0.01 lots (1,000 units)")
    print("  Type: Market Order")
    print()

    response = input("Continue with test trade? (yes/no): ")
    if response.lower() != 'yes':
        print("Test cancelled.")
        return

    print("\n" + "=" * 60)
    print("Initializing FIX Client...")
    print("=" * 60)

    try:
        # Initialize and connect
        client = FIXClient()

        if not client.connect():
            print("❌ Failed to connect to FIX server")
            return

        print("\n✅ Connected and logged in successfully")
        print()
        print("=" * 60)
        print("Sending Market Order...")
        print("=" * 60)

        # Send a small market order
        order_id = client.send_market_order(
            symbol='EURUSD',
            side='BUY',
            quantity=0.01,  # Very small size for testing
            stop_loss=None,  # No SL/TP for this test
            take_profit=None
        )

        print()
        print("=" * 60)
        print("RESULT")
        print("=" * 60)

        if order_id:
            print(f"✅ SUCCESS!")
            print(f"Order ID: {order_id}")
            print(f"Order Status: FILLED")

            # Get order details
            if order_id in client.orders:
                order = client.orders[order_id]
                print(f"Fill Price: {order.get('fill_price', 'N/A')}")
                print(f"Fill Quantity: {order.get('fill_qty', 'N/A')}")

            print()
            print("✅ Trade should now be visible in your cTrader platform!")
            print("   Check the 'Positions' tab to see the open position.")

        else:
            print(f"❌ FAILED!")
            print(f"Order was not executed.")
            print(f"Check the logs in fix_logs/ for details.")

            # Show why it failed
            print()
            print("Possible reasons:")
            print("  - Order was rejected by server")
            print("  - Timeout waiting for confirmation")
            print("  - Invalid symbol ID")
            print("  - Insufficient margin")

        print()
        print("=" * 60)
        print("Disconnecting...")
        print("=" * 60)

        client.disconnect()
        print("✅ Disconnected")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_live_trade()
