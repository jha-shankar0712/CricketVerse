"""
sound.py
--------
Procedural audio synthesizer using NumPy and Pygame mixer.
Generates realistic cricket sounds (bat hits, crowd cheers, umpire whistles,
wicket shattering, appeal, and UI clicks) without needing any audio files.
Includes robust error handling and silent fallback if audio device fails.
"""

import pygame
import numpy as np

class SoundManager:
    def __init__(self, settings=None):
        self.settings = settings
        self.enabled = True
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        self.sounds = {}
        self.initialized = False

        if settings:
            self.enabled = settings.get("sound_enabled", True)
            self.sfx_volume = settings.get("sfx_volume", 0.8)
            self.music_volume = settings.get("music_volume", 0.6)

        self._init_mixer()
        if self.initialized:
            self._generate_procedural_sounds()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            self.initialized = True
        except Exception as e:
            print(f"[SoundManager] Audio initialization failed ({e}). Running in silent fallback mode.")
            self.initialized = False
            self.enabled = False

    def _make_sound_from_array(self, mono_array):
        """Converts float numpy array (-1.0 to 1.0) into a 16-bit stereo Pygame Sound."""
        try:
            clamped = np.clip(mono_array, -1.0, 1.0)
            int16_arr = (clamped * 32767).astype(np.int16)
            # Make stereo (N, 2)
            stereo_arr = np.column_stack((int16_arr, int16_arr))
            return pygame.sndarray.make_sound(stereo_arr)
        except Exception as e:
            return None

    def _generate_procedural_sounds(self):
        sample_rate = 44100

        # 1. Bat hit solid (Wood 'thwack' sound)
        duration = 0.18
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        # Low frequency thump + mid woody snap + noise burst
        decay = np.exp(-t * 35)
        hit_wave = 0.6 * np.sin(2 * np.pi * 180 * t) + 0.3 * np.sin(2 * np.pi * 380 * t)
        noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 80) * 0.4
        solid_bat = (hit_wave + noise) * decay
        self.sounds["bat_solid"] = self._make_sound_from_array(solid_bat)

        # 2. Bat edge (Sharp snick)
        duration = 0.12
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        decay = np.exp(-t * 50)
        edge_wave = 0.5 * np.sin(2 * np.pi * 950 * t) + 0.3 * np.sin(2 * np.pi * 1800 * t)
        edge_noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 90) * 0.3
        self.sounds["bat_edge"] = self._make_sound_from_array((edge_wave + edge_noise) * decay)

        # 3. Wicket shatter (Stump strike / wooden crash)
        duration = 0.45
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        decay = np.exp(-t * 12)
        crash_wave = (
            0.4 * np.sin(2 * np.pi * 220 * t) +
            0.3 * np.sin(2 * np.pi * 440 * t) +
            0.3 * np.sin(2 * np.pi * 110 * t)
        )
        crash_noise = (np.random.rand(len(t)) * 2 - 1) * np.exp(-t * 20) * 0.6
        self.sounds["wicket"] = self._make_sound_from_array((crash_wave + crash_noise) * decay)

        # 4. Crowd Cheer (Broadband noise with envelope)
        duration = 1.6
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        envelope = np.sin(np.pi * (t / duration)) ** 1.5
        noise = np.random.normal(0, 0.35, len(t))
        # Filter simulation via moving average
        kernel_size = 15
        filtered_noise = np.convolve(noise, np.ones(kernel_size)/kernel_size, mode='same')
        self.sounds["cheer"] = self._make_sound_from_array(filtered_noise * envelope)

        # 5. Boundary Roar (Denser cheer with celebration horn)
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        env = np.minimum(t * 3, 1.0) * np.exp(-t * 0.8)
        c_noise = np.random.normal(0, 0.4, len(t))
        horn = 0.25 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 554 * t)
        self.sounds["boundary"] = self._make_sound_from_array((c_noise + horn) * env * 0.7)

        # 6. UI Click
        duration = 0.05
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        click = np.sin(2 * np.pi * 880 * t) * np.exp(-t * 120)
        self.sounds["click"] = self._make_sound_from_array(click * 0.4)

        # 7. Whistle / Appeal ("Howzat!")
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        pitch = 600 + 400 * np.sin(np.pi * t / duration)
        whistle = 0.4 * np.sin(2 * np.pi * pitch * t) * np.exp(-t * 3)
        self.sounds["appeal"] = self._make_sound_from_array(whistle)

        # 8. Whistle / Buzzer for Wide/No-ball
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        buzzer = (0.3 * np.sign(np.sin(2 * np.pi * 280 * t))) * np.exp(-t * 4)
        self.sounds["buzzer"] = self._make_sound_from_array(buzzer)

        # 9. Ball bounce on pitch
        duration = 0.08
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        bounce = np.sin(2 * np.pi * 140 * t) * np.exp(-t * 60)
        self.sounds["bounce"] = self._make_sound_from_array(bounce * 0.5)

    def play(self, sound_name):
        """Plays sound by key if enabled and initialized."""
        if not self.enabled or not self.initialized:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.set_volume(self.sfx_volume)
                snd.play()
            except Exception:
                pass

    def update_volume(self, sfx_vol, music_vol):
        self.sfx_volume = max(0.0, min(1.0, sfx_vol))
        self.music_volume = max(0.0, min(1.0, music_vol))
        if self.settings:
            self.settings.set("sfx_volume", self.sfx_volume)
            self.settings.set("music_volume", self.music_volume)

    def set_enabled(self, enabled):
        self.enabled = enabled
        if self.settings:
            self.settings.set("sound_enabled", enabled)
