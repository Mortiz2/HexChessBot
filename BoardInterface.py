import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Parameters
radius = 5               # board radius (number of hexes from center to edge)
hex_size = 30            # size of each hex
colors = [(209, 150, 88), (228,197,165), (171, 117, 60)]  # alternating tile colors

# Convert hex grid coordinates (q, r) to pixel coordinates
def hex_to_pixel(q, r, size):
    x = size * (math.sqrt(3) * q + math.sqrt(3)/2 * r)
    y = size * (3/2 * r)
    return (x, y)

# Draw a single hex tile on the given surface
def draw_hex(surface, q, r, size, color, offset=(0,0)):
    cx, cy = hex_to_pixel(q, r, size)
    cx += offset[0]
    cy += offset[1]
    points = []
    for i in range(6):
        angle = math.pi / 3 * i + math.pi / 6  # 60° per corner, rotated by 30°
        points.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
    pygame.draw.polygon(surface, color, points, 0)   # filled hex
    pygame.draw.polygon(surface, (0,0,0), points, 1) # black outline

# Generate all hex coordinates forming a hex-shaped board
def generate_hex_map(radius):
    coords = []
    for q in range(-radius, radius+1):
        r1 = max(-radius, -q-radius)
        r2 = min(radius, -q+radius)
        for r in range(r1, r2+1):
            coords.append((q, r))
    return coords

# Create a transparent surface to draw the hex map
map_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
center_offset = (400, 300)

# Draw all hexes with alternating colors
hex_coords = generate_hex_map(radius)
for idx, (q, r) in enumerate(hex_coords):
    color = colors[(q - r) % 3]
    draw_hex(map_surface, q, r, hex_size, color, offset=center_offset)

# Rotate the whole map by 90 degrees
rotated_map = pygame.transform.rotate(map_surface, 90)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))
    rect = rotated_map.get_rect(center=(400, 300))
    screen.blit(rotated_map, rect.topleft)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()