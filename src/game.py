"""Main Game Controller, wave spawning director, state machine, and render loop."""

import math
import random
import pygame
from src.audio import get_audio
from src.config import (
    COLOR_BG,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from src.dungeon import Dungeon
from src.enemies import Enemy
from src.particles import ParticleManager
from src.player import Player
from src.ui import UPGRADE_CATALOG, UIManager


class GameState:
    MENU = "menu"
    CLASS_SELECT = "class_select"
    PLAYING = "playing"
    LEVEL_UP = "level_up"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    PAUSED = "paused"


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU

        # Class Selection
        self.class_keys = ["mage", "warrior", "assassin", "tank"]
        self.selected_class_idx = 0
        self.hovered_class_idx = 0
        self.anim_tick = 0.0

        # Managers
        self.audio = get_audio()
        self.particles = ParticleManager()
        self.ui = UIManager()
        self.dungeon = Dungeon()

        # Game Entities
        self.player = None
        self.enemies: list[Enemy] = []
        self.enemy_projectiles = []
        self.items = []

        # Time & Waves
        self.game_time = 0.0
        self.spawn_timer = 0.0
        self.boss_spawned = False
        self.boss_defeated = False

        # Card draft state
        self.draft_options: list[str] = []

        # Camera
        self.camera_x = 0.0
        self.camera_y = 0.0

        # Start ambient music
        self.audio.start_music()

    def reset_game(self, class_id: str = None):
        if class_id is None:
            class_id = self.class_keys[self.selected_class_idx]
        self.player = Player(class_id=class_id)
        self.enemies.clear()
        self.enemy_projectiles.clear()
        self.items.clear()
        self.particles = ParticleManager()
        self.game_time = 0.0
        self.spawn_timer = 0.0
        self.boss_spawned = False
        self.boss_defeated = False
        self.state = GameState.PLAYING

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.1)  # Clamp max dt to prevent spiral of death on window drag

            self.handle_events()
            self.update(dt)
            self.render()

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state in (GameState.MENU, GameState.GAME_OVER, GameState.VICTORY):
                        self.running = False

                if self.state == GameState.MENU:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = GameState.CLASS_SELECT
                        self.audio.play("gem")
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.running = False

                elif self.state == GameState.CLASS_SELECT:
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        self.selected_class_idx = 0
                        self.audio.play("gem")
                        self.reset_game(self.class_keys[0])
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        self.selected_class_idx = 1
                        self.audio.play("gem")
                        self.reset_game(self.class_keys[1])
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        self.selected_class_idx = 2
                        self.audio.play("gem")
                        self.reset_game(self.class_keys[2])
                    elif event.key in (pygame.K_4, pygame.K_KP4):
                        self.selected_class_idx = 3
                        self.audio.play("gem")
                        self.reset_game(self.class_keys[3])
                    elif event.key in (pygame.K_a, pygame.K_LEFT):
                        self.selected_class_idx = (self.selected_class_idx - 1) % len(self.class_keys)
                        self.audio.play("hit")
                    elif event.key in (pygame.K_d, pygame.K_RIGHT):
                        self.selected_class_idx = (self.selected_class_idx + 1) % len(self.class_keys)
                        self.audio.play("hit")
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.audio.play("gem")
                        self.reset_game(self.class_keys[self.selected_class_idx])
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.state = GameState.MENU

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_q:
                        self.state = GameState.MENU

                elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.reset_game()
                    elif event.key == pygame.K_c:
                        self.state = GameState.CLASS_SELECT
                    elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                        self.state = GameState.MENU

                elif self.state == GameState.LEVEL_UP:
                    if event.key in (pygame.K_1, pygame.K_KP1) and len(self.draft_options) > 0:
                        self.choose_upgrade(0)
                    elif event.key in (pygame.K_2, pygame.K_KP2) and len(self.draft_options) > 1:
                        self.choose_upgrade(1)
                    elif event.key in (pygame.K_3, pygame.K_KP3) and len(self.draft_options) > 2:
                        self.choose_upgrade(2)

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.player.start_dash(self.particles)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    if self.state == GameState.MENU:
                        self.state = GameState.CLASS_SELECT
                        self.audio.play("gem")
                    elif self.state == GameState.CLASS_SELECT:
                        if 0 <= self.hovered_class_idx < len(self.class_keys):
                            self.selected_class_idx = self.hovered_class_idx
                            self.audio.play("gem")
                            self.reset_game(self.class_keys[self.selected_class_idx])
                    elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                        self.state = GameState.CLASS_SELECT
                    elif self.state == GameState.LEVEL_UP:
                        if self.ui.hovered_card >= 0 and self.ui.hovered_card < len(self.draft_options):
                            self.choose_upgrade(self.ui.hovered_card)
                    elif self.state == GameState.PLAYING:
                        # Left click can also trigger dash or extra focus
                        self.player.start_dash(self.particles)

    def trigger_level_up_draft(self):
        self.state = GameState.LEVEL_UP
        # Pick 3 random unique upgrades from catalog
        keys = list(UPGRADE_CATALOG.keys())
        self.draft_options = random.sample(keys, min(3, len(keys)))

    def choose_upgrade(self, index: int):
        if index < 0 or index >= len(self.draft_options):
            return

        choice = self.draft_options[index]
        self._apply_upgrade(choice)
        self.audio.play("gem")

        self.player.pending_upgrades -= 1
        if self.player.pending_upgrades > 0:
            # Another pending level up to draft
            self.trigger_level_up_draft()
        else:
            self.state = GameState.PLAYING

    def _apply_upgrade(self, key: str):
        if key in ("wand", "cleave", "orbit", "lightning", "aura", "dagger"):
            self.player.weapons.level_up_weapon(key)
        elif key == "boots":
            self.player.speed_multiplier += 0.18
        elif key == "heart":
            self.player.max_hp += 30.0
            self.player.heal(30.0)
        elif key == "quickcast":
            self.player.cooldown_multiplier *= 0.85
        elif key == "crit":
            self.player.crit_chance += 0.12
        elif key == "magnet":
            self.player.magnet_radius *= 1.45
        elif key == "vampirism":
            self.player.vampirism += 0.08
        elif key == "regen":
            self.player.regen_rate += 1.2

    def update(self, dt: float):
        self.anim_tick += dt

        if self.state != GameState.PLAYING:
            return

        self.game_time += dt

        # Handle player input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update(dt, self.dungeon.pillars, self.particles)

        # Check death
        if not self.player.alive:
            self.state = GameState.GAME_OVER
            return

        # Check pending level up
        if self.player.pending_upgrades > 0:
            self.trigger_level_up_draft()
            return

        # Update dungeon torches
        self.dungeon.update(dt)

        # Update weapons
        self.player.weapons.update(dt, self.enemies, self.particles)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(dt, self.player, self.enemies, self.enemy_projectiles, self.particles)
            if not enemy.alive:
                enemy.on_death(self.player, self.items, self.particles)
                if enemy.enemy_type == "boss":
                    self.boss_defeated = True
                    self.state = GameState.VICTORY

        # Clean dead enemies
        self.enemies = [e for e in self.enemies if e.alive]

        # Update enemy projectiles
        for ep in self.enemy_projectiles:
            ep.update(dt, self.particles)
            # Check collision with player
            dist = math.hypot(ep.x - self.player.x, ep.y - self.player.y)
            if dist < (ep.radius + self.player.radius):
                ep.alive = False
                self.player.take_damage(ep.damage, self.particles)
        self.enemy_projectiles = [ep for ep in self.enemy_projectiles if ep.alive]

        # Player projectiles vs Enemies collision
        for proj in self.player.weapons.projectiles:
            if not proj.alive:
                continue
            for enemy in self.enemies:
                if not enemy.alive or enemy.id in proj.hit_enemies:
                    continue
                dist = math.hypot(enemy.x - proj.x, enemy.y - proj.y)
                if dist < (enemy.radius + proj.radius):
                    proj.hit_enemies.add(enemy.id)
                    proj.pierce -= 1
                    is_crit = random.random() < self.player.crit_chance
                    dmg = proj.damage * (2.5 if is_crit else 1.0)
                    enemy.take_damage(dmg, is_crit, self.particles)
                    self.audio.play("hit")

                    # Pushback
                    pdx = enemy.x - proj.x
                    pdy = enemy.y - proj.y
                    pdist = max(1.0, math.hypot(pdx, pdy))
                    enemy.kb_vx += (pdx / pdist) * 90.0
                    enemy.kb_vy += (pdy / pdist) * 90.0

                    if proj.pierce <= 0:
                        proj.alive = False
                        break

        # Check Nuke Bomb trigger from item pickup
        if self.player.trigger_nuke:
            self.player.trigger_nuke = False
            for enemy in self.enemies:
                if enemy.enemy_type != "boss":
                    enemy.alive = False
                    enemy.on_death(self.player, self.items, self.particles)
            self.enemies = [e for e in self.enemies if e.alive]

        # Update items
        for item in self.items:
            item.update(dt, self.player, self.items, self.particles)
        self.items = [i for i in self.items if i.alive]

        # Update particles & screen shake
        self.particles.update(dt)

        # Spawning Director
        self._spawn_director(dt)

        # Update camera (Smooth Lerp + Screen Shake)
        target_cam_x = self.player.x - SCREEN_WIDTH / 2.0
        target_cam_y = self.player.y - SCREEN_HEIGHT / 2.0
        self.camera_x += (target_cam_x - self.camera_x) * 0.12
        self.camera_y += (target_cam_y - self.camera_y) * 0.12

        # Clamp camera to dungeon borders
        self.camera_x = max(0, min(WORLD_WIDTH - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.camera_y))

    def _spawn_director(self, dt: float):
        self.spawn_timer += dt

        # Wave Escalation
        t = self.game_time
        wave_scale = 1.0 + (t / 120.0)  # Stat scaling over time

        # Max simultaneous enemies scales from 25 up to 90
        target_enemy_count = int(min(90, 25 + (t / 10.0)))
        spawn_interval = max(0.25, 1.4 - (t / 180.0))

        # Check Boss Spawn milestone (at 3 minutes = 180 seconds)
        if t >= 180.0 and not self.boss_spawned:
            self.boss_spawned = True
            self.audio.play("boss_roar")
            self.particles.shake.add_trauma(0.9)
            # Spawn Archlich Malakor 450px from player
            ang = random.uniform(0, 2.0 * math.pi)
            bx = self.player.x + math.cos(ang) * 450.0
            by = self.player.y + math.sin(ang) * 450.0
            self.enemies.append(Enemy(bx, by, "boss", wave_scale=wave_scale * 1.5))

        if self.spawn_timer >= spawn_interval:
            self.spawn_timer = 0.0

            if len(self.enemies) < target_enemy_count:
                # Determine pool of enemy archetypes based on time
                pool = ["slime"]
                if t > 30.0:
                    pool.extend(["skeleton"] * 2)
                if t > 70.0:
                    pool.append("golem")
                if t > 110.0:
                    pool.append("warlock")

                # Spawn cluster around player just off-screen
                cluster_size = random.randint(1, 4 if t > 60.0 else 2)
                spawn_angle = random.uniform(0, 2.0 * math.pi)
                spawn_dist = random.uniform(SCREEN_WIDTH * 0.55, SCREEN_WIDTH * 0.75)

                for _ in range(cluster_size):
                    etype = random.choice(pool)
                    ex = self.player.x + math.cos(spawn_angle) * spawn_dist + random.uniform(-40, 40)
                    ey = self.player.y + math.sin(spawn_angle) * spawn_dist + random.uniform(-40, 40)
                    # Keep inside world
                    ex = max(40, min(WORLD_WIDTH - 40, ex))
                    ey = max(40, min(WORLD_HEIGHT - 40, ey))
                    self.enemies.append(Enemy(ex, ey, etype, wave_scale=wave_scale))

    def render(self):
        # Calculate camera with screen shake
        shake_ox, shake_oy = self.particles.shake.get_offset()
        cam = (self.camera_x + shake_ox, self.camera_y + shake_oy)

        if self.state in (GameState.PLAYING, GameState.LEVEL_UP, GameState.PAUSED, GameState.GAME_OVER, GameState.VICTORY):
            # 1. Dungeon Floor & Outer Walls
            self.dungeon.render_background(self.screen, cam)

            # 2. Items & Pickups
            for item in self.items:
                item.render(self.screen, cam)

            # 3. Dungeon Obstacles / Pillars
            self.dungeon.render_pillars(self.screen, cam)

            # 4. Enemies
            for enemy in self.enemies:
                enemy.render(self.screen, cam)

            # 5. Enemy Projectiles
            for ep in self.enemy_projectiles:
                ep.render(self.screen, cam)

            # 6. Player
            self.player.render(self.screen, cam)

            # 7. Player Weapons & Orbiters
            self.player.weapons.render(self.screen, cam)

            # 8. Particles, damage numbers, and shockwaves
            self.particles.render(self.screen, cam)

            # 9. Dungeon Torchlight & Vignette
            self.dungeon.render_lighting(self.screen, cam, self.player.x, self.player.y)

            # 10. In-game HUD
            self.ui.render_hud(self.screen, self.player, self.game_time)

            # Modal overlays
            if self.state == GameState.LEVEL_UP:
                mouse_pos = pygame.mouse.get_pos()
                self.ui.render_level_up_modal(self.screen, self.draft_options, mouse_pos)
            elif self.state == GameState.PAUSED:
                self.ui.render_wrapped_text(self.screen, "PAUSED - PRESS ESC TO RESUME", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 400, self.ui.font_heading)
            elif self.state in (GameState.GAME_OVER, GameState.VICTORY):
                self.ui.render_game_over(self.screen, self.player, self.game_time, victory=(self.state == GameState.VICTORY))

        elif self.state == GameState.MENU:
            # Menu background
            self.screen.fill(COLOR_BG)
            self.ui.render_main_menu(self.screen)

        elif self.state == GameState.CLASS_SELECT:
            self.screen.fill(COLOR_BG)
            self.hovered_class_idx = self.ui.render_class_select(
                self.screen, self.selected_class_idx, pygame.mouse.get_pos(), self.anim_tick
            )

        pygame.display.flip()
