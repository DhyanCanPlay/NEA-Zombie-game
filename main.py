import pygame
import math
import random
import os
import heapq

# Initialise pygame
pygame.init()
pygame.font.init()

# Setup game window
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Game - NEA")

# Clock for frame rate
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GRAY = (70, 70, 70)
LIGHT_GRAY = (120, 120, 120)
BLACK = (0, 0, 0)   

# Fonts for menus and text
FONT_BIG = pygame.font.SysFont("Arial", 50, bold=True)
FONT_MED = pygame.font.SysFont("Arial", 30, bold=True)

# Path to the img folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "img")

# Load images
player_img = pygame.image.load(os.path.join(IMG_DIR, "player.png")).convert_alpha()
zombie_img = pygame.image.load(os.path.join(IMG_DIR, "zombie.png")).convert_alpha()
bullet_img = pygame.image.load(os.path.join(IMG_DIR, "bullet.png")).convert_alpha()

# Barrel offset relative to the center of player.png
# Center is (125, 82.5) and gun tip is (233, 121)
BARREL_DX = 233.0 - 125.0
BARREL_DY = 121.0 - 82.5

# Player position (fixed in center)
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_angle = 0.0

# Bullet variables
bullets = []
BULLET_SPEED = 18
RELOAD_SPEED = 0.7  # Time in seconds between shots
last_shot_time = RELOAD_SPEED

# Grid size for pathfinding
CELL_SIZE = 60
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

# Convert screen x and y pixels to grid row and column
def world_to_grid(x, y):
    column = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    c = max(0, min(GRID_COLS - 1, column))
    r = max(0, min(GRID_ROWS - 1, row))
    return r, c

