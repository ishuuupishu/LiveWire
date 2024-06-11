from email import message
import socket
import threading
import tkinter as tk
from tkinter import simpledialog
from Crypto.Cipher import AES
import base64


class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client")
        self.root.configure(bg="#f0f0f0")

        self.header_label = tk.Label(root, text="Client", font=("Helvetica", 18), bg="#336699", fg="white", pady=10)
        self.header_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.server_label = tk.Label(root, text="Server IP:", bg="#f0f0f0")
        self.server_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.server_entry = tk.Entry(root, width=30)
        self.server_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.port_label = tk.Label(root, text="Port:", bg="#f0f0f0")
        self.port_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.port_entry = tk.Entry(root, width=10)
        self.port_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.username_label = tk.Label(root, text="Username:", bg="#f0f0f0")
        self.username_label.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server, bg="#4CAF50", fg="black", bd=0, padx=20, pady=10)
        self.connect_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.logout_button = tk.Button(root, text="Logout", command=self.logout, state=tk.DISABLED, bg="#D69F56", fg="white", bd=0, padx=20, pady=10)
        self.logout_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.private_chat_button = tk.Button(root, text="Private Chat", command=self.private_chat, state=tk.DISABLED, bg="#DFC5FE", fg="white", bd=0, padx=20, pady=10)
        self.private_chat_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        self.chat_display = tk.Text(root, width=35, height=15, bg="white", fg="black", font=("Helvetica", 12))
        self.chat_display.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.grid(row=8, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.send_button = tk.Button(root, text="Send", command=self.send_message, state=tk.DISABLED, bg="#FF5733", fg="white", bd=0, padx=20, pady=10)
        self.send_button.grid(row=8, column=2, padx=10, pady=10, sticky="ew")

        self.delete_for_me_button = tk.Button(root, text="Delete for Me", command=self.delete_for_me, state=tk.DISABLED, bg="#4CAF50", fg="white", bd=0, padx=20, pady=10)
        self.delete_for_me_button.grid(row=9, column=0, padx=10, pady=10, sticky="ew")

        self.delete_for_everyone_button = tk.Button(root, text="Delete for Everyone", command=self.delete_for_everyone, state=tk.DISABLED, bg="#4CAF50", fg="black", bd=0, padx=20, pady=10)
        self.delete_for_everyone_button.grid(row=9, column=1, padx=10, pady=10, sticky="ew")

        self.client_socket = None
        self.encryption_key = b'This is a key123' 

    def connect_to_server(self):
        server_ip = self.server_entry.get()
        port = int(self.port_entry.get())
        username = self.username_entry.get()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((server_ip, port))
        self.client_socket.send(self.encrypt(username))

        threading.Thread(target=self.receive_messages).start()

        self.connect_button.config(state=tk.DISABLED)
        self.logout_button.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.private_chat_button.config(state=tk.NORMAL)
        self.delete_for_me_button.config(state=tk.NORMAL)
        self.delete_for_everyone_button.config(state=tk.NORMAL)

    def receive_messages(self):
        while True:
            try:
                message = self.decrypt(self.client_socket.recv(1024)).decode('utf-8')
                if message.startswith("/delete_for_everyone"):
                    message_to_delete = message.split(' ', 1)[1]
                    self.delete_message(message_to_delete)
                else:
                    self.chat_display.insert(tk.END, message + '\n')
            except Exception as e:
                print(e)
                break

    def send_message(self):
        message = self.message_entry.get()
        self.client_socket.send(self.encrypt(message))
        self.message_entry.delete(0, tk.END)

    def private_chat(self):
        recipient = simpledialog.askstring("Personal Chat", "Enter recipient's username:", parent=self.root)
        recipient_address = simpledialog.askstring("Personal Chat", "Enter recipient's address (IP:port):", parent=self.root)
        if recipient and recipient_address:
            message = simpledialog.askstring("Personal Chat", "Enter your message:", parent=self.root)
            if message:
                private_message = f"@{recipient}:{message}"
                self.client_socket.send(self.encrypt(private_message))
                self.message_entry.delete(0, tk.END)
                self.chat_display.insert(tk.END, f"Private to {recipient} at {recipient_address}: {message}\n")

    def delete_for_me(self):
        self.chat_display.delete('1.0', tk.END)

    def delete_for_everyone(self):
        message = self.message_entry.get()
        self.client_socket.send(self.encrypt(f"/delete_for_everyone {message}"))
        self.message_entry.delete(0, tk.END)
        self.delete_message(message)

    def delete_message(self, message):
        content = self.chat_display.get('1.0', tk.END).split('\n')
        new_content = '\n'.join([line for line in content if message not in line])
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.insert(tk.END, new_content)

    def logout(self):
        self.client_socket.close()
        self.root.destroy()

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
client_gui = ClientGUI(root)
root.mainloop()

