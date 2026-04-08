
# Helper functions for our wire protocol, used by both server and client.
# Centralizing these here keeps the protocol logic in one place so the
# server and client don't drift out of sync.
import socket
import sys

HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 4096   # chunk size in bytes for file transfers


def send_line(sock, message):
    """
    Send a newline-terminated UTF-8 string over the socket.

    We use sendall() instead of send() because send() might not push
    all bytes in one call — sendall() keeps going until everything
    is sent or an error occurs.
    """
    sock.sendall((message + "\n").encode("utf-8"))


def recv_line(sock):
    """
    Read one newline-terminated line from the socket.

    TCP doesn't have message boundaries — it's just a stream of bytes.
    So we read byte-by-byte until we hit a newline. This is fine for
    short command strings (not great for bulk data, but that's what
    send_file / recv_file are for).

    Returns the line without the newline, or "" if connection closed.
    """
    # Using a bytearray here instead of concatenating bytes objects
    # because bytearray.extend() is O(1) amortized while b"" + b"x"
    # creates a new object every time — small optimization but good habit.
    # Ref: https://docs.python.org/3/library/stdtypes.html#bytearray
    buf = bytearray()
    while True:
        byte = sock.recv(1)
        if not byte:
            return ""       # other side closed the connection
        if byte == b"\n":
            break
        buf.extend(byte)
    return buf.decode("utf-8")


def send_file(sock, filepath):
    """
    Stream a file's raw bytes over the socket in BUFFER_SIZE chunks.
    Opens in binary mode so the bytes go out exactly as they are on disk.
    """
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(BUFFER_SIZE)
            if not chunk:
                break
            sock.sendall(chunk)


def recv_file(sock, filesize, filepath, show_progress=False):
    """
    Receive exactly `filesize` bytes from the socket and write to `filepath`.

    We loop on recv() because one call might not return everything we
    asked for — TCP can deliver data in smaller pieces depending on
    network conditions and OS buffering.

    If show_progress is True, prints a simple progress bar to stdout.
    This is handy on the client side so the user can see something is
    actually happening during large transfers.
    """
    bytes_received = 0
    with open(filepath, "wb") as f:
        while bytes_received < filesize:
            # Only ask for as many bytes as we still need
            to_read = min(BUFFER_SIZE, filesize - bytes_received)
            chunk = sock.recv(to_read)
            if not chunk:
                raise ConnectionError("Connection lost during file transfer")
            f.write(chunk)
            bytes_received += len(chunk)

            # Print a progress bar if requested
            if show_progress and filesize > 0:
                _print_progress(bytes_received, filesize)

    if show_progress:
        print()  # newline after the progress bar


def _print_progress(current, total):
    """
    Overwrite the current terminal line with a simple progress bar.
    Example output:  [=========>          ] 47%

    Ref: Using \\r to overwrite lines — https://stackoverflow.com/a/3160819
    """
    bar_width = 30
    fraction = current / total
    filled = int(bar_width * fraction)
    bar = "=" * filled + ">" + " " * (bar_width - filled - 1)
    percent = int(fraction * 100)
    sys.stdout.write(f"\r  [{bar}] {percent}%")
    sys.stdout.flush()
