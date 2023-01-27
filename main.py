import pygame
import random
import sys

from constants import *
from shooter import Shooter
import obstacle
from enemy import Enemy, Extra
from laser import Laser

class Game:
    def __init__(self):
        # Shooter setup
        shooter_sprite = Shooter((SCREEN_WIDTH/2, SCREEN_HEIGHT-10), laser_speed=10)
        self.shooter = pygame.sprite.GroupSingle(shooter_sprite)

        # Health and score setup
        self.lives = 3
        self.live_surf = pygame.image.load('imgs/heart.png').convert_alpha()
        self.live_surf = pygame.transform.scale(self.live_surf, (40,40))
        self.live_x_start_pos = SCREEN_WIDTH - (self.live_surf.get_size()[0] * 2) - 60
        self.score = 0
        self.font = pygame.font.Font('fonts/font2.otf', 35)

        # Obstacle setup
        self.blocks = pygame.sprite.Group()
        self.shape = obstacle.shape
        self.block_size = 6
        self.obstacle_amount = 4
        self.obstacle_offsets = [num*(SCREEN_WIDTH/self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_offsets, x_start=50, y_start=680)

        # Enemy setup
        self.enemies = pygame.sprite.Group()
        self.enemy_lasers = pygame.sprite.Group()
        self.create_multiple_enemies(5, 11, 50, 50, 80, 200)
        self.direction = 2
        self.move_down_y_amount = 10

        # Extra setup
        self.extra_alien = pygame.sprite.GroupSingle()
        self.extra_spawn_time = random.randint(800, 1200)

        # Audio
        music = pygame.mixer.Sound('audio/music.wav')
        music.set_volume(0.4)
        music.play(loops=-1)
        self.alien_laser_sound = pygame.mixer.Sound('audio/enemy_laser.wav')
        self.alien_laser_sound.set_volume(0.2)
        self.extra_sound = pygame.mixer.Sound('audio/extra.wav')
        self.extra_sound.set_volume(0.2)
        self.game_over_sound = pygame.mixer.Sound('audio/game_over.wav')
        self.game_over_sound.set_volume(0.9)
        self.get_hit_sound = pygame.mixer.Sound('audio/get_hit.wav')
        self.get_hit_sound.set_volume(0.4)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.1)

        # FIXME
        self.run_game_over = True

    def create_obstacle(self, x_start, y_start, x_offset):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = col_index * self.block_size + x_start + x_offset
                    y = row_index * self.block_size + y_start
                    block = obstacle.Block(x, y, self.block_size)
                    self.blocks.add(block)
        
    def create_multiple_obstacles(self, *offsets, x_start, y_start):
        for x_offset in offsets:
            self.create_obstacle(x_start, y_start, x_offset)

    def create_multiple_enemies(self,rows,cols,x_separation,y_separation,x_o,y_o):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_separation + x_o
                y = row_index * y_separation + y_o
                if row_index==0: enemy = Enemy(x, y, 'yellow')
                if 1 <= row_index <= 2: enemy = Enemy(x, y, 'blue')
                if 3 <= row_index <= 5: enemy = Enemy(x, y, 'pink')
                self.enemies.add(enemy)

    def check_enemy_direction(self):
        for enemy in self.enemies.sprites():
            if enemy.rect.right > SCREEN_WIDTH:
                self.direction = -self.direction
                self.move_enemy_down(self.move_down_y_amount, -10)
            if enemy.rect.left < 0: 
                self.direction = -self.direction
                self.move_enemy_down(self.move_down_y_amount, 10)


    def move_enemy_down(self, move_down_y_amount, shift):
        if self.enemies.sprites():
            for enemy in self.enemies.sprites():
                enemy.rect.y += move_down_y_amount
                enemy.rect.x += shift

    def enemy_shoot_laser(self, speed):
        if self.enemies.sprites():
            enemy_shooter = random.choice(self.enemies.sprites())
            self.enemy_lasers.add(Laser(enemy_shooter.rect.center, -speed, 'white'))
            self.alien_laser_sound.play()

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time == 0:
            self.extra_alien.add(Extra(random.choice(['left', 'right']),speed=random.randint(3,5)))
            self.extra_spawn_time = random.randint(800,1400)

    def collision_checks(self):
        # Player lasers
        if self.shooter.sprite.lasers:
            for laser in self.shooter.sprite.lasers:
                # Obstacle collisions
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()

                # Enemy collisions
                aliens_hit = pygame.sprite.spritecollide(laser, self.enemies, True)
                for enemy in aliens_hit:
                    self.explosion_sound.play()
                    self.score += enemy.value
                    laser.kill()
                    
                # Extra collisions
                if pygame.sprite.spritecollide(laser, self.extra_alien, True):
                    self.explosion_sound.play()
                    laser.kill()
                    self.score += 500

        # Enemy lasers
        if self.enemy_lasers:
            for e_laser in self.enemy_lasers:
                # Obstacle collisions
                if pygame.sprite.spritecollide(e_laser, self.blocks, True):
                    e_laser.kill()

                # Player collisions
                if pygame.sprite.spritecollide(e_laser, self.shooter, False):
                    e_laser.kill()
                    self.get_hit_sound.play()
                    self.lives -= 1
        
        # Enemies with obstacles
        if self.enemies:
            for enemy in self.enemies:
                pygame.sprite.spritecollide(enemy, self.blocks, True)
                if pygame.sprite.spritecollide(enemy, self.shooter, False):
                    self.lives = 0

    def display_lives(self):
        for life in range(self.lives):
            x = self.live_x_start_pos + (life * self.live_surf.get_size()[0] * 1.1)
            screen.blit(self.live_surf, (x, 8))

    def display_score(self):
        self.text_surf = self.font.render(f'Score: {self.score}', True, white)
        screen.blit(self.text_surf, (12,10))

    # TODO
    def check_game_over(self):
        if self.run_game_over:
            if self.lives == 0:
                self.game_over_sound.play()
                self.run_game_over = False
            

    def run(self):
        # Updates
        self.enemy_lasers.update()
        self.enemies.update(self.direction)
        self.extra_alien.update()
        self.shooter.update() 

        # Functions 
        self.check_enemy_direction()
        self.extra_alien_timer()
        self.collision_checks()
        self.display_lives()
        self.display_score()
        self.check_game_over()

        # Draw
        self.extra_alien.draw(screen)
        self.blocks.draw(screen)
        self.enemy_lasers.draw(screen)
        self.enemies.draw(screen)
        self.shooter.sprite.lasers.draw(screen)
        self.shooter.draw(screen)

class CRT:
    def __init__(self):
        self.tv = pygame.image.load('imgs/tv.png').convert_alpha()
        self.tv = pygame.transform.scale(self.tv, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def draw(self):
        self.tv.set_alpha(80)
        screen.blit(self.tv, (0,0))
    




# class GameState:
#     def __init__(self):
#         self.state = 'intro'

#     def intro(self):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#         # Main logic
#         screen.fill(dark_gray)

#     def main_game(self):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == ALIENLASER:
#                 game.enemy_shoot_laser(4)

#         # Main logic
#         screen.fill(dark_gray)
#         game.run()
#         crt.draw()







if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Screen
    screen = pygame.display.set_mode(size)

    game = Game()
    crt = CRT()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.enemy_shoot_laser(4)

        # Main logic
        screen.fill(dark_gray)
        game.run()
        crt.draw()

        # Update
        clock.tick(60)
        pygame.display.update()



