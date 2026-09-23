"""
main.py
-------
Entry point for Ultimate Cricket League.
Run this file from the CricketGame/ folder:

    python main.py

Requirements (see requirements.txt):
    pip install pygame numpy
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game import Game


def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"\n[Ultimate Cricket League] Fatal Runtime Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
