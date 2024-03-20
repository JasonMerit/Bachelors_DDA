import pygame as pg
from pygame.color import Color
from pygame.surface import Surface
from pygame.sprite import Sprite, Group
import random, os, time, math

from game.endless_runner import EndlessRunner, Platform, Player
from game.config import Config

from math import sqrt

FONT = "rockwell"
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".TTF"):
            FONT = os.path.join(root, file)[2:]
            break
        
def blit_rotate(surf, image, topleft, angle):
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

def random_color():
    return (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))    

def lerp_color(color1, color2, t):
    return [x + (y-x) * t for x, y in zip(Color(color1), Color(color2))]

class Display(EndlessRunner):
    
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pg.display.set_caption(Config.caption)

        self.clock = pg.time.Clock()
        # font_style = pg.font.SysFont(None, 30)
        # font_big = pg.font.SysFont("rockwell", 50)
        self.font_big = pg.font.Font(FONT, 50)
        # font_big = pg.font.Font("ROCK.TTF", 50)
        # font_style_small = pg.font.SysFont(None, 20)
        self.sprites = Group()
        super().__init__()
    
    def reset(self, seed=None):
        self.sprites.empty()
        self.sprites.add(self.player)
        super().reset(seed)
    
    def close(self):
        pg.quit()
    
    def render(self, state=None):
        self.screen.fill(Config.BLACK)
        self.sprites.update(self.screen)
        
        # Draw score
        self.score += 1
        msg = self.font_big.render(f'{self.score} m', True, Config.GREY)
        self.screen.blit(msg, (Config.WIDTH - msg.get_width() - 20, 20))

        # Draw death count
        msg = self.font_big.render(f'{self.deaths} deaths', True, Config.GREY)
        self.screen.blit(msg, (20, 20))

        # Draw player.cleared_platforms
        msg = self.font_big.render(f'{self.player.cleared_platforms} cleared', True, Config.GREY)
        self.screen.blit(msg, (Config.WIDTH - msg.get_width() - 20, 70))

        # Draw FPS
        msg = self.font_big.render(f'{Config.FPS}', True, Config.GREY)
        self.screen.blit(msg, (Config.WIDTH // 2, 20))
        
        # Draw player trajectory
        self.player.draw_curve(self.screen, self.platforms[:2])

        # Draw state
        if state is not None:
            x1, y1, x2, y2 = state.astype(int)
            pg.draw.circle(self.screen, Config.WHITE, (x1, Config.HEIGHT - y1), 5)
            pg.draw.circle(self.screen, Config.WHITE, (x2, Config.HEIGHT - y2), 5)

        pg.display.flip()
        self.clock.tick(Config.FPS)
    
    def construct_player(self):
        return PlayerSprite()
    
    def construct_platform(self, topleft, width=300, level=0):
        # platform = super().construct_platform(topleft, width, level=level)
        color = Config.GREEN if level else random_color()
        platform_sprite = PlatformSprite(topleft, width, color, level=level)
        self.sprites.add(platform_sprite)
        return platform_sprite

    def remove_platform(self):
        platform = self.platforms.pop(0)
        self.sprites.remove(platform)


class PlatformSprite(Platform, Sprite):

    def __init__(self, topleft, width, color, level=0):
        super().__init__(topleft, width, level=level)
        Sprite.__init__(self)
        
        self.font = pg.font.Font(FONT, 50)

        # self.surface = pg.Surface((platform.width, HEIGHT))
        # t0 = time.time()
        self.surface = pg.Surface((width, Config.HEIGHT))
        # self.surface = pg.Surface((platform.width, HEIGHT)).convert()
        # self.surface = pg.Surface((platform.width, HEIGHT)).convert_alpha()
        # print(f'Time: {time.time() - t0:.2f}')
        self.rect = self.surface.get_rect()
        self.surface.set_colorkey((0, 0, 0))
        pg.draw.rect(self.surface, Config.WHITE, self.rect, 0, 10)
        shade_color = lerp_color(color, Config.WHITE, 0.4)
        pg.draw.rect(self.surface, shade_color, self.rect, 15, 10)
        # pg.draw.rect(self.surface, SHADE, self.rect, 15, 10)

        self.surface.fill(color, special_flags=3)  # 0.63

        if self.is_rest_area:
            # font = pg.font.Font("ROCK.TTF", 50)
            # font = pg.font.SysFont("rockwell", 50)
            msg = self.font.render(f"LEVEL {self.is_rest_area}", True, Config.GREY)
            x = (msg.get_width() - self.width // 4) / 2  
            y = (self.top - msg.get_height()) / 2
            self.surface.blit(msg, (x, y))

        # Copy surface and add red outline
        self.outline_surface = self.surface.copy()
        pg.draw.rect(self.outline_surface, Config.RED, self.rect, 2, 10)

            

    def update(self, screen : Surface):
        screen.blit(self.surface, (self.x, Config.HEIGHT - self.top))
    
    def outline(self, invert=False):
        if invert:
            self.surface = self.outline_surface
        else:
            temp = self.surface
            self.surface = self.outline_surface
            self.outline_surface = temp


import numpy as np
class PlayerSprite(Player, Sprite):
    
    def __init__(self):
        Sprite .__init__(self)
        super().__init__()
        self.surface = Surface((self.size, self.size)).convert_alpha()
        self.surface.fill(Config.WHITE)        
        
        # add shade to image
        shade = (0, 0, 0, 100)
        line_width = self.size // 8
        
        # Horizontal
        shadow = Surface((self.size, line_width)).convert_alpha()
        shadow.fill(shade)
        self.surface.blit(shadow, (0, 0))
        self.surface.blit(shadow, (0, self.size - line_width))

        # Vertical
        shadow = Surface((line_width, self.size - 2 * line_width)).convert_alpha()
        shadow.fill(shade)
        self.surface.blit(shadow, (0, line_width))
        self.surface.blit(shadow, (self.size - line_width, line_width))

    
    @property
    def topleft(self):
        return (self.x - self.size, Config.HEIGHT - self.y - self.size)

    def update(self, screen : Surface):
        if self.angle_speed == 0:
            screen.blit(self.surface, self.topleft)
        else:
            self.angle += self.angle_speed
            blit_rotate(screen, self.surface, self.topleft, -self.angle)
        pg.draw.rect(screen, Config.RED, (*self.topleft, self.size, self.size), 2)
    
    def _compute_omega(self):
        # First phase constant speed
        # h = v_0t_1 
        v, t1 = self.jump_speed, self.max_hold_frames
        h = v*t1
        
        # Second phase constant acceleration
        # y = h + v_1t_2 - 1/2gt_2^2 = 0
        g = self.gravity
        t2 = (v + sqrt(v**2 + 2 * g * h)) / g  # positive root

        t = t1 + t2
        omega = 90 / t
        self.angle_speed = omega

        # d = self.jump_speed ** 2 + 2 * self.gravity * self.jump_speed * self.max_hold_frames
        # tom = (self.jump_speed + sqrt(d)) / self.gravity + self.max_hold_frames  # time of flight
        # omega = self.rotations * 90 / tom
        # self.angle_speed = omega

    def draw_curve(self, screen : Surface, platforms : list):
        if self.is_floor is True:
            return

        g = self.gravity
        v = self.speed  # Current y-speed
        h = self.y  # Current height

        ### y(t) = h + vt - 1/2gt^2 = b
        b0 = platforms[0].top  # Destination height
        d = v**2 + 2 * g * (h - b0)
        if d > 0:
            t = (v + sqrt(d)) / g  # Can always reach current platform 

        # Maybe next platform will be reached
        b1 = platforms[1].top  
        d = v**2 + 2 * g * (h - b1) 
        if d > 0:
            t1 = (v + sqrt(d)) / g  # positive root
            if self.x + t1 * Platform.scroll_speed >= self.platforms[1].left:  # If player reaches the next platform
                t = t1
        try:
            T = np.linspace(0, t, 300)
            X = Platform.scroll_speed * T + self.x
            Y = Config.HEIGHT - (h + v * T - 0.5 * g * T ** 2)
            for x, y in zip(X, Y):
                pg.draw.circle(screen, Config.BLUE, (x, y), 2)
        except UnboundLocalError:  # If fell without jumping
            pass
    
    def change_color(self, is_floor: bool):
        if is_floor:
            self.surface.fill(Config.WHITE)
        else:
            self.surface.fill(Config.BLUE)

    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and self.is_floor:
                self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE and not self.is_floor:
                self.is_holding = False  # Release jump from keyup
                # if self.is_falling is False:
                #     self._fall()

