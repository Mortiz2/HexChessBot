import hexmath as hm
from hexmath import Hex, hex_neighbor, hex_distance
import pygame

ROOK_DIRECTIONS = range(6)
BISHOP_DIRECTIONS = range(6, 12)
KNIGHT_OFFSETS = [
    Hex(-2, -1, 3),
    Hex(-1, -2, 3),
    Hex(1, -3, 2),
    Hex(2, -3, 1),
    Hex(3, -2, -1),
    Hex(3, -1, -2),
    Hex(2, 1, -3),
    Hex(1, 2, -3),
    Hex(-1, 3, -2),
    Hex(-2, 3, -1),
    Hex(-3, 2, 1),
    Hex(-3, 1, 2),
]

BLACK_PAWN_START_HEXES = {
    (-5, 4, 1), (-4, 3, 1), (-3, 2, 1), (-2, 1, 1), (-1, 0, 1),
    (-1, -1, 2), (-1, -2, 3), (-1, -3, 4), (-1, -4, 5)
}

WHITE_PAWN_START_HEXES = {
    (1, 4, -5), (1, 3, -4), (1, 2, -3), (1, 1, -2), (1, 0, -1),
    (2, -1, -1), (3, -2, -1), (4, -3, -1), (5, -4, -1)
}

class Piece:
    def __init__(self, pos: Hex, color: str, img_name: str):
        self.pos = pos
        self.color = color
        self.name = "Piece"
        raw = pygame.image.load(f"assets/{color}-{img_name}.png")
        self.image = pygame.transform.smoothscale(raw, (46, 46))

    def pos_tuple(self):
        return (self.pos.q, self.pos.r, self.pos.s)

    def get_moves(self, board, last_move=None):
        return []

    def _is_on_board(self, board, target: Hex):
        return not hasattr(board, "hex_coords") or (target.q, target.r) in board.hex_coords

    def _get_sliding_moves(self, board, directions):
        moves = []

        for direction in directions:
            target = hex_neighbor(self.pos, direction)

            while self._is_on_board(board, target):
                key = (target.q, target.r, target.s)

                if key not in board.pieces:
                    moves.append(target)
                    target = hex_neighbor(target, direction)
                    continue

                if board.pieces[key].color != self.color:
                    moves.append(target)

                break

        return moves

    def _get_leaper_moves(self, board, offsets):
        moves = []

        for offset in offsets:
            target = hm.hex_add(self.pos, offset)

            if not self._is_on_board(board, target):
                continue

            key = (target.q, target.r, target.s)
            if key not in board.pieces or board.pieces[key].color != self.color:
                moves.append(target)

        return moves

class Pawn(Piece):
    def __init__(self, pos: Hex, color: str,):
        super().__init__(pos, color, "pawn")
        self.name = "Pawn"

    def is_on_start_hex(self):
        key = (self.pos.q, self.pos.r, self.pos.s)
        return key in WHITE_PAWN_START_HEXES if self.color == "white" else key in BLACK_PAWN_START_HEXES

    def get_moves(self, board, last_move=None):
        moves = []

        if self.color == "white":
            forward_dir = 0
            attack_dirs = [1, 5]
        else:
            forward_dir = 3
            attack_dirs = [2, 4]

        forward = hex_neighbor(self.pos, forward_dir)
        key_forward = (forward.q, forward.r, forward.s)

        if key_forward not in board.pieces:
            moves.append(forward)

            if self.is_on_start_hex():
                double_forward = hex_neighbor(forward, forward_dir)
                key_double = (double_forward.q, double_forward.r, double_forward.s)
                if key_double not in board.pieces:
                    moves.append(double_forward)

        for d in attack_dirs:
            target = hex_neighbor(self.pos, d)
            key = (target.q, target.r, target.s)

            if key in board.pieces:
                if board.pieces[key].color != self.color:
                    moves.append(target)

        if last_move and last_move.piece.name == "Pawn" and last_move.piece.color != self.color:
            from_pos = last_move.from_pos
            to_pos = last_move.to_pos

            if hex_distance(from_pos, to_pos) == 2:
                # enemy pawn must have landed directly beside us in an attack direction
                adjacent_in_attack = any(
                    hex_neighbor(self.pos, d) == to_pos for d in attack_dirs
                )
                if adjacent_in_attack:
                    # target is the hex the enemy pawn passed over (one step in our forward dir)
                    en_passant_hex = hex_neighbor(to_pos, forward_dir)
                    key_en_passant = (en_passant_hex.q, en_passant_hex.r, en_passant_hex.s)
                    if key_en_passant not in board.pieces:
                        moves.append(en_passant_hex)

        return moves

class King(Piece):
    def __init__(self, pos: Hex, color: str, ):
        super().__init__(pos, color, "king")
        self.name = "King"

    def get_moves(self, board, last_move=None):
        moves = []

        for direction in range(12):
            target = hex_neighbor(self.pos, direction)

            if not self._is_on_board(board, target):
                continue

            key = (target.q, target.r, target.s)

            if key not in board.pieces:
                moves.append(target)
                continue

            if board.pieces[key].color != self.color:
                moves.append(target)

        return moves


class Rook(Piece):
    def __init__(self, pos: Hex, color: str):
        super().__init__(pos, color, "rook")
        self.name = "Rook"

    def get_moves(self, board, last_move=None):
        return self._get_sliding_moves(board, ROOK_DIRECTIONS)


class Bishop(Piece):
    def __init__(self, pos: Hex, color: str):
        super().__init__(pos, color, "bishop")
        self.name = "Bishop"

    def get_moves(self, board, last_move=None):
        return self._get_sliding_moves(board, BISHOP_DIRECTIONS)


class Knight(Piece):
    def __init__(self, pos: Hex, color: str):
        super().__init__(pos, color, "knight")
        self.name = "Knight"

    def get_moves(self, board, last_move=None):
        return self._get_leaper_moves(board, KNIGHT_OFFSETS)


class Queen(Piece):
    def __init__(self, pos: Hex, color: str):
        super().__init__(pos, color, "queen")
        self.name = "Queen"

    def get_moves(self, board, last_move=None):
        return self._get_sliding_moves(board, range(12))


class Move:
    """Record of a completed move, used for en passant detection."""
    def __init__(self, piece, from_pos, to_pos):
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos


def create_piece(pos: Hex, color: str, piece_type: str):
    piece_classes = {
        "bishop": Bishop,
        "king": King,
        "knight": Knight,
        "pawn": Pawn,
        "queen": Queen,
        "rook": Rook,
    }

    piece_class = piece_classes.get(piece_type)
    if piece_class:
        return piece_class(pos, color)

    piece = Piece(pos, color, piece_type)
    piece.name = piece_type.capitalize()
    return piece