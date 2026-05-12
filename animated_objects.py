import pygame
import math
import random

class AnimatedMainTown:
    def __init__(self, x, y, path, team, scale_factor=1.0):
        self.original_image = pygame.image.load(path).convert_alpha()
        if scale_factor != 1.0:
            new_size = (int(self.original_image.get_width() * scale_factor),
                        int(self.original_image.get_height() * scale_factor))
            self.image = pygame.transform.scale(self.original_image, new_size)
        else:
            self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.team = team
        self.time = 0
        self.health = 500
        self.max_health = 500
        self.damage = 10
        self.attack_range = 60
        self.attack_cooldown = 2.0
        self.last_attack_time = 0.0

    def take_damage(self, amount, attacker=None):
        self.health -= amount
        if self.health <= 0:
            print(f"Main town {self.team} destroyed!")

    def attack_targets(self, targets, current_time):
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        for target in targets:
            if target.team != self.team:
                distance = pygame.math.Vector2(self.rect.center).distance_to(target.position if hasattr(target, 'position') else target.rect.center)
                if distance <= self.attack_range:
                    target.take_damage(self.damage, self)
                    self.last_attack_time = current_time
                    break

    def update(self, dt):
        self.time += dt * 2
        self.glow = int(30 * (math.sin(self.time * 5) + 1))

    def get_image(self):
        if self.health <= 0:
            blank = pygame.Surface((1, 1), pygame.SRCALPHA)
            return blank, pygame.Rect(-100, -100, 1, 1)
        img = self.image.copy()
        if self.glow > 10:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((self.glow, self.glow, self.glow, 80))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        return img, self.rect

class AnimatedTower:
    def __init__(self, x, y, path, team, scale_factor=1.0):
        self.original_image = pygame.image.load(path).convert_alpha()
        if scale_factor != 1.0:
            new_size = (int(self.original_image.get_width() * scale_factor),
                        int(self.original_image.get_height() * scale_factor))
            self.image = pygame.transform.scale(self.original_image, new_size)
        else:
            self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.team = team
        self.time = 0
        self.original_center = self.rect.center
        self.health = 200
        self.max_health = 200
        self.damage = 5
        self.attack_range = 60
        self.attack_cooldown = 1.0
        self.last_attack_time = 0.0
        self.current_target = None

    @property
    def hp(self):
        return self.health

    def take_damage(self, amount, attacker=None):
        self.health -= amount
        if self.health <= 0:
            print(f"Tower {self.team} destroyed!")

    def draw_health_bar(self, screen, camera_x=0, camera_y=0):
        bar_width = self.rect.width
        bar_height = 8
        x = self.rect.x - camera_x
        y = self.rect.y - camera_y - 12
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        health_percent = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * health_percent, bar_height))

    def update(self, dt, creeps=None):
        self.time += dt * 5
        self.shake_x = math.sin(self.time * 10) * 1.5
        self.shake_y = math.sin(self.time * 12) * 1.5
        self.glow = int(40 * (math.sin(self.time * 8) + 1))

    def attack_targets(self, targets, current_time, bullets):
        if self.health <= 0:
            return
        if self.current_target is not None:
            if not self._is_valid_target(self.current_target) or not self._in_range(self.current_target):
                self.current_target = None
        if self.current_target is None:
            candidates = [t for t in targets if self._is_valid_target(t) and self._in_range(t)]
            if not candidates:
                return
            candidates.sort(key=lambda t: (0 if isinstance(t, Creep) else 1,
                                          pygame.math.Vector2(self.rect.center).distance_to(self._target_position(t))))
            self.current_target = candidates[0]
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        if not self._in_range(self.current_target):
            self.current_target = None
            return
        self.attack_target(self.current_target, bullets)
        self.last_attack_time = current_time

    def _is_valid_target(self, target):
        if isinstance(target, Creep):
            return target.team != self.team and getattr(target, 'hp', 0) > 0
        if isinstance(target, AnimatedCharacter):
            return target.team != self.team and getattr(target, 'health', 0) > 0
        return False

    def _target_position(self, target):
        return target.position if hasattr(target, 'position') else pygame.math.Vector2(target.rect.center)

    def _in_range(self, target):
        return pygame.math.Vector2(self.rect.center).distance_to(self._target_position(target)) <= self.attack_range

    def attack_target(self, target, bullets):
        if target is None:
            return
        from bullet import Bullet
        bullet = Bullet(self.rect.centerx, self.rect.centery, target, self.damage, speed=180)
        bullets.append(bullet)

    def get_image(self):
        if self.health <= 0:
            blank = pygame.Surface((1, 1), pygame.SRCALPHA)
            return blank, pygame.Rect(-100, -100, 1, 1)
        img = self.image.copy()
        if self.glow > 10:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((self.glow, self.glow, self.glow, 100))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        new_rect = self.rect.move(self.shake_x, self.shake_y)
        return img, new_rect
