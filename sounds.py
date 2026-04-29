import pygame
import os

# Simple sound loader – use placeholder beep if files not present
def load_sound(name):
    path = os.path.join(os.path.dirname(__file__), f"{name}.wav")
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    # Fallback: generate a short beep using pygame's Sound array (silence) to avoid errors
    return None

# Load sounds (optional)
EAT_SOUND = load_sound('eat')
DEATH_SOUND = load_sound('death')
START_SOUND = load_sound('start')