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
- Support for multiple clients on different devices

## Project Structure

- `client.py` - Main client application with UI and network logic
- `server_test.py` - Test server for handling client connections
- `run_server.py` - Helper script to run the server with network information
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
- argparse library (standard)

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

### Running the Server

Run the server using the helper script:
```
python run_server.py
```

This will:
- Start the server on port 5555
- Display your local network IP address
- Show instructions for clients to connect

### Client Connection Options

1. **Connect from the same computer**:
```
python client.py
```
(Uses localhost by default)

2. **Connect from another device on the same network**:
```
python client.py --host <SERVER_LOCAL_IP>
```
(Use the Local Network IP displayed when starting the server)

3. **Connect from outside the network** (requires port forwarding):
```
python client.py --host <SERVER_PUBLIC_IP>
```

### Playing the Game

1. Enter a username and click "Connect"
2. Click "FIND GAME" to start matchmaking
3. Play chess against your opponent!

## Network Configuration

For clients to connect from outside your local network:
1. Set up port forwarding on your router to forward port 5555 to your server computer
2. Clients will use your public IP address to connect
3. Some networks may block connections - try using a mobile hotspot if you encounter issues

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