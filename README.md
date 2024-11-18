# TriviaGame-CS457
This is a simple yet enjoyable trivia game you may play by yourself or with up to four additional friends who must be on different computers. This game was created by using Python sockets to seamlessly connect you and your friends so that you all may play a trivia game together! This game proposes a question from the server and waits to listen for responses. Once a response from a client is received, the server will assign it a position in queue starting at one up to the number of players. The server then checks whether the answer from whoever answered first was correct or not, and if it wasn't, it checks the next answer in the order received. This allows for seamless connectivity as well as ensuring the players who answered the quickest with the correct answer can win! Points will be assigned to those who answered correctly first, and the winner is tallied up at the end of the last question. This is a product made for educational purposes by Nicholas Chaffee and Chasen Villiers. This was made as an assignment for CS457.  
</br> </br>

### New Features and Updates
1. **Game State Synchronization**: The server now synchronizes game state across all clients, ensuring each client has the same view of the players' current positions, scores, and the current turn.

2. **Turn-Based Gameplay**: The game now supports turn-based gameplay. The server maintains a turn order based on the order clients join, and only the player whose turn it is can make moves. Other players see a single message indicating they are waiting for the current player’s turn.

3. **Unique Player Identification**: Each player is now assigned a unique position number upon joining. This position is used to keep track of the player throughout the game and to display their order.

4. **Initial Game State and Turn Display**: When a new player joins, they immediately see the current game state and whose turn it is, preventing any delay in receiving this information.

5. **Improved Client Interface for Turn Waiting**: Players waiting for their turn no longer receive continuous "Waiting for turn" messages. Instead, they receive a single notification about waiting for the current player’s turn, and the display updates when the turn changes.

### How to play:
1. **Start the server:**  
   Run the `server.py` script:
   ```bash
   python server.py -p <PORT>

### Game Instructions

1. **Start the Server:**
   - Replace `<PORT>` with the desired port number (e.g., `65433`).
   - The server will bind to `0.0.0.0`, making it accessible across the local network.
   - The first client to connect will set the total number of players.
   - The server waits for all players to join before starting the game.
   </br>

2. **Connect Clients:**
   - Run the `client.py` script for each player:
     ```bash
     python client.py -i <SERVER_IP> -p <PORT>
     ```
   - Replace `<SERVER_IP>` with the server's IP address (e.g., `127.0.0.1` for localhost).
   - Replace `<PORT>` with the same port used to start the server.
   - Each client must connect using a unique device or terminal.
   </br>

3. **Play the Game:**
   - The first client will be prompted to set the total number of players.
   - Each client enters their username upon connecting and sees the updated game state.
   - During their turn, players answer questions by entering the option number corresponding to their chosen answer.
   - Points are awarded for correct answers, and scores are updated in real time.
   - The game continues until all questions are answered, and the winner is determined based on the final scores.
   </br>

### Game Flow:

- **Joining:** Players join in the order they connect. The first player sets the total number of participants.
- **Question Display:** The server broadcasts a trivia question to all clients.
- **Turn-Based Answering:** Only the active player can respond during their turn. If the answer is incorrect, the next player gets their turn.
- **Score Updates:** After all players have answered, the game state is updated and displayed to all clients.
- **Winning:** The game ends after a set number of rounds (default: 10). The player with the highest score wins, with results broadcasted to all clients.
</br>

### Technologies Used:

- **Python**
- **Sockets**
- **Logging**
- **Threading**
- **JSON**
- **sys**
</br>

### Additional Resources:

- [Python Documentation](https://docs.python.org)
- [Socket Programming Tutorial](https://realpython.com/python-sockets/)
