"""
settings.py
-----------
Handles loading, saving, and defaults for game configuration.
Uses data/settings.json with graceful fallback when missing or corrupted.
"""

import json
import os

DEFAULT_SETTINGS = {
    "music_volume": 0.6,
    "sfx_volume": 0.8,
    "sound_enabled": True,
    "fullscreen": False,
    "difficulty": "Medium",
    "screen_shake": True,
    "particles": True,
    "commentary_enabled": True
}

class Settings:
    def __init__(self, filepath="data/settings.json"):
        self.filepath = filepath
        self.data = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        """Loads settings from JSON file, falling back to defaults if error."""
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        for k, v in loaded.items():
                            if k in DEFAULT_SETTINGS:
                                self.data[k] = v
                        return
        except Exception as e:
            print(f"[Settings] Warning: Failed to load {self.filepath} ({e}). Using defaults.")

        self.data = dict(DEFAULT_SETTINGS)
        self.save()

    def save(self):
        """Saves current settings to JSON file."""
        try:
            folder = os.path.dirname(self.filepath)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"[Settings] Warning: Failed to save {self.filepath}: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()
