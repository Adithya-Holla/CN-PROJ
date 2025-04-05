# Chess Game with Python Socket Programming and GUI

A multiplayer chess game built with Python socket programming and Pygame. This application allows users to play chess with others over a network connection.

## Features

- Realtime multiplayer chess gameplay
- Full implementation of chess rules and valid moves
- Server that supports multiple concurrent games
- Simple matchmaking system
- In-game chat functionality
- Game status tracking (check, checkmate, draws)

## Requirements

- Python 3.6 or higher
- Pygame 2.5.2 or higher

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/chess-game.git
   cd chess-game
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Application

### Starting the Server

1. Run the server script:
   ```
   python server.py
   ```

   By default, the server runs on port 5555 and accepts connections from any IP address.

### Starting the Client

1. Run the client script:
   ```
   python client.py
   ```

2. Enter your username and click "Connect" to connect to the server.

3. Once connected, click "Find Game" to be matched with another player.

## How to Play

1. After being matched with another player, the game will begin automatically.

2. The white player moves first.

3. Click on a piece to select it, then click on a valid destination square to move.

4. Use the chat panel on the right to communicate with your opponent.

5. The game ends when one player:
   - Checkmates the opponent
   - Makes the opponent run out of valid moves (stalemate)
   - Resigns
   - Disconnects

## Project Structure

- `server.py` - The server application that handles client connections and game logic
- `client.py` - The client application with the GUI
- `chess_logic.py` - Implementation of chess rules and game state
- `gui/` - Contains GUI components:
  - `board.py` - Chess board rendering and interaction
  - `menu.py` - Login and main menu screens
  - `chat.py` - Chat panel implementation
  - `utils.py` - Utility functions and UI components

## Customization

- The game uses placeholder images for chess pieces. You can replace these with your own images by adding PNG files to the `assets/pieces/` directory.
- Modify the colors in the `colors` dictionary in `client.py` to change the appearance of the game.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Chess piece images can be replaced with standard chess piece designs available from various sources.
- The game logic follows standard international chess rules. 