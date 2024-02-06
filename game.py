from config import *
import pygame as pg

import numpy as np
import random
import os
from math import sqrt

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, color, rest_area = 0, fog = None):
        pg.sprite.Sprite.__init__(self)
        self.is_rest_area = rest_area
        self.image = pg.Surface((width, HEIGHT)).convert_alpha()
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))
        pg.draw.rect(self.image, WHITE, self.rect, 0, 10)
        pg.draw.rect(self.image, SHADE, self.rect, 15, 10)

        self.rect.topleft = (x, y)
        self.image.fill(color, special_flags=3)

    @staticmethod
    def rest_area(x, y, level):
        return Platform(x, y, 300, GREEN, rest_area = level)

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
            self.kill()
        elif self.rect.left < WIDTH:
            screen.blit(self.image, self.rect)
    
    def move(self, dx, dy):
        self.rect.move_ip(dx, dy)
    
    def draw(self, screen):
        if self.rect.right <= 0:
            self.kill()
        elif self.rect.left < WIDTH:
            screen.blit(self.image, self.rect)
    
    def is_colliding(self, player):
        return self.rect.colliderect(player.rect)
    
class Game1():
    scroll_speed = 5
    rest_width = 300
    min_height, max_height = HEIGHT - 100, 100
    min_gap = 50
    platform_width = 300 if not FLAT else 100000
    obstacle_density = 0.2
    obstacle_size = 40
    deaths = -1

    def __init__(self):
        self.restart()
    
    def restart(self):
        self.deaths += 1
        self.score = 0
        self.level = 0

        pos = 100, 100
        self.player = Agent(*pos, 20, WHITE) if AGENT else Player(*pos, 20, WHITE)
        self.player_max_jump_height = self.player.jump_speed * self.player.max_hold_frames

        self.level += 1
        self.platforms = [Platform.rest_area(*pos, self.level)]
        self.construct_platforms()
        self.level += 1
        self.construct_platforms()
        self.level += 1
        self.platform = self.platforms.pop(0)
        print(f'{len(self.platforms)} platforms')
    
    def construct_platforms(self, count=5):
        """Extends platforms.
        Called when reaching a rest area from tick().
        Each platform is added to the sprite group."""
        # [(1.25, 0.5), (11.5, 0.75), (19.25, 0.75)]
        
        x, y = self.platforms[-1].topright
        for _ in range(count):
            x, y = self.get_next_position(*self.platforms[-1].topright)
            self.platforms.append(Platform(x, y, self.platform_width, random_color()))
            # self.platforms.append(Platform(x, y()))

            # Add obstacle
            if random.random() < self.obstacle_density:
                pass
                # self.obstacle_sprites.add(Obstacle(x + self.platform_width // 2, y, self.obstacle_image))
                # self.obstacle_sprites.add(Obstacle(x + self.platform_width // 2, y, self.obstacle_size))
        self.platforms.append(Platform.rest_area(*self.platforms[-1].topright, self.level + 1))

        # Assert no overlap
        for i in range(len(self.platforms) - 1):
            assert self.platforms[i].right <= self.platforms[i+1].left, f'{self.platforms[i]} overlaps {self.platforms[i+1]}'
        
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
    
    def tick(self):
        # Move objects (wait to draw player until after collision check)
        # obstacle = self.obstacle_sprites.sprites()[0] if self.obstacle_sprites else None
        # self.player.step(self.platform, self.platforms[0], obstacle)
        self.player.update()
        for platform in self.platforms:
            platform.move(-self.scroll_speed, 0)
        if self.platform:
            self.platform.move(-self.scroll_speed, 0)
        # self.platform_sprites.update(self.screen, self.scroll_speed)
        # self.obstacle_sprites.update(self.screen, self.scroll_speed)

        # Check for new platform and wall collision
        if self.platform_transition():
            self.restart()
            return True # Wall collision
        
        # Check for floor collision
        if self.platform:
            self.player.floor_collision(self.platform.top)

            # Check for obstacle collision
            # if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
            #     self.restart()
            #     return
        else:
            # Check for off screen
            if not GOD and self.player.top > HEIGHT:
                self.restart()
                return True
    
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

