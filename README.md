# Chess Online Game

A multiplayer chess game built with Python and Pygame, featuring online gameplay through socket programming.

## Features

- Real-time multiplayer chess over the network
- Modern user interface with intuitive controls
- In-game chat system
- Matchmaking system to pair players automatically
- Game state synchronization between players
- Proper handling of chess rules including valid moves
- Visual feedback for selected pieces and valid moves

## Project Structure

- `client.py` - Main client application with UI and network logic
- `server_test.py` - Test server for handling client connections
- `chess_logic.py` - Implementation of chess rules and game state
- `gui/` - GUI components:
  - `board.py` - Chess board representation
  - `menu.py` - Login and menu screens
  - `chat.py` - In-game chat system
  - `utils.py` - UI utilities (buttons, textboxes, etc.)
- `assets/` - Game assets including chess piece images

## Requirements

- Python 3.6+
- Pygame
- Socket library (standard)
- JSON library (standard)

## Installation

1. Clone the repository:
```
git clone https://github.com/Adithya-Holla/CN-PROJ.git
```

2. Install the required packages:
```
pip install -r requirements.txt
```

## Usage

1. Start the server:
```
python server_test.py
```

2. Run the client (in a separate terminal):
```
python client.py
```

3. Enter a username and click "Connect"
4. Click "FIND GAME" to start matchmaking
5. Play chess against your opponent!

## Network Protocol

The game uses a JSON-based protocol for communication between client and server:

- Connection setup with username registration
- Game matchmaking requests
- Move validation and synchronization
- Chat message exchange
- Game state updates

## Game Modes

- Player vs Player: Play against another player online

## Contributors

- Adithya Holla

## License

This project is created as part of a computer networks course assignment. 