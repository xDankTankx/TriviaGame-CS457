import socket
import threading
import json
import logging

logging.basicConfig(level=logging.INFO)
clients = {}  # Dictionary to store clients and their usernames

def broadcast(message, sender_socket):
    """Send the message to all connected clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception as e:
                logging.error(f"Failed to send message to a client: {e}")
                client.close()
                del clients[client]  # Remove disconnected client

def handle_message(message, client_socket):
    """Process incoming JSON messages based on their type."""
    try:
        data = json.loads(message)
        message_type = data.get('type')

        if message_type == 'join':
            username = data['data']['username']
            if client_socket not in clients:
                clients[client_socket] = username
                logging.info(f"{username} has joined the game.")
                broadcast(json.dumps({"type": "system", "data": {"message": f"{username} has joined the game!"}}), client_socket)

        elif client_socket in clients:  # Ensure client has joined before proceeding
            username = clients[client_socket]

            if message_type == 'move':
                position = data['data']['position']
                logging.info(f"{username} made a move to position {position}")
                broadcast(json.dumps({"type": "move", "data": {"username": username, "position": position}}), client_socket)

            elif message_type == 'chat':
                chat_message = data['data']['message']
                logging.info(f"{username} says: {chat_message}")
                broadcast(json.dumps({"type": "chat", "data": {"username": username, "message": chat_message}}), client_socket)

            elif message_type == 'quit':
                logging.info(f"{username} has quit the game.")
                broadcast(json.dumps({"type": "system", "data": {"message": f"{username} has left the game!"}}), client_socket)
                del clients[client_socket]  # Remove client from the clients list

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode message: {e}")

def handle_client(client_socket, address):
    """Handle communication with a connected client."""
    logging.info(f"Connection from {address}")
    
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Client disconnected
            handle_message(message, client_socket)
    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        if client_socket in clients:
            username = clients[client_socket]
            logging.info(f"Disconnected from {username}")
            del clients[client_socket]  # Remove the client when they disconnect
        client_socket.close()

def start_server(host='127.0.0.1', port=65432):
    """Start the server and listen for incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Server started on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

start_server()
