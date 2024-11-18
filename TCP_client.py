import socket
import threading
import json
import logging
import sys
import time

logging.basicConfig(level=logging.INFO)

username = None
stop_flag = False
current_turn = None
client_socket = None  # Make the socket globally accessible for sending messages

def receive_messages(client_socket):
    """Receive messages from the server and print them."""
    global stop_flag, current_turn
    buffer = ""
    while not stop_flag:
        try:
            buffer += client_socket.recv(1024).decode('utf-8')
            messages = buffer.split('\n')
            buffer = messages.pop()  # Keep the last part in buffer if it's incomplete
            
            for message in messages:
                if message:
                    sys.stdout.write('\r' + ' ' * len("Enter message type (move, chat, quit, answer): ") + '\r')
                    sys.stdout.flush()

                    logging.info(f"New message: {message}")
                    process_server_message(message)

                    print("Enter message type (move, chat, quit, answer): ", end='', flush=True)
                
        except Exception as e:
            if not stop_flag:
                logging.error(f"Error receiving message: {e}")
            break

def process_server_message(message):
    """Parse and process messages from the server."""
    global current_turn, client_socket
    try:
        data = json.loads(message)
        message_type = data['type']

        if message_type == 'system':
            system_message = data['data']['message']
            logging.info(f"System Message: {system_message}")
            print(f"System: {system_message}")
            
        elif message_type == 'prompt':  # Handle the prompt for total players
            prompt_message = data['data']['message']
            logging.info(f"Prompt Message: {prompt_message}")
            print(f"{prompt_message}")
            num_players = input("Enter the total number of players: ")
            send_message(client_socket, 'total_players', {"count": num_players})

        elif message_type == 'chat':
            logging.info(f"{data['data']['username']}: {data['data']['message']}")
            print(f"{data['data']['username']}: {data['data']['message']}")

        elif message_type == 'move':
            logging.info(f"{data['data']['username']} moved to position {data['data']['position']}")
            print(f"{data['data']['username']} moved to position {data['data']['position']}")

        elif message_type == 'game_state':
            render_game_state(data['data'])

        elif message_type == 'turn_update':
            current_turn = data['data']['current_turn']
            logging.info(f"It's now {current_turn}'s turn!")
            print(f"It's now {current_turn}'s turn!")

        elif message_type == 'question':
            render_question(data['data'])

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode server message: {e}")

def render_game_state(game_state):
    """Render the game state for display."""
    print("\nCurrent Game State:")
    for player, state in game_state.items():
        print(f"{player} - Position: {state['position']}, Score: {state['score']}")

def render_question(question_data):
    """Render the trivia question for the player."""
    print("\nTrivia Question:")
    print(question_data['question'])
    for i, option in enumerate(question_data['options'], start=1):
        print(f"{i}. {option}")
    print("\nAnswer the question during your turn by entering the number of your choice!")

def send_message(client_socket, message_type, data):
    """Send a JSON-encoded message to the server."""
    message = json.dumps({
        "type": message_type,
        "data": data
    })
    client_socket.send(message.encode('utf-8'))

def connect_to_server(host='127.0.0.1', port=65433):
    """Connect to the server and start receiving/sending messages."""
    global username, stop_flag, current_turn, client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        logging.info("Connected to server")

        # Check if this is the first client and prompt for total players
        is_first_client = input("Are you the first client to join? (yes/no): ").lower()
        if is_first_client == "yes":
            total_players = input("Enter the total number of players: ")
            send_message(client_socket, 'total_players', {"count": total_players})

        # Enter username
        while not username:
            username = input("Enter your username: ")
            send_message(client_socket, 'join', {"username": username})

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.start()

        while True:
            if current_turn == username:
                msg_type = input("Enter message type (move, chat, quit, answer): ")
                
                if msg_type == 'move':
                    position = input("Enter your move position: ")
                    send_message(client_socket, 'move', {"position": position})

                elif msg_type == 'chat':
                    chat_msg = input("Enter your message: ")
                    send_message(client_socket, 'chat', {"message": chat_msg})

                elif msg_type == 'quit':
                    send_message(client_socket, 'quit', {})
                    break

                elif msg_type == 'answer':
                    answer = input("Enter your answer to the trivia question: ")
                    send_message(client_socket, 'answer', {"answer": answer})

            elif current_turn:
                print(f"Waiting for {current_turn}'s turn.")
                time.sleep(5)

    except socket.error as e:
        logging.error(f"Error: {e}")
    finally:
        stop_flag = True
        client_socket.close()
        logging.info("Disconnected from server")
        receive_thread.join()

connect_to_server()
