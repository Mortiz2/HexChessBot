import pygame
from board import Board

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

board = Board(radius=5, hex_size=30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((215, 200, 170))
    board.draw(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
