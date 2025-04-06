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

You have two server options:

### Option 1: Main Server (Recommended)

#### Windows
Run the `start_main_server.bat` file by double-clicking it.

#### Linux/Mac
1. Make the script executable:
   ```
   chmod +x start_main_server.sh
   ```
2. Run the script:
   ```
   ./start_main_server.sh
   ```

#### Manual Start
You can also start the server directly with Python:
```
python server.py
```

### Option 2: Test Server

#### Windows
Run the `start_server.bat` file by double-clicking it.

#### Linux/Mac
1. Make the script executable:
   ```
   chmod +x start_server.sh
   ```
2. Run the script:
   ```
   ./start_server.sh
   ```

#### Manual Start
You can also start the test server directly with Python:
```
python server_test.py
```

### Client Connection Options

1. **Connect from the same computer**:
```
python client.py --host localhost --port 5555
```

2. **Connect from another device on the same network**:
```
python client.py --host [SERVER_LOCAL_IP] --port 5555
```

3. **Connect from outside the network** (requires port forwarding):
```
python client.py --host [SERVER_PUBLIC_IP] --port 5555
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

# Chess Online Server

## Starting the Server

You have two server options:

### Option 1: Main Server (Recommended)

#### Windows
Run the `start_main_server.bat` file by double-clicking it.

#### Linux/Mac
1. Make the script executable:
   ```
   chmod +x start_main_server.sh
   ```
2. Run the script:
   ```
   ./start_main_server.sh
   ```

#### Manual Start
You can also start the server directly with Python:
```
python server.py
```

### Option 2: Test Server

#### Windows
Run the `start_server.bat` file by double-clicking it.

#### Linux/Mac
1. Make the script executable:
   ```
   chmod +x start_server.sh
   ```
2. Run the script:
   ```
   ./start_server.sh
   ```

#### Manual Start
You can also start the test server directly with Python:
```
python server_test.py
```

## Connecting Clients

Clients can connect to the server using:

1. **From the same computer**: 
   ```
   python client.py --host localhost --port 5555
   ```

2. **From another device on the same network**:
   ```
   python client.py --host [SERVER_LOCAL_IP] --port 5555
   ```
   The server's local IP will be shown when you start the server.

3. **From the internet** (requires port forwarding on your router):
   ```
   python client.py --host [SERVER_PUBLIC_IP] --port 5555
   ```

## Important Notes

- The server now listens on all network interfaces (`0.0.0.0`), allowing connections from any device
- To allow connections from the internet, you need to set up port forwarding on your router for port 5555
- Press Ctrl+C to stop the server 