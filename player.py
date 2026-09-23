"""
player.py
---------
Player base class, batsman, bowler, and fielder agents with chase physics.
"""

import pygame
import math
import random
from constants import (
    PITCH_X, PITCH_TOP_Y, PITCH_BOTTOM_Y,
    COLOR_TEXT_LIGHT, GROUND_CENTER
)

class Player:
    def __init__(self, name, role, bat_skill=80, bowl_skill=50):
        self.name = name
        self.role = role
        self.bat_skill = bat_skill
        self.bowl_skill = bowl_skill
        # Match statistics
        self.runs = 0
        self.balls = 0
        self.fours = 0
        self.sixes = 0
        self.is_out = False
        self.dismissal = "not out"
        # Bowling stats
        self.overs_bowled = 0
        self.balls_in_over = 0
        self.maidens = 0
        self.runs_conceded = 0
        self.wickets_taken = 0
        self.extras_conceded = 0

class Fielder:
    """Fielder entity stationed on ground with dynamic ball-chase & throw."""
    def __init__(self, name, base_x, base_y, primary_color=(20, 100, 220)):
        self.name = name
        self.base_x = float(base_x)
        self.base_y = float(base_y)
        self.x = float(base_x)
        self.y = float(base_y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 3.6
        self.primary_color = primary_color
        self.has_ball = False
        self.dive_timer = 0

    def reset_position(self):
        self.x = self.base_x
        self.y = self.base_y
        self.vx = 0
        self.vy = 0
        self.has_ball = False
        self.dive_timer = 0

    def update(self, ball):
        if ball.state == "hit":
            # Chase the ball
            dx = ball.x - self.x
            dy = ball.y - self.y
            dist = math.hypot(dx, dy)
            if dist > 8:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
                self.x += self.vx
                self.y += self.vy
            else:
                # Reached ball
                if not ball.is_aerial or ball.z < 25:
                    self.has_ball = True
                    ball.vx *= 0.2
                    ball.vy *= 0.2
        elif ball.state in ("bowled", "in_hand", "dead"):
            # Return towards base position gradually
            dx = self.base_x - self.x
            dy = self.base_y - self.y
            if math.hypot(dx, dy) > 3:
                self.x += dx * 0.05
                self.y += dy * 0.05

    def draw(self, surface, camera=None):
        pos = (int(self.x), int(self.y))
        if camera:
            pos = camera.apply(pos)

        # Shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 80), (pos[0] - 6, pos[1] + 6, 12, 5))
        # Body (Jersey)
        pygame.draw.rect(surface, self.primary_color, (pos[0] - 5, pos[1] - 12, 10, 14), border_radius=2)
        # Head
        pygame.draw.circle(surface, (235, 195, 160), (pos[0], pos[1] - 17), 5)
        # Cap
        pygame.draw.arc(surface, self.primary_color, (pos[0] - 5, pos[1] - 22, 10, 8), 0, math.pi, 2)
