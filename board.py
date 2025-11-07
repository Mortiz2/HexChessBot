import pygame
import math
import hexmath

class Board:
    def __init__(self, radius=5, hex_size=30, colors=None, center_offset=(400, 300), rotation=90):
        self.radius = radius
        self.hex_size = hex_size
        self.colors = colors or [(209, 150, 88), (228,197,165), (171, 117, 60)]
        self.center_offset = center_offset
        self.rotation = rotation
        self.hex_coords = self.generate_hex_map()
        self.map_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        self.draw_map()

    # Convert hex grid coordinates (q, r) to pixel coordinates
    def hex_to_pixel(self, q, r):
        x = self.hex_size * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
        y = self.hex_size * (3/2 * r)
        return (x + self.center_offset[0], y + self.center_offset[1])

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

    def draw_map(self):
        self.map_surface.fill((0,0,0,0))
        for q, r in self.hex_coords:
            color = self.colors[(q - r) % len(self.colors)]
            self.draw_hex(self.map_surface, q, r, color)
        if self.rotation != 0:
            self.map_surface = pygame.transform.rotate(self.map_surface, self.rotation)

    def draw(self, screen):
        rect = self.map_surface.get_rect(center=self.center_offset)
        screen.blit(self.map_surface, rect.topleft)