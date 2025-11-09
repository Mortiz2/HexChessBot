import hexmath as hm
from hexmath import Hex, hex_neighbor
import pygame


class Piece:
    def __init__(self, pos, color, image_path, alive=True):
        self.pos = pos
        self.color = color
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (40, 40))
        self.alive = alive

    def pos_tuple(self):
        return (self.pos.q, self.pos.r, self.pos.s)

class Pawn(Piece):
    def __init__(self, pos, color):
        super().__init__(pos, color)
        self.name = "Pawn"
        self.image = pygame.image.load("assets/pawn-w.svg").convert_alpha()

        def get_moves(self, board):
            moves = []

            direction = 2 if self.color == "white" else 5

            forward_hex = hex_neighbor(self.pos, direction)

            if forward_hex not in board.pieces:
                moves.append(forward_hex)

            if self.color == "white":
                attack_dirs = [1, 3]
            else:
                attack_dirs = [4, 0]

            for d in attack_dirs:
                target = hex_neighbor(self.pos, d)
                if target in board.pieces and board.pieces[target].color != self.color:
                    moves.append(target)

            return moves



if __name__ == "__main__":
    import hexmath as hm

    p = Pawn(hm.Hex(0, 0, 0), "white")
    print(p.name, p.pos, p.color, p.alive)