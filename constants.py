"""
constants.py
------------
Centralized constants, colors, physics tunings, game states, team rosters,
and tournament structures for Ultimate Cricket League.
"""

# Screen & Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Ultimate Cricket League"

# Game Flow States
STATE_MAIN_MENU = "MAIN_MENU"
STATE_MATCH_SETUP = "MATCH_SETUP"
STATE_TOSS = "TOSS"
STATE_MATCH = "MATCH"
STATE_PRACTICE = "PRACTICE"
STATE_TOURNAMENT = "TOURNAMENT"
STATE_SETTINGS = "SETTINGS"
STATE_HOW_TO_PLAY = "HOW_TO_PLAY"
STATE_RESULT = "RESULT"
STATE_PAUSE = "PAUSE"

# In-Match Sub-States
MATCH_STATE_READY = "READY_TO_BOWL"
MATCH_STATE_BOWLER_RUNUP = "BOWLER_RUNUP"
MATCH_STATE_BALL_IN_AIR = "BALL_IN_AIR"
MATCH_STATE_SHOT_PLAYED = "SHOT_PLAYED"
MATCH_STATE_FIELDING = "FIELDING"
MATCH_STATE_BALL_DEAD = "BALL_DEAD"
MATCH_STATE_OVER_BREAK = "OVER_BREAK"
MATCH_STATE_INNINGS_BREAK = "INNINGS_BREAK"
MATCH_STATE_MATCH_FINISHED = "MATCH_FINISHED"

# Delivery Types
DELIVERY_FAST = "Fast"
DELIVERY_MEDIUM = "Medium"
DELIVERY_SPIN = "Spin"
DELIVERY_TYPES = [DELIVERY_FAST, DELIVERY_MEDIUM, DELIVERY_SPIN]

# Length Types
LENGTH_YORKER = "Yorker"
LENGTH_FULL = "Full Length"
LENGTH_GOOD = "Good Length"
LENGTH_SHORT = "Bouncer / Short"
LENGTH_TYPES = [LENGTH_YORKER, LENGTH_FULL, LENGTH_GOOD, LENGTH_SHORT]

# Batting Shots (1 to 7 keys)
SHOT_DEFENSIVE = 1
SHOT_STRAIGHT_DRIVE = 2
SHOT_COVER_DRIVE = 3
SHOT_PULL = 4
SHOT_SWEEP = 5
SHOT_CUT = 6
SHOT_LOFTED = 7

SHOT_NAMES = {
    SHOT_DEFENSIVE: "Defensive Block",
    SHOT_STRAIGHT_DRIVE: "Straight Drive",
    SHOT_COVER_DRIVE: "Cover Drive",
    SHOT_PULL: "Pull Shot",
    SHOT_SWEEP: "Sweep Shot",
    SHOT_CUT: "Square Cut",
    SHOT_LOFTED: "Lofted Drive"
}

# Timing Feedback Windows (in seconds relative to perfect hit point)
TIMING_PERFECT = "PERFECT"
TIMING_GOOD = "GOOD"
TIMING_EARLY = "EARLY"
TIMING_LATE = "LATE"
TIMING_EDGE = "EDGE"
TIMING_MISS = "MISS"

# Difficulty Levels
DIFF_EASY = "Easy"
DIFF_MEDIUM = "Medium"
DIFF_HARD = "Hard"
DIFF_EXPERT = "Expert"
DIFFICULTY_LEVELS = [DIFF_EASY, DIFF_MEDIUM, DIFF_HARD, DIFF_EXPERT]

# Pitch and Ground Dimensions (Virtual 2D/3D Pitch)
PITCH_X = SCREEN_WIDTH // 2
PITCH_TOP_Y = 180         # Bowler end
PITCH_BOTTOM_Y = 560      # Batsman crease
PITCH_WIDTH = 90
PITCH_LENGTH = PITCH_BOTTOM_Y - PITCH_TOP_Y

# Stumps positions
BOWLER_STUMPS_POS = (PITCH_X, PITCH_TOP_Y + 10)
BATSMAN_STUMPS_POS = (PITCH_X, PITCH_BOTTOM_Y + 15)

