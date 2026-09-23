"""
physics.py
----------
Cricket ball flight physics, bounce calculations, shot outcome resolution,
and fielder catch evaluations.
"""

import math
import random
from constants import (
    PITCH_X, PITCH_TOP_Y, PITCH_BOTTOM_Y,
    GROUND_CENTER, GROUND_RADIUS_X, GROUND_RADIUS_Y,
    TIMING_PERFECT, TIMING_GOOD, TIMING_EARLY, TIMING_LATE, TIMING_EDGE, TIMING_MISS,
    SHOT_DEFENSIVE, SHOT_STRAIGHT_DRIVE, SHOT_COVER_DRIVE, SHOT_PULL,
    SHOT_SWEEP, SHOT_CUT, SHOT_LOFTED
)

class PhysicsEngine:
    @staticmethod
    def calculate_shot_outcome(shot_type, timing_quality, batsman_pos, ball_speed, batsman_skill=80):
        """
        Determines the hit angle, initial speed, loft factor, and outcome
        based on the chosen shot type and timing quality.
        """
        if timing_quality == TIMING_MISS:
            return None

        # Shot directional angles in radians (0 is right, pi/2 is down, -pi/2 is straight up toward bowler)
        # In screen coords: Straight drive goes towards top/straight (-pi/2)
        base_angles = {
            SHOT_DEFENSIVE: math.radians(90),       # gentle drop near feet
            SHOT_STRAIGHT_DRIVE: math.radians(-90), # straight back past bowler
            SHOT_COVER_DRIVE: math.radians(-130),   # through off-side cover
            SHOT_PULL: math.radians(20),            # through mid-wicket / leg side
            SHOT_SWEEP: math.radians(45),           # fine leg / backward square
            SHOT_CUT: math.radians(-170),           # through point / third man
            SHOT_LOFTED: math.radians(-90)          # lofted over bowler/mid-on
        }

        angle = base_angles.get(shot_type, math.radians(-90))
        # Add small natural variance
        angle += random.uniform(-0.12, 0.12)

        # Base power based on shot type
        power_map = {
            SHOT_DEFENSIVE: 0.15,
            SHOT_STRAIGHT_DRIVE: 0.85,
            SHOT_COVER_DRIVE: 0.88,
            SHOT_PULL: 0.92,
            SHOT_SWEEP: 0.78,
            SHOT_CUT: 0.82,
            SHOT_LOFTED: 1.05
        }
        power = power_map.get(shot_type, 0.8)

        # Timing multiplier
        timing_mult = {
            TIMING_PERFECT: 1.25,
            TIMING_GOOD: 1.0,
            TIMING_EARLY: 0.65,
            TIMING_LATE: 0.60,
            TIMING_EDGE: 0.35
        }.get(timing_quality, 0.7)

        skill_mult = (batsman_skill / 80.0)
        speed = 22.0 * power * timing_mult * skill_mult

        # Loft (is ball in air?)
        is_aerial = False
        loft_chance = 0.0
        if shot_type == SHOT_LOFTED:
            is_aerial = True
            loft_chance = 0.95
        elif shot_type == SHOT_DEFENSIVE:
            is_aerial = False
        else:
            if timing_quality in (TIMING_EARLY, TIMING_LATE, TIMING_EDGE):
                loft_chance = 0.45
            else:
                loft_chance = 0.15

        if random.random() < loft_chance:
            is_aerial = True

        return {
            "vx": speed * math.cos(angle),
            "vy": speed * math.sin(angle),
            "is_aerial": is_aerial,
            "power": power * timing_mult,
            "timing": timing_quality,
            "angle": angle
        }

    @staticmethod
    def is_inside_boundary(pos):
        """Checks whether the ball has crossed the boundary ellipse."""
        dx = (pos[0] - GROUND_CENTER[0]) / GROUND_RADIUS_X
        dy = (pos[1] - GROUND_CENTER[1]) / GROUND_RADIUS_Y
        return (dx * dx + dy * dy) <= 1.0
