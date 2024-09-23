# TriviaGame-CS457
This is a simple yet enjoyable trivia game you may play by yourself or with up to four additional friends who must be on different computers. This game was created by using Python sockets to seamlessly connect you and your friends so that you all may play a trivia game together! This game proposes a question from the server and waits to listen for responses. Once a response from a client is recieved the server will assign it a position in queue starting at one up to the amount of players. The server then checks whether the answer from whoever answered first was correct or not, and if it wasn't, it checks the next answer in the order recieved. This allows for seamless connectivity as well as ensuring the players who answered the quickest with the correct answer can win! Points will be assigned to those who answered correct first and the winner is tallied up at the end of the last question. This is a product made for educational purposes by Nicholas Chaffee and Chasen Villiers. This was made as an assignment for CS457. 

**How to play:**
1. **Start the server:** Run the `trivia_server.py` script. This script will ask how many players will be playing (answer 1-4) before initializing and waiting to connect to the amount of players specified on start-up. Once the players are connected the server will wait 5 seconds before sending the first trivia question to all connected clients.
2. **Connect clients:** Run the `trivia_client.py` script on up to four different machines or terminals. Please wait 5 seconds after all specified players/clients have connected to the server before typing or entering anything to allow the server to accurately send out the first question.
3. **Play the game:** Players answer the question posed by the server as quickly and as accurately as they can. Whichever player's answer is received first will be checked first by the server to see whether it is correct or not. Whichever player's answer is correct will recieve 1 point! This game loop will last for 10 rounds (as of now: 9/22/24) and at the end of the final 10th round, the server will automatically check each player's points to determine a winner. Then will output each player's place in ranking to all clients. The first place winner will recieve a congratulatory message (the others will receive a message as well but 2nd, 3rd, and 4th place messages will be determined at a later date). Have fun and enjoy!

**Technologies used:**
* Python
* Sockets

**Additional resources:**
* [Link to Python documentation]
* [Link to sockets tutorial]
