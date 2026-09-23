"""
stadium.py
----------
Procedural rendering of the stadium, turf grass with mowing patterns,
pitch markings, boundary ropes, stumps with flying bails, and animated crowd.
"""

import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PITCH_X, PITCH_TOP_Y, PITCH_BOTTOM_Y,
    PITCH_WIDTH, GROUND_CENTER, GROUND_RADIUS_X, GROUND_RADIUS_Y,
    INNER_CIRCLE_RADIUS_X, INNER_CIRCLE_RADIUS_Y,
    COLOR_GRASS_LIGHT, COLOR_GRASS_DARK, COLOR_PITCH, COLOR_PITCH_LINES,
    COLOR_STUMPS, COLOR_BAILS, COLOR_BOUNDARY_ROPE
)

class Stadium:
    def __init__(self, stadium_key="MCG"):
        self.key = stadium_key
        self.crowd_cheering = False
        self.cheer_timer = 0
        self.bails_dislodged = False
        self.bails_pos = [(PITCH_X - 4, PITCH_BOTTOM_Y + 12), (PITCH_X + 4, PITCH_BOTTOM_Y + 12)]
        self.bails_vel = [(0, 0), (0, 0)]
        self._init_crowd()

    def _init_crowd(self):
        """Generates random crowd spectators in stadium stands."""
        self.spectators = []
        colors = [(200, 50, 50), (50, 100, 220), (240, 200, 40), (240, 240, 240), (50, 180, 80)]
        # Outer ring stands
        for angle_deg in range(0, 360, 4):
            rad = math.radians(angle_deg)
            for r_offset in [1.06, 1.10, 1.14]:
                cx = GROUND_CENTER[0] + math.cos(rad) * (GROUND_RADIUS_X * r_offset)
                cy = GROUND_CENTER[1] + math.sin(rad) * (GROUND_RADIUS_Y * r_offset)
                color = random.choice(colors)
                self.spectators.append({"pos": (cx, cy), "color": color, "phase": random.random() * math.pi * 2})

    def dislodge_bails(self):
        self.bails_dislodged = True
        self.bails_vel = [
            (random.uniform(-4, -1), random.uniform(-6, -3)),
            (random.uniform(1, 4), random.uniform(-6, -3))
        ]

    def reset_stumps(self):
        self.bails_dislodged = False
        self.bails_pos = [(PITCH_X - 4, PITCH_BOTTOM_Y + 12), (PITCH_X + 4, PITCH_BOTTOM_Y + 12)]
        self.bails_vel = [(0, 0), (0, 0)]

    def update(self):
        if self.bails_dislodged:
            new_pos = []
            for i in range(2):
                x, y = self.bails_pos[i]
                vx, vy = self.bails_vel[i]
                vy += 0.4  # gravity
                new_pos.append((x + vx, y + vy))
                self.bails_vel[i] = (vx * 0.95, vy)
            self.bails_pos = new_pos

        if self.cheer_timer > 0:
            self.cheer_timer -= 1
        else:
            self.crowd_cheering = False

    def trigger_cheer(self, duration=90):
        self.crowd_cheering = True
        self.cheer_timer = duration

    def draw(self, surface, camera=None):
        # 1. Ground grass mowing concentric stripes
        for r_x, r_y in zip(range(GROUND_RADIUS_X, 0, -50), range(GROUND_RADIUS_Y, 0, -28)):
            color = COLOR_GRASS_LIGHT if (r_x // 50) % 2 == 0 else COLOR_GRASS_DARK
            rect = (GROUND_CENTER[0] - r_x, GROUND_CENTER[1] - r_y, r_x * 2, r_y * 2)
            if camera:
                rect = (rect[0] + camera.offset_x, rect[1] + camera.offset_y, rect[2], rect[3])
            pygame.draw.ellipse(surface, color, rect)

        # 2. 30-yard inner circle (dashed/dotted)
        circle_rect = (
            GROUND_CENTER[0] - INNER_CIRCLE_RADIUS_X,
            GROUND_CENTER[1] - INNER_CIRCLE_RADIUS_Y,
            INNER_CIRCLE_RADIUS_X * 2,
            INNER_CIRCLE_RADIUS_Y * 2
        )
        if camera:
            circle_rect = (circle_rect[0] + camera.offset_x, circle_rect[1] + camera.offset_y, circle_rect[2], circle_rect[3])
        pygame.draw.ellipse(surface, (255, 255, 255, 140), circle_rect, 2)

        # 3. Boundary Rope
        boundary_rect = (
            GROUND_CENTER[0] - GROUND_RADIUS_X,
            GROUND_CENTER[1] - GROUND_RADIUS_Y,
            GROUND_RADIUS_X * 2,
            GROUND_RADIUS_Y * 2
        )
        if camera:
            boundary_rect = (boundary_rect[0] + camera.offset_x, boundary_rect[1] + camera.offset_y, boundary_rect[2], boundary_rect[3])
        pygame.draw.ellipse(surface, COLOR_BOUNDARY_ROPE, boundary_rect, 4)

        # 4. Pitch strip
        pitch_rect = (
            PITCH_X - PITCH_WIDTH // 2,
            PITCH_TOP_Y,
            PITCH_WIDTH,
            PITCH_BOTTOM_Y - PITCH_TOP_Y + 30
        )
        if camera:
            pitch_rect = (pitch_rect[0] + camera.offset_x, pitch_rect[1] + camera.offset_y, pitch_rect[2], pitch_rect[3])
        pygame.draw.rect(surface, COLOR_PITCH, pitch_rect, border_radius=4)

        # 5. Pitch Crease Markings (Bowler end & Batsman end)
        bx = PITCH_X + (camera.offset_x if camera else 0)
        # Batsman popping crease
        bat_y = PITCH_BOTTOM_Y + (camera.offset_y if camera else 0)
        pygame.draw.line(surface, COLOR_PITCH_LINES, (bx - 40, bat_y), (bx + 40, bat_y), 2)
        # Bowler popping crease
        bowl_y = PITCH_TOP_Y + 15 + (camera.offset_y if camera else 0)
        pygame.draw.line(surface, COLOR_PITCH_LINES, (bx - 36, bowl_y), (bx + 36, bowl_y), 2)

        # 6. Stumps and Bails
        self._draw_stumps(surface, (PITCH_X, PITCH_TOP_Y + 10), camera)
        self._draw_stumps(surface, (PITCH_X, PITCH_BOTTOM_Y + 16), camera)

        # 7. Animated crowd in stands
        time_ms = pygame.time.get_ticks()
        for s in self.spectators:
            p = s["pos"]
            if camera:
                p = camera.apply(p)
            bob = 0
            if self.crowd_cheering:
                bob = int(math.sin(time_ms * 0.01 + s["phase"]) * 4)
            pygame.draw.circle(surface, s["color"], (int(p[0]), int(p[1] + bob)), 3)

    def _draw_stumps(self, surface, base_pos, camera=None):
        pos = base_pos
        if camera:
            pos = camera.apply(pos)

        # 3 wooden stumps
        stump_w = 2
        stump_h = 16
        for offset_x in (-6, 0, 6):
            pygame.draw.rect(surface, COLOR_STUMPS, (pos[0] + offset_x - 1, pos[1] - stump_h, stump_w, stump_h))

        # Bails on top
        if not self.bails_dislodged or base_pos[1] < 300:
            pygame.draw.line(surface, COLOR_BAILS, (pos[0] - 7, pos[1] - stump_h), (pos[0] + 7, pos[1] - stump_h), 2)
        else:
            # Draw dislodged bails
            for bp in self.bails_pos:
                p = bp
                if camera:
                    p = camera.apply(bp)
                pygame.draw.circle(surface, COLOR_BAILS, (int(p[0]), int(p[1])), 2)
