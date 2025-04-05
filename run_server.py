import os
import sys
import socket
from server_test import start_test_server

def get_ip_addresses():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    try:
        # Get the public IP (this requires internet access)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        public_ip = s.getsockname()[0]
        s.close()
    except:
        public_ip = "Could not determine (check internet connection)"
    
    return local_ip, public_ip

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    port = 5555  # Default port
    
    local_ip, public_ip = get_ip_addresses()
    
    print("=" * 50)
    print("  CHESS ONLINE SERVER")
    print("=" * 50)
    print("\nIP Addresses for clients to connect to:")
    print(f"  • Local network (LAN): {local_ip}:{port}")
    print(f"  • Public (require port forwarding): {public_ip}:{port}")
    print("\nClient connection instructions:")
    print("  1. To connect from this computer: Use 'localhost' or '127.0.0.1'")
    print(f"  2. To connect from other devices on same network: Use '{local_ip}'")
    print("  3. To connect from outside your network:")
    print("     - Set up port forwarding on your router for port 5555")
    print(f"     - Clients use your public IP: {public_ip}")
    print("\nRun the client with:")
    print(f"  python client.py --host <IP_ADDRESS> --port {port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    print("\nStarting server...\n")
    
    # Start the server
    start_test_server('', port)

if __name__ == "__main__":
    main() 