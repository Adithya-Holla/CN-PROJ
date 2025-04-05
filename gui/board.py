import pygame
import os

class ChessBoard:
    def __init__(self, screen, colors, board_size=600):
        self.screen = screen
        self.colors = colors
        self.board_size = board_size
        self.square_size = board_size // 8
        self.board_position = (50, 50)  # Position on screen
        self.board = [[None for _ in range(8)] for _ in range(8)]
        
        # Create the pieces directory and generate placeholder images
        self.setup_assets()
        
        # Load piece images
        self.pieces_images = self.load_piece_images()
    
    def setup_assets(self):
        # Create assets directory if it doesn't exist
        if not os.path.exists('assets'):
            os.makedirs('assets')
        if not os.path.exists('assets/pieces'):
            os.makedirs('assets/pieces')
            
        # Generate placeholder images if any piece image is missing
        piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        colors = ['white', 'black']
        
        # Check if any image is missing
        missing_any = False
        for color in colors:
            for piece_type in piece_types:
                img_path = f'assets/pieces/{color}_{piece_type}.png'
                if not os.path.exists(img_path):
                    missing_any = True
                    break
            if missing_any:
                break
        
        # Generate all placeholder images if any is missing
        if missing_any:
            self.generate_placeholder_images()
    
    def load_piece_images(self):
        pieces = {}
        
        # Define piece names
        piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        colors = ['white', 'black']
        
        # Load each piece image
        for color in colors:
            pieces[color] = {}
            for piece_type in piece_types:
                try:
                    img_path = f'assets/pieces/{color}_{piece_type}.png'
                    img = pygame.image.load(img_path)
                    # Scale image to fit square
                    img = pygame.transform.scale(img, (self.square_size, self.square_size))
                    pieces[color][piece_type] = img
                except pygame.error:
                    # If image loading fails, use a placeholder
                    pieces[color][piece_type] = self.create_placeholder_piece(color, piece_type)
        
        return pieces
    
    def generate_placeholder_images(self):
        print("Generating placeholder chess piece images...")
        # Generate placeholder images for pieces
        piece_types = ['pawn', 'rook', 'knight', 'bishop', 'queen', 'king']
        colors = ['white', 'black']
        
        for color in colors:
            for piece_type in piece_types:
                surface = self.create_placeholder_piece(color, piece_type)
                try:
                    pygame.image.save(surface, f'assets/pieces/{color}_{piece_type}.png')
                    print(f"Created placeholder for {color} {piece_type}")
                except Exception as e:
                    print(f"Error creating placeholder for {color} {piece_type}: {e}")
    
    def create_placeholder_piece(self, color, piece_type):
        # Create a simple representation of a piece using shapes and text
        surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        
        # Draw the piece shape
        if color == 'white':
            fill_color = (240, 240, 240)
            outline_color = (50, 50, 50)
        else:
            fill_color = (70, 70, 70)
            outline_color = (240, 240, 240)
        
        # Draw different shapes for different pieces
        if piece_type == 'pawn':
            pygame.draw.circle(surface, fill_color, (self.square_size // 2, self.square_size // 2), self.square_size // 3)
        elif piece_type == 'rook':
            pygame.draw.rect(surface, fill_color, (self.square_size // 4, self.square_size // 4, 
                                                  self.square_size // 2, self.square_size // 2))
        elif piece_type == 'knight':
            points = [
                (self.square_size // 4, self.square_size // 4),
                (self.square_size * 3 // 4, self.square_size // 4),
                (self.square_size * 3 // 4, self.square_size * 3 // 4),
                (self.square_size // 4, self.square_size * 3 // 4),
                (self.square_size // 4, self.square_size // 2)
            ]
            pygame.draw.polygon(surface, fill_color, points)
        elif piece_type == 'bishop':
            pygame.draw.polygon(surface, fill_color, [
                (self.square_size // 2, self.square_size // 4),
                (self.square_size * 3 // 4, self.square_size * 3 // 4),
                (self.square_size // 4, self.square_size * 3 // 4)
            ])
        elif piece_type == 'queen':
            pygame.draw.polygon(surface, fill_color, [
                (self.square_size // 2, self.square_size // 4),
                (self.square_size * 3 // 4, self.square_size // 2),
                (self.square_size // 2, self.square_size * 3 // 4),
                (self.square_size // 4, self.square_size // 2)
            ])
        elif piece_type == 'king':
            pygame.draw.rect(surface, fill_color, (self.square_size // 4, self.square_size // 4, 
                                                  self.square_size // 2, self.square_size // 2))
            pygame.draw.line(surface, outline_color, 
                             (self.square_size // 2, self.square_size // 6),
                             (self.square_size // 2, self.square_size * 5 // 6), 4)
            pygame.draw.line(surface, outline_color, 
                             (self.square_size // 6, self.square_size // 2),
                             (self.square_size * 5 // 6, self.square_size // 2), 4)
        
        # Draw outline
        if piece_type != 'king':  # King already has cross
            if piece_type == 'pawn':
                pygame.draw.circle(surface, outline_color, (self.square_size // 2, self.square_size // 2), 
                                  self.square_size // 3, 2)
            elif piece_type == 'rook':
                pygame.draw.rect(surface, outline_color, (self.square_size // 4, self.square_size // 4, 
                                                         self.square_size // 2, self.square_size // 2), 2)
            else:
                # For other pieces, just use the first letter
                font = pygame.font.SysFont('Arial', self.square_size // 2)
                text = font.render(piece_type[0].upper(), True, outline_color)
                text_rect = text.get_rect(center=(self.square_size // 2, self.square_size // 2))
                surface.blit(text, text_rect)
        
        return surface
    
    def update_board(self, board_state):
        if not board_state:
            print("Warning: Received empty board state in update_board")
            return
        
        print(f"Updating board with state, dimensions: {len(board_state)}x{len(board_state[0]) if board_state else 0}")
        
        try:
            # Verify the board state format
            if len(board_state) != 8 or any(len(row) != 8 for row in board_state):
                print(f"Warning: Invalid board dimensions - expected 8x8, got {len(board_state)}x{len(board_state[0]) if board_state else 0}")
            
            # Copy the board state
            self.board = board_state
            print("Board updated successfully")
        except Exception as e:
            print(f"Error updating board: {e}")
            import traceback
            traceback.print_exc()
    
    def reset_board(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
    
    def draw_board(self):
        # Draw a nice wooden border around the board
        border_size = 30
        border_rect = pygame.Rect(
            self.board_position[0] - border_size,
            self.board_position[1] - border_size,
            self.board_size + border_size * 2,
            self.board_size + border_size * 2
        )
        
        # Draw wooden texture border
        pygame.draw.rect(self.screen, (120, 81, 45), border_rect)
        
        # Inner border highlight
        pygame.draw.rect(self.screen, (140, 95, 52), border_rect, 2)
        pygame.draw.rect(self.screen, (100, 65, 35), 
                        (border_rect.left + 4, border_rect.top + 4, 
                         border_rect.width - 8, border_rect.height - 8), 2)
        
        # Draw the chess board
        for row in range(8):
            for col in range(8):
                x = self.board_position[0] + col * self.square_size
                y = self.board_position[1] + row * self.square_size
                
                # Determine square color
                if (row + col) % 2 == 0:
                    color = self.colors['light_square']
                else:
                    color = self.colors['dark_square']
                
                # Draw square
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))
                
                # Draw piece if there is one
                piece = self.board[row][col]
                if piece:
                    try:
                        piece_color = piece.get('color')
                        piece_type = piece.get('type')
                        
                        if not piece_color or not piece_type:
                            print(f"Invalid piece at {row},{col}: {piece}")
                            continue
                        
                        # Draw the piece image
                        if piece_color in self.pieces_images and piece_type in self.pieces_images[piece_color]:
                            # Add slight shadow for pieces
                            shadow_surf = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
                            shadow_surf.fill((0, 0, 0, 0))  # Transparent
                            shadow_img = self.pieces_images[piece_color][piece_type].copy()
                            shadow_img.set_alpha(60)  # Semi-transparent for shadow
                            
                            # Offset shadow slightly
                            self.screen.blit(shadow_img, (x + 3, y + 3))
                            # Draw actual piece
                            self.screen.blit(self.pieces_images[piece_color][piece_type], (x, y))
                        else:
                            print(f"Missing image for {piece_color} {piece_type}")
                    except Exception as e:
                        print(f"Error drawing piece at {row},{col}: {e}")
                        print(f"Piece data: {piece}")
        
        # Draw coordinate labels with better styling
        font = pygame.font.SysFont('Arial', 16)
        
        # Draw file labels (a-h)
        for col in range(8):
            file_label = chr(ord('a') + col)
            
            # Top labels (in the border)
            text_top = font.render(file_label, True, (240, 230, 210))
            x_top = self.board_position[0] + col * self.square_size + self.square_size // 2 - text_top.get_width() // 2
            y_top = self.board_position[1] - 20
            self.screen.blit(text_top, (x_top, y_top))
            
            # Bottom labels (in the border)
            text_bottom = font.render(file_label, True, (240, 230, 210))
            x_bottom = self.board_position[0] + col * self.square_size + self.square_size // 2 - text_bottom.get_width() // 2
            y_bottom = self.board_position[1] + self.board_size + 5
            self.screen.blit(text_bottom, (x_bottom, y_bottom))
        
        # Draw rank labels (1-8)
        for row in range(8):
            rank_label = str(8 - row)
            
            # Left labels (in the border)
            text_left = font.render(rank_label, True, (240, 230, 210))
            x_left = self.board_position[0] - 20
            y_left = self.board_position[1] + row * self.square_size + self.square_size // 2 - text_left.get_height() // 2
            self.screen.blit(text_left, (x_left, y_left))
            
            # Right labels (in the border)
            text_right = font.render(rank_label, True, (240, 230, 210))
            x_right = self.board_position[0] + self.board_size + 5
            y_right = self.board_position[1] + row * self.square_size + self.square_size // 2 - text_right.get_height() // 2
            self.screen.blit(text_right, (x_right, y_right))
    
    def highlight_square(self, pos, color):
        row, col = pos
        x = self.board_position[0] + col * self.square_size
        y = self.board_position[1] + row * self.square_size
        
        # Create a semi-transparent surface
        highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        highlight.fill(color)
        self.screen.blit(highlight, (x, y))
    
    def handle_click(self, mouse_pos, player_color):
        # Check if the click is on the board
        x, y = mouse_pos
        board_x = x - self.board_position[0]
        board_y = y - self.board_position[1]
        
        if 0 <= board_x < self.board_size and 0 <= board_y < self.board_size:
            # Convert to board coordinates
            col = board_x // self.square_size
            row = board_y // self.square_size
            
            # Return the position and the piece at that position (if any)
            return (row, col), self.board[row][col]
        
        return None
    
    def get_valid_moves(self, from_pos, player_color):
        # For the client, we'll do a simplified check for valid moves
        # The server will do the full validation
        row, col = from_pos
        piece = self.board[row][col]
        
        if not piece or piece['color'] != player_color:
            return []
        
        valid_moves = []
        
        # For pawns
        if piece['type'] == 'pawn':
            # Get direction based on color
            direction = -1 if player_color == 'white' else 1
            
            # Move forward one square
            if 0 <= row + direction < 8:
                if not self.board[row + direction][col]:
                    valid_moves.append((row + direction, col))
                    
                    # Move forward two squares from starting position
                    starting_row = 6 if player_color == 'white' else 1
                    if row == starting_row and not self.board[row + 2 * direction][col]:
                        valid_moves.append((row + 2 * direction, col))
            
            # Capture diagonally
            for offset in [-1, 1]:
                if 0 <= row + direction < 8 and 0 <= col + offset < 8:
                    target = self.board[row + direction][col + offset]
                    if target and target['color'] != player_color:
                        valid_moves.append((row + direction, col + offset))
        
        # For knights
        elif piece['type'] == 'knight':
            knight_moves = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            
            for dr, dc in knight_moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if not target or target['color'] != player_color:
                        valid_moves.append((r, c))
        
        # For bishops, rooks, and queens
        elif piece['type'] in ['bishop', 'rook', 'queen']:
            # Define direction vectors
            directions = []
            
            if piece['type'] in ['bishop', 'queen']:
                # Diagonal directions
                directions.extend([(1, 1), (1, -1), (-1, 1), (-1, -1)])
            
            if piece['type'] in ['rook', 'queen']:
                # Horizontal and vertical directions
                directions.extend([(0, 1), (1, 0), (0, -1), (-1, 0)])
            
            for dr, dc in directions:
                r, c = row + dr, col + dc
                while 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if not target:
                        valid_moves.append((r, c))
                    elif target['color'] != player_color:
                        valid_moves.append((r, c))
                        break
                    else:
                        break
                    r += dr
                    c += dc
        
        # For kings
        elif piece['type'] == 'king':
            king_moves = [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 1),
                (1, -1), (1, 0), (1, 1)
            ]
            
            for dr, dc in king_moves:
                r, c = row + dr, col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    target = self.board[r][c]
                    if not target or target['color'] != player_color:
                        valid_moves.append((r, c))
            
            # Castling (simplified for client)
            if not piece.get('has_moved', False):
                # Kingside castling
                if (col + 3 < 8 and 
                    not self.board[row][col + 1] and 
                    not self.board[row][col + 2] and 
                    self.board[row][col + 3] and 
                    self.board[row][col + 3]['type'] == 'rook' and 
                    self.board[row][col + 3]['color'] == player_color and 
                    not self.board[row][col + 3].get('has_moved', False)):
                    valid_moves.append((row, col + 2))
                
                # Queenside castling
                if (col - 4 >= 0 and 
                    not self.board[row][col - 1] and 
                    not self.board[row][col - 2] and 
                    not self.board[row][col - 3] and 
                    self.board[row][col - 4] and 
                    self.board[row][col - 4]['type'] == 'rook' and 
                    self.board[row][col - 4]['color'] == player_color and 
                    not self.board[row][col - 4].get('has_moved', False)):
                    valid_moves.append((row, col - 2))
        
        return valid_moves 