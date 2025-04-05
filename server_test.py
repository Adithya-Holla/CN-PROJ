import socket
import threading
import json
import time
import traceback
import queue

# Queue for players waiting for a match
waiting_players = queue.Queue()
# Lock for thread-safe operations
player_lock = threading.Lock()
# Connected clients
clients = {}

def handle_client(client_socket, addr):
    username = "Unknown"
    game_started = False
    opponent_socket = None
    player_color = None
    
    try:
        print(f"New connection from {addr}")
        client_socket.settimeout(300)  # Set a longer timeout (5 minutes)
        
        # Receive username
        data = client_socket.recv(1024).decode('utf-8')
        if not data:
            print(f"No data received from {addr}")
            return
        
        try:
            username = json.loads(data).get('username', 'Unknown')
            print(f"Client connected: {username} from {addr}")
            
            # Store client in connected clients dict
            with player_lock:
                clients[username] = {
                    'socket': client_socket,
                    'in_game': False,
                    'opponent': None
                }
            
        except json.JSONDecodeError:
            print(f"Invalid JSON from {addr}: {data}")
            return
        
        # Send welcome message
        welcome_msg = {'type': 'connection_success', 'message': f'Welcome {username}!'}
        client_socket.send(json.dumps(welcome_msg).encode('utf-8'))
        print(f"Sent welcome message to {username}")
        
        # Wait for client to send messages
        client_socket.settimeout(None)  # Remove timeout for receiving messages
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    print(f"Client {username} disconnected (no data)")
                    break
                
                print(f"Received from {username}: {data}")
                try:
                    message = json.loads(data)
                    print(f"Parsed message: {message}")
                    msg_type = message.get('type')
                    print(f"Message type: {msg_type}")
                    
                    # Handle find_game request
                    if msg_type == 'find_game' and not game_started:
                        print(f"Received find_game request from {username}")
                        
                        # Send queue message
                        queue_msg = {'type': 'queue', 'message': 'Looking for opponent...'}
                        queue_data = json.dumps(queue_msg).encode('utf-8')
                        client_socket.send(queue_data)
                        print(f"Sent queue message to {username}")
                        
                        # Check if there's a waiting player
                        matched_player = None
                        
                        # Try to get a waiting player
                        if not waiting_players.empty():
                            with player_lock:
                                try:
                                    matched_player = waiting_players.get_nowait()
                                    # Verify this player is still connected and waiting
                                    if matched_player not in clients or clients[matched_player]['in_game']:
                                        matched_player = None
                                except queue.Empty:
                                    matched_player = None
                        
                        if matched_player:
                            # We found a match!
                            print(f"Matched {username} with {matched_player}")
                            
                            # Get the opponent's socket
                            with player_lock:
                                if matched_player in clients:
                                    opponent_socket = clients[matched_player]['socket']
                                    # Mark both players as in a game
                                    clients[username]['in_game'] = True
                                    clients[matched_player]['in_game'] = True
                                    clients[username]['opponent'] = matched_player
                                    clients[matched_player]['opponent'] = username
                                    
                                    # Assign colors - matched player (who was waiting) is white
                                    player_color = 'black'
                                    opponent_color = 'white'
                                    
                                    # Store colors in client data
                                    clients[username]['color'] = player_color
                                    clients[matched_player]['color'] = opponent_color
                                else:
                                    # Opponent disconnected while matchmaking
                                    print(f"Opponent {matched_player} disconnected during matchmaking")
                                    matched_player = None
                            
                            if matched_player and opponent_socket:
                                # Start game for both players
                                
                                # Send game_start to the current player (black)
                                game_start_msg = {
                                    'type': 'game_start',
                                    'color': player_color,
                                    'opponent': matched_player
                                }
                                game_start_data = json.dumps(game_start_msg).encode('utf-8')
                                client_socket.send(game_start_data)
                                print(f"Sent game_start message to {username} (black)")
                                
                                # Send game_start to the opponent (white)
                                opponent_game_start_msg = {
                                    'type': 'game_start',
                                    'color': opponent_color,
                                    'opponent': username
                                }
                                opponent_socket.send(json.dumps(opponent_game_start_msg).encode('utf-8'))
                                print(f"Sent game_start message to {matched_player} (white)")
                                
                                # Create initial board state
                                board_state = [[None for _ in range(8)] for _ in range(8)]
                                
                                # Add some test pieces
                                board_state[0][0] = {'color': 'black', 'type': 'rook', 'has_moved': False}
                                board_state[0][4] = {'color': 'black', 'type': 'king', 'has_moved': False}
                                board_state[7][0] = {'color': 'white', 'type': 'rook', 'has_moved': False}
                                board_state[7][4] = {'color': 'white', 'type': 'king', 'has_moved': False}
                                
                                # Send board state to both players
                                board_msg = {
                                    'type': 'board_state',
                                    'board': board_state,
                                    'turn': 'white'
                                }
                                board_data = json.dumps(board_msg).encode('utf-8')
                                
                                client_socket.send(board_data)
                                print(f"Sent board_state message to {username}")
                                
                                opponent_socket.send(board_data)
                                print(f"Sent board_state message to {matched_player}")
                                
                                game_started = True
                            else:
                                # Add back to queue if matching failed
                                waiting_players.put(username)
                                error_msg = {
                                    'type': 'error',
                                    'message': 'Opponent disconnected during matchmaking, trying again...'
                                }
                                client_socket.send(json.dumps(error_msg).encode('utf-8'))
                        else:
                            # No match found, add to waiting queue
                            print(f"Adding {username} to waiting queue")
                            waiting_players.put(username)
                            
                            # Send updated queue message
                            queue_update_msg = {'type': 'queue', 'message': 'Waiting for opponent...'}
                            client_socket.send(json.dumps(queue_update_msg).encode('utf-8'))
                    
                    # Handle chat messages
                    elif message.get('type') == 'chat' and game_started:
                        # Forward chat to opponent
                        with player_lock:
                            opponent_name = clients[username]['opponent']
                            if opponent_name in clients:
                                opponent_socket = clients[opponent_name]['socket']
                                
                                chat_message = {
                                    'type': 'chat',
                                    'sender': username,
                                    'content': message.get('content', '')
                                }
                                opponent_socket.send(json.dumps(chat_message).encode('utf-8'))
                                print(f"Forwarded chat from {username} to {opponent_name}")
                    
                    # Handle move requests
                    elif message.get('type') == 'move' and game_started:
                        # Process move and update game state...
                        from_pos = message.get('from')
                        to_pos = message.get('to')
                        
                        # Update board state (simplified)
                        board_state = [[None for _ in range(8)] for _ in range(8)]
                        board_state[0][0] = {'color': 'black', 'type': 'rook', 'has_moved': False}
                        board_state[0][4] = {'color': 'black', 'type': 'king', 'has_moved': False}
                        board_state[7][0] = {'color': 'white', 'type': 'rook', 'has_moved': False}
                        board_state[7][4] = {'color': 'white', 'type': 'king', 'has_moved': False}
                        
                        # Determine next player's turn
                        next_turn = 'black' if player_color == 'white' else 'white'
                        
                        # Send move result to current player
                        move_result = {
                            'type': 'move_result',
                            'valid': True,
                            'board': board_state,
                            'turn': next_turn,
                            'status': {'game_over': False}
                        }
                        client_socket.send(json.dumps(move_result).encode('utf-8'))
                        
                        # Send opponent_move to opponent
                        with player_lock:
                            opponent_name = clients[username]['opponent']
                            if opponent_name in clients:
                                opponent_socket = clients[opponent_name]['socket']
                                
                                opponent_move = {
                                    'type': 'opponent_move',
                                    'from': from_pos,
                                    'to': to_pos,
                                    'board': board_state,
                                    'turn': next_turn,
                                    'status': {'game_over': False}
                                }
                                opponent_socket.send(json.dumps(opponent_move).encode('utf-8'))
                                print(f"Sent move from {username} to {opponent_name}")
                    
                    # Handle resignation
                    elif message.get('type') == 'resign' and game_started:
                        # Handle player resignation
                        with player_lock:
                            opponent_name = clients[username]['opponent']
                            if opponent_name in clients:
                                opponent_socket = clients[opponent_name]['socket']
                                
                                # Notify the resigning player
                                resign_result = {
                                    'type': 'game_over',
                                    'result': 'resignation',
                                    'winner': 'opponent'
                                }
                                client_socket.send(json.dumps(resign_result).encode('utf-8'))
                                
                                # Notify the opponent
                                opponent_win = {
                                    'type': 'game_over',
                                    'result': 'opponent_resigned',
                                    'winner': clients[opponent_name]['color']
                                }
                                opponent_socket.send(json.dumps(opponent_win).encode('utf-8'))
                                print(f"{username} resigned, {opponent_name} wins")
                                
                                # Reset game state
                                clients[username]['in_game'] = False
                                clients[username]['opponent'] = None
                                clients[opponent_name]['in_game'] = False
                                clients[opponent_name]['opponent'] = None
                                game_started = False
                    
                    # Handle other message types if needed
                    else:
                        print(f"Unknown or inappropriate message type: {message.get('type')}")
                
                except json.JSONDecodeError as e:
                    print(f"JSON decode error from {username}: {e}")
                    continue
                except Exception as e:
                    print(f"Error processing message from {username}: {e}")
                    traceback.print_exc()
                    break
            except Exception as e:
                print(f"Error receiving from {username}: {e}")
                traceback.print_exc()
                break
    except Exception as e:
        print(f"Error handling client {username} from {addr}: {e}")
        traceback.print_exc()
    finally:
        try:
            client_socket.close()
        except:
            pass
        
        # Clean up client data
        with player_lock:
            if username in clients:
                # Notify opponent if in a game
                if clients[username]['in_game'] and clients[username]['opponent']:
                    opponent_name = clients[username]['opponent']
                    if opponent_name in clients:
                        try:
                            opponent_socket = clients[opponent_name]['socket']
                            disconnect_msg = {
                                'type': 'game_over',
                                'result': 'opponent_disconnected',
                                'winner': clients[opponent_name]['color']
                            }
                            opponent_socket.send(json.dumps(disconnect_msg).encode('utf-8'))
                            clients[opponent_name]['in_game'] = False
                            clients[opponent_name]['opponent'] = None
                            print(f"Notified {opponent_name} that {username} disconnected")
                        except:
                            pass
                
                # Remove client from dictionary
                del clients[username]
        
        print(f"Client {username} from {addr} disconnected")

def start_test_server(host='0.0.0.0', port=5555):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"Test server started on {host}:{port}")
        
        while True:
            try:
                client_socket, addr = server.accept()
                print(f"Connection from {addr}")
                
                client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
                client_thread.daemon = True
                client_thread.start()
            except Exception as e:
                print(f"Error accepting connection: {e}")
                traceback.print_exc()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    print("Starting test chess server...")
    start_test_server() 