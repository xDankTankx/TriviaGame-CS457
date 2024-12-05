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
    """Initialize the question databank as a hash map."""
    global questions
    
questions = {
    "What is the capital of France?": {
        "options": ["Paris", "London", "Berlin", "Rome"],
        "correct": 1,  # Correct: Paris
    },
    "Which planet is known as the Red Planet?": {
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "correct": 2,  # Correct: Mars
    },
    "Who wrote 'To Kill a Mockingbird'?": {
        "options": ["Harper Lee", "Mark Twain", "J.K. Rowling", "Ernest Hemingway"],
        "correct": 1,  # Correct: Harper Lee
    },
    "What is the smallest prime number?": {
        "options": ["1", "2", "3", "5"],
        "correct": 2,  # Correct: 2
    },
    "What is the tallest mountain in the world?": {
        "options": ["K2", "Mount Everest", "Kangchenjunga", "Makalu"],
        "correct": 2,  # Correct: Mount Everest
    },
    "Who painted the ceiling of the Sistine Chapel?": {
        "options": ["Leonardo da Vinci", "Michelangelo", "Raphael", "Donatello"],
        "correct": 2,  # Correct: Michelangelo
    },
    "Which chemical element has the symbol 'He'?": {
        "options": ["Hydrogen", "Helium", "Hafnium", "Holmium"],
        "correct": 2,  # Correct: Helium
    },
    "In what year did the Titanic sink?": {
        "options": ["1912", "1920", "1905", "1898"],
        "correct": 1,  # Correct: 1912
    },
    "Which country is known as the Land of the Rising Sun?": {
        "options": ["China", "Japan", "Thailand", "South Korea"],
        "correct": 2,  # Correct: Japan
    },
    "What is the square root of 144?": {
        "options": ["10", "11", "12", "13"],
        "correct": 3,  # Correct: 12
    },
    "Who was the first president of the United States?": {
        "options": ["Thomas Jefferson", "George Washington", "John Adams", "James Madison"],
        "correct": 2,  # Correct: George Washington
    },
    "What is the largest mammal in the world?": {
        "options": ["Elephant", "Blue Whale", "Great White Shark", "Giraffe"],
        "correct": 2,  # Correct: Blue Whale
    },
    "Which city hosted the 2012 Summer Olympics?": {
        "options": ["Beijing", "London", "Rio de Janeiro", "Tokyo"],
        "correct": 2,  # Correct: London
    },
    "What is the freezing point of water in Celsius?": {
        "options": ["-1", "0", "1", "100"],
        "correct": 2,  # Correct: 0
    },
    "What is the main ingredient in guacamole?": {
        "options": ["Tomato", "Avocado", "Lime", "Onion"],
        "correct": 2,  # Correct: Avocado
    },
}

def get_random_question():
    """Get a random question from the hash map."""
    global questions
    if not questions:
        return None  # No questions left

    # Randomly select a question
    question_text = random.choice(list(questions.keys()))
    question_data = questions[question_text]

    # Remove the question from the hash map (optional, if you don't want repeats)
    del questions[question_text]

    # Return the question text, options, and correct answer index
    return question_text, question_data["options"], question_data["correct"]

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

def send_question():
    """Send the next question to all clients and set the current question."""
    global current_question, questions

    # Fetch a random question
    question_data = get_random_question()
    if question_data:
        question_text, options, correct_choice = question_data
        # Set the global current question
        current_question = {
            "text": question_text,
            "options": options,
            "correct": correct_choice,
        }

        logging.info(f"New question: {question_text} (Correct answer index: {correct_choice})")
        # Broadcast the question and options along with the questions remaining
        broadcast(json.dumps({
            "type": "question",
            "data": {
                "question": question_text,
                "options": options,
                "questions_remaining": len(questions)  # Include questions remaining
            }
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

    # Check if a question is active
    if not current_question:
        logging.error("No active question set!")
        broadcast(json.dumps({"type": "system", "data": {"message": "No active question!"}}))
        return

    # Unpack the current question details
    question_text = current_question["text"]
    options = current_question["options"]
    correct_choice = current_question["correct"]

    logging.info(f"Current question: {question_text}")
    logging.info(f"Options: {options}")
    logging.info(f"Correct answer index: {correct_choice}")
    logging.info(f"Player {username} submitted answer: {answer}")

    # Validate the player's answer
    if str(answer) == str(correct_choice):  # Ensure both are strings for comparison
        game_state["players"][username]["score"] += 1  # Increment score
        logging.info(f"{username} answered correctly! New score: {game_state['players'][username]['score']}")
        broadcast(json.dumps({"type": "system", "data": {"message": f"{username} answered correctly!"}}))
    else:
        logging.info(f"{username} answered incorrectly.")
        broadcast(json.dumps({"type": "system", "data": {"message": f"{username} answered incorrectly."}}))

    # Check for a win condition
    if game_state["players"][username]["score"] >= 5:
        logging.info(f"Game over! {username} wins with a score of 5.")
        broadcast_game_state()  # Show the final scoreboard
        broadcast(json.dumps({"type": "system", "data": {"message": f"Congratulations, {username}! You Won!"}}))
        reset_game_state()  # Optionally reset the game for another round
        return  # Stop further processing as the game is over

    # Mark the player as having completed their turn
    game_state["players"][username]["answered"] = True
    logging.info(f"Player {username} marked as 'answered'.")

    # Check if all players have answered
    if all(player_data.get("answered", False) for player_data in game_state["players"].values()):
        # Reset 'answered' for all players
        for player_data in game_state["players"].values():
            player_data["answered"] = False

        # Broadcast updated game state (gameboard)
        broadcast_game_state()

        # Announce round results
        broadcast(json.dumps({"type": "system", "data": {"message": "Round complete! Check the scoreboard."}}))

        # Reset to the first player's turn and send a new question
        client_list = list(clients.keys())
        if client_list:
            current_turn = client_list[0]
            broadcast(json.dumps({
                "type": "turn_update",
                "data": {"current_turn": clients[current_turn]}
            }))
            threading.Timer(3, send_question).start()  # Delay before next question
    else:
        # Progress the turn to the next player
        handle_turn_progression()

def handle_message(message, client_socket):
    """Process incoming JSON messages based on their type."""
    global current_turn, next_position, total_players
    try:
        logging.info(f"Raw message from client: {message}")  # Log raw data for debugging
        data = json.loads(message)
        logging.info(f"Parsed data: {data}")  # Log parsed JSON
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
                handle_answer(data['data'], client_socket)
            
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