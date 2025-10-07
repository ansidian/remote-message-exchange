# Chat Application for Remote Message Exchange

## Overview

This is a TCP-based chat application that enables message exchange among remote peers. The application integrates both client and server functionality into a single program, allowing peers to establish connections, send messages, and manage multiple concurrent connections using socket programming.

## Requirements

- Python 3

## Running the Program

```bash
./chat <port>
```

Where `<port>` is the port number on which the process will listen for incoming connections.

**Example:**

```bash
./chat 4545
```

## Functionality

The application provides a CLI with the following functionality:

### `help`

Display information about available user interface options or command manual.

### `myip`

Display the IP address of this process. Note: This will show the actual IP address of the computer, not the local address (127.0.0.1).

### `myport`

Display the port on which this process is listening for incoming connections.

### `connect <destination> <port>`

Establish a new TCP connection to the specified destination IP address and port number. The application handles invalid IPs, self-connections, and duplicate connections with appropriate error messages.

**Example:**

```bash
connect 192.168.1.100 4545
```

### `list`

Display a numbered list of all connections this process is part of, including both outgoing and incoming connections. Shows the IP address and listening port of connected peers.

**Example output:**

```
id: IP address Port No.
1: 192.168.21.21 4545
2: 192.168.21.22 5454
3: 192.168.21.23 5000
```

### `terminate <connection id>`

Terminate the connection specified by the connection ID from the list command.

**Example:**

```bash
terminate 2
```

### `send <connection id> <message>`

Send a message (up to 100 characters) to the peer specified by the connection ID. Messages are displayed on the receiver's screen with sender information.

**Example:**

```bash
send 3 Hello, how are you?
```

**Receiver output format:**

```
Message received from 192.168.21.21
Sender's Port: <port number>
Message: "<received message>"
```

### `exit`

Close all connections and terminate the process. Other connected peers will be notified and will update their connection lists.

## Contributors

### Andy ([@ansidian](https://github.com/ansidian))
- Server initialization and connection acceptance functions
- Client connection functions
- Message handling functions
- Main program and command loop

### Joshua Soteras ([@soterasjoshua](https://github.com/soterasjoshua))
- Command handler functions
- Connection management functions
- Command parsing functions

### Sanskar Thapa ([@sskarz](https://github.com/sskarz))
- Utility functions
- Notification functions
