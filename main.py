import pygame
from map import GameMap

pygame.init()
# Bạn có thể đổi kích thước màn hình ở đây
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Tự động tính scale_factor để map vừa khít màn hình
temp_map = pygame.image.load("map.png").convert()
orig_w, orig_h = temp_map.get_size()
scale_w = SCREEN_WIDTH / orig_w
scale_h = SCREEN_HEIGHT / orig_h
scale_factor = min(scale_w, scale_h)  # thu nhỏ để vừa cả chiều
print(f"Original map: {orig_w}x{orig_h} -> Scale factor: {scale_factor:.3f}")

# Khởi tạo map với scale_factor
game_map = GameMap(screen, scale_factor=scale_factor)

# Bạn có thể thêm danh sách các object và tọa độ gốc cần hiệu chỉnh
# Bấm chuột để lấy tọa độ gốc, sau đó cập nhật vào map.py

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            game_map.handle_click(event.pos)   # in ra world và original
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    game_map.update(dt)
    screen.fill((0,0,0))
    game_map.draw()
    pygame.display.flip()

pygame.quit()