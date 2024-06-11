import socket
import threading
import tkinter as tk
from Crypto.Cipher import AES
import base64

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server")
        self.root.configure(bg="#f0f0f0")

        self.header_label = tk.Label(root, text="Server", font=("Helvetica", 18), bg="#336699", fg="white", pady=10)
        self.header_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.start_button = tk.Button(root, text="Start Server", command=self.start_server, bg="#4CAF50", fg="white", bd=0, padx=20, pady=10)
        self.start_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.stop_button = tk.Button(root, text="Stop Server", command=self.stop_server, state=tk.DISABLED, bg="#FF5733", fg="white", bd=0, padx=20, pady=10)
        self.stop_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.message_display = tk.Text(root, width=50, height=20, bg="white", fg="black", font=("Helvetica", 12))
        self.message_display.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.clients_display = tk.Text(root, width=30, height=20, bg="white", fg="black", font=("Helvetica", 12))
        self.clients_display.grid(row=2, column=2, padx=10, pady=10)

        self.server_socket = None
        self.clients = []
        self.client_usernames = {}
        self.encryption_key = b'This is a key123' 

    def start_server(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 5555))
        self.server_socket.listen(5)

        threading.Thread(target=self.accept_clients).start()

        self.message_display.insert(tk.END, "Server started. Waiting for clients...\n")

    def accept_clients(self):
        while True:
            client_socket, address = self.server_socket.accept()
            username = self.decrypt(client_socket.recv(1024)).decode('utf-8')
            self.clients.append((client_socket, address))
            self.client_usernames[client_socket] = username
            self.update_clients_display()
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        username = self.client_usernames[client_socket]
        self.message_display.insert(tk.END, f"New connection from {address} with username: {username}\n")
        while True:
            try:
                message = self.decrypt(client_socket.recv(1024)).decode('utf-8')
                if message.startswith("@"):
                    target_username, private_message = message[1:].split(":", 1)
                    self.send_private_message(private_message, target_username, address, username, client_socket)
                elif message.startswith("/delete_for_everyone"):
                    self.broadcast_message(message, client_socket, exclude_sender=True)
                else:
                    if not message:
                        break
                    encrypted_message = self.encrypt(f"{username}: {message}").decode('utf-8')
                    self.message_display.insert(tk.END, f"{encrypted_message}\n")
                    self.broadcast_message(f"{username}: {message}", client_socket)
            except Exception as e:
                print(e)
                break
        client_socket.close()
        self.clients.remove((client_socket, address))
        del self.client_usernames[client_socket]
        self.update_clients_display()

    def broadcast_message(self, message, sender_socket, exclude_sender=False):
        for client, _ in self.clients:
            if not exclude_sender or client != sender_socket:
                client.send(self.encrypt(message))

    def send_private_message(self, message, target_username, sender_address, sender_username, sender_socket):
        found = False
        for client_socket, username in self.client_usernames.items():
            client_address = client_socket.getpeername()
            if username == target_username and client_address != sender_address:

                client_socket.send(self.encrypt(f"Private message from {sender_username}: {message}"))
                sender_socket.send(self.encrypt(f"Private to {target_username} at {client_address}: {message}"))
                found = True
                break
        if not found:
            sender_socket.send(self.encrypt(f"User {target_username} not found."))

    def stop_server(self):
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.message_display.insert(tk.END, "Server stopped.\n")
        self.server_socket.close()

    def update_clients_display(self):
        self.clients_display.delete('1.0', tk.END)
        for client, address in self.clients:
            self.clients_display.insert(tk.END, f"{self.client_usernames[client]} ({address[0]}:{address[1]})\n")

    def encrypt(self, message):
        cipher = AES.new(self.encryption_key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(message.encode('utf-8'))
        return base64.b64encode(nonce + ciphertext)

    def decrypt(self, ciphertext):
        raw = base64.b64decode(ciphertext)
        nonce = raw[:16]
        cipher = AES.new(self.encryption_key, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt(raw[16:])

root = tk.Tk()
server_gui = ServerGUI(root)
root.mainloop()
