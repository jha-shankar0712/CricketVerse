"""
game.py
-------
Master game controller: manages window, clock, top-level state machine,
pause overlay, post-match presentation screen, and practice mode.
"""

import pygame
import sys
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    COLOR_BG_DARK, COLOR_PANEL_SOLID, COLOR_PANEL_BORDER,
    COLOR_PRIMARY, COLOR_ACCENT, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    STATE_MAIN_MENU, STATE_MATCH_SETUP, STATE_TOSS, STATE_MATCH,
    STATE_PRACTICE, STATE_TOURNAMENT, STATE_SETTINGS, STATE_HOW_TO_PLAY, STATE_RESULT,
    STATE_PAUSE, TEAMS_DATA
)
from settings import Settings
from sound import SoundManager
from camera import Camera
from animation import ParticleManager
from menu import MenuManager
from match import Match
from utils import get_font, Button, draw_rounded_rect, draw_glass_panel

class Game:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.sound = SoundManager(self.settings)
        self.camera = Camera(enabled=self.settings.get("screen_shake", True))
        self.particles = ParticleManager(enabled=self.settings.get("particles", True))

        # Setup display surface
        self.fullscreen = self.settings.get("fullscreen", False)
        flags = pygame.FULLSCREEN if self.fullscreen else 0
        try:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        except Exception as e:
            print(f"[Game] Warning: Display mode error ({e}). Falling back to default window.")
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # State Management
        self.state = STATE_MAIN_MENU
        self.previous_state = None
        self.menu_manager = MenuManager(self)
        self.current_match = None
        self.match_result = None

        # Pause menu buttons
        cx = SCREEN_WIDTH // 2 - 120
        self.pause_buttons = [
            Button((cx, 260, 240, 48), "RESUME", 22, bg_color=(2, 132, 199), on_click=self.resume_game),
            Button((cx, 325, 240, 48), "RESTART MATCH", 22, bg_color=(217, 119, 6), on_click=self.restart_match),
            Button((cx, 390, 240, 48), "MAIN MENU", 22, bg_color=(220, 38, 38), on_click=self.exit_to_main_menu)
        ]

    def change_state(self, new_state):
        self.previous_state = self.state
        self.state = new_state

    def start_match(self, player_team="IND", opponent_team="AUS", max_overs=5,
                    difficulty="Medium", stadium="MCG", user_bats_first=True):
        self.current_match = Match(
            player_team=player_team,
            opponent_team=opponent_team,
            max_overs=max_overs,
            difficulty=difficulty,
            stadium=stadium,
            user_bats_first=user_bats_first,
            sound=self.sound,
            settings=self.settings,
            camera=self.camera,
            particles=self.particles,
            on_finish=self.handle_match_result
        )
        self.state = STATE_MATCH

    def start_practice(self):
        self.current_match = Match(
            player_team="IND",
            opponent_team="AUS",
            max_overs=20,
            difficulty="Medium",
            stadium="WANKHEDE",
            user_bats_first=True,
            sound=self.sound,
            settings=self.settings,
            camera=self.camera,
            particles=self.particles,
            is_practice=True,
            on_finish=self.handle_match_result
        )
        self.state = STATE_MATCH

    def handle_match_result(self, result_data):
        self.match_result = result_data
        self.state = STATE_RESULT
        if self.sound:
            self.sound.play("boundary")

    def resume_game(self):
        if self.previous_state:
            self.state = self.previous_state
        else:
            self.state = STATE_MATCH

    def restart_match(self):
        if self.current_match:
            self.start_match(
                player_team=self.current_match.player_team_key,
                opponent_team=self.current_match.opponent_team_key,
                max_overs=self.current_match.max_overs,
                difficulty=self.current_match.difficulty,
                stadium=self.current_match.stadium_key,
                user_bats_first=self.current_match.user_bats_first
            )

    def exit_to_main_menu(self):
        self.current_match = None
        self.state = STATE_MAIN_MENU

    def quit_game(self):
        self.running = False

    def run(self):
        """Core application loop."""
        while self.running:
            self.clock.tick(FPS)
            self.camera.update()
            if self.particles:
                self.particles.update()

            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_game()
                return

            if self.state == STATE_PAUSE:
                for btn in self.pause_buttons:
                    btn.handle_event(event, self.sound)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.resume_game()
                continue

            if self.state == STATE_MATCH:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.previous_state = STATE_MATCH
                    self.state = STATE_PAUSE
                    return
                if self.current_match:
                    self.current_match.handle_event(event)

            elif self.state == STATE_MAIN_MENU:
                self.menu_manager.handle_main_menu_event(event)
            elif self.state == STATE_MATCH_SETUP:
                self.menu_manager.handle_setup_event(event)
            elif self.state == STATE_TOSS:
                self.menu_manager.handle_toss_event(event)
            elif self.state == STATE_SETTINGS:
                self.menu_manager.handle_settings_event(event)
            elif self.state == STATE_HOW_TO_PLAY:
                self.menu_manager.handle_how_to_play_event(event)
            elif self.state == STATE_TOURNAMENT:
                self.menu_manager.handle_tournament_event(event)
            elif self.state == STATE_RESULT:
                self._handle_result_event(event)

    def _update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.state == STATE_MAIN_MENU:
            self.menu_manager.update_main_menu(mouse_pos)
        elif self.state == STATE_TOSS:
            self.menu_manager.update_toss()
        elif self.state == STATE_MATCH and self.current_match:
            self.current_match.update()
        elif self.state == STATE_PAUSE:
            for btn in self.pause_buttons:
                btn.update(mouse_pos)

    def _draw(self):
        if self.state == STATE_MAIN_MENU:
            self.menu_manager.draw_main_menu(self.screen)
        elif self.state == STATE_MATCH_SETUP:
            self.menu_manager.draw_match_setup(self.screen)
        elif self.state == STATE_TOSS:
            self.menu_manager.draw_toss(self.screen)
        elif self.state == STATE_MATCH and self.current_match:
            self.current_match.draw(self.screen)
        elif self.state == STATE_TOURNAMENT:
            self.menu_manager.draw_tournament(self.screen)
        elif self.state == STATE_SETTINGS:
            self.menu_manager.draw_settings(self.screen)
        elif self.state == STATE_HOW_TO_PLAY:
            self.menu_manager.draw_how_to_play(self.screen)
        elif self.state == STATE_RESULT:
            self._draw_result_screen(self.screen)
        elif self.state == STATE_PAUSE:
            if self.current_match:
                self.current_match.draw(self.screen)
            self._draw_pause_overlay(self.screen)

    def _draw_pause_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 210))
        surface.blit(overlay, (0, 0))

        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 180, 170, 360, 340), border_radius=12)
        f_hdr = get_font(36, bold=True)
        if f_hdr:
            t = f_hdr.render("GAME PAUSED", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 210)))

        for btn in self.pause_buttons:
            btn.draw(surface)

    def _handle_result_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Rematch
            if pygame.Rect(SCREEN_WIDTH // 2 - 210, 600, 190, 50).collidepoint(mx, my):
                self.sound.play("click")
                self.restart_match()
            # Main Menu
            elif pygame.Rect(SCREEN_WIDTH // 2 + 20, 600, 190, 50).collidepoint(mx, my):
                self.sound.play("click")
                self.exit_to_main_menu()

    def _draw_result_screen(self, surface):
        surface.fill(COLOR_BG_DARK)
        if not self.match_result:
            return

        f_hdr = get_font(42, bold=True)
        f_win = get_font(32, bold=True)
        f_sub = get_font(20, bold=True)
        f_txt = get_font(16)

        # Presentation Header
        if f_hdr:
            t = f_hdr.render("POST-MATCH PRESENTATION", True, COLOR_ACCENT)
            surface.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        # Winner Announcement Card
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 340, 95, 680, 110), border_radius=12)
        winner = self.match_result["winner"]
        margin = self.match_result["margin"]
        if f_win:
            w_str = f"VICTORIOUS: {TEAMS_DATA.get(winner, {}).get('name', winner).upper()}"
            w_surf = f_win.render(w_str, True, COLOR_SUCCESS)
            surface.blit(w_surf, w_surf.get_rect(center=(SCREEN_WIDTH // 2, 130)))
        if f_sub:
            m_surf = f_sub.render(f"Won by {margin}", True, COLOR_TEXT_LIGHT)
            surface.blit(m_surf, m_surf.get_rect(center=(SCREEN_WIDTH // 2, 172)))

        # Match Summary Breakdown Panels
        inn1 = self.match_result.get("innings1")
        inn2 = self.match_result.get("innings2")

        draw_glass_panel(surface, (120, 230, 480, 200), border_radius=10)
        draw_glass_panel(surface, (680, 230, 480, 200), border_radius=10)

        if f_sub and inn1 and inn2:
            surface.blit(f_sub.render(f"1st Innings: {inn1['team']}", True, COLOR_PRIMARY), (145, 245))
            surface.blit(f_sub.render(f"Score: {inn1['runs']}/{inn1['wickets']} ({inn1['overs']}.{inn1['balls']} ovs)", True, COLOR_TEXT_LIGHT), (145, 280))

            surface.blit(f_sub.render(f"2nd Innings: {inn2['team']}", True, COLOR_PRIMARY), (705, 245))
            surface.blit(f_sub.render(f"Score: {inn2['runs']}/{inn2['wickets']} ({inn2['overs']}.{inn2['balls']} ovs)", True, COLOR_TEXT_LIGHT), (705, 280))

        # Player of the match card
        draw_glass_panel(surface, (SCREEN_WIDTH // 2 - 280, 455, 560, 115), border_radius=10)
        if f_sub:
            surface.blit(f_sub.render("PLAYER OF THE MATCH AWARD", True, COLOR_ACCENT), (SCREEN_WIDTH // 2 - 160, 470))
        if f_txt:
            surface.blit(f_txt.render("Outstanding all-round performance with bat and ball!", True, COLOR_TEXT_MUTED), (SCREEN_WIDTH // 2 - 190, 502))
            surface.blit(f_txt.render("Awarded Golden Willow Trophy & Match Medallion", True, COLOR_SUCCESS), (SCREEN_WIDTH // 2 - 180, 526))

        # Bottom Buttons
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 - 210, 600, 190, 50), (16, 185, 129), border_radius=8)
        draw_rounded_rect(surface, (SCREEN_WIDTH // 2 + 20, 600, 190, 50), (71, 85, 105), border_radius=8)
        if f_sub:
            surface.blit(f_sub.render("PLAY AGAIN", True, (255, 255, 255)), (SCREEN_WIDTH // 2 - 168, 613))
            surface.blit(f_sub.render("MAIN MENU", True, (255, 255, 255)), (SCREEN_WIDTH // 2 + 62, 613))
