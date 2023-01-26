import pygame
from constants import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.image.load(f'imgs/{color}_alien.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (40,30))
        self.rect = self.image.get_rect(topleft = (x, y))
        self.tmp = 0
        if color == 'pink': self.value = 100
        elif color == 'blue': self.value = 200
        else: self.value = 400
    
    def update(self,direction):
        self.tmp += 1
        if not self.tmp % 1:
            self.rect.x += direction
            self.tmp = 0


class Extra(pygame.sprite.Sprite):
    def __init__(self,side):
        super().__init__()
        self.image = pygame.image.load(f'imgs/extra_alien.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (80,35))

        if side == 'left':
            self.rect = self.image.get_rect(center = (-100, 80))
            self.speed = 1
        elif side == 'right':
            self.rect = self.image.get_rect(center = (SCREEN_WIDTH+100, 80))
            self.speed = -1

    def update(self):
        self.rect.x += self.speed
