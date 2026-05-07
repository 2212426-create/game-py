import pygame
from animated_objects import AnimatedTower, AnimatedGrass, AnimatedWater

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

        # ----- BỤI CỎ (tọa độ gốc) -----
        grass_positions_original = [
            (368, 135), (258, 135), (257, 212), (377, 219),
        ]
        grass_scale = self.scale_factor * 0.25   # nhỏ hơn map
        for x, y in grass_positions_original:
            sx = int(x * self.scale_factor)
            sy = int(y * self.scale_factor)
            self.animated_objects.append(AnimatedGrass(sx, sy, "assets/images/grass.png", grass_scale))

        # ----- THÁP (tọa độ gốc) -----
        tower_positions_original = [
            (276, 161, "blue"), (192, 163, "blue"),
            (386, 162, "red"), (479, 164, "red")
        ]
        tower_scale = self.scale_factor * 0.15
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
        # ----- CÁC VÙNG NƯỚC -----
        self.water_areas = []

        # Vùng nước thứ nhất (khe trên) - hãy chỉnh lại tọa độ theo click của bạn
        water_rect_original1 = (242, 1, 191, 130)
        scaled_rect1 = (int(water_rect_original1[0] * self.scale_factor),
                        int(water_rect_original1[1] * self.scale_factor),
                        int(water_rect_original1[2] * self.scale_factor),
                        int(water_rect_original1[3] * self.scale_factor))
        self.water_areas.append(AnimatedWater(*scaled_rect1, self.scale_factor, "assets/images/water.png"))

        # Vùng nước thứ hai (khe dưới) - thay tọa độ bằng số bạn đo được
        water_rect_original2 = (243, 237, 197, 126)  # ví dụ
        scaled_rect2 = (int(water_rect_original2[0] * self.scale_factor),
                        int(water_rect_original2[1] * self.scale_factor),
                        int(water_rect_original2[2] * self.scale_factor),
                        int(water_rect_original2[3] * self.scale_factor))
        self.water_areas.append(AnimatedWater(*scaled_rect2, self.scale_factor, "assets/images/water.png"))

    def update(self, dt, player_rect=None):
        for obj in self.animated_objects:
            obj.update(dt)
        for water in self.water_areas:
            water.update(dt)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        for obj in self.animated_objects:
            img, rect = obj.get_image()
            self.screen.blit(img, rect)
        for water in self.water_areas:
            water_surf = pygame.Surface((water.rect.w, water.rect.h), pygame.SRCALPHA)
            water.draw(water_surf)
            self.screen.blit(water_surf, (water.rect.x, water.rect.y))

    def handle_click(self, pos):
        original_x = int(pos[0] / self.scale_factor)
        original_y = int(pos[1] / self.scale_factor)
        print(f"🖱️ Click tại screen: {pos} -> ảnh gốc: ({original_x}, {original_y})")