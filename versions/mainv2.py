import pygame
import math
import os

# Initialise pygame
pygame.init()

# Setup screen
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Game - NEA")

# Clock for frame rate
clock = pygame.time.Clock()

# Load player image
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(os.path.dirname(BASE_DIR), "img")
player_img = pygame.image.load(os.path.join(IMG_DIR, "player.png")).convert_alpha()

# Player position (fixed in center)
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_angle = 0.0

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Rotate player towards mouse using atan2
    dx = mouse_pos[0] - player_x
    dy = mouse_pos[1] - player_y
    player_angle = math.atan2(dy, dx)

    # Drawing
    screen.fill((0, 0, 0))

    # Rotate sprite and draw
    rot_player = pygame.transform.rotate(player_img, -math.degrees(player_angle))
    rect = rot_player.get_rect(center=(player_x, player_y))
    screen.blit(rot_player, rect)

    pygame.display.flip()

pygame.quit()
