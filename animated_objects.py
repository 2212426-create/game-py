import pygame
import math
import random
from bullet import Bullet


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
        self.health = 500  # Main town health, higher than towers
        self.max_health = 500
        self.damage = 30  # Higher damage
        self.attack_range = 60  # Larger range
        self.attack_cooldown = 2.0  # Slower attack
        self.last_attack_time = 0.0

    def take_damage(self, damage, attacker=None):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            print(f"Main Town {self.team} destroyed!")

    def attack_targets(self, targets, current_time):
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        for target in targets:
            if target.team != self.team:  # Don't attack own team
                distance = pygame.math.Vector2(self.rect.center).distance_to(
                    target.position if hasattr(target, 'position') else target.rect.center)
                if distance <= self.attack_range:
                    target.take_damage(self.damage, self)  # Pass self as attacker
                    self.last_attack_time = current_time
                    print(f"Main Town {self.team} attacked {target}")
                    break  # Attack one target per cooldown

    def update(self, dt):
        # Có thể thêm animation cho nhà chính (ví dụ glow)
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
        # Scale ảnh tháp theo hệ số
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
        self.health = 200  # Tower health
        self.max_health = 200
        self.damage = 50  # Damage per attack
        self.attack_range = 100  # Attack range
        self.attack_cooldown = 1.0  # Attack every 1 second
        self.last_attack_time = 0.0
        self.current_target = None

    def take_damage(self, damage, attacker=None):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            print(f"Tower {self.team} destroyed!")

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

    def attack_targets(self, targets, current_time, bullets=None):
        if self.health <= 0:
            return

        if self.current_target is not None:
            if not self._is_valid_target(self.current_target) or not self._in_range(self.current_target):
                self.current_target = None

        if self.current_target is None:
            candidates = [t for t in targets if self._is_valid_target(t) and self._in_range(t)]
            if not candidates:
                return

            def priority_key(t):
                priority = 0 if isinstance(t, Creep) else 1
                return (priority, pygame.math.Vector2(self.rect.center).distance_to(self._target_position(t)))

            candidates.sort(key=priority_key)
            self.current_target = candidates[0]

        if current_time - self.last_attack_time < self.attack_cooldown:
            return

        if self.current_target is None:
            return

        if not self._in_range(self.current_target):
            self.current_target = None
            return

        self.attack_target(self.current_target, bullets)
        self.last_attack_time = current_time
        print(f"Tower {self.team} attacked {self.current_target}")

    def attack_target(self, target, bullets, damage=None, speed=None, image_path=None):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        if target is None:
            return
        target_hp = getattr(target, 'hp', None)
        target_health = getattr(target, 'health', None)
        if (target_hp is not None and target_hp <= 0) or (target_health is not None and target_health <= 0):
            return

        projectile_damage = damage if damage is not None else self.damage
        projectile_speed = speed if speed is not None else 180
        bullets.append(Bullet(self.rect.centerx, self.rect.centery, target, projectile_damage, speed=projectile_speed,
                              image_path=image_path))
        self.last_attack_time = current_time
        print(f"Tower {self.team} fired bullet at {target}")

    @property
    def hp(self):
        return self.health

    def update(self, dt, creeps=None):
        self.time += dt * 5  # tốc độ animation
        # Rung nhẹ và glow dùng sin
        self.shake_x = math.sin(self.time * 10) * 1.5
        self.shake_y = math.sin(self.time * 12) * 1.5
        self.glow = int(40 * (math.sin(self.time * 8) + 1))  # 0 -> 80

    def get_image(self):
        if self.health <= 0:
            blank = pygame.Surface((1, 1), pygame.SRCALPHA)
            return blank, pygame.Rect(-100, -100, 1, 1)
        # Tạo bản sao ảnh để thêm hiệu ứng glow
        img = self.image.copy()
        if self.glow > 10:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((self.glow, self.glow, self.glow, 100))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        # Dịch vị trí theo rung
        new_rect = self.rect.move(self.shake_x, self.shake_y)
        return img, new_rect


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
        self.player_id = player_id  # 1 for WASD/1-2-3, 2 for Arrow/1-2-3
        self.team = "blue" if player_id == 1 else "red"

        # Health and stamina
        self.health = 10000
        self.max_health = 10000
        self.stamina = 350
        self.max_stamina = 350
        self.stamina_regen_rate = 10  # per second
        self.kill_count = 0  # Kill count
        self.death_count = 0  # Death count
        self.last_damage_by_player = None
        self.last_damage_time = 0.0
        self.last_damage_dealt_time = 0.0  # Last time this player dealt damage
        self.last_damage_received_time = 0.0  # Last time this player received damage
        self.invulnerable = False
        self.hit_timer = 0.0
        self.hit_duration = 0.2
        self.damage = 10  # Damage per attack
        self.attack_range = 20  # Attack range (tighter center-to-center range)

        # Load frames
        self.run_right_frames = [load_surface(f"modelheros/run_right_{i}.png", scale_factor) for i in range(1, 9)]
        self.run_left_frames = [pygame.transform.flip(img, True, False) for img in self.run_right_frames]

        self.walk_right_frames = [load_surface(f"modelheros/walk_right_{i}.png", scale_factor) for i in range(1, 9)]
        self.walk_left_frames = [pygame.transform.flip(img, True, False) for img in self.walk_right_frames]

        idle_scale = scale_factor * 0.3  # Reduce idle sprite size further for better visual proportion
        self.idle_right = load_surface("modelheros/hero01_BenPhai.png", idle_scale, remove_bg=True)
        self.idle_left = load_surface("modelheros/hero01_BenTrai.png", idle_scale, remove_bg=True)

        # New combat frames
        self.combat1_right_frames = [
            load_surface("modelheros/combo_right.1.1.png", scale_factor),
            load_surface("modelheros/combo_right1.2.png", scale_factor),
            load_surface("modelheros/combo_right.1.3.png", scale_factor),
            load_surface("modelheros/combo_right.1.4.png", scale_factor)
        ]
        self.combat1_left_frames = [pygame.transform.flip(img, True, False) for img in self.combat1_right_frames]

        self.combat2_right_frames = [load_surface(f"modelheros/combo_right.2.{i}.png", scale_factor) for i in
                                     range(1, 5)]
        self.combat2_left_frames = [pygame.transform.flip(img, True, False) for img in self.combat2_right_frames]

        # Dash frames
        self.dash_right_frames = [load_surface(f"modelheros/dash_right_{i}.png", scale_factor) for i in range(1, 5)]
        self.dash_left_frames = [pygame.transform.flip(img, True, False) for img in self.dash_right_frames]

        # Guard frames
        self.guard_right_frames = [load_surface(f"modelheros/guard_right_{i}.png", scale_factor) for i in range(1, 3)]
        self.guard_left_frames = [pygame.transform.flip(img, True, False) for img in self.guard_right_frames]

        self.current_frames = self.run_right_frames
        self.rect = self.idle_right.get_rect(center=self.position)

        # New state variables
        self.combo_step = 0  # 0: none, 1: combat1, 2: combat2
        self.dash_timer = 0.0
        self.guard_active = False
        self.animation_timer = 0.0
        self.combat_active = False
        self.dash_active = False
        self.last_hit_target = None  # Track last hit target for single hit per combo
        self.last_hit_frame = -1  # Track last hit frame
        self.is_dead = False  # Track if player is dead
        self.respawn_timer = 0.0
        self.respawn_base = 3.0
        self.respawn_growth_interval = 10.0
        self.start_position = pygame.math.Vector2(x, y)

    def update(self, dt, keys=None, game_map=None, enemies=None):
        if keys is None:
            keys = pygame.key.get_pressed()

        # Stop all actions if dead
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

        # Get control keys based on player_id
        if self.player_id == 1:
            # Player 1: WASD for movement
            move_left = keys[pygame.K_a]
            move_right = keys[pygame.K_d]
            move_up = keys[pygame.K_w]
            move_down = keys[pygame.K_s]
        else:
            # Player 2: Arrow keys for movement
            move_left = keys[pygame.K_LEFT]
            move_right = keys[pygame.K_RIGHT]
            move_up = keys[pygame.K_UP]
            move_down = keys[pygame.K_DOWN]

        # Handle movement keys - only if not guarding
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

        # Get attack keys based on player_id
        if self.player_id == 1:
            # Player 1: j = attack1, k = guard, l = dash
            attack1 = keys[pygame.K_j]
            attack2 = keys[pygame.K_k]
            attack3 = keys[pygame.K_l]
        else:
            # Player 2: numpad 1 = attack1, numpad 2 = guard, numpad 3 = dash
            attack1 = keys[pygame.K_KP1]
            attack2 = keys[pygame.K_KP2]
            attack3 = keys[pygame.K_KP3]

        # Handle action keys
        if attack1 and not self.combat_active and not self.dash_active:
            if self.combo_step == 0:
                self.combo_step = 1
                self.state = 'combat1'
                self.frame_index = 0.0
                self.animation_timer = 0.0
                self.combat_active = True
            elif self.combo_step == 1 and self.animation_timer > 0.2:  # Allow combo after short time
                self.combo_step = 2
                self.state = 'combat2'
                self.frame_index = 0.0
                self.animation_timer = 0.0
                self.combat_active = True

        if attack3 and not self.combat_active and not self.dash_active and self.stamina >= 50:
            self.state = 'dash'
            self.dash_timer = 0.3  # Dash duration
            self.frame_index = 0.0
            self.animation_timer = 0.0
            self.dash_active = True
            self.stamina -= 50

        if attack2 and not self.combat_active and not self.dash_active:
            self.guard_active = True
            self.state = 'guard'
            self.frame_index = 0.0
            self.invulnerable = True  # Invulnerable while guarding
        else:
            self.guard_active = False
            self.invulnerable = False

        # Update animation timer
        self.animation_timer += dt

        # Stamina regen
        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen_rate * dt)

        # Health regeneration: 5 HP per second if no damage dealt/received in 5 seconds
        current_time = pygame.time.get_ticks() / 1000.0
        if (current_time - self.last_damage_dealt_time > 5.0 and
                current_time - self.last_damage_received_time > 5.0 and
                self.health < self.max_health):
            self.health = min(self.max_health, self.health + 5 * dt)

        # Handle dash movement - automatic in facing direction
        if self.dash_active:
            dash_speed = self.speed * 3
            if self.facing == 'right':
                dx += dash_speed * dt
            else:
                dx -= dash_speed * dt
            self.moving = True  # Consider dash as moving
            self.dash_timer -= dt
            if self.dash_timer <= 0:
                self.dash_active = False
                self.state = 'idle'

        # Handle combat animation end
        if self.combat_active:
            if self.frame_index >= len(self.current_frames) - 1:
                self.combat_active = False
                self.state = 'idle'
                self.last_hit_target = None  # Reset hit tracking
                if self.combo_step == 1:
                    self.combo_step = 0  # Reset after combat1
                elif self.combo_step == 2:
                    self.combo_step = 0  # Reset after combat2

        # Determine state if not in action
        if not self.combat_active and not self.dash_active:
            if self.guard_active:
                self.state = 'guard'
            elif self.moving:
                self.state = 'run'
            else:
                self.state = 'idle'

        new_x = self.position.x + dx
        new_y = self.position.y + dy

        can_move = True
        if game_map and not game_map.point_in_polygon(new_x, new_y):
            can_move = False
            # Allow the player to step a small distance outside the polygon to reach an enemy main tower
            for obj in game_map.animated_objects:
                if isinstance(obj, AnimatedMainTown) and obj.team != self.team:
                    town_center = pygame.math.Vector2(obj.rect.center)
                    if pygame.math.Vector2(new_x, new_y).distance_to(town_center) <= 5:
                        can_move = True
                        break

            # Allow access through specified main tower approach zones
            if not can_move:
                target_team = "blue" if self.team == "red" else "red"
                if game_map.point_in_main_town_access_zone(new_x, new_y, target_team):
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
                self.frame_index = len(self.current_frames) - 1  # Hold last frame
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
        # else: idle, no frames update

        # Update rect
        if self.state == 'idle':
            if self.facing == 'right':
                self.rect = self.idle_right.get_rect(center=self.position)
            else:
                self.rect = self.idle_left.get_rect(center=self.position)
        else:
            self.rect = self.current_frames[int(self.frame_index)].get_rect(center=self.position)
        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)

    def take_damage(self, damage, attacker=None):
        # Don't take damage if already dead
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
                self.health = 0  # Clamp health to 0
                self.is_dead = True
                self.respawn_timer = 0.0
                self.death_count += 1

                kill_assigned = False
                if isinstance(attacker, AnimatedCharacter) and attacker.team != self.team:
                    attacker.kill_count += 1
                    kill_assigned = True
                    print(
                        f"Player {attacker.player_id} killed Player {self.player_id}! Kill count: {attacker.kill_count}")
                elif self.last_damage_by_player and self.last_damage_by_player.team != self.team and current_time - self.last_damage_time <= 7.0:
                    self.last_damage_by_player.kill_count += 1
                    kill_assigned = True
                    print(
                        f"Player {self.last_damage_by_player.player_id} earned the kill on Player {self.player_id} via recent damage! Kill count: {self.last_damage_by_player.kill_count}")

                print(f"Player {self.player_id} died! Death count: {self.death_count}")

    def init_respawn_timer(self, game_time):
        if self.respawn_timer <= 0:
            self.respawn_timer = self.compute_respawn_time(game_time)
            print(f"Player {self.player_id} will respawn in {self.respawn_timer:.1f}s")

    def compute_respawn_time(self, game_time):
        # Respawn delay increases over match time
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

    def _is_in_attack_direction(self, other_pos):
        relative = other_pos - self.position
        if relative.length_squared() == 0:
            return True

        if relative.length_squared() <= 400:  # allow very close targets regardless of slight direction mismatch
            return True

        direction = pygame.math.Vector2(1, 0) if self.facing == 'right' else pygame.math.Vector2(-1, 0)
        return direction.dot(relative.normalize()) >= 0.1

    def _is_attack_frame(self):
        current_frame = int(self.frame_index)
        return self.current_frames and 1 <= current_frame <= 2

    def check_and_deal_damage(self, game_map=None):
        """Check if this character is attacking and dealing damage to any nearby valid target."""
        if not self.combat_active or self.is_dead or game_map is None:
            return

        if not self._is_attack_frame():
            self.last_hit_target = None
            return

        def phys_distance(target):
            if hasattr(target, 'position'):
                return self.position.distance_to(target.position)
            if hasattr(target, 'rect'):
                return self.position.distance_to(pygame.math.Vector2(target.rect.center))
            return float('inf')

        valid_targets = []
        for other in game_map.animated_objects:
            if other is self or getattr(other, 'team', None) == self.team or not hasattr(other, 'take_damage'):
                continue

            if isinstance(other, AnimatedMainTown):
                alive_towers = game_map.count_alive_towers(other.team)
                if alive_towers > 0:
                    continue

            distance = phys_distance(other)
            target_pos = other.position if hasattr(other, 'position') else pygame.math.Vector2(other.rect.center)
            if distance <= self.attack_range and self._is_in_attack_direction(target_pos):
                valid_targets.append((distance, other))

        for creep in game_map.creeps:
            if creep.team == self.team or creep.hp <= 0:
                continue
            distance = phys_distance(creep)
            creep_pos = creep.position if hasattr(creep, 'position') else pygame.math.Vector2(creep.rect.center)
            if distance <= self.attack_range and self._is_in_attack_direction(creep_pos):
                valid_targets.append((distance, creep))

        if not valid_targets:
            self.last_hit_target = None
            return

        valid_targets.sort(key=lambda item: item[0])
        target = valid_targets[0][1]
        current_frame = int(self.frame_index)
        if self.last_hit_target != target or current_frame != self.last_hit_frame:
            target.take_damage(self.damage, self)
            self.last_damage_dealt_time = pygame.time.get_ticks() / 1000.0
            self.last_hit_target = target
            self.last_hit_frame = current_frame

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

        return image, self.rect


