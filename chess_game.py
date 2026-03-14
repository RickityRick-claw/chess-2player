#!/usr/bin/env python3
"""
Python Chess Game with AI
Built with pygame and python-chess
"""

import chess
import pygame
import sys
import random
from datetime import datetime

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 640, 720  # Extra space for status
SQ_SIZE = WIDTH // 8
FPS = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BROWN = (238, 238, 213)
DARK_BROWN = (118, 150, 86)
HIGHLIGHT = (255, 255, 0, 150)
LEGAL_MOVE = (100, 200, 100, 150)
CHECK_RED = (255, 80, 80)

# Piece symbols (Unicode)
PIECE_SYMBOLS = {
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'
}

# Fonts
pygame.font.init()
PIECE_font = pygame.font.SysFont('segoe ui symbol', int(SQ_SIZE * 0.8))
STATUS_font = pygame.font.SysFont('arial', 20)
TITLE_font = pygame.font.SysFont('arial', 28, bold=True)

class ChessGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chess - Python Edition")
        self.clock = pygame.time.Clock()
        
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.mode = 'menu'  # menu, pvp, pvc
        self.turn = 'white'  # white or black for pvc
        self.message = ""
        self.message_timer = 0
    
    def draw_board(self):
        """Draw the chess board"""
        for r in range(8):
            for c in range(8):
                color = LIGHT_BROWN if (r + c) % 2 == 0 else DARK_BROWN
                pygame.draw.rect(self.screen, color, 
                               (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
                # Highlight selected square
                if self.selected_square == (r, c):
                    s = pygame.Surface((SQ_SIZE, SQ_SIZE))
                    s.set_alpha(150)
                    s.fill((255, 255, 0))
                    self.screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
                
                # Highlight king in check
                if self.board.is_check():
                    king_square = self.board.king(chess.WHITE) if self.board.turn == chess.WHITE else self.board.king(chess.BLACK)
                    if king_square == chess.square(c, 7-r):
                        s = pygame.Surface((SQ_SIZE, SQ_SIZE))
                        s.set_alpha(100)
                        s.fill(CHECK_RED)
                        self.screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
                
                # Highlight legal moves
                if self.selected_square is not None:
                    from_sq = chess.square(self.selected_square[1], 7 - self.selected_square[0])
                    to_sq = chess.square(c, 7 - r)
                    if to_sq in self.valid_moves:
                        s = pygame.Surface((SQ_SIZE//3, SQ_SIZE//3))
                        s.set_alpha(150)
                        s.fill((0, 200, 0))
                        self.screen.blit(s, (c * SQ_SIZE + SQ_SIZE//3, r * SQ_SIZE + SQ_SIZE//3))
        
        # Draw pieces
        for r in range(8):
            for c in range(8):
                sq = chess.square(c, 7 - r)
                piece = self.board.piece_at(sq)
                if piece:
                    symbol = PIECE_SYMBOLS[piece.symbol()]
                    # Choose color based on piece color
                    text_color = BLACK if piece.color == chess.WHITE else BLACK
                    # For better visibility on dark squares, use white for dark pieces
                    if (r + c) % 2 == 1 and piece.color == chess.BLACK:
                        text_color = WHITE
                    elif (r + c) % 2 == 0 and piece.color == chess.WHITE:
                        text_color = BLACK
                    else:
                        text_color = WHITE if piece.color == chess.BLACK else BLACK
                    
                    text = PIECE_font.render(symbol, True, text_color)
                    text_rect = text.get_rect(center=(c * SQ_SIZE + SQ_SIZE//2, r * SQ_SIZE + SQ_SIZE//2))
                    self.screen.blit(text, text_rect)
    
    def draw_status(self):
        """Draw game status"""
        # Status bar background
        pygame.draw.rect(self.screen, (30, 30, 50), (0, 8*SQ_SIZE, WIDTH, 80))
        
        # Game status
        if self.board.is_checkmate():
            status = f"Checkmate! {'White' if self.board.turn == chess.BLACK else 'Black'} wins!"
            color = (255, 100, 100)
        elif self.board.is_stalemate():
            status = "Stalemate - Draw!"
            color = (255, 255, 100)
        elif self.board.is_check():
            status = f"{'White' if self.board.turn == chess.WHITE else 'Black'}'s turn - CHECK!"
            color = (255, 100, 100)
        elif self.game_over:
            status = self.message
            color = (255, 255, 100)
        else:
            status = f"{'White' if self.board.turn == chess.WHITE else 'Black'}'s turn"
            color = (255, 255, 255)
        
        if self.mode == 'pvc' and self.board.turn == chess.BLACK and not self.game_over:
            status += " (AI thinking...)"
        
        text = STATUS_font.render(status, True, color)
        self.screen.blit(text, (20, 8*SQ_SIZE + 25))
        
        # Mode indicator
        mode_text = STATUS_font.render(f"Mode: {self.mode.upper()}", True, (180, 180, 180))
        self.screen.blit(mode_text, (WIDTH - 150, 8*SQ_SIZE + 25))
        
        # Back button
        back_rect = pygame.Rect(WIDTH - 80, 8*SQ_SIZE + 50, 60, 25)
        pygame.draw.rect(self.screen, (200, 80, 80), back_rect, border_radius=5)
        back_text = STATUS_font.render("Menu", True, WHITE)
        self.screen.blit(back_text, (back_rect.x + 12, back_rect.y + 3))
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill((30, 30, 50))
        
        # Title
        title = TITLE_font.render("Chess", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - 60, 150))
        
        subtitle = STATUS_font.render("Python Edition", True, (180, 180, 180))
        self.screen.blit(subtitle, (WIDTH//2 - 70, 190))
        
        # Buttons
        btn_width, btn_height = 200, 50
        buttons = [
            ("vs Player (PVP)", (WIDTH//2 - btn_width//2, 280)),
            ("vs Computer (PVC)", (WIDTH//2 - btn_width//2, 360)),
            ("Quit", (WIDTH//2 - btn_width//2, 440)),
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for text, (x, y) in buttons:
            rect = pygame.Rect(x, y, btn_width, btn_height)
            color = (80, 120, 200) if rect.collidepoint(mouse_pos) else (60, 90, 160)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            
            btn_text = STATUS_font.render(text, True, WHITE)
            self.screen.blit(btn_text, (x + btn_width//2 - btn_text.get_width()//2, y + 15))
        
        return buttons
    
    def get_square(self, pos):
        """Convert pixel position to square"""
        x, y = pos
        if y >= 8 * SQ_SIZE:
            return None
        return (7 - y // SQ_SIZE, x // SQ_SIZE)
    
    def get_legal_moves(self, square):
        """Get legal moves for a square"""
        if square is None:
            return []
        sq = chess.square(square[1], 7 - square[0])
        return [chess.square_to_square(m.to_square) for m in self.board.legal_moves if m.from_square == sq]
    
    def make_move(self, from_sq, to_sq):
        """Make a move"""
        from_chess = chess.square(from_sq[1], 7 - from_sq[0])
        to_chess = chess.square(to_sq[1], 7 - to_sq[0])
        
        # Check for promotion
        move = None
        for m in self.board.legal_moves:
            if m.from_square == from_chess and m.to_square == to_chess:
                move = m
                # Auto-promote to queen
                if chess.square_rank(to_chess) in [0, 7] and self.board.piece_at(from_chess).piece_type == chess.PAWN:
                    move = chess.Move(from_chess, to_chess, promotion=chess.QUEEN)
                break
        
        if move and move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False
    
    def ai_move(self):
        """Simple AI - Random but prefers captures and checks"""
        moves = list(self.board.legal_moves)
        if not moves:
            return
        
        # Score moves
        scored_moves = []
        for move in moves:
            score = 0
            # Prefer captures
            if self.board.is_capture(move):
                score += 10
                captured = self.board.piece_at(move.to_square)
                if captured:
                    piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 100}
                    score += piece_values.get(captured.symbol().lower(), 0)
            # Prefer checks
            temp_board = self.board.copy()
            temp_board.push(move)
            if temp_board.is_check():
                score += 20
            # Prefer central control
            to_sq = move.to_square
            if chess.square_file(to_sq) in [3, 4] and chess.square_rank(to_sq) in [3, 4]:
                score += 2
            
            scored_moves.append((score + random.random() * 5, move))
        
        # Sort by score and pick best
        scored_moves.sort(reverse=True)
        self.board.push(scored_moves[0][1])
    
    def handle_click(self, pos):
        """Handle mouse click"""
        if self.mode == 'menu':
            buttons = [
                ((WIDTH//2 - 100, 280), 'pvp'),
                ((WIDTH//2 - 100, 360), 'pvc'),
                ((WIDTH//2 - 100, 440), 'quit'),
            ]
            for (x, y), mode in buttons:
                if x <= pos[0] <= x + 200 and y <= pos[1] <= y + 50:
                    if mode == 'quit':
                        pygame.quit()
                        sys.exit()
                    self.mode = mode
                    self.board.reset()
                    self.game_over = False
                    self.selected_square = None
                    self.valid_moves = []
            return
        
        # Game mode - check for back button
        if pos[1] > 8 * SQ_SIZE:
            if WIDTH - 80 <= pos[0] <= WIDTH - 20:
                self.mode = 'menu'
                self.board.reset()
            return
        
        square = self.get_square(pos)
        if square is None:
            return
        
        # PVC - prevent clicking during AI turn
        if self.mode == 'pvc' and self.board.turn == chess.BLACK and not self.game_over:
            return
        
        if self.selected_square is None:
            # First click - select piece
            sq = chess.square(square[1], 7 - square[0])
            piece = self.board.piece_at(sq)
            if piece and ((self.board.turn == chess.WHITE and piece.color == chess.WHITE) or
                          (self.board.turn == chess.BLACK and piece.color == chess.BLACK)):
                self.selected_square = square
                self.valid_moves = self.get_legal_moves(square)
        else:
            # Second click - try to move
            if square == self.selected_square:
                # Deselect
                self.selected_square = None
                self.valid_moves = []
            elif square in [(7 - chess.square_rank(m), chess.square_file(m)) for m in self.valid_moves]:
                # Make move
                if self.make_move(self.selected_square, square):
                    self.selected_square = None
                    self.valid_moves = []
                    
                    # Check game over
                    if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient_material():
                        self.game_over = True
                    
                    # AI move in PVC mode
                    if self.mode == 'pvc' and not self.game_over and self.board.turn == chess.BLACK:
                        pygame.time.wait(300)  # Small delay for better UX
                        self.ai_move()
                        if self.board.is_checkmate() or self.board.is_stalemate() or self.board.is_insufficient_material():
                            self.game_over = True
            else:
                # Clicked different square - try to select new piece
                sq = chess.square(square[1], 7 - square[0])
                piece = self.board.piece_at(sq)
                if piece and ((self.board.turn == chess.WHITE and piece.color == chess.WHITE) or
                              (self.board.turn == chess.BLACK and piece.color == chess.BLACK)):
                    self.selected_square = square
                    self.valid_moves = self.get_legal_moves(square)
                else:
                    self.selected_square = None
                    self.valid_moves = []
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.handle_click(event.pos)
            
            # Draw
            if self.mode == 'menu':
                self.draw_menu()
            else:
                self.draw_board()
                self.draw_status()
            
            pygame.display.flip()
        
        pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()