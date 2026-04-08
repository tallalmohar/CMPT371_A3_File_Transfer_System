
# TCP server that listens for client connections and handles commands.
# Supports: UPLOAD, DOWNLOAD, LIST, QUIT

import socket
import os
import sys
import threading

# Add the project root so we can import shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.protocol import HOST, PORT, send_line, recv_line, send_file, recv_file

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


def handle_download(client_socket, filename):
    """
    Handle a DOWNLOAD request.

    If the file exists, send its size then stream the bytes.
    If not, send an error line so the client knows what happened.
    """
    safe_name = os.path.basename(filename)
    filepath = os.path.join(SERVER_FILES_DIR, safe_name)

    if not os.path.isfile(filepath):
        send_line(client_socket, f"ERROR file not found: {safe_name}")
        print(f"  [DOWNLOAD] File not found: {safe_name}")
        return

    filesize = os.path.getsize(filepath)

    # Tell the client what's coming: name and size
    send_line(client_socket, f"FILEDATA {safe_name} {filesize}")

    # Stream the file
    send_file(client_socket, filepath)
    print(f"  [DOWNLOAD] Sent {safe_name} ({filesize} bytes)")


def handle_list(client_socket):
    """
    Send back a list of all files currently stored on the server.

    Protocol:
      1. Send "FILELIST <count>"
      2. For each file send "<filename> <size>"
    """
    try:
        files = os.listdir(SERVER_FILES_DIR)
    except FileNotFoundError:
        files = []

    send_line(client_socket, f"FILELIST {len(files)}")
    for fname in files:
        fpath = os.path.join(SERVER_FILES_DIR, fname)
        fsize = os.path.getsize(fpath)
        send_line(client_socket, f"{fname} {fsize}")

    print(f"  [LIST] Sent file list ({len(files)} files)")


def handle_client(client_socket, address):
    """
    Main loop for one connected client. Runs in its own thread.

    Keeps reading newline-terminated commands from the socket and
    dispatching them to the appropriate handler. The loop ends when
    the client sends QUIT, closes the connection, or something breaks.
    """
    print(f"[CONNECTED] {address[0]}:{address[1]}")

    try:
        while True:
            # Block until we get a full line (or the connection drops)
            line = recv_line(client_socket)
            if not line:
                # recv_line returns "" when the socket is closed
                break

            # Parse the command — first word is the action, rest are args
            parts = line.split()
            command = parts[0].upper()

            if command == "UPLOAD" and len(parts) == 3:
                filename = parts[1]
                filesize = int(parts[2])
                handle_upload(client_socket, filename, filesize)

            elif command == "DOWNLOAD" and len(parts) == 2:
                filename = parts[1]
                handle_download(client_socket, filename)

            elif command == "LIST":
                handle_list(client_socket)

            elif command == "QUIT":
                break

            else:
                send_line(client_socket, f"ERROR unknown command: {line}")

    except (ConnectionResetError, BrokenPipeError, ConnectionError) as e:
        # Client dropped mid-transfer or mid-command — not our fault,
        # just log it and clean up. The thread exits, server keeps running.
        print(f"  [DISCONNECTED] {address[0]}:{address[1]} — {e}")
    except ValueError as e:
        # Bad data from the client (e.g. non-numeric filesize)
        print(f"  [ERROR] Bad request from {address[0]}:{address[1]} — {e}")
    except Exception as e:
        # Catch-all so one buggy client can never crash the whole server
        print(f"  [ERROR] Unexpected error with {address[0]}:{address[1]} — {e}")
    finally:
        client_socket.close()
        print(f"[CLOSED] {address[0]}:{address[1]}")


def start_server():
    """
    Entry point. Creates the server socket, binds it, and enters
    the accept loop. Each new client gets its own daemon thread.
    """
    # Create the storage directory if it doesn't already exist
    # Ref: https://docs.python.org/3/library/os.html#os.makedirs
    os.makedirs(SERVER_FILES_DIR, exist_ok=True)

    # AF_INET  = IPv4 addressing
    # SOCK_STREAM = TCP (reliable, ordered byte stream)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR lets us restart the server immediately after stopping it.
    # Without this the OS keeps the port in TIME_WAIT for ~60 seconds.
    # Ref: https://docs.python.org/3/library/socket.html#socket.socket.setsockopt
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind((HOST, PORT))
    server_socket.listen()  # mark the socket as passive (ready to accept)
    print(f"[SERVER] Listening on {HOST}:{PORT} ...")

    try:
        while True:
            client_socket, address = server_socket.accept()

            # Spin up a new thread for each client so they don't block
            # each other. daemon=True means these threads die automatically
            # when the main thread exits (no orphaned threads on Ctrl+C).
            # Ref: https://realpython.com/intro-to-python-threading/
            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address),
                daemon=True,
            )
            thread.start()
            print(f"[ACTIVE] {threading.active_count() - 1} client(s) connected")

    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
