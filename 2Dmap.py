import pygame
import sys
import random
import math

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 50, 50
MINIMAP_SCALE = 0.1
FPS = 60
SWIM_SPEED_FACTOR = 0.5
BOB_AMPLITUDE = 4
BOB_SPEED = 400

# Colors
def rand_color(base, variance):
    return tuple(
        max(0, min(255, base[i] + random.randint(-variance, variance)))
        for i in range(3)
    )

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (100, 50, 0)
LEAF_GREEN = (34, 139, 34)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D World with Trees & Refined Bob")
clock = pygame.time.Clock()

# Tile generation functions
def make_grass_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    base = (50, 180, 50)
    surf.fill(base)
    for _ in range(20):
        x, y = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
        surf.set_at((x, y), rand_color(base, 20))
    for _ in range(10):
        x, y = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
        length = random.randint(3, 7)
        angle = random.uniform(-math.pi / 4, math.pi / 4)
        pygame.draw.line(
            surf,
            rand_color((30, 150, 30), 15),
            (x, y),
            (x + math.cos(angle) * length, y - math.sin(angle) * length),
            1,
        )
    return surf

def make_water_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    base = (30, 100, 200)
    surf.fill(base)
    for _ in range(3):
        y = random.randint(0, TILE_SIZE - 5)
        pygame.draw.arc(
            surf,
            rand_color((255, 255, 255), 50),
            (0, y, TILE_SIZE, 10),
            0,
            random.uniform(math.pi, 2 * math.pi),
            1,
        )
    return surf

def make_sand_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    base = (194, 178, 128)
    surf.fill(base)
    for _ in range(20):
        x, y = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
        surf.set_at((x, y), rand_color((150, 130, 80), 20))
    return surf

def make_block_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    base = (120, 120, 120)
    surf.fill(base)
    for _ in range(30):
        x, y = random.randint(0, TILE_SIZE - 1), random.randint(0, TILE_SIZE - 1)
        surf.set_at((x, y), rand_color((90, 90, 90), 30))
    return surf

