"""
Test FIX API Connection to ICMarkets cTrader
Simple standalone test to verify credentials and connection
"""

import socket
import time
from datetime import datetime

try:
    import simplefix
except ImportError:
    print("ERROR: simplefix not installed")
    print("Install with: pip install simplefix")
    exit(1)

import fix_config as fconfig


def test_fix_connection():
    """Test FIX connection with correct tag ordering"""

    print("=" * 60)
    print("FIX API Connection Test")
    print("=" * 60)
    print(f"Host: {fconfig.FIX_HOST}:{fconfig.FIX_PORT}")
    print(f"SenderCompID: {fconfig.FIX_SENDER_COMP_ID}")
    print(f"TargetCompID: {fconfig.FIX_TARGET_COMP_ID}")
    print(f"Account: {fconfig.FIX_ACCOUNT_ID}")
    print("=" * 60)

    # Step 1: Connect to server
    print("\n[1/4] Connecting to server...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((fconfig.FIX_HOST, fconfig.FIX_PORT))
        print("      SUCCESS - TCP connection established")
    except Exception as e:
        print(f"      FAILED - {e}")
        return False

    # Step 2: Build logon message with CORRECT tag ordering
    print("\n[2/4] Building logon message...")
    try:
        logon = simplefix.FixMessage()
        logon.begin_string = b'FIX.4.4'

        # CRITICAL: Tags must be in this exact order per cTrader spec
        logon.append_pair(35, "A", header=True)  # MsgType = Logon
        logon.append_pair(49, fconfig.FIX_SENDER_COMP_ID, header=True)  # SenderCompID
        logon.append_pair(56, fconfig.FIX_TARGET_COMP_ID, header=True)  # TargetCompID (must be CSERVER)
        logon.append_pair(57, fconfig.FIX_SENDER_SUB_ID, header=True)  # TargetSubID (TRADE or QUOTE)
        logon.append_pair(50, fconfig.FIX_ACCOUNT_ID, header=True)  # SenderSubID (account number)
        logon.append_pair(34, 1, header=True)  # MsgSeqNum
        logon.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S"), header=True)  # SendingTime (NO milliseconds)

        # Body tags (non-header)
        logon.append_pair(98, 0)  # EncryptMethod = None
        logon.append_pair(108, 30)  # HeartBtInt = 30 seconds
        logon.append_pair(141, "Y")  # ResetSeqNumFlag
        logon.append_pair(553, fconfig.FIX_ACCOUNT_ID)  # Username (must be numeric account number)
        logon.append_pair(554, fconfig.FIX_PASSWORD)  # Password

        encoded = logon.encode()
        readable = encoded.replace(b'\x01', b'|').decode('latin-1')

        print("      Message built:")
        print(f"      {readable}")

    except Exception as e:
        print(f"      FAILED - {e}")
        sock.close()
        return False

    # Step 3: Send logon message
    print("\n[3/4] Sending logon message...")
    try:
        sock.sendall(encoded)
        print("      SUCCESS - Logon message sent")
    except Exception as e:
        print(f"      FAILED - {e}")
        sock.close()
        return False

    # Step 4: Wait for response
    print("\n[4/4] Waiting for server response...")
    parser = simplefix.FixParser()

    try:
        sock.settimeout(10)
        start_time = time.time()

        while time.time() - start_time < 10:
            try:
                data = sock.recv(4096)
                if not data:
                    print("      FAILED - Connection closed by server")
                    sock.close()
                    return False

                parser.append_buffer(data)
                msg = parser.get_message()

                if msg:
                    msg_type = msg.get(35)
                    readable_response = data.replace(b'\x01', b'|').decode('latin-1', errors='ignore')

                    print(f"\n      Received message type: {msg_type}")
                    print(f"      Full message: {readable_response}")

                    if msg_type == b'A':
                        print("\n" + "=" * 60)
                        print("SUCCESS - Logon accepted!")
                        print("=" * 60)

                        # Send logout to cleanly disconnect
                        logout = simplefix.FixMessage()
                        logout.begin_string = b'FIX.4.4'
                        logout.append_pair(35, "5", header=True)
                        logout.append_pair(49, fconfig.FIX_SENDER_COMP_ID, header=True)
                        logout.append_pair(56, fconfig.FIX_TARGET_COMP_ID, header=True)
                        logout.append_pair(34, 2, header=True)
                        logout.append_pair(52, datetime.utcnow().strftime("%Y%m%d-%H:%M:%S"), header=True)
                        sock.sendall(logout.encode())
                        time.sleep(0.5)
                        sock.close()
                        return True

                    elif msg_type == b'5':
                        # Logout - check reason
                        text = msg.get(58)  # Text field
                        print(f"\n      FAILED - Server sent logout")
                        if text:
                            print(f"      Reason: {text.decode()}")
                        print("\n" + "=" * 60)
                        print("TROUBLESHOOTING:")
                        print("- Check your FIX API credentials in fix_config.py")
                        print("- Verify FIX_PASSWORD is the FIX API password (not login password)")
                        print("- Ensure FIX API is enabled in your cTrader account settings")
                        print("- Check if using correct server (demo vs live)")
                        print("=" * 60)
                        sock.close()
                        return False

                    elif msg_type == b'3':
                        # Reject
                        text = msg.get(58)
                        ref_tag = msg.get(371)
                        print(f"\n      FAILED - Message rejected")
                        if text:
                            print(f"      Reason: {text.decode()}")
                        if ref_tag:
                            print(f"      Problem with tag: {ref_tag.decode()}")
                        sock.close()
                        return False

            except socket.timeout:
                continue

        print("      FAILED - Timeout waiting for response")
        sock.close()
        return False

    except Exception as e:
        print(f"      FAILED - {e}")
        sock.close()
        return False


if __name__ == "__main__":
    success = test_fix_connection()
    exit(0 if success else 1)
