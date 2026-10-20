import pygame
import math
import random
import os
import heapq

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
zombie_img = pygame.image.load(os.path.join(IMG_DIR, "zombie.png")).convert_alpha()
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

# Grid for A* pathfinding (60x60 pixel cells)
CELL_SIZE = 60
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

def world_to_grid(x, y):
    c = max(0, min(GRID_COLS - 1, int(x // CELL_SIZE)))
    r = max(0, min(GRID_ROWS - 1, int(y // CELL_SIZE)))
    return r, c

def grid_to_world(r, c):
    return c * CELL_SIZE + CELL_SIZE // 2, r * CELL_SIZE + CELL_SIZE // 2

# A* pathfinding function
def a_star(start_rc, target_rc):
    if start_rc == target_rc:
        return [target_rc]

    def h(r, c):
        return math.hypot(c - target_rc[1], r - target_rc[0])

    frontier = []
    heapq.heappush(frontier, (h(*start_rc), 0, start_rc))
    came_from = {start_rc: None}
    cost_so_far = {start_rc: 0}

    while len(frontier) > 0:
        _, current_cost, current = heapq.heappop(frontier)
        if current == target_rc:
            break

        cr, cc = current
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
            nr, nc = cr + dr, cc + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                step_cost = 1.414 if (dr != 0 and dc != 0) else 1.0
                new_cost = current_cost + step_cost
                if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                    cost_so_far[(nr, nc)] = new_cost
                    priority = new_cost + h(nr, nc)
                    heapq.heappush(frontier, (priority, new_cost, (nr, nc)))
                    came_from[(nr, nc)] = current

    if target_rc not in came_from:
        return []

    curr = target_rc
    path = []
    while curr is not None and curr != start_rc:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

# Zombie class with A* pathfinding
class Zombie:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.speed = random.uniform(2.0, 3.0)
        self.path = []
        self.recalc_timer = random.uniform(0.0, 0.5)
        self.angle = 0.0

    def update(self, dt, target_x, target_y):
        self.recalc_timer += dt
        if self.recalc_timer >= 0.5 or not self.path:
            self.recalc_timer = 0.0
            start_rc = world_to_grid(self.x, self.y)
            target_rc = world_to_grid(target_x, target_y)
            self.path = a_star(start_rc, target_rc)

        target_wx, target_wy = target_x, target_y
        if len(self.path) > 0:
            nr, nc = self.path[0]
            wx, wy = grid_to_world(nr, nc)
            if math.hypot(wx - self.x, wy - self.y) < 25:
                self.path.pop(0)
                if len(self.path) > 0:
                    nr, nc = self.path[0]
                    wx, wy = grid_to_world(nr, nc)
            target_wx, target_wy = wx, wy

        dx = target_wx - self.x
        dy = target_wy - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.angle = math.atan2(target_y - self.y, target_x - self.x)

    def draw(self, surf):
        rot_img = pygame.transform.rotate(zombie_img, -math.degrees(self.angle))
        rect = rot_img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rot_img, rect)

zombies = []
zombie_spawn_timer = 0.0
game_over = False

running = True
while running:
    dt = clock.tick(60) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            if last_shot_time >= RELOAD_SPEED:
                last_shot_time = 0.0
                cos_a = math.cos(player_angle)
                sin_a = math.sin(player_angle)
                spawn_x = player_x + (BARREL_DX * cos_a - BARREL_DY * sin_a)
                spawn_y = player_y + (BARREL_DX * sin_a + BARREL_DY * cos_a)

                dx = event.pos[0] - spawn_x
                dy = event.pos[1] - spawn_y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                else:
                    dir_x, dir_y = cos_a, sin_a

                bullets.append([spawn_x, spawn_y, dir_x, dir_y])

    if not game_over:
        last_shot_time += dt

        p_dx = mouse_pos[0] - player_x
        p_dy = mouse_pos[1] - player_y
        player_angle = math.atan2(p_dy, p_dx)

        # Spawn zombies every 2 seconds
        zombie_spawn_timer += dt
        if zombie_spawn_timer >= 2.0:
            zombie_spawn_timer = 0.0
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                zx, zy = random.randint(0, SCREEN_WIDTH), 0
            elif side == "bottom":
                zx, zy = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT
            elif side == "left":
                zx, zy = 0, random.randint(0, SCREEN_HEIGHT)
            else:
                zx, zy = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
            zombies.append(Zombie(zx, zy))

        # Update zombies
        for z in zombies:
            z.update(dt, player_x, player_y)
            if math.hypot(z.x - player_x, z.y - player_y) < 70:
                game_over = True

        # Update bullets
        active_bullets = []
        for b in bullets:
            b[0] += b[2] * BULLET_SPEED
            b[1] += b[3] * BULLET_SPEED

            hit_zombie = None
            for z in zombies:
                if math.hypot(z.x - b[0], z.y - b[1]) < 60:
                    hit_zombie = z
                    break

            if hit_zombie is not None:
                zombies.remove(hit_zombie)
                continue

            if 0 <= b[0] <= SCREEN_WIDTH and 0 <= b[1] <= SCREEN_HEIGHT:
                active_bullets.append(b)
        bullets = active_bullets

    # Drawing
    screen.fill((0, 0, 0))

    # Draw bullets
    for b in bullets:
        b_rect = bullet_img.get_rect(center=(int(b[0]), int(b[1])))
        screen.blit(bullet_img, b_rect)

    # Draw zombies
    for z in zombies:
        z.draw(screen)

    # Draw player
    rot_player = pygame.transform.rotate(player_img, -math.degrees(player_angle))
    p_rect = rot_player.get_rect(center=(player_x, player_y))
    screen.blit(rot_player, p_rect)

    pygame.display.flip()

pygame.quit()
