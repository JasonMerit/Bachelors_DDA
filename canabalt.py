import pygame as pg
from pygame.math import Vector2
import numpy as np
import random
import os

from config import *

random.seed(SEED)
np.random.seed(SEED)

class Platform(pg.sprite.Sprite):
    
    def __init__(self, x, y, width, color, rest_area = 0):
        pg.sprite.Sprite.__init__(self)
        self.is_rest_area = rest_area  # Flag for level completion
        

        self.image = pg.Surface((width, HEIGHT-y)).convert_alpha()
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        shade = (0, 0, 0, 100)
        line_width = 10
        shadow = pg.Surface((width, line_width)).convert_alpha()
        shadow.fill(shade)
        self.image.blit(shadow, (0, 0))

        shadow = pg.Surface((line_width, HEIGHT-y)).convert_alpha()
        shadow.fill(shade)
        self.image.blit(shadow, (0, line_width))
        self.image.blit(shadow, (width - line_width, line_width))

        if rest_area:
            font = pg.font.SysFont("rockwell", 50)
            msg = font.render(f"LEVEL {rest_area}", True, GREY)
            x = (width - msg.get_width()) / 2
            y = (HEIGHT-y - msg.get_height()) / 2
            self.image.blit(msg, (x, y))

            
    
    @staticmethod
    def rest_area(x, y, rest_width, level):
        return Platform(x, y, rest_width, GREEN, rest_area = level)

    @property
    def top(self):
        return self.rect.top

    @property
    def topright(self):
        return self.rect.topright

    @property
    def bounds(self):
        return self.rect.left, self.rect.right

    @property
    def right(self):
        return self.rect.right
    
    @property
    def left(self):
        return self.rect.left
    
    def __str__(self):
        if self.is_rest_area:
            return f'Rest Area({self.left}, {self.right})'
        return f'Platform({self.left}, {self.right})'
        # return f'Platform({self.rect.left}, {self.rect.top}, {self.rect.width}, {self.rect.height})'
    
    def update(self, screen : pg.Surface, speed = 10):
        self.rect.move_ip((-speed, 0))
        if self.rect.right <= 0:
            self.rect.left = 800
            self.kill()
        else:
            screen.blit(self.image, self.rect)
    
    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)

class Player(pg.sprite.Sprite):

    gravity = 3.0
    speed = 0.0
    ground_height = 500
    is_floor = False
    
    # jumping
    jump_speed = 15.0
    is_holding = False
    max_hold_time = 0.3
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
    def top(self):
        return self.rect.top

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

    # BLUE, GREY = (60, 65, 186), (179, 178, 194) 
    
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Canabalt")

    clock = pg.time.Clock()
    font_style = pg.font.SysFont(None, 30)
    font_style_big = pg.font.SysFont("rockwell", 50)
    # font_style_big = pg.font.SysFont("verdana", 50)
    font_style_small = pg.font.SysFont(None, 20)

    rest_width = 300
    min_height = HEIGHT - 100
    platform_width = 300
    gap = 100

    def __init__(self):
        self.restart()

    def restart(self):
        # Player
        player_x = 100
        self.player = Player(player_x, 450, 20, WHITE)
        self.player_max_jump_height = self.player.jump_speed * self.player.max_hold_time
        self.score = 0

        # Platforms
        self.sprites = pg.sprite.Group()
        self.level = 1
        self.platform = Platform.rest_area(0, 450, self.rest_width, self.level)
        self.sprites.add(self.platform)
        self.platforms = [self.platform]
        self.construct_platforms()
        self.level += 1

        self.pause(0.1)

    def get_next_height(self, height):
        max_height = height - self.player_max_jump_height  # - because y increases downwards
        max_height = int(min(max_height * 0.7, self.min_height))
        return random.randrange(max_height, self.min_height, 10)
    
    def construct_platforms(self):
        """Returns non-overlapping platforms.
        Called when reaching a rest area from tick().
        Each platform is added to the sprite group."""
        # [(1.25, 0.5), (11.5, 0.75), (19.25, 0.75)]
        y = self.platforms[-1].top
        for i in range(3):
            y = self.get_next_height(y)
            self.platforms.append(Platform(self.platforms[-1].right + self.gap, y, self.platform_width, random_color()))
        self.platforms.append(Platform.rest_area(*self.platforms[-1].topright, self.rest_width, self.level + 1))
        

        # Determine overlap
        for i in range(len(self.platforms) - 1):
            assert self.platforms[i].right <= self.platforms[i+1].left, f'{self.platforms[i]} overlaps {self.platforms[i+1]}'
        
        self.sprites.add(self.platforms)

    def platform_transition(self):
        """Check if player has reached new platform and construct new platforms.
        Mutates self.platform and self.platforms when leaving and reaching new platform."""

        # Leaving current platform
        if self.platform and self.player.right > self.platform.right: 
            self.platform = None
            self.player.is_floor = False  # Let player fall
        
        # Reaching new platform
        if self.platform is None and self.player.right > self.platforms[0].left:
            platform = self.platforms[0]

            # Wall collision
            grace = 30
            if self.player.bottom > platform.top + grace:
                self.restart()
                return
            
            # Generate next level upon completing current level
            if platform.is_rest_area:
                self.construct_platforms()
                self.level += 1
                
                # self.platforms += self.construct_platforms()
            
            self.platform = self.platforms.pop(0)

    def tick(self):
        self.process_events()

        # Drawing player, platforms and score
        self.screen.fill(BLACK)

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
            if self.player.top > HEIGHT:
                self.restart()
                return

        self.player.draw(self.screen)

        # Draw score
        self.score += 1
        msg = self.font_style_big.render(f'{self.score} m', True, GREY)
        self.screen.blit(msg, (WIDTH - msg.get_width() - 20, 20))
        
        pg.display.update()
        self.clock.tick(FPS)
    
    def debug(self, string):
        msg = self.font_style_big.render(string, True, GREY)
        self.screen.blit(msg, (20, 20))
    
    def pause(self, time):
        # pause for time seconds
        start = pg.time.get_ticks()
        while pg.time.get_ticks() - start < time * 1000:
            self.process_events()
            self.clock.tick(FPS)
        

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
                elif event.key == pg.K_RETURN:
                    print()
                    for platform in self.platforms:
                        print(platform)
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
                    
                
def random_color():
    return (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))    
                
if __name__ == "__main__":
    game = Game()
    
    while True:
        game.tick()