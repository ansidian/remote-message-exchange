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
    #Josh
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
    #Josh 
    """Display available commands"""
    print("  myip                          - Display IP address of this process")
    print("  myport                        - Display the port this process is listening on")
    print("  connect <destination> <port>  - Connect to a peer at destination:port")
    print("  list                          - Display list of all connections")
    print("  terminate <connection id>     - Terminate the connection with the specified ID")
    print("  send <connection id> <message>- Send a message to the specified connection")
    print("  exit                          - Close all connections and exit")


def myip():
    #Josh
    """Display this process's IP address"""
    ip = get_my_ip() #Under utility functions
    print(f"My IP address: {ip}")


def myport():
    #Josh
    """Display this process's listening port"""
    if listening_port: #listening_port is a global var/type boolean
        print(f"My port: {listening_port}")
    else:
        print("Server not initialized")
    

def connect(args):
    #Josh
    """Handle connect command"""

    #should be at least two arguments: destination and port
    if len(args) < 2:
        print("Error: connect command requires <destination> <port>")
        return
    
    destination = args[0]
    
    try:
        port = int(args[1])

    except ValueError:
        print("Error: Port must be a valid integer")
        return
    
    # Validate IP address
    if not validate_ip(destination): #utility function
        print(f"Error: Invalid IP address format: {destination}")
        return
    
    # Check if trying to connect to self
    if is_self_connection(destination, port): #utility function
        print("Error: Cannot connect to yourself")
        return
    
    #Check for duplicate connection
    if is_duplicate_connection(destination, port): #utility function
        print(f"Error: Already connected to {destination}:{port}")
        return
    
    # Attempt connection
    success = connect_to_peer(destination, port)  #client connection
    if not success:
        print(f"Error: Failed to connect to {destination}:{port}")


def list():
    """Display all connections"""
    #check if dictionary is empty 
    if not peer_connections:
        print("No active connections")
        return
    
    #Display results 
    print(f"\nid: IP address              Port No.")
    for conn_id, conn_info in peer_connections.items():
        print(f"{conn_id}:  {conn_info['ip']:<20} {conn_info['port']}")


def terminate(args):
    #Josh
    """Handle terminate command"""
    #Argument must be at least one: connection id
    if len(args) < 1:
        print("Error: terminate command requires <connection id>")
        return
    
    #validate if the argument is an actually integer
    try:
        connection_id = int(args[0])
    except ValueError:
        print("Error: Connection ID must be a valid integer")
        return


def send(args):
    #Josh
    """Handle send command"""
    #arguments must have two: connetion id and message 
    if len(args) < 2:
        print("Error: send command requires <connection id> <message>")
        return

    #validate connection id is an int 
    try:
        connection_id = int(args[0])
    #if not an int print invalid argument for conneciton id
    except ValueError:
        print("Error: Connection ID must be a valid integer")
        return

    # Join remaining args as the message
    message = ' '.join(args[1:])
    

    success = send_message(connection_id, message) #message handling function

    #if the message failed to send
    if not success:
        print(f"Error: Failed to send message to connection {connection_id}")


def exit():
    """Handle exit command"""
    #ensure we are accessing the serving_running var 
    #Boolean value 
    global server_running
    
    
    print("Exiting...")
    broadcast_exit_notification() #client function
    server_running = False

    #client connection section
    #ensure that all connections are close
    #client connections
    cleanup_connections(peer_connections, server_socket)
    sys.exit(0)


# Command line interface
def parse_command(command_line):
    """Parse user input into command and arguments"""
    #.strip method removes and leading and trailing whitespace
    #.splite method breaks a string into list of substrings
    parts = command_line.strip().split()
    if not parts:
        return None, []
    
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def command_loop():
    while True:
        try:
        
            command_line = input()
            command, args = parse_command(command_line)
            
            if command is None:
                continue 
            
            if command == "help":
                help()
            elif command == "myip":
                myip()
            elif command == "myport":
                myport()
            elif command == "connect":
                connect(args)
            elif command == "list":
                list()
            elif command == "terminate":
                terminate(args)
            elif command == "send":
                send(args)
            elif command == "exit":
                exit()
            else:
                print(f"Unknown command: {command}. Type 'help' for available commands.")
        
        except EOFError:
            exit()
        except KeyboardInterrupt:
            print("\nUse 'exit' command to quit")


# Main program
def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Error:, please specify Port using: python chat.py <port>")
        sys.exit(1)

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Error: Port must be a valid integer")
        sys.exit(1)

    if port < 1024 or port > 65535:
        print("Error: Port must be in range 1024-65535")
        sys.exit(1)

    initialize_server(port)

    print("=" * 50)
    print("P2P Chat Application Started")
    print("=" * 50)
    print(f"Listening on IP: {get_my_ip()}")
    print(f"Listening on Port: {listening_port}")
    print("\nType 'help' for available commands")
    print("=" * 50)

    command_loop()


if __name__ == "__main__":
    main()