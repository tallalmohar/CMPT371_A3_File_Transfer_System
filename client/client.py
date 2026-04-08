# client/client.py
# Interactive CLI client for the file transfer system.
# Supports: Upload, Download, List, Quit
#
# Ref: https://docs.python.org/3/library/socket.html

import socket
import os
import sys

# Add project root so we can import shared/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.protocol import HOST, PORT, send_line, recv_line, send_file, recv_file

# Where downloaded files get saved
DOWNLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "downloads")


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


def download_file(sock):
    """
    Ask the server for a file by name and save it locally.

    Protocol:
      1. Send "DOWNLOAD <filename>"
      2. Server responds with "FILEDATA <filename> <filesize>" or "ERROR ..."
      3. Receive the raw file bytes
    """
    filename = input("Enter the filename to download: ").strip()
    if not filename:
        print("Error: no filename provided.")
        return

    send_line(sock, f"DOWNLOAD {filename}")

    # See what the server says
    response = recv_line(sock)
    if response.startswith("ERROR"):
        print(f"Server: {response}")
        return

    # Parse "FILEDATA <filename> <filesize>"
    parts = response.split()
    if len(parts) != 3 or parts[0] != "FILEDATA":
        print(f"Unexpected response: {response}")
        return

    server_filename = parts[1]
    filesize = int(parts[2])

    # Make sure the downloads folder exists
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    save_path = os.path.join(DOWNLOADS_DIR, server_filename)

    print(f"[DOWNLOAD] Downloading {server_filename} ({filesize} bytes)...")
    recv_file(sock, filesize, save_path, show_progress=True)
    print(f"[DOWNLOAD] Saved to {save_path}")


def list_files(sock):
    """
    Ask the server what files it has and print them out.

    Protocol:
      1. Send "LIST"
      2. Server responds with "FILELIST <count>"
      3. Read <count> lines, each is "<filename> <size>"
    """
    send_line(sock, "LIST")

    response = recv_line(sock)
    parts = response.split()
    if len(parts) != 2 or parts[0] != "FILELIST":
        print(f"Unexpected response: {response}")
        return

    count = int(parts[1])
    if count == 0:
        print("No files on the server.")
        return

    print("Files available on server:")
    for _ in range(count):
        file_info = recv_line(sock)
        # Split from the right so filenames with spaces don't break things
        info_parts = file_info.rsplit(" ", 1)
        name = info_parts[0]
        size = info_parts[1] if len(info_parts) == 2 else "?"
        print(f"  {name}  ({size} bytes)")


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
                download_file(sock)
            elif choice == "3":
                list_files(sock)
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
