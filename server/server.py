# server/server.py
# Basic TCP server that listens for incoming client connections.
# Right now it just accepts a connection, prints a message, and closes.
# We'll add actual command handling in later commits.
#
# Ref: https://docs.python.org/3/library/socket.html
# Ref: https://docs.python.org/3/howto/sockets.html

import socket

HOST = "127.0.0.1"
PORT = 5001


def start_server():
    # Create a TCP socket (IPv4)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Let us reuse the port right away if we restart the server.
    # Without this you get "Address already in use" for like a minute.
    # Ref: https://docs.python.org/3/library/socket.html#socket.socket.setsockopt
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT} ...")

    try:
        while True:
            # This blocks until someone connects
            client_socket, address = server_socket.accept()
            print(f"[SERVER] Connection from {address[0]}:{address[1]}")

            # For now just read whatever the client sends and print it
            # We'll replace this with proper command handling later
            try:
                while True:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    print(f"[SERVER] Received: {data.decode('utf-8').strip()}")
            except ConnectionResetError:
                print(f"[SERVER] Client {address[0]}:{address[1]} disconnected unexpectedly")
            finally:
                client_socket.close()
                print(f"[SERVER] Connection closed with {address[0]}:{address[1]}")

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
