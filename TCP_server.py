import socket
import threading
import json
import logging

logging.basicConfig(level=logging.INFO)
clients = {}  # Dictionary to store clients and their usernames
game_state = {}  # Game state to track players' positions, scores, and turns
current_turn = None  # Track whose turn it is
next_position = 1  # Track the next position number to assign

def broadcast(message, sender_socket=None):
    """Send the message to all connected clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send((message + "\n").encode('utf-8'))
            except Exception as e:
                logging.error(f"Failed to send message to a client: {e}")
                client.close()
                if client in clients:
                    del clients[client]

def broadcast_game_state():
    """Broadcast the entire game state to all clients."""
    broadcast(json.dumps({"type": "game_state", "data": game_state}))

def handle_turn_progression():
    """Advance the turn to the next player and notify all clients."""
    global current_turn
    client_list = list(clients.keys())
    if client_list:
        # Rotate to the next client in the list
        current_index = client_list.index(current_turn) if current_turn in client_list else -1
        next_index = (current_index + 1) % len(client_list)
        current_turn = client_list[next_index]
        
        # Broadcast the current turn to all clients
        broadcast(json.dumps({"type": "turn_update", "data": {"current_turn": clients[current_turn]}}))

def handle_message(message, client_socket):
    """Process incoming JSON messages based on their type."""
    global current_turn, next_position
    try:
        data = json.loads(message)
        message_type = data.get('type')

        if message_type == 'join':
            username = data['data']['username']
            if client_socket not in clients:
                clients[client_socket] = username
                game_state[username] = {"position": next_position, "score": 0}
                next_position += 1  # Increment position for the next player
                logging.info(f"{username} has joined the game.")
                
                # Broadcast system message about new join
                broadcast(json.dumps({"type": "system", "data": {"message": f"{username} has joined the game!"}}))
                
                # Broadcast the updated game state to all clients
                broadcast_game_state()

                # Set the first client as the current turn if current_turn is None
                if current_turn is None:
                    current_turn = client_socket
                
                # Broadcast the current turn to all clients
                broadcast(json.dumps({"type": "turn_update", "data": {"current_turn": clients[current_turn]}}))

        elif client_socket in clients:  # Ensure client has joined before proceeding
            username = clients[client_socket]

            if message_type == 'move' and client_socket == current_turn:
                position = data['data']['position']
                game_state[username]["position"] = position
                game_state[username]["score"] += 1  # Example score increment for a move
                logging.info(f"{username} moved to position {position}")

                # Broadcast the updated game state to all clients
                broadcast_game_state()

                # Progress the turn after a valid move
                handle_turn_progression()

            elif message_type == 'chat':
                chat_message = data['data']['message']
                logging.info(f"{username} says: {chat_message}")
                broadcast(json.dumps({"type": "chat", "data": {"username": username, "message": chat_message}}))

            elif message_type == 'quit':
                logging.info(f"{username} has quit the game.")
                broadcast(json.dumps({"type": "system", "data": {"message": f"{username} has left the game!"}}))
                if client_socket in clients:
                    del clients[client_socket]
                if username in game_state:
                    del game_state[username]
                
                # Broadcast updated game state after player quits
                broadcast_game_state()

                # If the quitting player was the current turn, progress the turn
                if client_socket == current_turn:
                    handle_turn_progression()

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
            del clients[client_socket]
            if username in game_state:
                del game_state[username]
            broadcast_game_state()
            # If the disconnected client was the current turn, progress the turn
            if client_socket == current_turn:
                handle_turn_progression()
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
