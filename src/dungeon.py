"""Dungeon arena, tactical pillars, torch illumination, and lighting effects."""

import math
import random
import pygame
from src.config import (
    COLOR_BG,
    COLOR_WALL,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TILE_SIZE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.sprites import get_tile_surface


class Pillar:
    def __init__(self, x: float, y: float, radius: float = 26.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.sprite = get_tile_surface("pillar", int(radius * 2 + 12))
        self.has_torch = random.random() < 0.6
        self.torch_flicker = random.uniform(0.0, 6.28)

    def update(self, dt: float):
        self.torch_flicker += dt * 7.0

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        screen_x = int(self.x - camera_offset[0] - self.sprite.get_width() // 2)
        screen_y = int(self.y - camera_offset[1] - self.sprite.get_height() // 2)
        surface.blit(self.sprite, (screen_x, screen_y))

        # Torch flame on pillar
        if self.has_torch:
            flicker = math.sin(self.torch_flicker) * 2.0
            tx = int(self.x - camera_offset[0])
            ty = int(self.y - camera_offset[1] - 8 + flicker)
            # Flame core
            pygame.draw.circle(surface, (255, 140, 30), (tx, ty), 5)
            pygame.draw.circle(surface, (255, 230, 100), (tx, ty - 1), 3)


class Dungeon:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.pillars: list[Pillar] = []
        self._generate_pillars()

        # Pre-render a chunked or procedural tile grid pattern
        # Since world is 3200x3200, we can cache tile selection deterministically by grid coordinates
        self.seed = 42
        self.tile_types = ["floor_1", "floor_1", "floor_1", "floor_2", "floor_rune"]

        # Light / Vignette mask surface
        self.light_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def _generate_pillars(self):
        """Places symmetrical and organic clusters of stone pillars for tactical kiting."""
        random.seed(1337)
        # Inner ring around spawn
        ring_radii = [400, 800, 1200]
        center_x = WORLD_WIDTH / 2.0
        center_y = WORLD_HEIGHT / 2.0

        for r in ring_radii:
            num_pillars = int((2.0 * math.pi * r) / 380)
            for i in range(num_pillars):
                ang = (i / num_pillars) * math.pi * 2.0 + random.uniform(-0.1, 0.1)
                px = center_x + math.cos(ang) * r + random.uniform(-30, 30)
                py = center_y + math.sin(ang) * r + random.uniform(-30, 30)
                self.pillars.append(Pillar(px, py))

        # Reset random seed
        random.seed()

    def update(self, dt: float):
        for p in self.pillars:
            p.update(dt)

    def get_tile_for_coord(self, gx: int, gy: int) -> str:
        # Deterministic hash for tile picking
        h = (gx * 374761393 + gy * 668265263) ^ 0x5BF03635
        idx = (h ^ (h >> 13)) % len(self.tile_types)
        return self.tile_types[idx]

    def render_background(self, surface: pygame.Surface, camera_offset: tuple):
        cam_x, cam_y = camera_offset

        start_col = max(0, int(cam_x // TILE_SIZE))
        end_col = min(WORLD_WIDTH // TILE_SIZE, int((cam_x + SCREEN_WIDTH) // TILE_SIZE) + 1)

        start_row = max(0, int(cam_y // TILE_SIZE))
        end_row = min(WORLD_HEIGHT // TILE_SIZE, int((cam_y + SCREEN_HEIGHT) // TILE_SIZE) + 1)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_name = self.get_tile_for_coord(col, row)
                tile_surf = get_tile_surface(tile_name, TILE_SIZE)
                draw_x = col * TILE_SIZE - int(cam_x)
                draw_y = row * TILE_SIZE - int(cam_y)
                surface.blit(tile_surf, (draw_x, draw_y))

        # Draw outer dungeon wall border
        border_thickness = 24
        # Left
        if cam_x < border_thickness:
            pygame.draw.rect(
                surface,
                COLOR_WALL,
                (0 - cam_x, 0 - cam_y, border_thickness, WORLD_HEIGHT),
            )
        # Top
        if cam_y < border_thickness:
            pygame.draw.rect(
                surface,
                COLOR_WALL,
                (0 - cam_x, 0 - cam_y, WORLD_WIDTH, border_thickness),
            )
        # Right
        if cam_x + SCREEN_WIDTH > WORLD_WIDTH - border_thickness:
            pygame.draw.rect(
                surface,
                COLOR_WALL,
                (WORLD_WIDTH - border_thickness - cam_x, 0 - cam_y, border_thickness, WORLD_HEIGHT),
            )
        # Bottom
        if cam_y + SCREEN_HEIGHT > WORLD_HEIGHT - border_thickness:
            pygame.draw.rect(
                surface,
                COLOR_WALL,
                (0 - cam_x, WORLD_HEIGHT - border_thickness - cam_y, WORLD_WIDTH, border_thickness),
            )

    def render_pillars(self, surface: pygame.Surface, camera_offset: tuple):
        cam_x, cam_y = camera_offset
        for p in self.pillars:
            # View frustum culling
            if (
                cam_x - 60 <= p.x <= cam_x + SCREEN_WIDTH + 60
                and cam_y - 60 <= p.y <= cam_y + SCREEN_HEIGHT + 60
            ):
                p.render(surface, camera_offset)

    def render_lighting(self, surface: pygame.Surface, camera_offset: tuple, player_x: float, player_y: float):
        """Draws subtle dark vignette with glowing halos around player & torches."""
        self.light_mask.fill((12, 10, 18, 90))  # Ambient dungeon dimness

        # Player torch halo
        px = int(player_x - camera_offset[0])
        py = int(player_y - camera_offset[1])

        # Cut out soft light circle for player
        for r, alpha in [(220, 0), (160, 0), (90, 0)]:
            pygame.draw.circle(self.light_mask, (0, 0, 0, alpha), (px, py), r)

        # Torch lights on visible pillars
        cam_x, cam_y = camera_offset
        for p in self.pillars:
            if p.has_torch:
                if (
                    cam_x - 100 <= p.x <= cam_x + SCREEN_WIDTH + 100
                    and cam_y - 100 <= p.y <= cam_y + SCREEN_HEIGHT + 100
                ):
                    tx = int(p.x - cam_x)
                    ty = int(p.y - cam_y - 8)
                    pygame.draw.circle(self.light_mask, (0, 0, 0, 30), (tx, ty), 80)

        # Blend light mask onto screen
        surface.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
