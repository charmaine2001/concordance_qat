import paramiko

hostname = "197.221.242.150"
port = 7507
username = "cmakara"
password = "server2025#"   # replace with your actual password

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting...")
    client.connect(hostname, port=port, username=username, password=password)
    print("Connected!")

    stdin, stdout, stderr = client.exec_command("whoami")
    print("Output:", stdout.read().decode().strip())

    client.close()
    print("Connection closed.")
except Exception as e:
    print("Error:", e)
