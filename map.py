import pygame
from animated_objects import AnimatedTower, AnimatedGrass, AnimatedMainTown, AnimatedCharacter, Creep


class GameMap:
    def __init__(self, screen, scale_factor=1.0):
        self.screen = screen
        self.scale_factor = scale_factor

        self.original_background = pygame.image.load("map.png").convert()
        self.original_width, self.original_height = self.original_background.get_size()

        # Scale background
        if self.scale_factor != 1.0:
            new_size = (int(self.original_width * self.scale_factor),
                        int(self.original_height * self.scale_factor))
            self.background = pygame.transform.scale(self.original_background, new_size).convert()
        else:
            self.background = self.original_background

        self.map_width, self.map_height = self.background.get_size()
        print(f"Map size after scale: {self.map_width} x {self.map_height} (scale={self.scale_factor})")

        self.animated_objects = []
        self.bullets = []
        self.creeps = []
        self.wave_timer = 0.0
        self.wave_interval = 10.0
        self.spawn_check_distance = 100
        self.spawn_blocked = {'blue': False, 'red': False}
        self.spawn_scaled = {}
        self.target_scaled = {}

        self.game_time = 0.0  # Total match time in seconds
        self.main_towns = {}  # Store main town positions
        self.game_over = False
        self.winner = None

        # ----- NHÀ CHÍNH (main town) -----
        main_town_positions_original = [
            (5, 230, "blue"),  # tạm giữ, nhưng hãy click để lấy lại
            (972, 246, "red")
        ]
        main_town_scale = self.scale_factor * 0.6  # giảm từ 0.3 xuống 0.25 (nhỏ hơn)
        for x, y, team in main_town_positions_original:
            sx = int(x * self.scale_factor)
            sy = int(y * self.scale_factor)
            path = f"assets/images/main-town-{team}.png"
            try:
                obj = AnimatedMainTown(sx, sy, path, team, main_town_scale)
                self.animated_objects.append(obj)
                self.main_towns[team] = pygame.math.Vector2(obj.rect.center)
                print(f"Main town {team} at ({obj.rect.centerx}, {obj.rect.centery})")
            except Exception as e:
                print(f"Lỗi main town {team}: {e}")

        center_x = self.map_width // 2
        center_y = self.map_height // 2 + 10
        # Spawn positions near each main town so creeps originate from their base
        blue_spawn_offset = int(80 * self.scale_factor)
        red_spawn_offset = int(80 * self.scale_factor)
        blue_spawn = (int(self.main_towns['blue'].x + blue_spawn_offset), int(self.main_towns['blue'].y))
        red_spawn = (int(self.main_towns['red'].x - red_spawn_offset), int(self.main_towns['red'].y))
        self.spawn_scaled = {
            'blue': blue_spawn,
            'red': red_spawn,
        }
        self.map_center = (center_x, center_y)
        self.target_scaled = {
            'blue': (int(self.main_towns['red'].x), int(self.main_towns['red'].y)),
            'red': (int(self.main_towns['blue'].x), int(self.main_towns['blue'].y)),
        }

        # ----- BỤI CỎ (tọa độ gốc) -----
        grass_positions_original = [
            (320, 135), (300, 135), (320, 212), (300, 212),
        ]
        grass_scale = self.scale_factor * 0.4
        for x, y in grass_positions_original:
            sx = int(x * self.scale_factor)
            sy = int(y * self.scale_factor)
            self.animated_objects.append(AnimatedGrass(sx, sy, "assets/images/grass.png", grass_scale))

        # ----- THÁP (tọa độ gốc) -----
        tower_positions_original = [
            (384, 290, "blue"), (565, 290, "blue"),
            (766, 290, "red"), (953, 290, "red")
        ]
        tower_scale = self.scale_factor * 0.45  # giảm từ 0.15 xuống 0.12 (nhỏ hơn)
        for idx, (x, y, team) in enumerate(tower_positions_original):
            sx = int(x * self.scale_factor)
            sy = int(y * self.scale_factor)
            path = f"assets/images/tower_{team}.png"
            try:
                obj = AnimatedTower(sx, sy, path, team, tower_scale)
                self.animated_objects.append(obj)
                print(f"Tower {idx + 1}: {team} at ({sx},{sy})")
            except FileNotFoundError:
                print(f"Không tìm thấy ảnh: {path}")
            except Exception as e:
                print(f"Lỗi khác: {e}")

        # ----- NHÂN VẬT BÊN TRONG VÙNG DI CHUYỂN (POLYGON XANH) -----
        # Player 1
        hero_original_x = 171
        hero_original_y = 499
        hero_scale = self.scale_factor * 0.4  # reduce character size
        hero_x = int(hero_original_x * self.scale_factor)
        hero_y = int(hero_original_y * self.scale_factor)
        try:
            self.animated_objects.append(AnimatedCharacter(hero_x, hero_y, hero_scale, player_id=1))
            print(f"Added player 1 at ({hero_x},{hero_y})")
        except Exception as e:
            print(f"Không thể tạo nhân vật 1: {e}")

        # Player 2
        hero2_original_x = 1000
        hero2_original_y = 499
        hero2_x = int(hero2_original_x * self.scale_factor)
        hero2_y = int(hero2_original_y * self.scale_factor)
        try:
            self.animated_objects.append(AnimatedCharacter(hero2_x, hero2_y, hero_scale, player_id=2))
            print(f"Added player 2 at ({hero2_x},{hero2_y})")
        except Exception as e:
            print(f"Không thể tạo nhân vật 2: {e}")

        # ----- VÙNG DI CHUYỂN -----
        polygon_original = [
            (504, 762), (352, 761), (352, 653), (169, 501), (222, 436), (218, 433),
            (324, 367), (324, 370), (225, 292), (425, 168), (432, 136), (336, 47),
            (339, 1), (500, 1), (503, 280), (905, 284), (907, 2), (1070, 2),
            (1071, 61), (1025, 97), (1024, 150), (1013, 166), (1008, 185),
            (1056, 225), (1071, 235), (1071, 250), (1103, 263), (1144, 293),
            (1075, 373), (1074, 391), (1164, 433), (1132, 449), (1138, 470),
            (1103, 442), (1039, 475), (1043, 756), (921, 756), (920, 493),
            (505, 486), (501, 754),
        ]
        self.polygon = [(int(x * self.scale_factor), int(y * self.scale_factor)) for x, y in polygon_original]

        # Main tower access regions (original map coordinates)
        self.main_town_attack_zones_original = {
            "blue": [(315, 369), (233, 426), (257, 324)],
            "red": [(1178, 448), (1071, 384), (1147, 341)]
        }
        self.main_town_attack_zones = {
            team: [(int(x * self.scale_factor), int(y * self.scale_factor)) for x, y in points]
            for team, points in self.main_town_attack_zones_original.items()
        }

    def point_in_polygon(self, x, y):
        inside = False
        polygon = self.polygon
        n = len(polygon)

        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]

            if ((y1 > y) != (y2 > y)):
                xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 0.00001) + x1
                if x < xinters:
                    inside = not inside

        return inside

    def point_in_custom_polygon(self, x, y, polygon):
        inside = False
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if ((y1 > y) != (y2 > y)):
                xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 0.00001) + x1
                if x < xinters:
                    inside = not inside
        return inside

    def point_in_main_town_access_zone(self, x, y, target_team):
        zone = self.main_town_attack_zones.get(target_team)
        if not zone:
            return False
        return self.point_in_custom_polygon(x, y, zone)

    def get_team_towers(self, team):
        return [t for t in self.animated_objects if isinstance(t, AnimatedTower) and t.team == team]

    def count_alive_towers(self, team):
        return len([t for t in self.get_team_towers(team) if t.health > 0])

    def update(self, dt, keys=None):
        self.game_time += dt

        # Update spawn state before other updates so newly spawned creeps
        # can be targeted in the same frame they appear.
        for team in ['blue', 'red']:
            spawn_pt = self.spawn_scaled[team]
            blocked = False
            for creep in self.creeps:
                if creep.team == team:
                    dx = creep.position.x - spawn_pt[0]
                    dy = creep.position.y - spawn_pt[1]
                    if dx * dx + dy * dy < self.spawn_check_distance ** 2:
                        blocked = True
                        break
            self.spawn_blocked[team] = blocked

        self.wave_timer += dt
        if self.wave_timer >= self.wave_interval:
            self.wave_timer -= self.wave_interval
            if not self.spawn_blocked['blue']:
                self.spawn_wave('blue')
            if not self.spawn_blocked['red']:
                self.spawn_wave('red')

        characters = [obj for obj in self.animated_objects if isinstance(obj, AnimatedCharacter)]
        towers = [obj for obj in self.animated_objects if isinstance(obj, AnimatedTower)]
        main_towns = [obj for obj in self.animated_objects if isinstance(obj, AnimatedMainTown)]

        for obj in self.animated_objects:
            if isinstance(obj, AnimatedCharacter):
                obj.update(dt, keys, self)
                obj.check_and_deal_damage(self)
            elif isinstance(obj, AnimatedTower):
                obj.update(dt)
                enemy_targets = [c for c in self.creeps if c.team != obj.team and c.hp > 0] + [p for p in characters if
                                                                                               p.team != obj.team]
                obj.attack_targets(enemy_targets, self.game_time, self.bullets)
                if obj.health <= 0:
                    self.animated_objects.remove(obj)
                    print(f"Removed destroyed tower {obj.team}")
            elif isinstance(obj, AnimatedMainTown):
                obj.update(dt)
                # Main town attacks
                obj.attack_targets(characters, self.game_time)
                if obj.health <= 0:
                    self.animated_objects.remove(obj)
                    print(f"Removed destroyed main town {obj.team}")
                    # Game over condition
                    if obj.team == "blue":
                        self.game_over = True
                        self.winner = "red"
                    else:
                        self.game_over = True
                        self.winner = "blue"
            else:
                obj.update(dt)

        # Update creeps and bullets separately; keep existing hero/main-town logic unchanged.
        blue_creeps = [c for c in self.creeps if c.team == 'blue' and c.hp > 0]
        red_creeps = [c for c in self.creeps if c.team == 'red' and c.hp > 0]
        blue_characters = [p for p in characters if p.team == 'blue' and not p.is_dead]
        red_characters = [p for p in characters if p.team == 'red' and not p.is_dead]
        for creep in self.creeps:
            if creep.hp <= 0:
                continue
            enemies = red_creeps if creep.team == 'blue' else blue_creeps
            enemy_chars = red_characters if creep.team == 'blue' else blue_characters
            creep.update(dt, enemies, towers, self, enemy_chars)

        for bullet in self.bullets[:]:
            bullet.update(dt)
            if not bullet.active:
                self.bullets.remove(bullet)

        self.creeps = [c for c in self.creeps if c.hp > 0]

        for team in ['blue', 'red']:
            spawn_pt = self.spawn_scaled[team]
            blocked = False
            for creep in self.creeps:
                if creep.team == team:
                    dx = creep.position.x - spawn_pt[0]
                    dy = creep.position.y - spawn_pt[1]
                    if dx * dx + dy * dy < self.spawn_check_distance ** 2:
                        blocked = True
                        break
            self.spawn_blocked[team] = blocked

    def get_character_position(self):
        for obj in self.animated_objects:
            if isinstance(obj, AnimatedCharacter):
                return obj.position
        return None

    def draw_tower_attack_warnings(self):
        towers = [obj for obj in self.animated_objects if isinstance(obj, AnimatedTower)]
        players = [obj for obj in self.animated_objects if isinstance(obj, AnimatedCharacter)]
        for tower in towers:
            tower_img, tower_rect = tower.get_image()
            target = None

            # Prefer current locked target if still valid and in range
            if hasattr(tower, 'current_target') and tower.current_target is not None:
                current = tower.current_target
                valid = False
                if isinstance(current, Creep):
                    valid = current.team != tower.team and current.hp > 0
                elif isinstance(current, AnimatedCharacter):
                    valid = current.team != tower.team and current.health > 0
                if valid:
                    curr_pos = current.position if hasattr(current, 'position') else pygame.math.Vector2(
                        current.rect.center)
                    if pygame.math.Vector2(tower_rect.center).distance_to(curr_pos) <= tower.attack_range:
                        target = current
                    else:
                        tower.current_target = None

            # If no locked target, choose closest in-range enemy (creep first)
            if target is None:
                closest_distance = float('inf')
                for creep in self.creeps:
                    if creep.team != tower.team and creep.hp > 0:
                        distance = pygame.math.Vector2(tower_rect.center).distance_to(creep.position)
                        if distance <= tower.attack_range and distance < closest_distance:
                            target = creep
                            closest_distance = distance
                if target is None:
                    for player in players:
                        if player.team != tower.team and player.health > 0:
                            distance = pygame.math.Vector2(tower_rect.center).distance_to(player.position)
                            if distance <= tower.attack_range and distance < closest_distance:
                                target = player
                                closest_distance = distance

            if target is not None:
                pygame.draw.circle(self.screen, (255, 200, 0), tower_rect.center, tower.attack_range, 3)
                target_pos = target.position if hasattr(target, 'position') else pygame.math.Vector2(target.rect.center)
                pygame.draw.line(self.screen, (255, 180, 0), tower_rect.center, (int(target_pos.x), int(target_pos.y)),
                                 2)
                pygame.draw.circle(self.screen, (255, 180, 0), (int(target_pos.x), int(target_pos.y)), 10, 2)
                if hasattr(tower, 'current_target') and tower.current_target is target:
                    pygame.draw.circle(self.screen, (255, 255, 0), (int(target_pos.x), int(target_pos.y)), 14, 2)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for obj in self.animated_objects:
            img, rect = obj.get_image()
            self.screen.blit(img, rect)
        self.draw_tower_attack_warnings()
        self.draw_player_labels()
        self.draw_health_bar()
        self.draw_object_health_bars()
        self.draw_respawn_timers()
        self.draw_match_timer()

        # Draw creeps and bullets
        for creep in self.creeps:
            img, rect = creep.get_image()
            self.screen.blit(img, rect)
            creep.draw_health_bar(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)

        if self.game_over:
            self.draw_game_over_screen()
        # pygame.draw.polygon(self.screen, (0,255,0), self.polygon, 2)  # ẩn đường polygon xanh

    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        font_large = pygame.font.SysFont(None, 80)
        font_small = pygame.font.SysFont(None, 40)

        winner_text = f"PLAYER {1 if self.winner == 'blue' else 2} WINS!"
        winner_surface = font_large.render(winner_text, True, (255, 215, 0))
        winner_rect = winner_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        self.screen.blit(winner_surface, winner_rect)

        restart_text = "Game will restart in 3 seconds..."
        restart_surface = font_small.render(restart_text, True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(restart_surface, restart_rect)

    def draw_health_bar(self):
        characters = self.get_characters()
        if not characters:
            return

        bar_width = 200
        bar_height = 18
        border_color = (255, 255, 255)
        hp_bg_color = (50, 0, 0)
        hp_color = (200, 20, 20)
        stamina_bg_color = (40, 20, 0)
        stamina_color = (240, 180, 40)

        # Draw Player 1 (top-left)
        if len(characters) > 0:
            player = characters[0]
            x, y = 20, 20
            pygame.draw.rect(self.screen, border_color, (x - 2, y - 2, bar_width + 4, bar_height + 4), border_radius=8)
            pygame.draw.rect(self.screen, hp_bg_color, (x, y, bar_width, bar_height), border_radius=8)
            hp_ratio = max(0, player.health) / max(1, player.max_health)
            fill_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y, fill_width, bar_height), border_radius=8)

            stamina_y = y + bar_height + 10
            pygame.draw.rect(self.screen, border_color, (x - 2, stamina_y - 2, bar_width + 4, bar_height + 4),
                             border_radius=8)
            pygame.draw.rect(self.screen, stamina_bg_color, (x, stamina_y, bar_width, bar_height), border_radius=8)
            stamina_ratio = max(0, player.stamina) / max(1, player.max_stamina)
            stamina_width = int(bar_width * stamina_ratio)
            pygame.draw.rect(self.screen, stamina_color, (x, stamina_y, stamina_width, bar_height), border_radius=8)

            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"P1 HP: {player.health}/{player.max_health} Kills: {player.kill_count}", True,
                                  (255, 255, 255))
            self.screen.blit(hp_text, (x + 8, y - 2))
            st_text = font.render(f"STAMINA: {int(player.stamina)}/{player.max_stamina}", True, (255, 255, 255))
            self.screen.blit(st_text, (x + 8, stamina_y - 2))
            kd_text = font.render(f"KILLS: {player.kill_count}  DEATHS: {player.death_count}", True, (255, 255, 255))
            self.screen.blit(kd_text, (x + 8, stamina_y + 16))

        # Draw Player 2 (top-right)
        if len(characters) > 1:
            player = characters[1]
            x, y = self.screen.get_width() - bar_width - 20, 20
            pygame.draw.rect(self.screen, border_color, (x - 2, y - 2, bar_width + 4, bar_height + 4), border_radius=8)
            pygame.draw.rect(self.screen, hp_bg_color, (x, y, bar_width, bar_height), border_radius=8)
            hp_ratio = max(0, player.health) / max(1, player.max_health)
            fill_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y, fill_width, bar_height), border_radius=8)

            stamina_y = y + bar_height + 10
            pygame.draw.rect(self.screen, border_color, (x - 2, stamina_y - 2, bar_width + 4, bar_height + 4),
                             border_radius=8)
            pygame.draw.rect(self.screen, stamina_bg_color, (x, stamina_y, bar_width, bar_height), border_radius=8)
            stamina_ratio = max(0, player.stamina) / max(1, player.max_stamina)
            stamina_width = int(bar_width * stamina_ratio)
            pygame.draw.rect(self.screen, stamina_color, (x, stamina_y, stamina_width, bar_height), border_radius=8)

            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"P2 HP: {player.health}/{player.max_health} Kills: {player.kill_count}", True,
                                  (255, 255, 255))
            self.screen.blit(hp_text, (x + 8, y - 2))
            st_text = font.render(f"STAMINA: {int(player.stamina)}/{player.max_stamina}", True, (255, 255, 255))
            self.screen.blit(st_text, (x + 8, stamina_y - 2))
            kd_text = font.render(f"KILLS: {player.kill_count}  DEATHS: {player.death_count}", True, (255, 255, 255))
            self.screen.blit(kd_text, (x + 8, stamina_y + 16))

    def draw_object_health_bars(self):
        font = pygame.font.SysFont(None, 16)
        bar_width = 40
        bar_height = 6
        hp_bg_color = (50, 0, 0)
        hp_color = (200, 20, 20)

        # Draw main town health bars
        main_towns = [obj for obj in self.animated_objects if isinstance(obj, AnimatedMainTown) and obj.health > 0]
        for main_town in main_towns:
            x = main_town.rect.centerx - bar_width // 2
            y = main_town.rect.top - 20
            pygame.draw.rect(self.screen, hp_bg_color, (x, y, bar_width, bar_height))
            hp_ratio = max(0, main_town.health) / max(1, main_town.max_health)
            fill_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y, fill_width, bar_height))
            hp_text = font.render(f"{main_town.health}", True, (255, 255, 255))
            self.screen.blit(hp_text, (x + bar_width // 2 - 8, y - 12))

        # Draw tower health bars
        towers = [obj for obj in self.animated_objects if isinstance(obj, AnimatedTower) and obj.health > 0]
        for tower in towers:
            x = tower.rect.centerx - bar_width // 2
            y = tower.rect.top - 15
            pygame.draw.rect(self.screen, hp_bg_color, (x, y, bar_width, bar_height))
            hp_ratio = max(0, tower.health) / max(1, tower.max_health)
            fill_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y, fill_width, bar_height))
            hp_text = font.render(f"{tower.health}", True, (255, 255, 255))
            self.screen.blit(hp_text, (x + bar_width // 2 - 8, y - 12))

    def get_characters(self):
        """Get all player character objects"""
        return [obj for obj in self.animated_objects if isinstance(obj, AnimatedCharacter) and obj.player_id in [1, 2]]

    def draw_respawn_timers(self):
        characters = self.get_characters()
        font = pygame.font.SysFont(None, 20)
        for idx, player in enumerate(characters, start=1):
            if player.is_dead:
                x = 20 if idx == 1 else self.screen.get_width() - 220
                y = 80
                text = f"P{player.player_id} respawn: {max(0, player.respawn_timer):.1f}s"
                label = font.render(text, True, (255, 255, 0))
                self.screen.blit(label, (x, y))

    def draw_player_labels(self):
        characters = [obj for obj in self.animated_objects if isinstance(obj, AnimatedCharacter)]
        font = pygame.font.SysFont(None, 20)
        for player in characters:
            if player.player_id in [1, 2]:
                label_text = f"P{player.player_id}"
            else:
                continue
            label = font.render(label_text, True, (255, 255, 255))
            label_rect = label.get_rect(center=(player.position.x, player.position.y - 30))
            self.screen.blit(label, label_rect)

    def draw_match_timer(self):
        font = pygame.font.SysFont(None, 20)
        mins = int(self.game_time) // 60
        secs = int(self.game_time) % 60
        text = f"Match time: {mins:02d}:{secs:02d}"
        label = font.render(text, True, (255, 255, 255))
        self.screen.blit(label, (self.screen.get_width() // 2 - 60, 20))

    def get_character(self):
        """Get first character (for backward compatibility)"""
        for obj in self.animated_objects:
            if isinstance(obj, AnimatedCharacter):
                return obj
        return None

    def handle_click(self, pos):
        original_x = int(pos[0] / self.scale_factor)
        original_y = int(pos[1] / self.scale_factor)
        print(f"🖱️ Click tại screen: {pos} -> ảnh gốc: ({original_x}, {original_y})")

    def spawn_wave(self, team):
        # Spawn creeps in the middle of the map
        spawn_base = self.spawn_scaled[team]
        target_pos = self.target_scaled[team]

        if team == 'blue':
            creep_order = [
                ('orc_tanker', 'orc-tanker.png'),
                ('orc_warrior', 'orc-warrior.png'),
                ('orc_warrior', 'orc-warrior.png'),
                ('slime', 'slime.png'),
            ]
        else:
            creep_order = [
                ('warrior', 'warrior.png'),
                ('warrior', 'warrior.png'),
                ('archer', 'archer.png'),
                ('mage', 'mage.png'),
            ]

        spacing = 25
        direction = 1 if target_pos[0] > spawn_base[0] else -1

        for idx, (creep_type, img_file) in enumerate(creep_order):
            img_path = f"assets/images/{img_file}"
            if direction == 1:
                offset_x = (len(creep_order) - 1 - idx) * spacing
            else:
                offset_x = -((len(creep_order) - 1 - idx) * spacing)
            if creep_type in ['slime', 'archer']:
                offset_x += -15 * direction
            if creep_type in ['mage']:
                offset_x += -25 * direction
            spawn_x = spawn_base[0] + offset_x
            spawn_y = spawn_base[1] + (idx % 2) * 6
            creep = Creep(spawn_x, spawn_y, team, target_pos, creep_type, img_path, self.scale_factor)
            creep.waypoints = [pygame.math.Vector2(self.map_center), pygame.math.Vector2(target_pos)]
            print(f"Spawn {creep_type} at ({spawn_x}, {spawn_y}), team={team}")
            self.creeps.append(creep)
        print(f"Đợt lính {team} spawn theo hàng dọc, ranged ở cuối")
