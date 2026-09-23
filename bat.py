"""
bat.py
------
Batsman stance, swing animation, and timing window detector.
"""

import pygame
import math
from constants import (
    PITCH_X, PITCH_BOTTOM_Y, TIMING_PERFECT, TIMING_GOOD,
    TIMING_EARLY, TIMING_LATE, TIMING_EDGE, TIMING_MISS,
    SHOT_NAMES
)

class Bat:
    def __init__(self):
        self.crease_y = PITCH_BOTTOM_Y
        self.swinging = False
        self.swing_progress = 0.0
        self.current_shot = None
        self.swing_angle = 0.0

    def start_swing(self, shot_type):
        self.swinging = True
        self.swing_progress = 0.0
        self.current_shot = shot_type

    def update(self):
        if self.swinging:
            self.swing_progress += 0.12
            if self.swing_progress >= 1.0:
                self.swinging = False
                self.swing_progress = 0.0

    def evaluate_timing(self, ball_y, ball_speed_kmh):
        """
        Calculates precision timing based on the distance between the ball and crease.
        """
        diff = ball_y - (self.crease_y - 12)
        # diff < 0 means ball is still approaching (early)
        # diff > 0 means ball has passed crease (late)

        abs_diff = abs(diff)
        if abs_diff <= 14:
            return TIMING_PERFECT
        elif abs_diff <= 32:
            return TIMING_GOOD
        elif diff < -32 and diff >= -60:
            return TIMING_EARLY
        elif diff > 32 and diff <= 65:
            return TIMING_LATE
        elif abs_diff <= 90:
            return TIMING_EDGE
        else:
            return TIMING_MISS

    def draw(self, surface, batsman_x, batsman_y, camera=None):
        pos = (batsman_x, batsman_y)
        if camera:
            pos = camera.apply(pos)

        # Bat dimensions
        bat_len = 28
        bat_width = 5

        angle = 15
        if self.swinging:
            # Swing arc from -45 to 65 degrees
            angle = -45 + math.sin(self.swing_progress * math.pi) * 110

        rad = math.radians(angle)
        end_x = pos[0] + math.sin(rad) * bat_len
        end_y = pos[1] + math.cos(rad) * bat_len

        # Bat blade
        pygame.draw.line(surface, (190, 140, 80), (pos[0] + 5, pos[1]), (int(end_x), int(end_y)), bat_width)
        # Bat grip
        pygame.draw.line(surface, (255, 255, 255), (pos[0] + 5, pos[1]), (pos[0] + 3, pos[1] - 8), 3)
