import socket
import threading
import select
import sys

server_socket = None
listening_port = None
peer_connections = {}
connection_counter = 0
server_running = False

# connection management
def initialize_server(port):
    """Initialize server socket to listen for incoming connections"""
    global server_socket, listening_port, server_running

    try:
        server_socket = socket.socket()
        server_socket.bind(("", port))

        listening_port = port

        server_socket.listen(10)
        server_running = True

        thread = threading.Thread(target=accept_connections, daemon=True)
        thread.start()
    
    except OSError as e:
        print(f"Error: Unable to bind to port {port}. The port may already be in use.")
        sys.exit(1)

def accept_connections():
    """Accept incoming connections and add to peer list"""
    global server_socket, peer_connections, connection_counter, server_running

    while server_running:
        try:
            connection_socket, address = server_socket.accept()
            connection_counter += 1
            peer_connections[connection_counter] = {
                'socket': connection_socket,
                'ip': address[0],
                'port': address[1]
            }

            print(f"Connection accepted from {address[0]}:{address[1]}")

            thread = threading.Thread(target=receive_messages, args=(connection_socket, address[0], address[1]), daemon=True)
            thread.start()
        except:
            break



# client
def connect_to_peer(destination, port):
    """Establish outgoing connection to a peer"""
    global peer_connections, connection_counter

    try:
        client_socket = socket.socket()
        client_socket.connect((destination, port))
        connection_counter += 1
        peer_connections[connection_counter] = {
            'socket': client_socket,
            'ip': destination,
            'port': port
        }

        print(f"Successfully connected to {destination}:{port}")
        notification = "CONNECTED"
        client_socket.send(notification.encode())

        thread = threading.Thread(target=receive_messages, args=(client_socket, destination, port), daemon=True)
        thread.start()
        return True
    except:
        return False


def terminate_connection(connection_id, peer_connections):
    #Josh
    """
        - Terminate a specific connection by ID
        - Remove Conncection within peer_connections Dictionary 
        - Send error message if not found within dictionary or error
    """
    #Find if key (connection_id) exist within the dictionary (peer_connections)
    if connection_id in peer_connections: 

        #pop from dictionary removes (key and value)  and deletes it entirely while returning value
        closeConnection = peer_connections.pop(connection_id)

        #close the socket connection
        try: 

            #.close() terminates network socket connection 
            closeConnection.close()
            print(f"Connection {connection_id} has been terminated!.")

        #handle errors if socket cannot close for some reason e
        except Exception as e:

            print(f"An error occurred while atteping to closing connection {connection_id}: {e}")
    
    #if the key (connection_id) doesn't exist within the dict then say not found to user
    else:

        print(f"Connection ID {connection_id} not found with peer_connections")


def cleanup_connections(peer_connections, server_socket):
    #Josh
    """
        Close all connections on exit
        Make sure dictionary is empty.
        Have to close the main server socket
    """

    #Display size dictionary (size of connections)
    print(f"Number of connection(s) to close: {len(peer_connections)}")
    
    for uID in peer_connections:
        
        socketObj = peer_connections.pop(uID)
        
        #Close Socket
        try: 
            socketObj.close()
        
        #if there is an error than the client socket might be closed
        except Exception as e:
            
            print(f"An error occurred while atteping to closing connection {socketObj}: {e}")

    #Double checking that the dictionary is completed cleared
    peer_connections.clear()
    print(f"Closed and cleared {len(peer_connections)} client connection(s).")

    #Close out the main server socket
    if server_socket:
        try:
            server_socket.close()
            print("Main server socket has been closed.")
        except Exception as e:
            print(f"Error closing the server socket: {e}")



# Message handling
def send_message(connection_id, message):
    """Send message to specified peer"""
    if connection_id in peer_connections:
        try:
            peer_connections[connection_id]['socket'].send(message.encode())
            print(f"Message sent to {connection_id}")
            return True
        except:
            return False
    return False


def receive_messages(peer_socket, sender_ip, sender_port):
    """Handle incoming messages from a peer"""
    while True:
        try: 
            data = peer_socket.recv(1024)
            if not data:
                break

            message = data.decode()
            if message == "CONNECTED":
                print(f"Peer {sender_ip}:{sender_port} has connected.")
            else:
                print(f"Message received from sender {sender_ip}")
                print(f"Sender's Port: {sender_port}")
                print(f"Message: {message}")
        except:
            break

def broadcast_exit_notification():
    """Notify all peers that this process is exiting"""
    exit_message = "EXIT"
    for conn_id, conn in peer_connections.items():
        try:
            conn['socket'].send(exit_message.encode())
        except:
            pass


# Utility functions
def get_my_ip():
    """Get actual IP address of this machine (not 127.0.0.1)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine IP address"


def validate_ip(ip_address):
    """Validate IP address format"""
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        return False


def is_duplicate_connection(ip, port):
    """Check if connection already exists"""
    for conn in peer_connections.values():
        if conn['ip'] == ip and conn['port'] == port:
            return True
    return False


def is_self_connection(ip, port):
    """Check if trying to connect to self"""
    my_ip = get_my_ip()
    return (ip == my_ip or ip == "127.0.0.1" or ip == "localhost") and port == listening_port


# Command handlers
def help():
    """Display available commands"""
    # TODO: print available commands
    pass


def myip():
    """Display this process's IP address"""
    # TODO: print get_my_ip() result
    pass


def myport():
    """Display this process's listening port"""
    # TODO: print listening_port
    pass


def connect(args):
    """Handle connect command"""
    # TODO: parse args, validate, call connect_to_peer()
    pass


def list():
    """Display all connections"""
    # TODO: print formatted list of peer_connections
    pass


def terminate(args):
    """Handle terminate command"""
    # TODO: parse connection_id, call terminate_connection()
    pass


def send(args):
    """Handle send command"""
    # TODO: parse connection_id and message, call send_message()
    pass


def exit():
    """Handle exit command"""
    # TODO: notify peers, cleanup, and sys.exit()
    pass


# Command line interface
def parse_command(command_line):
    """Parse user input into command and arguments"""
    # TODO: split input into command and args
    pass


def command_loop():
    """Main command loop for user input"""
    # TODO: input loop that dispatches to command handlers
    pass


# Main program
def main():
    """Main entry point"""
    # TODO: parse sys.argv, start server, start command loop
    pass


if __name__ == "__main__":
    main()