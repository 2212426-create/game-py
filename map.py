import pygame
from animated_objects import AnimatedTower, AnimatedGrass, AnimatedMainTown, Creep

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


        # ----- NHÀ CHÍNH (main town) -----
        # ⚠️ BẠN CẦN LẤY LẠI TỌA ĐỘ GỐC BẰNG CÁCH CLICK CHUỘT TRÊN MAP MỚI
        main_town_positions_original = [
            (5, 230, "blue"),    # tạm giữ, nhưng hãy click để lấy lại
            (972, 246, "red")
        ]
        main_town_scale = self.scale_factor * 0.6    # giảm từ 0.3 xuống 0.25 (nhỏ hơn)
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
        tower_scale = self.scale_factor * 0.45   # giảm từ 0.15 xuống 0.12 (nhỏ hơn)
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

        # ----- LÍNH (CREEP) -----
        self.creeps = []                # danh sách lính hiện có
        self.wave_timer = 0
        self.wave_interval = 10.0       # mỗi 10 giây sinh 1 đợt
        self.creeps_per_wave = 4        # mỗi đợt 4 lính mỗi bên
        self.spawn_check_distance = 100   # pixel
        self.spawn_blocked = {'blue': False, 'red': False}

        # ĐIỂM SPAWN (tọa độ gốc của map 1400x768, bạn cần lấy lại bằng click)
        self.spawn_points = {
            'blue': (87, 204),
            'red': (945, 210)
        }
        self.target_points = {
            'blue': (810, 280),
            'red': (120, 280)
        }

        # Scale các điểm spawn và target
        self.spawn_scaled = {}
        self.target_scaled = {}
        for team, (x, y) in self.spawn_points.items():
            self.spawn_scaled[team] = (int(x * self.scale_factor), int(y * self.scale_factor))
        for team, (x, y) in self.target_points.items():
            self.target_scaled[team] = (int(x * self.scale_factor), int(y * self.scale_factor))

    def update(self, dt, player_rect=None):
        # Cập nhật object tĩnh
        for obj in self.animated_objects:
            obj.update(dt)

        # Cập nhật lính (di chuyển + combat)
        blue_creeps = [c for c in self.creeps if c.team == 'blue']
        red_creeps = [c for c in self.creeps if c.team == 'red']
        for creep in self.creeps:
            enemies = red_creeps if creep.team == 'blue' else blue_creeps
            creep.update(dt, enemies)

        # Xóa lính chết
        self.creeps = [c for c in self.creeps if c.hp > 0]

        # Xóa lính đến target (nếu muốn)
        '''for creep in self.creeps[:]:
            if (abs(creep.rect.x - creep.target[0]) < 20 and
                    abs(creep.rect.y - creep.target[1]) < 20):
                self.creeps.remove(creep)'''

        # Kiểm tra xem khu vực spawn có còn lính không
        for team in ['blue', 'red']:
            spawn_pt = self.spawn_scaled[team]
            blocked = False
            for creep in self.creeps:
                if creep.team == team:
                    dx = creep.rect.x - spawn_pt[0]
                    dy = creep.rect.y - spawn_pt[1]
                    if dx * dx + dy * dy < self.spawn_check_distance ** 2:
                        blocked = True
                        break
            self.spawn_blocked[team] = blocked

        # Spawn wave nếu timer hết và không bị chặn
        self.wave_timer += dt
        if self.wave_timer >= self.wave_interval:
            self.wave_timer = 0
            if not self.spawn_blocked['blue']:
                self.spawn_wave('blue')
            if not self.spawn_blocked['red']:
                self.spawn_wave('red')

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for obj in self.animated_objects:
            img, rect = obj.get_image()
            self.screen.blit(img, rect)
        for creep in self.creeps:
            img, rect = creep.get_image()
            self.screen.blit(img, rect)
            creep.draw_health_bar(self.screen)  # vẽ thanh máu

    def handle_click(self, pos):
        original_x = int(pos[0] / self.scale_factor)
        original_y = int(pos[1] / self.scale_factor)
        print(f"🖱️ Click tại screen: {pos} -> ảnh gốc: ({original_x}, {original_y})")
    #
    def spawn_wave(self, team):
        spawn_base = self.spawn_scaled[team]
        target_pos = self.target_scaled[team]

        # Định nghĩa danh sách lính theo thứ tự từ TRƯỚC đến SAU (front to back)
        if team == 'blue':
            # Hàng ngang: di chuyển sang phải, front là x lớn hơn, back là x nhỏ hơn
            creep_order = [
                ('orc_tanker', 'orc-tanker.png'),  # đứng trước nhất
                ('orc_warrior', 'orc-warrior.png'),  # lính thứ 4 (có thể đổi)
                ('orc_warrior', 'orc-warrior.png'),
                ('slime', 'slime.png'),

            ]
        else:  # red
            # Di chuyển sang trái, front là x nhỏ hơn, back là x lớn hơn
            creep_order = [
                ('warrior', 'warrior.png'),  # front
                ('warrior', 'warrior.png'),
                ('archer', 'archer.png'),
                ('mage', 'mage.png'),

            ]

        # Khoảng cách giữa các lính trong hàng (pixel, theo phương di chuyển)
        spacing = 25
        # Xác định chiều (+1: blue đi phải, -1: red đi trái)
        direction = 1 if target_pos[0] > spawn_base[0] else -1

        for idx, (creep_type, img_file) in enumerate(creep_order):
            img_path = f"assets/images/{img_file}"
            # Tính offset dọc theo hàng: idx càng lớn (càng về sau) thì offset càng âm (lùi về phía nhà)
            if direction == 1:  # blue: front có offset lớn hơn (x càng lớn càng gần địch)
                offset_x = (len(creep_order) - 1 - idx) * spacing  # front có offset max
            else:  # red: front có offset âm (x càng nhỏ càng gần địch)
                offset_x = -((len(creep_order) - 1 - idx) * spacing)
            # Nếu là lính đánh xa (slime, archer, mage) có thể lùi thêm chút nữa

            if creep_type in ['slime', 'archer']:
                offset_x += -15 * direction  # lùi thêm 8 pixel
            if creep_type in ['mage']:
                offset_x += -25 * direction  # lùi thêm 8 pixel

            # Tọa độ spawn thực tế
            spawn_x = spawn_base[0] + offset_x
            # Giữ nguyên y (cùng lane), có thể thêm offset nhỏ để tránh chồng khít
            spawn_y = spawn_base[1] + (idx % 2) * 6  # hơi lệch dọc để tránh đè lên nhau

            creep = Creep(spawn_x, spawn_y, team, target_pos, creep_type, img_path, self.scale_factor)
            self.creeps.append(creep)

        print(f"Đợt lính {team} spawn theo hàng dọc, ranged ở cuối")