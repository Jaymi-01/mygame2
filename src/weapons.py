"""Weapons, projectiles, and offensive skill systems."""

import math
import random
import pygame
from src.audio import get_audio
from src.config import (
    COLOR_ARCANE_BLUE,
    COLOR_ARCANE_CYAN,
    COLOR_FIRE_ORANGE,
    COLOR_GOLD,
    COLOR_WHITE,
)
from src.particles import Particle


class Projectile:
    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        damage: float,
        pierce: int = 1,
        lifetime: float = 2.5,
        color: tuple = COLOR_ARCANE_CYAN,
        radius: float = 6.0,
        is_enemy: bool = False,
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.pierce = pierce
        self.lifetime = lifetime
        self.age = 0.0
        self.color = color
        self.radius = radius
        self.is_enemy = is_enemy
        self.alive = True
        self.hit_enemies = set()

    def update(self, dt: float, particle_mgr=None):
        self.age += dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Spawn subtle trail particle
        if particle_mgr and random.random() < 0.4:
            particle_mgr.particles.append(
                Particle(
                    self.x + random.uniform(-2, 2),
                    self.y + random.uniform(-2, 2),
                    -self.vx * 0.1,
                    -self.vy * 0.1,
                    self.color,
                    radius=self.radius * 0.6,
                    lifetime=0.15,
                    shrink=True,
                )
            )

        if self.age >= self.lifetime or self.pierce <= 0:
            self.alive = False

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Outer glow
        glow_r = int(self.radius * 1.8)
        glow_surf = pygame.Surface((glow_r * 2 + 2, glow_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (*self.color[:3], 90),
            (glow_r + 1, glow_r + 1),
            glow_r,
        )
        surface.blit(glow_surf, (screen_x - glow_r - 1, screen_y - glow_r - 1))

        # Core
        pygame.draw.circle(surface, self.color[:3], (screen_x, screen_y), int(self.radius))
        pygame.draw.circle(surface, COLOR_WHITE, (screen_x, screen_y), max(1, int(self.radius * 0.4)))


class OrbitingBlade:
    """Orbs / Blades rotating in a circle protecting the player."""
    def __init__(self, index: int, total: int, player_x: float = 0.0, player_y: float = 0.0):
        self.index = index
        self.total = total
        self.radius = 80.0
        self.angle = (index / max(1, total)) * math.pi * 2.0
        self.speed = 3.2  # radians per second
        self.damage = 25.0
        self.hit_cooldowns = {}  # enemy_id: cooldown timer
        self.x = player_x + math.cos(self.angle) * self.radius
        self.y = player_y + math.sin(self.angle) * self.radius

    def update(self, dt: float, player_x: float, player_y: float):
        self.angle += self.speed * dt
        self.x = player_x + math.cos(self.angle) * self.radius
        self.y = player_y + math.sin(self.angle) * self.radius

        # Update hit cooldowns
        for eid in list(self.hit_cooldowns.keys()):
            self.hit_cooldowns[eid] -= dt
            if self.hit_cooldowns[eid] <= 0:
                del self.hit_cooldowns[eid]

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        if not hasattr(self, "x") or not hasattr(self, "y"):
            return

        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])

        # Glowing cyan/gold protective energy crystal
        pygame.draw.circle(surface, COLOR_ARCANE_CYAN, (screen_x, screen_y), 9)
        pygame.draw.circle(surface, COLOR_WHITE, (screen_x, screen_y), 5)
        # Connecting tether line to player
        # Draw a faint trailing particle
        pygame.draw.circle(surface, (120, 240, 255), (screen_x, screen_y), 11, width=1)


class LightningBolt:
    """Visual chain lightning bolt leaping between points."""
    def __init__(self, segments: list[tuple[float, float]], lifetime: float = 0.18):
        self.segments = segments
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        progress = self.age / self.lifetime
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0 or len(self.segments) < 2:
            return

        points = [(int(x - camera_offset[0]), int(y - camera_offset[1])) for x, y in self.segments]

        # Draw glow line
        for i in range(len(points) - 1):
            pygame.draw.line(surface, COLOR_ARCANE_CYAN, points[i], points[i + 1], 4)
            pygame.draw.line(surface, COLOR_WHITE, points[i], points[i + 1], 2)


