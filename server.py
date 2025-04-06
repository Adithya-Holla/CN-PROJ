import socket
import threading
import json
import random
import time
from chess_logic import ChessGame

class ChessServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # {client_socket: {'username': username, 'game': game_id, 'color': color}}
        self.waiting_queue = []  # List of client sockets waiting for a match
        self.games = {}  # {game_id: {'white': client_socket, 'black': client_socket, 'game': ChessGame}}
        self.lock = threading.Lock()
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        # Get and display IP addresses for connection
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        try:
            # Get the public IP (this requires internet access)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            public_ip = s.getsockname()[0]
            s.close()
        except:
            public_ip = "Could not determine (check internet connection)"
        
        print("=" * 50)
        print("  CHESS ONLINE SERVER")
        print("=" * 50)
        print(f"\nServer started on port {self.port}")
        print(f"Server is listening on all network interfaces (0.0.0.0)")
        print("\nIP Addresses for clients to connect to:")
        print(f"  • Local (same computer): 127.0.0.1 or localhost")
        print(f"  • Local network (LAN): {local_ip}")
        print(f"  • Public (requires port forwarding): {public_ip}")
        print("\nClient connection instructions:")
        print(f"  python client.py --host <IP_ADDRESS> --port {self.port}")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} established")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket):
        try:
            # First message from client should be their username
            username_data = client_socket.recv(1024).decode('utf-8')
            username = json.loads(username_data)['username']
            
            with self.lock:
                self.clients[client_socket] = {'username': username, 'game': None, 'color': None}
                
            # Inform client they have connected successfully
            self.send_message(client_socket, {'type': 'connection_success', 'message': f'Welcome {username}!'})
            
            # Handle client communication
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.process_message(client_socket, message)
                
        except json.JSONDecodeError:
            print(f"Invalid JSON received from client")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self.disconnect_client(client_socket)
    
    def process_message(self, client_socket, message):
        message_type = message.get('type')
        
        if message_type == 'find_game':
            self.find_game(client_socket)
        elif message_type == 'move':
            self.handle_move(client_socket, message.get('from'), message.get('to'))
        elif message_type == 'resign':
            self.handle_resignation(client_socket)
        elif message_type == 'chat':
            self.handle_chat(client_socket, message.get('content'))
    
    def find_game(self, client_socket):
        with self.lock:
            # Add client to waiting queue if not already in a game
            if self.clients[client_socket]['game'] is None and client_socket not in self.waiting_queue:
                self.waiting_queue.append(client_socket)
                self.send_message(client_socket, {'type': 'queue', 'message': 'Looking for opponent...'})
                print(f"Added client {self.clients[client_socket]['username']} to waiting queue")
                
                # Check if we can match two players
                if len(self.waiting_queue) >= 2:
                    # Use a separate thread for matchmaking to avoid blocking
                    match_thread = threading.Thread(target=self.match_players)
                    match_thread.daemon = True
                    match_thread.start()
                    print("Started matchmaking thread")
    
    def match_players(self):
        with self.lock:
            # Verify we have at least 2 players
            if len(self.waiting_queue) < 2:
                print("Not enough players in queue for matchmaking")
                return
            
            # Get two clients from the waiting queue
            client1 = self.waiting_queue.pop(0)
            client2 = self.waiting_queue.pop(0)
            
            print(f"Matching players: {self.clients[client1]['username']} and {self.clients[client2]['username']}")
            
            # Create a unique game ID
            game_id = str(random.randint(1000, 9999))
            
            # Create a new chess game
            game = ChessGame()
            
            # Randomly assign colors
            colors = ['white', 'black']
            random.shuffle(colors)
            
            # Update client information
            self.clients[client1]['game'] = game_id
            self.clients[client1]['color'] = colors[0]
            self.clients[client2]['game'] = game_id
            self.clients[client2]['color'] = colors[1]
            
            # Store game information
            self.games[game_id] = {
                'white': client1 if colors[0] == 'white' else client2,
                'black': client2 if colors[0] == 'white' else client1,
                'game': game
            }
        
        # Outside the lock to avoid potential deadlocks with send_message
        try:
            # Send game_start notifications first
            print(f"Sending game_start to {self.clients[client1]['username']} as {colors[0]}")
            success1 = self.send_message(client1, {
                'type': 'game_start',
                'color': colors[0],
                'opponent': self.clients[client2]['username']
            })
            
            print(f"Sending game_start to {self.clients[client2]['username']} as {colors[1]}")
            success2 = self.send_message(client2, {
                'type': 'game_start',
                'color': colors[1],
                'opponent': self.clients[client1]['username']
            })
            
            # If either message failed, clean up the game
            if not (success1 and success2):
                print("Failed to send game_start messages. Cleaning up game.")
                with self.lock:
                    self.cleanup_game(game_id)
                return
            
            # Small delay to ensure game_start messages are processed first
            time.sleep(0.1)
            
            # Send initial board state to both players
            board_state = game.get_board_state()
            
            print(f"Sending board_state to {self.clients[client1]['username']}")
            self.send_message(client1, {
                'type': 'board_state',
                'board': board_state,
                'turn': game.get_current_turn()
            })
            
            print(f"Sending board_state to {self.clients[client2]['username']}")
            self.send_message(client2, {
                'type': 'board_state',
                'board': board_state,
                'turn': game.get_current_turn()
            })
            
            print(f"Game {game_id} successfully started")
        except Exception as e:
            print(f"Error during matchmaking: {e}")
            # Clean up the game if something went wrong
            with self.lock:
                self.cleanup_game(game_id)
    
    def handle_move(self, client_socket, from_pos, to_pos):
        with self.lock:
            game_id = self.clients[client_socket]['game']
            
            if game_id is None:
                self.send_message(client_socket, {'type': 'error', 'message': 'Not in a game'})
                return
            
            game = self.games[game_id]['game']
            player_color = self.clients[client_socket]['color']
            
            # Check if it's this player's turn
            if game.get_current_turn() != player_color:
                self.send_message(client_socket, {'type': 'error', 'message': 'Not your turn'})
                return
            
            # Make the move
            move_result = game.make_move(from_pos, to_pos)
            
            if move_result['valid']:
                # Get opponent socket
                opponent = self.games[game_id]['white'] if player_color == 'black' else self.games[game_id]['black']
                
                # Update both players with new board state
                board_state = game.get_board_state()
                game_status = game.get_game_status()
                
                # Additional game information
                game_info = {
                    'move_count': game.get_move_count(),
                    'duration': game.get_formatted_duration(),
                    'points': {
                        'white': game.get_points('white'),
                        'black': game.get_points('black')
                    }
                }
                
                self.send_message(client_socket, {
                    'type': 'move_result',
                    'valid': True,
                    'board': board_state,
                    'turn': game.get_current_turn(),
                    'status': game_status,
                    'game_info': game_info
                })
                
                self.send_message(opponent, {
                    'type': 'opponent_move',
                    'from': from_pos,
                    'to': to_pos,
                    'board': board_state,
                    'turn': game.get_current_turn(),
                    'status': game_status,
                    'game_info': game_info
                })
                
                # Check if game is over
                if game_status['game_over']:
                    self.handle_game_over(game_id, game_status, game_info)
            else:
                # Invalid move
                self.send_message(client_socket, {
                    'type': 'move_result',
                    'valid': False,
                    'message': move_result.get('message', 'Invalid move')
                })
    
    def handle_resignation(self, client_socket):
        with self.lock:
            game_id = self.clients[client_socket]['game']
            
            if game_id is None:
                return
            
            game = self.games[game_id]['game']
            player_color = self.clients[client_socket]['color']
            winner_color = 'black' if player_color == 'white' else 'white'
            
            # Get opponent socket
            opponent = self.games[game_id]['white'] if player_color == 'black' else self.games[game_id]['black']
            
            # Additional game information
            game_info = {
                'move_count': game.get_move_count(),
                'duration': game.get_formatted_duration(),
                'points': {
                    'white': game.get_points('white'),
                    'black': game.get_points('black')
                }
            }
            
            # Notify both players
            self.send_message(client_socket, {
                'type': 'game_over',
                'result': 'resignation',
                'winner': winner_color,
                'game_info': game_info
            })
            
            self.send_message(opponent, {
                'type': 'game_over',
                'result': 'opponent_resigned',
                'winner': winner_color,
                'game_info': game_info
            })
            
            # Clean up game
            self.cleanup_game(game_id)
    
    def handle_game_over(self, game_id, status, game_info):
        white_client = self.games[game_id]['white']
        black_client = self.games[game_id]['black']
        
        self.send_message(white_client, {
            'type': 'game_over',
            'result': status['result'],
            'winner': status['winner'],
            'game_info': game_info
        })
        
        self.send_message(black_client, {
            'type': 'game_over',
            'result': status['result'],
            'winner': status['winner'],
            'game_info': game_info
        })
        
        # Clean up game
        self.cleanup_game(game_id)
    
    def handle_chat(self, client_socket, content):
        with self.lock:
            game_id = self.clients[client_socket]['game']
            
            if game_id is None:
                return
            
            username = self.clients[client_socket]['username']
            
            # Get opponent socket
            opponent = self.games[game_id]['white'] if client_socket == self.games[game_id]['black'] else self.games[game_id]['black']
            
            # Forward chat message to opponent
            self.send_message(opponent, {
                'type': 'chat',
                'sender': username,
                'content': content
            })
    
    def cleanup_game(self, game_id):
        if game_id not in self.games:
            return
        
        white_client = self.games[game_id]['white']
        black_client = self.games[game_id]['black']
        
        # Reset client data
        if white_client in self.clients:
            self.clients[white_client]['game'] = None
            self.clients[white_client]['color'] = None
        
        if black_client in self.clients:
            self.clients[black_client]['game'] = None
            self.clients[black_client]['color'] = None
        
        # Remove game
        del self.games[game_id]
    
    def disconnect_client(self, client_socket):
        with self.lock:
            # Remove client from waiting queue if they're in it
            if client_socket in self.waiting_queue:
                self.waiting_queue.remove(client_socket)
            
            # Check if client is in a game
            if client_socket in self.clients and self.clients[client_socket]['game'] is not None:
                game_id = self.clients[client_socket]['game']
                
                # Handle as a resignation if game is still active
                if game_id in self.games:
                    player_color = self.clients[client_socket]['color']
                    winner_color = 'black' if player_color == 'white' else 'white'
                    
                    # Get opponent socket
                    opponent = self.games[game_id]['white'] if client_socket == self.games[game_id]['black'] else self.games[game_id]['black']
                    
                    # Notify opponent
                    self.send_message(opponent, {
                        'type': 'game_over',
                        'result': 'opponent_disconnected',
                        'winner': winner_color
                    })
                    
                    # Clean up game
                    self.cleanup_game(game_id)
            
            # Remove client from clients dict
            if client_socket in self.clients:
                del self.clients[client_socket]
            
            # Close socket
            try:
                client_socket.close()
            except:
                pass
    
    def send_message(self, client_socket, message):
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
            return True
        except:
            # If sending fails, disconnect the client
            self.disconnect_client(client_socket)
            return False


if __name__ == "__main__":
    server = ChessServer()
    server.start() 