import pygame
import random
import sys

from constants import *
from shooter import Shooter
import obstacle
from enemy import Enemy, Extra, Nyan
from laser import Laser

class Game:
    def __init__(self, enemy_speed=2, enemy_y_jump=10, enemy_shoot_freq=60, enemy_shoot_speed=4, laser_cooldown=580, wave=1, score=0, lives=3):
        # Shooter setup
        shooter_sprite = Shooter((SCREEN_WIDTH/2, SCREEN_HEIGHT-10), laser_speed=10, laser_cooldown=laser_cooldown)
        self.shooter = pygame.sprite.GroupSingle(shooter_sprite)

        # Health and score setup
        self.lives = lives
        self.live_surf = pygame.image.load('imgs/heart.png').convert_alpha()
        self.live_surf = pygame.transform.scale(self.live_surf, (40,40))
        self.live_x_start_pos = SCREEN_WIDTH - (self.live_surf.get_size()[0] * 2) - 60
        self.score = score
        self.wave = wave
        def font(size):
            return pygame.font.Font('fonts/font.otf', size)
        self.font = font(35)
        self.wave_font = font(25)

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
        self.create_multiple_enemies(5, 2, 50, 50, 80, 200)
        self.direction = enemy_speed
        self.move_down_y_amount = enemy_y_jump
        self.enemy_shoot_freq = enemy_shoot_freq
        self.enemy_cooldown = enemy_shoot_freq
        self.enemy_shoot_speed = enemy_shoot_speed

        # Extra setup
        self.extra_alien = pygame.sprite.GroupSingle()
        self.extra_spawn_time = random.randint(800, 1200)

        # Audio
        self.alien_laser_sound = pygame.mixer.Sound('audio/enemy_laser.wav')
        self.alien_laser_sound.set_volume(0.2)
        self.extra_sound = pygame.mixer.Sound('audio/extra.wav')
        self.extra_sound.set_volume(0.2)
        self.get_hit_sound = pygame.mixer.Sound('audio/get_hit.wav')
        self.get_hit_sound.set_volume(0.6)
        self.explosion_sound = pygame.mixer.Sound('audio/explosion.wav')
        self.explosion_sound.set_volume(0.1)


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
        self.enemy_cooldown -= 1
        if self.enemy_cooldown == 0:
            if self.enemies.sprites():
                enemy_shooter = random.choice(self.enemies.sprites())
                self.enemy_lasers.add(Laser(enemy_shooter.rect.center, -speed, 'white'))
                self.alien_laser_sound.play()
                self.enemy_cooldown = self.enemy_shoot_freq

    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time == 0:
            self.extra_alien.add(Nyan('left',speed=4))
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
                if pygame.sprite.spritecollide(laser, self.extra_alien, False):
                    self.explosion_sound.play()
                    self.extra_alien.sprite.extra_kill()
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

    def display_info(self):
        self.score_surf = self.font.render(f'Score: {self.score}', True, white)
        screen.blit(self.score_surf, (12,10))
        self.wave_surf = self.wave_font.render(f'Wave {self.wave}', True, white)
        screen.blit(self.wave_surf, self.wave_surf.get_rect(center =(SCREEN_WIDTH/2,26)))

    def check_victory(self):
        if not self.enemies:
            if self.extra_alien.sprites():
                self.extra_alien.sprite.extra_kill()
            return True

    def check_game_over(self):
        if self.lives == 0:
            if self.extra_alien.sprites():
                self.extra_alien.sprite.extra_kill()
            return True

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
        self.display_info()
        self.enemy_shoot_laser(self.enemy_shoot_speed)

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
    
class GameState:
    def __init__(self):
        self.state = 'intro'
        self.game = None

        # Inits related to states
        # Intro
        self.intro_img = pygame.image.load('imgs/logo.png').convert_alpha()
        self.intro_img = pygame.transform.scale(self.intro_img, (150,150))
        def shaded_font(size):
            return pygame.font.Font('fonts/shaded_font.ttf', size)
        self.invade_text = shaded_font(90).render(f'INVADE', True, red)
        self.space_text = shaded_font(160).render(f'SPACE', True, red)
        self.font = pygame.font.Font('fonts/font.otf', 24)
        self.intro_text = self.font.render(f'Click anywhere to start', True, white)
        #Outro
        self.outro_img = pygame.image.load('imgs/logo_dead.png').convert_alpha()
        self.outro_img = pygame.transform.scale(self.outro_img, (200,200))
        self.game_over_img = pygame.image.load('imgs/game_over.png').convert_alpha()
        self.game_over_img = pygame.transform.scale(self.game_over_img, (350,350))
        self.game_over_sound = pygame.mixer.Sound('audio/game_over.wav')
        self.outro_text = self.font.render(f'Click anywhere to restart', True, white)
        self.game_over_sound.set_volume(0.9)
        #Music
        self.music_w1 = pygame.mixer.Sound('audio/music_w1.wav')
        self.music_w1.set_volume(0.4)
        self.music_w1.play(loops=-1)
        self.music_w2 = pygame.mixer.Sound('audio/music_w2.wav')
        self.music_w2.set_volume(0.4)

    def state_manager(self):
        if self.state == 'intro':
            self.intro()
        elif self.state == 'wave_one':
            self.wave_one()
        elif self.state == 'wave_two':
            self.wave_two()
        elif self.state == 'game_over':
            self.game_over()

    def intro(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game = Game()
                self.state = 'wave_one'
        
        def blink():
            if int(pygame.time.get_ticks()/800) % 2 == 0:
                screen.blit(self.intro_text, self.intro_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-200)))

        # Main logic
        screen.fill(dark_gray)
        screen.blit(self.intro_img, self.intro_img.get_rect(center = (SCREEN_WIDTH/2, 200)))
        screen.blit(self.invade_text, self.invade_text.get_rect(center = (SCREEN_WIDTH/2, 300)))
        screen.blit(self.space_text, self.space_text.get_rect(center = (SCREEN_WIDTH/2, 400)))
        blink()
        crt.draw()

    def wave_one(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Main logic
        screen.fill(dark_gray)
        self.game.run()
        crt.draw()
        if self.game.check_victory():
            self.music_w1.fadeout(3000)
            self.music_w2.play(loops=-1, fade_ms=6000)
            self.game = Game(
                enemy_speed=3, enemy_shoot_freq=50, 
                laser_cooldown=500,
                wave=2, score=self.game.score, lives=self.game.lives
                )
            self.state = 'wave_two'

        if self.game.check_game_over():
            self.game_over_sound.play()
            self.state = 'game_over'

    def wave_two(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Main logic
        screen.fill(dark_gray)
        self.game.run()
        crt.draw()
        if self.game.check_game_over():
            self.music_w2.fadeout(1000)
            self.game_over_sound.play()
            self.state = 'game_over'

    def game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.game = Game()
                self.state = 'wave_one'

        def out_blink():
            if int(pygame.time.get_ticks()/800) % 2 == 0:
                screen.blit(self.outro_text, self.outro_text.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT-200)))

        # Main logic
        screen.fill(dark_gray)
        screen.blit(self.outro_img, self.outro_img.get_rect(center = (SCREEN_WIDTH/2, 150)))
        screen.blit(self.game_over_img, self.game_over_img.get_rect(center = (SCREEN_WIDTH/2, 300)))
        out_blink()
        crt.draw()


if __name__ == '__main__':
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # Screen
    screen = pygame.display.set_mode(size)
    game_state = GameState()
    crt = CRT()

    while True:
        game_state.state_manager()

        # Update
        clock.tick(60)
        pygame.display.update()



