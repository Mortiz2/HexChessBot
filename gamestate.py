from pieces import Piece

class GameState:
    def __init__(self):
        self.turn = "white"
        self.pieces = []
        self.last_move = None
        self.setup_initial_position()

    def setup_initial_position(self):
        self.pieces = [
    (-5, 0, 5, "bishop", "black"),
    (-4, 0, 4, "bishop", "black"),
    (-3, 0, 3, "bishop", "black"),
    (-4, -1, 5, "king", "black"),
    (-5, 1, 4, "queen", "black"),
    (-5, 2, 3, "knight", "black"),
    (-3, -2, 5, "knight", "black"),
    (-5, 3, 2, "rook", "black"),
    (-2, -3, 5, "rook", "black"),
    (-5, 4, 1, "pawn", "black"),
    (-4, 3, 1, "pawn", "black"),
    (-3, 2, 1, "pawn", "black"),
    (-2, 1, 1, "pawn", "black"),
    (-1, 0, 1, "pawn", "black"),
    (-1, -1, 2, "pawn", "black"),
    (-1, -2, 3, "pawn", "black"),
    (-1, -3, 4, "pawn", "black"),
    (-1, -4, 5, "pawn", "black"),

    (5, 0, -5, "bishop", "white"),
    (4, 0, -4, "bishop", "white"),
    (3, 0, -3, "bishop", "white"),
    (4, 1, -5, "queen", "white"),
    (5, -1, -4, "king", "white"),
    (5, -2, -3, "knight", "white"),
    (3, 2, -5, "knight", "white"),
    (2, 3, -5, "rook", "white"),
    (5, -3, -2, "rook", "white"),
    (1, 4, -5, "pawn", "white"),
    (1, 3, -4, "pawn", "white"),
    (1, 2, -3, "pawn", "white"),
    (1, 1, -2, "pawn", "white"),
    (1, 0, -1, "pawn", "white"),
    (2, -1, -1, "pawn", "white"),
    (3, -2, -1, "pawn", "white"),
    (4, -3, -1, "pawn", "white"),
    (5, -4, -1, "pawn", "white"),
]

def get_piece(self, q, r):
    return self.pieces.get((q, r))

def move_piece(self, from_hex, to_hex):
    piece = self.pieces.get(from_hex)
    if not piece:
        return False

    if to_hex in self.pieces:
        del self.pieces[to_hex]

    self.pieces[to_hex] = piece
    del self.pieces[from_hex]
    piece.q, piece.r = to_hex

    self.turn = "black" if self.turn == "white" else "white"
    return True

def is_occupied(self, q, r):
    return (q, r) in self.pieces