# Boundary Radius (Elliptical ground)
GROUND_RADIUS_X = 580
GROUND_RADIUS_Y = 320
GROUND_CENTER = (PITCH_X, 380)

# 30-Yard Circle Radius
INNER_CIRCLE_RADIUS_X = 280
INNER_CIRCLE_RADIUS_Y = 160

# Modern Color Palette
COLOR_BG_DARK = (15, 23, 42)        # Slate 900
COLOR_PANEL_BG = (30, 41, 59, 230)  # Slate 800 with alpha
COLOR_PANEL_SOLID = (30, 41, 59)
COLOR_PANEL_BORDER = (71, 85, 105)  # Slate 600
COLOR_PRIMARY = (56, 189, 248)      # Sky 400
COLOR_PRIMARY_HOVER = (14, 165, 233)# Sky 500
COLOR_ACCENT = (250, 204, 21)       # Amber 400 (Gold)
COLOR_SUCCESS = (34, 197, 94)       # Emerald 500
COLOR_DANGER = (239, 68, 68)        # Red 500
COLOR_WARNING = (249, 115, 22)      # Orange 500

COLOR_TEXT_LIGHT = (248, 250, 252)  # Slate 50
COLOR_TEXT_MUTED = (148, 163, 184)  # Slate 400
COLOR_TEXT_DARK = (15, 23, 42)

# Field and Pitch Colors
COLOR_GRASS_LIGHT = (34, 140, 34)
COLOR_GRASS_DARK = (28, 120, 28)
COLOR_PITCH = (205, 183, 140)
COLOR_PITCH_LINES = (245, 245, 245)
COLOR_STUMPS = (220, 190, 130)
COLOR_BAILS = (240, 140, 20)
COLOR_BOUNDARY_ROPE = (255, 255, 255)
COLOR_BALL_RED = (220, 38, 38)
COLOR_BALL_SEAM = (255, 255, 255)

