import pygame
from constants import *

class Player:
    def __init__(self, x, y):
        # Position in pixels (float for smooth movement)
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        # Direction: (dx, dy) - one of (0,0), (1,0), (-1,0), (0,1), (0,-1)
        self.direction = (0, 0)
        self.speed = 2  # Pixels per frame
        self.radius = TILE_SIZE // 2
        self.score = 0

    def update(self, maze):
        # Calculate new position based on current direction
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        # Check if the new position is valid (not a wall)
        # We'll check the center of the player for simplicity
        if not maze.is_wall(new_x + self.radius, new_y + self.radius):
            self.x = new_x
            self.y = new_y
            # Check for pellet collision
            self.check_pellet_collision(maze)
        else:
            # If we hit a wall, we stop moving in that direction
            pass

    def check_pellet_collision(self, maze):
        # Convert player's center position to grid coordinates
        center_x = self.x + self.radius
        center_y = self.y + self.radius
        grid_x = int(center_x // TILE_SIZE)
        grid_y = int(center_y // TILE_SIZE)
        
        # Check if there's a pellet at this position
        if (grid_x, grid_y) in maze.pellets:
            maze.pellets.remove((grid_x, grid_y))
            self.score += 10  # Points per pellet
            # Play pellet sound if available
            try:
                from sounds import EAT_SOUND
                if EAT_SOUND:
                    EAT_SOUND.play()
            except Exception:
                pass

    def draw(self, screen):
        # Draw Pac-Man as a yellow circle
        pygame.draw.circle(screen, PACMAN_COLOR, (int(self.x) + self.radius, int(self.y) + self.radius), self.radius)

    def handle_input(self):
        # This method will be called to set the direction based on key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.direction = (-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.direction = (1, 0)
        elif keys[pygame.K_UP]:
            self.direction = (0, -1)
        elif keys[pygame.K_DOWN]:
            self.direction = (0, 1)
        # If no key is pressed, direction remains the same (so we keep moving in the last direction until blocked)