# Convert grid row and column back to screen pixel coordinates
def grid_to_world(r, c):
    x = c * CELL_SIZE + (CELL_SIZE // 2)
    y = r * CELL_SIZE + (CELL_SIZE // 2)
    return x, y

# A* pathfinding algorithm
def a_star(start_rc, target_rc):
    if start_rc == target_rc:
        return [target_rc]

    # Heuristic function using distance
    def h(r, c):
        diff_c = c - target_rc[1]
        diff_r = r - target_rc[0]
        return math.sqrt(diff_c * diff_c + diff_r * diff_r)

    frontier = []
    initial_heuristic = h(start_rc[0], start_rc[1])
    heapq.heappush(frontier, (initial_heuristic, 0, start_rc))

    came_from = {}
    came_from[start_rc] = None
    
    cost_so_far = {}
    cost_so_far[start_rc] = 0

    while len(frontier) > 0:
        _, current_cost, current = heapq.heappop(frontier)

        if current == target_rc:
            break

        cr, cc = current

        # Check 8 surrounding directions
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:
            nr = cr + dr
            nc = cc + dc

            # Check if inside grid boundaries
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                # Diagonals cost 1.414, straight moves cost 1
                if dr != 0 and dc != 0:
                    step_cost = 1.414
                else:
                    step_cost = 1.0

                new_cost = current_cost + step_cost

                if (nr, nc) not in cost_so_far or new_cost < cost_so_far[(nr, nc)]:
                    cost_so_far[(nr, nc)] = new_cost
                    priority = new_cost + h(nr, nc)
                    heapq.heappush(frontier, (priority, new_cost, (nr, nc)))
                    came_from[(nr, nc)] = current

    if target_rc not in came_from:
        return []

    # Build path back to start
    curr = target_rc
    path = []
    while curr is not None and curr != start_rc:
        path.append(curr)
        curr = came_from[curr]

    path.reverse()
    return path

# Zombie enemy class
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

        # Recalculate A* path every 0.5 seconds
        if self.recalc_timer >= 0.5 or len(self.path) == 0:
            self.recalc_timer = 0.0
            start_rc = world_to_grid(self.x, self.y)
            target_rc = world_to_grid(target_x, target_y)
            self.path = a_star(start_rc, target_rc)

        target_wx = target_x
        target_wy = target_y

        # Follow path waypoint
        if len(self.path) > 0:
            nr, nc = self.path[0]
            wx, wy = grid_to_world(nr, nc)
            
            diff_x = wx - self.x
            diff_y = wy - self.y
            dist_to_waypoint = math.sqrt(diff_x * diff_x + diff_y * diff_y)

            # Move to next waypoint when close
            if dist_to_waypoint < 25:
                self.path.pop(0)
                if len(self.path) > 0:
                    nr, nc = self.path[0]
                    wx, wy = grid_to_world(nr, nc)

            target_wx = wx
            target_wy = wy

        # Move zombie
        dx = target_wx - self.x
        dy = target_wy - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            self.angle = math.atan2(target_y - self.y, target_x - self.x)

    def draw(self, surf):
        angle_deg = math.degrees(self.angle)
        rot_img = pygame.transform.rotate(zombie_img, -angle_deg)
        rect = rot_img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rot_img, rect)

# Draw menu button
def draw_button(surf, text, center_x, center_y, width, height, mouse_pos):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (center_x, center_y)
    
    is_hover = rect.collidepoint(mouse_pos)
    color = LIGHT_GRAY if is_hover else GRAY
    
    pygame.draw.rect(surf, color, rect)
    pygame.draw.rect(surf, WHITE, rect, 2)
    
    txt_surf = FONT_MED.render(text, True, WHITE)
    txt_rect = txt_surf.get_rect(center=rect.center)
    surf.blit(txt_surf, txt_rect)
    
    return rect

# Main game function
def main():
    global last_shot_time, player_angle, bullets
    
    zombies = []
    zombie_spawn_timer = 0.0
    state = "PLAYING"

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Pause toggle
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    if state == "PLAYING":
                        state = "PAUSED"
                    elif state == "PAUSED":
                        state = "PLAYING"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Pause menu clicks
                if state == "PAUSED":
                    btn_resume = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 40, 240, 50)
                    btn_quit = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 30, 240, 50)
                    if btn_resume.collidepoint(event.pos):
                        state = "PLAYING"
                    elif btn_quit.collidepoint(event.pos):
                        running = False

                # Game over menu clicks
                elif state == "GAME_OVER":
                    btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 10, 240, 50)
                    btn_quit = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 60, 240, 50)
                    if btn_retry.collidepoint(event.pos):
                        zombies.clear()
                        bullets.clear()
                        last_shot_time = RELOAD_SPEED
                        state = "PLAYING"
                    elif btn_quit.collidepoint(event.pos):
                        running = False

                # Firing bullets
                elif state == "PLAYING":
                    if last_shot_time >= RELOAD_SPEED:
                        last_shot_time = 0.0
                        
                        # Rotate barrel offset
                        cos_a = math.cos(player_angle)
                        sin_a = math.sin(player_angle)
                        spawn_x = player_x + (BARREL_DX * cos_a - BARREL_DY * sin_a)
                        spawn_y = player_y + (BARREL_DX * sin_a + BARREL_DY * cos_a)

                        dx = event.pos[0] - spawn_x
                        dy = event.pos[1] - spawn_y
                        dist = math.sqrt(dx * dx + dy * dy)
                        
                        if dist > 0:
                            dir_x = dx / dist
                            dir_y = dy / dist
                        else:
                            dir_x, dir_y = cos_a, sin_a

                        bullets.append([spawn_x, spawn_y, dir_x, dir_y])

        # Game updates
        if state == "PLAYING":
            last_shot_time += dt

            # Rotate player towards mouse
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
                
                # Check collision with player
                dist_to_player = math.sqrt((z.x - player_x)**2 + (z.y - player_y)**2)
                if dist_to_player < 70:
                    state = "GAME_OVER"

            # Update bullets
            active_bullets = []
            for b in bullets:
                b[0] += b[2] * BULLET_SPEED
                b[1] += b[3] * BULLET_SPEED

                # Check bullet collision with zombies
                hit_zombie = None
                for z in zombies:
                    dist_to_bullet = math.sqrt((z.x - b[0])**2 + (z.y - b[1])**2)
                    if dist_to_bullet < 60:
                        hit_zombie = z
                        break

                if hit_zombie is not None:
                    zombies.remove(hit_zombie)
                    continue

                if 0 <= b[0] <= SCREEN_WIDTH and 0 <= b[1] <= SCREEN_HEIGHT:
                    active_bullets.append(b)

            bullets = active_bullets

        # Drawing
        screen.fill(BLACK)

        for b in bullets:
            b_rect = bullet_img.get_rect(center=(int(b[0]), int(b[1])))
            screen.blit(bullet_img, b_rect)

        for z in zombies:
            z.draw(screen)

        rot_player = pygame.transform.rotate(player_img, -math.degrees(player_angle))
        p_rect = rot_player.get_rect(center=(player_x, player_y))
        screen.blit(rot_player, p_rect)

        # Draw Pause Menu
        if state == "PAUSED":
            title = FONT_BIG.render("PAUSED", True, WHITE)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))
            draw_button(screen, "Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15, 240, 50, mouse_pos)
            draw_button(screen, "Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55, 240, 50, mouse_pos)

        # Draw Game Over Screen
        elif state == "GAME_OVER":
            title = FONT_BIG.render("GAME OVER", True, RED)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))
            draw_button(screen, "Try Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15, 240, 50, mouse_pos)
            draw_button(screen, "Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 85, 240, 50, mouse_pos)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
