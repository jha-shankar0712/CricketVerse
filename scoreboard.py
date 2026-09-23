"""
scoreboard.py
-------------
Live broadcast cricket HUD, mini scorecard, over ball tracking,
partnership display, and full detailed scorecard modal.
"""

import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_PANEL_SOLID, COLOR_PANEL_BORDER,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_SUCCESS,
    COLOR_DANGER, COLOR_PRIMARY
)
from utils import get_font, draw_rounded_rect, draw_glass_panel

class Scoreboard:
    def __init__(self):
        self.show_full_scorecard = False

    def draw_hud(self, surface, match_data):
        """Draws top and bottom broadcast TV banners."""
        # Top banner: Score, Wickets, Overs, CRR, Target / RRR
        banner_rect = (SCREEN_WIDTH // 2 - 380, 12, 760, 48)
        draw_glass_panel(surface, banner_rect, border_radius=10)

        f_big = get_font(26, bold=True)
        f_mid = get_font(18, bold=True)
        f_sml = get_font(14, bold=False)

        batting_team = match_data["batting_team"]
        score_str = f"{batting_team}  {match_data['runs']}/{match_data['wickets']}"
        overs_str = f"Ovs: {match_data['overs']}.{match_data['balls_in_over']} / {match_data['max_overs']}"

        # Score & overs
        if f_big:
            s_surf = f_big.render(score_str, True, COLOR_ACCENT)
            surface.blit(s_surf, (banner_rect[0] + 16, banner_rect[1] + 10))

        if f_mid:
            ov_surf = f_mid.render(overs_str, True, COLOR_TEXT_LIGHT)
            surface.blit(ov_surf, (banner_rect[0] + 200, banner_rect[1] + 14))

        # CRR & Target
        crr = match_data["crr"]
        crr_str = f"CRR: {crr:.2f}"
        if match_data["target"] is not None:
            needed = max(0, match_data["target"] - match_data["runs"])
            rem_balls = (match_data["max_overs"] * 6) - (match_data["overs"] * 6 + match_data["balls_in_over"])
            rrr = (needed / (rem_balls / 6.0)) if rem_balls > 0 else 0.0
            stat_str = f"Target: {match_data['target']} (Need {needed} from {rem_balls}b, RRR: {rrr:.1f})"
        else:
            stat_str = f"{crr_str} | 1st Innings"

        if f_sml:
            stat_surf = f_sml.render(stat_str, True, COLOR_PRIMARY)
            surface.blit(stat_surf, (banner_rect[0] + 410, banner_rect[1] + 16))

        # Bottom Left: Batsmen on pitch
        bat_card_rect = (20, SCREEN_HEIGHT - 95, 340, 80)
        draw_glass_panel(surface, bat_card_rect, border_radius=8)
        striker = match_data["striker"]
        non_striker = match_data["non_striker"]
        if f_sml and striker and non_striker:
            s_name = f"*{striker.name}: {striker.runs} ({striker.balls}) [4s:{striker.fours} 6s:{striker.sixes}]"
            ns_name = f" {non_striker.name}: {non_striker.runs} ({non_striker.balls})"
            surface.blit(f_sml.render(s_name, True, COLOR_TEXT_LIGHT), (bat_card_rect[0] + 12, bat_card_rect[1] + 10))
            surface.blit(f_sml.render(ns_name, True, COLOR_TEXT_MUTED), (bat_card_rect[0] + 12, bat_card_rect[1] + 34))
            p_str = f"Partnership: {match_data.get('partnership_runs', 0)} ({match_data.get('partnership_balls', 0)}b)"
            surface.blit(f_sml.render(p_str, True, COLOR_ACCENT), (bat_card_rect[0] + 12, bat_card_rect[1] + 56))

        # Bottom Right: Current Bowler & Over timeline
        bowl_card_rect = (SCREEN_WIDTH - 380, SCREEN_HEIGHT - 95, 360, 80)
        draw_glass_panel(surface, bowl_card_rect, border_radius=8)
        bowler = match_data["bowler"]
        if f_sml and bowler:
            b_line = f"Bowler: {bowler.name} | {bowler.wickets_taken}/{bowler.runs_conceded} ({bowler.overs_bowled}.{bowler.balls_in_over})"
            surface.blit(f_sml.render(b_line, True, COLOR_TEXT_LIGHT), (bowl_card_rect[0] + 12, bowl_card_rect[1] + 10))

            # Ball timeline circles for current over
            this_over = match_data.get("this_over_balls", [])
            ox = bowl_card_rect[0] + 14
            oy = bowl_card_rect[1] + 40
            for ball_event in this_over:
                c_bg = (50, 70, 90)
                if "W" in ball_event:
                    c_bg = COLOR_DANGER
                elif ball_event in ("4", "6"):
                    c_bg = COLOR_SUCCESS
                pygame.draw.circle(surface, c_bg, (ox + 12, oy + 12), 12)
                t_b = f_sml.render(ball_event, True, COLOR_TEXT_LIGHT)
                t_rect = t_b.get_rect(center=(ox + 12, oy + 12))
                surface.blit(t_b, t_rect)
                ox += 28

        # Tab prompt for scorecard
        if f_sml:
            tab_prompt = f_sml.render("[TAB] Full Scorecard | [ESC] Pause", True, (160, 180, 200))
            surface.blit(tab_prompt, (SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT - 26))

    def draw_full_scorecard(self, surface, match):
        """Draws comprehensive scorecard overlay when TAB is toggled."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 25, 240))
        surface.blit(overlay, (0, 0))

        panel_rect = (160, 60, SCREEN_WIDTH - 320, SCREEN_HEIGHT - 120)
        draw_glass_panel(surface, panel_rect, border_radius=12)

        f_hdr = get_font(28, bold=True)
        f_sub = get_font(20, bold=True)
        f_row = get_font(16, bold=False)

        if f_hdr:
            t_surf = f_hdr.render("MATCH SCORECARD", True, COLOR_ACCENT)
            surface.blit(t_surf, (panel_rect[0] + 24, panel_rect[1] + 20))

        # Show current batting innings players
        y_pos = panel_rect[1] + 70
        if f_sub:
            col_hdr = f"{'BATSMAN':<24}{'RUNS':<8}{'BALLS':<8}{'4s':<6}{'6s':<6}{'SR':<8}{'STATUS'}"
            surface.blit(f_sub.render(col_hdr, True, COLOR_PRIMARY), (panel_rect[0] + 24, y_pos))
        y_pos += 30

        team_roster = match.batting_squad
        for p in team_roster[:11]:
            if p.balls > 0 or p.is_out or p == match.striker or p == match.non_striker:
                sr = (p.runs / p.balls * 100.0) if p.balls > 0 else 0.0
                row = f"{p.name:<24}{p.runs:<8}{p.balls:<8}{p.fours:<6}{p.sixes:<6}{sr:<8.1f}{p.dismissal}"
                c = COLOR_TEXT_LIGHT if not p.is_out else COLOR_TEXT_MUTED
                if f_row:
                    surface.blit(f_row.render(row, True, c), (panel_rect[0] + 24, y_pos))
                y_pos += 24

        # Close hint
        if f_row:
            hint = f_row.render("Press [TAB] or [ESC] to return to match", True, COLOR_ACCENT)
            surface.blit(hint, (panel_rect[0] + panel_rect[2] // 2 - 130, panel_rect[1] + panel_rect[3] - 35))
