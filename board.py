import pygame
import math
import hexmath

class Board:
    def __init__(self, radius=5, hex_size=30, colors=None, center_offset=(400, 300), rotation=90, game_state=None):
        self.radius = radius
        self.hex_size = hex_size
        self.colors = colors or [(209, 150, 88), (228,197,165), (171, 117, 60)]
        self.center_offset = center_offset
        self.rotation = rotation
        self.game_state = game_state

        self.hex_coords = set(self.generate_hex_map())
        self.map_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        self.draw_map()

        self.pieces = {}

    # Convert hex grid coordinates (q, r) to pixel coordinates
    def hex_to_pixel(self, q, r):
        x = self.hex_size * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
        y = self.hex_size * (3/2 * r)
        return (x + self.center_offset[0], y + self.center_offset[1])

    def pixel_to_hex(self, x, y):
        """Convert a screen pixel position to the nearest hex cube coordinate."""
        if self.rotation != 0:
            x, y = self.rotate_point(x, y, -self.rotation)
        cx, cy = self.center_offset
        dx = (x - cx) / self.hex_size
        dy = (y - cy) / self.hex_size
        q_f = dx / math.sqrt(3) - dy / 3
        r_f = dy * 2 / 3
        s_f = -q_f - r_f
        return hexmath.cube_round(q_f, r_f, s_f)

    # Draw a single hex tile on the given surface
    def draw_hex(self, surface, q, r, color):
        cx, cy = self.hex_to_pixel(q, r)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i + math.pi / 6
            points.append((cx + self.hex_size * math.cos(angle),
                           cy + self.hex_size * math.sin(angle)))
        pygame.draw.polygon(surface, color, points, 0)
        pygame.draw.polygon(surface, (0,0,0), points, 1)

    # Generate all hex coordinates forming a hex-shaped board
    def generate_hex_map(self):
        coords = []
        r = self.radius
        for q in range(-r, r+1):
            r1 = max(-r, -q-r)
            r2 = min(r, -q+r)
            for rr in range(r1, r2+1):
                coords.append((q, rr))
        return coords

    def rotate_point(self, x, y, angle_degrees):
        angle = math.radians(angle_degrees)
        cx, cy = self.center_offset
        dx = x - cx
        dy = y - cy
        rx = dx * math.cos(angle) - dy * math.sin(angle)
        ry = dx * math.sin(angle) + dy * math.cos(angle)
        return rx + cx, ry + cy


    def draw_map(self):
        self.map_surface.fill((0,0,0,0))
        for q, r in self.hex_coords:
            color = self.colors[(q - r) % len(self.colors)]
            self.draw_hex(self.map_surface, q, r, color)
        if self.rotation != 0:
            self.map_surface = pygame.transform.rotate(self.map_surface, self.rotation)

    def draw(self, screen, selected_key=None, legal_moves=None, check_key=None):
        rect = self.map_surface.get_rect(center=self.center_offset)
        screen.blit(self.map_surface, rect.topleft)

        # Highlight king in check (red ring)
        if check_key is not None:
            q, r, s = check_key
            x, y = self.hex_to_pixel(q, r)
            if self.rotation != 0:
                x, y = self.rotate_point(x, y, self.rotation)
            pygame.draw.circle(screen, (220, 30, 30),
                               (int(x), int(y)), int(self.hex_size * 0.82), 4)

        # Highlight selected piece (gold ring)
        if selected_key is not None:
            q, r, s = selected_key
            x, y = self.hex_to_pixel(q, r)
            if self.rotation != 0:
                x, y = self.rotate_point(x, y, self.rotation)
            pygame.draw.circle(screen, (255, 215, 0),
                               (int(x), int(y)), int(self.hex_size * 0.75), 3)

        # Highlight legal move targets
        if legal_moves:
            for h in legal_moves:
                x, y = self.hex_to_pixel(h.q, h.r)
                if self.rotation != 0:
                    x, y = self.rotate_point(x, y, self.rotation)
                key = (h.q, h.r, h.s)
                if key in self.pieces:
                    # Capture square: red ring
                    pygame.draw.circle(screen, (200, 60, 60),
                                       (int(x), int(y)), int(self.hex_size * 0.75), 3)
                else:
                    # Empty square: green dot
                    pygame.draw.circle(screen, (60, 190, 60),
                                       (int(x), int(y)), int(self.hex_size * 0.28))

        for pos_key, piece in self.pieces.items():
            q, r, s = pos_key
            x, y = self.hex_to_pixel(q, r)

            if self.rotation != 0:
                x, y = self.rotate_point(x, y, self.rotation)

            rect = piece.image.get_rect(center=(x, y))
            screen.blit(piece.image, rect)

    def add_piece(self, piece):
        self.pieces[piece.pos_tuple()] = piece

    def move_piece(self, from_key, to_key):
        piece = self.pieces.pop(from_key)
        self.pieces.pop(to_key, None)  # remove captured piece if any
        piece.pos = hexmath.Hex(*to_key)
        self.pieces[to_key] = piece

    def find_king_key(self, color):
        return next(
            (k for k, p in self.pieces.items() if p.color == color and p.name == "King"),
            None
        )

    def is_in_check(self, color):
        king_key = self.find_king_key(color)
        if king_key is None:
            return False
        enemy = "black" if color == "white" else "white"
        for piece in list(self.pieces.values()):
            if piece.color == enemy:
                for mv in piece.get_moves(self):
                    if (mv.q, mv.r, mv.s) == king_key:
                        return True
        return False

    def get_legal_moves(self, piece, last_move=None):
        """Return pseudo-legal moves filtered so they don't leave own king in check."""
        pseudo = piece.get_moves(self, last_move)
        legal = []
        from_key = piece.pos_tuple()
        for target in pseudo:
            to_key = (target.q, target.r, target.s)

            # Detect en passant: pawn moves diagonally to an empty square
            ep_key = None
            if (piece.name == "Pawn" and to_key not in self.pieces
                    and last_move and last_move.piece.name == "Pawn"
                    and last_move.piece.color != piece.color):
                ep_key = (last_move.to_pos.q, last_move.to_pos.r, last_move.to_pos.s)

            moved = self.pieces.pop(from_key)
            captured = self.pieces.pop(to_key, None)
            ep_piece = self.pieces.pop(ep_key, None) if ep_key else None
            moved.pos = target
            self.pieces[to_key] = moved
            still_in_check = self.is_in_check(piece.color)
            self.pieces.pop(to_key)
            moved.pos = hexmath.Hex(*from_key)
            self.pieces[from_key] = moved
            if captured is not None:
                self.pieces[to_key] = captured
            if ep_piece is not None:
                self.pieces[ep_key] = ep_piece
            if not still_in_check:
                legal.append(target)
        return legal

    def has_legal_moves(self, color, last_move=None):
        for piece in list(self.pieces.values()):
            if piece.color == color:
                if self.get_legal_moves(piece, last_move):
                    return True
        return False