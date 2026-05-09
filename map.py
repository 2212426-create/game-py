import pygame
from animated_objects import AnimatedTower, AnimatedGrass, AnimatedMainTown

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
        # ⚠️ CẦN LẤY LẠI TỌA ĐỘ CHO MAP 1400x768
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

        # ----- ĐÃ XÓA TOÀN BỘ NƯỚC -----

    def update(self, dt, player_rect=None):
        for obj in self.animated_objects:
            obj.update(dt)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for obj in self.animated_objects:
            img, rect = obj.get_image()
            self.screen.blit(img, rect)

    def handle_click(self, pos):
        original_x = int(pos[0] / self.scale_factor)
        original_y = int(pos[1] / self.scale_factor)
        print(f"🖱️ Click tại screen: {pos} -> ảnh gốc: ({original_x}, {original_y})")