"""Enemy archetypes, behaviors, AI, projectile shooting, and boss encounter."""

import math
import random
import pygame
from src.audio import get_audio
from src.config import (
    COLOR_ARCANE_CYAN,
    COLOR_FIRE_ORANGE,
    COLOR_GOLD,
    COLOR_HEALTH_GREEN,
    COLOR_HEALTH_RED,
    COLOR_XP_GEM,
    COLOR_XP_LEGENDARY,
    COLOR_XP_RARE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.items import Item
from src.sprites import get_enemy_frames
from src.weapons import Projectile

_ENEMY_ID_COUNTER = 0


def _next_enemy_id() -> int:
    global _ENEMY_ID_COUNTER
    _ENEMY_ID_COUNTER += 1
    return _ENEMY_ID_COUNTER


class Enemy:
    def __init__(self, x: float, y: float, enemy_type: str, wave_scale: float = 1.0):
        self.id = _next_enemy_id()
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.alive = True
        self.facing_left = False

        # Configure Archetype Stats
        if enemy_type == "slime":
            self.max_hp = 25.0 * wave_scale
            self.speed = 135.0
            self.radius = 12.0
            self.damage = 8.0
            self.xp_type = "gem_normal"
            self.xp_chance = 1.0

        elif enemy_type == "skeleton":
            self.max_hp = 55.0 * wave_scale
            self.speed = 105.0
            self.radius = 15.0
            self.damage = 15.0
            self.xp_type = "gem_normal"
            self.xp_chance = 1.0

        elif enemy_type == "golem":
            self.max_hp = 180.0 * wave_scale
            self.speed = 70.0
            self.radius = 24.0
            self.damage = 28.0
            self.xp_type = "gem_rare"
            self.xp_chance = 1.0
            # Charge skill
            self.charge_timer = random.uniform(3.0, 6.0)
            self.is_charging = False
            self.charge_duration = 0.0

        elif enemy_type == "warlock":
            self.max_hp = 70.0 * wave_scale
            self.speed = 85.0
            self.radius = 16.0
            self.damage = 12.0
            self.xp_type = "gem_rare"
            self.xp_chance = 1.0
            self.cast_timer = random.uniform(1.5, 3.0)

        elif enemy_type == "boss":
            self.max_hp = 1500.0 * wave_scale
            self.speed = 75.0
            self.radius = 36.0
            self.damage = 35.0
            self.xp_type = "gem_legendary"
            self.xp_chance = 1.0
            self.boss_skill_timer = 2.5
            self.phase = 1

        self.hp = self.max_hp
        self.frames = get_enemy_frames(enemy_type)
        self.anim_timer = random.uniform(0.0, 2.0)
        self.anim_frame = 0

        # Knockback / Stun
        self.kb_vx = 0.0
        self.kb_vy = 0.0
        self.flash_timer = 0.0

    def take_damage(self, amount: float, is_crit: bool, particle_mgr=None):
        if not self.alive:
            return

        self.hp -= amount
        self.flash_timer = 0.12

        if particle_mgr:
            particle_mgr.add_damage_number(self.x, self.y - 10, int(amount), is_crit=is_crit)
            color = COLOR_FIRE_ORANGE if self.enemy_type == "golem" else ((160, 40, 220) if self.enemy_type in ("warlock", "boss") else (180, 220, 180))
            particle_mgr.emit_burst(self.x, self.y, color, count=6, speed_range=(40, 120))

        if self.hp <= 0.0:
            self.alive = False

    def on_death(self, player, items_list: list, particle_mgr=None):
        audio = get_audio()
        audio.play("kill")

        player.total_kills += 1

        # Vampirism roll
        if player.vampirism > 0.0 and random.random() < player.vampirism:
            actual = player.heal(4)
            if actual > 0 and particle_mgr:
                particle_mgr.add_damage_number(player.x, player.y - 25, actual, is_heal=True)

        if particle_mgr:
            if self.enemy_type == "boss":
                particle_mgr.emit_shockwave(self.x, self.y, 250.0, COLOR_GOLD, lifetime=0.8, width=5)
                particle_mgr.emit_burst(self.x, self.y, COLOR_GOLD, count=36, speed_range=(60, 240))
                particle_mgr.shake.add_trauma(0.8)
            else:
                particle_mgr.emit_burst(self.x, self.y, (180, 50, 70), count=12)

        # Drop XP Gem
        if random.random() < self.xp_chance:
            items_list.append(Item(self.x, self.y, self.xp_type))

        # Drop special loot roll
        if self.enemy_type == "boss":
            items_list.append(Item(self.x + 20, self.y, "chest"))
            items_list.append(Item(self.x - 20, self.y, "potion"))
        else:
            loot_roll = random.random()
            if loot_roll < 0.025:
                items_list.append(Item(self.x, self.y, "potion"))
            elif loot_roll < 0.035:
                items_list.append(Item(self.x, self.y, "magnet"))
            elif loot_roll < 0.042:
                items_list.append(Item(self.x, self.y, "bomb"))
            elif loot_roll < 0.045:
                items_list.append(Item(self.x, self.y, "chest"))

    def update(self, dt: float, player, enemies: list, enemy_projectiles: list, particle_mgr=None):
        if not self.alive:
            return

        # Flash timer
        if self.flash_timer > 0.0:
            self.flash_timer -= dt

        # Knockback decay
        self.x += self.kb_vx * dt
        self.y += self.kb_vy * dt
        self.kb_vx *= 0.85 ** (dt * 60.0)
        self.kb_vy *= 0.85 ** (dt * 60.0)

        # Distance to player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0.001:
            nx = dx / dist
            ny = dy / dist
        else:
            nx, ny = 0.0, 0.0

        self.facing_left = dx < 0

        # Behavior per enemy archetype
        if self.enemy_type in ("slime", "skeleton"):
            # Direct chase
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt

        elif self.enemy_type == "golem":
            self.charge_timer -= dt
            if self.is_charging:
                self.charge_duration -= dt
                # Charge at high speed in locked direction
                self.x += self.charge_vx * dt
                self.y += self.charge_vy * dt
                if particle_mgr and random.random() < 0.4:
                    particle_mgr.emit_burst(self.x, self.y, (180, 160, 140), count=2, speed_range=(10, 40))
                if self.charge_duration <= 0.0:
                    self.is_charging = False
                    self.charge_timer = random.uniform(4.0, 7.0)
            else:
                self.x += nx * self.speed * dt
                self.y += ny * self.speed * dt
                if self.charge_timer <= 0.0 and dist < 450.0:
                    # Initiate charge!
                    self.is_charging = True
                    self.charge_duration = 0.8
                    self.charge_vx = nx * 360.0
                    self.charge_vy = ny * 360.0
                    if particle_mgr:
                        particle_mgr.emit_shockwave(self.x, self.y, 40.0, COLOR_FIRE_ORANGE, lifetime=0.3)

        elif self.enemy_type == "warlock":
            # Maintain kiting distance (~280px from player)
            preferred_dist = 280.0
            if dist < preferred_dist - 40:
                # Back away
                self.x -= nx * self.speed * 0.9 * dt
                self.y -= ny * self.speed * 0.9 * dt
            elif dist > preferred_dist + 40:
                # Approach
                self.x += nx * self.speed * dt
                self.y += ny * self.speed * dt

            # Cast dark magic bolt
            self.cast_timer -= dt
            if self.cast_timer <= 0.0 and dist < 600.0:
                self.cast_timer = random.uniform(2.2, 3.5)
                bullet_speed = 220.0
                proj = Projectile(
                    self.x,
                    self.y,
                    nx * bullet_speed,
                    ny * bullet_speed,
                    damage=self.damage,
                    pierce=1,
                    lifetime=3.5,
                    color=(220, 60, 240),
                    radius=7.0,
                    is_enemy=True,
                )
                enemy_projectiles.append(proj)

        elif self.enemy_type == "boss":
            # Boss moves steadily towards player
            self.x += nx * self.speed * dt
            self.y += ny * self.speed * dt

            self.boss_skill_timer -= dt
            if self.boss_skill_timer <= 0.0:
                self.boss_skill_timer = 3.2
                self._execute_boss_skill(nx, ny, enemy_projectiles, particle_mgr)

        # Flocking / Bumping separation between nearby enemies
        for other in enemies:
            if other.id == self.id or not other.alive:
                continue
            sep_dx = self.x - other.x
            sep_dy = self.y - other.y
            sep_dist = math.hypot(sep_dx, sep_dy)
            min_sep = self.radius + other.radius
            if sep_dist < min_sep and sep_dist > 0.001:
                overlap = (min_sep - sep_dist) * 0.5
                self.x += (sep_dx / sep_dist) * overlap * 0.35
                self.y += (sep_dy / sep_dist) * overlap * 0.35

        # Deal contact damage to player
        if dist < (self.radius + player.radius):
            player.take_damage(self.damage, particle_mgr)

        # Clamp inside world bounds
        self.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.y))

        # Animation
        self.anim_timer += dt * 8.0
        self.anim_frame = int(self.anim_timer) % len(self.frames)

    def _execute_boss_skill(self, nx: float, ny: float, enemy_projectiles: list, particle_mgr=None):
        """Boss rotates through attacks: radial nova, triple aimed shots, or shockwave ground pound."""
        attack = random.choice(["radial", "tri_shot", "pound"])
        audio = get_audio()

        if attack == "radial":
            # 10-way dark skull barrage
            audio.play("lightning")
            num_bolts = 10
            for i in range(num_bolts):
                ang = i * (2.0 * math.pi / num_bolts)
                speed = 210.0
                enemy_projectiles.append(
                    Projectile(
                        self.x,
                        self.y,
                        math.cos(ang) * speed,
                        math.sin(ang) * speed,
                        damage=20.0,
                        pierce=1,
                        lifetime=4.0,
                        color=(210, 40, 240),
                        radius=8.0,
                        is_enemy=True,
                    )
                )

        elif attack == "tri_shot":
            # Fan of 3 fast bolts aimed at player
            audio.play("shoot")
            base_ang = math.atan2(ny, nx)
            for offset in [-0.25, 0.0, 0.25]:
                ang = base_ang + offset
                speed = 340.0
                enemy_projectiles.append(
                    Projectile(
                        self.x,
                        self.y,
                        math.cos(ang) * speed,
                        math.sin(ang) * speed,
                        damage=25.0,
                        pierce=1,
                        lifetime=3.5,
                        color=(255, 60, 90),
                        radius=9.0,
                        is_enemy=True,
                    )
                )

        elif attack == "pound":
            # Ground slam shockwave
            audio.play("boss_roar")
            if particle_mgr:
                particle_mgr.emit_shockwave(self.x, self.y, 200.0, (180, 40, 220), lifetime=0.6, width=6)
                particle_mgr.shake.add_trauma(0.5)

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        frame = self.frames[self.anim_frame]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        draw_x = int(self.x - camera_offset[0] - frame.get_width() // 2)
        draw_y = int(self.y - camera_offset[1] - frame.get_height() // 2)

        # Hit flash: draw silhouette in bright white when struck
        if self.flash_timer > 0.0:
            flash_surf = frame.copy()
            flash_surf.fill((255, 255, 255, 200), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(flash_surf, (draw_x, draw_y))
        else:
            surface.blit(frame, (draw_x, draw_y))

        # Health bar for Golems and Bosses
        if self.enemy_type in ("golem", "boss") and self.hp < self.max_hp:
            bar_w = 48 if self.enemy_type == "golem" else 90
            bar_h = 5 if self.enemy_type == "golem" else 8
            bx = int(self.x - camera_offset[0] - bar_w // 2)
            by = draw_y - 12
            # Background
            pygame.draw.rect(surface, (20, 16, 24), (bx, by, bar_w, bar_h), border_radius=2)
            # Fill
            pct = max(0.0, min(1.0, self.hp / self.max_hp))
            fill_col = COLOR_HEALTH_RED if self.enemy_type == "boss" else (240, 160, 40)
            pygame.draw.rect(surface, fill_col, (bx, by, int(bar_w * pct), bar_h), border_radius=2)
            pygame.draw.rect(surface, (10, 8, 14), (bx, by, bar_w, bar_h), width=1, border_radius=2)