class PlatformSprite(Platform):
    _keks = 0

    def __init__(self, platform):
        self.topleft = platform.topleft
        self.width = platform.width

    def add_internal(self, lol):
        self._keks += 1
    
    def remove_internal(self, lol):
        self._keks -= 1
    
    def update(self):
        print(self._keks)

class Display(Game1):
    pg.init()

    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Canabalt")

    clock = pg.time.Clock()
    font_style = pg.font.SysFont(None, 30)
    font_style_big = pg.font.SysFont("rockwell", 50)
    font_style_small = pg.font.SysFont(None, 20)

    platform_sprites = pg.sprite.Group()
    obstacle_sprites = pg.sprite.Group()
    background_sprites = pg.sprite.Group()

    # Obstacle
    # obstacle_density = 0.2
    # size = 40
    # obstacle_image = pg.surface.Surface((size, size)).convert_alpha()
    # obstacle_image.set_colorkey(COLOR_KEY)
    # obstacle_image.fill(COLOR_KEY)
    # pg.draw.polygon(obstacle_image, YELLOW , [(0, size), (size // 2, 0), (size, size)])
    # msg = pg.font.SysFont("rockwell", 40).render('!', True, BLACK)
    # obstacle_image.blit(msg, (15, 0))

    def __init__(self):
        # add a listener to self.platforms
        
        self.restart()
    
    def restart(self):
        super().restart()

        self.platform_sprites.empty()
        self.platform_sprites.add(self.platform)
        # self.obstacle_sprites.empty()
        # self.background_sprites.empty()
        # self.construct_platforms = self.construct_platforms
    
    # def platforms_updated(self, platforms):
    #     self.platform_sprites.empty()
    #     self.platform_sprites.add(platforms + [self.platform])
    
    # redefine game.construct_platforms to add 
    # new platforms to self.platform_sprites

    def tick(self):
        if super().tick():
            return
        
        self.process_events()
        # self.draw_background()
        self.screen.fill(BLACK)

        # Determine if game has added new platforms
        for platform in self.platforms[:2]:
            platform.draw(self.screen)
        if self.platform:
            self.platform.draw(self.screen)
        # self.platform_sprites.update(self.screen, self.scroll_speed)
        self.player.draw(self.screen)

        pg.display.update()
        self.clock.tick(FPS)

    def process_events(self):
        global FPS
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
                    self.restart()
                elif event.key == pg.K_RETURN:
                    self.kek += [1]

                elif event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL:
                    path = "assets/screenshots"
                    pg.image.save(self.screen, f"{path}/{len(os.listdir(path))}.png")
                elif event.key == pg.K_DOWN:
                    
                    FPS -= 60
                    FPS = max(10, FPS)
                    # change screen caption
                    pg.display.set_caption(f"Canabalt - {FPS}")
                elif event.key == pg.K_UP:
                    
                    FPS += 60
                    FPS = min(1000, FPS)
                    pg.display.set_caption(f"Canabalt - {FPS}")
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

    base_color = BLACK
    next_color = BLUE
    step = 1
    max_step = 1000
    def draw_background(self):
        # Draw the sky
        self.step += 1
        if self.step < self.max_step:
            color = lerp_color(self.base_color, self.next_color, self.step / self.max_step)
        else:
            self.step = 1
            self.base_color = BLACK if self.base_color == BLUE else BLUE
            self.next_color = BLACK if self.next_color == BLUE else BLUE
            color = self.base_color
        
        self.screen.fill(color)
        # self.background_sprites.update(self.screen, 2)

class Game():
    
    def __init__(self):
        self.restart()

    def restart(self):
        pass


def main():
    game = Display() if GAME else Game()
    while True:
        game.tick()

if __name__ == "__main__":
    main()