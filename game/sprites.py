from math import sqrt, radians

import pygame as pg
from pygame.surface import Surface
from pygame.sprite import Sprite
from pygame.color import Color

from game.endless_runner import Platform, Flat, Slope, Player, Obstacle
from game.config import Config

def blit_rotate(surf, image, topleft, angle):
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    surf.blit(rotated_image, new_rect.topleft)

# def random_color():
#     return (random.randint(100, 150), random.randint(100, 150), random.randint(100, 150))    

def lerp_color(color1, color2, t):
    return Color([x + (y-x) * t for x, y in zip(Color(color1), Color(color2))])

class RectSprite(Sprite):
    # Platform
    x : int
    top : int

    # Sprite
    draw_top : int

    def __init__(self):
        super().__init__()
        self.surface.set_colorkey((0, 0, 0))
        
        # Copy surface and add red outline
        self.outline_surface = self.surface.copy()
        pg.draw.rect(self.outline_surface, Config.RED, self.surface.get_rect(), 2, 10)

        

    def update(self, screen : Surface, debug: bool):
        screen.blit(self.surface, (self.x, self.draw_top))
    
    def outline(self, invert=False):
        if invert:
            self.surface = self.outline_surface
        else:
            temp = self.surface
            self.surface = self.outline_surface
            self.outline_surface = temp

class FlatSprite(Flat, RectSprite):
    def __init__(self, topleft, width, color):
        super().__init__(topleft, width)
        rounding = 10

        height = Config.height
        self.surface = pg.Surface((width, height))
        rect = self.surface.get_rect()
        pg.draw.rect(self.surface, color, rect)

        # height = 100
        # self.surface = pg.Surface((width, height))
        # rect = self.surface.get_rect()
        # pg.draw.rect(self.surface, color, rect, border_radius=rounding)
        # shade_color = lerp_color(color, Config.BLACK, 0.4)
        # pg.draw.rect(self.surface, shade_color, rect, 15, rounding)

        self.draw_top = Config.height - self.top

        RectSprite.__init__(self)

from math import tan, radians, cos, sin
class SlopeSprite(Slope, RectSprite):
    def __init__(self, topleft, width, color):
        super().__init__(topleft, width)
        rounding = 10
        height = 100
        tip = width * self.slope  # Slope height
        self.surface = pg.Surface((width, height + tip))  # Extra height for slope
        
        hypotenuse = width / cos(radians(self.angle))
        
        self.surface = pg.Surface((hypotenuse, height))
        rect = self.surface.get_rect()
        pg.draw.rect(self.surface, color, rect, border_radius=rounding)
        shade_color = lerp_color(color, Config.BLACK, 0.4)
        pg.draw.rect(self.surface, shade_color, rect, 15, rounding)
        
        ### Do some rotation
        rotated_image = pg.transform.rotate(self.surface, self.angle)
        pos = (self.x, Config.height - self.top)
        image_rect = self.surface.get_rect(topleft = pos)
        offset_center_to_pivot = pg.math.Vector2(pos) - image_rect.center
        rotated_offset = offset_center_to_pivot.rotate(-self.angle)
        rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
        rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
        
        self.surface = rotated_image
        self.draw_top = rotated_image_rect.top

        # Reverse y-axis and offset
        tip = width * self.slope  # Slope height
        self.draw_top = Config.height - self.top - tip

        RectSprite.__init__(self)

class _SlopeSprite(Slope, RectSprite):
    def __init__(self, topleft, width, color):
        super().__init__(topleft, width)
        rounding = 10
        height = Config.height
        # tip = width * self.slope  # Slope height
        tip = width * abs(self.slope)  # Slope height
        self.surface = pg.Surface((width, height + tip))  # Extra height for slope
        
        box_rect = pg.Rect(0, tip, width, height)
        pg.draw.rect(self.surface, color, box_rect)
        # shade_color = lerp_color(color, Config.BLACK, 0.4)
        # pg.draw.rect(self.surface, shade_color, box_rect, 15)
        points = [(0, tip), (width, tip), (width, 0)] if self.slope > 0 else [(0, 0), (width, tip), (0, tip)]
        # draw rounded triangle
        pg.draw.polygon(self.surface, color, points)
        # pg.draw.polygon(self.surface, shade_color, points, 15)

        # Reverse y-axis and offset
        tip = width * self.slope * int(self.angle > 0)  # Slope height
        self.draw_top = Config.height - self.top - tip

        RectSprite.__init__(self)


class ObstacleSprite(Obstacle, RectSprite):
    def __init__(self, platform):
        super().__init__(platform)
        self.surface = pg.Surface((self.width, self.height))
        rect = self.surface.get_rect()
        pg.draw.rect(self.surface, (255, 0, 0), rect)
        self.draw_top = Config.height - self.top
        
        RectSprite.__init__(self)

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
        return (self.x - self.size, Config.height - self.y - self.size)

    def update(self, screen : Surface, debug):
        if self.angle_speed == 0 and self.angle == 0:
            screen.blit(self.surface, self.topleft)
        else:
            self.angle += self.angle_speed
            blit_rotate(screen, self.surface, self.topleft, -self.angle)
        
        # if debug:
            # red rectangle around player
            # pg.draw.rect(screen, Config.RED, (*self.topleft, self.size, self.size), 2)
    
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
            Y = Config.height - (h + v * T - 0.5 * g * T ** 2)
            for x, y in zip(X, Y):
                pg.draw.circle(screen, Config.BLUE, (x, y), 2)
            pg.draw.circle(screen, Config.RED, (X[-1], Y[-1]), 5)  # Last point

        except UnboundLocalError:  # If fell without jumping
            pass
    
    def change_color(self, is_floor: bool):
        pass
        # if is_floor:
        #     self.surface.fill(Config.WHITE)
        # else:
        #     self.surface.fill(Config.BLUE)

    def process_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE and self.is_floor:
                self.jump()
                
        elif event.type == pg.KEYUP:
            if event.key == pg.K_SPACE and not self.is_floor:
                self.is_holding = False  # Release jump from keyup
