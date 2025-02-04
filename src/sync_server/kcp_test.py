from aiokcp.sync import KCPSocket

server = KCPSocket.create_server(('127.0.0.1', 18586))
client1_socket = KCPSocket.create_connection(('127.0.0.1', 18586))
server_sock1, _ = server.accept()
client2_socket = KCPSocket.create_connection(('127.0.0.1', 18586))
server_sock2, _ = server.accept()
server_sock1.send(b'123')
print(client1_socket.recv(100))
client1_socket.send(b'234')
client2_socket.send(b'567')
print(server_sock1.recv(100))
print(server_sock2.recv(100))