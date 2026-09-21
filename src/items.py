"""Collectible items and drops: XP Gems, Health Potions, Magnets, Bombs, and Chests."""

import math
import random
import pygame
from src.audio import get_audio
from src.config import COLOR_HEALTH_GREEN, COLOR_XP_GEM, COLOR_XP_LEGENDARY, COLOR_XP_RARE
from src.sprites import get_bomb_sprite, get_chest_sprite, get_gem_sprite, get_magnet_sprite, get_potion_sprite


class Item:
    def __init__(self, x: float, y: float, item_type: str):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.vx = random.uniform(-40, 40)
        self.vy = random.uniform(-40, 40)
        self.bob_timer = random.uniform(0, 6.28)
        self.radius = 12.0
        self.alive = True
        self.is_magnetized = False
        self.sprite = self._init_sprite()

    def _init_sprite(self) -> pygame.Surface:
        if self.item_type == "gem_normal":
            return get_gem_sprite("normal")
        elif self.item_type == "gem_rare":
            return get_gem_sprite("rare")
        elif self.item_type == "gem_legendary":
            return get_gem_sprite("legendary")
        elif self.item_type == "potion":
            return get_potion_sprite()
        elif self.item_type == "magnet":
            return get_magnet_sprite()
        elif self.item_type == "bomb":
            return get_bomb_sprite()
        elif self.item_type == "chest":
            return get_chest_sprite()
        return get_gem_sprite("normal")

    def update(self, dt: float, player, all_gems: list = None, particle_mgr = None):
        self.bob_timer += dt * 4.0

        # Initial drop friction
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vx *= 0.88 ** (dt * 60.0)
        self.vy *= 0.88 ** (dt * 60.0)

        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        # Magnet attraction
        magnet_range = player.magnet_radius if not self.is_magnetized else 9999.0
        if dist < magnet_range or self.is_magnetized:
            self.is_magnetized = True
            # Accelerate smoothly toward player
            speed = max(380.0, 750.0 - dist)
            if dist > 0.001:
                self.x += (dx / dist) * speed * dt
                self.y += (dy / dist) * speed * dt

        # Collision with player
        if dist < (self.radius + player.radius):
            self.on_collect(player, all_gems, particle_mgr)
            self.alive = False

    def on_collect(self, player, all_gems: list = None, particle_mgr = None):
        audio = get_audio()

        if self.item_type == "gem_normal":
            player.gain_xp(1)
            audio.play("gem")
            if particle_mgr:
                particle_mgr.emit_burst(self.x, self.y, COLOR_XP_GEM, count=6, speed_range=(30, 90))

        elif self.item_type == "gem_rare":
            player.gain_xp(5)
            audio.play("gem")
            if particle_mgr:
                particle_mgr.emit_burst(self.x, self.y, COLOR_XP_RARE, count=10, speed_range=(40, 120))

        elif self.item_type == "gem_legendary":
            player.gain_xp(25)
            audio.play("gem")
            if particle_mgr:
                particle_mgr.emit_burst(self.x, self.y, COLOR_XP_LEGENDARY, count=16, speed_range=(50, 160))

        elif self.item_type == "potion":
            heal_amount = 35
            actual = player.heal(heal_amount)
            audio.play("gem")
            if particle_mgr:
                particle_mgr.add_damage_number(player.x, player.y - 20, actual, is_heal=True)
                particle_mgr.emit_burst(player.x, player.y, COLOR_HEALTH_GREEN, count=12)

        elif self.item_type == "magnet":
            audio.play("chest")
            if all_gems:
                for g in all_gems:
                    g.is_magnetized = True
            if particle_mgr:
                particle_mgr.emit_shockwave(player.x, player.y, 400.0, (80, 200, 255), lifetime=0.5)

        elif self.item_type == "bomb":
            audio.play("kill")
            if particle_mgr:
                particle_mgr.emit_shockwave(self.x, self.y, 600.0, (255, 140, 40), lifetime=0.6, width=6)
                particle_mgr.shake.add_trauma(0.7)
            # Notify player to trigger screen wipe
            player.trigger_nuke = True

        elif self.item_type == "chest":
            audio.play("chest")
            player.gain_xp(50)
            player.heal(50)
            player.pending_upgrades += 1  # Bonus free upgrade card draft!
            if particle_mgr:
                particle_mgr.emit_shockwave(self.x, self.y, 250.0, COLOR_XP_LEGENDARY, lifetime=0.5)
                particle_mgr.emit_burst(self.x, self.y, COLOR_XP_LEGENDARY, count=24, speed_range=(60, 200))

    def render(self, surface: pygame.Surface, camera_offset: tuple):
        bob_offset = math.sin(self.bob_timer) * 3.0
        draw_x = int(self.x - camera_offset[0] - self.sprite.get_width() // 2)
        draw_y = int(self.y - camera_offset[1] - self.sprite.get_height() // 2 + bob_offset)
        surface.blit(self.sprite, (draw_x, draw_y))
