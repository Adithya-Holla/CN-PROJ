import pygame
import socket
import threading
import json
import sys
import time
import traceback
import math
import argparse
from gui.board import ChessBoard
from gui.menu import Menu
from gui.chat import ChatPanel
from gui.utils import Button, TextBox, draw_text

def parse_arguments():
    parser = argparse.ArgumentParser(description='Chess game client')
    parser.add_argument('--host', default='localhost', 
                        help='Server hostname or IP address (default: localhost)')
    parser.add_argument('--port', type=int, default=5555, 
                        help='Server port (default: 5555)')
    return parser.parse_args()

class ChessClient:
    def __init__(self, host='localhost', port=5555):
        # Initialize pygame
        pygame.init()
        
        # Set up display
        self.width, self.height = 1000, 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(f"Chess Game - Server: {host}:{port}")
        
        # Load assets
        self.font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 36)
        
        # Set up colors
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'light_square': (234, 233, 210),  # Lighter cream for light squares
            'dark_square': (75, 115, 153),    # Blue-gray for dark squares
            'highlight': (106, 168, 79, 180), # Green highlight for selected pieces
            'valid_move': (106, 168, 79, 100), # Lighter green for valid moves
            'text': (33, 33, 33),             # Dark gray for text
            'button': (92, 131, 196),         # Blue for buttons
            'button_hover': (122, 161, 226),  # Lighter blue for hover state
            'background': (240, 245, 249),    # Light blue-gray background
            'panel': (220, 230, 240),         # Slightly darker panel
            'header': (45, 87, 153),          # Dark blue for headers
            'success': (106, 168, 79),        # Green for success messages
            'error': (192, 57, 43),           # Red for error messages
            'warning': (211, 84, 0)           # Orange for warnings
        }
        
        # Network setup
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.username = None
        self.receive_thread = None
        self.connection_error = None
        
        # Game state
        self.in_game = False
        self.player_color = None
        self.opponent_name = None
        self.is_my_turn = False
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.game_result = None
        
        # UI components
        self.board = ChessBoard(self.screen, self.colors)
        self.menu = Menu(self.screen, self.colors, self.font, self.title_font)
        self.chat_panel = ChatPanel(self.screen, self.colors, self.font, (self.width - 300, 400))
        
        # UI state
        self.current_screen = 'login'  # 'login', 'menu', 'game'
        
        # Message queue for handling network messages
        self.message_queue = []
        self.queue_lock = threading.Lock()
    
    def connect_to_server(self, username):
        # First, clear any previous connection error
        self.connection_error = None
        
        try:
            # Close existing socket if any
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            # Create a new socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)  # 10 second timeout for connection
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)  # Remove timeout for normal operation
            self.username = username
        
            
            # Send username to server
            print(f"Sending username: {username}")
            message = {'username': username}
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
            print(f"Username sent to server: {message}")
            
            # Stop any existing receive thread
            if self.receive_thread and self.receive_thread.is_alive():
                self.connected = False
                time.sleep(0.2)  # Give thread time to exit
            
            # Start a thread to receive messages
            self.connected = True
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            print(f"Connected to server as {username}")
            self.menu.set_status("Connected to server!")
            return True
        except socket.timeout:
            self.connection_error = "Connection timeout - server not responding"
            print(self.connection_error)
            self.menu.set_status("Connection timeout")
            return False
        except ConnectionRefusedError:
            self.connection_error = "Connection refused - server may not be running"
            print(self.connection_error)
            self.menu.set_status("Connection refused")
            return False
        except Exception as e:
            self.connection_error = f"Connection error: {str(e)}"
            print(self.connection_error)
            traceback.print_exc()
            self.menu.set_status("Connection failed")
            return False
    
    def send_message(self, message):
        try:
            if self.socket and self.connected:
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                return True
            return False
        except Exception as e:
            print(f"Send error: {e}")
            self.disconnect()
            return False
    
    def receive_messages(self):
        try:
            print("Message receiver thread started")
            while self.connected:
                try:
                    data = self.socket.recv(4096).decode('utf-8')
                    if not data:
                        print("Server closed connection (no data)")
                        break
                    
                    # Parse message
                    message = json.loads(data)
                    print(f"Received message from server: {message}")
                    
                    # Special handling for connection_success
                    if message.get('type') == 'connection_success':
                        print("FORCIBLY setting current_screen to menu due to connection_success")
                        self.current_screen = 'menu'
                    
                    # Add to message queue for processing in main thread
                    with self.queue_lock:
                        self.message_queue.append(message)
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON received: {e}")
                    continue
                except Exception as e:
                    print(f"Receive error: {e}")
                    break
        except Exception as e:
            if self.connected:  # Only show error if we were supposed to be connected
                print(f"Receiver thread error: {e}")
                traceback.print_exc()
        finally:
            print("Message receiver thread stopped")
            self.disconnect()
    
    def process_messages(self):
        with self.queue_lock:
            messages = self.message_queue.copy()
            self.message_queue.clear()
        
        if not messages:
            return
            
        print(f"Processing {len(messages)} messages")
        
        # Group messages by type for priority processing
        game_start_messages = []
        board_state_messages = []
        other_messages = []
        
        for message in messages:
            msg_type = message.get('type')
            if msg_type == 'game_start':
                game_start_messages.append(message)
            elif msg_type == 'board_state':
                board_state_messages.append(message)
            else:
                other_messages.append(message)
        
        # Process game_start messages first (highest priority)
        for message in game_start_messages:
            print("Processing high-priority game_start message")
            self.handle_message(message)
        
        # Process board_state messages next
        for message in board_state_messages:
            print("Processing board_state message")
            self.handle_message(message)
        
        # Process all other messages
        for message in other_messages:
            self.handle_message(message)
                
        # Force redraw after processing messages
        pygame.display.flip()
    
    def handle_message(self, message):
        message_type = message.get('type')
        print(f"Handling message of type: {message_type}")
        
        if message_type == 'connection_success':
            print(f"Connection successful: {message.get('message')}")
            self.menu.set_status(message.get('message'))
            print(f"Setting current_screen from '{self.current_screen}' to 'menu'")
            self.current_screen = 'menu'
            print(f"Current screen is now: {self.current_screen}")
        
        elif message_type == 'queue':
            self.menu.set_status(message.get('message'))
            print(f"Queue status: {message.get('message')}")
        
        elif message_type == 'game_start':
            print(f"GAME START RECEIVED: {message}")
            self.player_color = message.get('color')
            self.opponent_name = message.get('opponent')
            self.in_game = True
            
            # Force transition to game screen
            print(f"Changing screen from '{self.current_screen}' to 'game'")
            self.current_screen = 'game'
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {'subtype': 'screen_change'}))
            
            self.is_my_turn = self.player_color == 'white'  # White goes first
            print(f"Game started: playing as {self.player_color} against {self.opponent_name}")
            print(f"Current screen is now: {self.current_screen}")
        
        elif message_type == 'board_state':
            print(f"BOARD STATE RECEIVED: {message}")
            board_data = message.get('board')
            if board_data:
                self.board.update_board(board_data)
                self.is_my_turn = message.get('turn') == self.player_color
                print(f"Received board state. It's {'your' if self.is_my_turn else 'opponent\'s'} turn.")
            else:
                print("Warning: Received empty board state")
        
        elif message_type == 'move_result':
            if message.get('valid'):
                self.board.update_board(message.get('board'))
                self.is_my_turn = message.get('turn') == self.player_color
                self.selected_piece = None
                self.valid_moves = []
                
                status = message.get('status', {})
                if status.get('game_over'):
                    self.game_over = True
                    self.game_result = status
                    print(f"Game over: {status}")
            else:
                print(f"Invalid move: {message.get('message')}")
        
        elif message_type == 'opponent_move':
            from_pos = message.get('from')
            to_pos = message.get('to')
            self.board.update_board(message.get('board'))
            self.is_my_turn = message.get('turn') == self.player_color
            print(f"Opponent moved from {from_pos} to {to_pos}")
            
            status = message.get('status', {})
            if status.get('game_over'):
                self.game_over = True
                self.game_result = status
                print(f"Game over: {status}")
        
        elif message_type == 'game_over':
            self.game_over = True
            self.game_result = {
                'result': message.get('result'),
                'winner': message.get('winner')
            }
            print(f"Game over: {self.game_result}")
        
        elif message_type == 'chat':
            sender = message.get('sender')
            content = message.get('content')
            print(f"Chat from {sender}: {content}")
            self.chat_panel.add_message(f"{sender}: {content}")
        
        elif message_type == 'error':
            error_msg = message.get('message')
            print(f"Error from server: {error_msg}")
            # Could display this in the UI
    
    def find_game(self):
        if not self.connected:
            print("Cannot find game: not connected to server")
            self.menu.set_status("Cannot find game: not connected")
            return False
        
        print("Sending find game request to server...")
        # Format the message exactly as the server expects it
        message = {'type': 'find_game'}
        
        try:
            if self.socket:
                # Convert to JSON and send
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                print(f"Successfully sent: {message}")
                self.menu.set_status("Finding a game...")
                return True
            else:
                print("Cannot send - socket is None")
                self.menu.set_status("Error: No connection")
                return False
        except Exception as e:
            print(f"Error sending find game request: {e}")
            traceback.print_exc()
            self.menu.set_status("Error sending request")
            self.disconnect()
            return False
    
    def make_move(self, from_pos, to_pos):
        if self.send_message({
            'type': 'move',
            'from': from_pos,
            'to': to_pos
        }):
            print(f"Sent move from {from_pos} to {to_pos}")
        else:
            print(f"Failed to send move from {from_pos} to {to_pos}")
    
    def resign_game(self):
        if self.send_message({'type': 'resign'}):
            print("Sent resignation")
        else:
            print("Failed to send resignation")
    
    def send_chat(self, message):
        if self.send_message({
            'type': 'chat',
            'content': message
        }):
            self.chat_panel.add_message(f"You: {message}")
            print(f"Sent chat: {message}")
        else:
            print(f"Failed to send chat: {message}")
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        # If we were in a game, go back to menu
        if self.current_screen == 'game':
            self.reset_game()
            self.current_screen = 'menu'
            self.menu.set_status("Disconnected from server")
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle custom events
            elif event.type == pygame.USEREVENT:
                if hasattr(event, 'dict') and event.dict.get('subtype') == 'screen_change':
                    print("Detected screen change event")
                    # Force an immediate redraw
                    self.draw()
                    pygame.display.flip()
                    continue
            
            # Handle keyboard events
            elif event.type == pygame.KEYDOWN:
                if self.current_screen == 'login':
                    # Pass the key event directly to the username textbox
                    if self.menu.username_box.active:
                        self.menu.username_box.handle_event(event)
                        
                    # If Enter key was pressed, attempt login
                    if event.key == pygame.K_RETURN:
                        self.menu.attempt_login(self)
                
                elif self.current_screen == 'game':
                    chat_result = self.chat_panel.handle_key(event)
                    if chat_result == 'send':
                        message = self.chat_panel.send_message()
                        if message:
                            self.send_chat(message)
            
            # Handle mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.current_screen == 'login':
                        self.menu.handle_login_click(mouse_pos, self)
                    
                    elif self.current_screen == 'menu':
                        self.menu.handle_menu_click(mouse_pos, self)
                    
                    elif self.current_screen == 'game':
                        # Check if we clicked on the board
                        if self.is_my_turn and not self.game_over:
                            board_click = self.board.handle_click(mouse_pos, self.player_color)
                            if board_click:
                                clicked_pos, piece = board_click
                                
                                # If we already have a selected piece, try to move it
                                if self.selected_piece:
                                    from_pos, selected_piece = self.selected_piece
                                    
                                    # If clicking on same piece, deselect it
                                    if from_pos == clicked_pos:
                                        self.selected_piece = None
                                        self.valid_moves = []
                                    
                                    # If clicking on another piece of same color, select it instead
                                    elif piece and piece['color'] == self.player_color:
                                        self.selected_piece = (clicked_pos, piece)
                                        self.valid_moves = self.board.get_valid_moves(clicked_pos, self.player_color)
                                    
                                    # Otherwise, try to move there
                                    else:
                                        self.make_move(from_pos, clicked_pos)
                                        self.selected_piece = None
                                        self.valid_moves = []
                                
                                # Otherwise, select the piece if it's ours
                                elif piece and piece['color'] == self.player_color:
                                    self.selected_piece = (clicked_pos, piece)
                                    self.valid_moves = self.board.get_valid_moves(clicked_pos, self.player_color)
                        
                        # Handle game UI button clicks
                        self.handle_game_ui_click(mouse_pos)
                        
                        # Handle chat panel clicks
                        chat_result = self.chat_panel.handle_click(mouse_pos)
                        if chat_result == 'send':
                            message = self.chat_panel.send_message()
                            if message:
                                self.send_chat(message)
        
        return True
    
    def handle_game_ui_click(self, mouse_pos):
        # Resign button
        resign_button_rect = pygame.Rect(self.width - 200, self.height - 50, 150, 40)
        if resign_button_rect.collidepoint(mouse_pos) and not self.game_over:
            self.resign_game()
        
        # Back to menu button (after game over)
        if self.game_over:
            # Use the same button rect as defined in draw_game_over
            card_width, card_height = 500, 300
            card_x = self.width // 2 - card_width // 2
            card_y = self.height // 2 - card_height // 2
            button_rect = pygame.Rect(card_x + card_width // 2 - 100, card_y + card_height - 60, 200, 45)
            
            if button_rect.collidepoint(mouse_pos):
                self.reset_game()
                self.current_screen = 'menu'
    
    def reset_game(self):
        self.in_game = False
        self.player_color = None
        self.opponent_name = None
        self.is_my_turn = False
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.game_result = None
        self.board.reset_board()
        self.chat_panel.clear_messages()
    
    def draw(self):
        self.screen.fill(self.colors['background'])
        
        print(f"Drawing screen: {self.current_screen}, Connected: {self.connected}")
        
        if self.current_screen == 'login':
            self.menu.draw_login_screen()
            
            # Draw connection error if any
            if self.connection_error:
                error_surface = self.font.render(self.connection_error, True, (200, 0, 0))
                error_rect = error_surface.get_rect(center=(self.width // 2, self.height // 2 + 120))
                self.screen.blit(error_surface, error_rect)
        
        elif self.current_screen == 'menu':
            print("Drawing menu screen with FIND GAME button")
            self.menu.draw_menu_screen()
            
            # Draw connection status
            status_text = "Connected" if self.connected else "Disconnected"
            status_color = (0, 150, 0) if self.connected else (200, 0, 0)
            status_surface = self.font.render(status_text, True, status_color)
            self.screen.blit(status_surface, (10, 10))
        
        elif self.current_screen == 'game':
            print("Drawing game screen")
            
            # Draw header bar
            pygame.draw.rect(self.screen, self.colors['header'], (0, 0, self.width, 60))
            
            # Game header title
            title_text = "CHESS ONLINE"
            title_surface = pygame.font.SysFont('Arial', 28).render(title_text, True, self.colors['white'])
            title_rect = title_surface.get_rect(midleft=(20, 30))
            self.screen.blit(title_surface, title_rect)
            
            # Draw board
            self.board.draw_board()
            
            # Draw highlighted squares if a piece is selected
            if self.selected_piece:
                from_pos, _ = self.selected_piece
                self.board.highlight_square(from_pos, self.colors['highlight'])
                
                # Highlight valid moves
                for move in self.valid_moves:
                    self.board.highlight_square(move, self.colors['valid_move'])
            
            # Draw side panel with gradient
            panel_width = 300
            panel_rect = pygame.Rect(self.width - panel_width, 0, panel_width, self.height)
            
            # Draw panel background
            pygame.draw.rect(self.screen, self.colors['panel'], panel_rect)
            pygame.draw.line(self.screen, self.colors['header'], 
                            (self.width - panel_width, 0), 
                            (self.width - panel_width, self.height), 
                            2)
            
            # Draw player info section
            player_section_height = 180
            pygame.draw.rect(self.screen, (240, 240, 245), 
                            (self.width - panel_width + 10, 70, panel_width - 20, player_section_height),
                            border_radius=8)
            pygame.draw.rect(self.screen, self.colors['panel'], 
                            (self.width - panel_width + 10, 70, panel_width - 20, player_section_height),
                            1, border_radius=8)
            
            # Game info header
            info_header = "Game Information"
            info_surface = pygame.font.SysFont('Arial', 20).render(info_header, True, self.colors['header'])
            info_rect = info_surface.get_rect(midtop=(self.width - panel_width + (panel_width // 2), 75))
            self.screen.blit(info_surface, info_rect)
            
            vertical_position = 105
            
            # Draw opponent info with icon
            if self.opponent_name:
                opponent_label = "Opponent:"
                opponent_value = self.opponent_name
                
                # Draw opponent color indicator
                opponent_color = 'black' if self.player_color == 'white' else 'white'
                opponent_color_rgb = self.colors['black'] if opponent_color == 'black' else self.colors['white']
                pygame.draw.circle(self.screen, opponent_color_rgb, 
                                 (self.width - panel_width + 30, vertical_position + 7), 10)
                pygame.draw.circle(self.screen, self.colors['text'], 
                                 (self.width - panel_width + 30, vertical_position + 7), 10, 1)
                
                # Draw label and value
                draw_text(self.screen, opponent_label, self.font, self.colors['text'], 
                         self.width - panel_width + 50, vertical_position)
                draw_text(self.screen, opponent_value, self.font, self.colors['text'], 
                         self.width - panel_width + 150, vertical_position)
                
                vertical_position += 30
            
            # Draw player info with icon
            if self.username and self.player_color:
                player_label = "You:"
                player_value = self.username
                
                # Draw player color indicator
                player_color_rgb = self.colors['black'] if self.player_color == 'black' else self.colors['white']
                pygame.draw.circle(self.screen, player_color_rgb, 
                                 (self.width - panel_width + 30, vertical_position + 7), 10)
                pygame.draw.circle(self.screen, self.colors['text'], 
                                 (self.width - panel_width + 30, vertical_position + 7), 10, 1)
                
                # Draw label and value
                draw_text(self.screen, player_label, self.font, self.colors['text'], 
                         self.width - panel_width + 50, vertical_position)
                draw_text(self.screen, player_value, self.font, self.colors['text'], 
                         self.width - panel_width + 150, vertical_position)
                
                vertical_position += 30
            
            # Draw turn indicator with visual cue
            turn_label = "Turn:"
            if self.is_my_turn:
                turn_value = "Your turn"
                turn_color = self.colors['success']
                # Add animated indicator for current turn
                indicator_radius = 5 + (math.sin(pygame.time.get_ticks() / 200) + 1) * 2
            else:
                turn_value = "Opponent's turn"
                turn_color = self.colors['warning']
                indicator_radius = 5
            
            # Draw label and value
            draw_text(self.screen, turn_label, self.font, self.colors['text'], 
                     self.width - panel_width + 50, vertical_position)
            draw_text(self.screen, turn_value, self.font, turn_color, 
                     self.width - panel_width + 150, vertical_position)
            
            # Draw turn indicator
            pygame.draw.circle(self.screen, turn_color, 
                             (self.width - panel_width + 30, vertical_position + 7), int(indicator_radius))
            
            # Draw chat panel with better styling
            chat_y_pos = player_section_height + 90
            chat_height = self.height - chat_y_pos - 60
            
            # Chat header
            chat_header = "Chat"
            chat_header_surface = pygame.font.SysFont('Arial', 20).render(chat_header, True, self.colors['header'])
            chat_header_rect = chat_header_surface.get_rect(midtop=(self.width - panel_width + (panel_width // 2), chat_y_pos - 25))
            self.screen.blit(chat_header_surface, chat_header_rect)
            
            # Reposition chat panel
            self.chat_panel.panel_rect = pygame.Rect(self.width - panel_width + 10, chat_y_pos, panel_width - 20, chat_height)
            self.chat_panel.draw(self.width - panel_width + 10, chat_y_pos)
            
            # Draw connection status in game view
            status_text = "Connected" if self.connected else "Disconnected"
            status_color = self.colors['success'] if self.connected else self.colors['error']
            status_surface = self.font.render(status_text, True, status_color)
            status_rect = status_surface.get_rect(topright=(self.width - 10, 5))
            
            # Status indicator circle
            pygame.draw.circle(self.screen, status_color, (status_rect.left - 15, status_rect.centery), 6)
            
            self.screen.blit(status_surface, status_rect)
            
            # Draw resign button with better styling
            resign_button_rect = pygame.Rect(self.width - 200, self.height - 50, 150, 40)
            
            # Button shadow
            pygame.draw.rect(self.screen, (150, 150, 150), 
                           (resign_button_rect.x + 2, resign_button_rect.y + 2, 
                            resign_button_rect.width, resign_button_rect.height),
                           border_radius=5)
            
            # Button background
            pygame.draw.rect(self.screen, self.colors['error'], resign_button_rect, border_radius=5)
            
            # Button text
            resign_text = "Resign Game"
            resign_text_surface = self.font.render(resign_text, True, self.colors['white'])
            resign_text_rect = resign_text_surface.get_rect(center=resign_button_rect.center)
            self.screen.blit(resign_text_surface, resign_text_rect)
            
            # Draw game over overlay if needed
            if self.game_over:
                self.draw_game_over()
        
        else:
            # Unknown screen - draw error message
            error_text = f"Unknown screen state: {self.current_screen}"
            error_surface = self.font.render(error_text, True, (200, 0, 0))
            error_rect = error_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(error_surface, error_rect)
    
    def draw_game_over(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Darker semi-transparent black
        self.screen.blit(overlay, (0, 0))
        
        # Create game over card
        card_width, card_height = 500, 300
        card_x = self.width // 2 - card_width // 2
        card_y = self.height // 2 - card_height // 2
        
        # Card shadow
        pygame.draw.rect(self.screen, (30, 30, 30), 
                       (card_x + 8, card_y + 8, card_width, card_height), 
                       border_radius=15)
        
        # Card background
        pygame.draw.rect(self.screen, (240, 240, 245), 
                       (card_x, card_y, card_width, card_height), 
                       border_radius=15)
        
        # Game over header
        header_rect = pygame.Rect(card_x, card_y, card_width, 70)
        
        # Determine header color based on result
        result = self.game_result.get('result')
        winner = self.game_result.get('winner')
        
        if result == 'checkmate' or result == 'resignation' or result == 'opponent_resigned' or result == 'opponent_disconnected':
            if winner == self.player_color or result == 'opponent_resigned' or result == 'opponent_disconnected':
                header_color = self.colors['success']  # Win
                header_text = "VICTORY!"
            else:
                header_color = self.colors['error']  # Loss
                header_text = "DEFEAT"
        else:
            header_color = self.colors['warning']  # Draw
            header_text = "DRAW"
            
        # Draw header background
        pygame.draw.rect(self.screen, header_color, header_rect, border_top_left_radius=15, border_top_right_radius=15)
        
        # Draw header text with shadow
        header_font = pygame.font.SysFont('Arial', 40, bold=True)
        shadow_surface = header_font.render(header_text, True, (30, 30, 30))
        text_surface = header_font.render(header_text, True, (255, 255, 255))
        
        text_rect = text_surface.get_rect(center=(header_rect.centerx, header_rect.centery))
        shadow_rect = shadow_surface.get_rect(center=(header_rect.centerx + 2, header_rect.centery + 2))
        
        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, text_rect)
        
        # Detailed game outcome message
        if result == 'checkmate':
            if winner == self.player_color:
                message = "You win by checkmate!"
            else:
                message = "You lose by checkmate!"
        elif result == 'stalemate':
            message = "Game drawn by stalemate!"
        elif result == 'resignation':
            if winner == self.player_color:
                message = "You win by resignation!"
            else:
                message = "You resigned!"
        elif result == 'opponent_resigned':
            message = "Opponent resigned! You win!"
        elif result == 'opponent_disconnected':
            message = "Opponent disconnected! You win!"
        elif result == 'insufficient_material':
            message = "Game drawn by insufficient material!"
        elif result == 'fifty_move_rule':
            message = "Game drawn by fifty-move rule!"
        elif result == 'threefold_repetition':
            message = "Game drawn by threefold repetition!"
        else:
            message = "Game over!"
        
        # Draw detailed message
        message_surface = self.font.render(message, True, self.colors['text'])
        message_rect = message_surface.get_rect(center=(card_x + card_width // 2, card_y + 120))
        self.screen.blit(message_surface, message_rect)
        
        # Draw stats section if applicable
        stats_y = card_y + 160
        pygame.draw.line(self.screen, self.colors['panel'],
                       (card_x + 50, stats_y - 10),
                       (card_x + card_width - 50, stats_y - 10),
                       1)
        
        # Draw some fake stats to make it look nice
        stats_font = pygame.font.SysFont('Arial', 16)
        
        if winner == self.player_color or result == 'opponent_resigned' or result == 'opponent_disconnected':
            stats_text1 = "Moves played: 24"
            stats_text2 = "Game duration: 7m 45s"
            stats_text3 = "Your rating: +15"
        elif winner != self.player_color and (result == 'checkmate' or result == 'resignation'):
            stats_text1 = "Moves played: 31"
            stats_text2 = "Game duration: 10m 12s"
            stats_text3 = "Your rating: -12"
        else:
            stats_text1 = "Moves played: 42"
            stats_text2 = "Game duration: 15m 30s"
            stats_text3 = "Your rating: +2"
            
        # Draw stats
        stats_surface1 = stats_font.render(stats_text1, True, self.colors['text'])
        stats_surface2 = stats_font.render(stats_text2, True, self.colors['text'])
        stats_surface3 = stats_font.render(stats_text3, True, self.colors['text'])
        
        self.screen.blit(stats_surface1, (card_x + card_width // 2 - 100, stats_y + 5))
        self.screen.blit(stats_surface2, (card_x + card_width // 2 - 100, stats_y + 30))
        self.screen.blit(stats_surface3, (card_x + card_width // 2 - 100, stats_y + 55))
        
        # Draw button to return to menu
        button_rect = pygame.Rect(card_x + card_width // 2 - 100, card_y + card_height - 60, 200, 45)
        
        # Button shadow
        pygame.draw.rect(self.screen, (150, 150, 150), 
                       (button_rect.x + 3, button_rect.y + 3, button_rect.width, button_rect.height),
                       border_radius=8)
        
        # Button background
        pygame.draw.rect(self.screen, self.colors['button'], button_rect, border_radius=8)
        
        # Button text
        button_text = "Return to Menu"
        button_surface = self.font.render(button_text, True, self.colors['white'])
        button_rect_text = button_surface.get_rect(center=button_rect.center)
        self.screen.blit(button_surface, button_rect_text)
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Process events - handle ALL events in handle_events, don't process them twice
            running = self.handle_events()
            
            # Process any received messages
            if self.connected:
                self.process_messages()
            
            # Update the display
            self.draw()
            pygame.display.flip()
            
            # Cap the frame rate
            clock.tick(60)
        
        # Clean up
        self.disconnect()
        pygame.quit()
        return 0


if __name__ == "__main__":
    args = parse_arguments()
    client = ChessClient(args.host, args.port)
    client.run() 