class Creep:
    def __init__(self, x, y, team, target_pos, creep_type, image_path, scale_factor=1.0):
        self.position = pygame.math.Vector2(x, y)
        self.team = team
        self.creep_type = creep_type
        self.scale_factor = scale_factor
        self.target_pos = pygame.math.Vector2(target_pos)
        self.waypoints = [pygame.math.Vector2(target_pos)]
        self.current_waypoint = 0

        stats = {
            'orc_tanker': {'hp': 140, 'speed': 28, 'damage': 4, 'range': 8, 'color': (80, 80, 180)},
            'orc_warrior': {'hp': 100, 'speed': 36, 'damage': 5, 'range': 9, 'color': (120, 80, 180)},
            'slime': {'hp': 65, 'speed': 34, 'damage': 3, 'range': 7, 'color': (80, 200, 120)},
            'warrior': {'hp': 90, 'speed': 34, 'damage': 4, 'range': 9, 'color': (200, 100, 100)},
            'archer': {'hp': 55, 'speed': 32, 'damage': 3, 'range': 9, 'color': (200, 180, 80)},
            'mage': {'hp': 50, 'speed': 30, 'damage': 4, 'range': 10, 'color': (150, 100, 220)},
        }.get(creep_type, {'hp': 70, 'speed': 30, 'damage': 3, 'range': 8, 'color': (180, 180, 180)})

        self.hp = stats['hp']
        self.max_hp = stats['hp']
        self.speed = stats['speed'] * scale_factor
        self.damage = stats['damage']
        self.attack_range = max(8, int(stats['range'] * scale_factor * 0.45))
        self.tower_attack_range = max(4, self.attack_range // 2)
        self.attack_cooldown = 1.5
        self.last_attack_time = 0.0
        self.hit_timer = 0.0
        self.hit_duration = 0.2
        self.attack_timer = 0.0
        self.attack_duration = 0.25

        try:
            self.original_image = pygame.image.load(image_path).convert_alpha()
            if scale_factor != 1.0:
                new_size = (int(self.original_image.get_width() * scale_factor),
                            int(self.original_image.get_height() * scale_factor))
                self.image = pygame.transform.scale(self.original_image, new_size)
            else:
                self.image = self.original_image
        except Exception:
            self.image = pygame.Surface((int(24 * scale_factor), int(24 * scale_factor)), pygame.SRCALPHA)
            self.image.fill(stats['color'])

        self.rect = self.image.get_rect(center=self.position)

    def _distance_to_object(self, target):
        if hasattr(target, 'position'):
            return self.position.distance_to(target.position)
        if hasattr(target, 'rect'):
            return self.position.distance_to(pygame.math.Vector2(target.rect.center))
        return float('inf')

    def update(self, dt, enemies=None, towers=None, game_map=None, enemy_characters=None):
        if self.hp <= 0:
            return

        current_time = pygame.time.get_ticks() / 1000.0

        targets = []

        if enemies:
            for enemy in enemies:
                if enemy.team == self.team or enemy.hp <= 0:
                    continue
                targets.append(enemy)

        if enemy_characters:
            for character in enemy_characters:
                if character.team == self.team or character.is_dead:
                    continue
                targets.append(character)

        if towers:
            for tower in towers:
                if tower.team == self.team or tower.health <= 0:
                    continue
                targets.append(tower)

        closest_unit = None
        closest_unit_distance = float('inf')
        closest_tower = None
        closest_tower_distance = float('inf')
        alive_enemy_units = False

        if enemies:
            for enemy in enemies:
                if enemy.team == self.team or enemy.hp <= 0:
                    continue
                alive_enemy_units = True
                distance = self._distance_to_object(enemy)
                if distance < closest_unit_distance:
                    closest_unit_distance = distance
                    closest_unit = enemy

        if enemy_characters:
            for character in enemy_characters:
                if character.team == self.team or character.is_dead:
                    continue
                alive_enemy_units = True
                distance = self._distance_to_object(character)
                if distance < closest_unit_distance:
                    closest_unit_distance = distance
                    closest_unit = character

        if towers:
            for tower in towers:
                if tower.team == self.team or tower.health <= 0:
                    continue
                distance = self._distance_to_object(tower)
                if distance < closest_tower_distance:
                    closest_tower_distance = distance
                    closest_tower = tower

        if closest_unit is not None and closest_unit_distance <= max(self.attack_range, 5):
            self.attack(closest_unit, current_time)
            return

        if not alive_enemy_units and closest_tower is not None and closest_tower_distance <= self.tower_attack_range:
            self.attack(closest_tower, current_time)
            return

        if closest_tower is not None and closest_tower_distance <= self.tower_attack_range and closest_unit is None:
            self.attack(closest_tower, current_time)
            return

        if self.waypoints and self.current_waypoint < len(self.waypoints):
            current_target = self.waypoints[self.current_waypoint]
            direction = current_target - self.position
            if direction.length() <= 4:
                self.current_waypoint += 1
                if self.current_waypoint < len(self.waypoints):
                    current_target = self.waypoints[self.current_waypoint]
                else:
                    current_target = self.target_pos
                direction = current_target - self.position
        else:
            current_target = self.target_pos
            direction = current_target - self.position

        if direction.length() > 0.5:
            direction = direction.normalize()
            self.position += direction * self.speed * dt
            self.rect.center = self.position

        if game_map is not None:
            self.position.x = max(0, min(self.position.x, game_map.map_width))
            self.position.y = max(0, min(self.position.y, game_map.map_height))
            self.rect.center = self.position

        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)
        if self.attack_timer > 0:
            self.attack_timer = max(0.0, self.attack_timer - dt)

    def attack(self, target, current_time):
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        if getattr(target, 'hp', None) is not None and target.hp <= 0:
            return
        if getattr(target, 'health', None) is not None and target.health <= 0:
            return

        target.take_damage(self.damage, self)
        self.last_attack_time = current_time
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
        if self.hit_timer > 0:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 90))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        return img, self.rect


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
        # Xoay qua lại nhẹ
        self.angle = math.sin(self.time) * 3

    def get_image(self):
        rotated = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        return rotated, new_rect

    def update(self, dt):
        self.time += dt * 4
        # Xoay qua lại nhẹ
        self.angle = math.sin(self.time) * 3

    def get_image(self):
        rotated = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated.get_rect(center=self.rect.center)
        return rotated, new_rect


