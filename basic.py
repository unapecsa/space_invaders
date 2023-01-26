import pygame, sys
from constants import *

class Game:
    def __init__(self):
        # Initialize all sprites
        pass

    def run(self):
        # Update and draw all sprite groups
        pass

if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Screen
    screen = pygame.display.set_mode(size)

    game = Game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Main logic
        screen.fill(dark_gray)
        game.run()

        # Update
        clock.tick(60)
        pygame.display.update()



