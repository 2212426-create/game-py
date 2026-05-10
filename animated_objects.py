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

    #///
class Creep:
    def __init__(self, x, y, team, target, creep_type, image_path, scale_factor=1.0):
        self.original_image = pygame.image.load(image_path).convert_alpha()
        if scale_factor != 1.0:
            new_size = (int(self.original_image.get_width() * scale_factor),
                        int(self.original_image.get_height() * scale_factor))
            self.image = pygame.transform.scale(self.original_image, new_size)
        else:
            self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.team = team
        self.target = target
        self.type = creep_type
        self.spawn_x = x
        self.spawn_y = y

        # Chỉ số mặc định
        self.max_hp = 100
        self.hp = 100
        self.attack_damage = 10
        self.attack_cooldown = 0
        self.attack_range = 40
        self.attack_speed = 1.0
        self.cooldown_max = 1.0 / self.attack_speed
        self.speed = 100
        self.is_ranged = False

        # Gán theo loại (đã tăng tốc độ cho warrior/archer/mage)
        if creep_type == "orc_warrior":
            self.max_hp = 120
            self.attack_damage = 15
            self.speed = 120
            self.attack_range = 35
        elif creep_type == "orc_tanker":
            self.max_hp = 250
            self.attack_damage = 8
            self.speed = 110
            self.attack_range = 35
        elif creep_type == "slime":
            self.max_hp = 70
            self.attack_damage = 12
            self.speed = 110
            self.attack_range = 110
            self.is_ranged = True
        elif creep_type == "warrior":
            self.max_hp = 100
            self.attack_damage = 12
            self.speed = 110
            self.attack_range = 35
        elif creep_type == "archer":
            self.max_hp = 70
            self.attack_damage = 18
            self.speed = 110
            self.attack_range = 120
            self.is_ranged = True
        elif creep_type == "mage":
            self.max_hp = 80
            self.attack_damage = 20
            self.speed = 105
            self.attack_range = 130
            self.is_ranged = True
        else:
            self.max_hp = 100
            self.attack_damage = 10
            self.speed = 100

        self.hp = self.max_hp

    def attack(self, enemy):
        """Tấn công kẻ địch"""
        enemy.take_damage(self.attack_damage)
        self.attack_cooldown = self.cooldown_max

    def update(self, dt, enemies):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # Tìm kẻ địch gần nhất trong tầm phát hiện
        detection_range = self.attack_range + 150
        closest = None
        min_dist = detection_range
        for e in enemies:
            if e.team != self.team and e.hp > 0:
                dx = e.rect.centerx - self.rect.centerx
                dy = e.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist < min_dist:
                    min_dist = dist
                    closest = e

        if closest:
            # Tấn công nếu trong tầm
            if self.attack_cooldown <= 0 and min_dist <= self.attack_range:
                self.attack(closest)

            # Xử lý di chuyển: ranged chỉ tiến, không lùi
            if self.is_ranged:
                ideal_dist = self.attack_range - 10
                dx = self.rect.centerx - closest.rect.centerx
                dy = self.rect.centery - closest.rect.centery
                dist = math.hypot(dx, dy)
                # Chỉ tiến lại nếu quá xa, không bao giờ lùi
                if dist > ideal_dist + 20:
                    if dist > 0:
                        step = min(self.speed * dt, dist - ideal_dist)
                        self.rect.x -= dx / dist * step
                        self.rect.y -= dy / dist * step
                # Nếu quá gần hoặc trong tầm lý tưởng: đứng yên
            else:
                # Cận chiến: lao vào địch
                dx = closest.rect.centerx - self.rect.centerx
                dy = closest.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 5:
                    step = min(self.speed * dt, dist)
                    self.rect.x += dx / dist * step
                    self.rect.y += dy / dist * step
            return

        # Không có địch: di chuyển về target (base đối phương)
        dx = self.target[0] - self.rect.x
        dy = self.target[1] - self.rect.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            step_x = dx / dist * self.speed * dt
            step_y = dy / dist * self.speed * dt
            self.rect.x += step_x
            self.rect.y += step_y

        # Giới hạn map (tránh bay ra ngoài)
        if self.rect.x < -300 or self.rect.x > 2300:
            self.hp = 0

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            return True
        return False

    def draw_health_bar(self, screen, camera_x=0, camera_y=0):
        bar_width = 40
        bar_height = 6
        x = self.rect.x - camera_x + (self.rect.width - bar_width) // 2
        y = self.rect.y - camera_y - 8
        pygame.draw.rect(screen, (255, 0, 0), (x, y, bar_width, bar_height))
        health_percent = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (0, 255, 0), (x, y, bar_width * health_percent, bar_height))

    def get_image(self):
        return self.image, self.rect