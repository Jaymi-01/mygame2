"""Player character entity, attributes, inputs, leveling, and dash mechanics."""

import math
import pygame
from src.audio import get_audio
from src.config import (
    CHARACTER_CLASSES,
    COLOR_ARCANE_CYAN,
    COLOR_HEALTH_RED,
    COLOR_WHITE,
    PLAYER_BASE_HP,
    PLAYER_BASE_MAGNET_RADIUS,
    PLAYER_BASE_SPEED,
    PLAYER_DASH_COOLDOWN,
    PLAYER_DASH_DURATION,
    PLAYER_DASH_SPEED,
    PLAYER_RADIUS,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.sprites import get_player_frames
from src.weapons import WeaponManager
from src.particles import Particle


class Player:
    def __init__(self, x: float = WORLD_WIDTH / 2.0, y: float = WORLD_HEIGHT / 2.0, class_id: str = "mage"):
        self.x = x
        self.y = y
        self.radius = PLAYER_RADIUS
        self.class_id = class_id
        self.class_info = CHARACTER_CLASSES.get(class_id, CHARACTER_CLASSES["mage"])

        # Class Base Stats
        self.max_hp = self.class_info["hp"]
        self.hp = self.max_hp
        self.base_speed = self.class_info["speed"]
        self.dash_cooldown_base = self.class_info["dash_cooldown"]
        self.dash_color = self.class_info["color"]
        self.starting_weapon = self.class_info["starting_weapon"]

        # Movement
        self.speed_multiplier = 1.0
        self.vx = 0.0
        self.vy = 0.0
        self.facing_left = False

        # Dash mechanics
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown_timer = 0.0
        self.dash_dir = (1.0, 0.0)

        # Level & Progression
        self.level = 1
        self.current_xp = 0
        self.xp_to_next = 15
        self.pending_upgrades = 0
        self.total_kills = 0

        # Stat Multipliers & Passives
        self.damage_multiplier = self.class_info["damage_multiplier"]
        self.cooldown_multiplier = self.class_info["cooldown_multiplier"]
        self.crit_chance = self.class_info["crit_chance"]
        self.crit_mult = self.class_info.get("crit_mult", 2.5)
        self.magnet_radius = self.class_info["magnet_radius"]
        self.regen_rate = self.class_info["regen_rate"]
        self.vampirism = self.class_info["vampirism"]

        # Status & Flags
        self.invulnerable_timer = 0.0
        self.trigger_nuke = False
        self.alive = True

        # Graphics & Animation
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.frames = get_player_frames(class_id)

        # Weapons (initialized with class starting weapon)
        self.weapons = WeaponManager(self)

    @property
    def speed(self) -> float:
        return self.base_speed * self.speed_multiplier

    def handle_input(self, keys):
        if self.is_dashing:
            return

        dx = 0.0
        dy = 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1.0
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1.0
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1.0

        length = math.hypot(dx, dy)
        if length > 0.0:
            self.vx = (dx / length) * self.speed
            self.vy = (dy / length) * self.speed
            self.dash_dir = (dx / length, dy / length)
            if dx < 0:
                self.facing_left = True
            elif dx > 0:
                self.facing_left = False
        else:
            self.vx = 0.0
            self.vy = 0.0

    def start_dash(self, particle_mgr=None):
        if self.dash_cooldown_timer <= 0.0 and not self.is_dashing:
            self.is_dashing = True
            self.dash_timer = PLAYER_DASH_DURATION
            self.dash_cooldown_timer = self.dash_cooldown_base
            self.invulnerable_timer = PLAYER_DASH_DURATION + 0.05
            get_audio().play("dash")

            if particle_mgr:
                particle_mgr.emit_shockwave(self.x, self.y, 45.0, self.dash_color, lifetime=0.25)
                particle_mgr.emit_burst(self.x, self.y, self.dash_color, count=10)

    def take_damage(self, amount: float, particle_mgr=None) -> bool:
        """Returns True if damage was applied."""
        if self.invulnerable_timer > 0.0 or not self.alive:
            return False

        self.hp = max(0.0, self.hp - amount)
        self.invulnerable_timer = 0.5  # brief invulnerability window
        get_audio().play("hurt")

        if particle_mgr:
            particle_mgr.add_damage_number(self.x, self.y - 20, int(amount), color=COLOR_HEALTH_RED)
            particle_mgr.emit_burst(self.x, self.y, COLOR_HEALTH_RED, count=14)
            particle_mgr.shake.add_trauma(0.4)

        if self.hp <= 0.0:
            self.alive = False

        return True

    def heal(self, amount: float) -> int:
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return int(self.hp - old_hp)

    def gain_xp(self, amount: int):
        self.current_xp += amount
        while self.current_xp >= self.xp_to_next:
            self.current_xp -= self.xp_to_next
            self.level += 1
            # Scaling XP threshold
            self.xp_to_next = int(18 * (1.2 ** (self.level - 1)) + (self.level * 10))
            self.pending_upgrades += 1
            get_audio().play("levelup")

    def update(self, dt: float, obstacles: list = None, particle_mgr = None):
        # Health regeneration passive
        if self.regen_rate > 0.0 and self.alive:
            self.hp = min(self.max_hp, self.hp + self.regen_rate * dt)

        # Timers
        if self.invulnerable_timer > 0.0:
            self.invulnerable_timer -= dt
        if self.dash_cooldown_timer > 0.0:
            self.dash_cooldown_timer -= dt

        # Dash execution
        if self.is_dashing:
            self.dash_timer -= dt
            self.x += self.dash_dir[0] * PLAYER_DASH_SPEED * dt
            self.y += self.dash_dir[1] * PLAYER_DASH_SPEED * dt

            if particle_mgr:
                particle_mgr.particles.append(
                    Particle(
                        self.x,
                        self.y,
                        -self.dash_dir[0] * 50,
                        -self.dash_dir[1] * 50,
                        self.dash_color,
                        radius=4.0,
                        lifetime=0.2,
                    )
                )

            if self.dash_timer <= 0.0:
                self.is_dashing = False
        else:
            self.x += self.vx * dt
            self.y += self.vy * dt

        # Boundary clamping
        margin = 32
        self.x = max(margin, min(WORLD_WIDTH - margin, self.x))
        self.y = max(margin, min(WORLD_HEIGHT - margin, self.y))

        # Obstacle collision (pillars)
        if obstacles:
            for obs in obstacles:
                dx = self.x - obs.x
                dy = self.y - obs.y
                dist = math.hypot(dx, dy)
                min_dist = self.radius + obs.radius
                if dist < min_dist and dist > 0.001:
                    push = min_dist - dist
                    self.x += (dx / dist) * push
                    self.y += (dy / dist) * push

        # Animation frame update
        if abs(self.vx) > 0.1 or abs(self.vy) > 0.1:
            self.anim_timer += dt * 10.0
            self.anim_frame = int(self.anim_timer) % len(self.frames)
        else:
            self.anim_timer = 0.0
            self.anim_frame = 0

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        # Flicker when invulnerable
        if self.invulnerable_timer > 0.0 and int(self.invulnerable_timer * 20) % 2 == 0:
            return

        frame = self.frames[self.anim_frame]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)

        draw_x = int(self.x - camera_offset[0] - frame.get_width() // 2)
        draw_y = int(self.y - camera_offset[1] - frame.get_height() // 2)
        surface.blit(frame, (draw_x, draw_y))
