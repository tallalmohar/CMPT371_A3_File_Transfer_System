# server/server.py
# TCP server that listens for client connections and handles file uploads.
# Currently supports: UPLOAD, QUIT
# More commands (DOWNLOAD, LIST) coming in the next commit.
#
# Ref: https://docs.python.org/3/library/socket.html
# Ref: https://docs.python.org/3/howto/sockets.html

import socket
import os
import sys

# Add the project root so we can import shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.protocol import HOST, PORT, send_line, recv_line, recv_file

# Where uploaded files get saved
SERVER_FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "server_files")


def handle_upload(client_socket, filename, filesize):
    """
    Handle an incoming UPLOAD request.

    Steps:
      1. Sanitize the filename (strip directory parts for safety)
      2. Tell the client we're ready
      3. Receive the file bytes
      4. Confirm we got it
    """
    # os.path.basename strips directory components so a client can't
    # write to weird paths like "../../etc/something"
    # Ref: https://docs.python.org/3/library/os.path.html#os.path.basename
    safe_name = os.path.basename(filename)
    save_path = os.path.join(SERVER_FILES_DIR, safe_name)

    # Let the client know we're ready to receive
    send_line(client_socket, "OK ready")

    # Pull in the file data and write it to disk
    recv_file(client_socket, filesize, save_path)

    # Confirm receipt
    send_line(client_socket, f"OK {safe_name} received")
    print(f"  [UPLOAD] Saved {safe_name} ({filesize} bytes)")


def handle_client(client_socket, address):
    """
    Main loop for one connected client.
    Reads commands until QUIT or disconnect.
    """
    print(f"[CONNECTED] {address[0]}:{address[1]}")

    try:
        while True:
            line = recv_line(client_socket)
            if not line:
                # Empty means the client closed the connection
                break

            parts = line.split()
            command = parts[0].upper()

            if command == "UPLOAD" and len(parts) == 3:
                filename = parts[1]
                filesize = int(parts[2])
                handle_upload(client_socket, filename, filesize)

            elif command == "QUIT":
                break

            else:
                send_line(client_socket, f"ERROR unknown command: {line}")

    except (ConnectionResetError, BrokenPipeError, ConnectionError) as e:
        print(f"  [DISCONNECTED] {address[0]}:{address[1]} — {e}")
    finally:
        client_socket.close()
        print(f"[CLOSED] {address[0]}:{address[1]}")


def start_server():
    # Make sure the uploads folder exists
    # Ref: https://docs.python.org/3/library/os.html#os.makedirs
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER] Listening on {HOST}:{PORT} ...")

    try:
        while True:
            client_socket, address = server_socket.accept()
            # For now handle one client at a time — threading comes later
            handle_client(client_socket, address)

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
