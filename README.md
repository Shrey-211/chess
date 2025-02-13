# Chess Game with AI

A Python-based chess game implementation featuring a graphical interface and AI opponent. The game uses the Pygame library for the GUI and integrates with chess engines for AI moves.

## Features

- Interactive graphical chess board
- Drag-and-drop piece movement
- Legal move validation
- AI opponent
- Game state saving in PGN format
- Automatic piece image downloads from Lichess
- Move highlighting
- Game history tracking

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Chess.git
cd Chess
```

2. Install the required dependencies:
```bash
pip install pygame python-chess requests
```

## Project Structure

```
Chess/
├── src/                 # Source code files
│   ├── chess_backend.py # Main game logic
│   └── assets/         # Chess piece images
├── games/              # Saved game files in PGN format
├── config/            # Configuration files
└── README.md          # This file
```

## Usage

1. Run the game:
```bash
python src/chess_backend.py
```

2. Playing the Game:
   - Click and drag pieces to make moves
   - Legal moves will be highlighted in green
   - The AI will automatically respond to your moves
   - Games are automatically saved in the `games` folder

## Game Controls

- Left-click: Select a piece
- Drag and Drop: Move pieces
- The game automatically validates moves and prevents illegal moves
- The AI opponent will automatically make its move after you complete yours

## Features in Detail

### Board Visualization
- 8x8 chess board with alternating colors
- Piece visualization using standard chess pieces
- Move highlighting for legal moves
- Visual feedback during piece dragging

### Game Mechanics
- Full implementation of chess rules
- Legal move validation
- Support for all special moves (castling, en passant, pawn promotion)
- Game state tracking
- PGN format game saving

### AI Integration
- AI opponent for single-player games
- Automatic move generation
- Strategic gameplay

## Saving Games

Games are automatically saved in PGN format in the `games` directory. Each game file includes:
- Player information
- Date and time
- Complete move history
- Game result

## Contributing

Feel free to fork the repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.