class AnimatedGrass:
    def __init__(self, x, y, path, scale_factor=1.0):
        self.original_image = pygame.image.load(path).convert_alpha()
        if scale_factor != 1.0:
            new_size = (int(self.original_image.get_width() * scale_factor),
                        int(self.original_image.get_height() * scale_factor))
            self.image = pygame.transform.scale(self.original_image, new_size)
        else:
            self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.time = 0
        self.original_center = self.rect.center

    def update(self, dt):
        self.time += dt * 4
        self.angle = math.sin(self.time) * 3

    def get_image(self):
        rotated = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        return rotated, new_rect

# ---------- Phần của Trug-Kien ----------
def load_surface(path, scale_factor=1.0, remove_bg=False):
    surface = pygame.image.load(path)
    if remove_bg:
        surface = surface.convert()
        colorkey = surface.get_at((0, 0))
        surface.set_colorkey(colorkey, pygame.RLEACCEL)
        surface = surface.convert_alpha()
    else:
        try:
            surface = surface.convert_alpha()
        except Exception:
            surface = surface.convert()
    if scale_factor != 1.0:
        new_size = (int(surface.get_width() * scale_factor), int(surface.get_height() * scale_factor))
        surface = pygame.transform.smoothscale(surface, new_size)
    return surface

class AnimatedCharacter:
    def __init__(self, x, y, scale_factor=1.0, player_id=1):
        self.position = pygame.math.Vector2(x, y)
        self.speed = 100 * scale_factor
        self.frame_index = 0.0
        self.frame_speed = 12.0
        self.facing = 'right'
        self.moving = False
        self.state = 'idle'
        self.scale_factor = scale_factor
        self.player_id = player_id
        self.team = "blue" if player_id == 1 else "red"   # Quan trọng!

        # Health and stamina
        self.health = 100
        self.max_health = 100
        self.stamina = 150
        self.max_stamina = 150
        self.stamina_regen_rate = 10
        self.kill_count = 0
        self.death_count = 0
        self.last_damage_by_player = None
        self.last_damage_time = 0.0
        self.last_damage_dealt_time = 0.0
        self.last_damage_received_time = 0.0
        self.invulnerable = False
        self.hit_timer = 0.0
        self.hit_duration = 0.2
        self.damage = 10
        self.attack_range = 30  # Tăng lên 30 pixel

        # Respawning
        self.is_dead = False
        self.respawn_timer = 0.0
        self.respawn_base = 3.0
        self.respawn_growth_interval = 10.0
        self.start_position = pygame.math.Vector2(x, y)

        # Load frames
        self.run_right_frames = [load_surface(f"modelheros/run_right_{i}.png", scale_factor) for i in range(1, 9)]
        self.run_left_frames = [pygame.transform.flip(img, True, False) for img in self.run_right_frames]

        self.walk_right_frames = [load_surface(f"modelheros/walk_right_{i}.png", scale_factor) for i in range(1, 9)]
        self.walk_left_frames = [pygame.transform.flip(img, True, False) for img in self.walk_right_frames]

        self.idle_right = load_surface("modelheros/hero01_BenPhai.png", scale_factor, remove_bg=True)
        self.idle_left = load_surface("modelheros/hero01_BenTrai.png", scale_factor, remove_bg=True)

        self.combat1_right_frames = [
            load_surface("modelheros/combo_right.1.1.png", scale_factor),
            load_surface("modelheros/combo_right1.2.png", scale_factor),
            load_surface("modelheros/combo_right.1.3.png", scale_factor),
            load_surface("modelheros/combo_right.1.4.png", scale_factor)
        ]
        self.combat1_left_frames = [pygame.transform.flip(img, True, False) for img in self.combat1_right_frames]

        self.combat2_right_frames = [load_surface(f"modelheros/combo_right.2.{i}.png", scale_factor) for i in range(1, 5)]
        self.combat2_left_frames = [pygame.transform.flip(img, True, False) for img in self.combat2_right_frames]

        self.dash_right_frames = [load_surface(f"modelheros/dash_right_{i}.png", scale_factor) for i in range(1, 5)]
        self.dash_left_frames = [pygame.transform.flip(img, True, False) for img in self.dash_right_frames]

        self.guard_right_frames = [load_surface(f"modelheros/guard_right_{i}.png", scale_factor) for i in range(1, 3)]
        self.guard_left_frames = [pygame.transform.flip(img, True, False) for img in self.guard_right_frames]

        self.current_frames = self.run_right_frames
        self.rect = self.idle_right.get_rect(center=self.position)

        self.combo_step = 0
        self.dash_timer = 0.0
        self.guard_active = False
        self.animation_timer = 0.0
        self.combat_active = False
        self.dash_active = False
        self.last_hit_target = None
        self.last_hit_frame = -1

    def update(self, dt, keys=None, game_map=None):
        if keys is None:
            keys = pygame.key.get_pressed()

        if self.is_dead:
            if game_map is not None:
                self.init_respawn_timer(game_map.game_time)
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                self.respawn()
            return

        self.moving = False
        dx = 0
        dy = 0

        # Player 1 (WASD) and Player 2 (Arrows) - but here we only have one?
        # To support two players, we need different key sets based on player_id.
        # For simplicity, you can keep as is and later separate. I'll assume single player for now.
        # But to match the code, we'll keep original key mapping (WASD) and add second player keys later if needed.
        # Actually, your code earlier had two players, so I'll add key mapping for both.

        # Determine control keys based on player_id
        if self.player_id == 1:
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]
            move_up = keys[pygame.K_w]
            move_down = keys[pygame.K_s]
            attack1 = keys[pygame.K_j]
            attack2 = keys[pygame.K_k]
            attack3 = keys[pygame.K_l]
        else:
            move_left = keys[pygame.K_LEFT]
            move_right = keys[pygame.K_RIGHT]
            move_up = keys[pygame.K_UP]
            move_down = keys[pygame.K_DOWN]
            attack1 = keys[pygame.K_KP1]
            attack2 = keys[pygame.K_KP2]
            attack3 = keys[pygame.K_KP3]

        if not self.guard_active:
            if move_left:
                dx -= self.speed * dt
                self.facing = 'left'
                self.moving = True
            if move_right:
                dx += self.speed * dt
                self.facing = 'right'
                self.moving = True
            if move_up:
                dy -= self.speed * dt
                self.moving = True
            if move_down:
                dy += self.speed * dt
                self.moving = True

        if attack1 and not self.combat_active and not self.dash_active:
            if self.combo_step == 0:
                self.combo_step = 1
                self.state = 'combat1'
                self.frame_index = 0.0
                self.animation_timer = 0.0
                self.combat_active = True
            elif self.combo_step == 1 and self.animation_timer > 0.2:
                self.combo_step = 2
                self.state = 'combat2'
                self.frame_index = 0.0
                self.animation_timer = 0.0
                self.combat_active = True

        if attack3 and not self.combat_active and not self.dash_active and self.stamina >= 50:
            self.state = 'dash'
            self.dash_timer = 0.3
            self.frame_index = 0.0
            self.animation_timer = 0.0
            self.dash_active = True
            self.stamina -= 50

        if attack2 and not self.combat_active and not self.dash_active:
            self.guard_active = True
            self.state = 'guard'
            self.frame_index = 0.0
            self.invulnerable = True
        else:
            self.guard_active = False
            self.invulnerable = False

        self.animation_timer += dt

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * dt)

        # Health regen after 5 seconds of no combat
        current_time = pygame.time.get_ticks() / 1000.0
        if (current_time - self.last_damage_dealt_time > 5.0 and
            current_time - self.last_damage_received_time > 5.0 and
            self.health < self.max_health):
            self.health = min(self.max_health, self.health + 5 * dt)

        if self.dash_active:
            dash_speed = self.speed * 3
            if self.facing == 'right':
                dx += dash_speed * dt
            else:
                dx -= dash_speed * dt
            self.moving = True
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_active = False
                self.state = 'idle'

        if self.combat_active:
            if self.frame_index >= len(self.current_frames) - 1:
                self.combat_active = False
                self.state = 'idle'
                self.last_hit_target = None
                if self.combo_step == 1 or self.combo_step == 2:
                    self.combo_step = 0

        if not self.combat_active and not self.dash_active:
            if self.guard_active:
                self.state = 'guard'
            elif self.moving:
                self.state = 'run'
            else:
                self.state = 'idle'

        new_x = self.position.x + dx
        new_y = self.position.y + dy

        # Check movement constraints (polygon, etc.)
        can_move = True
        if game_map and not game_map.point_in_polygon(new_x, new_y):
            can_move = False
            # Allow small step to reach enemy main town
            for obj in game_map.animated_objects:
                if isinstance(obj, AnimatedMainTown) and obj.team != self.team:
                    town_center = pygame.math.Vector2(obj.rect.center)
                    if pygame.math.Vector2(new_x, new_y).distance_to(town_center) <= 5:
                        can_move = True
                        break
            # Also allow through access zones (if defined)
            if not can_move:
                target_team = "blue" if self.team == "red" else "red"
                if hasattr(game_map, 'point_in_main_town_access_zone') and game_map.point_in_main_town_access_zone(new_x, new_y, target_team):
                    can_move = True

        if can_move:
            self.position.x = new_x
            self.position.y = new_y
        elif not self.moving and not self.dash_active:
            pass

        # Set frames based on state
        if self.state == 'run':
            if self.facing == 'right':
                self.current_frames = self.run_right_frames
            else:
                self.current_frames = self.run_left_frames
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index -= len(self.current_frames)
        elif self.state == 'combat1':
            if self.facing == 'right':
                self.current_frames = self.combat1_right_frames
            else:
                self.current_frames = self.combat1_left_frames
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index = len(self.current_frames) - 1
        elif self.state == 'combat2':
            if self.facing == 'right':
                self.current_frames = self.combat2_right_frames
            else:
                self.current_frames = self.combat2_left_frames
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index = len(self.current_frames) - 1
        elif self.state == 'dash':
            if self.facing == 'right':
                self.current_frames = self.dash_right_frames
            else:
                self.current_frames = self.dash_left_frames
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index = len(self.current_frames) - 1
        elif self.state == 'guard':
            if self.facing == 'right':
                self.current_frames = self.guard_right_frames
            else:
                self.current_frames = self.guard_left_frames
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index = len(self.current_frames) - 1

        if self.state == 'idle':
            self.rect = (self.idle_right if self.facing == 'right' else self.idle_left).get_rect(center=self.position)
        else:
            self.rect = self.current_frames[int(self.frame_index)].get_rect(center=self.position)

        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)

    def check_and_deal_damage(self, other, game_map=None):
        if not other or not self.combat_active:
            return

        if isinstance(other, AnimatedMainTown) and game_map:
            enemy_team = other.team
            alive_towers = game_map.count_alive_towers(enemy_team)
            if alive_towers > 0:
                return

        current_frame = int(self.frame_index)
        total_frames = len(self.current_frames) if self.current_frames else 1

        if total_frames >= 3 and current_frame >= 1 and current_frame <= 2:
            other_pos = other.position if hasattr(other, 'position') else pygame.math.Vector2(other.rect.center)
            distance = self.position.distance_to(other_pos)
            if distance <= self.attack_range:
                if self.last_hit_target != other or current_frame != self.last_hit_frame:
                    other.take_damage(self.damage, self)
                    self.last_damage_dealt_time = pygame.time.get_ticks() / 1000.0
                    self.last_hit_target = other
                    self.last_hit_frame = current_frame
            else:
                self.last_hit_target = None

    def take_damage(self, damage, attacker=None):
        if self.is_dead:
            return

        current_time = pygame.time.get_ticks() / 1000.0
        self.last_damage_received_time = current_time

        if isinstance(attacker, AnimatedCharacter) and attacker is not self and attacker.team != self.team:
            self.last_damage_by_player = attacker
            self.last_damage_time = current_time

        if self.guard_active:
            if self.stamina >= 10:
                self.stamina = max(0, self.stamina - 10)
                self.hit_timer = self.hit_duration
                print(f"Player {self.player_id}: Guarded attack. Stamina -10 -> {self.stamina}")
                return

        if not self.invulnerable:
            self.health -= damage
            self.hit_timer = self.hit_duration
            print(f"Player {self.player_id} took {damage} damage! Health: {self.health}")
            if self.health <= 0:
                self.health = 0
                self.is_dead = True
                self.respawn_timer = 0.0
                self.death_count += 1

                kill_assigned = False
                if isinstance(attacker, AnimatedCharacter) and attacker.team != self.team:
                    attacker.kill_count += 1
                    kill_assigned = True
                    print(f"Player {attacker.player_id} killed Player {self.player_id}! Kill count: {attacker.kill_count}")
                elif self.last_damage_by_player and self.last_damage_by_player.team != self.team and current_time - self.last_damage_time <= 7.0:
                    self.last_damage_by_player.kill_count += 1
                    kill_assigned = True
                    print(f"Player {self.last_damage_by_player.player_id} earned the kill on Player {self.player_id} via recent damage! Kill count: {self.last_damage_by_player.kill_count}")

                print(f"Player {self.player_id} died! Death count: {self.death_count}")

    def init_respawn_timer(self, game_time):
        if self.respawn_timer <= 0:
            self.respawn_timer = self.compute_respawn_time(game_time)
            print(f"Player {self.player_id} will respawn in {self.respawn_timer:.1f}s")

    def compute_respawn_time(self, game_time):
        extra = int(game_time / self.respawn_growth_interval)
        return self.respawn_base + extra

    def respawn(self):
        self.is_dead = False
        self.health = self.max_health
        self.stamina = self.max_stamina
        self.invulnerable = False
        self.guard_active = False
        self.dash_active = False
        self.combat_active = False
        self.state = 'idle'
        self.frame_index = 0.0
        self.respawn_timer = 0.0
        self.position = self.start_position.copy()
        self.rect = self.idle_right.get_rect(center=self.position)
        print(f"Player {self.player_id} respawned")

    def get_image(self):
        if self.is_dead:
            blank = pygame.Surface((1, 1), pygame.SRCALPHA)
            return blank, pygame.Rect(-100, -100, 1, 1)

        if self.state == 'idle':
            image = self.idle_right if self.facing == 'right' else self.idle_left
        elif self.state in ['run', 'combat1', 'combat2', 'dash', 'guard']:
            image = self.current_frames[int(self.frame_index)]
        else:
            image = self.idle_right if self.facing == 'right' else self.idle_left

        if self.hit_timer > 0:
            image = image.copy()
            overlay = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 120))
            image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return image, self.rect
