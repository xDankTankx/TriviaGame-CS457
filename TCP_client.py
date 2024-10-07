import socket
import threading
import logging

logging.basicConfig(level=logging.INFO)

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                logging.info(f"New message: {message}")
            else:
                break
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            break

def connect_to_server(host='127.0.0.1', port=65432):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
        logging.info("Connected to server")

        # Start a thread to handle incoming messages
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.start()

        # Main thread will handle sending messages
        while True:
            msg = input("Enter message: ")
            client.send(msg.encode('utf-8'))

    except socket.error as e:
        logging.error(f"Error: {e}")
    finally:
        client.close()
        logging.info("Disconnected from server")

connect_to_server()