class CleaveVisual:
    """Expanding crescent greatsword slash visual."""
    def __init__(self, x: float, y: float, angle: float, radius: float, arc_span: float, color: tuple, lifetime: float = 0.18):
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = radius
        self.arc_span = arc_span
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0

    def update(self, dt: float) -> bool:
        self.age += dt
        return self.age < self.lifetime

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        progress = self.age / self.lifetime
        alpha = int(255 * (1.0 - progress))
        if alpha <= 0:
            return

        cx = int(self.x - camera_offset[0])
        cy = int(self.y - camera_offset[1])
        r = int(self.radius * (0.8 + 0.2 * progress))

        num_pts = 16
        pts_outer = []
        pts_inner = []
        start_ang = self.angle - self.arc_span / 2.0
        step = self.arc_span / max(1, num_pts - 1)
        inner_r = max(10, r - 26)

        for i in range(num_pts):
            a = start_ang + i * step
            pts_outer.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
            pts_inner.append((cx + math.cos(a) * inner_r, cy + math.sin(a) * inner_r))

        poly = pts_outer + list(reversed(pts_inner))
        if len(poly) >= 3:
            box_r = r + 30
            slash_surf = pygame.Surface((box_r * 2, box_r * 2), pygame.SRCALPHA)
            offset_poly = [(px - (cx - box_r), py - (cy - box_r)) for px, py in poly]
            pygame.draw.polygon(slash_surf, (*self.color[:3], alpha), offset_poly)
            pygame.draw.polygon(slash_surf, (255, 255, 255, int(alpha * 0.95)), offset_poly, width=2)
            surface.blit(slash_surf, (cx - box_r, cy - box_r))


