# client/client.py
# TCP client that connects to the server and shows an interactive menu.
# For now we just connect and loop the menu — actual commands come later.
#
# Ref: https://docs.python.org/3/library/socket.html

import socket

HOST = "127.0.0.1"
PORT = 5001


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
    # Connect to the server
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
                print("[TODO] Upload not implemented yet.")
            elif choice == "2":
                print("[TODO] Download not implemented yet.")
            elif choice == "3":
                print("[TODO] List not implemented yet.")
            elif choice == "4":
                # Send a quit message so the server knows we're leaving
                sock.sendall(b"QUIT\n")
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
