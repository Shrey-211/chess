import chess
import chess.pgn
import requests
import pygame
import logging
from datetime import datetime
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Pygame Setup
WIDTH, HEIGHT = 480, 480
SQUARE_SIZE = WIDTH // 8
WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (124, 252, 0, 128)  # Semi-transparent green for move highlights

def download_chess_pieces():
    """Download chess piece images from Lichess."""
    pieces = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
    colors = ['white', 'black']
    base_url = "https://lichess1.org/assets/piece/cburnett/"
    
    # Ensure assets directory exists
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
    
    for color in colors:
        for piece in pieces:
            filename = f"{color}_{piece}.png"
            filepath = os.path.join(assets_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(filepath):
                continue
                
            # Construct URL (Lichess uses first letter of piece name, capitalized for white)
            piece_char = piece[0].upper() if color == 'white' else piece[0].lower()
            url = f"{base_url}{piece_char}.svg"
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                logging.info(f"Downloaded {filename}")
                
            except requests.RequestException as e:
                logging.error(f"Failed to download {filename}: {str(e)}")
                raise

class ChessGame:
    """Main game controller class with error handling."""
    
    def __init__(self):
        # Clear previous games
        self._clear_games_folder()
        
        self.board = chess.Board()
        self.game = chess.pgn.Game()
        self.game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        self.game.headers["White"] = "Player"
        self.game.headers["Black"] = "AI"
        self.node = self.game
        self.selected_square = None
        self.dragging = False
        self.drag_piece = None
        self.drag_pos = None
        self.legal_moves = set()
        
        # Download pieces if needed
        download_chess_pieces()
        
        self._init_pygame()
        self._load_pieces()

    def _init_pygame(self):
        """Initialize Pygame resources with error handling."""
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
            # Create a transparent surface for highlights
            self.highlight_surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            pygame.draw.rect(self.highlight_surface, HIGHLIGHT, (0, 0, SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error as e:
            logging.critical(f"Pygame initialization failed: {str(e)}")
            raise

    def _load_pieces(self):
        """Load chess piece images."""
        self.pieces = {}
        piece_size = int(SQUARE_SIZE * 0.8)  # Slightly smaller than square size
        
        try:
            # Ensure assets directory exists
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)
            
            # Map of piece symbols to their image filenames
            piece_files = {
                'p': 'black_pawn.png', 'r': 'black_rook.png', 'n': 'black_knight.png',
                'b': 'black_bishop.png', 'q': 'black_queen.png', 'k': 'black_king.png',
                'P': 'white_pawn.png', 'R': 'white_rook.png', 'N': 'white_knight.png',
                'B': 'white_bishop.png', 'Q': 'white_queen.png', 'K': 'white_king.png'
            }
            
            # Load and scale each piece image
            for symbol, filename in piece_files.items():
                filepath = os.path.join(assets_dir, filename)
                if os.path.exists(filepath):
                    image = pygame.image.load(filepath)
                    self.pieces[symbol] = pygame.transform.smoothscale(image, (piece_size, piece_size))
                else:
                    logging.error(f"Missing piece image: {filepath}")
                    raise FileNotFoundError(f"Missing piece image: {filepath}")
                    
        except (pygame.error, FileNotFoundError) as e:
            logging.critical(f"Failed to load piece images: {str(e)}")
            raise

    def square_to_pos(self, square):
        """Convert chess square (0-63) to screen position."""
        file_idx = chess.square_file(square)
        rank_idx = 7 - chess.square_rank(square)
        return (file_idx * SQUARE_SIZE, rank_idx * SQUARE_SIZE)

    def pos_to_square(self, pos):
        """Convert screen position to chess square (0-63)."""
        x, y = pos
        file_idx = x // SQUARE_SIZE
        rank_idx = 7 - (y // SQUARE_SIZE)
        if 0 <= file_idx <= 7 and 0 <= rank_idx <= 7:
            return chess.square(file_idx, rank_idx)
        return None

    def draw_board(self):
        """Draw the chessboard with move highlights."""
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else BROWN
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        # Highlight legal moves
        if self.selected_square is not None:
            for move in self.legal_moves:
                if move.from_square == self.selected_square:
                    pos = self.square_to_pos(move.to_square)
                    self.screen.blit(self.highlight_surface, pos)

    def draw_pieces(self):
        """Render chess pieces on the board using images."""
        # Draw all pieces except the dragged one
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                # Convert piece to character (e.g., 'P' for white pawn, 'p' for black pawn)
                piece_char = piece.symbol()
                
                if not (self.dragging and square == self.selected_square):
                    piece_img = self.pieces[piece_char]
                    # Get the file (column) and rank (row) from the square
                    file_idx = chess.square_file(square)
                    rank_idx = 7 - chess.square_rank(square)  # Flip rank since we draw from top
                    
                    # Center the piece in the square
                    x = file_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_img.get_width()) // 2
                    y = rank_idx * SQUARE_SIZE + (SQUARE_SIZE - piece_img.get_height()) // 2
                    self.screen.blit(piece_img, (x, y))
        
        # Draw dragged piece last
        if self.dragging and self.drag_piece in self.pieces:
            piece_img = self.pieces[self.drag_piece]
            # Center the piece on the mouse cursor
            x = self.drag_pos[0] - piece_img.get_width() // 2
            y = self.drag_pos[1] - piece_img.get_height() // 2
            self.screen.blit(piece_img, (x, y))

    def handle_click(self, pos):
        """Handle mouse click events for piece selection."""
        square = self.pos_to_square(pos)
        if square is None:
            return
        
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == (self.board.turn == chess.WHITE):
                self.selected_square = square
                self.legal_moves = set(move for move in self.board.legal_moves 
                                    if move.from_square == square)
                self.drag_piece = str(piece)
                self.dragging = True
                self.drag_pos = pygame.mouse.get_pos()
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.legal_moves:
                self.make_move(move)
            self.selected_square = None
            self.legal_moves.clear()
            self.dragging = False
            self.drag_piece = None

    def make_move(self, move):
        """Make a move on the board and update game state."""
        self.board.push(move)
        self.node = self.node.add_variation(move)
        self.save_game()  # Auto-save after each move

    def save_game(self):
        """Save the game in PGN format."""
        try:
            os.makedirs("games", exist_ok=True)
            filename = f"games/game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
            with open(filename, "w") as f:
                print(self.game, file=f, end="\n\n")
            logging.info(f"Game saved to {filename}")
        except IOError as e:
            logging.error(f"Failed to save game: {str(e)}")

    @staticmethod
    def get_ai_move(fen: str) -> str | None:
        """Get AI move from LLM API with error handling and move validation."""
        url = "http://localhost:11434/api/generate"
        headers = {"Content-Type": "application/json"}
        
        # Create a temporary board to get legal moves
        board = chess.Board(fen)
        legal_moves = [move.uci() for move in board.legal_moves]
        
        # If no legal moves, return None
        if not legal_moves:
            return None
            
        prompt = (
            f"Current chess position FEN: {fen}\n\n"
            f"Legal moves in UCI format: {', '.join(legal_moves)}\n\n"
            "You are a chess engine. Choose one move from the legal moves list above.\n"
            "Rules:\n"
            "1. Respond ONLY with a single UCI move from the legal moves list\n"
            "2. Do not add any explanation or analysis\n"
            "3. The move must be exactly as shown in the legal moves list\n"
            "4. Do not make up moves - use only moves from the provided list\n\n"
            "Choose one move:"
        )
        
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload),
                timeout=10
            )
            if response.status_code != 200:
                logging.error(f"API request failed with status code: {response.status_code}")
                return None
                
            # Get the response and clean it
            move = response.json().get("response", "").strip().lower()
            # Extract just the first word (in case of extra text)
            move = move.split()[0]
            
            logging.info(f"Raw AI response: {move}")
            
            # Validate that the move is in the legal moves list
            if move not in legal_moves:
                logging.error(f"AI suggested move {move} is not in legal moves list: {legal_moves}")
                return None
                
            return move
            
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            logging.error(f"AI move request failed: {str(e)}")
            return None

    def _clear_games_folder(self):
        """Clear all PGN files from the games folder."""
        try:
            games_dir = os.path.join(os.path.dirname(__file__), "games")
            if os.path.exists(games_dir):
                for file in os.listdir(games_dir):
                    if file.endswith('.pgn'):
                        file_path = os.path.join(games_dir, file)
                        try:
                            os.remove(file_path)
                            logging.info(f"Removed previous game file: {file}")
                        except OSError as e:
                            logging.error(f"Error removing file {file}: {str(e)}")
        except Exception as e:
            logging.error(f"Error clearing games folder: {str(e)}")

    def _main_loop(self):
        """Main game loop with GUI."""
        pygame.display.set_caption("Chess Game")
        clock = pygame.time.Clock()
        running = True
        
        logging.info('Starting the game...')
        while running:
            self.screen.fill((0, 0, 0))
            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.dragging:
                        self.handle_click(event.pos)
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.drag_pos = event.pos
            
            if self.board.turn == chess.BLACK and not self.board.is_game_over():
                ai_move = self.get_ai_move(self.board.fen())
                print("Board FEN:", self.board.fen())
                print("Legal moves:", self.board.legal_moves)
                print("Ai suggested move:", ai_move)
                if ai_move and chess.Move.from_uci(ai_move) in self.board.legal_moves:
                    self.make_move(chess.Move.from_uci(ai_move))
                else:
                    logging.error("AI returned an invalid move. Ending game.")
                    break
            
            if self.board.is_game_over():
                self.save_game()
                logging.info(f"Game Over. Result: {self.board.result()}")
                running = False
            
            clock.tick(60)  # Limit to 60 FPS

    def run(self):
        """Main game loop with proper cleanup."""
        try:
            self._main_loop()
        finally:
            pygame.quit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
