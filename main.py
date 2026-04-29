# main.py
import sys
import random
import pygame

from maze import Maze
from player import Player
from ghost import Ghost
from constants import *
from mazes import MAZE_LAYOUTS
from sounds import START_SOUND, DEATH_SOUND, EAT_SOUND

# ----------------------------------------------------------------------
# Game states
# ----------------------------------------------------------------------
MENU = 0          # Main menu
START = 1         # Transition to mode‑display screen
CHAOS_DISPLAY = 2 # Show selected chaos mode before play
PLAYING = 3
INSTRUCTIONS = 4
HIGHSCORE = 5
GAME_OVER = 6

# ----------------------------------------------------------------------
# Chaos modes
# ----------------------------------------------------------------------
CHAOS_MODES = ["maze", "ghost", "vision"]
MODE_COLORS = {
    "maze": (0, 255, 0),
    "ghost": (255, 0, 0),
    "vision": (0, 0, 255),
}


class ChaosMode:
    """Base class for chaos modes."""
    def __init__(self, name):
        self.name = name

    def apply(self, maze, player, ghosts):
        """Modify maze / player / ghosts – overridden per mode."""
        pass

    def draw_overlay(self, screen, player):
        """Optional visual overlay – overridden per mode."""
        pass


class MazeMode(ChaosMode):
    def __init__(self):
        super().__init__("maze")

    def apply(self, maze, player, ghosts):
        maze.hide_walls = True  # walls are invisible but still solid


class GhostMode(ChaosMode):
    def __init__(self):
        super().__init__("ghost")

    def apply(self, maze, player, ghosts):
        # speed up existing ghosts
        for g in ghosts:
            g.speed *= 1.5
        # add two extra ghosts at random walkable tiles
        extra = []
        for _ in range(2):
            while True:
                gx = random.randint(1, maze.width - 2)
                gy = random.randint(1, maze.height - 2)
                if maze.grid[gy][gx] == 0:
                    extra.append(Ghost(gx, gy))
                    break
        ghosts.extend(extra)


class VisionMode(ChaosMode):
    def __init__(self):
        super().__init__("vision")

    def apply(self, maze, player, ghosts):
        player.vision_mode = True

    def draw_overlay(self, screen, player):
        # dark overlay with a clear circular viewport around the player
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        radius = TILE_SIZE * 4
        pygame.draw.circle(
            overlay,
            (0, 0, 0, 0),
            (int(player.x) + player.radius, int(player.y) + player.radius),
            radius,
        )
        screen.blit(overlay, (0, 0))