class AnimatedWater:
    def __init__(self, x, y, w, h, scale_factor=1.0, image_path="assets/images/water.png"):
        self.rect = pygame.Rect(x, y, w, h)
        self.time = 0
        self.w = w
        self.h = h

        # Load ảnh nền nước nếu có, nếu không thì tạo surface xanh
        try:
            self.background = pygame.image.load(image_path).convert_alpha()
            self.background = pygame.transform.scale(self.background, (w, h))
        except:
            self.background = pygame.Surface((w, h))
            self.background.fill((0, 150, 200))  # xanh biển nhạt

        # Tạo một surface tạm để vẽ sóng
        self.wave_surface = pygame.Surface((w, h), pygame.SRCALPHA)

        # Tham số sóng
        self.wave_amplitude = 4  # độ cao sóng (pixel)
        self.wave_length = 30  # khoảng cách giữa các đỉnh sóng
        self.wave_speed = 3.0  # tốc độ di chuyển

    def update(self, dt):
        self.time += dt * self.wave_speed

    def draw(self, surface):
        # Xóa surface vẽ sóng
        self.wave_surface.fill((0, 0, 0, 0))

        # Vẽ các đường sóng ngang
        for y in range(0, self.h, 8):  # vẽ mỗi 8 pixel một đường sóng
            # Tính độ dịch pha theo chiều ngang
            phase = self.time
            # Vẽ đường cong sin mờ
            points = []
            for x in range(0, self.w, 4):
                # Sóng chính
                offset_y = self.wave_amplitude * math.sin(x / self.wave_length + phase)
                # Thêm sóng phụ (tần số cao hơn) để rối hơn
                offset_y += 2 * math.sin(x / 12 - phase * 2.5)
                points.append((x, y + offset_y))
            # Vẽ đường mờ trắng/xanh
            if len(points) > 1:
                pygame.draw.lines(self.wave_surface, (255, 255, 255, 60), False, points, 1)

        # Vẽ thêm các "đợt sóng" sáng hơn chạy dọc
        for offset in range(0, self.w, 60):
            x = (self.time * 50 + offset) % (self.w + 100) - 50
            highlight_surf = pygame.Surface((80, self.h), pygame.SRCALPHA)
            for i in range(self.h):
                alpha = 40 - abs(i - self.h / 2) * 0.5
                if alpha > 0:
                    pygame.draw.line(highlight_surf, (255, 255, 255, alpha), (0, i), (80, i), 1)
            self.wave_surface.blit(highlight_surf, (x, 0), special_flags=pygame.BLEND_ALPHA_SDL2)

        # Kết hợp nền nước + hiệu ứng sóng
        surface.blit(self.background, (0, 0))
        surface.blit(self.wave_surface, (0, 0))

