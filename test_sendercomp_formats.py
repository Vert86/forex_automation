"""
Test different SenderCompID formats to find the correct one
"""

import socket
import time
from datetime import datetime

try:
    import simplefix
except ImportError:
    print("ERROR: simplefix not installed")
    exit(1)

import fix_config as fconfig


def test_sendercomp_format(sender_comp_id):
    """Test a specific SenderCompID format"""

    print(f"\nTesting SenderCompID: {sender_comp_id}")
    print("-" * 60)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((fconfig.FIX_HOST, fconfig.FIX_PORT))

        logon = simplefix.FixMessage()
        logon.begin_string = b'FIX.4.4'
        logon.append_pair(35, "A", header=True)
        logon.append_pair(49, sender_comp_id, header=True)
        logon.append_pair(56, fconfig.FIX_TARGET_COMP_ID, header=True)
        logon.append_pair(57, fconfig.FIX_SENDER_SUB_ID, header=True)
        logon.append_pair(50, fconfig.FIX_ACCOUNT_ID, header=True)
        logon.append_pair(34, 1, header=True)
        logon.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S"), header=True)
        logon.append_pair(98, 0)
        logon.append_pair(108, 30)
        logon.append_pair(141, "Y")
        logon.append_pair(553, fconfig.FIX_ACCOUNT_ID)
        logon.append_pair(554, fconfig.FIX_PASSWORD)

        encoded = logon.encode()
        sock.sendall(encoded)

        # Wait for response
        parser = simplefix.FixParser()
        start_time = time.time()

        while time.time() - start_time < 5:
            try:
                data = sock.recv(4096)
                if not data:
                    print("  Result: Connection closed (no response)")
                    sock.close()
                    return False

                parser.append_buffer(data)
                msg = parser.get_message()

                if msg:
                    msg_type = msg.get(35)
                    readable = data.replace(b'\x01', b'|').decode('latin-1', errors='ignore')

                    if msg_type == b'A':
                        print(f"  Result: SUCCESS - Logon accepted!")
                        print(f"  Response: {readable}")

                        # Send logout
                        logout = simplefix.FixMessage()
                        logout.begin_string = b'FIX.4.4'
                        logout.append_pair(35, "5", header=True)
                        logout.append_pair(49, sender_comp_id, header=True)
                        logout.append_pair(56, fconfig.FIX_TARGET_COMP_ID, header=True)
                        logout.append_pair(34, 2, header=True)
                        logout.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S"), header=True)
                        sock.sendall(logout.encode())
                        time.sleep(0.5)
                        sock.close()
                        return True

                    elif msg_type == b'5':
                        text = msg.get(58)
                        reason = text.decode() if text else "Unknown"
                        print(f"  Result: FAILED - {reason}")
                        sock.close()
                        return False

            except socket.timeout:
                continue

        print("  Result: Timeout (no response)")
        sock.close()
        return False

    except Exception as e:
        print(f"  Result: ERROR - {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing SenderCompID Formats")
    print("=" * 60)
    print(f"Account: {fconfig.FIX_ACCOUNT_ID}")
    print(f"CTrader ID: {fconfig.FIX_CTRADER_ID}")

    # Test different formats
    formats_to_test = [
        f"demo.icmarkets.{fconfig.FIX_ACCOUNT_ID}",  # Original
        f"demo.icmarkets.{fconfig.FIX_CTRADER_ID}",  # CTrader ID
        f"{fconfig.FIX_CTRADER_ID}.{fconfig.FIX_ACCOUNT_ID}",  # ID.Account
        f"{fconfig.FIX_CTRADER_ID}",  # Just ID
        f"icmarkets.{fconfig.FIX_ACCOUNT_ID}",  # Without demo prefix
        f"icmarkets.{fconfig.FIX_CTRADER_ID}",  # Without demo prefix + ID
    ]

    for fmt in formats_to_test:
        if test_sendercomp_format(fmt):
            print("\n" + "=" * 60)
            print(f"FOUND WORKING FORMAT: {fmt}")
            print("=" * 60)
            print(f"\nUpdate fix_config.py:")
            print(f'FIX_SENDER_COMP_ID = "{fmt}"')
            break
        time.sleep(0.5)  # Brief delay between tests
    else:
        print("\n" + "=" * 60)
        print("NONE OF THE FORMATS WORKED")
        print("=" * 60)
        print("\nYou need to check your cTrader FIX API settings to get the exact SenderCompID value.")
        print("In cTrader: Settings -> FIX API -> Look for 'SenderCompID' or 'Sender Comp ID'")
