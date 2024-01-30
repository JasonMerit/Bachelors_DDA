import pygame as pg
from pygame.math import Vector2
import numpy as np
import random
import os

from config import *

random.seed(SEED)
np.random.seed(SEED)

class Platform(pg.sprite.Sprite):
    
    def __init__(self, x, y, width, color):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width, 20)).convert_alpha()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    @property
    def top(self):
        return self.rect.top

    @property
    def bounds(self):
        return self.rect.left, self.rect.right

    @property
    def right(self):
        return self.rect.right
    
    @property
    def left(self):
        return self.rect.left
    
    def update(self, screen, speed = 10.0):
        self.rect.move_ip((-speed, 0))
        if self.rect.right <= 0:
            self.rect.left = 800
            # del self
            # remove from sprite group
            self.kill()
        # screen.blit(self.image, self.rect)
        self.draw(screen)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)

class Player(pg.sprite.Sprite):

    gravity = 2.0
    speed = 0.0
    ground_height = 500
    is_floor = False
    
    # jumping
    jump_speed = 15.0
    is_holding = False
    max_hold_time = 0.1
    hold_timer = 0.0
    jump_threshold = 10.0
    
    def __init__(self, x, y, size, color):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((size, size)).convert_alpha()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
    
    @property
    def bottom(self):
        return self.rect.bottom

    @property
    def left(self):
        return self.rect.left

    @property
    def right(self):
        return self.rect.right
    
    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                # grace using time
                distance = self.ground_height - self.bottom
                # print(f'{distance = }, {self.speed = }')
                if self.is_floor or distance - 1.5*self.speed <= self.jump_threshold: 
                    self.is_holding = True
                    self.hold_timer = 0.0
                    self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.is_holding = False
    
    def update(self):
        # Apply gravity if not on floor
        if not self.is_floor:  
            
            # Holding jump
            if self.is_holding:
                self.hold_timer += DT
                if self.hold_timer >= self.max_hold_time:
                    self.is_holding = False
            else:
                self.speed += self.gravity

            # Move player
            self.rect.move_ip((0, self.speed))  
    
    def draw(self, screen):
        screen.blit(self.image, self.rect)
    
    def jump(self):
        self.speed = -self.jump_speed
        self.is_floor = False

    def floor_collision(self, platform : Platform):
        # height = self.platform.height if left <= self.player_x <= right else self.player.ground_height
        # if platform is None:
        #     self.is_floor = False
        #     return
        height = platform.top
        if self.rect.bottom > height:  
            self.rect.bottom = height
            self.is_floor = True
            self.speed = 0.0
        elif self.rect.bottom < height:
            self.is_floor = False
    

class Game():
    pg.init()

    BLACK, WHITE = (24, 24, 24), (202, 202, 202)
    BLUE, GREY = (90, 95, 116), (179, 178, 194) 
    RED, GREEN = (232, 65, 24), (24, 232, 65)
    width, height = 800, 600
    screen = pg.display.set_mode((width, height))
    screen.fill(BLUE)
    pg.display.set_caption("Canabalt")

    clock = pg.time.Clock()
    font_style = pg.font.SysFont(None, 30)
    font_style_big = pg.font.SysFont("rockwell", 50)
    # font_style_big = pg.font.SysFont("verdana", 50)
    font_style_small = pg.font.SysFont(None, 20)

    scrolling_speed = 1
    # gap = Platform(0, height-20, width, RED)
    
    def __init__(self):
        self.restart()

    def restart(self):
        # Platforms
        self.sprites = pg.sprite.Group()
        self.platforms = [Platform(i * 250, 450, 250, self.random_color()) for i in range(NUM_PLATFORM)]
        self.sprites.add(self.platforms)
        # self.platforms = self.construct_platforms()
        # self.active_platform_indx = 0
        self.platform : Platform = self.platforms.pop(0)
        # self.platforms.append(self.platform)
        # self.platform : Platform = self.platforms[self.platform_indx]
        
        # self.gap.name = 'gap'
        self.platform.name = 'kek'

        # Player
        player_x = 100
        self.player = Player(player_x, self.platform.top, 20, self.BLACK)
        self.score = 0

    def random_color(self):
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def construct_platforms(self):
        # [(1.25, 0.5), (11.5, 0.75), (19.25, 0.75)]
        width = 300
        y = 450
        platforms = [Platform(self.width -20 + i * 380, y, width, self.random_color()) for i in range(NUM_PLATFORM)]
        self.sprites.add(platforms)
        return platforms

    def platform_transition(self):
        # Leaving current platform
        if self.platform and self.player.right > self.platform.right: # Extending over current platform
            self.platform = None
            self.player.is_floor = False
        
        # Reaching new platform
        if self.platform is None and self.player.right > self.platforms[0].left:
            self.platform = self.platforms.pop(0)
            
            # wall collision
            grace = 30
            if self.player.bottom > self.platform.top + grace:
                self.restart()
                # return
            
            if len(self.platforms) == 1:
                self.platforms += self.construct_platforms()

    def tick(self):
        self.process_events()

        # Drawing player, gap, platforms and score
        self.screen.fill(self.BLUE)

        # Move objects (wait to draw player until after collision check)
        self.player.update()
        self.sprites.update(self.screen)

        # Check for new platform and wall collision
        self.platform_transition()
        
        # Check for floor collision
        if self.platform:
            self.player.floor_collision(self.platform)
        else:
            # Check for off screen
            if self.player.bottom > self.height:
                self.restart()

        self.player.draw(self.screen)

        # Draw score
        self.score += 1
        msg = self.font_style_big.render(f'{self.score} m', True, self.GREY)
        self.screen.blit(msg, (self.width - msg.get_width() - 20, 20))
        
        pg.display.update()
        self.clock.tick(FPS)
    
    def debug(self, string):
        msg = self.font_style_big.render(string, True, self.GREY)
        self.screen.blit(msg, (20, 20))
    
    # def pause(self, time):
    #     # pause for time seconds
        

    def process_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                if event.key == pg.K_r:
                    self.restart()
                elif event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL:
                    path = "assets/screenshots"
                    pg.image.save(self.screen, f"{path}/{len(os.listdir(path))}.png")
                elif event.key == pg.K_p:
                    paused = True
                    while paused:
                        for event in pg.event.get():
                            if event.type == pg.QUIT:
                                pg.quit()
                                quit()
                            elif event.type == pg.KEYDOWN:
                                if event.key == pg.K_ESCAPE:
                                    pg.quit()
                                    quit()
                                if event.key == pg.K_p:
                                    paused = False
            
            self.player.process_event(event)
                    
                
                
                
if __name__ == "__main__":
    game = Game()
    
    while True:
        game.tick()