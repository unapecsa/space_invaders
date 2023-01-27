import pygame
from constants import *

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, laser_speed, color):
        super().__init__()
        # self.image = pygame.Surface((4,20))
        # self.image.fill(white)
        self.image = pygame.image.load(f'imgs/{color}_laser.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (4,20))
        self.rect = self.image.get_rect(center = pos)
        self.laser_speed = laser_speed

    def destroy(self):
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

    def update(self):
        self.rect.y -= self.laser_speed
        self.destroy()