def make_trunk_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    surf.fill(BROWN)
    for _ in range(10):
        x = random.randint(0, TILE_SIZE - 1)
        h = random.randint(5, TILE_SIZE // 2)
        y = random.randint(0, TILE_SIZE - h)
        pygame.draw.rect(surf, rand_color((80, 40, 0), 20), (x, y, 2, h))
    return surf

def make_leaf_tile():
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    cell = 4
    for i in range(0, TILE_SIZE, cell):
        for j in range(0, TILE_SIZE, cell):
            if random.random() < 0.7:
                pygame.draw.rect(surf, LEAF_GREEN, (i, j, cell, cell))
    return surf

# Generate static textures once
grass_tile = make_grass_tile()
water_tile = make_water_tile()  # Fix: pre-generate this
sand_tile = make_sand_tile()
block_proto = make_block_tile()
trunk_proto = make_trunk_tile()
leaf_proto = make_leaf_tile()

# World generation
world_map = [[0] * MAP_WIDTH for _ in range(MAP_HEIGHT)]
block_textures = {}
trunk_textures = {}
leaves = []
tree_positions = []

def generate_lakes_and_sand():
    for _ in range(random.randint(3, 6)):
        cx = random.randint(0, MAP_WIDTH - 1)
        cy = random.randint(0, MAP_HEIGHT - 1)
        r = random.randint(4, 10)
        for y in range(max(0, cy - r), min(MAP_HEIGHT, cy + r)):
            for x in range(max(0, cx - r), min(MAP_WIDTH, cx + r)):
                if math.hypot(x - cx, y - cy) < r * (0.8 + 0.4 * random.random()):
                    world_map[y][x] = 1  # water
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if world_map[y][x] == 1:
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT and world_map[ny][nx] == 0:
                            world_map[ny][nx] = 2  # sand

generate_lakes_and_sand()

# Place trees and blocks
choices = [(x, y) for y in range(MAP_HEIGHT) for x in range(MAP_WIDTH) if world_map[y][x] == 0]
tree_positions = random.sample(choices, 4)
for tx, ty in tree_positions:
    world_map[ty][tx] = 4  # trunk
    trunk_textures[(tx, ty)] = trunk_proto.copy()
    for ly in range(ty - 1, ty + 2):
        for lx in range(tx - 1, tx + 2):
            if 0 <= lx < MAP_WIDTH and 0 <= ly < MAP_HEIGHT and world_map[ly][lx] == 0:
                world_map[ly][lx] = 5  # leaf
                leaves.append(((lx, ly), leaf_proto.copy()))

for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        if world_map[y][x] == 0 and random.random() < 0.05:
            world_map[y][x] = 3
            block_textures[(x, y)] = block_proto.copy()

# Player setup
player_size = TILE_SIZE // 2
player_speed = 4
player_pos = [MAP_WIDTH // 2 * TILE_SIZE, MAP_HEIGHT // 2 * TILE_SIZE]
player_rect = pygame.Rect(*player_pos, player_size, player_size)
camera_offset = [0, 0]

# Drawing
def draw_world():
    for y, row in enumerate(world_map):
        for x, t in enumerate(row):
            sx = x * TILE_SIZE - camera_offset[0]
            sy = y * TILE_SIZE - camera_offset[1]
            if -TILE_SIZE < sx < SCREEN_WIDTH and -TILE_SIZE < sy < SCREEN_HEIGHT:
                if t == 0:
                    screen.blit(grass_tile, (sx, sy))
                elif t == 1:
                    screen.blit(water_tile, (sx, sy))
                elif t == 2:
                    screen.blit(sand_tile, (sx, sy))
                elif t == 3:
                    screen.blit(block_textures[(x, y)], (sx, sy))
                elif t == 4:
                    screen.blit(trunk_textures[(x, y)], (sx, sy))

def draw_minimap():
    mw = int(MAP_WIDTH * TILE_SIZE * MINIMAP_SCALE)
    mh = int(MAP_HEIGHT * TILE_SIZE * MINIMAP_SCALE)
    mini = pygame.Surface((mw, mh))
    cmap = {
        0: (0, 180, 0),
        1: (0, 0, 200),
        2: (210, 180, 140),
        3: (100, 100, 100),
        4: BROWN,
        5: LEAF_GREEN,
    }
    for y, row in enumerate(world_map):
        for x, t in enumerate(row):
            color = cmap.get(t, (0, 0, 0))
            rx, ry = int(x * TILE_SIZE * MINIMAP_SCALE), int(y * TILE_SIZE * MINIMAP_SCALE)
            pygame.draw.rect(mini, color, (rx, ry, 2, 2))
    px = int(player_rect.centerx * MINIMAP_SCALE)
    py = int(player_rect.centery * MINIMAP_SCALE)
    pygame.draw.circle(mini, (255, 0, 0), (px, py), 3)
    screen.blit(mini, (SCREEN_WIDTH - mw - 10, 10))

# Game loop
running = True
start_ticks = pygame.time.get_ticks()

while running:
    dt = clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_s]: dy += 1
    if keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_d]: dx += 1

    # Normalize movement
    if dx != 0 and dy != 0:
        dx *= 0.7071
        dy *= 0.7071

    # Determine if in water
    cx, cy = int(player_rect.centerx / TILE_SIZE), int(player_rect.centery / TILE_SIZE)
    in_water = 0 <= cx < MAP_WIDTH and 0 <= cy < MAP_HEIGHT and world_map[cy][cx] == 1
    speed = player_speed * (SWIM_SPEED_FACTOR if in_water else 1)

    player_rect.x += dx * speed
    player_rect.y += dy * speed

    camera_offset[0] = player_rect.centerx - SCREEN_WIDTH // 2
    camera_offset[1] = player_rect.centery - SCREEN_HEIGHT // 2

    # Bobbing effect
    elapsed = pygame.time.get_ticks() - start_ticks
    bob_offset = math.sin(elapsed / BOB_SPEED) * BOB_AMPLITUDE

    screen.fill(BLACK)
    draw_world()
    for (x, y), surf in leaves:
        screen.blit(surf, (x * TILE_SIZE - camera_offset[0], y * TILE_SIZE - camera_offset[1]))
    pygame.draw.rect(screen, WHITE, (player_rect.x - camera_offset[0], player_rect.y - camera_offset[1] + bob_offset, player_size, player_size))
    draw_minimap()

    pygame.display.flip()

pygame.quit()
sys.exit() 
