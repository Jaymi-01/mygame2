"""User interface, HUD, level up card drafting modal, menus, and game over screen."""

import math
import pygame
from src.config import (
    CHARACTER_CLASSES,
    COLOR_ARCANE_CYAN,
    COLOR_GOLD,
    COLOR_HEALTH_GREEN,
    COLOR_HEALTH_RED,
    COLOR_WHITE,
    COLOR_XP_GEM,
    COLOR_XP_LEGENDARY,
    COLOR_XP_RARE,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from src.sprites import get_player_frames

# Catalog of available upgrades
UPGRADE_CATALOG = {
    "wand": {
        "title": "Arcane Missile",
        "category": "Weapon",
        "color": COLOR_ARCANE_CYAN,
        "rarity": "Common",
        "description": "Fires arcane energy bolts at nearby enemies. Increases bolt count and damage.",
    },
    "cleave": {
        "title": "Whirlwind Cleave",
        "category": "Weapon",
        "color": COLOR_HEALTH_RED,
        "rarity": "Rare",
        "description": "Swings a massive greatsword in a wide sweeping arc, violently slicing and throwing back foes.",
    },
    "orbit": {
        "title": "Orbiting Arc",
        "category": "Weapon",
        "color": (120, 240, 255),
        "rarity": "Rare",
        "description": "Conjures protective magical crystals that rotate and smash into incoming foes.",
    },
    "lightning": {
        "title": "Chain Lightning",
        "category": "Weapon",
        "color": (255, 230, 80),
        "rarity": "Epic",
        "description": "Strikes foes with high-voltage electricity that arcs between multiple enemies.",
    },
    "aura": {
        "title": "Blaze Aura",
        "category": "Weapon",
        "color": (255, 120, 30),
        "rarity": "Rare",
        "description": "Radiates an intense fiery aura that scorches all monsters near the player.",
    },
    "dagger": {
        "title": "Phantom Dagger",
        "category": "Weapon",
        "color": COLOR_GOLD,
        "rarity": "Common",
        "description": "Throws rapid-fire piercing daggers directly at the closest threat.",
    },
    "boots": {
        "title": "Phantom Boots",
        "category": "Passive",
        "color": (100, 220, 255),
        "rarity": "Common",
        "description": "Increases movement speed by +18%.",
    },
    "heart": {
        "title": "Iron Heart",
        "category": "Passive",
        "color": COLOR_HEALTH_RED,
        "rarity": "Common",
        "description": "Increases maximum health by +30 HP and heals 30 HP immediately.",
    },
    "quickcast": {
        "title": "Arcane Haste",
        "category": "Passive",
        "color": (180, 100, 255),
        "rarity": "Rare",
        "description": "Reduces weapon cooldowns by 15%, increasing attack rate.",
    },
    "crit": {
        "title": "Keen Senses",
        "category": "Passive",
        "color": COLOR_GOLD,
        "rarity": "Rare",
        "description": "Increases critical hit chance by +12% for devastating 2.5x damage.",
    },
    "magnet": {
        "title": "Aether Magnet",
        "category": "Passive",
        "color": (80, 200, 240),
        "rarity": "Common",
        "description": "Expands XP gem collection radius by +45%.",
    },
    "vampirism": {
        "title": "Soul Siphon",
        "category": "Passive",
        "color": (220, 60, 100),
        "rarity": "Epic",
        "description": "Grants an 8% chance to siphon 4 HP upon eliminating any monster.",
    },
    "regen": {
        "title": "Elder Regeneration",
        "category": "Passive",
        "color": COLOR_HEALTH_GREEN,
        "rarity": "Epic",
        "description": "Channel ancient vitality to passively regenerate +1.2 HP every second.",
    },
}


class UIManager:
    def __init__(self):
        self.font_title = None
        self.font_heading = None
        self.font_body = None
        self.font_small = None
        self._init_fonts()

        # Cached modal surfaces
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.hovered_card = -1

    def _init_fonts(self):
        try:
            self.font_title = pygame.font.Font(None, 64)
            self.font_heading = pygame.font.Font(None, 34)
            self.font_body = pygame.font.Font(None, 24)
            self.font_small = pygame.font.Font(None, 18)
        except Exception:
            pass

    def render_hud(self, surface: pygame.Surface, player, game_time: float):
        # 1. Top XP Bar
        bar_height = 14
        pygame.draw.rect(surface, (20, 18, 28), (0, 0, SCREEN_WIDTH, bar_height))
        xp_pct = min(1.0, max(0.0, player.current_xp / max(1, player.xp_to_next)))
        if xp_pct > 0:
            pygame.draw.rect(surface, COLOR_ARCANE_CYAN, (0, 0, int(SCREEN_WIDTH * xp_pct), bar_height))
            # Glowing right tip
            pygame.draw.line(surface, COLOR_WHITE, (int(SCREEN_WIDTH * xp_pct), 0), (int(SCREEN_WIDTH * xp_pct), bar_height), 2)
        pygame.draw.line(surface, (45, 40, 58), (0, bar_height), (SCREEN_WIDTH, bar_height), 1)

        # 2. Level Badge (Top Left)
        lvl_str = f"LVL {player.level}"
        lvl_surf = self.font_heading.render(lvl_str, True, COLOR_GOLD)
        surface.blit(lvl_surf, (20, 22))

        # XP Numbers below level
        xp_str = f"XP: {player.current_xp} / {player.xp_to_next}"
        xp_txt = self.font_small.render(xp_str, True, (180, 175, 195))
        surface.blit(xp_txt, (22, 54))

        # 3. Health Bar (Left, below Level)
        hp_x, hp_y = 150, 24
        hp_w, hp_h = 240, 22
        # HP background
        pygame.draw.rect(surface, (26, 20, 26), (hp_x, hp_y, hp_w, hp_h), border_radius=4)
        hp_pct = max(0.0, min(1.0, player.hp / max(1.0, player.max_hp)))
        fill_w = int(hp_w * hp_pct)
        if fill_w > 0:
            # Color shifts from green to red when low
            col = COLOR_HEALTH_GREEN if hp_pct > 0.45 else (COLOR_HEALTH_RED if hp_pct <= 0.25 else (240, 160, 40))
            pygame.draw.rect(surface, col, (hp_x, hp_y, fill_w, hp_h), border_radius=4)
        pygame.draw.rect(surface, (60, 55, 70), (hp_x, hp_y, hp_w, hp_h), width=2, border_radius=4)

        hp_txt = self.font_body.render(f"{int(player.hp)} / {int(player.max_hp)} HP", True, COLOR_WHITE)
        surface.blit(hp_txt, (hp_x + (hp_w - hp_txt.get_width()) // 2, hp_y + 2))

        # 4. Dash Status Indicator
        dash_x = hp_x + hp_w + 16
        dash_y = hp_y
        dash_ready = player.dash_cooldown_timer <= 0.0
        dash_col = COLOR_ARCANE_CYAN if dash_ready else (80, 75, 95)
        dash_txt = "DASH [SPACE]: READY" if dash_ready else f"DASH: {player.dash_cooldown_timer:.1f}s"
        dash_surf = self.font_body.render(dash_txt, True, dash_col)
        surface.blit(dash_surf, (dash_x, dash_y + 3))

        # 5. Survival Clock (Top Center)
        mins = int(game_time // 60)
        secs = int(game_time % 60)
        time_str = f"{mins:02d}:{secs:02d}"
        time_surf = self.font_title.render(time_str, True, COLOR_WHITE)
        surface.blit(time_surf, (SCREEN_WIDTH // 2 - time_surf.get_width() // 2, 20))

        # 6. Kill Count (Top Right)
        kills_str = f"Kills: {player.total_kills}"
        kills_surf = self.font_heading.render(kills_str, True, (240, 100, 100))
        surface.blit(kills_surf, (SCREEN_WIDTH - kills_surf.get_width() - 25, 24))

        # 7. Active Skills & Weapons Icons (Bottom Left)
        self._render_active_equipment(surface, player)

    def _render_active_equipment(self, surface: pygame.Surface, player):
        slots = [
            ("Arcane Wand", player.weapons.wand_level, COLOR_ARCANE_CYAN),
            ("Cleave", player.weapons.cleave_level, COLOR_HEALTH_RED),
            ("Orbit Blade", player.weapons.orbit_level, (120, 240, 255)),
            ("Lightning", player.weapons.lightning_level, (255, 230, 80)),
            ("Blaze Aura", player.weapons.aura_level, (255, 120, 30)),
            ("Dagger", player.weapons.dagger_level, COLOR_GOLD),
        ]
        start_x = 20
        start_y = SCREEN_HEIGHT - 45
        for name, lvl, col in slots:
            if lvl > 0:
                tag = f"{name} L{lvl}"
                txt = self.font_small.render(tag, True, col)
                rect = txt.get_rect(topleft=(start_x, start_y))
                bg_rect = rect.inflate(12, 8)
                pygame.draw.rect(surface, (20, 18, 30, 200), bg_rect, border_radius=4)
                pygame.draw.rect(surface, col, bg_rect, width=1, border_radius=4)
                surface.blit(txt, (start_x, start_y))
                start_x += bg_rect.width + 10

    def render_level_up_modal(self, surface: pygame.Surface, options: list[str], mouse_pos: tuple):
        # Dark dim background
        self.overlay.fill((10, 8, 16, 210))
        surface.blit(self.overlay, (0, 0))

        # Header Title
        title_surf = self.font_title.render("LEVEL UP!", True, COLOR_GOLD)
        subtitle_surf = self.font_heading.render("Choose an Arcane Blessing", True, COLOR_WHITE)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 85))
        surface.blit(subtitle_surf, (SCREEN_WIDTH // 2 - subtitle_surf.get_width() // 2, 145))

        # Render 3 Upgrade Cards
        card_w = 260
        card_h = 360
        gap = 40
        total_w = len(options) * card_w + (len(options) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 210

        self.hovered_card = -1
        mx, my = mouse_pos

        for idx, key in enumerate(options):
            info = UPGRADE_CATALOG.get(key, {})
            cx = start_x + idx * (card_w + gap)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            is_hovered = card_rect.collidepoint(mx, my)
            if is_hovered:
                self.hovered_card = idx
                # Lift up slightly on hover
                card_rect.y -= 8

            # Rarity border color
            rarity = info.get("rarity", "Common")
            border_col = COLOR_GOLD if rarity == "Epic" else ((220, 100, 255) if rarity == "Rare" else COLOR_ARCANE_CYAN)
            bg_col = (34, 30, 48) if is_hovered else (24, 21, 35)

            # Draw card body
            pygame.draw.rect(surface, bg_col, card_rect, border_radius=12)
            pygame.draw.rect(surface, border_col, card_rect, width=3 if is_hovered else 2, border_radius=12)

            # Key prompt [1], [2], [3]
            num_surf = self.font_heading.render(f"[{idx + 1}]", True, border_col)
            surface.blit(num_surf, (card_rect.x + 18, card_rect.y + 16))

            # Rarity Tag
            rarity_surf = self.font_small.render(rarity.upper(), True, border_col)
            surface.blit(rarity_surf, (card_rect.right - rarity_surf.get_width() - 18, card_rect.y + 22))

            # Upgrade Title
            name_surf = self.font_heading.render(info.get("title", key), True, COLOR_WHITE)
            surface.blit(name_surf, (card_rect.x + 18, card_rect.y + 70))

            # Category
            cat_surf = self.font_small.render(info.get("category", "Upgrade"), True, (160, 155, 180))
            surface.blit(cat_surf, (card_rect.x + 18, card_rect.y + 105))

            # Divider line
            pygame.draw.line(
                surface,
                (55, 50, 75),
                (card_rect.x + 18, card_rect.y + 130),
                (card_rect.right - 18, card_rect.y + 130),
                1,
            )

            # Description (word wrapped)
            desc = info.get("description", "")
            self._render_wrapped_text(surface, desc, card_rect.x + 18, card_rect.y + 150, card_w - 36, self.font_body)

            # Select button hint
            hint_txt = "CLICK TO SELECT" if is_hovered else f"PRESS [{idx + 1}]"
            hint_col = COLOR_GOLD if is_hovered else (140, 135, 160)
            hint_surf = self.font_body.render(hint_txt, True, hint_col)
            surface.blit(hint_surf, (card_rect.centerx - hint_surf.get_width() // 2, card_rect.bottom - 36))

    def _render_wrapped_text(self, surface: pygame.Surface, text: str, x: int, y: int, max_width: int, font):
        words = text.split(" ")
        line = ""
        current_y = y
        line_height = font.get_linesize() + 4

        for word in words:
            test_line = line + (" " if line else "") + word
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                txt_surf = font.render(line, True, (215, 210, 225))
                surface.blit(txt_surf, (x, current_y))
                current_y += line_height
                line = word

        if line:
            txt_surf = font.render(line, True, (215, 210, 225))
            surface.blit(txt_surf, (x, current_y))

    def render_game_over(self, surface: pygame.Surface, player, game_time: float, victory: bool = False):
        self.overlay.fill((10, 8, 16, 235))
        surface.blit(self.overlay, (0, 0))

        title_text = "VICTORY ACHIEVED!" if victory else "YOU HAVE FALLEN"
        title_col = COLOR_GOLD if victory else COLOR_HEALTH_RED
        title_surf = self.font_title.render(title_text, True, title_col)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 140))

        # Stats Card
        mins = int(game_time // 60)
        secs = int(game_time % 60)
        stats = [
            f"Survival Time:  {mins:02d}:{secs:02d}",
            f"Monsters Defeated:  {player.total_kills}",
            f"Level Reached:  {player.level}",
        ]

        stat_y = 250
        for s in stats:
            surf = self.font_heading.render(s, True, COLOR_WHITE)
            surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, stat_y))
            stat_y += 45

        # Restart Prompt
        prompt = self.font_heading.render("Press ENTER or SPACE to Play Again  |  ESC for Menu", True, COLOR_ARCANE_CYAN)
        surface.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 450))

    def render_main_menu(self, surface: pygame.Surface):
        self.overlay.fill((14, 12, 20, 245))
        surface.blit(self.overlay, (0, 0))

        # Title
        t1 = self.font_title.render("CRYPT SURVIVOR", True, COLOR_GOLD)
        t2 = self.font_heading.render("Arcane Depths", True, COLOR_ARCANE_CYAN)
        surface.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, 130))
        surface.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, 200))

        # How to play
        instructions = [
            "CONTROLS:",
            "WASD / Arrow Keys : Move Hero",
            "SPACEBAR : Dash / Dodge Roll (Invulnerable)",
            "Weapons automatically target nearest monsters!",
            "Collect XP Gems to Level Up and unlock game-breaking builds.",
            "Survive the waves and face Archlich Malakor!",
        ]
        iy = 280
        for line in instructions:
            col = COLOR_GOLD if line.startswith("CONTROLS:") else (210, 205, 225)
            s = self.font_body.render(line, True, col)
            surface.blit(s, (SCREEN_WIDTH // 2 - s.get_width() // 2, iy))
            iy += 30

        # Start / Exit button hints
        start_txt = self.font_heading.render("Press ENTER or SPACE to Choose Hero", True, COLOR_ARCANE_CYAN)
        surface.blit(start_txt, (SCREEN_WIDTH // 2 - start_txt.get_width() // 2, 530))

        exit_txt = self.font_body.render("Press ESC to Exit", True, (140, 135, 155))
        surface.blit(exit_txt, (SCREEN_WIDTH // 2 - exit_txt.get_width() // 2, 575))

    def render_class_select(self, surface: pygame.Surface, selected_idx: int, mouse_pos: tuple, anim_tick: float = 0.0) -> int:
        """Renders interactive class selection screen with animated hero previews and stat cards."""
        self.overlay.fill((12, 10, 18, 245))
        surface.blit(self.overlay, (0, 0))

        # Title & Subtitle
        title = self.font_title.render("CHOOSE YOUR HERO", True, COLOR_GOLD)
        subtitle = self.font_body.render("Select a champion to delve into the Arcane Depths", True, COLOR_ARCANE_CYAN)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 35))
        surface.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 95))

        class_keys = ["mage", "warrior", "assassin", "tank"]
        card_w = 265
        card_h = 475
        gap = 22
        total_w = len(class_keys) * card_w + (len(class_keys) - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        card_y = 135

        hovered_idx = selected_idx
        mx, my = mouse_pos

        for idx, ckey in enumerate(class_keys):
            cinfo = CHARACTER_CLASSES[ckey]
            cx = start_x + idx * (card_w + gap)
            card_rect = pygame.Rect(cx, card_y, card_w, card_h)

            is_mouse_over = card_rect.collidepoint(mx, my)
            is_active = (idx == selected_idx) or is_mouse_over
            if is_mouse_over:
                hovered_idx = idx

            # Hover lift
            if is_active:
                card_rect.y -= 8

            # Background & border
            border_col = cinfo["color"]
            bg_col = (36, 30, 50) if is_active else (24, 20, 34)
            pygame.draw.rect(surface, bg_col, card_rect, border_radius=14)
            pygame.draw.rect(surface, border_col if is_active else (60, 52, 76), card_rect, width=3 if is_active else 2, border_radius=14)

            # Hotkey Badge [1], [2], [3], [4]
            badge_surf = self.font_heading.render(f"[{idx + 1}]", True, border_col)
            surface.blit(badge_surf, (card_rect.x + 16, card_rect.y + 14))

            # Hero Pedestal Circle & Animated Sprite
            pedestal_center = (card_rect.centerx, card_rect.y + 70)
            pygame.draw.circle(surface, (18, 15, 26), pedestal_center, 36)
            pygame.draw.circle(surface, border_col, pedestal_center, 36, width=2)

            frames = get_player_frames(ckey)
            curr_frame = frames[int(anim_tick * 6.0) % len(frames)]
            scaled_w = int(curr_frame.get_width() * 1.5)
            scaled_h = int(curr_frame.get_height() * 1.5)
            scaled_sprite = pygame.transform.scale(curr_frame, (scaled_w, scaled_h))
            surface.blit(scaled_sprite, (pedestal_center[0] - scaled_w // 2, pedestal_center[1] - scaled_h // 2))

            # Class Name
            name_surf = self.font_heading.render(cinfo["name"], True, COLOR_WHITE)
            surface.blit(name_surf, (card_rect.centerx - name_surf.get_width() // 2, card_rect.y + 118))

            # Class Title
            title_surf = self.font_small.render(cinfo["title"], True, border_col)
            surface.blit(title_surf, (card_rect.centerx - title_surf.get_width() // 2, card_rect.y + 148))

            # Divider
            pygame.draw.line(surface, (55, 48, 72), (card_rect.x + 16, card_rect.y + 168), (card_rect.right - 16, card_rect.y + 168), 1)

            # Starting Weapon Tag
            weap_tag = f"Weapon: {cinfo['icon_desc']}"
            weap_surf = self.font_body.render(weap_tag, True, (240, 230, 160))
            surface.blit(weap_surf, (card_rect.centerx - weap_surf.get_width() // 2, card_rect.y + 178))

            # Stats Grid (HP, SPD, DMG, CRIT)
            stats = [
                ("Health (HP)", f"{int(cinfo['hp'])}", COLOR_HEALTH_RED),
                ("Movement Speed", f"{int(cinfo['speed'])}", COLOR_ARCANE_CYAN),
                ("Damage Power", f"{int(cinfo['damage_multiplier']*100)}%", COLOR_GOLD),
                ("Crit Chance", f"{int(cinfo['crit_chance']*100)}%", (80, 240, 140)),
            ]
            sy = card_rect.y + 208
            for s_name, s_val, s_col in stats:
                lbl = self.font_small.render(s_name, True, (160, 155, 175))
                val = self.font_small.render(s_val, True, s_col)
                surface.blit(lbl, (card_rect.x + 20, sy))
                surface.blit(val, (card_rect.right - 20 - val.get_width(), sy))
                sy += 22

            # Divider
            pygame.draw.line(surface, (55, 48, 72), (card_rect.x + 16, sy + 6), (card_rect.right - 16, sy + 6), 1)

            # Passive Blessing
            pass_title = self.font_small.render("PASSIVE PERKS:", True, COLOR_GOLD)
            surface.blit(pass_title, (card_rect.x + 20, sy + 14))
            self._render_wrapped_text(surface, cinfo["passive_desc"], card_rect.x + 20, sy + 32, card_w - 40, self.font_small)

            # Action / Select Prompt
            btn_txt = "CLICK TO SELECT" if is_active else f"PRESS [{idx + 1}]"
            btn_col = COLOR_GOLD if is_active else (130, 125, 145)
            btn_surf = self.font_body.render(btn_txt, True, btn_col)
            surface.blit(btn_surf, (card_rect.centerx - btn_surf.get_width() // 2, card_rect.bottom - 34))

        # Bottom Navigation Hint
        hint = self.font_body.render(
            "Use [1-4] or Click to Pick  |  [A]/[D] to Browse  |  ENTER to Play  |  ESC for Menu",
            True,
            (175, 170, 195),
        )
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 42))

        return hovered_idx
