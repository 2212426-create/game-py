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

    def update(self, dt):
        # Có thể thêm animation cho nhà chính (ví dụ glow)
        self.time += dt * 2
        self.glow = int(30 * (math.sin(self.time * 5) + 1))

    def get_image(self):
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

    def update(self, dt):
        self.time += dt * 5  # tốc độ animation
        # Rung nhẹ và glow dùng sin
        self.shake_x = math.sin(self.time * 10) * 1.5
        self.shake_y = math.sin(self.time * 12) * 1.5
        self.glow = int(40 * (math.sin(self.time * 8) + 1))  # 0 -> 80

    def get_image(self):
        # Tạo bản sao ảnh để thêm hiệu ứng glow
        img = self.image.copy()
        if self.glow > 10:
            overlay = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            overlay.fill((self.glow, self.glow, self.glow, 100))
            img.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        # Dịch vị trí theo rung
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

