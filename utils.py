"""
utils.py
--------
Rendering utilities: modern UI buttons, panels, gradient cards,
font management with graceful fallbacks, and drawing helpers.
"""

import pygame
import math
from constants import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT_LIGHT,
    COLOR_TEXT_MUTED, COLOR_PANEL_SOLID, COLOR_PANEL_BORDER,
    COLOR_ACCENT, COLOR_SUCCESS, COLOR_DANGER
)

_FONT_CACHE = {}

def get_font(size=24, bold=False):
    """Safely retrieves cached fonts with graceful system fallbacks."""
    key = (size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    font_candidates = ["segoeui", "tahoma", "helvetica", "arial", "dejavusans", "freesansbold"]
    font = None
    for name in font_candidates:
        try:
            font = pygame.font.SysFont(name, size, bold=bold)
            if font:
                break
        except Exception:
            continue

    if not font:
        try:
            font = pygame.font.Font(None, size)
        except Exception:
            pass

    _FONT_CACHE[key] = font
    return font

def draw_rounded_rect(surface, rect, color, border_radius=8, border_color=None, border_width=1):
    """Draws a smooth anti-aliased rounded rectangle with optional border."""
    r = pygame.Rect(rect)
    pygame.draw.rect(surface, color, r, border_radius=border_radius)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, r, width=border_width, border_radius=border_radius)

def draw_glass_panel(surface, rect, border_radius=12):
    """Draws a modern translucent card panel with border."""
    panel_surf = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    panel_surf.fill((25, 33, 50, 220))
    surface.blit(panel_surf, (rect[0], rect[1]))
    pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, width=1, border_radius=border_radius)

class Button:
    """Modern interactive button with hover animations and sound trigger."""
    def __init__(self, rect, text, font_size=22, bg_color=COLOR_PRIMARY,
                 hover_color=COLOR_PRIMARY_HOVER, text_color=COLOR_TEXT_LIGHT,
                 border_radius=8, on_click=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font_size = font_size
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.on_click = on_click
        self.is_hovered = False
        self.scale_offset = 0

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        draw_rect = self.rect.inflate(2, 2) if self.is_hovered else self.rect
        draw_rounded_rect(surface, draw_rect, color, border_radius=self.border_radius,
                          border_color=(255, 255, 255) if self.is_hovered else None,
                          border_width=2 if self.is_hovered else 0)

        font = get_font(self.font_size, bold=True)
        if font:
            text_surf = font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=draw_rect.center)
            surface.blit(text_surf, text_rect)

    def handle_event(self, event, sound_mgr=None):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                if sound_mgr:
                    sound_mgr.play("click")
                if self.on_click:
                    self.on_click()
                return True
        return False

class OptionSelector:
    """Horizontal arrow selector for cycling options (e.g. Teams, Overs, Difficulty)."""
    def __init__(self, rect, label, options, current_idx=0, on_change=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.options = options
        self.current_idx = current_idx
        self.on_change = on_change
        self.btn_prev = Button((self.rect.x + 130, self.rect.y + 4, 36, 32), "<", 18,
                               bg_color=(51, 65, 85), hover_color=(71, 85, 105),
                               on_click=self.prev_opt)
        self.btn_next = Button((self.rect.right - 44, self.rect.y + 4, 36, 32), ">", 18,
                               bg_color=(51, 65, 85), hover_color=(71, 85, 105),
                               on_click=self.next_opt)

    def prev_opt(self):
        self.current_idx = (self.current_idx - 1) % len(self.options)
        if self.on_change:
            self.on_change(self.options[self.current_idx])

    def next_opt(self):
        self.current_idx = (self.current_idx + 1) % len(self.options)
        if self.on_change:
            self.on_change(self.options[self.current_idx])

    def get_selected(self):
        return self.options[self.current_idx]

    def update(self, mouse_pos):
        self.btn_prev.update(mouse_pos)
        self.btn_next.update(mouse_pos)

    def handle_event(self, event, sound_mgr=None):
        handled = self.btn_prev.handle_event(event, sound_mgr)
        if not handled:
            handled = self.btn_next.handle_event(event, sound_mgr)
        return handled

    def draw(self, surface):
        draw_glass_panel(surface, self.rect, border_radius=8)
        font = get_font(18, bold=True)
        if font:
            # Label
            lbl = font.render(self.label, True, COLOR_TEXT_MUTED)
            surface.blit(lbl, (self.rect.x + 12, self.rect.y + 10))
            # Current selected
            sel_text = str(self.options[self.current_idx])
            val = font.render(sel_text, True, COLOR_TEXT_LIGHT)
            val_rect = val.get_rect(center=(self.rect.x + (self.rect.width + 90)//2, self.rect.centery))
            surface.blit(val, val_rect)

        self.btn_prev.draw(surface)
        self.btn_next.draw(surface)
