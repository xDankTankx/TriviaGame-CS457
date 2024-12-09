import socket
import threading
import json
import argparse
import sys

# Suppress unnecessary logging on the client side
import logging
logging.basicConfig(level=logging.WARNING)

username = None
stop_flag = False
client_socket = None  # Make the socket globally accessible for sending messages


def receive_messages(client_socket):
    """Receive messages from the server and print them."""
    global stop_flag
    buffer = ""
    while not stop_flag:
        try:
            buffer += client_socket.recv(1024).decode('utf-8')
            while '\n' in buffer:  # Process each complete JSON message
                message, buffer = buffer.split('\n', 1)
                if message:
                    process_server_message(message)
        except Exception as e:
            if not stop_flag:
                print(f"Error receiving message: {e}")
            break

def process_server_message(message):
    """Parse and process messages from the server."""
    global client_socket, stop_flag
    try:
        data = json.loads(message)
        message_type = data['type']

        if message_type == 'system':
            render_system_message(data['data']['message'])
            if "shutting down" in data['data']['message'].lower():
                print("\nThank you for playing! Disconnecting...")
                print("Please press CTRL+C to return to your terminal.")
                stop_flag = True
                client_socket.close()
                sys.exit(0)  # Exit the program

        elif message_type == 'chat':
            print(f"{data['data']['username']}: {data['data']['message']}")

        elif message_type == 'game_state':
            render_game_state(data['data'])
            render_system_message("Scoreboard updated!")

        elif message_type == 'question':
            render_question(data['data'])

    except json.JSONDecodeError as e:
        print(f"Failed to decode server message: {e}")


def render_game_state(game_state):
    """Render the game state for display."""
    print("\n========================================")
    print("🏆 Current Game State 🏆")
    print("========================================")
    print(f"{'Player':<15} {'Score':<10}")
    print("----------------------------------------")

    for player, details in game_state["players"].items():
        score = details.get("score", 0)
        print(f"{player:<15} {score:<10}")

    print("========================================")


def render_question(question_data):
    """Render the trivia question for the player."""
    print("\n" + "=" * 40)
    print(f"🎯 Trivia Question 🎯 | Questions Remaining: {question_data.get('questions_remaining', 'N/A')}")
    print("=" * 40)
    print(question_data['question'])
    print("\nOptions:")
    for i, option in enumerate(question_data['options'], 1):
        print(f"  {i}. {option}")
    print("=" * 40)
    print("Answer by typing the option number!")
    print("=" * 40 + "\n")


def render_system_message(message):
    """Display system messages in a formatted way."""
    print("\n" + "=" * 40)
    print(f"📢 System Message: {message}")
    print("=" * 40 + "\n")


def send_message(client_socket, message_type, data):
    """Send a JSON-encoded message to the server."""
    message = json.dumps({
        "type": message_type,
        "data": data
    })
    client_socket.send(message.encode('utf-8'))


def parse_client_args():
    """Parse command-line arguments for the client."""
    parser = argparse.ArgumentParser(description="Connect to the trivia game server.")
    parser.add_argument("-i", "--ip", type=str, required=True, help="Server IP or DNS name.")
    parser.add_argument("-p", "--port", type=int, required=True, help="Port to connect to.")
    return parser.parse_args()


def get_valid_answer():
    """Prompt the user for a valid answer between 1 and 4."""
    while True:
        try:
            answer = int(input("Enter your answer (1-4): "))
            if 1 <= answer <= 4:
                return answer
            else:
                print("Invalid choice. Please enter a number between 1 and 4.")
        except ValueError:
            print("Invalid input. Please enter a numeric value between 1 and 4.")


def connect_to_server():
    """Connect to the server and start receiving/sending messages."""
    global username, stop_flag, client_socket

    args = parse_client_args()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((args.ip, args.port))

        # Enter username
        while not username:
            username = input("Enter your username: ")
            send_message(client_socket, 'join', {"username": username})

        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        receive_thread.daemon = True  # Ensure thread exits with the main program
        receive_thread.start()

        while not stop_flag:
            try:
                msg_type = input("Enter message type (chat, quit, answer): ")

                if stop_flag:  # Check if shutdown message was received
                    break

                if msg_type == 'chat':
                    chat_msg = input("Enter your message: ")
                    send_message(client_socket, 'chat', {"message": chat_msg})

                elif msg_type == 'quit':
                    send_message(client_socket, 'quit', {})
                    stop_flag = True
                    break

                elif msg_type == 'answer':
                    answer = get_valid_answer()
                    send_message(client_socket, 'answer', {"answer": answer})

            except KeyboardInterrupt:
                print("\nExiting the game. Goodbye!")
                stop_flag = True
                break

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        stop_flag = True
        print("\nDisconnected from server.")
        if client_socket:
            client_socket.close()
        sys.exit(0)  # Ensure immediate exit


if __name__ == "__main__":
    connect_to_server()
