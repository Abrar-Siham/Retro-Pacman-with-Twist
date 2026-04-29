import pygame
import random
from constants import *

class Ghost:
    def __init__(self, x, y, color=None, score=0):
        # Position in pixels (float for smooth movement)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        # Direction: (dx, dy) - one of (0,0), (1,0), (-1,0), (0,1), (0,-1)
        self.direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        # Ensure the ghost is not stationary initially
        while self.direction == (0, 0):
            self.direction = (random.choice([-1, 0, 1]), random.choice([-1, 0, 1]))
        self.speed = 1.5  # Slightly slower than Pac-Man
        self.radius = TILE_SIZE // 2
        self.color = color if color is not None else GHOST_COLOR  # Default ghost color
        self.score = score  # For compatibility when controlled by player

    def update(self, maze):
        # Calculate new position based on current direction
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        # Check if the new position is valid (not a wall)
        # We check the center of the ghost for simplicity
        if not maze.is_wall(new_x + self.radius, new_y + self.radius):
            self.x = new_x
            self.y = new_y
        else:
            # If we hit a wall, choose a new random direction
            self.choose_new_direction(maze)

        # Occasionally change direction randomly (even if not blocked)
        if random.random() < 0.02:  # 2% chance per frame to change direction
            self.choose_new_direction(maze)

    def choose_new_direction(self, maze):
        # Choose a random direction that is not blocked
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(directions)
        for dx, dy in directions:
            # Check if moving in this direction is possible (at least one step)
            test_x = self.x + dx * self.speed
            test_y = self.y + dy * self.speed
            if not maze.is_wall(test_x + self.radius, test_y + self.radius):
                self.direction = (dx, dy)
                break
        # If all directions are blocked (shouldn't happen in open maze), stay stationary
        else:
            self.direction = (0, 0)

    def draw(self, screen):
        # Draw ghost as a circle
        pygame.draw.circle(screen, self.color, (int(self.x) + self.radius, int(self.y) + self.radius), self.radius)

    def get_rect(self):
        # Return a rectangle for collision detection
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)