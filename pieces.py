import hexmath as hm
from hexmath import Hex, hex_neighbor, hex_distance
import pygame

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

        path = f"assets/{color}-{img_name}.png"

    def pos_tuple(self):
        return (self.pos.q, self.pos.r, self.pos.s)

    def get_moves(self, board):
        return []

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
            forward_dir = 2
            attack_dirs = [1, 3]
        else:
            forward_dir = 5
            attack_dirs = [4, 0]

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

            if key not in board.pieces:
                if board.pieces[key].color != self.color:
                    moves.append(target)

        if last_move and last_move.piece.name == "Pawn":
            moved_pawn = last_move.piece
            from_pos = last_move.from_pos
            to_pos = last_move.to_pos

            if abs(from_pos.q - to_pos.q) + abs(from_pos.r - to_pos.r) + abs(from_pos.s - to_pos.s) == 2:
                if hex_distance(self.pos, to_pos) == 1:
                    en_passant_hex = Hex(
                        to_pos.q,
                        to_pos.r,
                        to_pos.s - 1 if self.color == "white" else to_pos.s + 1
                    )
                    key_en_passant = (en_passant_hex.q, en_passant_hex.r, en_passant_hex.s)
                    if key_en_passant not in board.pieces:
                        moves.append(en_passant_hex)

        return moves
#
# class King(Piece):
#     def __init__(self, pos: Hex, color: str, ):
#         super().__init__(pos, color, "king")
#         self.name = "King"
#
#