# ---------- Class Creep ----------
class Creep:
    def __init__(self, x, y, team, target_pos, creep_type, image_path, scale_factor=1.0):
        self.position = pygame.math.Vector2(x, y)
        self.team = team
        self.creep_type = creep_type
        self.scale_factor = scale_factor
        self.target_pos = pygame.math.Vector2(target_pos)   # điểm đích (base đối phương)

        # Chỉ số theo loại lính (tùy chỉnh theo ý bạn)
        stats = {
            'orc_tanker': {'hp': 140, 'speed': 28, 'damage': 4, 'color': (80, 80, 180)},
            'orc_warrior': {'hp': 100, 'speed': 36, 'damage': 5, 'color': (120, 80, 180)},
            'slime': {'hp': 65, 'speed': 34, 'damage': 3, 'color': (80, 200, 120)},
            'warrior': {'hp': 90, 'speed': 34, 'damage': 4, 'color': (200, 100, 100)},
            'archer': {'hp': 55, 'speed': 32, 'damage': 3, 'color': (200, 180, 80)},
            'mage': {'hp': 50, 'speed': 30, 'damage': 4, 'color': (150, 100, 220)},
        }.get(creep_type, {'hp': 70, 'speed': 30, 'damage': 3, 'color': (180, 180, 180)})

        self.max_hp = stats['hp']
        self.hp = stats['hp']
        self.speed = stats['speed'] * scale_factor
        self.damage = stats['damage']
        self.attack_range = 20
        self.attack_cooldown = 1.5          # giây giữa các đòn
        self.last_attack_time = 0.0
        self.hit_timer = 0.0                # hiệu ứng bị đánh
        self.hit_duration = 0.2
        self.attack_timer = 0.0             # hiệu ứng tấn công

        # Load ảnh (nếu có)
        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            if scale_factor != 1.0:
                new_size = (int(self.original_image.get_width() * scale_factor),
                            int(self.original_image.get_height() * scale_factor))
                self.image = pygame.transform.scale(self.original_image, new_size)
            else:
                self.image = self.original_image
        except Exception:
            # Ảnh dự phòng: hình vuông màu
            self.image = pygame.Surface((int(24 * scale_factor), int(24 * scale_factor)), pygame.SRCALPHA)
            self.image.fill(stats['color'])

        self.rect = self.image.get_rect(center=self.position)

    def update(self, dt, enemies=None, towers=None, game_map=None):
        if self.hp <= 0:
            return

        current_time = pygame.time.get_ticks() / 1000.0

        # 1. Tấn công lính địch nếu có trong tầm
        if enemies:
            for enemy in enemies:
                if enemy.team == self.team:
                    continue
                # Kiểm tra enemy có còn sống không
                enemy_hp = getattr(enemy, 'hp', getattr(enemy, 'health', 0))
                if enemy_hp <= 0:
                    continue
                enemy_pos = enemy.position if hasattr(enemy, 'position') else pygame.math.Vector2(enemy.rect.center)
                distance = self.position.distance_to(enemy_pos)
                if distance <= self.attack_range:
                    self.attack(enemy, current_time)
                    return   # đã tấn công, không di chuyển trong frame này

        # 2. Tấn công tháp địch nếu có trong tầm (và không có lính địch)
        if towers:
            for tower in towers:
                if tower.team == self.team or tower.health <= 0:
                    continue
                distance = self.position.distance_to(pygame.math.Vector2(tower.rect.center))
                if distance <= self.attack_range:
                    self.attack(tower, current_time)
                    return

        # 3. Không có mục tiêu trong tầm → di chuyển về target_pos
        direction = self.target_pos - self.position
        if direction.length() > 4:                # tránh rung lắc khi gần đến nơi
            direction = direction.normalize()
            self.position += direction * self.speed * dt
            self.rect.center = self.position

        # 4. Giới hạn trong map (nếu có game_map)
        if game_map is not None:
            self.position.x = max(0, min(self.position.x, game_map.map_width))
            self.position.y = max(0, min(self.position.y, game_map.map_height))
            self.rect.center = self.position

        # 5. Cập nhật timer hiệu ứng
        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)
        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)

    def attack(self, target, current_time):
        """Tấn công mục tiêu (creep, tháp, nhà chính,...)"""
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        # Kiểm tra mục tiêu còn sống
        hp = getattr(target, 'hp', getattr(target, 'health', 0))
        if hp <= 0:
            return

        target.take_damage(self.damage, self)
        self.last_attack_time = current_time
        self.hit_timer = self.hit_duration
        self.attack_timer = self.attack_duration

    def take_damage(self, damage, attacker=None):
        self.hp -= damage
        self.hit_timer = self.hit_duration
        if self.hp <= 0:
            self.hp = 0
            print(f"Creep {self.creep_type} ({self.team}) died!")

    def draw_health_bar(self, screen):
        if self.hp <= 0:
            return
        bar_width = 40
        bar_height = 6
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 15
        pygame.draw.rect(screen, (50, 0, 0), (x, y, bar_width, bar_height))
        hp_ratio = max(0, self.hp) / max(1, self.max_hp)
        fill_width = int(bar_width * hp_ratio)
        pygame.draw.rect(screen, (200, 20, 20), (x, y, fill_width, bar_height))
        font = pygame.font.SysFont(None, 14)
        text = font.render(str(self.hp), True, (255, 255, 255))
        screen.blit(text, (x + bar_width // 2 - 8, y - 12))

    def get_image(self):
        if self.hp <= 0:
            blank = pygame.Surface((1, 1), pygame.SRCALPHA)
            return blank, pygame.Rect(-100, -100, 1, 1)

        img = self.image.copy()
        if self.attack_timer > 0:
            # Hiệu ứng vàng khi tấn công
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 180, 0, 100))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            pygame.draw.circle(img, (255, 255, 0), (img.get_width() // 2, img.get_height() // 2),
                               max(3, img.get_width() // 6), 1)
        elif self.hit_timer > 0:
            # Hiệu ứng đỏ khi bị đánh
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 90))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        return img, self.rect