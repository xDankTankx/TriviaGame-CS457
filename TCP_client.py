import socket
import threading
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)

username = None
stop_flag = False

def receive_messages(client_socket):
    """Receive messages from the server and print them."""
    global stop_flag
    while not stop_flag:  
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                sys.stdout.write('\r' + ' ' * len("Enter message type (move, chat, quit): ") + '\r')
                sys.stdout.flush()

                logging.info(f"New message: {message}")
                process_server_message(message)

                print("Enter message type (move, chat, quit): ", end='', flush=True)
            else:
                break
        except Exception as e:
            if not stop_flag: 
                logging.error(f"Error receiving message: {e}")
            break

def process_server_message(message):
    """Parse and process messages from the server."""
    try:
        data = json.loads(message)
        message_type = data.get('type')

        if message_type == 'system':
            logging.info(f"System Message: {data['data']['message']}")

        elif message_type == 'chat':
            logging.info(f"{data['data']['username']}: {data['data']['message']}")

        elif message_type == 'move':
            logging.info(f"{data['data']['username']} moved to position {data['data']['position']}")

    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode server message: {e}")

def send_message(client_socket, message_type, data):
    """Send a JSON-encoded message to the server."""
    message = json.dumps({
        "type": message_type,
        "data": data
    })
    client_socket.send(message.encode('utf-8'))

def connect_to_server(host='127.0.0.1', port=65432):
    """Connect to the server and start receiving/sending messages."""
    global username, stop_flag
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        logging.info("Connected to server")

        while not username:
            username = input("Enter your username: ")
            send_message(client, 'join', {"username": username})

        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        while True:
            msg_type = input("Enter message type (move, chat, quit): ")
            
            if msg_type == 'move':
                position = input("Enter your move position: ")
                send_message(client, 'move', {"username": username, "position": position})

            elif msg_type == 'chat':
                chat_msg = input("Enter your message: ")
                send_message(client, 'chat', {"message": chat_msg})

            elif msg_type == 'quit':
                send_message(client, 'quit', {})
                break

    except socket.error as e:
        logging.error(f"Error: {e}")
    finally:
        stop_flag = True
        client.close()
        logging.info("Disconnected from server")
        receive_thread.join()

connect_to_server()

