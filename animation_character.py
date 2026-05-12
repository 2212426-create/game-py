import os
import pygame

pygame.init()

class SpriteSheet:
    def __init__(self, image_path):
        self.sheet = pygame.image.load(image_path).convert_alpha()

    def image_at(self, rect, colorkey=None):
        rect = pygame.Rect(rect)
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, count, colorkey=None):
        x, y, w, h = rect
        return [self.image_at((x + i * w, y, w, h), colorkey) for i in range(count)]

class CharacterSprite:
    def __init__(self, root_path="modelheros", scale_factor=1.0):
        self.root_path = root_path
        self.scale_factor = scale_factor
        self.facing = "right"
        self.state = "idle"
        self.frame_index = 0.0
        self.frame_speed = 12.0

        self.idle_right = self.load_image("hero01_BenPhai.png", remove_bg=True)
        self.idle_left = self.load_image("hero01_BenTrai.png", remove_bg=True)

        self.run_right_frames = self.load_sequence("run_right_{}.png", 8)
        self.run_left_frames = [pygame.transform.flip(img, True, False) for img in self.run_right_frames]

        self.walk_right_frames = self.load_sequence("walk_right_{}.png", 8)
        self.walk_left_frames = [pygame.transform.flip(img, True, False) for img in self.walk_right_frames]

        self.current_frames = self.run_right_frames

    def load_image(self, filename, remove_bg=False):
        path = os.path.join(self.root_path, filename)
        image = pygame.image.load(path)
        if remove_bg:
            image = image.convert()
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
            image = image.convert_alpha()
        else:
            image = image.convert_alpha()

        if self.scale_factor != 1.0:
            new_size = (int(image.get_width() * self.scale_factor), int(image.get_height() * self.scale_factor))
            image = pygame.transform.smoothscale(image, new_size)
        return image

    def load_sequence(self, pattern, count):
        frames = []
        for i in range(1, count + 1):
            frames.append(self.load_image(pattern.format(i)))
        return frames

    def set_state(self, moving, facing):
        self.state = "run" if moving else "idle"
        self.facing = facing
        if self.state == "run":
            self.current_frames = self.run_right_frames if self.facing == "right" else self.run_left_frames
        else:
            self.current_frames = []
            self.frame_index = 0.0

    def update(self, dt):
        if self.state == "run" and self.current_frames:
            self.frame_index += self.frame_speed * dt
            if self.frame_index >= len(self.current_frames):
                self.frame_index -= len(self.current_frames)

    def get_image(self):
        if self.state == "idle":
            return self.idle_right if self.facing == "right" else self.idle_left
        return self.current_frames[int(self.frame_index)]

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    character = CharacterSprite(scale_factor=1.0)
    x, y = 100, 100
    speed = 180

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        moving = False
        facing = character.facing

        dx = dy = 0
        if keys[pygame.K_a]:
            dx -= speed * dt
            facing = "left"
            moving = True
        if keys[pygame.K_d]:
            dx += speed * dt
            facing = "right"
            moving = True
        if keys[pygame.K_w]:
            dy -= speed * dt
            moving = True
        if keys[pygame.K_s]:
            dy += speed * dt
            moving = True

        x += dx
        y += dy
        character.set_state(moving, facing)
        character.update(dt)

        screen.fill((30, 30, 30))
        image = character.get_image()
        rect = image.get_rect(center=(int(x), int(y)))
        screen.blit(image, rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()

    pygame.quit()