"""
umpire.py
---------
Cricket rules referee: wide, no-ball, out decisions, and visual signals.
"""

import pygame
import math
from constants import (
    PITCH_X, PITCH_TOP_Y, COLOR_TEXT_LIGHT,
    COLOR_WARNING, COLOR_DANGER
)

class Umpire:
    def __init__(self):
        self.signal = None      # "OUT", "WIDE", "NO_BALL", "FOUR", "SIX"
        self.signal_timer = 0
        self.x = PITCH_X - 25
        self.y = PITCH_TOP_Y + 5

    def check_delivery(self, ball):
        """Checks for Wide ball outside tramline markings."""
        # Crease width is 90; wide if ball crosses more than 36px off center
        if abs(ball.x - PITCH_X) > 38 and ball.y >= PITCH_TOP_Y + 100:
            return "WIDE"
        return "FAIR"

    def set_signal(self, signal, duration=80):
        self.signal = signal
        self.signal_timer = duration

    def update(self):
        if self.signal_timer > 0:
            self.signal_timer -= 1
        else:
            self.signal = None

    def draw(self, surface, camera=None):
        pos = (int(self.x), int(self.y))
        if camera:
            pos = camera.apply(pos)

        # Umpire body (White coat + black trousers)
        pygame.draw.rect(surface, (20, 20, 20), (pos[0] - 4, pos[1] + 5, 8, 12))  # trousers
        pygame.draw.rect(surface, (240, 240, 240), (pos[0] - 6, pos[1] - 8, 12, 14), border_radius=2)  # coat
        pygame.draw.circle(surface, (230, 190, 160), (pos[0], pos[1] - 13), 5)  # head
        pygame.draw.ellipse(surface, (220, 220, 220), (pos[0] - 7, pos[1] - 18, 14, 6))  # white sunhat

        # Signal gesture
        if self.signal == "OUT":
            # Right index finger raised high
            pygame.draw.line(surface, (240, 240, 240), (pos[0] + 5, pos[1] - 5), (pos[0] + 7, pos[1] - 22), 2)
        elif self.signal == "WIDE":
            # Both arms outstretched horizontally
            pygame.draw.line(surface, (240, 240, 240), (pos[0] - 14, pos[1] - 2), (pos[0] + 14, pos[1] - 2), 2)
        elif self.signal == "NO_BALL":
            # Right arm raised horizontal
            pygame.draw.line(surface, (240, 240, 240), (pos[0], pos[1] - 2), (pos[0] + 15, pos[1] - 2), 2)
        elif self.signal == "SIX":
            # Both arms raised high above head
            pygame.draw.line(surface, (240, 240, 240), (pos[0] - 6, pos[1] - 5), (pos[0] - 10, pos[1] - 24), 2)
            pygame.draw.line(surface, (240, 240, 240), (pos[0] + 6, pos[1] - 5), (pos[0] + 10, pos[1] - 24), 2)