def load_high_score():
    try:
        with open("highscore.txt", "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def save_high_score(score):
    try:
        with open("highscore.txt", "w") as f:
            f.write(str(score))
    except Exception:
        pass


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac‑Man: Chaos Mode")
    clock = pygame.time.Clock()

    # ------------------------------------------------------------------
    # Fonts
    # ------------------------------------------------------------------
    font_small = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 48)
    font_large = pygame.font.Font(None, 72)

    # ------------------------------------------------------------------
    # Initial state
    # ------------------------------------------------------------------
    state = MENU
    selected_mode_name = None
    mode_instance = None
    mode_start_time = 0
    selected_layout = "default"

    # Game objects (created when we actually start playing)
    maze = None
    player = None
    ghosts = []

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    running = True
    while running:
        # ------------------------------------------------------------------
        # Event handling
        # ------------------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # --------------------------------------------------------------
                # MENU navigation
                # --------------------------------------------------------------
                if state == MENU:
                    if event.key == pygame.K_1:          # Start Game
                        selected_mode_name = random.choice(CHAOS_MODES)
                        if selected_mode_name == "maze":
                            mode_instance = MazeMode()
                        elif selected_mode_name == "ghost":
                            mode_instance = GhostMode()
                        elif selected_mode_name == "vision":
                            mode_instance = VisionMode()
                        else:
                            mode_instance = ChaosMode(selected_mode_name)
                        state = CHAOS_DISPLAY
                        mode_start_time = pygame.time.get_ticks()
                        # optional start sound
                        if START_SOUND:
                            START_SOUND.play()

                    elif event.key == pygame.K_2:        # Instructions
                        state = INSTRUCTIONS

                    elif event.key == pygame.K_3:        # High Score
                        state = HIGHSCORE

                    elif event.key == pygame.K_4:        # Quit
                        running = False

                # --------------------------------------------------------------
                # INSTRUCTIONS / HIGHSCORE screens – any key returns to menu
                # --------------------------------------------------------------
                elif state in (INSTRUCTIONS, HIGHSCORE):
                    if event.key == pygame.K_ESCAPE:
                        state = MENU

                # --------------------------------------------------------------
                # GAME OVER – restart or quit
                # --------------------------------------------------------------
                elif state == GAME_OVER:
                    if event.key == pygame.K_SPACE:      # Restart (go back to menu)
                        state = MENU
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        # ------------------------------------------------------------------
        # State handling & drawing
        # ------------------------------------------------------------------
        # --------------------------- MENU ---------------------------
        if state == MENU:
            screen.fill(BLACK)
            title = font_large.render("Pac‑Man: Chaos Mode", True, PACMAN_COLOR)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                                SCREEN_HEIGHT // 4))

            options = ["Start Game", "Instructions", "High Score", "Quit"]
            for i, opt in enumerate(options):
                txt = font_small.render(f"{i + 1}. {opt}", True, WHITE)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2,
                                 SCREEN_HEIGHT // 2 + i * 40))

        # ------------------------ INSTRUCTIONS --------------------
        elif state == INSTRUCTIONS:
            screen.fill(BLACK)
            title = font_large.render("Instructions", True, PACMAN_COLOR)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                                SCREEN_HEIGHT // 6))

            lines = [
                "Arrow keys – move Pac‑Man",
                "When a ghost touches Pac‑Man the game ends.",
                "",
                "Chaos Modes (chosen randomly when you start):",
                " • Maze  – walls are hidden, layout switches every 10‑15 s",
                " • Ghost – ghosts move faster and extra ghosts appear",
                " • Vision – limited visibility around Pac‑Man",
                "",
                "Press ESC to return to the main menu."
            ]
            for i, line in enumerate(lines):
                surf = font_small.render(line, True, WHITE)
                screen.blit(surf, (50, SCREEN_HEIGHT // 3 + i * 30))

        # ----------------------- HIGHSCORE -----------------------
        elif state == HIGHSCORE:
            screen.fill(BLACK)
            title = font_large.render("High Score", True, PACMAN_COLOR)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2,
                                SCREEN_HEIGHT // 4))

            best = load_high_score()
            score_surf = font_medium.render(f"Best Score: {best}", True, WHITE)
            screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2,
                                      SCREEN_HEIGHT // 2))

            hint = font_small.render("Press ESC to return", True, WHITE)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                               SCREEN_HEIGHT * 3 // 4))

        # ---------------------- CHAOS DISPLAY ---------------------
        elif state == CHAOS_DISPLAY:
            # Show the selected chaos mode for 2 seconds before gameplay
            elapsed = pygame.time.get_ticks() - mode_start_time
            if elapsed >= 2000:
                # Initialise game objects for the chosen layout
                maze = Maze(selected_layout)
                player = Player(1, 1)

                # ----- Ghost placement (always inside the current maze) -----
                ghosts = []
                # Ghost 1 – near top‑right
                gx1 = max(1, maze.width - 2)
                gy1 = 1
                if maze.grid[gy1][gx1] != 0:
                    for _ in range(10):
                        gx1 = random.randint(1, maze.width - 2)
                        gy1 = random.randint(1, maze.height - 2)
                        if maze.grid[gy1][gx1] == 0:
                            break
                ghosts.append(Ghost(gx1, gy1))

                # Ghost 2 – near bottom‑left
                gx2 = 1
                gy2 = max(1, maze.height - 2)
                if maze.grid[gy2][gx2] != 0:
                    for _ in range(10):
                        gx2 = random.randint(1, maze.width - 2)
                        gy2 = random.randint(1, maze.height - 2)
                        if maze.grid[gy2][gx2] == 0:
                            break
                ghosts.append(Ghost(gx2, gy2))

                # Apply the specific chaos‑mode modifications
                mode_instance.apply(maze, player, ghosts)

                state = PLAYING
            else:
                screen.fill(BLACK)
                col = MODE_COLORS.get(selected_mode_name, WHITE)
                mode_txt = font_large.render(selected_mode_name.upper(), True, col)
                instr = font_medium.render("Get ready!", True, WHITE)
                screen.blit(mode_txt, (SCREEN_WIDTH // 2 - mode_txt.get_width() // 2,
                                       SCREEN_HEIGHT // 2 - 60))
                screen.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 20))

        # ------------------------ PLAYING ------------------------
        elif state == PLAYING:
            # ---------- Input ----------
            if hasattr(player, "handle_input"):
                player.handle_input()

            # ---------- Update ----------
            player.update(maze)
            for g in ghosts:
                g.update(maze)

            # ---------- Maze‑mode automatic layout switch ----------
            if isinstance(mode_instance, MazeMode):
                if not hasattr(mode_instance, "next_switch"):
                    mode_instance.next_switch = pygame.time.get_ticks() + random.randint(
                        10000, 15000
                    )
                now = pygame.time.get_ticks()
                if now >= mode_instance.next_switch:
                    # flash indication
                    mode_instance.flash = True
                    mode_instance.flash_start = now

                    # Choose a *different* layout
                    keys = list(MAZE_LAYOUTS.keys())
                    new_layout = random.choice(keys)
                    while new_layout == selected_layout:
                        new_layout = random.choice(keys)
                    selected_layout = new_layout
                    maze = Maze(selected_layout)

                    # Reset player position
                    player.x = TILE_SIZE
                    player.y = TILE_SIZE

                    # Re‑create core ghosts inside the new maze
                    ghosts = []
                    # top‑right ghost
                    gx = max(1, maze.width - 2)
                    gy = 1
                    if maze.grid[gy][gx] != 0:
                        for _ in range(10):
                            gx = random.randint(1, maze.width - 2)
                            gy = random.randint(1, maze.height - 2)
                            if maze.grid[gy][gx] == 0:
                                break
                    ghosts.append(Ghost(gx, gy))
                    # bottom‑left ghost
                    gx = 1
                    gy = max(1, maze.height - 2)
                    if maze.grid[gy][gx] != 0:
                        for _ in range(10):
                            gx = random.randint(1, maze.width - 2)
                            gy = random.randint(1, maze.height - 2)
                            if maze.grid[gy][gx] == 0:
                                break
                    ghosts.append(Ghost(gx, gy))

                    # reset timer for next switch
                    mode_instance.next_switch = now + random.randint(10000, 15000)

            # ---------- Collision detection ----------
            player_rect = pygame.Rect(player.x, player.y, TILE_SIZE, TILE_SIZE)
            for g in ghosts:
                if player_rect.colliderect(g.get_rect()):
                    state = GAME_OVER
                    if DEATH_SOUND:
                        DEATH_SOUND.play()
                    break

            # ---------- Drawing ----------
            screen.fill(BLACK)
            maze.draw(screen)
            player.draw(screen)
            for g in ghosts:
                g.draw(screen)

            # flash overlay (maze mode)
            if isinstance(mode_instance, MazeMode) and getattr(mode_instance, "flash", False):
                if pygame.time.get_ticks() - mode_instance.flash_start < 200:
                    flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    flash.fill(WHITE)
                    screen.blit(flash, (0, 0))
                else:
                    mode_instance.flash = False

            # score
            score_surf = font_small.render(f"Score: {player.score}", True, WHITE)
            screen.blit(score_surf, (10, 10))

            # mode‑specific overlay (e.g., vision)
            if mode_instance:
                mode_instance.draw_overlay(screen, player)

        # ----------------------- GAME OVER ----------------------
        elif state == GAME_OVER:
            screen.fill(BLACK)
            over = font_large.render("GAME OVER", True, (255, 0, 0))
            sc = font_small.render(f"Final Score: {player.score}", True, WHITE)
            hint = font_small.render(
                "Press SPACE to Restart or ESC to Quit", True, WHITE
            )
            screen.blit(over, (SCREEN_WIDTH // 2 - over.get_width() // 2,
                               SCREEN_HEIGHT // 3))
            screen.blit(sc, (SCREEN_WIDTH // 2 - sc.get_width() // 2,
                             SCREEN_HEIGHT // 2))
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                               SCREEN_HEIGHT * 2 // 3))

            # Update high score if needed
            best = load_high_score()
            if player.score > best:
                save_high_score(player.score)

        # ------------------------------------------------------------------
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()