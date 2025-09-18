import paramiko

hostname = "197.221.242.150"
port = 7507
username = "cmakara"
key_path = "/Users/russelmarange/.ssh/id_ed25519"

try:
    key = paramiko.Ed25519Key.from_private_key_file(key_path)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print("Connecting with key...")
    client.connect(hostname, port=port, username=username, pkey=key)
    print("Connected!")

    stdin, stdout, stderr = client.exec_command("whoami")
    print("Output:", stdout.read().decode().strip())

    client.close()
    print("Connection closed.")
except Exception as e:
    print("Error:", e)
