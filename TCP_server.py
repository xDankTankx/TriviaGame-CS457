import socket
import threading
import logging

logging.basicConfig(level=logging.INFO)
clients = []  # List to keep track of connected clients

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except Exception as e:
                logging.error(f"Failed to send message to a client: {e}")
                client.close()
                clients.remove(client)  # Remove client if it has disconnected

def handle_client(client_socket, address):
    logging.info(f"Connection from {address}")
    clients.append(client_socket)
    
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break  # Client disconnected
            logging.info(f"Received message from {address}: {message.decode('utf-8')}")
            broadcast(message, client_socket)
    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        logging.info(f"Disconnected from {address}")

def start_server(host='127.0.0.1', port=65432):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    logging.info(f"Server started on {host}:{port}")
    
    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

start_server()
