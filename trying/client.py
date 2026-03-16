import socket

client = socket.socket()
client.connect(("localhost", 9090))
print("Connected to the server on port 9090.")

while True:
    msg = input("You: ")
    client.send(msg.encode("utf-8"))
    if msg.lower() == "exit":
        print("Exiting client.")
        break

    response = client.recv(1024).decode("utf-8")
    if response.lower() == "exit":
        print("Exiting client.")
        break
    print(f"Server: {response}")
client.close()
