"""
Space Shuttle Endeavor
Developed by Joshua

Description:
    Space Shuttle Endeavor is a Pygame-based game where players control a space shuttle
    navigating through space, avoiding obstacles, and collecting points.

Controls:
    - Use arrow keys (up, down, left, right) to navigate the space shuttle.
    - Press the space bar to shoot projectiles to destroy obstacles.

Features:
    - Realistic space shuttle movement simulation.
    - Dynamic obstacle generation for challenging gameplay.
    - Score tracking and display.
    - Sound effects and background music to enhance immersion.

Dependencies:
    - Python 3.x
    - Pygame library (version X.X.X or later)

Instru  ctions:
    1. Install Python from https://www.python.org/downloads/.
    2. Install Pygame using pip install pygame.
    3. Run this script to start the game.

Usage:
    $ python shuttle.py

Credits:
    - Joshua Mistal: Lead Developer
    - Mark Brin: Sprites, Presentation and Artwork
    - Jomari Raphael: Narrator
    - Ralph Daniel: Scriptwriter, Story
"""

import sys
import pygame as pg
import data

if __name__ == "__main__":
    data.main()
    pg.quit()
    sys.exit()