import pygame
from constants import *

import random
from mazes import MAZE_LAYOUTS

class Maze:
    def __init__(self, layout_name="default"):
        # Load a predefined layout
        self.grid = MAZE_LAYOUTS.get(layout_name, MAZE_LAYOUTS["default"]).copy()
        # Store actual dimensions of the chosen layout
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0
        # If layout dimensions differ from constants, optionally scale or pad (here we trust layout sizes)
        # Pellets on walkable tiles
        self.pellets = [(x, y) for y in range(self.height) for x in range(self.width) if self.grid[y][x] == 0]
        self.hide_walls = False

    def draw(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    if not self.hide_walls:
                        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(screen, WALL_COLOR, rect)
                elif (x, y) in self.pellets:
                    # Draw pellet
                    center_x = x * TILE_SIZE + TILE_SIZE // 2
                    center_y = y * TILE_SIZE + TILE_SIZE // 2
                    pygame.draw.circle(screen, PELLET_COLOR, (center_x, center_y), PELLET_RADIUS)

    def is_wall(self, x, y):
        # Check if position (x, y) is a wall
        # Convert pixel coordinates to grid coordinates
        grid_x = int(x // TILE_SIZE)
        grid_y = int(y // TILE_SIZE)
        # Check bounds using actual dimensions
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return True
        return self.grid[grid_y][grid_x] == 1