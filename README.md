# **CMPT 371 A3 Socket Programming `File Transfer System`**

**Course:** CMPT 371 \- Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  
<span style="color: purple;">**_RUBRIC NOTE: As per submission guidelines, only one group member will submit the link to this repository on Canvas._**</span>

## **Group Members**

| Name   | Student ID | Email        |
| :----- | :--------- | :----------- |
| Name 1 | 301465076  | tma79@sfu.ca |
| Name 2 | 301452022  | vwl29@sfu.ca |

## **1\. Project Overview & Description**

This project is a TCP-based File Transfer System built using Python's Socket API. It follows a client-server architecture where a central server stores files and handles multiple clients concurrently. Clients can **upload** files to the server, **download** files from the server, and **list** all available files — all over a persistent TCP connection. The server uses threading to handle multiple simultaneous clients without blocking.

## **2\. System Limitations & Edge Cases**

As required by the project specifications, we have identified and handled (or defined) the following limitations and potential issues within our application scope:

- **Handling Multiple Clients Concurrently:**
  - <span style="color: green;">_Solution:_</span> We utilized Python's `threading` module. Each client connection is handed off to a dedicated daemon thread (`handle_client`), allowing the main server loop to continue accepting new connections without blocking.
  - <span style="color: red;">_Limitation:_</span> Thread creation is bounded by system resources. A production system would use a thread pool (`concurrent.futures.ThreadPoolExecutor`) or async I/O (`asyncio`) to scale to thousands of simultaneous connections.

- **TCP Stream Buffering (Partial Reads/Writes):**
  - <span style="color: green;">_Solution:_</span> TCP is a byte stream, not a message stream — a single `send()` may not deliver all bytes in one `recv()`. We handle this by looping on `recv()` until the expected number of bytes (specified in the file header) have been fully received before proceeding.
  - <span style="color: red;">_Limitation:_</span> Very large files increase memory pressure on slow networks. We mitigate this with a fixed `BUFFER_SIZE = 4096` bytes for chunked transfer, but there is no explicit file size cap enforced.

- **Client Disconnection Mid-Transfer:**
  - <span style="color: green;">_Solution:_</span> All socket operations on the server are wrapped in `try/except` blocks catching `ConnectionResetError` and `BrokenPipeError`. If a client disconnects mid-transfer, the server logs the event, cleans up the socket, and the thread exits gracefully without crashing the server.
  - <span style="color: red;">_Limitation:_</span> Partially uploaded files are not automatically removed from the server's storage directory. The server may be left with an incomplete file if the client drops during an upload.

- **Filename Collisions:**
  - <span style="color: red;">_Limitation:_</span> If a client uploads a file with the same name as an existing file on the server, the existing file is silently overwritten. There is no versioning or conflict resolution mechanism in this implementation.

- **Security:**
  - <span style="color: red;">_Limitation:_</span> There is no authentication, authorization, or encryption. Any client that can reach the server's IP and port can upload or download any file. This application is intended for trusted local network use only.

## **3\. Video Demo**

Our 2-minute video demonstration covering server startup, client connection, file upload, file download, listing files, and process termination can be viewed below:  
[**▶️ Watch Project Demo**](./a3_videodemo.mp4)

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

- **Python 3.7** or higher.
- No external pip installations are required (uses standard `socket`, `threading`, `os`, `sys` libraries).
- (Optional) VS Code or any terminal emulator.

<span style="color: purple;">**_RUBRIC NOTE: No external libraries are required. A `requirements.txt` is included but contains no installable packages — the entire project runs on Python's standard library._**</span>

## **5\. Step-by-Step Run Guide**

