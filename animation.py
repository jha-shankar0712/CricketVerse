"""
animation.py
------------
Particle systems, floating announcement popups, easing utilities.
"""

import pygame
import random
import math
from constants import COLOR_ACCENT, COLOR_SUCCESS, COLOR_DANGER

class Particle:
    def __init__(self, x, y, vx, vy, color, size, life):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life

    def update(self, dt=1.0):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 0.15 * dt  # subtle gravity
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0, min(255, int((self.life / self.max_life) * 255)))
        r = max(1, int(self.size * (self.life / self.max_life)))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        c = (self.color[0], self.color[1], self.color[2], alpha)
        pygame.draw.circle(s, c, (r, r), r)
        surface.blit(s, (self.x - r, self.y - r))

class FloatingText:
    def __init__(self, x, y, text, color=(255, 255, 255), size=28, duration=60):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.size = size
        self.duration = duration
        self.age = 0
        self.vy = -1.5

    def update(self):
        self.y += self.vy
        self.vy *= 0.94
        self.age += 1

    def is_dead(self):
        return self.age >= self.duration

    def draw(self, surface):
        from utils import get_font
        font = get_font(self.size, bold=True)
        if not font:
            return
        progress = self.age / self.duration
        alpha = max(0, min(255, int((1.0 - progress) * 255)))
        txt_surf = font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(txt_surf, (0, 0))
        alpha_surf.set_alpha(alpha)
        rect = alpha_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(alpha_surf, rect)

class ParticleManager:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.particles = []
        self.floating_texts = []

    def spawn_confetti(self, x, y, count=35):
        if not self.enabled:
            return
        colors = [(255, 215, 0), (255, 60, 60), (50, 205, 50), (30, 144, 255), (255, 105, 180)]
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2.5, 7.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2.0
            color = random.choice(colors)
            size = random.uniform(3, 6)
            life = random.randint(40, 75)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def spawn_dust(self, x, y, count=12):
        if not self.enabled:
            return
        for _ in range(count):
            angle = random.uniform(math.pi * 0.8, math.pi * 2.2)
            speed = random.uniform(1.0, 3.0)
            vx = math.cos(angle) * speed
            vy = -abs(math.sin(angle) * speed)
            color = (210, 190, 160)
            size = random.uniform(2, 4)
            life = random.randint(15, 30)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def spawn_shatter(self, x, y, count=25):
        if not self.enabled:
            return
        for _ in range(count):
            vx = random.uniform(-4.0, 4.0)
            vy = random.uniform(-6.0, -1.0)
            color = (230, 200, 140)
            size = random.uniform(3, 5)
            life = random.randint(30, 50)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def add_floating_text(self, x, y, text, color=COLOR_ACCENT, size=30):
        self.floating_texts.append(FloatingText(x, y, text, color, size))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        for ft in self.floating_texts:
            ft.update()
        self.floating_texts = [ft for ft in self.floating_texts if not ft.is_dead()]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)
        for ft in self.floating_texts:
            ft.draw(surface)
