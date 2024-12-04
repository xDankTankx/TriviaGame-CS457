import socket
import threading
import json
import logging
import random
import argparse

logging.basicConfig(level=logging.INFO)

clients = {}  # Dictionary to store clients and their usernames
current_turn = None  # Track whose turn it is
next_position = 1  # Track the next position number to assign
questions = []  # Array to store trivia questions
current_question = None  # Store the current trivia question
correct_player = None  # Track who answered correctly
total_players = None  # Total number of players expected

# Game State
game_state = {
    "players": {},  # Tracks player usernames and scores
    "current_question": None,
    "turn": None,  # Current player's turn
    "total_players": None,  # Number of players set by the first client
    "winner": None,  # Winner's username when determined
    "game_over": False  # Whether the game is over
}

# Initialize trivia question bank
def initialize_questions():
    """Initialize the question databank as a tuple-based list."""
    global questions
    questions = [
        ("What is the capital of France?", ["Paris", "London", "Berlin", "Rome"], 1),
        ("Which planet is known as the Red Planet?", ["Earth", "Mars", "Jupiter", "Saturn"], 2),
        ("Who wrote 'To Kill a Mockingbird'?", ["Harper Lee", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"], 1),
        ("What is the smallest prime number?", ["1", "2", "3", "5"], 2),
        ("What is the boiling point of water in Celsius?", ["90", "95", "100", "110"], 3),
        ("Which element has the chemical symbol 'O'?", ["Oxygen", "Osmium", "Gold", "Silver"], 1),
        ("Who painted the Mona Lisa?", ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Claude Monet"], 1),
        ("What is the largest ocean on Earth?", ["Atlantic", "Pacific", "Indian", "Arctic"], 2),
        ("In which year did World War II end?", ["1942", "1945", "1948", "1950"], 2),
        ("What is the chemical formula for water?", ["H2O", "CO2", "NaCl", "O2"], 1),
    ]

# Function to pick and remove a random question
def get_random_question():
    """Pick and remove a random question, returning only the question and options."""
    global questions, current_question
    if len(questions) == 0:
        return None  # No more questions available

    # Randomly select a question tuple
    question_tuple = random.choice(questions)
    questions.remove(question_tuple)  # Remove it from the databank
    current_question = question_tuple  # Store the full tuple for server-side use

    # Return only the question and options to be sent to the client
    return {"question": question_tuple[0], "options": question_tuple[1]}

def reset_game_state():
    """Reset the game state for a new round."""
    global game_state
    game_state["players"] = {player: 0 for player in game_state["players"]}  # Reset scores
    game_state["current_question"] = None
    game_state["turn"] = None
    game_state["winner"] = None
    game_state["game_over"] = False
    initialize_questions()  # Reinitialize question bank
    broadcast(json.dumps({"type": "system", "data": {"message": "Game reset. Starting a new round!"}}))

# Function to handle trivia questions
def send_question():
    """Send the current question to all clients."""
    question_data = get_random_question()
    if question_data:
        broadcast(json.dumps({
            "type": "question",
            "data": question_data  # Send only the question and options
        }))
    else:
        logging.info("No more questions available.")
        broadcast(json.dumps({
            "type": "system",
            "data": {
                "message": "No more questions available. The game has ended!"
            }
        }))

def send_current_question(client_socket):
    """Send the current question to a specific client if one is active."""
    if current_question:
        client_socket.send(json.dumps({
            "type": "question",
            "data": {
                "question": current_question["question"],
                "options": current_question["options"]
            }
        }).encode('utf-8'))

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
    formatted_state = {
        "players": {
            username: {
                "position": player_data.get("position", "N/A"),
                "score": player_data.get("score", 0)
            } for username, player_data in game_state["players"].items()
        }
    }
    broadcast(json.dumps({"type": "game_state", "data": formatted_state}))

def handle_turn_progression():
    """Advance the turn to the next player and notify all clients."""
    global current_turn, correct_player

    if game_state["game_over"]:
        return  # Stop turn progression if the game is over

    client_list = list(clients.keys())
    if not client_list:
        return  # No clients to handle

    # Get the current index of the player whose turn it is
    current_index = client_list.index(current_turn) if current_turn in client_list else -1
    next_index = (current_index + 1) % len(client_list)  # Circularly progress to the next player
    current_turn = client_list[next_index]

    # Notify all clients about the turn update
    broadcast(json.dumps({
        "type": "turn_update",
        "data": {"current_turn": clients[current_turn]}
    }))

    # If the next turn cycles back to the first player, send a new question
    if next_index == 0:  # Check if we've cycled back to the first player
        correct_player = None  # Reset correct player for the next question
        threading.Timer(3, send_question).start()  # Slight delay before sending the next question



def handle_answer(data, client_socket):
    """Handle a player's answer and check correctness."""
    global current_question, game_state, current_turn

    username = clients[client_socket]
    answer = data.get('answer')  # Player's submitted answer

    # Store the player's answer in their game state for later validation
    if current_question and answer:
        game_state["players"][username]["current_answer"] = answer
        logging.info(f"Player {username} submitted answer: {answer}")
    else:
        logging.info(f"No active question or invalid answer from {username}.")

    # Mark the player as having completed their turn
    game_state["players"][username]["answered"] = True
    logging.info(f"Player {username} marked as 'answered'.")

    # Check if all players have answered
    if all(player_data.get("answered", False) for player_data in game_state["players"].values()):
        # Validate answers and update scores
        correct_choice = current_question[2]  # Correct answer index (1-based)
        for player, data in game_state["players"].items():
            if data.get("current_answer") == str(correct_choice):  # Compare as string
                data["score"] += 1  # Increment score for correct answer
                logging.info(f"Player {player} answered correctly! New score: {data['score']}")
            else:
                logging.info(f"Player {player} answered incorrectly.")

        # Reset 'answered' and 'current_answer' for all players
        for data in game_state["players"].values():
            data["answered"] = False
            data.pop("current_answer", None)  # Remove temporary answer

        # Broadcast the updated game state (gameboard)
        formatted_state = {
            "players": {
                user: {
                    "position": player.get("position", "N/A"),
                    "score": player.get("score", 0)
                } for user, player in game_state["players"].items()
            }
        }
        broadcast(json.dumps({"type": "game_state", "data": formatted_state}))

        # Announce the end of the round
        broadcast(json.dumps({"type": "system", "data": {"message": "Round complete! Check the scoreboard."}}))

        # Reset to the first player's turn and send a new question
        client_list = list(clients.keys())
        if client_list:
            current_turn = client_list[0]
            broadcast(json.dumps({
                "type": "turn_update",
                "data": {"current_turn": clients[current_turn]}
            }))
            threading.Timer(3, send_question).start()  # Delay before the next question
    else:
        # Progress the turn to the next player
        handle_turn_progression()

def handle_message(message, client_socket):
    """Process incoming JSON messages based on their type."""
    global current_turn, next_position, total_players
    try:
        data = json.loads(message)
        message_type = data['type']

        if message_type == 'total_players' and total_players is None:
            # Set the total number of players
            total_players = int(data['data']['count'])
            logging.info(f"Total players set to {total_players}. Waiting for players to join.")
            broadcast(json.dumps({
                "type": "system",
                "data": {"message": f"Waiting for {total_players} players to join."}
            }))

        elif message_type == 'join':
            username = data['data']['username']
            if client_socket not in clients:
                clients[client_socket] = username
                game_state["players"][username] = {"position": next_position, "score": 0, "answered": False}
                next_position += 1
                logging.info(f"{username} has joined the game.")
                
                # Broadcast system message about new join
                broadcast(json.dumps({"type": "system", "data": {"message": f"{username} has joined the game!"}}))
                
                # Broadcast the updated game state to all clients
                broadcast_game_state()

                # Start the game when all players join
                if total_players and len(clients) == total_players:
                    logging.info(f"All {total_players} players have joined. Starting the game.")
                    current_turn = list(clients.keys())[0]  # Set the first turn
                    send_question()  # Start trivia
                    broadcast(json.dumps({"type": "turn_update", "data": {"current_turn": clients[current_turn]}}))

        elif client_socket in clients:  # Handle game actions
            username = clients[client_socket]
            
            if message_type == 'answer' and client_socket == current_turn:
                handle_answer(data, client_socket)
            
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
                broadcast_game_state()
                if client_socket == current_turn:
                    handle_turn_progression()

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode message: {e}")
        
        # Function to handle a single client
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

def start_server(host='0.0.0.0', port=65433):
    """Start the server and listen for incoming connections."""
    initialize_questions()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Server started on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

# Function to parse command-line arguments
def parse_server_args():
    parser = argparse.ArgumentParser(description="Start the trivia game server.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port for the server to listen on.")
    return parser.parse_args()

# Main execution entry point
if __name__ == "__main__":
    args = parse_server_args()
    start_server(port=args.port)