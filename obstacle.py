import pygame
from constants import * 

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.image = pygame.Surface((size,size))
        self.image.fill(green)
        self.rect = self.image.get_rect(topleft = (x, y))
        self.speed = 2
        

shape = [
    '  xxxxxxx',
    ' xxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]
        