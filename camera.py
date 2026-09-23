"""
camera.py
---------
Screen shake and dynamic viewpoint offset controller.
"""

import random

class Camera:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.offset_x = 0
        self.offset_y = 0
        self.shake_magnitude = 0.0
        self.shake_decay = 0.90

    def shake(self, magnitude=12.0):
        if not self.enabled:
            return
        self.shake_magnitude = max(self.shake_magnitude, magnitude)

    def update(self):
        if self.shake_magnitude > 0.5:
            self.offset_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.offset_y = random.uniform(-self.shake_magnitude, self.shake_magnitude)
            self.shake_magnitude *= self.shake_decay
        else:
            self.shake_magnitude = 0.0
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, pos):
        """Applies camera screen-shake offset to coordinates."""
        return int(pos[0] + self.offset_x), int(pos[1] + self.offset_y)
