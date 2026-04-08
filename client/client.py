# client/client.py
# Interactive CLI client for the file transfer system.
# Currently supports: Upload, Quit
# Download and List will be added next.
#
# Ref: https://docs.python.org/3/library/socket.html

import socket
import os
import sys

# Add project root so we can import shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.protocol import HOST, PORT, send_line, recv_line, send_file


def upload_file(sock):
    """
    Prompt the user for a file path, then upload it to the server.

    Protocol:
      1. Send "UPLOAD <filename> <filesize>"
      2. Wait for "OK ready"
      3. Stream the file bytes
      4. Wait for "OK <filename> received"
    """
    filepath = input("Enter the path to the file you want to upload: ").strip()

    # Make sure the file actually exists before bothering the server
    if not os.path.isfile(filepath):
        print(f"Error: file not found — {filepath}")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    # Tell the server what's coming
    send_line(sock, f"UPLOAD {filename} {filesize}")

    # Wait for the go-ahead
    response = recv_line(sock)
    if not response.startswith("OK"):
        print(f"Server error: {response}")
        return

    # Send the actual file data
    print(f"[UPLOAD] Uploading {filename} ({filesize} bytes)...")
    send_file(sock, filepath)

    # Wait for confirmation
    confirmation = recv_line(sock)
    print(f"[UPLOAD] {confirmation}")


def show_menu():
    """Print the main menu options."""
    print("----------------------------------------")
    print("File Transfer Client")
    print("----------------------------------------")
    print("1. Upload a file")
    print("2. Download a file")
    print("3. List files on server")
    print("4. Quit")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(f"Could not connect to server at {HOST}:{PORT}. Is it running?")
        return

    print(f"Connected to server at {HOST}:{PORT}")

    try:
        while True:
            show_menu()
            choice = input("Select an option: ").strip()

            if choice == "1":
                upload_file(sock)
            elif choice == "2":
                print("[TODO] Download not implemented yet.")
            elif choice == "3":
                print("[TODO] List not implemented yet.")
            elif choice == "4":
                send_line(sock, "QUIT")
                print("Disconnected from server.")
                break
            else:
                print("Invalid option. Please enter 1, 2, 3, or 4.")
    except (ConnectionResetError, BrokenPipeError):
        print("Lost connection to server.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
