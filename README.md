# Ultimate Cricket League

A modern, fast-paced, 2D cricket simulation game built in Python using Pygame and NumPy.
All visuals are generated procedurally (vector graphics, lush turf, animated crowd, player sprites, camera shake, particles) and all sound effects are synthesized in real-time with NumPy — requiring **zero external image or audio downloads**.

---

## 🌟 Key Features

- **Procedural Graphics & Audio:** No missing image assets or audio files. Sounds (solid bat crack, edge nick, wicket shatter, crowd roar, umpire whistles, UI clicks) are generated on startup via pure NumPy synthesis.
- **Multiple Game Modes:**
  - **Quick Match:** Full two-innings international cricket match with authentic rules.
  - **Tournament Mode (Champions Cup):** Knockout fixtures (Semi-Finals and Grand Final) with champion celebration.
  - **Practice Nets:** Dynamic batting practice with real-time timing analysis.
- **Interactive Match Setup & Toss:**
  - 8 International Teams: India, Australia, England, South Africa, Pakistan, New Zealand (authentic rosters, player roles, batting and bowling skills).
  - 4 Iconic Stadiums: Melbourne Stadium, Lord's, Eden Gardens, Wankhede Stadium with distinct pitch conditions (bounce, swing, spin).
  - Configurable overs: 2, 5, 10, or 20 overs per innings.
  - 3D Animated Coin Toss: Interactive heads/tails call and bat/bowl choice.
- **Deep Batting & Bowling Systems:**
  - **7 Shot Types:** Defensive block, straight drive, cover drive, pull shot, sweep, cut, and lofted maximum drive.
  - **Precision Timing Windows:** PERFECT, GOOD, EARLY, LATE, EDGE, and MISS with instant HUD popups and particle celebrations.
  - **Interactive Bowling Gauge:** Moving sweet-spot meter for pace variation (Fast, Medium, Spin) and line/length adjustments.
- **Broadcast-Grade HUD & Presentation:**
  - Live TV score strip, required run rate, partnership tracker, and over-by-over ball timeline.
  - Full Detailed Scorecard Modal available at any time by pressing `TAB`.
  - Realistic dismissals (Bowled with flying bails, Caught in the deep, Run Out chances).
  - Wide and No-Ball detection with extra runs.
  - Post-Match Presentation with Player of the Match and full innings summaries.
- **Configurable Settings:**
  - Sound FX volume, camera screen shake toggle, particle effects toggle saved safely to `data/settings.json`.

---

## 💻 System Requirements

- **Python:** 3.9 or higher (tested on Python 3.11, 3.12, 3.13)
- **Dependencies:**
  - `pygame >= 2.5.2`
  - `numpy >= 1.26.0`

---

## 🚀 Installation & Running

### Windows (Command Prompt / PowerShell / VS Code)

1. Open VS Code and navigate to the project directory:
   ```cmd
   cd CricketGame
   ```
2. (Optional but recommended) Create and activate a virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install required packages:
   ```cmd
   pip install -r requirements.txt
   ```
4. Run the game:
   ```cmd
   python main.py
   ```

### macOS / Linux

```bash
cd CricketGame
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

---

## 🎮 Game Controls

### Menus & Setup
- **Mouse Left Click:** Select options, press buttons, cycle through teams/overs/difficulty.
- **ESC:** Go back / Pause match.

### Batting Controls (When you are batting)
- **`←` / `→` or `A` / `D`:** Shuffle laterally across the batting crease.
- **`1`:** Defensive Block (safely drops ball at feet)
- **`2`:** Straight Drive (down the ground)
- **`3`:** Cover Drive (through extra cover)
- **`4`:** Pull Shot (swatted through mid-wicket / leg-side)
- **`5`:** Sweep Shot (paddle sweep towards fine leg)
- **`6`:** Square Cut (past point / third man)
- **`7`:** Lofted Shot (high aerial drive for a SIX!)

> **Timing Tip:** Watch the ball flight and press the shot key the instant the ball approaches your crease!

### Bowling Controls (When you are bowling)
- **`1`:** Fast Pace (140 - 150 km/h)
- **`2`:** Medium Pace (125 - 135 km/h)
- **`3`:** Spin Bowling (85 - 98 km/h)
- **`←` / `→` or `A` / `D`:** Adjust delivery line across stumps.
- **`SPACE`:** Lock in accuracy meter when the marker is centered in the green sweet spot!

### In-Match Shortcuts
- **`TAB`:** Toggle Full Match Scorecard overlay.
- **`ESC`:** Open Pause Menu (Resume, Restart, Main Menu).

---

## 📁 Project Architecture

```
CricketGame/
│
├── main.py                 # Application launcher & error handler
├── requirements.txt        # Pinned runtime dependencies
├── README.md               # Full setup, controls, and architecture docs
│
├── assets/                 # Reserved for optional custom art/skins
├── data/
│   ├── settings.json       # Saved user preferences & audio volumes
│   └── save/               # Reserved for save-game profiles
│
└── src/
    ├── __init__.py         # Package declaration
    ├── constants.py        # Dimensions, teams, rosters, colors, states
    ├── settings.py         # JSON settings load/save with safe defaults
    ├── sound.py            # NumPy procedural audio synthesizer
    ├── utils.py            # UI buttons, glass panels, font manager
    ├── animation.py        # Particle system & floating notification text
    ├── camera.py           # Smooth screen-shake camera system
    ├── physics.py          # Trajectory calculation & shot evaluation
    ├── ball.py             # 3D ball entity with flight, trail & bounce
    ├── bat.py              # Batsman swing mechanics & timing window
    ├── player.py           # Batsman, bowler, and chasing fielders
    ├── stadium.py          # Procedural grass, pitch, crowd & stumps
    ├── umpire.py           # Referee decisions (Wide, Out, Six, Four)
    ├── scoreboard.py       # TV broadcast HUD & full scorecard modal
    ├── ai.py               # AI bowling and batting decision matrix
    ├── menu.py             # Main menu, setup, toss, tournament, settings
    ├── match.py            # Ball-by-ball match state machine
    └── game.py             # Top-level application coordinator
```

---

## 🛠️ Troubleshooting

- **Audio initialization failure:**
  If you run on a headless server or system without an active audio card, the built-in `SoundManager` automatically catches the exception and operates in silent mode without crashing.
- **Display resolution issues:**
  The game renders in a standard 1280x720 window. You can toggle fullscreen mode in `data/settings.json` or through Settings.
- **ModuleNotFoundError:**
  Ensure you are executing `python main.py` directly inside the `CricketGame/` directory.

---

## 📜 Credits

- Built with **Python 3**, **Pygame**, and **NumPy**.
- Developed as a completely standalone, self-contained cricket game.
