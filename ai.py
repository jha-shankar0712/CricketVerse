"""
ai.py
-----
Cricket intelligence engine: AI bowling selection (line, length, variation),
AI batting shot selection and timing accuracy scaled across Easy, Medium,
Hard, and Expert difficulty levels.
"""

import random
from constants import (
    DIFF_EASY, DIFF_MEDIUM, DIFF_HARD, DIFF_EXPERT,
    DELIVERY_FAST, DELIVERY_MEDIUM, DELIVERY_SPIN,
    LENGTH_YORKER, LENGTH_FULL, LENGTH_GOOD, LENGTH_SHORT,
    SHOT_DEFENSIVE, SHOT_STRAIGHT_DRIVE, SHOT_COVER_DRIVE,
    SHOT_PULL, SHOT_SWEEP, SHOT_CUT, SHOT_LOFTED,
    PITCH_X, TIMING_PERFECT, TIMING_GOOD, TIMING_EARLY, TIMING_LATE, TIMING_EDGE, TIMING_MISS
)

class CricketAI:
    def __init__(self, difficulty=DIFF_MEDIUM):
        self.difficulty = difficulty

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def choose_bowling_delivery(self, bowler, match_state):
        """Chooses length, type, target line and speed for AI bowler."""
        # Bowling type based on bowler's role
        if "Spin" in bowler.role or bowler.bowl_skill > 88 and bowler.name in ("K. Yadav", "A. Zampa", "A. Rashid", "M. Santner"):
            del_type = DELIVERY_SPIN
            speed = random.uniform(84.0, 98.0)
        elif bowler.bowl_skill > 85:
            del_type = DELIVERY_FAST
            speed = random.uniform(138.0, 150.0)
        else:
            del_type = DELIVERY_MEDIUM
            speed = random.uniform(118.0, 134.0)

        # Length choice based on match situation and difficulty
        if self.difficulty in (DIFF_HARD, DIFF_EXPERT):
            # Death overs or tight match -> bowl yorkers and bouncers
            overs_left = match_state["max_overs"] - match_state["overs"]
            if overs_left <= 2 and random.random() < 0.45:
                length = LENGTH_YORKER
            else:
                length = random.choice([LENGTH_GOOD, LENGTH_FULL, LENGTH_SHORT, LENGTH_YORKER])
        else:
            length = random.choice([LENGTH_GOOD, LENGTH_FULL, LENGTH_SHORT])

        # Target X on pitch (stumps around PITCH_X)
        if self.difficulty == DIFF_EXPERT:
            target_x = PITCH_X + random.uniform(-14, 14)
            swing = random.uniform(-2.5, 2.5)
        elif self.difficulty == DIFF_HARD:
            target_x = PITCH_X + random.uniform(-22, 22)
            swing = random.uniform(-1.8, 1.8)
        else:
            target_x = PITCH_X + random.uniform(-34, 34)
            swing = random.uniform(-1.0, 1.0)

        return {
            "delivery_type": del_type,
            "length": length,
            "target_x": target_x,
            "speed": speed,
            "swing": swing
        }

    def choose_batting_shot(self, batsman, ball_info, match_state):
        """AI batsman selects appropriate shot and evaluates hit timing."""
        target = match_state.get("target")
        runs = match_state.get("runs", 0)
        overs = match_state.get("overs", 0)
        balls = match_state.get("balls_in_over", 0)
        max_overs = match_state.get("max_overs", 5)

        aggressive = False
        if target is not None:
            needed = target - runs
            rem_balls = (max_overs * 6) - (overs * 6 + balls)
            rrr = (needed / (rem_balls / 6.0)) if rem_balls > 0 else 6.0
            if rrr > 8.0:
                aggressive = True

        # Shot selection
        if aggressive or random.random() < 0.25:
            shots = [SHOT_LOFTED, SHOT_PULL, SHOT_STRAIGHT_DRIVE, SHOT_COVER_DRIVE]
        else:
            shots = [SHOT_STRAIGHT_DRIVE, SHOT_COVER_DRIVE, SHOT_DEFENSIVE, SHOT_CUT, SHOT_SWEEP]

        chosen_shot = random.choice(shots)

        # Timing quality probability based on AI difficulty & batsman skill
        skill_boost = (batsman.bat_skill - 80) / 100.0  # -0.4 to +0.15

        if self.difficulty == DIFF_EXPERT:
            weights = [0.45 + skill_boost, 0.40, 0.08, 0.04, 0.03]  # Perfect, Good, Early/Late, Edge, Miss
        elif self.difficulty == DIFF_HARD:
            weights = [0.35 + skill_boost, 0.42, 0.12, 0.07, 0.04]
        elif self.difficulty == DIFF_MEDIUM:
            weights = [0.22, 0.45, 0.18, 0.10, 0.05]
        else:  # Easy
            weights = [0.12, 0.38, 0.25, 0.15, 0.10]

        # Normalize weights
        total = sum(max(0.01, w) for w in weights)
        probs = [max(0.01, w) / total for w in weights]

        outcome_pool = [TIMING_PERFECT, TIMING_GOOD, TIMING_EARLY, TIMING_EDGE, TIMING_MISS]
        chosen_timing = random.choices(outcome_pool, weights=probs)[0]

        return chosen_shot, chosen_timing
