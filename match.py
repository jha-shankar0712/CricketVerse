"""
match.py
--------
Ball-by-ball cricket match engine, batting/bowling loops, fielder chase,
wicket/boundary detection, commentary, and innings transitions.
"""

import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, PITCH_X, PITCH_TOP_Y, PITCH_BOTTOM_Y,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_SUCCESS, COLOR_DANGER, COLOR_TEXT_LIGHT,
    COLOR_PANEL_SOLID, TIMING_PERFECT, TIMING_GOOD, TIMING_EARLY, TIMING_LATE,
    TIMING_EDGE, TIMING_MISS, SHOT_NAMES, SHOT_DEFENSIVE, SHOT_STRAIGHT_DRIVE,
    SHOT_COVER_DRIVE, SHOT_PULL, SHOT_SWEEP, SHOT_CUT, SHOT_LOFTED,
    DELIVERY_FAST, DELIVERY_MEDIUM, DELIVERY_SPIN,
    TEAMS_DATA, STADIUMS
)
from player import Player, Fielder
from ball import Ball
from bat import Bat
from stadium import Stadium
from umpire import Umpire
from scoreboard import Scoreboard
from ai import CricketAI
from physics import PhysicsEngine
from utils import get_font, draw_rounded_rect, draw_glass_panel

COMMENTARY_FOURS = [
    "Cracking shot! Pierces the gap for FOUR!",
    "Glorious stroke! Races away to the fence!",
    "Exquisite timing! Finds the boundary rope with style!",
    "Slammed through the covers! Pure elegance for four!"
]

COMMENTARY_SIXES = [
    "INTO THE ORBIT! That is a MASSIVE SIX!",
    "High, handsome, and OUT OF THE GROUND! What a hit!",
    "Launched into the crowd! Stand and deliver for SIX!",
    "Sweet sound off the willow! It clears the rope with ease!"
]

COMMENTARY_WICKETS = [
    "OUT! Clean bowled, middle stump uprooted!",
    "EDGED AND TAKEN! A huge wicket falls!",
    "GONE! Splendid catch taken in the deep!",
    "Timber! The batsman has to make the long walk back!"
]

