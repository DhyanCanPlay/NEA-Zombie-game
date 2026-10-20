import pygame

# Initialise pygame
pygame.init()

# Setup screen
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Game - NEA")

# Clock for frame rate
clock = pygame.time.Clock()

running = True
while running:
    clock.tick(60)

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill background with black
    screen.fill((0, 0, 0))

    # Update screen
    pygame.display.flip()

pygame.quit()
