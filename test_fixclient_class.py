"""
Test the FIXClient class to verify it connects properly
"""

import time
from fix_client import FIXClient

def test_fixclient():
    """Test FIXClient connection"""

    print("=" * 60)
    print("Testing FIXClient Class")
    print("=" * 60)

    try:
        # Initialize client
        print("\n[1/3] Initializing FIXClient...")
        client = FIXClient()
        print("      SUCCESS - FIXClient initialized")

        # Connect and login
        print("\n[2/3] Connecting and logging in...")
        if client.connect():
            print("      SUCCESS - Connected and logged in!")
            print(f"      Connected: {client.connected}")
            print(f"      Logged in: {client.logged_in}")

            # Wait a moment to receive any messages
            print("\n[3/3] Waiting 3 seconds for heartbeat...")
            time.sleep(3)

            # Disconnect
            print("\n[4/4] Disconnecting...")
            client.disconnect()
            print("      SUCCESS - Disconnected cleanly")

            print("\n" + "=" * 60)
            print("ALL TESTS PASSED!")
            print("=" * 60)
            print("\nYour FIX API client is working correctly.")
            print("Check the logs in fix_logs/ for detailed message history.")
            return True

        else:
            print("      FAILED - Could not connect/login")
            print("\n" + "=" * 60)
            print("CONNECTION FAILED")
            print("=" * 60)
            print("\nCheck fix_logs/ for detailed error messages.")
            return False

    except Exception as e:
        print(f"\n      ERROR - {e}")
        print("\n" + "=" * 60)
        print("TEST FAILED WITH ERROR")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_fixclient()
    exit(0 if success else 1)