class Match:
    def __init__(self, player_team="IND", opponent_team="AUS", max_overs=5,
                 difficulty="Medium", stadium="MCG", user_bats_first=True,
                 sound=None, settings=None, camera=None, particles=None,
                 is_practice=False, on_finish=None):
        self.sound = sound
        self.settings = settings
        self.camera = camera
        self.particles = particles
        self.on_finish = on_finish
        self.is_practice = is_practice

        self.player_team_key = player_team
        self.opponent_team_key = opponent_team
        self.max_overs = max_overs
        self.difficulty = difficulty
        self.stadium_key = stadium
        self.user_bats_first = user_bats_first

        self.stadium = Stadium(stadium)
        self.umpire = Umpire()
        self.scoreboard = Scoreboard()
        self.ai = CricketAI(difficulty)
        self.ball = Ball()
        self.bat = Bat()

        # Build player squads
        self.p1_squad = [Player(p["name"], p["role"], p["bat_skill"], p["bowl_skill"])
                         for p in TEAMS_DATA[player_team]["roster"]]
        self.p2_squad = [Player(p["name"], p["role"], p["bat_skill"], p["bowl_skill"])
                         for p in TEAMS_DATA[opponent_team]["roster"]]

        # Innings tracking
        self.current_innings = 1
        self.innings1_data = None
        self.target = None

        # Fielders
        self.fielders = self._create_fielders()

        # Bowling meter for human bowling
        self.meter_val = 0.0
        self.meter_dir = 1
        self.meter_speed = 0.045
        self.selected_delivery_type = DELIVERY_FAST
        self.bowl_target_x = PITCH_X

        # Batsman position
        self.batsman_x = PITCH_X
        self.batsman_y = PITCH_BOTTOM_Y

        # Match State
        self.state = "READY_TO_BOWL"
        self.state_timer = 0
        self.active_shot = None
        self.timing_feedback = None
        self.commentary_line = "Welcome to the match! Ready for the first delivery."
        self.show_innings_break = False

        self._setup_innings()

    def _create_fielders(self):
        color = TEAMS_DATA[self.opponent_team_key]["primary_color"]
        field_positions = [
            ("Keeper", PITCH_X, PITCH_BOTTOM_Y + 45),
            ("Slip 1", PITCH_X - 35, PITCH_BOTTOM_Y + 40),
            ("Point", PITCH_X - 160, PITCH_BOTTOM_Y - 20),
            ("Cover", PITCH_X - 180, PITCH_BOTTOM_Y - 120),
            ("Mid-Off", PITCH_X - 90, PITCH_TOP_Y + 50),
            ("Mid-On", PITCH_X + 90, PITCH_TOP_Y + 50),
            ("Mid-Wicket", PITCH_X + 180, PITCH_BOTTOM_Y - 100),
            ("Square Leg", PITCH_X + 160, PITCH_BOTTOM_Y + 10),
            ("Fine Leg", PITCH_X + 220, PITCH_BOTTOM_Y + 80),
            ("Deep Extra Cover", PITCH_X - 280, PITCH_BOTTOM_Y - 140)
        ]
        return [Fielder(name, fx, fy, primary_color=color) for name, fx, fy in field_positions]

    def _setup_innings(self):
        if self.current_innings == 1:
            if self.user_bats_first:
                self.batting_team_key = self.player_team_key
                self.bowling_team_key = self.opponent_team_key
                self.batting_squad = self.p1_squad
                self.bowling_squad = self.p2_squad
                self.user_is_batting = True
            else:
                self.batting_team_key = self.opponent_team_key
                self.bowling_team_key = self.player_team_key
                self.batting_squad = self.p2_squad
                self.bowling_squad = self.p1_squad
                self.user_is_batting = False
        else:
            # 2nd innings swap
            if self.user_bats_first:
                self.batting_team_key = self.opponent_team_key
                self.bowling_team_key = self.player_team_key
                self.batting_squad = self.p2_squad
                self.bowling_squad = self.p1_squad
                self.user_is_batting = False
            else:
                self.batting_team_key = self.player_team_key
                self.bowling_team_key = self.opponent_team_key
                self.batting_squad = self.p1_squad
                self.bowling_squad = self.p2_squad
                self.user_is_batting = True

        self.runs = 0
        self.wickets = 0
        self.overs = 0
        self.balls_in_over = 0
        self.striker_idx = 0
        self.non_striker_idx = 1
        self.bowler_idx = 8  # Bumrah/Starc typical bowler
        self.striker = self.batting_squad[self.striker_idx]
        self.non_striker = self.batting_squad[self.non_striker_idx]
        self.bowler = self.bowling_squad[self.bowler_idx]
        self.this_over_balls = []
        self.partnership_runs = 0
        self.partnership_balls = 0
        self.state = "READY_TO_BOWL"
        self.stadium.reset_stumps()

        # Update fielder jersey colors
        f_color = TEAMS_DATA[self.bowling_team_key]["primary_color"]
        for f in self.fielders:
            f.primary_color = f_color
            f.reset_position()

    def handle_event(self, event):
        if self.show_innings_break:
            if (event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN)) or                (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                self.show_innings_break = False
                self.current_innings = 2
                self._setup_innings()
            return

        # Toggle scorecard modal
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            self.scoreboard.show_full_scorecard = not self.scoreboard.show_full_scorecard
            return

        if self.scoreboard.show_full_scorecard:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.scoreboard.show_full_scorecard = False
            return

        # Batting inputs (when user is batting)
        if self.user_is_batting:
            if event.type == pygame.KEYDOWN:
                # Crease shuffling
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.batsman_x = max(PITCH_X - 32, self.batsman_x - 10)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.batsman_x = min(PITCH_X + 32, self.batsman_x + 10)

                # Shots 1-7
                shot_map = {
                    pygame.K_1: SHOT_DEFENSIVE,
                    pygame.K_2: SHOT_STRAIGHT_DRIVE,
                    pygame.K_3: SHOT_COVER_DRIVE,
                    pygame.K_4: SHOT_PULL,
                    pygame.K_5: SHOT_SWEEP,
                    pygame.K_6: SHOT_CUT,
                    pygame.K_7: SHOT_LOFTED
                }
                if event.key in shot_map and self.ball.state in ("bowled", "pitched"):
                    self._execute_bat_shot(shot_map[event.key])

        # Bowling inputs (when user is bowling)
        else:
            if self.state == "READY_TO_BOWL":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.selected_delivery_type = DELIVERY_FAST
                    elif event.key == pygame.K_2:
                        self.selected_delivery_type = DELIVERY_MEDIUM
                    elif event.key == pygame.K_3:
                        self.selected_delivery_type = DELIVERY_SPIN
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.bowl_target_x = max(PITCH_X - 36, self.bowl_target_x - 8)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.bowl_target_x = min(PITCH_X + 36, self.bowl_target_x + 8)
                    elif event.key == pygame.K_SPACE:
                        self._release_player_delivery()

    def _release_player_delivery(self):
        """Releases delivery based on player's timing on the accuracy meter."""
        # Accuracy is best when meter_val is near 0.5 (center)
        acc_diff = abs(self.meter_val - 0.5)
        speed = 142.0 if self.selected_delivery_type == DELIVERY_FAST else (128.0 if self.selected_delivery_type == DELIVERY_MEDIUM else 92.0)
        swing = (self.meter_val - 0.5) * 4.0

        length = "Good Length"
        if acc_diff < 0.12:
            length = "Good Length"
        elif self.meter_val > 0.7:
            length = "Bouncer / Short"
        else:
            length = "Full Length"

        self.ball.deliver(self.bowl_target_x, length, self.selected_delivery_type, speed, swing)
        self.state = "BALL_IN_AIR"
        if self.sound:
            self.sound.play("bounce")

    def _execute_bat_shot(self, shot_type):
        self.bat.start_swing(shot_type)
        timing = self.bat.evaluate_timing(self.ball.y, self.ball.speed_kmh)
        self.timing_feedback = timing

        if timing in (TIMING_PERFECT, TIMING_GOOD):
            if self.sound:
                self.sound.play("bat_solid")
        elif timing == TIMING_EDGE:
            if self.sound:
                self.sound.play("bat_edge")

        if self.particles:
            color = COLOR_SUCCESS if timing == TIMING_PERFECT else (COLOR_ACCENT if timing == TIMING_GOOD else COLOR_DANGER)
            self.particles.add_floating_text(self.batsman_x, self.batsman_y - 30, f"{timing}!", color=color, size=24)

        shot_result = PhysicsEngine.calculate_shot_outcome(
            shot_type, timing, (self.batsman_x, self.batsman_y), self.ball.speed_kmh, self.striker.bat_skill
        )

        if shot_result:
            self.ball.hit(shot_result)
            self.state = "BALL_IN_PLAY"
            self.active_shot = shot_result
        else:
            # Missed ball
            pass

    def update(self):
        if self.show_innings_break:
            return

        self.stadium.update()
        self.umpire.update()
        self.bat.update()

        # Update accuracy meter when user is bowling
        if not self.user_is_batting and self.state == "READY_TO_BOWL":
            self.meter_val += self.meter_dir * self.meter_speed
            if self.meter_val >= 1.0:
                self.meter_val = 1.0
                self.meter_dir = -1
            elif self.meter_val <= 0.0:
                self.meter_val = 0.0
                self.meter_dir = 1

        # AI Bowling Trigger
        if self.user_is_batting and self.state == "READY_TO_BOWL":
            self.state_timer += 1
            if self.state_timer > 50:
                self.state_timer = 0
                match_state = {"max_overs": self.max_overs, "overs": self.overs, "runs": self.runs, "target": self.target}
                deliv = self.ai.choose_bowling_delivery(self.bowler, match_state)
                self.ball.deliver(deliv["target_x"], deliv["length"], deliv["delivery_type"], deliv["speed"], deliv["swing"])
                self.state = "BALL_IN_AIR"
                if self.sound:
                    self.sound.play("bounce")

        # Ball in flight logic
        if self.state in ("BALL_IN_AIR", "BALL_IN_PLAY"):
            self.ball.update()

            # AI Batting Trigger (when AI is batting)
            if not self.user_is_batting and self.state == "BALL_IN_AIR":
                # AI swings when ball gets close to crease
                if self.ball.y >= PITCH_BOTTOM_Y - 40 and not self.bat.swinging:
                    match_state = {"max_overs": self.max_overs, "overs": self.overs, "balls_in_over": self.balls_in_over, "runs": self.runs, "target": self.target}
                    shot, timing = self.ai.choose_batting_shot(self.striker, self.ball, match_state)
                    self.bat.start_swing(shot)
                    self.timing_feedback = timing

                    if timing != TIMING_MISS:
                        if self.sound:
                            self.sound.play("bat_solid" if timing in (TIMING_PERFECT, TIMING_GOOD) else "bat_edge")
                        shot_res = PhysicsEngine.calculate_shot_outcome(shot, timing, (PITCH_X, PITCH_BOTTOM_Y), self.ball.speed_kmh, self.striker.bat_skill)
                        if shot_res:
                            self.ball.hit(shot_res)
                            self.state = "BALL_IN_PLAY"
                            if self.particles:
                                self.particles.add_floating_text(PITCH_X, PITCH_BOTTOM_Y - 30, f"{timing}!", size=22)

            # Check Bowled (ball passes crease unhit and strikes stumps)
            if self.state == "BALL_IN_AIR" and self.ball.y >= PITCH_BOTTOM_Y + 10:
                if abs(self.ball.x - PITCH_X) <= 12 and self.ball.z < 26:
                    # Clean bowled!
                    self._handle_dismissal("b " + self.bowler.name, is_bowled=True)
                    return
                elif self.ball.y >= PITCH_BOTTOM_Y + 45:
                    # Past keeper / dead ball
                    self._end_delivery(runs=0, ball_symbol=".")
                    return

            # Check Wide ball
            if self.state == "BALL_IN_AIR" and self.ball.y >= PITCH_BOTTOM_Y:
                if self.umpire.check_delivery(self.ball) == "WIDE":
                    self._handle_extra(extra_type="WIDE")
                    return

            # Fielder chase and catch
            ball_has_been_caught = False
            for f in self.fielders:
                f.update(self.ball)
                # Catch check if ball in air and near fielder
                if self.state == "BALL_IN_PLAY" and self.ball.is_aerial and self.ball.z <= 28:
                    dist = math.hypot(f.x - self.ball.x, f.y - self.ball.y)
                    if dist < 22:
                        ball_has_been_caught = True
                        self._handle_dismissal(f"c {f.name} b {self.bowler.name}", is_bowled=False)
                        return

            # Check Boundary Rope
            if not PhysicsEngine.is_inside_boundary((self.ball.x, self.ball.y)):
                if self.ball.is_aerial:
                    # MAXIMUM SIX!
                    self._score_boundary(runs=6)
                else:
                    # FOUR!
                    self._score_boundary(runs=4)
                return

            # Ball stopped rolling
            if self.state == "BALL_IN_PLAY" and self.ball.state == "dead":
                # Calculated running between wickets based on ball distance
                dist = math.hypot(self.ball.x - PITCH_X, self.ball.y - PITCH_BOTTOM_Y)
                runs = 1 if dist > 90 else (2 if dist > 200 else 0)
                self._end_delivery(runs=runs, ball_symbol=str(runs) if runs > 0 else ".")

    def _score_boundary(self, runs):
        self.state = "BALL_DEAD"
        self.ball.reset()
        if runs == 6:
            self.umpire.set_signal("SIX")
            self.stadium.trigger_cheer(120)
            if self.sound:
                self.sound.play("boundary")
            if self.camera:
                self.camera.shake(14.0)
            if self.particles:
                self.particles.spawn_confetti(self.ball.x, self.ball.y, 45)
                self.particles.add_floating_text(SCREEN_WIDTH // 2, 280, "SIX! 102m MAXIMUM!", color=COLOR_ACCENT, size=38)
            self.commentary_line = random.choice(COMMENTARY_SIXES)
            self.striker.sixes += 1
        else:
            self.umpire.set_signal("FOUR")
            self.stadium.trigger_cheer(90)
            if self.sound:
                self.sound.play("cheer")
            if self.particles:
                self.particles.spawn_confetti(self.ball.x, self.ball.y, 25)
                self.particles.add_floating_text(SCREEN_WIDTH // 2, 280, "FOUR RUNS! Cracking Boundary!", color=COLOR_SUCCESS, size=34)
            self.commentary_line = random.choice(COMMENTARY_FOURS)
            self.striker.fours += 1

        self._end_delivery(runs=runs, ball_symbol=str(runs))

    def _handle_dismissal(self, dismissal_text, is_bowled=False):
        self.state = "BALL_DEAD"
        self.ball.reset()
        self.wickets += 1
        self.striker.is_out = True
        self.striker.dismissal = dismissal_text
        self.bowler.wickets_taken += 1
        self.umpire.set_signal("OUT")
        self.stadium.trigger_cheer(100)

        if is_bowled:
            self.stadium.dislodge_bails()
            if self.sound:
                self.sound.play("wicket")
            if self.camera:
                self.camera.shake(10.0)
            if self.particles:
                self.particles.spawn_shatter(PITCH_X, PITCH_BOTTOM_Y + 10, 30)
                self.particles.add_floating_text(SCREEN_WIDTH // 2, 280, "BOWLED HIM! Middle Stump Out!", color=COLOR_DANGER, size=36)
        else:
            if self.sound:
                self.sound.play("appeal")
            if self.particles:
                self.particles.add_floating_text(SCREEN_WIDTH // 2, 280, "CAUGHT OUT!", color=COLOR_DANGER, size=36)

        self.commentary_line = random.choice(COMMENTARY_WICKETS)
        self._end_delivery(runs=0, ball_symbol="W")

        # Bring in next batsman if available
        next_idx = max(self.striker_idx, self.non_striker_idx) + 1
        if next_idx < len(self.batting_squad) and self.wickets < 10:
            self.striker_idx = next_idx
            self.striker = self.batting_squad[self.striker_idx]
            self.partnership_runs = 0
            self.partnership_balls = 0

    def _handle_extra(self, extra_type="WIDE"):
        self.state = "BALL_DEAD"
        self.ball.reset()
        self.runs += 1
        self.bowler.runs_conceded += 1
        self.bowler.extras_conceded += 1
        self.umpire.set_signal(extra_type)
        if self.sound:
            self.sound.play("buzzer")
        if self.particles:
            self.particles.add_floating_text(SCREEN_WIDTH // 2, 280, f"{extra_type} +1 Run!", color=COLOR_PRIMARY, size=32)
        self.commentary_line = f"Umpire signals {extra_type}! 1 extra run conceded."
        self.this_over_balls.append("Wd" if extra_type == "WIDE" else "Nb")
        # Extras do not increment legal ball count
        self.state = "READY_TO_BOWL"
        self.state_timer = 0

    def _end_delivery(self, runs, ball_symbol):
        self.runs += runs
        self.striker.runs += runs
        self.striker.balls += 1
        self.bowler.runs_conceded += runs
        self.partnership_runs += runs
        self.partnership_balls += 1

        self.this_over_balls.append(ball_symbol)
        self.balls_in_over += 1

        # Check Target reached in 2nd innings
        if self.current_innings == 2 and self.target is not None and self.runs >= self.target:
            self._finish_match()
            return

        # Check all out
        if self.wickets >= 10:
            self._handle_innings_end()
            return

        # Check over completion
        if self.balls_in_over >= 6:
            self.overs += 1
            self.balls_in_over = 0
            self.bowler.overs_bowled += 1
            self.this_over_balls = []
            # Switch strike
            self.striker, self.non_striker = self.non_striker, self.striker
            # Rotate bowler
            self.bowler_idx = 7 if self.bowler_idx == 8 else (9 if self.bowler_idx == 7 else 8)
            self.bowler = self.bowling_squad[self.bowler_idx]

            # Check if innings overs finished
            if self.overs >= self.max_overs:
                self._handle_innings_end()
                return

        # Reset fielders and ball
        for f in self.fielders:
            f.reset_position()
        self.ball.reset()
        self.state = "READY_TO_BOWL"
        self.state_timer = 0

    def _handle_innings_end(self):
        if self.current_innings == 1:
            self.innings1_data = {
                "team": self.batting_team_key,
                "runs": self.runs,
                "wickets": self.wickets,
                "overs": self.overs,
                "balls": self.balls_in_over
            }
            self.target = self.runs + 1
            self.show_innings_break = True
            self.commentary_line = f"Innings 1 finished! Target is {self.target} runs."
        else:
            self._finish_match()

    def _finish_match(self):
        # Determine winner
        p_team = self.player_team_key
        o_team = self.opponent_team_key
        if self.current_innings == 2:
            team2_runs = self.runs
            team1_runs = self.innings1_data["runs"]
            team2_name = self.batting_team_key
            team1_name = self.innings1_data["team"]

            if team2_runs >= self.target:
                winner = team2_name
                margin = f"{10 - self.wickets} wickets"
            elif team2_runs < team1_runs:
                winner = team1_name
                margin = f"{team1_runs - team2_runs} runs"
            else:
                winner = "TIE"
                margin = "Scores level! Super Over!"
        else:
            winner = p_team
            margin = "Practice match concluded"

        result_summary = {
            "winner": winner,
            "margin": margin,
            "innings1": self.innings1_data,
            "innings2": {
                "team": self.batting_team_key,
                "runs": self.runs,
                "wickets": self.wickets,
                "overs": self.overs,
                "balls": self.balls_in_over
            },
            "p1_squad": self.p1_squad,
            "p2_squad": self.p2_squad,
            "player_team": p_team,
            "opponent_team": o_team
        }

        if self.on_finish:
            self.on_finish(result_summary)

    def draw(self, surface):
        surface.fill((15, 23, 42))

        # 1. Stadium, Pitch, Stumps, Crowd
        self.stadium.draw(surface, self.camera)

        # 2. Umpire
        self.umpire.draw(surface, self.camera)

        # 3. Fielders
        for f in self.fielders:
            f.draw(surface, self.camera)

        # 4. Batsman sprite
        bx = int(self.batsman_x if self.user_is_batting else PITCH_X)
        by = int(self.batsman_y)
        if self.camera:
            bx, by = self.camera.apply((bx, by))

        # Jersey
        p_col = TEAMS_DATA[self.batting_team_key]["primary_color"]
        pygame.draw.rect(surface, (240, 240, 240), (bx - 7, by - 5, 14, 18), border_radius=2)  # pads
        pygame.draw.rect(surface, p_col, (bx - 7, by - 22, 14, 18), border_radius=3)           # jersey
        pygame.draw.circle(surface, (230, 190, 150), (bx, by - 27), 6)                         # head
        pygame.draw.ellipse(surface, (30, 50, 90), (bx - 7, by - 33, 14, 8))                   # helmet

        # Bat
        self.bat.draw(surface, self.batsman_x if self.user_is_batting else PITCH_X, self.batsman_y, self.camera)

        # Bowler sprite at top
        bw_x, bw_y = PITCH_X + 16, PITCH_TOP_Y + 12
        if self.camera:
            bw_x, bw_y = self.camera.apply((bw_x, bw_y))
        b_col = TEAMS_DATA[self.bowling_team_key]["primary_color"]
        pygame.draw.rect(surface, b_col, (bw_x - 5, bw_y - 12, 10, 16), border_radius=2)
        pygame.draw.circle(surface, (230, 190, 150), (bw_x, bw_y - 16), 5)

        # 5. Ball with trail and shadow
        self.ball.draw(surface, self.camera)

        # 6. Particles and floating text
        if self.particles:
            self.particles.draw(surface)

        # 7. Bowling Meter UI (When user is bowling)
        if not self.user_is_batting and self.state == "READY_TO_BOWL":
            self._draw_bowling_meter(surface)

        # 8. Broadcast TV HUD Scoreboard
        crr = (self.runs / (self.overs + self.balls_in_over / 6.0)) if (self.overs * 6 + self.balls_in_over) > 0 else 0.0
        hud_data = {
            "batting_team": self.batting_team_key,
            "runs": self.runs,
            "wickets": self.wickets,
            "overs": self.overs,
            "balls_in_over": self.balls_in_over,
            "max_overs": self.max_overs,
            "crr": crr,
            "target": self.target,
            "striker": self.striker,
            "non_striker": self.non_striker,
            "bowler": self.bowler,
            "this_over_balls": self.this_over_balls,
            "partnership_runs": self.partnership_runs,
            "partnership_balls": self.partnership_balls
        }
        self.scoreboard.draw_hud(surface, hud_data)

        # 9. Live Commentary Bar
        c_rect = (SCREEN_WIDTH // 2 - 320, 68, 640, 28)
        draw_glass_panel(surface, c_rect, border_radius=6)
        fc = get_font(15, bold=False)
        if fc:
            c_surf = fc.render(self.commentary_line, True, (220, 235, 250))
            surface.blit(c_surf, c_surf.get_rect(center=(SCREEN_WIDTH // 2, 82)))

        # 10. Full Scorecard Modal if toggled
        if self.scoreboard.show_full_scorecard:
            self.scoreboard.draw_full_scorecard(surface, self)

        # 11. Innings Break Modal
        if self.show_innings_break:
            self._draw_innings_break_modal(surface)

    def _draw_bowling_meter(self, surface):
        """Draws interactive bowling power and accuracy gauge."""
        panel_rect = (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT - 165, 320, 60)
        draw_glass_panel(surface, panel_rect, border_radius=8)

        f_lbl = get_font(14, bold=True)
        if f_lbl:
            t = f_lbl.render(f"BOWLING METER - {self.selected_delivery_type.upper()} ([1/2/3] Change Pace | [SPACE] Bowl)", True, COLOR_ACCENT)
            surface.blit(t, (panel_rect[0] + 12, panel_rect[1] + 8))

        # Gauge bar
        bar_x = panel_rect[0] + 20
        bar_y = panel_rect[1] + 32
        bar_w = 280
        bar_h = 16
        pygame.draw.rect(surface, (40, 50, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=4)

        # Sweet spot in middle (green)
        sweet_x = bar_x + int(bar_w * 0.42)
        sweet_w = int(bar_w * 0.16)
        pygame.draw.rect(surface, COLOR_SUCCESS, (sweet_x, bar_y, sweet_w, bar_h), border_radius=2)

        # Moving marker
        marker_x = bar_x + int(self.meter_val * bar_w)
        pygame.draw.rect(surface, (255, 255, 255), (marker_x - 3, bar_y - 2, 6, bar_h + 4), border_radius=2)

    def _draw_innings_break_modal(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 230))
        surface.blit(overlay, (0, 0))

        box = (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 140, 500, 280)
        draw_glass_panel(surface, box, border_radius=12)

        f_hdr = get_font(32, bold=True)
        f_sub = get_font(20, bold=True)
        f_txt = get_font(16)

        if f_hdr:
            surface.blit(f_hdr.render("INNINGS BREAK", True, COLOR_ACCENT), (box[0] + 140, box[1] + 25))

        if f_sub and self.innings1_data:
            s_str = f"{self.innings1_data['team']} scored {self.innings1_data['runs']}/{self.innings1_data['wickets']} in {self.innings1_data['overs']}.{self.innings1_data['balls']} overs"
            surface.blit(f_sub.render(s_str, True, COLOR_TEXT_LIGHT), (box[0] + 45, box[1] + 85))
            target_str = f"Target for 2nd Innings: {self.target} Runs"
            surface.blit(f_sub.render(target_str, True, COLOR_PRIMARY), (box[0] + 105, box[1] + 130))

        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 130, box[1] + 195, 260, 48), (16, 185, 129), border_radius=8)
        if f_sub:
            c_txt = f_sub.render("START 2nd INNINGS >", True, (255, 255, 255))
            surface.blit(c_txt, c_txt.get_rect(center=(SCREEN_WIDTH // 2, box[1] + 219)))
