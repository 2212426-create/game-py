import pygame
import math

class Bullet:
    def __init__(self, x, y, target, damage, speed=50, image_path=None):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.active = True

        # Tạo hình ảnh cho viên đạn (có thể dùng ảnh hoặc vẽ hình tròn)
        if image_path:
            self.original_image = pygame.image.load(image_path).convert_alpha()
        else:
            self.original_image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 220, 80), (4, 4), 4)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        if not self.active or not self.target:
            self.active = False
            return

        target_hp = getattr(self.target, 'hp', None)
        target_health = getattr(self.target, 'health', None)
        if (target_hp is not None and target_hp <= 0) or (target_health is not None and target_health <= 0):
            self.active = False
            return

        target_rect = getattr(self.target, 'rect', None)
        if target_rect is None:
            self.active = False
            return

        dx = target_rect.centerx - self.x
        dy = target_rect.centery - self.y
        dist = math.hypot(dx, dy)
        if dist < 1:
            self.active = False
            return

        step = min(self.speed * dt, dist)
        self.x += (dx / dist) * step
        self.y += (dy / dist) * step
        self.rect.center = (self.x, self.y)

        if self.rect.colliderect(self.target.rect):
            self.target.take_damage(self.damage)
            self.active = False

    def draw(self, screen, camera_x=0, camera_y=0):
        if self.active:
            screen.blit(self.image, (self.x - camera_x, self.y - camera_y))
