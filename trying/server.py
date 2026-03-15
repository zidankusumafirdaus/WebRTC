import socket

server = socket.socket()
server.bind(('localhost', 9090))
server.listen(1)

print("Server is listening on port 9090...")
conn, addr = server.accept()
print(f"Connection established with {addr}")

while True:
    msg = conn.recv(1024).decode('utf-8')
    if msg.lower() == 'exit':
        print("Exiting server.")
        break
    print(f"Client: {msg}")

    response = input("You: ")
    conn.send(response.encode('utf-8'))
    if response.lower() == 'exit':
        print("Exiting server.")
        break
conn.close()