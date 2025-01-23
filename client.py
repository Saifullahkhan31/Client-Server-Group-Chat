import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server settings
HOST = '127.0.0.1'  # Localhost IP
PORT = 5555
BUFFER_SIZE = 1024

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Application")
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))

        self.username = None

        self.create_widgets()

    def create_widgets(self):
        # Frame for login/registration
        self.frame_login = tk.Frame(self.master)
        self.frame_login.pack(pady=20)

        # Login/Register Labels and Entry Fields
        tk.Label(self.frame_login, text="Username:").grid(row=0, column=0, padx=10)
        self.entry_username = tk.Entry(self.frame_login)
        self.entry_username.grid(row=0, column=1, padx=10)

        tk.Label(self.frame_login, text="Password:").grid(row=1, column=0, padx=10)
        self.entry_password = tk.Entry(self.frame_login, show='*')
        self.entry_password.grid(row=1, column=1, padx=10)

        # Buttons for Login and Register
        self.btn_login = tk.Button(self.frame_login, text="Login", command=self.login)
        self.btn_login.grid(row=2, column=0, pady=5)

        self.btn_register = tk.Button(self.frame_login, text="Register", command=self.register)
        self.btn_register.grid(row=2, column=1, pady=5)

        # Frame for chat
        self.frame_chat = tk.Frame(self.master)
        self.frame_chat.pack(pady=20)

        # Chat display area
        self.text_chat = tk.Text(self.frame_chat, height=15, width=50, state=tk.DISABLED)
        self.text_chat.grid(row=0, column=0, padx=10, pady=10)

        # Message input
        self.entry_message = tk.Entry(self.frame_chat, width=40)
        self.entry_message.grid(row=1, column=0, padx=10)

        # Send message button
        self.btn_send = tk.Button(self.frame_chat, text="Send", command=self.send_message)
        self.btn_send.grid(row=1, column=1, padx=10)

        self.frame_login.tkraise()

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        response = self.send_request("LOGIN", f"{username} {password}")
        if "successful" in response:
            self.username = username
            self.frame_chat.tkraise()
            self.start_receiving_messages()
        else:
            messagebox.showerror("Error", response)

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        response = self.send_request("REGISTER", f"{username} {password}")
        messagebox.showinfo("Info", response)

    def send_request(self, command, data):
        try:
            self.client_socket.send(f"{command} {data}".encode('utf-8'))
            response = self.client_socket.recv(BUFFER_SIZE).decode('utf-8')
            return response
        except (ConnectionResetError, ConnectionAbortedError) as e:
            print(f"Error: {e}")
            self.client_socket.close()
            exit()

    def send_message(self):
        message = self.entry_message.get()
        if message:
            if message.lower() == 'exit':
                self.send_request("LOGOUT", "")
                self.master.quit()
            elif message.startswith("@"):
                recipient, private_message = message[1:].split(' ', 1)
                self.send_request("PRIVATE", f"{recipient} {private_message}")
            else:
                self.send_request("MESSAGE", message)
            self.entry_message.delete(0, tk.END)

    def start_receiving_messages(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(BUFFER_SIZE).decode()
                if message:
                    self.text_chat.config(state=tk.NORMAL)
                    self.text_chat.insert(tk.END, f"{message}\n")
                    self.text_chat.config(state=tk.DISABLED)
                else:
                    break
            except (ConnectionResetError, ConnectionAbortedError):
                print("Connection lost.")
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
