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

# Load images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(os.path.dirname(BASE_DIR), "img")
player_img = pygame.image.load(os.path.join(IMG_DIR, "player.png")).convert_alpha()
bullet_img = pygame.image.load(os.path.join(IMG_DIR, "bullet.png")).convert_alpha()

# Barrel offset relative to center of player.png
BARREL_DX = 233.0 - 125.0
BARREL_DY = 121.0 - 82.5

# Player position
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_angle = 0.0

# Bullet variables
bullets = []
BULLET_SPEED = 18
RELOAD_SPEED = 0.7
last_shot_time = RELOAD_SPEED

running = True
while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot on left click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if last_shot_time >= RELOAD_SPEED:
                last_shot_time = 0.0

                # Calculate rotated barrel coordinates
                cos_a = math.cos(player_angle)
                sin_a = math.sin(player_angle)
                spawn_x = player_x + (BARREL_DX * cos_a - BARREL_DY * sin_a)
                spawn_y = player_y + (BARREL_DX * sin_a + BARREL_DY * cos_a)

                # Direction vector towards mouse click
                dx = event.pos[0] - spawn_x
                dy = event.pos[1] - spawn_y
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                else:
                    dir_x, dir_y = cos_a, sin_a

                bullets.append([spawn_x, spawn_y, dir_x, dir_y])

    last_shot_time += dt

    # Rotate player towards mouse
    p_dx = mouse_pos[0] - player_x
    p_dy = mouse_pos[1] - player_y
    player_angle = math.atan2(p_dy, p_dx)

    # Move bullets
    active_bullets = []
    for b in bullets:
        b[0] += b[2] * BULLET_SPEED
        b[1] += b[3] * BULLET_SPEED
        
        # Keep inside screen bounds
        if 0 <= b[0] <= SCREEN_WIDTH and 0 <= b[1] <= SCREEN_HEIGHT:
            active_bullets.append(b)
    bullets = active_bullets

    # Drawing
    screen.fill((0, 0, 0))

    # Draw bullets
    for b in bullets:
        b_rect = bullet_img.get_rect(center=(int(b[0]), int(b[1])))
        screen.blit(bullet_img, b_rect)

    # Draw player
    rot_player = pygame.transform.rotate(player_img, -math.degrees(player_angle))
    p_rect = rot_player.get_rect(center=(player_x, player_y))
    screen.blit(rot_player, p_rect)

    pygame.display.flip()

pygame.quit()
