import socket
import threading
import bcrypt

# Server settings
HOST = '127.0.0.1'  # Localhost IP
PORT = 5555
BUFFER_SIZE = 1024

# In-memory storage for user credentials and connected clients
user_credentials = {}
connected_clients = {}

def register_user(username, password):
    if username in user_credentials:
        return "Username already exists."
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    user_credentials[username] = hashed_password
    return "User registered successfully."

def login_user(username, password):
    if username not in user_credentials:
        return "Username does not exist."
    hashed_password = user_credentials[username]
    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
        connected_clients[username] = None  # Placeholder for client socket
        return "Login successful."
    else:
        return "Incorrect password."

def broadcast_message(sender, message, exclude=None):
    """Broadcast a message to all connected clients except the sender."""
    for username, client_socket in connected_clients.items():
        if username != exclude:
            client_socket.send(f"{sender}: {message}".encode())

def send_private_message(sender, recipient, message):
    """Send a private message to a specific user."""
    if recipient in connected_clients:
        client_socket = connected_clients[recipient]
        client_socket.send(f"PRIVATE from {sender}: {message}".encode())
        return f"Message sent to {recipient}."
    else:
        return f"User {recipient} is not online or does not exist."

def notify_user_status(username, status):
    """Notify all clients about a user's status (joined or left)."""
    message = f"** {username} has {status} the chat **"
    broadcast_message("Server", message)

def handle_client(client_socket, address):
    username = None
    try:
        while True:
            client_message = client_socket.recv(BUFFER_SIZE).decode()
            if not client_message:
                break

            command, *data = client_message.split(' ', 1)
            if command == "REGISTER":
                username, password = data[0].split()
                response = register_user(username, password)
            elif command == "LOGIN":
                username, password = data[0].split()
                response = login_user(username, password)
                if response == "Login successful.":
                    connected_clients[username] = client_socket  # Assign socket to the username
                    notify_user_status(username, "joined")
                    client_socket.send(response.encode())
                else:
                    client_socket.send(response.encode())
            elif command == "MESSAGE" and username:
                message = data[0]
                broadcast_message(username, message)
                response = "Message sent."
            elif command == "PRIVATE" and username:
                recipient, private_message = data[0].split(' ', 1)
                response = send_private_message(username, recipient, private_message)
            elif command == "LOGOUT" and username:
                notify_user_status(username, "left")
                break
            else:
                response = "Invalid command."

            client_socket.send(response.encode())
    except (ConnectionResetError, BrokenPipeError):
        print(f"Connection with {address} lost.")
    finally:
        if username and username in connected_clients:
            del connected_clients[username]
            notify_user_status(username, "left")
        client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server running on {HOST}:{PORT}...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"New connection from {address}.")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
