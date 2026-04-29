# Game constants
TILE_SIZE = 20
MAZE_WIDTH = 28
MAZE_HEIGHT = 31
SCREEN_WIDTH = TILE_SIZE * MAZE_WIDTH
SCREEN_HEIGHT = TILE_SIZE * MAZE_HEIGHT
FPS = 60

# Colors
BLACK = (10, 10, 10)          # Dark background
WHITE = (250, 250, 250)       # Near‑white for text
WALL_COLOR = (30, 30, 120)    # Soft blue walls
PACMAN_COLOR = (255, 255, 0)  # Classic yellow
GHOST_COLOR = (200, 30, 30)   # Red ghost
PELLET_COLOR = (200, 200, 200) # Light gray pellets

# Pellet
PELLET_RADIUS = TILE_SIZE // 8