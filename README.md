
# LiveWire: Real-Time Chat Application with Socket Programming

**LiveWire** is a real-time chat application built using Python's socket programming that facilitates communication between a server and multiple clients. The system provides a graphical user interface (GUI) for both the server and clients, allowing for easy messaging, client management, personal chats, and message deletion with encrypted communication.

## Features

### Basic Features:
- **Server:**
  - **Start/Stop Server:** Initiates and terminates the server, allowing clients to connect or disconnect.
  - **Client Management:** Displays a list of connected clients and their corresponding IP addresses and ports.
  - **Message Broadcasting:** Sends messages from one client to all connected clients.
  
- **Client:**
  - **Client Connection:** Connects to the server by providing the IP address, port, and a username.
  - **Login/Logout:** Clients can log in to the chat server using their username and log out, disconnecting from the server.
  - **Message Exchange:** Clients can send and receive messages from other connected clients.
  
### Advanced Features:
- **Private Messaging:** Clients can send direct, private messages to other users by specifying the recipient’s username.
- **Encryption & Decryption:** All messages are encrypted using AES (Advanced Encryption Standard) before transmission, ensuring that communication between clients and the server is secure.
- **Delete for Me:** Clients can delete specific messages for themselves, which will no longer appear in their message list.
- **Delete for Everyone:** Clients can delete a message for all participants in the chat, ensuring that the message is removed from every client’s chat interface.

## Technologies Used
- **Python**: For core programming and socket communication.
- **Socket Programming**: To establish server-client connections and facilitate communication.
- **Tkinter**: For building the graphical user interface (GUI) for both the client and server applications.
- **PyCryptodome (AES Encryption)**: For securing messages between clients and the server.
- **Threading**: To handle multiple clients simultaneously on the server.


## Future Enhancements

- Implement file upload and download functionality.
- Improve the GUI with more modern designs and better user feedback.
- Add more advanced encryption features for secure communication.

