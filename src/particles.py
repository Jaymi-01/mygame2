"""Particle system, floating damage numbers, visual effects, and screen shake."""

import math
import random
import pygame
from src.config import COLOR_GOLD, COLOR_HEALTH_GREEN, COLOR_WHITE


class DamageNumber:
    def __init__(self, x: float, y: float, text: str, color: tuple, is_crit: bool = False):
        self.x = x + random.uniform(-10, 10)
        self.y = y + random.uniform(-10, 10)
        self.text = text
        self.color = color
        self.is_crit = is_crit
        self.lifetime = 0.75  # seconds
        self.age = 0.0
        self.vy = -75.0 if not is_crit else -110.0
        self.vx = random.uniform(-25.0, 25.0)

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 60.0 * dt  # slight downward gravity drag
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, font: pygame.font.Font, font_crit: pygame.font.Font, camera_offset: tuple):
        progress = self.age / self.lifetime
        alpha = int(255 * (1.0 - (progress ** 1.5)))
        if alpha <= 0:
            return

        f = font_crit if self.is_crit else font
        txt_surf = f.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)

        # Render with dark outline for crisp readability
        outline_surf = f.render(self.text, True, (10, 8, 14))
        outline_surf.set_alpha(alpha)

        screen_x = self.x - camera_offset[0] - txt_surf.get_width() // 2
        screen_y = self.y - camera_offset[1] - txt_surf.get_height() // 2

        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            surface.blit(outline_surf, (screen_x + ox, screen_y + oy))
        surface.blit(txt_surf, (screen_x, screen_y))


class Particle:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: tuple,
        radius: float,
        lifetime: float,
        drag: float = 0.92,
        shrink: bool = True,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.initial_radius = radius
        self.radius = radius
        self.lifetime = lifetime
        self.age = 0.0
        self.drag = drag
        self.shrink = shrink

    def update(self, dt: float) -> bool:
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= (self.drag ** (dt * 60.0))
        self.vy *= (self.drag ** (dt * 60.0))
        if self.shrink:
            self.radius = max(0.5, self.initial_radius * (1.0 - (self.age / self.lifetime)))
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        alpha = int(255 * (1.0 - (self.age / self.lifetime)))
        if alpha <= 0 or self.radius < 0.5:
            return

        r = int(self.radius)
        if r <= 1:
            surface.set_at((screen_x, screen_y), self.color[:3])
        else:
            # Soft circular particle
            surf = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
            col = (*self.color[:3], alpha)
            pygame.draw.circle(surf, col, (r + 1, r + 1), r)
            surface.blit(surf, (screen_x - r - 1, screen_y - r - 1))


class Shockwave:
    def __init__(self, x: float, y: float, max_radius: float, color: tuple, lifetime: float = 0.35, width: int = 3):
        self.x = x
        self.y = y
        self.max_radius = max_radius
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
        self.width = width

    def update(self, dt: float) -> bool:
        self.age += dt
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        progress = self.age / self.lifetime
        current_r = int(self.max_radius * progress)
        alpha = int(255 * (1.0 - progress))
        if current_r <= 2 or alpha <= 0:
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        surf = pygame.Surface((current_r * 2 + 4, current_r * 2 + 4), pygame.SRCALPHA)
        col = (*self.color[:3], alpha)
        pygame.draw.circle(surf, col, (current_r + 2, current_r + 2), current_r, width=self.width)
        surface.blit(surf, (screen_x - current_r - 2, screen_y - current_r - 2))


class ScreenShake:
    """Trauma-based screen shake for visceral impacts."""
    def __init__(self):
        self.trauma = 0.0
        self.max_offset = 18.0

    def add_trauma(self, amount: float):
        self.trauma = min(1.0, self.trauma + amount)

    def update(self, dt: float):
        if self.trauma > 0.0:
            # Decay trauma linearly
            self.trauma = max(0.0, self.trauma - 1.6 * dt)

    def get_offset(self) -> tuple[float, float]:
        if self.trauma <= 0.001:
            return 0.0, 0.0
        shake = (self.trauma ** 2) * self.max_offset
        ox = random.uniform(-shake, shake)
        oy = random.uniform(-shake, shake)
        return ox, oy


class ParticleManager:
    def __init__(self):
        self.particles: list[Particle] = []
        self.damage_numbers: list[DamageNumber] = []
        self.shockwaves: list[Shockwave] = []
        self.shake = ScreenShake()
        self.font = None
        self.font_crit = None

    def init_fonts(self):
        try:
            self.font = pygame.font.Font(None, 24)
            self.font_crit = pygame.font.Font(None, 34)
        except Exception:
            pass

    def add_damage_number(
        self,
        x: float,
        y: float,
        damage: int,
        is_crit: bool = False,
        is_heal: bool = False,
        color: tuple = None,
    ):
        if color is not None:
            c = color
            text = str(damage)
        elif is_heal:
            text = f"+{damage}"
            c = COLOR_HEALTH_GREEN
        elif is_crit:
            text = f"{damage}!"
            c = COLOR_GOLD
        else:
            text = str(damage)
            c = COLOR_WHITE
        self.damage_numbers.append(DamageNumber(x, y, text, c, is_crit=is_crit))

    def emit_burst(
        self,
        x: float,
        y: float,
        color: tuple,
        count: int = 12,
        speed_range: tuple = (40.0, 180.0),
        lifetime_range: tuple = (0.2, 0.5),
        radius_range: tuple = (2.0, 4.5),
    ):
        for _ in range(count):
            angle = random.uniform(0, 2.0 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.uniform(*lifetime_range)
            radius = random.uniform(*radius_range)
            self.particles.append(Particle(x, y, vx, vy, color, radius, lifetime))

    def emit_shockwave(self, x: float, y: float, max_radius: float, color: tuple, lifetime: float = 0.35, width: int = 3):
        self.shockwaves.append(Shockwave(x, y, max_radius, color, lifetime, width))

    def update(self, dt: float):
        self.particles = [p for p in self.particles if p.update(dt)]
        self.damage_numbers = [d for d in self.damage_numbers if d.update(dt)]
        self.shockwaves = [s for s in self.shockwaves if s.update(dt)]
        self.shake.update(dt)

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        # 1. Shockwaves
        for s in self.shockwaves:
            s.render(surface, camera_offset)

        # 2. Particles
        for p in self.particles:
            p.render(surface, camera_offset)

        # 3. Damage numbers on top
        if self.font is None:
            self.init_fonts()
        for d in self.damage_numbers:
            d.render(surface, self.font, self.font_crit, camera_offset)
