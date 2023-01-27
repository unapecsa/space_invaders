import pygame
from constants import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.image.load(f'imgs/{color}_alien.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (40,30))
        self.rect = self.image.get_rect(topleft = (x, y))
        if color == 'pink': self.value = 100
        elif color == 'blue': self.value = 200
        else: self.value = 400
    
    def update(self,direction):
        self.rect.x += direction

class Extra(pygame.sprite.Sprite):
    def __init__(self,side,speed):
        super().__init__()
        self.image = pygame.image.load(f'imgs/extra_alien.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (80,35))
        self.extra_sound = pygame.mixer.Sound('audio/extra.wav')
        self.extra_sound.set_volume(0.05)
        self.extra_sound.play(loops=-1, fade_ms=500)

        if side == 'left':
            self.rect = self.image.get_rect(center = (-35, 80))
            self.speed = speed
        elif side == 'right':
            self.rect = self.image.get_rect(center = (SCREEN_WIDTH+35, 80))
            self.speed = -speed
        
    def destroy(self):
        if self.rect.right < 0 or self.rect.left > SCREEN_HEIGHT:
            self.kill()
            self.extra_sound.fadeout(500)

    def update(self):
        self.rect.x += self.speed
        self.destroy()