# Teams Database
TEAMS_DATA = {
    "IND": {
        "name": "India",
        "short": "IND",
        "primary_color": (30, 115, 230),
        "secondary_color": (255, 153, 51),
        "star_player": "V. Kohli",
        "roster": [
            {"name": "R. Sharma (c)", "role": "Batsman", "bat_skill": 92, "bowl_skill": 30},
            {"name": "S. Gill", "role": "Batsman", "bat_skill": 89, "bowl_skill": 25},
            {"name": "V. Kohli", "role": "Batsman", "bat_skill": 95, "bowl_skill": 40},
            {"name": "S. Iyer", "role": "Batsman", "bat_skill": 86, "bowl_skill": 25},
            {"name": "KL Rahul (wk)", "role": "WK/Batsman", "bat_skill": 88, "bowl_skill": 20},
            {"name": "H. Pandya", "role": "All-Rounder", "bat_skill": 87, "bowl_skill": 84},
            {"name": "R. Jadeja", "role": "All-Rounder", "bat_skill": 83, "bowl_skill": 89},
            {"name": "K. Yadav", "role": "Bowler", "bat_skill": 40, "bowl_skill": 91},
            {"name": "J. Bumrah", "role": "Bowler", "bat_skill": 35, "bowl_skill": 96},
            {"name": "M. Siraj", "role": "Bowler", "bat_skill": 28, "bowl_skill": 88},
            {"name": "M. Shami", "role": "Bowler", "bat_skill": 32, "bowl_skill": 92}
        ]
    },
    "AUS": {
        "name": "Australia",
        "short": "AUS",
        "primary_color": (234, 179, 8),
        "secondary_color": (22, 101, 52),
        "star_player": "P. Cummins",
        "roster": [
            {"name": "D. Warner", "role": "Batsman", "bat_skill": 90, "bowl_skill": 25},
            {"name": "T. Head", "role": "Batsman", "bat_skill": 91, "bowl_skill": 60},
            {"name": "M. Marsh", "role": "All-Rounder", "bat_skill": 87, "bowl_skill": 80},
            {"name": "S. Smith", "role": "Batsman", "bat_skill": 93, "bowl_skill": 50},
            {"name": "G. Maxwell", "role": "All-Rounder", "bat_skill": 88, "bowl_skill": 82},
            {"name": "M. Stoinis", "role": "All-Rounder", "bat_skill": 84, "bowl_skill": 79},
            {"name": "J. Inglis (wk)", "role": "WK/Batsman", "bat_skill": 82, "bowl_skill": 15},
            {"name": "P. Cummins (c)", "role": "Bowler", "bat_skill": 70, "bowl_skill": 94},
            {"name": "M. Starc", "role": "Bowler", "bat_skill": 62, "bowl_skill": 93},
            {"name": "A. Zampa", "role": "Bowler", "bat_skill": 30, "bowl_skill": 90},
            {"name": "J. Hazlewood", "role": "Bowler", "bat_skill": 35, "bowl_skill": 92}
        ]
    },
    "ENG": {
        "name": "England",
        "short": "ENG",
        "primary_color": (190, 24, 40),
        "secondary_color": (20, 60, 140),
        "star_player": "J. Buttler",
        "roster": [
            {"name": "J. Buttler (c/wk)", "role": "WK/Batsman", "bat_skill": 92, "bowl_skill": 10},
            {"name": "P. Salt", "role": "Batsman", "bat_skill": 87, "bowl_skill": 15},
            {"name": "J. Bairstow", "role": "Batsman", "bat_skill": 86, "bowl_skill": 15},
            {"name": "H. Brook", "role": "Batsman", "bat_skill": 88, "bowl_skill": 30},
            {"name": "B. Stokes", "role": "All-Rounder", "bat_skill": 90, "bowl_skill": 85},
            {"name": "L. Livingstone", "role": "All-Rounder", "bat_skill": 84, "bowl_skill": 78},
            {"name": "S. Curran", "role": "All-Rounder", "bat_skill": 80, "bowl_skill": 84},
            {"name": "C. Woakes", "role": "All-Rounder", "bat_skill": 75, "bowl_skill": 86},
            {"name": "A. Rashid", "role": "Bowler", "bat_skill": 40, "bowl_skill": 91},
            {"name": "M. Wood", "role": "Bowler", "bat_skill": 35, "bowl_skill": 90},
            {"name": "J. Archer", "role": "Bowler", "bat_skill": 42, "bowl_skill": 93}
        ]
    },
    "SA": {
        "name": "South Africa",
        "short": "SA",
        "primary_color": (22, 101, 52),
        "secondary_color": (234, 179, 8),
        "star_player": "H. Klaasen",
        "roster": [
            {"name": "Q. de Kock (wk)", "role": "WK/Batsman", "bat_skill": 91, "bowl_skill": 15},
            {"name": "A. Markram (c)", "role": "Batsman", "bat_skill": 88, "bowl_skill": 70},
            {"name": "T. Bavuma", "role": "Batsman", "bat_skill": 82, "bowl_skill": 20},
            {"name": "H. Klaasen", "role": "Batsman", "bat_skill": 94, "bowl_skill": 15},
            {"name": "D. Miller", "role": "Batsman", "bat_skill": 89, "bowl_skill": 20},
            {"name": "M. Jansen", "role": "All-Rounder", "bat_skill": 78, "bowl_skill": 88},
            {"name": "K. Maharaj", "role": "Bowler", "bat_skill": 60, "bowl_skill": 89},
            {"name": "K. Rabada", "role": "Bowler", "bat_skill": 45, "bowl_skill": 94},
            {"name": "A. Nortje", "role": "Bowler", "bat_skill": 30, "bowl_skill": 91},
            {"name": "L. Ngidi", "role": "Bowler", "bat_skill": 28, "bowl_skill": 86},
            {"name": "T. Shamsi", "role": "Bowler", "bat_skill": 25, "bowl_skill": 87}
        ]
    },
    "PAK": {
        "name": "Pakistan",
        "short": "PAK",
        "primary_color": (13, 94, 50),
        "secondary_color": (245, 245, 245),
        "star_player": "B. Azam",
        "roster": [
            {"name": "B. Azam (c)", "role": "Batsman", "bat_skill": 93, "bowl_skill": 25},
            {"name": "M. Rizwan (wk)", "role": "WK/Batsman", "bat_skill": 90, "bowl_skill": 20},
            {"name": "F. Zaman", "role": "Batsman", "bat_skill": 87, "bowl_skill": 25},
            {"name": "S. Ayub", "role": "Batsman", "bat_skill": 83, "bowl_skill": 55},
            {"name": "I. Ahmed", "role": "All-Rounder", "bat_skill": 82, "bowl_skill": 76},
            {"name": "S. Khan", "role": "All-Rounder", "bat_skill": 80, "bowl_skill": 86},
            {"name": "I. Wasim", "role": "All-Rounder", "bat_skill": 78, "bowl_skill": 84},
            {"name": "S. Afridi", "role": "Bowler", "bat_skill": 65, "bowl_skill": 94},
            {"name": "N. Shah", "role": "Bowler", "bat_skill": 40, "bowl_skill": 91},
            {"name": "H. Rauf", "role": "Bowler", "bat_skill": 30, "bowl_skill": 89},
            {"name": "A. Ali", "role": "Bowler", "bat_skill": 25, "bowl_skill": 85}
        ]
    },
    "NZ": {
        "name": "New Zealand",
        "short": "NZ",
        "primary_color": (25, 25, 30),
        "secondary_color": (240, 240, 245),
        "star_player": "K. Williamson",
        "roster": [
            {"name": "D. Conway (wk)", "role": "WK/Batsman", "bat_skill": 89, "bowl_skill": 15},
            {"name": "F. Allen", "role": "Batsman", "bat_skill": 85, "bowl_skill": 20},
            {"name": "K. Williamson (c)", "role": "Batsman", "bat_skill": 94, "bowl_skill": 45},
            {"name": "D. Mitchell", "role": "All-Rounder", "bat_skill": 89, "bowl_skill": 75},
            {"name": "G. Phillips", "role": "All-Rounder", "bat_skill": 86, "bowl_skill": 76},
            {"name": "M. Chapman", "role": "Batsman", "bat_skill": 81, "bowl_skill": 30},
            {"name": "M. Santner", "role": "All-Rounder", "bat_skill": 75, "bowl_skill": 89},
            {"name": "T. Southee", "role": "Bowler", "bat_skill": 60, "bowl_skill": 88},
            {"name": "T. Boult", "role": "Bowler", "bat_skill": 40, "bowl_skill": 93},
            {"name": "M. Henry", "role": "Bowler", "bat_skill": 35, "bowl_skill": 90},
            {"name": "L. Ferguson", "role": "Bowler", "bat_skill": 25, "bowl_skill": 89}
        ]
    }
}

# Stadiums
STADIUMS = {
    "MCG": {
        "name": "Melbourne Stadium",
        "location": "Melbourne",
        "pitch_type": "Bouncy & Fast",
        "bounce_factor": 1.15,
        "spin_factor": 0.85,
        "boundary_scale": 1.05
    },
    "LORDS": {
        "name": "Lord's Cricket Ground",
        "location": "London",
        "pitch_type": "Seam & Swing",
        "bounce_factor": 1.0,
        "spin_factor": 0.90,
        "boundary_scale": 0.98
    },
    "EDEN": {
        "name": "Eden Gardens",
        "location": "Kolkata",
        "pitch_type": "Turn & Spin",
        "bounce_factor": 0.90,
        "spin_factor": 1.25,
        "boundary_scale": 1.0
    },
    "WANKHEDE": {
        "name": "Wankhede Stadium",
        "location": "Mumbai",
        "pitch_type": "Batting Paradise",
        "bounce_factor": 1.05,
        "spin_factor": 1.0,
        "boundary_scale": 0.94
    }
}

OVERS_OPTIONS = [2, 5, 10, 20]
