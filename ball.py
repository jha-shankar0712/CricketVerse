"""
ball.py
-------
Ball entity with 3D flight trajectory, pitch bounce, ground friction,
visual trail, and shadow rendering.
"""

import pygame
import math
from constants import (
    COLOR_BALL_RED, COLOR_BALL_SEAM, PITCH_X, PITCH_TOP_Y, PITCH_BOTTOM_Y
)
from physics import PhysicsEngine

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = float(PITCH_X)
        self.y = float(PITCH_TOP_Y)
        self.z = 24.0      # Height above ground in virtual pixels
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.speed_kmh = 135.0
        self.state = "in_hand"  # in_hand, bowled, pitched, hit, fielded, dead
        self.has_bounced = False
        self.bounce_y = 380.0
        self.is_aerial = False
        self.trail = []
        self.max_trail = 10
        self.radius = 6

    def deliver(self, target_x, length_type, delivery_type, speed_kmh=135.0, swing=0.0):
        self.reset()
        self.speed_kmh = speed_kmh
        self.state = "bowled"
        self.x = float(PITCH_X + (swing * 5))
        self.y = float(PITCH_TOP_Y)
        self.z = 24.0

        # Pitch bounce location based on length
        if length_type == "Yorker":
            self.bounce_y = PITCH_BOTTOM_Y - 25
        elif length_type == "Full Length":
            self.bounce_y = PITCH_BOTTOM_Y - 75
        elif length_type == "Good Length":
            self.bounce_y = PITCH_BOTTOM_Y - 140
        else:  # Bouncer / Short
            self.bounce_y = PITCH_BOTTOM_Y - 220

        # Calculate forward speed
        fps_speed = (speed_kmh / 140.0) * 11.0
        dist_y = self.bounce_y - self.y
        time_to_bounce = dist_y / fps_speed if fps_speed > 0 else 30.0

        self.vy = fps_speed
        self.vx = (target_x - self.x) / time_to_bounce if time_to_bounce > 0 else 0.0
        self.vz = -self.z / time_to_bounce if time_to_bounce > 0 else -0.8
        self.is_aerial = True

    def hit(self, shot_data):
        self.state = "hit"
        self.vx = shot_data["vx"]
        self.vy = shot_data["vy"]
        self.is_aerial = shot_data["is_aerial"]
        if self.is_aerial:
            self.vz = shot_data["power"] * 8.0
        else:
            self.vz = 0.0
            self.z = 0.0

    def update(self, stadium_bounce=1.0):
        # Update trail
        if self.state in ("bowled", "hit"):
            self.trail.append((int(self.x), int(self.y - self.z)))
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)

        if self.state == "bowled":
            self.x += self.vx
            self.y += self.vy
            self.z += self.vz

            # Pitch bounce
            if not self.has_bounced and self.y >= self.bounce_y:
                self.has_bounced = True
                self.state = "pitched"
                self.z = 0.0
                # Rebound upwards
                self.vz = abs(self.vy) * 0.45 * stadium_bounce
                # Gravity kicks in
                self.gravity = -0.42

        elif self.state == "pitched":
            self.x += self.vx
            self.y += self.vy
            self.z += self.vz
            self.vz -= 0.38  # gravity
            if self.z <= 0 and self.y > self.bounce_y + 10:
                self.z = 0

        elif self.state == "hit":
            self.x += self.vx
            self.y += self.vy
            if self.is_aerial:
                self.z += self.vz
                self.vz -= 0.40  # gravity
                if self.z <= 0:
                    self.z = 0
                    self.is_aerial = False
                    self.vz = 0
            else:
                self.z = 0

            # Ground friction
            friction = 0.965 if self.z <= 0 else 0.99
            self.vx *= friction
            self.vy *= friction

            if math.hypot(self.vx, self.vy) < 0.2:
                self.vx = 0
                self.vy = 0
                self.state = "dead"

    def draw(self, surface, camera=None):
        if self.state == "in_hand":
            return

        # Draw motion trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                p1 = self.trail[i]
                p2 = self.trail[i + 1]
                if camera:
                    p1 = camera.apply(p1)
                    p2 = camera.apply(p2)
                alpha = int((i / len(self.trail)) * 140)
                width = max(1, int((i / len(self.trail)) * (self.radius - 1)))
                pygame.draw.line(surface, (255, 100, 100, alpha), p1, p2, width)

        # Ball shadow on ground
        shadow_pos = (int(self.x), int(self.y))
        if camera:
            shadow_pos = camera.apply(shadow_pos)
        shadow_r = max(2, int(self.radius * (1.0 - min(self.z, 150) / 200.0)))
        shadow_surf = pygame.Surface((shadow_r * 2 + 4, shadow_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 70), (2, 2, shadow_r * 2, shadow_r))
        surface.blit(shadow_surf, (shadow_pos[0] - shadow_r, shadow_pos[1] - shadow_r // 2))

        # Ball sphere in air
        render_pos = (int(self.x), int(self.y - self.z))
        if camera:
            render_pos = camera.apply(render_pos)

        r = max(3, int(self.radius + min(self.z * 0.03, 5)))
        pygame.draw.circle(surface, COLOR_BALL_RED, render_pos, r)
        # Highlight reflection
        pygame.draw.circle(surface, (255, 180, 180), (render_pos[0] - r // 3, render_pos[1] - r // 3), max(1, r // 3))
        # Seam line
        pygame.draw.line(surface, COLOR_BALL_SEAM, (render_pos[0] - r + 1, render_pos[1]), (render_pos[0] + r - 1, render_pos[1]), 1)
