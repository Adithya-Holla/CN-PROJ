class Piece:
    def __init__(self, color, piece_type):
        self.color = color  # 'white' or 'black'
        self.type = piece_type  # 'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
        self.has_moved = False
    
    def __str__(self):
        return f"{self.color[0]}{self.type[0]}"
    
    def to_dict(self):
        return {
            'color': self.color,
            'type': self.type,
            'has_moved': self.has_moved
        }


class ChessGame:
    def __init__(self):
        self.board = self.initialize_board()
        self.current_turn = 'white'
        self.move_history = []
        self.captured_pieces = {'white': [], 'black': []}
        self.game_over = False
        self.result = None
        self.winner = None
        self.check = {'white': False, 'black': False}
        self.en_passant_target = None
    
    def initialize_board(self):
        # Initialize an 8x8 empty board
        board = [[None for _ in range(8)] for _ in range(8)]
        
        # Set up pawns
        for col in range(8):
            board[1][col] = Piece('black', 'pawn')
            board[6][col] = Piece('white', 'pawn')
        
        # Set up rooks
        board[0][0] = Piece('black', 'rook')
        board[0][7] = Piece('black', 'rook')
        board[7][0] = Piece('white', 'rook')
        board[7][7] = Piece('white', 'rook')
        
        # Set up knights
        board[0][1] = Piece('black', 'knight')
        board[0][6] = Piece('black', 'knight')
        board[7][1] = Piece('white', 'knight')
        board[7][6] = Piece('white', 'knight')
        
        # Set up bishops
        board[0][2] = Piece('black', 'bishop')
        board[0][5] = Piece('black', 'bishop')
        board[7][2] = Piece('white', 'bishop')
        board[7][5] = Piece('white', 'bishop')
        
        # Set up queens
        board[0][3] = Piece('black', 'queen')
        board[7][3] = Piece('white', 'queen')
        
        # Set up kings
        board[0][4] = Piece('black', 'king')
        board[7][4] = Piece('white', 'king')
        
        return board
    
    def get_board_state(self):
        board_state = []
        for row in range(8):
            board_row = []
            for col in range(8):
                if self.board[row][col]:
                    board_row.append(self.board[row][col].to_dict())
                else:
                    board_row.append(None)
            board_state.append(board_row)
        return board_state
    
    def get_current_turn(self):
        return self.current_turn
    
    def get_game_status(self):
        return {
            'game_over': self.game_over,
            'result': self.result,
            'winner': self.winner,
            'check': self.check
        }
    
    def make_move(self, from_pos, to_pos):
        # Convert positions from chess notation to array indices if needed
        if isinstance(from_pos, str):
            from_pos = self.notation_to_indices(from_pos)
        if isinstance(to_pos, str):
            to_pos = self.notation_to_indices(to_pos)
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Check if positions are within bounds
        if not self._is_valid_position(from_row, from_col) or not self._is_valid_position(to_row, to_col):
            return {'valid': False, 'message': 'Position out of bounds'}
        
        # Check if there's a piece at the from position
        piece = self.board[from_row][from_col]
        if not piece:
            return {'valid': False, 'message': 'No piece at starting position'}
        
        # Check if it's the right color's turn
        if piece.color != self.current_turn:
            return {'valid': False, 'message': 'Not your turn'}
        
        # Check if the move is valid for this piece
        valid_move = self._is_valid_move(from_row, from_col, to_row, to_col)
        if not valid_move['valid']:
            return valid_move
        
        # Make the move
        captured_piece = self.board[to_row][to_col]
        
        # Special handling for en passant
        en_passant = False
        if piece.type == 'pawn' and to_col != from_col and not captured_piece:
            # This is an en passant capture
            en_passant = True
            if piece.color == 'white':
                captured_piece = self.board[to_row + 1][to_col]
                self.board[to_row + 1][to_col] = None
            else:
                captured_piece = self.board[to_row - 1][to_col]
                self.board[to_row - 1][to_col] = None
        
        # Record capture if there was one
        if captured_piece:
            self.captured_pieces[self.current_turn].append(captured_piece)
        
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        
        # Special handling for castling
        if piece.type == 'king' and abs(to_col - from_col) == 2:
            # This is castling - move the rook too
            if to_col > from_col:  # Kingside castling
                rook = self.board[from_row][7]
                self.board[from_row][7] = None
                self.board[from_row][5] = rook
                rook.has_moved = True
            else:  # Queenside castling
                rook = self.board[from_row][0]
                self.board[from_row][0] = None
                self.board[from_row][3] = rook
                rook.has_moved = True
        
        # Special handling for pawn promotion
        if piece.type == 'pawn' and (to_row == 0 or to_row == 7):
            # Promote pawn to queen by default (could be expanded to allow choice)
            self.board[to_row][to_col] = Piece(piece.color, 'queen')
        
        # Set en_passant_target if double pawn move
        self.en_passant_target = None
        if piece.type == 'pawn' and abs(from_row - to_row) == 2:
            self.en_passant_target = (to_row, to_col)
        
        # Mark piece as moved
        piece.has_moved = True
        
        # Record the move
        self.move_history.append({
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece.type,
            'color': piece.color,
            'captured': captured_piece.type if captured_piece else None,
            'en_passant': en_passant
        })
        
        # Change turn
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        
        # Check for check or checkmate
        self._update_check_status()
        if self._is_checkmate():
            self.game_over = True
            self.result = 'checkmate'
            self.winner = 'white' if self.current_turn == 'black' else 'black'
        elif self._is_stalemate():
            self.game_over = True
            self.result = 'stalemate'
            self.winner = None
        elif self._is_draw_by_insufficient_material():
            self.game_over = True
            self.result = 'insufficient_material'
            self.winner = None
        elif self._is_draw_by_fifty_move_rule():
            self.game_over = True
            self.result = 'fifty_move_rule'
            self.winner = None
        elif self._is_draw_by_threefold_repetition():
            self.game_over = True
            self.result = 'threefold_repetition'
            self.winner = None
        
        return {'valid': True}
    
    def _is_valid_position(self, row, col):
        return 0 <= row < 8 and 0 <= col < 8
    
    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Can't capture your own pieces
        if target and target.color == piece.color:
            return {'valid': False, 'message': 'Cannot capture your own piece'}
        
        # Different piece types have different movement rules
        if piece.type == 'pawn':
            return self._is_valid_pawn_move(from_row, from_col, to_row, to_col)
        elif piece.type == 'rook':
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif piece.type == 'knight':
            return self._is_valid_knight_move(from_row, from_col, to_row, to_col)
        elif piece.type == 'bishop':
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        elif piece.type == 'queen':
            return self._is_valid_queen_move(from_row, from_col, to_row, to_col)
        elif piece.type == 'king':
            return self._is_valid_king_move(from_row, from_col, to_row, to_col)
        
        return {'valid': False, 'message': 'Unknown piece type'}
    
    def _is_valid_pawn_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # Direction of movement depends on pawn color
        direction = -1 if piece.color == 'white' else 1
        
        # Regular move forward
        if from_col == to_col and not target:
            # One square forward
            if to_row == from_row + direction:
                return {'valid': True}
            
            # Two squares forward from starting position
            if not piece.has_moved and to_row == from_row + 2 * direction and not self.board[from_row + direction][from_col]:
                return {'valid': True}
        
        # Capture move
        if abs(from_col - to_col) == 1 and to_row == from_row + direction:
            # Regular capture
            if target:
                return {'valid': True}
            
            # En passant capture
            if self.en_passant_target and self.en_passant_target == (from_row, to_col):
                return {'valid': True}
        
        return {'valid': False, 'message': 'Invalid pawn move'}
    
    def _is_valid_rook_move(self, from_row, from_col, to_row, to_col):
        # Rooks move in straight lines (horizontally or vertically)
        if from_row != to_row and from_col != to_col:
            return {'valid': False, 'message': 'Rooks can only move horizontally or vertically'}
        
        # Check for pieces in the way
        if from_row == to_row:  # Horizontal move
            step = 1 if to_col > from_col else -1
            for col in range(from_col + step, to_col, step):
                if self.board[from_row][col]:
                    return {'valid': False, 'message': 'Cannot move through other pieces'}
        else:  # Vertical move
            step = 1 if to_row > from_row else -1
            for row in range(from_row + step, to_row, step):
                if self.board[row][from_col]:
                    return {'valid': False, 'message': 'Cannot move through other pieces'}
        
        return {'valid': True}
    
    def _is_valid_knight_move(self, from_row, from_col, to_row, to_col):
        # Knights move in an L-shape: 2 squares in one direction, then 1 square perpendicular
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            return {'valid': True}
        
        return {'valid': False, 'message': 'Invalid knight move'}
    
    def _is_valid_bishop_move(self, from_row, from_col, to_row, to_col):
        # Bishops move diagonally
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if row_diff != col_diff:
            return {'valid': False, 'message': 'Bishops can only move diagonally'}
        
        # Check for pieces in the way
        row_step = 1 if to_row > from_row else -1
        col_step = 1 if to_col > from_col else -1
        
        row, col = from_row + row_step, from_col + col_step
        while row != to_row and col != to_col:
            if self.board[row][col]:
                return {'valid': False, 'message': 'Cannot move through other pieces'}
            row += row_step
            col += col_step
        
        return {'valid': True}
    
    def _is_valid_queen_move(self, from_row, from_col, to_row, to_col):
        # Queens can move like rooks or bishops
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if from_row == to_row or from_col == to_col:
            # Rook-like move
            return self._is_valid_rook_move(from_row, from_col, to_row, to_col)
        elif row_diff == col_diff:
            # Bishop-like move
            return self._is_valid_bishop_move(from_row, from_col, to_row, to_col)
        
        return {'valid': False, 'message': 'Invalid queen move'}
    
    def _is_valid_king_move(self, from_row, from_col, to_row, to_col):
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        piece = self.board[from_row][from_col]
        
        # Normal king move (one square in any direction)
        if row_diff <= 1 and col_diff <= 1:
            # Check if the move would put the king in check
            temp_board = [row[:] for row in self.board]
            temp_board[to_row][to_col] = temp_board[from_row][from_col]
            temp_board[from_row][from_col] = None
            
            if self._is_square_attacked(to_row, to_col, piece.color, temp_board):
                return {'valid': False, 'message': 'Cannot move into check'}
            
            return {'valid': True}
        
        # Castling
        if not piece.has_moved and row_diff == 0 and col_diff == 2:
            # Check if the king is in check
            if self.check[piece.color]:
                return {'valid': False, 'message': 'Cannot castle while in check'}
            
            # Kingside castling
            if to_col > from_col:
                # Check if there are pieces between king and rook
                if any(self.board[from_row][c] for c in range(from_col + 1, 7)):
                    return {'valid': False, 'message': 'Cannot castle through pieces'}
                
                # Check if the rook has moved
                rook = self.board[from_row][7]
                if not rook or rook.type != 'rook' or rook.has_moved:
                    return {'valid': False, 'message': 'Cannot castle, rook has moved'}
                
                # Check if the king passes through check
                for col in range(from_col + 1, from_col + 3):
                    if self._is_square_attacked(from_row, col, piece.color):
                        return {'valid': False, 'message': 'Cannot castle through check'}
            
            # Queenside castling
            else:
                # Check if there are pieces between king and rook
                if any(self.board[from_row][c] for c in range(1, from_col)):
                    return {'valid': False, 'message': 'Cannot castle through pieces'}
                
                # Check if the rook has moved
                rook = self.board[from_row][0]
                if not rook or rook.type != 'rook' or rook.has_moved:
                    return {'valid': False, 'message': 'Cannot castle, rook has moved'}
                
                # Check if the king passes through check
                for col in range(from_col - 1, from_col - 3, -1):
                    if self._is_square_attacked(from_row, col, piece.color):
                        return {'valid': False, 'message': 'Cannot castle through check'}
            
            return {'valid': True}
        
        return {'valid': False, 'message': 'Invalid king move'}
    
    def _is_square_attacked(self, row, col, color, board=None):
        if board is None:
            board = self.board
        
        # Check for attacks from each direction and piece type
        opponent_color = 'black' if color == 'white' else 'white'
        
        # Check for pawn attacks
        pawn_direction = 1 if color == 'white' else -1
        for c_offset in [-1, 1]:
            r = row + pawn_direction
            c = col + c_offset
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece and piece.color == opponent_color and piece.type == 'pawn':
                    return True
        
        # Check for knight attacks
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for r_offset, c_offset in knight_moves:
            r = row + r_offset
            c = col + c_offset
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece and piece.color == opponent_color and piece.type == 'knight':
                    return True
        
        # Check for attacks along ranks and files (rook, queen)
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece:
                    if piece.color == opponent_color and (piece.type == 'rook' or piece.type == 'queen'):
                        return True
                    break
                r += dr
                c += dc
        
        # Check for attacks along diagonals (bishop, queen)
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece:
                    if piece.color == opponent_color and (piece.type == 'bishop' or piece.type == 'queen'):
                        return True
                    break
                r += dr
                c += dc
        
        # Check for king attacks (adjacent squares)
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for r_offset, c_offset in king_moves:
            r = row + r_offset
            c = col + c_offset
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                if piece and piece.color == opponent_color and piece.type == 'king':
                    return True
        
        return False
    
    def _update_check_status(self):
        # Find kings
        white_king_pos = None
        black_king_pos = None
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == 'king':
                    if piece.color == 'white':
                        white_king_pos = (row, col)
                    else:
                        black_king_pos = (row, col)
        
        # Check if kings are in check
        if white_king_pos:
            self.check['white'] = self._is_square_attacked(white_king_pos[0], white_king_pos[1], 'white')
        
        if black_king_pos:
            self.check['black'] = self._is_square_attacked(black_king_pos[0], black_king_pos[1], 'black')
    
    def _is_checkmate(self):
        # If the current player is not in check, it's not checkmate
        if not self.check[self.current_turn]:
            return False
        
        # Try all possible moves for all pieces of the current player
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece and piece.color == self.current_turn:
                    # Try all possible destinations
                    for to_row in range(8):
                        for to_col in range(8):
                            # Skip if same position
                            if from_row == to_row and from_col == to_col:
                                continue
                            
                            # Check if move is valid
                            valid_move = self._is_valid_move(from_row, from_col, to_row, to_col)
                            if valid_move['valid']:
                                # Try the move
                                temp_board = [row[:] for row in self.board]
                                temp_piece = temp_board[from_row][from_col]
                                temp_board[to_row][to_col] = temp_piece
                                temp_board[from_row][from_col] = None
                                
                                # Find king's position
                                king_pos = None
                                for r in range(8):
                                    for c in range(8):
                                        p = temp_board[r][c]
                                        if p and p.color == self.current_turn and p.type == 'king':
                                            king_pos = (r, c)
                                            break
                                    if king_pos:
                                        break
                                
                                # Check if king is still in check after move
                                if king_pos and not self._is_square_attacked(king_pos[0], king_pos[1], self.current_turn, temp_board):
                                    return False  # Found a move that gets out of check
        
        # No moves found that get out of check
        return True
    
    def _is_stalemate(self):
        # If the current player is in check, it's not stalemate
        if self.check[self.current_turn]:
            return False
        
        # Try all possible moves for all pieces of the current player
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece and piece.color == self.current_turn:
                    # Try all possible destinations
                    for to_row in range(8):
                        for to_col in range(8):
                            # Skip if same position
                            if from_row == to_row and from_col == to_col:
                                continue
                            
                            # Check if move is valid
                            valid_move = self._is_valid_move(from_row, from_col, to_row, to_col)
                            if valid_move['valid']:
                                return False  # Found a valid move
        
        # No valid moves found
        return True
    
    def _is_draw_by_insufficient_material(self):
        # Count pieces
        pieces = {'white': [], 'black': []}
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    pieces[piece.color].append(piece.type)
        
        # King vs King
        if len(pieces['white']) == 1 and len(pieces['black']) == 1:
            return True
        
        # King + Bishop/Knight vs King
        if (len(pieces['white']) == 1 and len(pieces['black']) == 2 and 
            ('bishop' in pieces['black'] or 'knight' in pieces['black'])):
            return True
        
        if (len(pieces['black']) == 1 and len(pieces['white']) == 2 and 
            ('bishop' in pieces['white'] or 'knight' in pieces['white'])):
            return True
        
        # King + Bishop vs King + Bishop (same color bishops)
        if (len(pieces['white']) == 2 and len(pieces['black']) == 2 and 
            'bishop' in pieces['white'] and 'bishop' in pieces['black']):
            # Would need to check bishop colors, but simplified for now
            return False
        
        return False
    
    def _is_draw_by_fifty_move_rule(self):
        # Check the last 50 moves for captures or pawn moves
        if len(self.move_history) < 50:
            return False
        
        for move in self.move_history[-50:]:
            if move['captured'] or move['piece'] == 'pawn':
                return False
        
        return True
    
    def _is_draw_by_threefold_repetition(self):
        # Simplified implementation - would need to track full board states
        return False
    
    def notation_to_indices(self, notation):
        if len(notation) != 2:
            raise ValueError("Invalid chess notation")
        
        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])
        
        return row, col
    
    def indices_to_notation(self, row, col):
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError("Invalid board indices")
        
        col_letter = chr(ord('a') + col)
        row_number = 8 - row
        
        return f"{col_letter}{row_number}" 