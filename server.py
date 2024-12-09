import socket
import threading
import json
import logging
import random
import argparse
import sys

logging.basicConfig(level=logging.INFO)

clients = {}  # Dictionary to store clients and their usernames
questions = []  # Array to store trivia questions
current_question = None  # Store the current trivia question
server_socket = None

# Game State
game_state = {
    "players": {},  # Tracks player usernames and scores
    "current_question": None,
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

    question_text = random.choice(list(questions.keys()))
    question_data = questions.pop(question_text)
    return question_text, question_data["options"], question_data["correct"]


def send_question():
    """Send a new question to all clients."""
    global current_question

    question_data = get_random_question()
    if question_data:
        question_text, options, correct_choice = question_data
        current_question = {
            "text": question_text,
            "options": options,
            "correct": correct_choice,
        }
        logging.info(f"New question: {question_text}")
        broadcast(json.dumps({
            "type": "question",
            "data": {
                "question": question_text,
                "options": options,
                "questions_remaining": len(questions)
            }
        }))
    else:
        broadcast(json.dumps({
            "type": "system",
            "data": {"message": "No more questions available. The game has ended!"}
        }))
        shutdown_game()

def broadcast(message):
    """Send the message to all connected clients."""
    for client in list(clients.keys()):
        try:
            client.send((message + "\n").encode('utf-8'))
        except Exception as e:
            logging.error(f"Error broadcasting to a client: {e}")
            client.close()
            del clients[client]


def handle_answer(data, client_socket):
    """Handle a player's answer and check correctness."""
    global current_question, game_state

    username = clients[client_socket]
    answer = data.get('answer')

    if not current_question:
        client_socket.send(json.dumps({
            "type": "system",
            "data": {"message": "No active question to answer!"}
        }).encode('utf-8'))
        return

    if game_state["players"][username].get("answered", False):
        client_socket.send(json.dumps({
            "type": "system",
            "data": {"message": "You have already answered this question!"}
        }).encode('utf-8'))
        return

    correct_choice = current_question["correct"]
    if str(answer) == str(correct_choice):
        game_state["players"][username]["score"] += 1
        game_state["players"][username]["answered_correctly"] = True
    else:
        game_state["players"][username]["answered_correctly"] = False

    game_state["players"][username]["answered"] = True

    if all(player["answered"] for player in game_state["players"].values()):
        end_round()


def end_round():
    """Process the end of a round."""
    global current_question

    correct_players = [user for user, data in game_state["players"].items() if data.get("answered_correctly")]
    broadcast(json.dumps({
        "type": "system",
        "data": {
            "message": f"Round complete! Correct answers: {', '.join(correct_players) if correct_players else 'None'}"
        }
    }))

    for player_data in game_state["players"].values():
        player_data["answered"] = False
        player_data["answered_correctly"] = False

    broadcast_game_state()

    for username, player_data in game_state["players"].items():
        if player_data["score"] >= 5:
            broadcast_game_state()  # Broadcast the final scoreboard
            broadcast(json.dumps({
                "type": "system",
                "data": {"message": f"Congratulations, {username}! You Won!"}
            }))
            shutdown_game()
            return

    send_question()
    
def broadcast_game_state():
    """Broadcast the current game state with dynamic ranking."""
    ranked_players = sorted(
        game_state["players"].items(),
        key=lambda item: item[1]["score"],
        reverse=True
    )
    formatted_state = {
        "players": {
            username: {
                "position": rank + 1,
                "score": data["score"]
            } for rank, (username, data) in enumerate(ranked_players)
        }
    }
    broadcast(json.dumps({
        "type": "game_state",
        "data": formatted_state
    }))

def send_current_question(client_socket):
    """Send the current question to a specific client if one is active."""
    if current_question:
        try:
            client_socket.send(json.dumps({
                "type": "question",
                "data": {
                    "question": current_question["text"],
                    "options": current_question["options"],
                    "questions_remaining": len(questions)
                }
            }).encode('utf-8'))
        except Exception as e:
            logging.error(f"Error sending current question to client: {e}")


def handle_message(message, client_socket):
    """Process incoming JSON messages based on their type."""
    global current_question

    try:
        logging.info(f"Raw message from client: {message}")
        data = json.loads(message)
        message_type = data['type']

        if message_type == 'join':
            username = data['data']['username']
            if client_socket not in clients:
                clients[client_socket] = username
                game_state["players"][username] = {"score": 0, "answered": False, "answered_correctly": False}
                logging.info(f"{username} has joined the game.")

                # Notify all clients about the new player
                broadcast(json.dumps({
                    "type": "system",
                    "data": {"message": f"{username} has joined!"}
                }))

                # Send the active question to the newly joined client
                if current_question:
                    send_current_question(client_socket)

                # Broadcast updated game state to all clients
                broadcast_game_state()

                # Broadcast the current question to all clients
                if current_question:
                    broadcast(json.dumps({
                        "type": "question",
                        "data": {
                            "question": current_question["text"],
                            "options": current_question["options"],
                            "questions_remaining": len(questions)
                        }
                    }))

                # Start the game if this is the first player
                if len(clients) == 1 and not current_question:
                    send_question()

        elif message_type == 'answer':
            handle_answer(data["data"], client_socket)

        elif message_type == 'chat':
            chat_message = data['data']['message']
            username = clients.get(client_socket, "Unknown")
            logging.info(f"{username} says: {chat_message}")
            broadcast(json.dumps({
                "type": "chat",
                "data": {"username": username, "message": chat_message}
            }))

        elif message_type == 'quit':
            username = clients.get(client_socket, "Unknown")
            logging.info(f"{username} has quit the game.")
            broadcast(json.dumps({
                "type": "system",
                "data": {"message": f"{username} has left the game!"}
            }))

            # Remove the player from the game state
            if client_socket in clients:
                del clients[client_socket]
            if username in game_state["players"]:
                del game_state["players"][username]

            broadcast_game_state()

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode message: {e}")

def handle_client(client_socket, address):
    """Handle a single client."""
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            handle_message(message, client_socket)
    except Exception as e:
        logging.error(f"Client error: {e}")
    finally:
        username = clients.pop(client_socket, None)
        if username:
            logging.info(f"{username} disconnected.")
            broadcast_game_state()
        client_socket.close()


def shutdown_game():
    """Shut down the server."""
    logging.info("Shutting down server...")
    broadcast(json.dumps({"type": "system", "data": {"message": "Server shutting down. Thank you for playing!"}}))
    for client in list(clients.keys()):
        client.close()
    if server_socket:
        server_socket.close()
    sys.exit(0)


def start_server(port):
    """Start the server."""
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    logging.info(f"Server started on port {port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()
    except KeyboardInterrupt:
        shutdown_game()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the trivia server.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port number to listen on.")
    args = parser.parse_args()

    initialize_questions()
    start_server(args.port)