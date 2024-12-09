# TriviaGame-CS457
This is a simple yet enjoyable trivia game you may play by yourself or with up to as many friends as you'd like, though they must be on different computers (or Terminals). This game was created by using Python sockets to seamlessly connect you and your friends so that you all may play a trivia game together! The server broadcasts a trivia question to all clients, and each client gets to answer the question. Once all connected players have answered, the server evaluates the responses, assigns points for correct answers, and updates the scoreboard. The game ends when a player achieves 5 points or when the question pool is depleted. This product was made for educational purposes by Chasen Villiers as an assignment for CS457.  
</br> </br>

### New Features and Updates
1. **Dynamic Player Handling**: Players can join mid-game and are dynamically integrated into the current round. New players receive the active question upon joining.
   
2. **Answer Restrictions**: Players are restricted to answering once per question. Attempts to answer again prompt an error message: "You've already answered this question."

3. **Dynamic Game State Updates**: When a player quits or disconnects, the game dynamically updates the remaining number of players needed to progress to the next round.

4. **Graceful Disconnect Handling**: When a player quits or disconnects (via `Ctrl+C` or `quit`), other players are notified, and the disconnected player is removed from the scoreboard.

5. **Real-Time Scoreboard Updates**: After each round, the updated scoreboard is broadcasted to all clients, showing the dynamically ranked players.

6. **Winning Condition**: The game ends when a player achieves 5 points, or when all questions have been exhausted, with a congratulatory message for the winner.

</br>

### How to Play:
1. **Start the Server:**  
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

## Play the Game:

- Each client enters their username upon connecting and sees the updated game state.
- Players answer questions by entering the option number corresponding to their chosen answer.
- Players cannot change their answers after submitting, and repeated attempts are blocked with an error message.
- Points are awarded for correct answers, and the scoreboard updates in real time.
- The game ends when a player reaches 5 points or the questions run out, with the final scores displayed to all players.

</br>

## Game Flow:

- **Joining Mid-Game**: Players joining mid-game immediately receive the active question and are added to the game state dynamically.
- **Answer Submission**: Each player submits their answer for the active question. After all remaining players have answered, the game progresses to the next question.
- **Score Updates**: After each round, the game state and scoreboard update dynamically and are broadcasted to all clients.
- **Player Disconnections**: If a player disconnects mid-question, the round adjusts for the remaining players, ensuring uninterrupted gameplay.
- **Winning**: The game ends when a player reaches 5 points or the question pool is exhausted, with a final congratulatory message for the winner.

</br>

## Retrospective:

### What Went Right:
- **Dynamic Integration of New Players**: The ability for players to join mid-game without disrupting the ongoing round was implemented smoothly.
- **Real-Time Updates**: The game state and scoreboard update dynamically, ensuring all clients are synchronized.
- **Graceful Disconnection Handling**: When players quit or disconnect, the game adjusts dynamically, notifying all clients and updating the required responses for the round to progress.

### What Could Be Improved:
- **Answer Restriction Robustness**: There were occasional edge cases where players could submit multiple answers, leading to skipped questions.
- **Handling Disconnections During Answers**: While the game dynamically adjusts for disconnections, further improvements can ensure seamless progression even in edge cases.
- **Error Handling and Logging**: Additional logging could help trace issues more effectively, especially when processing edge cases.



# How to Run the Project:

### Run the Server:
Start the server on the desired port:
```bash
python server.py -p <PORT>
```

### Run the Clients:
Connect clients to the server:
```bash
python client.py -i <SERVER_IP> -p <PORT>
```

### Follow Game Instructions:
- Players will see the questions, answer options, and their respective scores updated dynamically throughout the game.

</br>

## Roadmap:

1. **Enhanced Player Experience**: Add features like timers for answering questions and more informative messages during gameplay.
2. **Additional Question Categories**: Expand the question pool with categories to make the game more engaging.
3. **Web-Based Interface**: Transition to a web-based interface for easier access and improved user experience.
4. **Data Persistence**: Implement a database to store player statistics and game history for future analysis.

</br>

## Technologies Used:

- **Python**
- **Sockets**
- **Logging**
- **Threading**
- **JSON**
- **sys**
- **random**
- **argparse**

</br>

## Additional Resources:

- [Python Documentation](https://docs.python.org)
- [Socket Programming Tutorial](https://realpython.com/python-sockets/)
