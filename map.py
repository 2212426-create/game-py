import pygame
from bullet import Bullet
from animated_objects import AnimatedTower, AnimatedGrass, AnimatedMainTown, Creep, AnimatedCharacter

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
            self.game_time = 0.0
            self.game_over = False
            self.winner = None
            self.main_towns = {}  # lưu tọa độ nhà chính

            # ----- NHÀ CHÍNH (main town) -----
            main_town_positions_original = [
                (5, 230, "blue"),
                (972, 246, "red")
            ]
            main_town_scale = self.scale_factor * 0.6
            for x, y, team in main_town_positions_original:
                sx = int(x * self.scale_factor)
                sy = int(y * self.scale_factor)
                path = f"assets/images/main-town-{team}.png"
                try:
                    obj = AnimatedMainTown(sx, sy, path, team, main_town_scale)
                    self.animated_objects.append(obj)
                    print(f"Main town {team} at ({sx}, {sy})")
                except Exception as e:
                    print(f"Lỗi main town {team}: {e}")

            # ----- BỤI CỎ -----
            grass_positions_original = [
                (320, 135), (300, 135), (320, 212), (300, 212),
            ]
            grass_scale = self.scale_factor * 0.4
            for x, y in grass_positions_original:
                sx = int(x * self.scale_factor)
                sy = int(y * self.scale_factor)
                self.animated_objects.append(AnimatedGrass(sx, sy, "assets/images/grass.png", grass_scale))

            # ----- THÁP -----
            tower_positions_original = [
                (384, 290, "blue"), (565, 290, "blue"),
                (766, 290, "red"), (953, 290, "red")
            ]
            tower_scale = self.scale_factor * 0.45
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

            # ----- NHÂN VẬT (AnimatedCharacter) từ Trug-Kin -----
            hero_original_x = 171
            hero_original_y = 499
            hero_scale = self.scale_factor * 0.3
            hero_x = int(hero_original_x * self.scale_factor)
            hero_y = int(hero_original_y * self.scale_factor)
            try:
                self.animated_objects.append(AnimatedCharacter(hero_x, hero_y, hero_scale,player_id=1))
                print(f"Added animated character at ({hero_x},{hero_y})")
            except Exception as e:
                print(f"Không thể tạo nhân vật: {e}")

            # ----- VÙNG DI CHUYỂN (POLYGON) từ Trug-Kin -----
            polygon_original = [
                (504, 762),(352, 761),(352, 653),(169, 501),(222, 436),(218, 433),
                (324, 367),(324, 370),(225, 292),(425, 168),(432, 136),(336, 47),
                (339, 1),(500, 1),(503, 280),(905, 284),(907, 2),(1070, 2),
                (1071, 61),(1025, 97),(1024, 150),(1013, 166),(1008, 185),
                (1056, 225),(1071, 235),(1071, 250),(1103, 263),(1144, 293),
                (1075, 373),(1074, 391),(1164, 433),(1132, 449),(1138, 470),
                (1103, 442),(1039, 475),(1043, 756),(921, 756),(920, 493),
                (505, 486),(501, 754)
            ]
            self.polygon = [(int(x * self.scale_factor), int(y * self.scale_factor)) for x, y in polygon_original]

            # ----- LÍNH (CREEP) -----
            self.creeps = []
            self.wave_timer = 0
            self.wave_interval = 10.0
            self.creeps_per_wave = 4
            self.spawn_check_distance = 100
            self.spawn_blocked = {'blue': False, 'red': False}

            self.spawn_points = {
                'blue': (87, 204),
                'red': (945, 210)
            }
            self.target_points = {
                'blue': (810, 280),
                'red': (120, 280)
            }

            self.spawn_scaled = {}
            self.target_scaled = {}
            for team, (x, y) in self.spawn_points.items():
                self.spawn_scaled[team] = (int(x * self.scale_factor), int(y * self.scale_factor))
            for team, (x, y) in self.target_points.items():
                self.target_scaled[team] = (int(x * self.scale_factor), int(y * self.scale_factor))

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

        def update(self, dt, keys=None):
            self.game_time += dt
            characters = [obj for obj in self.animated_objects if isinstance(obj, AnimatedCharacter)]
            towers = [obj for obj in self.animated_objects if isinstance(obj, AnimatedTower)]
            main_towns = [obj for obj in self.animated_objects if isinstance(obj, AnimatedMainTown)]
            current_time = pygame.time.get_ticks() / 1000.0

            # Cập nhật animated_objects
            for obj in self.animated_objects:
                if isinstance(obj, AnimatedCharacter):
                    obj.update(dt, keys, self)
                elif isinstance(obj, AnimatedTower):
                    obj.update(dt, self.creeps)  # giữ nguyên nếu có tham số
                    # Tháp tấn công
                    obj.attack_targets([c for c in self.creeps if c.hp > 0] + characters, current_time, self.bullets)
                elif isinstance(obj, AnimatedMainTown):
                    obj.update(dt)
                    obj.attack_targets(characters, current_time)
                    if obj.health <= 0:
                        self.game_over = True
                        self.winner = "red" if obj.team == "blue" else "blue"
                else:
                    obj.update(dt)
            # Cập nhật lính
            blue_creeps = [c for c in self.creeps if c.team == 'blue']
            red_creeps = [c for c in self.creeps if c.team == 'red']
            for creep in self.creeps:
                enemies = red_creeps if creep.team == 'blue' else blue_creeps
                creep.update(dt, enemies, towers)  # thêm tham số towers
            # Cập nhật đạn
            for bullet in self.bullets[:]:
                bullet.update(dt)
                if not bullet.active:
                    self.bullets.remove(bullet)
            # Xóa lính chết
            self.creeps = [c for c in self.creeps if c.hp > 0]
            # Xóa tháp chết
            self.animated_objects = [obj for obj in self.animated_objects if not (isinstance(obj, AnimatedTower) and obj.hp <= 0)]
            # Xóa lính chết
            self.creeps = [c for c in self.creeps if c.hp > 0]
            # Kiểm tra spawn bị chặn
            for team in ['blue', 'red']:
                spawn_pt = self.spawn_scaled[team]
                blocked = False
                for creep in self.creeps:
                    if creep.team == team:
                        dx = creep.rect.x - spawn_pt[0]
                        dy = creep.rect.y - spawn_pt[1]
                        if dx*dx + dy*dy < self.spawn_check_distance ** 2:
                            blocked = True
                            break
                self.spawn_blocked[team] = blocked
            # ===== THÁP TẤN CÔNG LÍNH ĐỊCH =====
            for tower in self.animated_objects:
                if isinstance(tower, AnimatedTower) and tower.hp > 0:
                    closest_creep = None
                    min_dist = tower.attack_range
                    for creep in self.creeps:
                        if creep.team != tower.team and creep.hp > 0:
                            dx = creep.rect.centerx - tower.rect.centerx
                            dy = creep.rect.centery - tower.rect.centery
                            dist = (dx * dx + dy * dy) ** 0.5
                            # THÊM DÒNG NÀY
                            print(f"Khoảng cách từ tháp {tower.team} đến creep {creep.team}: {dist:.2f}")
                            if dist < min_dist:
                                min_dist = dist
                                closest_creep = creep
                    if closest_creep and min_dist <= tower.attack_range:
                        tower.attack_target(closest_creep, self.bullets)
            # Cập nhật đạn
            for bullet in self.bullets[:]:
                bullet.update(dt)
                if not bullet.active:
                    self.bullets.remove(bullet)
            # Spawn wave
            self.wave_timer += dt
            if self.wave_timer >= self.wave_interval:
                self.wave_timer = 0
                if not self.spawn_blocked['blue']:
                    self.spawn_wave('blue')
                if not self.spawn_blocked['red']:
                    self.spawn_wave('red')

        def draw(self):
            self.screen.blit(self.background, (0, 0))

            # Vẽ tất cả đối tượng tĩnh (nhà, cỏ, tháp, nhân vật)
            for obj in self.animated_objects:
                img, rect = obj.get_image()
                self.screen.blit(img, rect)

            # Vẽ thanh máu tháp
            for obj in self.animated_objects:
                if isinstance(obj, AnimatedTower) and obj.hp > 0:
                    obj.draw_health_bar(self.screen)

            # Vẽ phạm vi tấn công của tháp (vòng tròn vàng)
            for obj in self.animated_objects:
                if isinstance(obj, AnimatedTower) and obj.hp > 0:
                    pygame.draw.circle(self.screen, (255, 255, 0), obj.rect.center, obj.attack_range, 2)

            # Vẽ lính
            for creep in self.creeps:
                img, rect = creep.get_image()
                self.screen.blit(img, rect)
                creep.draw_health_bar(self.screen)

            # Vẽ đạn
            for bullet in self.bullets:
                bullet.draw(self.screen, 0, 0)

            # Vẽ thanh máu nhân vật chính
            self.draw_character_health_bars()


        def draw_character_health_bars(self):
            player = self.get_character()
            if not player:
                return
            bar_width = 260
            bar_height = 18
            x = 20
            y = 20
            border_color = (255, 255, 255)
            hp_bg_color = (50, 0, 0)
            hp_color = (200, 20, 20)
            stamina_bg_color = (40, 20, 0)
            stamina_color = (240, 180, 40)

            pygame.draw.rect(self.screen, border_color, (x - 2, y - 2, bar_width + 4, bar_height + 4), border_radius=8)
            pygame.draw.rect(self.screen, hp_bg_color, (x, y, bar_width, bar_height), border_radius=8)
            hp_ratio = max(0, player.health) / max(1, player.max_health)
            fill_width = int(bar_width * hp_ratio)
            pygame.draw.rect(self.screen, hp_color, (x, y, fill_width, bar_height), border_radius=8)

            stamina_y = y + bar_height + 10
            pygame.draw.rect(self.screen, border_color, (x - 2, stamina_y - 2, bar_width + 4, bar_height + 4), border_radius=8)
            pygame.draw.rect(self.screen, stamina_bg_color, (x, stamina_y, bar_width, bar_height), border_radius=8)
            stamina_ratio = max(0, player.stamina) / max(1, player.max_stamina)
            stamina_width = int(bar_width * stamina_ratio)
            pygame.draw.rect(self.screen, stamina_color, (x, stamina_y, stamina_width, bar_height), border_radius=8)

            font = pygame.font.SysFont(None, 20)
            hp_text = font.render(f"HP: {player.health}/{player.max_health}", True, (255, 255, 255))
            self.screen.blit(hp_text, (x + 8, y - 2))
            st_text = font.render(f"STAMINA: {int(player.stamina)}/{player.max_stamina}", True, (255, 255, 255))
            self.screen.blit(st_text, (x + 8, stamina_y - 2))

        def get_character(self):
            for obj in self.animated_objects:
                if isinstance(obj, AnimatedCharacter):
                    return obj
            return None

        def handle_click(self, pos):
            original_x = int(pos[0] / self.scale_factor)
            original_y = int(pos[1] / self.scale_factor)
            print(f"🖱️ Click tại screen: {pos} -> ảnh gốc: ({original_x}, {original_y})")

        def spawn_wave(self, team):
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
                print(f"Spawn {creep_type} at ({spawn_x}, {spawn_y}), team={team}")
                self.creeps.append(creep)
            print(f"Đợt lính {team} spawn theo hàng dọc, ranged ở cuối")