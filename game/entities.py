from typing import List
from math import sqrt

from game.util import *
from game.config import Config

class Platform():
    """x and top define position, representing the top left corner of the platform.
    """
    scroll_speed = 5
    rest_area_width = 300
    id = 0
    def __init__(self, topleft, width, level = 0):
        self.x, self.top = topleft
        self.width = width
        self.is_rest_area = level
        Platform.id += 1
        self.id = Platform.id
    
    @classmethod
    def rest_area(cls, topleft, level):
        return cls(topleft, cls.rest_area_width, level)
    
    @property 
    def topleft(self):
        return (self.x, self.top)    
    
    @property
    def topright(self):
        return (self.x + self.width, self.top)

    @property
    def right(self):
        return self.x + self.width

    @property
    def left(self):
        return self.x
    
    def move(self):
        self.x -= self.scroll_speed
    
    def outline(self, invert=False):
        pass # for debugging

    def __repr__(self):
        return f"Platform: {self.id}, {self.topleft}, {self.width}"

class Player():
    """x and y define position, representing the BOTTOM RIGHT corner of the player.
    Since platform uses TOP left corner, this allows for easy collision detection.
    TODO: replace with vector when dashing"""
    # platforms = []  # Set by EndlessRunner
    # current_platform = None
    # next_platform = None

    init_pos = Config.WIDTH // 10, 100
    gravity = 2
    size = 30
    
    # jumping
    jump_speed = 15
    is_holding = False
    max_hold_frames = 10
    jump_times = [max_hold_frames, max_hold_frames // 2, 0]  # 42 is for no jump, but index is never 0
    hold_frames = 0
    jump_threshold = 10

    # Rotation (visual)
    angle = 0
    angle_speed = 0
    rotations = 2

    # pre computations for physics constraints
    # max_jump_height = jump_speed * max_hold_frames + 0.5 * jump_speed ** 2 / gravity
    # up_time = jump_speed / gravity + max_hold_frames  # Increasing position time
    # fly_time = lambda self, delta_y: self.up_time + sqrt(2 * delta_y / self.gravity)

    def __init__(self):
        self.cleared_platforms = 0
        self._is_floor = True

    def reset(self, platforms : List[Platform]):
        self.platforms = platforms
        self.current_platform, self.next_platform = platforms[:2]
        self.x, self.y = self.init_pos
        self.speed = 0
        self.is_floor = True
        self.is_holding = False
        self.cleared_platforms = 0
    
    @property
    def pos(self):
        return self.x, self.y

    @property
    def right(self):
        return self.x
    
    @property
    def left(self):
        return self.x - self.size

    @property
    def top(self):
        return self.y + self.size
    
    @property 
    def is_floor(self):
        return self._is_floor
    
    @is_floor.setter
    def is_floor(self, value):
        self._is_floor = value
        self.change_color(value)
        if value is True:
            self.speed = 0
            self.angle = 0  # Set to slope of platform
            self.angle_speed = 0
            self.is_falling = False
        elif value is False:
            self.angle_speed = 5  # Rotate to simulate falling
    
    def change_color(self, is_floor: bool):
        pass # for debugging

    def draw_curve(self, screen, platformss):
        pass

    def jump(self, hold_frames=None):
        """Jump and hold jump if long is True. 
        Written this way to account for agent's jump.
        
        :param hold_frames: Number of frames to hold jump
        """
        self.is_holding = True
        if hold_frames is None:  # Human player
            self.hold_frames = 0
        else:
            self.hold_frames = self.jump_times[hold_frames]  
        self.speed = self.jump_speed
        self.is_floor = False
    
    def jump_release(self):
        self.is_holding = False

    def tick(self):
        
        if self.move() is True or self.collision() is True:
            return True
        return False
        
    def move(self):
        # # Apply gravity if not on floor
        if not self.is_floor:  
            # Holding jump
            if self.is_holding:
                self.hold_frames += 1
                if self.hold_frames >= self.max_hold_frames:
                    self.is_holding = False  # Release jump from expired hold
                    # self._fall()
            else:
                self.speed -= self.gravity
                # self.angle_speed = 100  # Rotate to simulate falling

            self.y += self.speed
            if self.top < 0:
                if not Config.GOD:
                    if Config.VERBOSE:
                        print("OFF SCREEN")
                    return True
                self.y = Config.HEIGHT
    
    def collision(self):
        """Check for collision with platforms and obstacles.
        Mutates current_platform and next_platform."""
        platform = self.current_platform

        # Leaving current platform
        if platform and self.left > platform.right:  
            # self.next_platform = self.platforms[self.platforms.index(platform) + 1]
            platform.outline(True)
            # self._floor_check(platform)  # Rare occurence

            platform = None
            if self.is_floor is True:  # May already be jumping
                self.is_floor = False  

        # Reaching next platform
        if self.x > self.next_platform.left: # and self.is_floor is False:
            if platform is None:  
                platform = self.next_platform
                platform.outline()
                self.next_platform = self.platforms[self.platforms.index(platform) + 1]
                if self.is_floor is True:  # May already be jumping
                    self.is_floor = False
            
            else: # Player still atop of a platform: __|  | case
                self._floor_check(platform)
                platform.outline(True)
                platform = self.next_platform
                platform.outline()
                self.next_platform = self.platforms[self.platforms.index(platform) + 1]
                if self._collide_with(platform) is True:
                    assert platform.rest_area == 0, "Collision with rest area :("
                    return True
        
        # Wall collision
        if platform and platform != self.current_platform:  # Changed platform
            if self._collide_with(platform) is True:
                return True
        
        # Floor collision. Safe, because x is always within the platform
        if platform:
            if self.y < platform.top:  
                self.y = platform.top
                self.is_floor = True
        
        # Check for obstacle collision
            # if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
            #     return True

        if platform and self.current_platform != platform:
            self.cleared_platforms += 1
        self.current_platform = platform
    
    def _collide_with(self, platform):
        if self.y + Config.grace_add < platform.top:
            if not Config.GOD:
                if Config.VERBOSE:
                    print("Wall collision", platform)
                return True
            self.y = platform.top  # Assuming flat surface
    
    def _floor_check(self, platform):
        if self.y < platform.top:  
            self.y = platform.top
            self.is_floor = True

