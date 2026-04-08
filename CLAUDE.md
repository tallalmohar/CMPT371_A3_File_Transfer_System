# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

CMPT 371 Assignment 3 — TCP-based File Transfer System using Python's socket API. Client-server architecture where a central server stores files and handles multiple clients concurrently via threading.

No external dependencies — uses only Python standard library (`socket`, `threading`, `os`, `sys`). Requires Python 3.7+.

## Commands

```bash
# Start server (binds to 127.0.0.1:5001, creates server_files/ automatically)
python server/server.py

# Start client (interactive menu: upload, download, list, quit)
python client/client.py
```

## Architecture

Three packages:
- **`server/`** — TCP server using one daemon thread per client (`threading` module). Stores uploaded files in `server_files/`.
- **`client/`** — Interactive CLI client. Downloads saved to `downloads/`.
- **`shared/`** — Shared protocol utilities (e.g., `protocol.py`).

Both `server_files/` and `downloads/` are gitignored runtime directories.

## Wire Protocol

Text-based application-layer protocol over TCP. Commands are UTF-8 newline-terminated lines. File data is raw bytes transferred in 4096-byte chunks.

| Operation | Client sends | Server responds |
|-----------|-------------|-----------------|
| Upload | `UPLOAD <filename> <filesize>\n` → raw bytes | `OK ready\n` → `OK <filename> received\n` |
| Download | `DOWNLOAD <filename>\n` | `FILEDATA <filename> <filesize>\n` → raw bytes |
| List | `LIST\n` | `FILELIST <count>\n` → `<filename> <size>\n` per file |
| Quit | `QUIT\n` | Server closes connection |

Key implementation details:
- Use `socket.sendall()` (not `send()`) for reliable delivery
- Loop on `recv()` until all expected bytes are received (TCP is a byte stream)
- `SO_REUSEADDR` set on server socket for fast restart
- `os.path.basename()` on uploaded filenames to prevent path traversal
