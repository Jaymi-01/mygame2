"""Procedural sprite generation for players, enemies, projectiles, items, and dungeon props."""

import math
import pygame
from src.config import (
    COLOR_ARCANE_BLUE,
    COLOR_ARCANE_CYAN,
    COLOR_FIRE_ORANGE,
    COLOR_GOLD,
    COLOR_HEALTH_RED,
    COLOR_WHITE,
    COLOR_XP_GEM,
    COLOR_XP_LEGENDARY,
    COLOR_XP_RARE,
)

# Global sprite cache
_SPRITE_CACHE = {}


def create_drop_shadow(width: int, height: int, alpha: int = 90) -> pygame.Surface:
    """Creates a soft elliptical drop shadow."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, (10, 8, 16, alpha), (0, 0, width, height))
    return surf


def get_player_frames(class_id: str = "mage") -> list[pygame.Surface]:
    """Generates animated walking/idle frames for chosen hero class."""
    key = f"player_frames_{class_id}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    frames = []
    size = 44 if class_id == "tank" else (42 if class_id == "warrior" else 40)

    for frame_idx in range(4):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        bob = math.sin(frame_idx * (math.pi / 2)) * 2.0
        hand_bob = math.cos(frame_idx * (math.pi / 2)) * 3.0

        if class_id == "mage":
            # --- ARCANE MAGE ---
            # Shadow
            surf.blit(create_drop_shadow(26, 10), (7, size - 11))

            # Robe / Body (Midnight blue/violet mantle)
            robe_pts = [
                (14, 18 + bob),
                (26, 18 + bob),
                (31, 35),
                (9, 35),
            ]
            pygame.draw.polygon(surf, (36, 32, 64), robe_pts)
            pygame.draw.polygon(surf, (60, 52, 98), robe_pts, width=2)

            # Golden sash / Belt
            pygame.draw.rect(surf, (220, 180, 50), (12, int(26 + bob), 16, 3))
            pygame.draw.circle(surf, (255, 230, 100), (20, int(27 + bob)), 3)

            # Hood
            pygame.draw.circle(surf, (28, 24, 48), (20, int(15 + bob)), 9)
            pygame.draw.circle(surf, (70, 60, 110), (20, int(15 + bob)), 9, width=2)

            # Glowing Arcane Eyes
            eye_y = int(14 + bob)
            pygame.draw.circle(surf, (180, 255, 255), (17, eye_y), 2)
            pygame.draw.circle(surf, (180, 255, 255), (23, eye_y), 2)

            # Arcane Staff
            staff_x = 31
            staff_top = int(8 + hand_bob)
            pygame.draw.line(surf, (140, 95, 50), (staff_x, staff_top), (staff_x, 34), 3)
            pygame.draw.circle(surf, (60, 220, 255), (staff_x, staff_top), 4)
            pygame.draw.circle(surf, (220, 255, 255), (staff_x, staff_top), 2)

        elif class_id == "warrior":
            # --- BERSERKER / WARRIOR ---
            surf.blit(create_drop_shadow(30, 10), (6, size - 11))

            # Flowing Crimson Battle Cape
            cape_pts = [(10, int(18 + bob)), (32, int(18 + bob)), (36, 37), (6, 37)]
            pygame.draw.polygon(surf, (180, 30, 45), cape_pts)

            # Steel Plate Armor Torso
            torso_rect = pygame.Rect(13, int(18 + bob), 16, 15)
            pygame.draw.rect(surf, (160, 165, 180), torso_rect, border_radius=4)
            pygame.draw.rect(surf, (90, 95, 110), torso_rect, width=2, border_radius=4)

            # Gold Emblem on Chest
            pygame.draw.circle(surf, (240, 190, 40), (21, int(24 + bob)), 3)

            # Steel Helm with Horns
            pygame.draw.circle(surf, (150, 155, 170), (21, int(13 + bob)), 9)
            pygame.draw.circle(surf, (80, 85, 95), (21, int(13 + bob)), 9, width=2)
            # Horns
            pygame.draw.polygon(surf, (220, 180, 50), [(14, int(11 + bob)), (9, int(4 + bob)), (16, int(8 + bob))])
            pygame.draw.polygon(surf, (220, 180, 50), [(28, int(11 + bob)), (33, int(4 + bob)), (26, int(8 + bob))])

            # Fierce Eye Slit
            pygame.draw.rect(surf, (255, 60, 60), (17, int(13 + bob), 8, 2))

            # Broadsword in Hand
            sword_top = int(4 + hand_bob)
            sword_x = 34
            pygame.draw.line(surf, (220, 225, 235), (sword_x, sword_top), (sword_x, 32), 4)
            pygame.draw.line(surf, (255, 255, 255), (sword_x, sword_top + 2), (sword_x, 30), 2)
            # Crossguard & Pommel
            pygame.draw.line(surf, (200, 160, 40), (sword_x - 4, sword_top + 18), (sword_x + 4, sword_top + 18), 3)
            pygame.draw.circle(surf, (200, 160, 40), (sword_x, sword_top + 24), 2)

        elif class_id == "assassin":
            # --- SHADOW ROGUE / ASSASSIN ---
            surf.blit(create_drop_shadow(24, 8), (8, size - 10))

            # Obsidian Stealth Tunic
            tunic_pts = [(13, int(17 + bob)), (27, int(17 + bob)), (30, 34), (10, 34)]
            pygame.draw.polygon(surf, (25, 22, 34), tunic_pts)
            pygame.draw.polygon(surf, (55, 48, 72), tunic_pts, width=1)

            # Leather Wrap Belts
            pygame.draw.line(surf, (110, 80, 60), (12, int(25 + bob)), (28, int(25 + bob)), 2)

            # Dark Cowl / Hood
            pygame.draw.circle(surf, (20, 18, 28), (20, int(13 + bob)), 8)
            pygame.draw.circle(surf, (45, 40, 60), (20, int(13 + bob)), 8, width=1)

            # Piercing Jade Green Eyes
            eye_y = int(13 + bob)
            pygame.draw.circle(surf, (80, 255, 140), (17, eye_y), 2)
            pygame.draw.circle(surf, (80, 255, 140), (23, eye_y), 2)

            # Dual Poison Daggers (one left, one right)
            # Right dagger
            rd_y = int(14 + hand_bob)
            pygame.draw.line(surf, (80, 240, 150), (32, rd_y), (32, rd_y + 12), 3)
            pygame.draw.circle(surf, (200, 255, 210), (32, rd_y), 1)
            # Left dagger
            ld_y = int(16 - hand_bob)
            pygame.draw.line(surf, (80, 240, 150), (8, ld_y), (8, ld_y + 12), 3)
            pygame.draw.circle(surf, (200, 255, 210), (8, ld_y), 1)

        elif class_id == "tank":
            # --- IRON JUGGERNAUT / PALADIN ---
            surf.blit(create_drop_shadow(36, 12), (4, size - 12))

            # Heavy Golden Pauldrons & Cuirass
            plate_rect = pygame.Rect(12, int(18 + bob), 20, 18)
            pygame.draw.rect(surf, (215, 175, 45), plate_rect, border_radius=5)
            pygame.draw.rect(surf, (255, 225, 90), plate_rect, width=2, border_radius=5)

            # White Crusader Tabard
            tabard_pts = [(16, int(18 + bob)), (28, int(18 + bob)), (27, 36), (17, 36)]
            pygame.draw.polygon(surf, (240, 240, 250), tabard_pts)
            # Golden Cross on Tabard
            pygame.draw.line(surf, (215, 160, 30), (22, int(20 + bob)), (22, int(30 + bob)), 2)
            pygame.draw.line(surf, (215, 160, 30), (19, int(24 + bob)), (25, int(24 + bob)), 2)

            # Bulky Greathelm
            pygame.draw.circle(surf, (200, 165, 40), (22, int(13 + bob)), 10)
            pygame.draw.circle(surf, (255, 230, 100), (22, int(13 + bob)), 10, width=2)
            # Visor Cross Slit
            pygame.draw.line(surf, (30, 25, 35), (18, int(14 + bob)), (26, int(14 + bob)), 2)
            pygame.draw.line(surf, (30, 25, 35), (22, int(10 + bob)), (22, int(17 + bob)), 2)

            # Massive Tower Kite Shield in hand
            shield_x = 34
            shield_y = int(14 + hand_bob)
            shield_w, shield_h = 10, 22
            shield_rect = pygame.Rect(shield_x - 3, shield_y, shield_w, shield_h)
            pygame.draw.rect(surf, (225, 185, 50), shield_rect, border_radius=3)
            pygame.draw.rect(surf, (255, 240, 140), shield_rect, width=2, border_radius=3)
            # Shield Gem
            pygame.draw.circle(surf, (60, 160, 255), (shield_x + 2, shield_y + 11), 3)

        frames.append(surf)

    _SPRITE_CACHE[key] = frames
    return frames


def get_enemy_frames(enemy_type: str) -> list[pygame.Surface]:
    """Generates procedural sprite animations for different monster types."""
    key = f"enemy_{enemy_type}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    frames = []

    if enemy_type == "slime":
        # Acidic Slime
        for f in range(4):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            squish = math.sin(f * (math.pi / 2)) * 3.0
            w = int(24 + squish)
            h = int(18 - squish)
            x = (32 - w) // 2
            y = 32 - h - 3

            # Drop shadow
            shadow = create_drop_shadow(w + 4, 8)
            surf.blit(shadow, (x - 2, 23))

            # Slime body
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.ellipse(surf, (40, 190, 70), rect)
            pygame.draw.ellipse(surf, (90, 240, 120), rect, width=2)
            # Inner glow
            pygame.draw.ellipse(surf, (150, 255, 170), (x + 4, y + 3, w - 8, h - 8))
            # Eyes
            pygame.draw.circle(surf, (20, 30, 20), (x + 6, y + h // 2 - 1), 3)
            pygame.draw.circle(surf, (255, 255, 255), (x + 5, y + h // 2 - 2), 1)
            pygame.draw.circle(surf, (20, 30, 20), (x + w - 7, y + h // 2 - 1), 3)
            pygame.draw.circle(surf, (255, 255, 255), (x + w - 8, y + h // 2 - 2), 1)
            frames.append(surf)

    elif enemy_type == "skeleton":
        # Skeleton Minion
        for f in range(4):
            surf = pygame.Surface((36, 40), pygame.SRCALPHA)
            bob = math.sin(f * (math.pi / 2)) * 2.0
            # Shadow
            surf.blit(create_drop_shadow(22, 8), (7, 31))

            # Ribcage & Spine
            pygame.draw.line(surf, (200, 200, 190), (18, 16 + bob), (18, 28 + bob), 3)
            for ry in [19, 23, 27]:
                pygame.draw.line(surf, (220, 220, 210), (13, ry + bob), (23, ry + bob), 2)

            # Skull
            pygame.draw.circle(surf, (230, 230, 220), (18, int(11 + bob)), 7)
            # Red glowing eye sockets
            pygame.draw.circle(surf, (220, 30, 40), (15, int(10 + bob)), 2)
            pygame.draw.circle(surf, (220, 30, 40), (21, int(10 + bob)), 2)

            # Jagged Rusty Sword in hand
            sword_bob = math.cos(f * (math.pi / 2)) * 3.0
            pygame.draw.line(
                surf,
                (180, 110, 70),
                (28, int(12 + sword_bob)),
                (28, int(30 + sword_bob)),
                3,
            )
            pygame.draw.line(
                surf,
                (210, 140, 90),
                (25, int(22 + sword_bob)),
                (31, int(22 + sword_bob)),
                2,
            )
            frames.append(surf)

    elif enemy_type == "golem":
        # Magma Stone Golem (Bulky brute)
        for f in range(4):
            surf = pygame.Surface((56, 56), pygame.SRCALPHA)
            bob = math.sin(f * (math.pi / 2)) * 2.0
            surf.blit(create_drop_shadow(44, 14), (6, 42))

            # Torso (Dark stone)
            pygame.draw.rect(surf, (45, 42, 52), (12, int(16 + bob), 32, 28), border_radius=6)
            pygame.draw.rect(surf, (70, 65, 80), (12, int(16 + bob), 32, 28), width=2, border_radius=6)

            # Molten cracks in chest
            pygame.draw.line(surf, (255, 100, 20), (22, int(20 + bob)), (28, int(32 + bob)), 3)
            pygame.draw.line(surf, (255, 200, 40), (28, int(32 + bob)), (36, int(24 + bob)), 2)

            # Rocky shoulder plates
            pygame.draw.circle(surf, (60, 55, 70), (10, int(22 + bob)), 9)
            pygame.draw.circle(surf, (60, 55, 70), (46, int(22 + bob)), 9)

            # Head / Brow
            pygame.draw.rect(surf, (38, 35, 45), (19, int(8 + bob), 18, 12), border_radius=3)
            # Burning orange eye slit
            pygame.draw.rect(surf, (255, 140, 20), (22, int(12 + bob), 12, 3))
            pygame.draw.rect(surf, (255, 255, 120), (24, int(12 + bob), 8, 2))
            frames.append(surf)

    elif enemy_type == "warlock":
        # Void Cultist / Warlock (Shooter)
        for f in range(4):
            surf = pygame.Surface((40, 44), pygame.SRCALPHA)
            bob = math.sin(f * (math.pi / 2)) * 3.0
            surf.blit(create_drop_shadow(26, 8), (7, 35))

            # Void Cape
            pts = [(10, 36), (30, 36), (24, 14 + bob), (16, 14 + bob)]
            pygame.draw.polygon(surf, (50, 15, 65), pts)

            # Hood
            pygame.draw.circle(surf, (35, 10, 45), (20, int(12 + bob)), 9)
            # Glowing purple eyes
            pygame.draw.circle(surf, (220, 70, 255), (17, int(11 + bob)), 2)
            pygame.draw.circle(surf, (220, 70, 255), (23, int(11 + bob)), 2)

            # Floating orb
            orb_y = int(22 + math.cos(f * (math.pi / 2)) * 4.0)
            pygame.draw.circle(surf, (180, 50, 230), (32, orb_y), 5)
            pygame.draw.circle(surf, (240, 180, 255), (32, orb_y), 2)
            frames.append(surf)

    elif enemy_type == "boss":
        # Archlich Malakor (The Necromancer Overlord)
        for f in range(4):
            surf = pygame.Surface((80, 88), pygame.SRCALPHA)
            bob = math.sin(f * (math.pi / 2)) * 4.0
            surf.blit(create_drop_shadow(60, 18), (10, 68))

            # Regal dark mantle / robes
            pts = [(16, 70), (64, 70), (52, 28 + bob), (28, 28 + bob)]
            pygame.draw.polygon(surf, (30, 10, 40), pts)
            pygame.draw.polygon(surf, (130, 40, 160), pts, width=3)

            # Bone ribs / Breastplate
            pygame.draw.rect(surf, (210, 200, 190), (30, int(34 + bob), 20, 22), border_radius=4)
            # Lich Soul Gem in chest
            pygame.draw.circle(surf, (240, 40, 80), (40, int(45 + bob)), 6)
            pygame.draw.circle(surf, (255, 180, 200), (40, int(45 + bob)), 2)

            # Horned Skull
            pygame.draw.circle(surf, (230, 225, 215), (40, int(22 + bob)), 15)
            # Horns
            pygame.draw.polygon(
                surf,
                (70, 50, 80),
                [(28, int(18 + bob)), (22, int(4 + bob)), (34, int(12 + bob))],
            )
            pygame.draw.polygon(
                surf,
                (70, 50, 80),
                [(52, int(18 + bob)), (58, int(4 + bob)), (46, int(12 + bob))],
            )

            # Crown
            crown_pts = [
                (31, int(14 + bob)),
                (33, int(6 + bob)),
                (40, int(10 + bob)),
                (47, int(6 + bob)),
                (49, int(14 + bob)),
            ]
            pygame.draw.polygon(surf, (240, 190, 40), crown_pts)

            # Flaming Purple Eyes
            pygame.draw.circle(surf, (230, 40, 255), (35, int(22 + bob)), 3)
            pygame.draw.circle(surf, (230, 40, 255), (45, int(22 + bob)), 3)

            # Massive Staff
            staff_top = int(6 + bob)
            pygame.draw.line(surf, (120, 90, 60), (68, staff_top), (68, 72), 4)
            # Floating Skull / Orb on staff
            pygame.draw.circle(surf, (180, 40, 230), (68, staff_top), 9)
            pygame.draw.circle(surf, (255, 200, 255), (68, staff_top), 4)

            frames.append(surf)

    _SPRITE_CACHE[key] = frames
    return frames


def get_gem_sprite(gem_type: str = "normal") -> pygame.Surface:
    """Returns faceted shiny XP Gem sprites."""
    key = f"gem_{gem_type}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    size = 18 if gem_type == "normal" else (22 if gem_type == "rare" else 26)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    half = size // 2

    # Drop shadow
    shadow = create_drop_shadow(size - 4, 6)
    surf.blit(shadow, (2, size - 6))

    if gem_type == "normal":
        color = COLOR_XP_GEM
        bright = (190, 255, 220)
    elif gem_type == "rare":
        color = COLOR_XP_RARE
        bright = (255, 180, 255)
    else:  # legendary
        color = COLOR_XP_LEGENDARY
        bright = (255, 255, 200)

    # Faceted Diamond Polygon
    pts = [
        (half, 2),
        (size - 3, half - 1),
        (half, size - 5),
        (3, half - 1),
    ]
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, (255, 255, 255), pts, width=1)

    # Specular shine facet
    top_facet = [
        (half, 2),
        (half + 4, half - 2),
        (half, half + 1),
        (half - 4, half - 2),
    ]
    pygame.draw.polygon(surf, bright, top_facet)

    _SPRITE_CACHE[key] = surf
    return surf


def get_chest_sprite() -> pygame.Surface:
    """Returns ornate Dungeon Treasure Chest sprite."""
    key = "chest"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    w, h = 36, 32
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Drop shadow
    surf.blit(create_drop_shadow(34, 10), (1, 22))

    # Wooden Chest Base
    pygame.draw.rect(surf, (110, 65, 30), (4, 12, 28, 16), border_radius=3)
    # Iron/Gold Banding
    pygame.draw.rect(surf, (215, 175, 45), (4, 12, 28, 16), width=2, border_radius=3)
    pygame.draw.line(surf, (215, 175, 45), (18, 12), (18, 27), 3)

    # Chest Lid with Dome
    pygame.draw.ellipse(surf, (140, 85, 40), (3, 5, 30, 14))
    pygame.draw.ellipse(surf, (235, 195, 55), (3, 5, 30, 14), width=2)

    # Keyhole
    pygame.draw.circle(surf, (20, 15, 10), (18, 18), 3)
    pygame.draw.polygon(surf, (20, 15, 10), [(17, 18), (19, 18), (20, 23), (16, 23)])

    _SPRITE_CACHE[key] = surf
    return surf


def get_potion_sprite() -> pygame.Surface:
    """Returns Red Healing Potion Flask sprite."""
    key = "potion"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    w, h = 22, 26
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(create_drop_shadow(18, 6), (2, 20))

    # Flask Neck & Cork
    pygame.draw.rect(surf, (160, 120, 70), (8, 2, 6, 4), border_radius=1)  # Cork
    pygame.draw.rect(surf, (180, 210, 230), (8, 6, 6, 4))  # Glass Neck

    # Round Flask Bulb
    pygame.draw.circle(surf, (210, 230, 255), (11, 16), 8)  # Glass
    pygame.draw.circle(surf, COLOR_HEALTH_RED, (11, 17), 7)  # Red Elixir
    pygame.draw.circle(surf, (255, 130, 150), (9, 14), 2)  # Specular Bubble

    _SPRITE_CACHE[key] = surf
    return surf


def get_magnet_sprite() -> pygame.Surface:
    """Returns Arcane Magnet Pickup sprite."""
    key = "magnet"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    w, h = 24, 24
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(create_drop_shadow(20, 6), (2, 18))

    # Horseshoe magnet
    pygame.draw.arc(surf, (220, 40, 50), (3, 2, 18, 18), 0, math.pi, 5)
    # Silver poles
    pygame.draw.rect(surf, (220, 220, 230), (3, 11, 5, 6))
    pygame.draw.rect(surf, (220, 220, 230), (16, 11, 5, 6))
    # Magnetic sparks
    pygame.draw.circle(surf, COLOR_ARCANE_CYAN, (7, 19), 2)
    pygame.draw.circle(surf, COLOR_ARCANE_CYAN, (17, 19), 2)

    _SPRITE_CACHE[key] = surf
    return surf


def get_bomb_sprite() -> pygame.Surface:
    """Returns Dungeon Cleansing Bomb pickup sprite."""
    key = "bomb"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    w, h = 24, 26
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.blit(create_drop_shadow(18, 6), (3, 20))

    # Round bomb body
    pygame.draw.circle(surf, (40, 40, 48), (12, 15), 8)
    pygame.draw.circle(surf, (80, 80, 95), (10, 13), 2)

    # Fuse
    pygame.draw.line(surf, (150, 110, 70), (12, 7), (16, 3), 2)
    # Spark
    pygame.draw.circle(surf, (255, 200, 30), (17, 2), 3)
    pygame.draw.circle(surf, (255, 255, 200), (17, 2), 1)

    _SPRITE_CACHE[key] = surf
    return surf


def get_tile_surface(tile_type: str, size: int = 64) -> pygame.Surface:
    """Generates dungeon floor tiles and wall/pillar surfaces."""
    key = f"tile_{tile_type}_{size}"
    if key in _SPRITE_CACHE:
        return _SPRITE_CACHE[key]

    surf = pygame.Surface((size, size))

    if tile_type == "floor_1":
        surf.fill((28, 25, 38))
        # Fine stone grid / mortar
        pygame.draw.rect(surf, (22, 19, 30), (0, 0, size, size), 1)
        # Subtle texture specks
        pygame.draw.rect(surf, (34, 30, 46), (8, 8, 22, 18))
        pygame.draw.rect(surf, (32, 28, 44), (36, 12, 20, 24))
        pygame.draw.rect(surf, (35, 31, 48), (14, 38, 26, 18))

    elif tile_type == "floor_2":
        surf.fill((29, 26, 40))
        pygame.draw.rect(surf, (22, 19, 30), (0, 0, size, size), 1)
        # Cracked stone variant
        pygame.draw.lines(
            surf,
            (18, 16, 24),
            False,
            [(16, 20), (28, 30), (32, 28), (44, 46)],
            2,
        )
        pygame.draw.rect(surf, (36, 32, 50), (4, 4, 18, 14))

    elif tile_type == "floor_rune":
        surf.fill((28, 25, 38))
        pygame.draw.rect(surf, (22, 19, 30), (0, 0, size, size), 1)
        # Faint arcane runic circle etched into the stone floor
        pygame.draw.circle(surf, (45, 38, 65), (size // 2, size // 2), 22, width=2)
        pygame.draw.circle(surf, (55, 45, 80), (size // 2, size // 2), 12, width=1)
        # Tiny glowing cyan rune center
        pygame.draw.circle(surf, (50, 140, 160), (size // 2, size // 2), 3)

    elif tile_type == "pillar":
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        # Circular ancient stone pillar
        # Shadow
        surf.blit(create_drop_shadow(size - 6, 20), (3, size - 18))
        # Base
        pygame.draw.circle(surf, (42, 38, 54), (size // 2, size // 2), size // 2 - 4)
        pygame.draw.circle(surf, (68, 62, 86), (size // 2, size // 2), size // 2 - 4, width=3)
        # Top ring
        pygame.draw.circle(surf, (55, 50, 70), (size // 2, size // 2 - 4), size // 2 - 10)
        pygame.draw.circle(surf, (85, 78, 106), (size // 2, size // 2 - 4), size // 2 - 10, width=2)

    _SPRITE_CACHE[key] = surf
    return surf
