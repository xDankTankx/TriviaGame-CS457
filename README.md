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
1. **Start the server:** Run the `TCP_server.py` script. This script will ask how many players will be playing (answer 1-4) (This will be implemented by Sprint 2), before initializing and waiting to connect to the number of players specified on start-up. Once the players are connected, the server will wait 5 seconds before sending the first trivia question to all connected clients.
</br>

2. **Connect clients:** Run the `TCP_client.py` script on up to four different machines or terminals. (Note that this software can accept more clients as of now, but we plan to limit it to four connections ((10/06/2024))). Players now enter a username upon connecting, which assigns them a unique position in the game. Once the username is entered, the client is able to see the current game state, including other players' positions and scores. The client interface has been improved to display a single message about waiting for the turn when necessary.
</br>

3. **Play the game:** Players answer the question posed by the server as quickly and accurately as they can. Whichever player's answer is received first will be checked by the server to see if it is correct. The player who answers correctly first will receive 1 point! This game loop lasts for 10 rounds (as of now: 9/22/24), and at the end of the final 10th round, the server will automatically check each player's points to determine a winner. It will then output each player's ranking to all clients, with a congratulatory message for the first-place winner.
</br>

**Technologies used:**
* Python
* Sockets
* Logging
* Threading
* JSON
* sys
</br>

**Additional resources:**
* [Link to Python documentation]
* [Link to sockets tutorial]