class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.projectiles: list[Projectile] = []
        self.lightning_visuals: list[LightningBolt] = []
        self.orbiting_blades: list[OrbitingBlade] = []
        self.cleave_visuals: list[CleaveVisual] = []

        # Weapon unlocked levels (0 = locked)
        self.wand_level = 0
        self.wand_timer = 0.0

        self.orbit_level = 0

        self.lightning_level = 0
        self.lightning_timer = 0.0

        self.aura_level = 0
        self.aura_tick_timer = 0.0

        self.dagger_level = 0
        self.dagger_timer = 0.0

        self.cleave_level = 0
        self.cleave_timer = 0.0

        # Unlock initial starting weapon based on hero class
        starting_weapon = getattr(self.player, "starting_weapon", "wand")
        self.level_up_weapon(starting_weapon)

    def _rebuild_orbiting_blades(self):
        self.orbiting_blades.clear()
        if self.orbit_level > 0:
            count = 1 + self.orbit_level  # 2, 3, 4, 5...
            px = getattr(self.player, "x", 0.0)
            py = getattr(self.player, "y", 0.0)
            for i in range(count):
                b = OrbitingBlade(i, count, px, py)
                b.damage = 18.0 + (self.orbit_level * 10.0) * self.player.damage_multiplier
                b.radius = 70.0 + (self.orbit_level * 10.0)
                b.x = px + math.cos(b.angle) * b.radius
                b.y = py + math.sin(b.angle) * b.radius
                self.orbiting_blades.append(b)

    def level_up_weapon(self, weapon_name: str):
        if weapon_name == "wand":
            self.wand_level += 1
        elif weapon_name == "orbit":
            self.orbit_level += 1
            self._rebuild_orbiting_blades()
        elif weapon_name == "lightning":
            self.lightning_level += 1
        elif weapon_name == "aura":
            self.aura_level += 1
        elif weapon_name == "dagger":
            self.dagger_level += 1
        elif weapon_name == "cleave":
            self.cleave_level += 1

    def update(self, dt: float, enemies: list, particle_mgr):
        audio = get_audio()

        # Update existing projectiles
        for p in self.projectiles:
            p.update(dt, particle_mgr)
        self.projectiles = [p for p in self.projectiles if p.alive]

        # Update lightning and cleave visuals
        self.lightning_visuals = [l for l in self.lightning_visuals if l.update(dt)]
        self.cleave_visuals = [cv for cv in self.cleave_visuals if cv.update(dt)]

        # --- 1. Arcane Wand Weapon ---
        if self.wand_level > 0:
            base_cooldown = max(0.18, 0.75 - (self.wand_level * 0.06)) * self.player.cooldown_multiplier
            self.wand_timer += dt
            if self.wand_timer >= base_cooldown and enemies:
                self.wand_timer = 0.0
                # Find nearest enemy to shoot towards
                target = self._get_nearest_enemy(enemies)
                if target:
                    dx = target.x - self.player.x
                    dy = target.y - self.player.y
                    base_angle = math.atan2(dy, dx)

                    # Number of projectiles scales with wand level
                    num_bolts = 1 + (self.wand_level // 2)
                    spread = 0.22  # radians
                    start_angle = base_angle - (spread * (num_bolts - 1) / 2.0)
                    speed = 520.0
                    base_dmg = (22.0 + self.wand_level * 7.0) * self.player.damage_multiplier
                    pierce_count = 1 + (self.wand_level // 3)

                    for i in range(num_bolts):
                        ang = start_angle + i * spread
                        vx = math.cos(ang) * speed
                        vy = math.sin(ang) * speed
                        self.projectiles.append(
                            Projectile(
                                self.player.x,
                                self.player.y,
                                vx,
                                vy,
                                damage=base_dmg,
                                pierce=pierce_count,
                                color=COLOR_ARCANE_CYAN,
                                radius=7.0,
                            )
                        )
                    audio.play("shoot")

        # --- 2. Orbiting Arc Blades ---
        if self.orbit_level > 0:
            for blade in self.orbiting_blades:
                blade.update(dt, self.player.x, self.player.y)
                # Check collision with enemies
                for enemy in enemies:
                    if not enemy.alive:
                        continue
                    if enemy.id in blade.hit_cooldowns:
                        continue
                    dist = math.hypot(enemy.x - blade.x, enemy.y - blade.y)
                    if dist < (enemy.radius + 12.0):
                        blade.hit_cooldowns[enemy.id] = 0.35  # don't hit same enemy every frame
                        is_crit = random.random() < self.player.crit_chance
                        dmg = blade.damage * (2.5 if is_crit else 1.0)
                        enemy.take_damage(dmg, is_crit, particle_mgr)
                        audio.play("hit")
                        # Push back slightly
                        edx = enemy.x - self.player.x
                        edy = enemy.y - self.player.y
                        edist = max(1.0, math.hypot(edx, edy))
                        enemy.x += (edx / edist) * 20.0
                        enemy.y += (edy / edist) * 20.0

        # --- 3. Chain Lightning ---
        if self.lightning_level > 0:
            cooldown = max(0.9, 2.2 - (self.lightning_level * 0.2)) * self.player.cooldown_multiplier
            self.lightning_timer += dt
            if self.lightning_timer >= cooldown and enemies:
                self.lightning_timer = 0.0
                self._cast_chain_lightning(enemies, particle_mgr, audio)

        # --- 4. Blaze Aura ---
        if self.aura_level > 0:
            self.aura_tick_timer += dt
            radius = 100.0 + self.aura_level * 20.0
            if self.aura_tick_timer >= 0.4:
                self.aura_tick_timer = 0.0
                dmg = (8.0 + self.aura_level * 5.0) * self.player.damage_multiplier
                for enemy in enemies:
                    if not enemy.alive:
                        continue
                    if math.hypot(enemy.x - self.player.x, enemy.y - self.player.y) <= radius:
                        is_crit = random.random() < self.player.crit_chance
                        actual_dmg = dmg * (2.5 if is_crit else 1.0)
                        enemy.take_damage(actual_dmg, is_crit, particle_mgr)
                        if random.random() < 0.3:
                            particle_mgr.emit_burst(enemy.x, enemy.y, COLOR_FIRE_ORANGE, count=4, speed_range=(20, 60))

        # --- 5. Phantom Daggers ---
        if self.dagger_level > 0:
            cooldown = max(0.2, 0.6 - (self.dagger_level * 0.07)) * self.player.cooldown_multiplier
            self.dagger_timer += dt
            if self.dagger_timer >= cooldown and enemies:
                self.dagger_timer = 0.0
                target = self._get_nearest_enemy(enemies)
                if target:
                    dx = target.x - self.player.x
                    dy = target.y - self.player.y
                    dist = max(1.0, math.hypot(dx, dy))
                    speed = 700.0
                    vx = (dx / dist) * speed
                    vy = (dy / dist) * speed
                    dmg = (18.0 + self.dagger_level * 8.0) * self.player.damage_multiplier
                    self.projectiles.append(
                        Projectile(
                            self.player.x,
                            self.player.y,
                            vx,
                            vy,
                            damage=dmg,
                            pierce=2 + self.dagger_level // 2,
                            color=COLOR_GOLD,
                            radius=5.0,
                        )
                    )
                    audio.play("shoot")

        # --- 6. Greatsword Whirlwind Cleave ---
        if self.cleave_level > 0:
            cooldown = max(0.4, 1.25 - (self.cleave_level * 0.1)) * self.player.cooldown_multiplier
            self.cleave_timer += dt
            if self.cleave_timer >= cooldown:
                self.cleave_timer = 0.0
                target = self._get_nearest_enemy(enemies)
                if target or len(enemies) > 0:
                    if target:
                        cleave_angle = math.atan2(target.y - self.player.y, target.x - self.player.x)
                    else:
                        cleave_angle = -math.pi if self.player.facing_left else 0.0

                    arc_span = math.pi * 0.95 if self.cleave_level < 3 else (math.pi * 2.0)
                    radius = 125.0 + (self.cleave_level * 20.0)
                    dmg = (35.0 + self.cleave_level * 18.0) * self.player.damage_multiplier

                    color = (255, 75, 85) if getattr(self.player, "class_id", "") == "warrior" else (225, 235, 255)
                    self.cleave_visuals.append(
                        CleaveVisual(self.player.x, self.player.y, cleave_angle, radius, arc_span, color)
                    )
                    audio.play("slash")

                    for enemy in enemies:
                        if not enemy.alive:
                            continue
                        edx = enemy.x - self.player.x
                        edy = enemy.y - self.player.y
                        edist = math.hypot(edx, edy)
                        if edist <= radius + enemy.radius:
                            if arc_span >= math.pi * 1.95:
                                in_arc = True
                            else:
                                enemy_ang = math.atan2(edy, edx)
                                diff = (enemy_ang - cleave_angle + math.pi) % (2.0 * math.pi) - math.pi
                                in_arc = abs(diff) <= (arc_span / 2.0)

                            if in_arc:
                                is_crit = random.random() < self.player.crit_chance
                                crit_m = getattr(self.player, "crit_mult", 2.5)
                                actual_dmg = dmg * (crit_m if is_crit else 1.0)
                                enemy.take_damage(actual_dmg, is_crit, particle_mgr)
                                if edist > 0.001:
                                    enemy.kb_vx += (edx / edist) * 220.0
                                    enemy.kb_vy += (edy / edist) * 220.0
                                if particle_mgr:
                                    particle_mgr.emit_burst(enemy.x, enemy.y, (255, 110, 110), count=6, speed_range=(40, 140))

    def _cast_chain_lightning(self, enemies: list, particle_mgr, audio):
        """Zaps nearest enemy and chains to nearby targets."""
        active_enemies = [e for e in enemies if e.alive and math.hypot(e.x - self.player.x, e.y - self.player.y) < 650.0]
        if not active_enemies:
            return

        # Sort by distance from player
        active_enemies.sort(key=lambda e: math.hypot(e.x - self.player.x, e.y - self.player.y))
        first = active_enemies[0]

        max_chains = 2 + self.lightning_level
        dmg = (35.0 + self.lightning_level * 14.0) * self.player.damage_multiplier

        chain_pts = [(self.player.x, self.player.y)]
        visited = set()
        current = first

        for _ in range(max_chains):
            if current is None:
                break
            visited.add(current.id)
            chain_pts.append((current.x, current.y))

            is_crit = random.random() < self.player.crit_chance
            actual_dmg = dmg * (2.5 if is_crit else 1.0)
            current.take_damage(actual_dmg, is_crit, particle_mgr)

            # Find next closest unvisited enemy within 220px
            candidates = [
                e for e in active_enemies
                if e.id not in visited and math.hypot(e.x - current.x, e.y - current.y) < 220.0
            ]
            if candidates:
                candidates.sort(key=lambda e: math.hypot(e.x - current.x, e.y - current.y))
                current = candidates[0]
            else:
                current = None

        if len(chain_pts) > 1:
            # Generate jagged lightning bolt segments
            jagged = []
            for i in range(len(chain_pts) - 1):
                p1 = chain_pts[i]
                p2 = chain_pts[i + 1]
                mid_x = (p1[0] + p2[0]) / 2.0 + random.uniform(-16, 16)
                mid_y = (p1[1] + p2[1]) / 2.0 + random.uniform(-16, 16)
                jagged.extend([p1, (mid_x, mid_y)])
            jagged.append(chain_pts[-1])

            self.lightning_visuals.append(LightningBolt(jagged))
            audio.play("lightning")

    def _get_nearest_enemy(self, enemies: list):
        nearest = None
        min_dist = float("inf")
        px, py = self.player.x, self.player.y
        for e in enemies:
            if not e.alive:
                continue
            d = (e.x - px) ** 2 + (e.y - py) ** 2
            if d < min_dist:
                min_dist = d
                nearest = e
        return nearest

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        # 1. Blaze aura circle
        if self.aura_level > 0:
            screen_x = int(self.player.x - camera_offset[0])
            screen_y = int(self.player.y - camera_offset[1])
            radius = int(100.0 + self.aura_level * 20.0)
            aura_surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (255, 120, 20, 45), (radius + 1, radius + 1), radius)
            pygame.draw.circle(aura_surf, (255, 160, 40, 110), (radius + 1, radius + 1), radius, width=2)
            surface.blit(aura_surf, (screen_x - radius - 1, screen_y - radius - 1))

        # 2. Lightning visuals
        for l in self.lightning_visuals:
            l.render(surface, camera_offset)

        # 3. Projectiles
        for p in self.projectiles:
            p.render(surface, camera_offset)

        # 4. Orbiting blades
        for b in self.orbiting_blades:
            b.render(surface, camera_offset)

        # 5. Cleave slashes
        for cv in self.cleave_visuals:
            cv.render(surface, camera_offset)
