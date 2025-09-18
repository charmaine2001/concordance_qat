from sshtunnel import SSHTunnelForwarder

server = SSHTunnelForwarder(
    ("197.221.242.150", 7507),        # SSH host and port
    ssh_username="cmakara",           # <-- replace with your SSH username
    ssh_password="charmie123*",       # <-- replace with your SSH password
    remote_bind_address=("127.0.0.1", 5432),
    local_bind_address=("127.0.0.1", 6543)  # bind locally to port 6543
)

print("Starting tunnel...")
server.start()
print(f"Tunnel open. Connect to localhost:{server.local_bind_port}")

input("Press Enter to close tunnel...")
server.stop()
print("Tunnel closed.")
