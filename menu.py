"""
menu.py
-------
UI screens for Main Menu, Match Setup, Animated Coin Toss, Practice Mode,
Tournament Mode, Settings, How to Play, and Post-Match Result screen.
"""

import pygame
import math
import random
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TITLE,
    COLOR_BG_DARK, COLOR_PANEL_SOLID, COLOR_PANEL_BORDER,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_ACCENT,
    COLOR_SUCCESS, COLOR_DANGER, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    STATE_MAIN_MENU, STATE_MATCH_SETUP, STATE_TOSS, STATE_MATCH,
    STATE_PRACTICE, STATE_TOURNAMENT, STATE_SETTINGS, STATE_HOW_TO_PLAY, STATE_RESULT,
    TEAMS_DATA, OVERS_OPTIONS, DIFFICULTY_LEVELS, STADIUMS
)
from utils import get_font, Button, OptionSelector, draw_rounded_rect, draw_glass_panel

class MenuManager:
    def __init__(self, game):
        self.game = game
        self.sound = game.sound
        self.settings = game.settings

        # Match Setup selections
        self.team_keys = list(TEAMS_DATA.keys())
        self.player_team_idx = 0
        self.opponent_team_idx = 1
        self.overs_idx = 1      # 5 overs default
        self.difficulty_idx = 1  # Medium default
        self.stadium_keys = list(STADIUMS.keys())
        self.stadium_idx = 0
        self.user_choice_bat_bowl = "Bat"

        # Toss screen state
        self.toss_coin_flipping = False
        self.toss_rot_angle = 0
        self.toss_winner = None
        self.toss_user_call = "Heads"
        self.toss_decision = None
        self.toss_result_text = ""

        # Tournament state
        self.tournament_teams = ["IND", "AUS", "ENG", "SA"]
        self.tournament_stage = "Semi-Final 1"
        self.tournament_matches = [
            {"team1": "IND", "team2": "ENG", "winner": None, "stage": "Semi-Final 1"},
            {"team1": "AUS", "team2": "SA", "winner": None, "stage": "Semi-Final 2"},
            {"team1": "TBD", "team2": "TBD", "winner": None, "stage": "Grand Final"}
        ]
        self.tournament_champion = None

        self._build_ui()

    def _build_ui(self):
        # Main Menu Buttons
        btn_w, btn_h = 240, 48
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        start_y = 230
        gap = 58

        self.main_buttons = [
            Button((cx, start_y, btn_w, btn_h), "QUICK MATCH", 22, bg_color=(2, 132, 199),
                   on_click=lambda: self.game.change_state(STATE_MATCH_SETUP)),
            Button((cx, start_y + gap, btn_w, btn_h), "TOURNAMENT", 22, bg_color=(13, 148, 136),
                   on_click=lambda: self.game.change_state(STATE_TOURNAMENT)),
            Button((cx, start_y + gap*2, btn_w, btn_h), "PRACTICE NETS", 22, bg_color=(124, 58, 237),
                   on_click=self.start_practice_mode),
            Button((cx, start_y + gap*3, btn_w, btn_h), "SETTINGS", 22, bg_color=(71, 85, 105),
                   on_click=lambda: self.game.change_state(STATE_SETTINGS)),
            Button((cx, start_y + gap*4, btn_w, btn_h), "HOW TO PLAY", 22, bg_color=(71, 85, 105),
                   on_click=lambda: self.game.change_state(STATE_HOW_TO_PLAY)),
            Button((cx, start_y + gap*5, btn_w, btn_h), "EXIT GAME", 22, bg_color=(220, 38, 38),
                   on_click=self.game.quit_game)
        ]

    def start_practice_mode(self):
        self.game.start_practice()

    def handle_main_menu_event(self, event):
        for btn in self.main_buttons:
            if btn.handle_event(event, self.sound):
                break

    def update_main_menu(self, mouse_pos):
        for btn in self.main_buttons:
            btn.update(mouse_pos)

    def draw_main_menu(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Cricket pitch background accents
        pygame.draw.ellipse(surface, (18, 30, 48), (SCREEN_WIDTH // 2 - 450, -50, 900, 800), 2)
        pygame.draw.ellipse(surface, (25, 45, 75), (SCREEN_WIDTH // 2 - 300, 50, 600, 600), 2)

        # Title
        f_title = get_font(52, bold=True)
        f_sub = get_font(22, bold=False)
        if f_title:
            t_surf = f_title.render("ULTIMATE CRICKET LEAGUE", True, COLOR_ACCENT)
            surface.blit(t_surf, t_surf.get_rect(center=(SCREEN_WIDTH // 2, 110)))
        if f_sub:
            sub_surf = f_sub.render("Modern 2D Cricket Simulation Engine", True, COLOR_TEXT_MUTED)
            surface.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 160)))

        for btn in self.main_buttons:
            btn.draw(surface)

        # Version watermark
        f_ver = get_font(14)
        if f_ver:
            v_txt = f_ver.render("v1.0.0 | Pure Python + Pygame + NumPy", True, (80, 100, 120))
            surface.blit(v_txt, (20, SCREEN_HEIGHT - 25))

    # --- MATCH SETUP SCREEN ---
    def handle_setup_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state(STATE_MAIN_MENU)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Start button
            if pygame.Rect(SCREEN_WIDTH // 2 - 120, 620, 240, 50).collidepoint(mx, my):
                self.sound.play("click")
                self.start_toss_screen()
                return

            # Back button
            if pygame.Rect(40, 40, 100, 40).collidepoint(mx, my):
                self.sound.play("click")
                self.game.change_state(STATE_MAIN_MENU)
                return

            # Team selectors
            if pygame.Rect(SCREEN_WIDTH // 2 - 260, 230, 40, 40).collidepoint(mx, my):
                self.player_team_idx = (self.player_team_idx - 1) % len(self.team_keys)
                self.sound.play("click")
            elif pygame.Rect(SCREEN_WIDTH // 2 - 60, 230, 40, 40).collidepoint(mx, my):
                self.player_team_idx = (self.player_team_idx + 1) % len(self.team_keys)
                self.sound.play("click")

            if pygame.Rect(SCREEN_WIDTH // 2 + 60, 230, 40, 40).collidepoint(mx, my):
                self.opponent_team_idx = (self.opponent_team_idx - 1) % len(self.team_keys)
                self.sound.play("click")
            elif pygame.Rect(SCREEN_WIDTH // 2 + 260, 230, 40, 40).collidepoint(mx, my):
                self.opponent_team_idx = (self.opponent_team_idx + 1) % len(self.team_keys)
                self.sound.play("click")

            # Overs selector
            if pygame.Rect(SCREEN_WIDTH // 2 - 150, 360, 300, 40).collidepoint(mx, my):
                self.overs_idx = (self.overs_idx + 1) % len(OVERS_OPTIONS)
                self.sound.play("click")

            # Difficulty selector
            if pygame.Rect(SCREEN_WIDTH // 2 - 150, 440, 300, 40).collidepoint(mx, my):
                self.difficulty_idx = (self.difficulty_idx + 1) % len(DIFFICULTY_LEVELS)
                self.sound.play("click")

            # Stadium selector
            if pygame.Rect(SCREEN_WIDTH // 2 - 150, 520, 300, 40).collidepoint(mx, my):
                self.stadium_idx = (self.stadium_idx + 1) % len(self.stadium_keys)
                self.sound.play("click")

    def draw_match_setup(self, surface):
        surface.fill(COLOR_BG_DARK)

        # Back button
        draw_rounded_rect(surface, (40, 40, 100, 40), (45, 55, 75), border_radius=6)
        fb = get_font(18, bold=True)
        if fb:
            surface.blit(fb.render("< BACK", True, COLOR_TEXT_LIGHT), (56, 48))

        f_hdr = get_font(36, bold=True)
        if f_hdr:
            t = f_hdr.render("MATCH SETUP", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Teams Selection Panels
        p_team = TEAMS_DATA[self.team_keys[self.player_team_idx]]
        o_team = TEAMS_DATA[self.team_keys[self.opponent_team_idx]]

        # Player Team Card
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 320, 140, 280, 170), border_radius=12)
        # Opponent Team Card
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 + 40, 140, 280, 170), border_radius=12)

        f_lbl = get_font(16, bold=True)
        f_team = get_font(28, bold=True)
        f_star = get_font(14, bold=False)

        # Player Team
        if f_lbl:
            surface.blit(f_lbl.render("YOUR TEAM (P1)", True, COLOR_PRIMARY), (SCREEN_WIDTH // 2 - 300, 155))
        if f_team:
            pt_txt = f_team.render(p_team["name"], True, p_team["primary_color"])
            surface.blit(pt_txt, (SCREEN_WIDTH // 2 - 300, 185))
        if f_star:
            surface.blit(f_star.render(f"Key Player: {p_team['star_player']}", True, COLOR_TEXT_MUTED), (SCREEN_WIDTH // 2 - 300, 265))

        # Opponent Team
        if f_lbl:
            surface.blit(f_lbl.render("OPPONENT (AI)", True, COLOR_DANGER), (SCREEN_WIDTH // 2 + 60, 155))
        if f_team:
            ot_txt = f_team.render(o_team["name"], True, o_team["primary_color"])
            surface.blit(ot_txt, (SCREEN_WIDTH // 2 + 60, 185))
        if f_star:
            surface.blit(f_star.render(f"Key Player: {o_team['star_player']}", True, COLOR_TEXT_MUTED), (SCREEN_WIDTH // 2 + 60, 265))

        # VS circle
        pygame.draw.circle(surface, (40, 50, 70), (SCREEN_WIDTH // 2, 225), 24)
        if f_lbl:
            vs = f_lbl.render("VS", True, COLOR_ACCENT)
            surface.blit(vs, vs.get_rect(center=(SCREEN_WIDTH // 2, 225)))

        # Arrow buttons for teams
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 260, 230, 40, 32), (60, 75, 95), border_radius=6)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 100, 230, 40, 32), (60, 75, 95), border_radius=6)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 100, 230, 40, 32), (60, 75, 95), border_radius=6)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 260, 230, 40, 32), (60, 75, 95), border_radius=6)
        if fb:
            surface.blit(fb.render("<", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 246, 236))
            surface.blit(fb.render(">", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 86, 236))
            surface.blit(fb.render("<", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 114, 236))
            surface.blit(fb.render(">", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 274, 236))

        # Settings selectors: Overs, Difficulty, Stadium
        f_opt = get_font(20, bold=True)
        # Overs
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 160, 350, 320, 50), border_radius=8)
        if f_opt:
            surface.blit(f_opt.render(f"Match Overs: {OVERS_OPTIONS[self.overs_idx]} Overs", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 120, 362))

        # Difficulty
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 160, 430, 320, 50), border_radius=8)
        if f_opt:
            surface.blit(f_opt.render(f"AI Difficulty: {DIFFICULTY_LEVELS[self.difficulty_idx]}", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 120, 442))

        # Stadium
        stadium_info = STADIUMS[self.stadium_keys[self.stadium_idx]]
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 160, 510, 320, 50), border_radius=8)
        if f_opt:
            surface.blit(f_opt.render(f"Venue: {stadium_info['name']}", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 140, 522))

        # PROCEED TO TOSS BUTTON
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 130, 610, 260, 52), (16, 185, 129), border_radius=10)
        f_go = get_font(22, bold=True)
        if f_go:
            go_t = f_go.render("PROCEED TO TOSS >", True, (255, 255, 255))
            surface.blit(go_t, go_t.get_rect(center=(SCREEN_WIDTH // 2, 636)))

    # --- TOSS SCREEN ---
    def start_toss_screen(self):
        self.toss_coin_flipping = True
        self.toss_rot_angle = 0
        self.toss_winner = None
        self.toss_decision = None
        self.toss_result_text = "Toss in progress..."
        self.sound.play("appeal")
        self.game.change_state(STATE_TOSS)

    def handle_toss_event(self, event):
        if not self.toss_coin_flipping and self.toss_winner:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                p_team_key = self.team_keys[self.player_team_idx]

                if self.toss_winner == p_team_key:
                    # Player decides: Bat or Bowl
                    if pygame.Rect(SCREEN_WIDTH // 2 - 180, 480, 160, 50).collidepoint(mx, my):
                        self.toss_decision = "Bat"
                        self.sound.play("click")
                        self.start_match_from_toss()
                    elif pygame.Rect(SCREEN_WIDTH // 2 + 20, 480, 160, 50).collidepoint(mx, my):
                        self.toss_decision = "Bowl"
                        self.sound.play("click")
                        self.start_match_from_toss()
                else:
                    # AI has already decided, player clicks Continue
                    if pygame.Rect(SCREEN_WIDTH // 2 - 100, 500, 200, 50).collidepoint(mx, my):
                        self.sound.play("click")
                        self.start_match_from_toss()

    def update_toss(self):
        if self.toss_coin_flipping:
            self.toss_rot_angle += 18
            if self.toss_rot_angle >= 360 * 3:
                self.toss_coin_flipping = False
                p_key = self.team_keys[self.player_team_idx]
                o_key = self.team_keys[self.opponent_team_idx]
                coin_res = random.choice(["Heads", "Tails"])
                if coin_res == self.toss_user_call:
                    self.toss_winner = p_key
                    self.toss_result_text = f"{TEAMS_DATA[p_key]['name']} WON THE TOSS!"
                else:
                    self.toss_winner = o_key
                    ai_dec = random.choice(["Bat", "Bowl"])
                    self.toss_decision = ai_dec
                    self.toss_result_text = f"{TEAMS_DATA[o_key]['name']} won the toss and elected to {ai_dec} first!"

    def draw_toss(self, surface):
        surface.fill(COLOR_BG_DARK)
        f_hdr = get_font(38, bold=True)
        if f_hdr:
            t = f_hdr.render("MATCH TOSS", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 70)))

        # Animated 3D Coin
        cx, cy = SCREEN_WIDTH // 2, 240
        coin_scale = abs(math.cos(math.radians(self.toss_rot_angle)))
        coin_w = max(4, int(90 * coin_scale))
        coin_h = 90
        coin_rect = (cx - coin_w // 2, cy - coin_h // 2, coin_w, coin_h)

        pygame.draw.ellipse(surface, (250, 204, 21), coin_rect)
        pygame.draw.ellipse(surface, (202, 138, 4), coin_rect, width=3)
        if coin_w > 25:
            fc = get_font(26, bold=True)
            if fc:
                sym = "H" if math.sin(math.radians(self.toss_rot_angle)) >= 0 else "T"
                c_lbl = fc.render(sym, True, (120, 53, 15))
                surface.blit(c_lbl, c_lbl.get_rect(center=(cx, cy)))

        # Toss Result
        f_res = get_font(28, bold=True)
        if f_res:
            res_surf = f_res.render(self.toss_result_text, True, COLOR_TEXT_LIGHT)
            surface.blit(res_surf, res_surf.get_rect(center=(SCREEN_WIDTH // 2, 360)))

        p_team_key = self.team_keys[self.player_team_idx]
        if not self.toss_coin_flipping and self.toss_winner:
            if self.toss_winner == p_team_key:
                # Prompt user choice
                f_p = get_font(22)
                if f_p:
                    surface.blit(f_p.render("Choose what you want to do first:", True, COLOR_PRIMARY), (SCREEN_WIDTH // 2 - 160, 420))

                draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 180, 480, 160, 50), (37, 99, 235), border_radius=8)
                draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 20, 480, 160, 50), (217, 119, 6), border_radius=8)
                fb = get_font(20, bold=True)
                if fb:
                    surface.blit(fb.render("BAT FIRST", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 150, 494))
                    surface.blit(fb.render("BOWL FIRST", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 45, 494))
            else:
                # AI made choice, show continue button
                draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 100, 480, 200, 50), (16, 185, 129), border_radius=8)
                fb = get_font(20, bold=True)
                if fb:
                    surface.blit(fb.render("START MATCH >", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 75, 494))

    def start_match_from_toss(self):
        p_team = self.team_keys[self.player_team_idx]
        o_team = self.team_keys[self.opponent_team_idx]
        overs = OVERS_OPTIONS[self.overs_idx]
        diff = DIFFICULTY_LEVELS[self.difficulty_idx]
        stadium = self.stadium_keys[self.stadium_idx]

        # Determine who bats first
        if self.toss_winner == p_team:
            user_bats_first = (self.toss_decision == "Bat")
        else:
            user_bats_first = (self.toss_decision == "Bowl")

        self.game.start_match(
            player_team=p_team,
            opponent_team=o_team,
            max_overs=overs,
            difficulty=diff,
            stadium=stadium,
            user_bats_first=user_bats_first
        )

    # --- TOURNAMENT SCREEN ---
    def handle_tournament_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state(STATE_MAIN_MENU)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Back
            if pygame.Rect(40, 40, 100, 40).collidepoint(mx, my):
                self.sound.play("click")
                self.game.change_state(STATE_MAIN_MENU)
                return
            # Play Match
            if pygame.Rect(SCREEN_WIDTH // 2 - 120, 580, 240, 50).collidepoint(mx, my):
                self.sound.play("click")
                # Start tournament semi-final
                self.player_team_idx = 0  # IND
                self.opponent_team_idx = 2  # ENG
                self.start_toss_screen()

    def draw_tournament(self, surface):
        surface.fill(COLOR_BG_DARK)
        # Back button
        draw_rounded_rect(surface, (40, 40, 100, 40), (45, 55, 75), border_radius=6)
        fb = get_font(18, bold=True)
        if fb:
            surface.blit(fb.render("< BACK", True, COLOR_TEXT_LIGHT), (56, 48))

        f_hdr = get_font(36, bold=True)
        if f_hdr:
            t = f_hdr.render("CHAMPIONS CUP TOURNAMENT", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        # Bracket Cards
        draw_glass_panel(surface, (150, 160, 420, 120), border_radius=10)
        draw_glass_panel(surface, (150, 320, 420, 120), border_radius=10)
        draw_glass_panel(surface, (720, 240, 420, 140), border_radius=10)

        f_sub = get_font(20, bold=True)
        f_sml = get_font(16)
        if f_sub:
            surface.blit(f_sub.render("SEMI-FINAL 1", True, COLOR_PRIMARY), (170, 175))
            surface.blit(f_sub.render("SEMI-FINAL 2", True, COLOR_PRIMARY), (170, 335))
            surface.blit(f_sub.render("GRAND FINAL", True, COLOR_ACCENT), (740, 255))

        if f_sml:
            surface.blit(f_sml.render("India  vs  England", True, COLOR_TEXT_LIGHT), (170, 215))
            surface.blit(f_sml.render("Australia  vs  South Africa", True, COLOR_TEXT_LIGHT), (170, 375))
            surface.blit(f_sml.render("Winner SF1  vs  Winner SF2", True, COLOR_TEXT_MUTED), (740, 305))

        # Play match button
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 120, 580, 240, 50), (16, 185, 129), border_radius=10)
        if fb:
            surface.blit(fb.render("PLAY FIXTURE >", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 68, 595))

    # --- SETTINGS SCREEN ---
    def handle_settings_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state(STATE_MAIN_MENU)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Back
            if pygame.Rect(40, 40, 100, 40).collidepoint(mx, my):
                self.sound.play("click")
                self.game.change_state(STATE_MAIN_MENU)
                return

            # Toggle Sound
            if pygame.Rect(SCREEN_WIDTH // 2 + 80, 220, 120, 40).collidepoint(mx, my):
                new_snd = not self.settings.get("sound_enabled", True)
                self.settings.set("sound_enabled", new_snd)
                self.sound.set_enabled(new_snd)
                self.sound.play("click")

            # Toggle Screen Shake
            if pygame.Rect(SCREEN_WIDTH // 2 + 80, 280, 120, 40).collidepoint(mx, my):
                new_shake = not self.settings.get("screen_shake", True)
                self.settings.set("screen_shake", new_shake)
                self.sound.play("click")

            # Toggle Particles
            if pygame.Rect(SCREEN_WIDTH // 2 + 80, 340, 120, 40).collidepoint(mx, my):
                new_part = not self.settings.get("particles", True)
                self.settings.set("particles", new_part)
                self.sound.play("click")

            # Volume +/-
            if pygame.Rect(SCREEN_WIDTH // 2 + 80, 400, 40, 36).collidepoint(mx, my):
                v = max(0.0, self.settings.get("sfx_volume", 0.8) - 0.1)
                self.sound.update_volume(v, v)
                self.sound.play("click")
            elif pygame.Rect(SCREEN_WIDTH // 2 + 160, 400, 40, 36).collidepoint(mx, my):
                v = min(1.0, self.settings.get("sfx_volume", 0.8) + 0.1)
                self.sound.update_volume(v, v)
                self.sound.play("click")

    def draw_settings(self, surface):
        surface.fill(COLOR_BG_DARK)
        # Back
        draw_rounded_rect(surface, (40, 40, 100, 40), (45, 55, 75), border_radius=6)
        fb = get_font(18, bold=True)
        if fb:
            surface.blit(fb.render("< BACK", True, COLOR_TEXT_LIGHT), (56, 48))

        f_hdr = get_font(36, bold=True)
        if f_hdr:
            t = f_hdr.render("GAME SETTINGS", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 280, 160, 560, 340), border_radius=12)

        f_opt = get_font(20, bold=True)
        f_sml = get_font(16)
        y = 225

        # 1. Sound FX
        if f_opt:
            surface.blit(f_opt.render("Sound Effects & Crowd:", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 240, y + 8))
        snd_on = self.settings.get("sound_enabled", True)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 80, y, 120, 36), COLOR_SUCCESS if snd_on else COLOR_DANGER, border_radius=6)
        if f_sml:
            txt = "ENABLED" if snd_on else "MUTED"
            surface.blit(f_sml.render(txt, True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 105, y + 8))

        # 2. Screen Shake
        y += 60
        if f_opt:
            surface.blit(f_opt.render("Camera Screen Shake:", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 240, y + 8))
        shake_on = self.settings.get("screen_shake", True)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 80, y, 120, 36), COLOR_SUCCESS if shake_on else (80, 90, 100), border_radius=6)
        if f_sml:
            txt = "ON" if shake_on else "OFF"
            surface.blit(f_sml.render(txt, True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 125, y + 8))

        # 3. Particle FX
        y += 60
        if f_opt:
            surface.blit(f_opt.render("Boundary & Pitch Particles:", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 240, y + 8))
        part_on = self.settings.get("particles", True)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 80, y, 120, 36), COLOR_SUCCESS if part_on else (80, 90, 100), border_radius=6)
        if f_sml:
            txt = "ON" if part_on else "OFF"
            surface.blit(f_sml.render(txt, True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 125, y + 8))

        # 4. Volume level
        y += 60
        vol = self.settings.get("sfx_volume", 0.8)
        if f_opt:
            surface.blit(f_opt.render(f"SFX Volume: {int(vol*100)}%", True, COLOR_TEXT_LIGHT), (SCREEN_WIDTH // 2 - 240, y + 8))
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 80, y, 36, 36), (60, 75, 95), border_radius=6)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 160, y, 36, 36), (60, 75, 95), border_radius=6)
        if fb:
            surface.blit(fb.render("-", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 93, y + 6))
            surface.blit(fb.render("+", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 172, y + 6))

    # --- HOW TO PLAY SCREEN ---
    def handle_how_to_play_event(self, event):
        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or            (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
            self.sound.play("click")
            self.game.change_state(STATE_MAIN_MENU)

    def draw_how_to_play(self, surface):
        surface.fill(COLOR_BG_DARK)
        draw_glass_panel(surface, (120, 40, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 80), border_radius=12)

        f_hdr = get_font(32, bold=True)
        f_sub = get_font(20, bold=True)
        f_txt = get_font(16)

        if f_hdr:
            surface.blit(f_hdr.render("HOW TO PLAY - CONTROLS & RULES", True, COLOR_ACCENT), (160, 60))

        y = 120
        # Batting
        if f_sub:
            surface.blit(f_sub.render("1. BATTING CONTROLS", True, COLOR_PRIMARY), (160, y))
        y += 28
        bat_instructions = [
            "<- / -> or A / D : Shuffle left / right across the crease",
            "1 : Defensive Block       (drops ball at crease, safe)",
            "2 : Straight Drive        (straight down the ground)",
            "3 : Cover Drive           (pierces off-side covers)",
            "4 : Pull Shot             (swats through mid-wicket / leg-side)",
            "5 : Sweep Shot            (paddle sweep to fine leg)",
            "6 : Square Cut            (cuts through point / third man)",
            "7 : Lofted Shot           (aerial drive for MAXIMUM SIX!)",
            "Timing is crucial: Press the shot key as the ball enters your crease area!"
        ]
        for line in bat_instructions:
            if f_txt:
                surface.blit(f_txt.render(line, True, COLOR_TEXT_LIGHT), (180, y))
            y += 24

        y += 15
        # Bowling
        if f_sub:
            surface.blit(f_sub.render("2. BOWLING CONTROLS", True, COLOR_PRIMARY), (160, y))
        y += 28
        bowl_instructions = [
            "1: Fast Bowling (140-150 km/h)   2: Medium Pace (125-135 km/h)   3: Spin Bowling (85-98 km/h)",
            "SPACEBAR: Press when the moving accuracy meter hits the CENTER GREEN ZONE for maximum pace & precision!",
            "<- / -> : Adjust delivery target line across batsman's off/leg stump."
        ]
        for line in bowl_instructions:
            if f_txt:
                surface.blit(f_txt.render(line, True, COLOR_TEXT_LIGHT), (180, y))
            y += 24

        y += 15
        # General
        if f_sub:
            surface.blit(f_sub.render("3. MATCH & RULES", True, COLOR_PRIMARY), (160, y))
        y += 28
        rules = [
            "Wide / No-Ball adds 1 extra run and must be re-bowled.",
            "TAB: Toggle live full scorecard modal during play.  ESC: Pause game."
        ]
        for line in rules:
            if f_txt:
                surface.blit(f_txt.render(line, True, COLOR_TEXT_LIGHT), (180, y))
            y += 24

        # Click to return
        if f_txt:
            prompt = f_txt.render("Click anywhere or press [ESC] to return to Main Menu", True, COLOR_ACCENT)
            surface.blit(prompt, (SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT - 70))
