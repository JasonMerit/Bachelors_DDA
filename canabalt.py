import pygame as pg
from pygame.color import Color
import numpy as np
import random
import os
from math import sqrt

from config import *

random.seed(SEED)
np.random.seed(SEED)

def blitRotate(surf, image, topleft, angle):
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

class Platform(pg.sprite.Sprite):
    
    def __init__(self, x, y, width, color, image : pg.surface.Surface, rest_area = 0):
        pg.sprite.Sprite.__init__(self)
        self.is_rest_area = rest_area  # Flag for level completion
        # self.image = pg.Surface((width, HEIGHT-y)).convert_alpha()
        self.image = image.copy()
        self.image.fill(color, special_flags=3)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        if rest_area:
            font = pg.font.SysFont("rockwell", 50)
            msg = font.render(f"LEVEL {rest_area}", True, GREY)
            x = (width - msg.get_width()) / 2
            y = (HEIGHT-y - msg.get_height()) / 2
            self.image.blit(msg, (x, y))
    
    @staticmethod
    def rest_area(x, y, rest_width, image, level):
        return Platform(x, y, rest_width, GREEN, image, rest_area = level)

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
    
    def update(self, screen : pg.Surface, speed):
        self.rect.move_ip((-speed, 0))
        if self.rect.right <= 0:
            self.rect.left = 800
            self.kill()
        elif self.rect.left < WIDTH:
            screen.blit(self.image, self.rect)
    
    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)

class Player(pg.sprite.Sprite):
    gravity = 2
    speed = 0
    is_floor = False
    
    # jumping
    jump_speed = 15
    is_holding = False
    max_hold_frames = 10
    hold_timer = 0
    jump_threshold = 10
    angle = 0
    angle_speed = 0
    rotations = 2

    # pre computations for physics constraints
    max_jump_height = jump_speed * max_hold_frames + 0.5 * jump_speed ** 2 / gravity
    up_time = jump_speed / gravity + max_hold_frames  # Increasing position time
    fly_time = lambda self, delta_y: self.up_time + sqrt(2 * delta_y / self.gravity)
    
    def __init__(self, x, y, size=20, color=WHITE):
        pg.sprite.Sprite.__init__(self)
        size = 30
        self.image = pg.Surface((size, size)).convert_alpha()
        self.image.fill(color)        
        # add shade to image
        shade = (0, 0, 0, 100)
        line_width = size // 8

        # horinzontal
        shadow = pg.Surface((size, line_width)).convert_alpha()
        shadow.fill(shade)
        self.image.blit(shadow, (0, 0))
        self.image.blit(shadow, (0, size - line_width))

        # Vertical
        shadow = pg.Surface((line_width, size - 2 * line_width)).convert_alpha()
        shadow.fill(shade)
        self.image.blit(shadow, (0, line_width))
        self.image.blit(shadow, (size - line_width, line_width))

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
            if event.key == pg.K_SPACE and self.is_floor:
                self.is_holding = True
                self.hold_frames = 0.0
                self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE:
                self.is_holding = False
    kek = 0
    def update(self):
        # Apply gravity if not on floor
        if not self.is_floor:  
            # Holding jump
            if self.is_holding:
                self.hold_frames += 1
                if self.hold_frames >= self.max_hold_frames:
                    self.is_holding = False
            else:
                self.speed += self.gravity

            # Move player
            self.rect.move_ip((0, self.speed))  

    
    def draw(self, screen):
        # Rotate player
        self.angle += self.angle_speed
        blitRotate(screen, self.image, self.rect.topleft, -self.angle)
        # screen.blit(self.image, self.rect)
    
    def jump(self):
        self.speed = -self.jump_speed
        # self.is_floor = False
        self.fall()
    
    def fall(self):
        self.is_floor = False
        
        d = self.jump_speed ** 2 + 2 * self.gravity * self.jump_speed * self.max_hold_frames
        t = (self.jump_speed + sqrt(d)) / self.gravity + self.max_hold_frames
        omega = self.rotations * 90 / t
        # d = self.jump_speed ** 2 + 2 * self.gravity * (self.rect.bottom - self.max_jump_height)
        self.angle_speed = omega

        # self.angle_speed = 5

    def floor_collision(self, height):
        if self.rect.bottom > height:  
            self.rect.bottom = height
            self.is_floor = True
            self.speed = 0.0
            self.angle = 0
            self.angle_speed = 0
    
