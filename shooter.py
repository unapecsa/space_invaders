import pygame
from laser import Laser
from constants import *

class Shooter(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Spaceship
        self.image = pygame.image.load('imgs/spaceship.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50,40))
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = 3
        # Laser
        self.ready = True
        self.laser_time = 0
        self.cooldown = 700
        self.lasers = pygame.sprite.Group()
        self.shooter_laser_sound = pygame.mixer.Sound('audio/shooter_laser.wav')
        self.shooter_laser_sound.set_volume(0.1)

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            
    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        elif self.rect.right >= SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        
    def shoot_laser(self):
        self.lasers.add(Laser(self.rect.midtop, 5, 'red'))
        self.shooter_laser_sound.play()

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.cooldown:
                self.ready = True