<span style="color: purple;">**_RUBRIC NOTE: The grader must be able to copy-paste these commands._**</span>

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/tallalmohar/CMPT371_A3_File_Transfer_System.git
cd CMPT371_A3_File_Transfer_System
```

### **Step 2: Start the Server**

Open a terminal and run the server. It will bind to `127.0.0.1` on port `5001` and create a `server_files/` directory automatically to store uploaded files.

```bash
python server/server.py
# Console output: "[SERVER] Listening on 127.0.0.1:5001 ..."
```

### **Step 3: Connect a Client**

Open a **new** terminal window (keep the server running). Run the client script.

```bash
python client/client.py
# Console output:
# Connected to server at 127.0.0.1:5001
# ----------------------------------------
# File Transfer Client
# ----------------------------------------
# 1. Upload a file
# 2. Download a file
# 3. List files on server
# 4. Quit
# Select an option:
```

### **Step 4: Upload a File**

From the client menu, select option `1` and provide a path to any file on your machine:

```
Select an option: 1
Enter the path to the file you want to upload: /path/to/your/file.txt
# Console output: "[UPLOAD] Uploading file.txt (1024 bytes)..."
# Console output: "[UPLOAD] file.txt uploaded successfully."
```

### **Step 5: List Files on the Server**

Select option `3` to see all files currently stored on the server:

```
Select an option: 3
# Console output:
# Files available on server:
#   file.txt  (1024 bytes)
```

### **Step 6: Download a File**

Select option `2` and enter the filename. The file will be saved to the local `downloads/` directory (created automatically).

```
Select an option: 2
Enter the filename to download: file.txt
# Console output: "[DOWNLOAD] Downloading file.txt (1024 bytes)..."
# Console output: "[DOWNLOAD] file.txt saved to downloads/file.txt"
```

### **Step 7: Quit**

Select option `4` to cleanly disconnect from the server:

```
Select an option: 4
# Console output: "Disconnected from server."
```

### **Step 8: Multiple Clients (Optional)**

Open additional terminal windows and run `python client/client.py` in each. The server handles all clients concurrently via threading — they do not block each other.

## **6\. Technical Protocol Details**

We designed a simple text-based application-layer protocol over TCP:

- **Command Format:** Commands are UTF-8 strings sent as a single newline-terminated line.
- **Upload Phase:**
  - Client sends: `UPLOAD <filename> <filesize>\n`
  - Server responds: `OK ready\n`
  - Client sends: raw file bytes (`filesize` bytes total, chunked at 4096 bytes)
  - Server responds: `OK <filename> received\n`
- **Download Phase:**
  - Client sends: `DOWNLOAD <filename>\n`
  - Server responds: `FILEDATA <filename> <filesize>\n`
  - Server sends: raw file bytes (`filesize` bytes total, chunked at 4096 bytes)
- **List Phase:**
  - Client sends: `LIST\n`
  - Server responds: `FILELIST <count>\n` followed by `<filename> <size>\n` per file
- **Termination:**
  - Client sends: `QUIT\n`
  - Server closes the connection

## **7\. Academic Integrity & References**

<span style="color: purple;">**_RUBRIC NOTE: List all references used and help you got._**</span>

- **Code Origin:**
  - The overall socket server/client structure was written by the group based on the course tutorials and lecture material. The chunked file transfer loop, `SO_REUSEADDR` socket option, and `os.path.basename` path sanitization were adapted from the references listed below. All protocol design, threading logic, and command handling were written by us.

- **GenAI Usage:**
  - Claude Code (Anthropic) was used to help scaffold the project structure, assist with implementation of `shared/protocol.py`, `server/server.py`, and `client/client.py`, and to generate and format this README.

- **Specific code references:**
  - `socket.sendall()` vs `socket.send()` — why we use sendall for reliable delivery:
    [Python Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html#using-a-socket)
  - `socket.setsockopt(SO_REUSEADDR)` — lets the server restart without waiting for port release:
    [Python `socket` module docs](https://docs.python.org/3/library/socket.html#socket.socket.setsockopt)
  - Threading model (one thread per client, daemon threads):
    [Real Python — Intro to Python Threading](https://realpython.com/intro-to-python-threading/)
  - `os.path.basename()` for stripping directory components from uploaded filenames (path traversal prevention):
    [Python `os.path` docs](https://docs.python.org/3/library/os.path.html#os.path.basename)
  - `os.makedirs(exist_ok=True)` for auto-creating storage directories:
    [Python `os` docs](https://docs.python.org/3/library/os.html#os.makedirs)
  - `bytearray` for efficient incremental byte buffering in `recv_line()`:
    [Python `bytearray` docs](https://docs.python.org/3/library/stdtypes.html#bytearray)
  - Using `\r` (carriage return) to overwrite terminal lines for the download progress bar:
    [Stack Overflow — Overwrite console output](https://stackoverflow.com/a/3160819)
  - General reference throughout: [Python `socket` module documentation](https://docs.python.org/3/library/socket.html)