class Obstacle(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
    
    def update(self, screen : pg.Surface, speed):
        self.rect.move_ip((-speed, 0))
        if self.rect.right <= 0:
            self.rect.left = 800
            self.kill()
        elif self.rect.left < WIDTH:
            screen.blit(self.image, self.rect)

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

    scroll_speed = 5
    rest_width = 300
    min_height, max_height = HEIGHT - 100, 100
    min_gap = 50
    platform_width = 300 if not FLAT else 100000

    # Platform
    platform_image = pg.Surface((platform_width, HEIGHT)).convert_alpha()
    platform_image.fill((255, 255, 255))

    shade = (0, 0, 0, 100)
    line_width = 15
    shadow = pg.Surface((platform_width, line_width)).convert_alpha()
    shadow.fill(shade)
    platform_image.blit(shadow, (0, 0))

    shadow = pg.Surface((line_width, HEIGHT)).convert_alpha()
    shadow.fill(shade)
    platform_image.blit(shadow, (0, line_width))
    platform_image.blit(shadow, (platform_width - line_width, line_width))

    # Obstacle
    obstacle_density = 0.2
    size = 30
    obstacle_image = pg.surface.Surface((size, size))
    obstacle_image.fill(RED)
    pg.draw.line(obstacle_image, YELLOW, (0, 0), (size, size), 3)
    pg.draw.line(obstacle_image, YELLOW, (0, size), (size, 0), 3)

    def __init__(self):
        self.restart()

    def restart(self):
        self.score = 0
        self.level = 1

        # Player
        player_x = 100
        self.player = Player(player_x, 450, 20, WHITE)
        self.player_max_jump_height = self.player.jump_speed * self.player.max_hold_frames

        # Sprite groups
        self.platform_sprites = pg.sprite.Group()
        self.obstacle_sprites = pg.sprite.Group()
        self.background_sprites = pg.sprite.Group()

        # Platforms
        self.platform = Platform.rest_area(player_x, 450, self.rest_width, self.platform_image, self.level)
        self.level += 1
        self.platform_sprites.add(self.platform)
        self.platforms = [self.platform]
        self.construct_platforms()

        background = [Platform(100 + i*500, HEIGHT // 2, 40, random_color(), self.platform_image) for i in range(10)]
        self.background_sprites.add(background)


        self.pause(0.1)

    def get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        # print(f'---- {self.level} ----')
        max_y = max(int(y - 0.7 * self.player.max_jump_height), self.max_height)  # 0.7 grace
        new_y = random.randrange(max_y, self.min_height)

        max_x = int(self.player.fly_time(new_y - max_y) * self.scroll_speed * 0.7)  # 0.7 grace
        new_x = x + random.randrange(self.min_gap, max_x)

        return new_x, new_y
    
    def construct_platforms(self, count=5):
        """Extends platforms.
        Called when reaching a rest area from tick().
        Each platform is added to the sprite group."""
        # [(1.25, 0.5), (11.5, 0.75), (19.25, 0.75)]
      
        x, y = self.platforms[-1].topright
        for _ in range(count):
            x, y = self.get_next_position(*self.platforms[-1].topright)
            self.platforms.append(Platform(x, y, self.platform_width, random_color(), self.platform_image))
            # self.platforms.append(Platform(x, y, self.platform_width, random_color()))

            # Add obstacle
            if random.random() < self.obstacle_density:
                self.obstacle_sprites.add(Obstacle(x + self.platform_width // 2, y, self.obstacle_image))
                # self.obstacle_sprites.add(Obstacle(x + self.platform_width // 2, y, self.obstacle_size))
        self.platforms.append(Platform.rest_area(*self.platforms[-1].topright, self.rest_width, self.platform_image, self.level + 1))

        # Assert no overlap
        for i in range(len(self.platforms) - 1):
            assert self.platforms[i].right <= self.platforms[i+1].left, f'{self.platforms[i]} overlaps {self.platforms[i+1]}'
        
        self.platform_sprites.add(self.platforms)

    def platform_transition(self):
        """Check if player has reached new platform and construct new platforms.
        Mutates self.platform and self.platforms when leaving and reaching new platform.
        Returns true if died"""

        # Leaving current platform
        if self.platform and self.player.right - 20 > self.platform.right: 
            self.platform = None
            self.player.fall()  # Let player fall
        
        # Reaching new platform
        if self.platform is None and self.player.right > self.platforms[0].left:
            platform = self.platforms[0]

            # Wall collision
            grace = 30
            if not GOD and self.player.bottom > platform.top + grace:
                self.restart()
                return True
            
            # Generate next level upon completing current level
            if platform.is_rest_area:
                self.construct_platforms()
                self.level += 1
                
            self.platform = self.platforms.pop(0)

    base_color = BLACK
    next_color = BLUE
    step = 1
    max_step = 500
    def draw_background(self):
        # Draw the sky
        self.step += 1
        if self.step < self.max_step:
            color = [x + (((y-x)/self.max_step)*self.step) for x, y in zip(Color(self.base_color), Color(self.next_color))]
        else:
            self.step = 1
            self.base_color = BLACK if self.base_color == BLUE else BLUE
            self.next_color = BLACK if self.next_color == BLUE else BLUE
            color = self.base_color
        
        self.screen.fill(color)

    def tick(self):
        self.process_events()
        self.screen.fill(BLACK)
        self.background_sprites.update(self.screen, 2)
        # self.draw_background()

        # Move objects (wait to draw player until after collision check)
        self.player.update()
        self.platform_sprites.update(self.screen, self.scroll_speed)
        self.obstacle_sprites.update(self.screen, self.scroll_speed)

        # Check for new platform and wall collision
        if self.platform_transition():
            return  # Wall collision
        
        # Check for floor collision
        if self.platform:
            self.player.floor_collision(self.platform.top)

            # Check for obstacle collision
            if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
                self.restart()
                return
        else:
            # Check for off screen
            if not GOD and self.player.top > HEIGHT:
                self.restart()
                return

        self.player.draw(self.screen)

        # Draw score
        self.score += 1
        msg = self.font_style_big.render(f'{self.score} m', True, GREY)
        self.screen.blit(msg, (WIDTH - msg.get_width() - 20, 20))

        # Draw a line at player's max jump height
        # if self.platform:
        #     max_height = self.platform.top - self.player.max_jump_height
        #     pg.draw.line(self.screen, RED, (0, max_height), (WIDTH, max_height), 1)
        
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