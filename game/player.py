from typing import List
from math import sqrt, sin, cos, radians
from icecream import ic
from game.util import *
from game.config import Config
from game.entities import Platform, Slope, Obstacle

class Player():
    """x and y define position, representing the BOTTOM RIGHT corner of the player.
    Since platform uses TOP left corner, this allows for easy collision detection.
    TODO: replace with vector when dashing"""

    init_pos = Config.height // 10, 100
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

    def __init__(self):
        self.cleared_platforms = 0
        self._is_floor = True

    def reset(self, platforms : List[Platform], obstacles : List[Obstacle]):
        self.platforms = platforms
        self.current_platform, self.next_platform = platforms[:2]
        self.x, self.y = self.init_pos
        self.speed = 0
        self.is_floor = True
        self.angle = 0
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
        return self.x - self.size# + 15*(sin(radians(self.angle)) - cos(radians(self.angle)))

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
        if self.move() or self.collision():
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
            else:
                self.speed -= self.gravity
                # self.angle_speed = 100  # Rotate to simulate falling

            self.y += self.speed
            if self.top < 0:
                if Config.GOD:
                    self.y = Config.height
                return True

        # Traverise along slope
        elif self.current_platform and isinstance(self.current_platform, Slope):
            self.y += self.current_platform.dy
    
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
        if self.x > self.next_platform.left:  # Next platform reached
            if platform is None:  # Clear from previous platform
                platform = self.next_platform
                platform.outline()
                
                self.next_platform = self.platforms[self.platforms.index(platform) + 1]
                if self.is_floor is True:  # May already be jumping
                    self.is_floor = False
            
            else: # Gap smaller than player size (rare)
                # self._floor_check(platform)  # TODO: Check if neccesary (was before, because could fall below collision and collide with next plat)
                platform.outline(True)
                platform = self.next_platform
                platform.outline()
                self.next_platform = self.platforms[self.platforms.index(platform) + 1]
                if self._is_colliding(platform) is True:
                    return True
                self.is_floor = False  
        
        # Wall collision
        if platform and platform != self.current_platform:  # Changed platform
            if self._is_colliding(platform):
                if Config.GOD:
                    self.y = platform.top  # Assuming flat surface
                    self.is_floor = True
                    platform.outline(True)
                return True
        
        # Floor collision. Safe, because x is always within the platform
        if platform:
            self._floor_check(platform)
            if self._obstacle_collision(platform):
                return True
        
        # Check for obstacle collision
            # if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
            #     return True

        # Score tick
        if platform and self.current_platform != platform:
            # ic("__________")
            self.cleared_platforms += 1
        self.current_platform = platform
    
    def _is_colliding(self, platform):
        return self.y + Config.grace_add < platform.top
    
    def _obstacle_collision(self, platform):
        if platform.obstacle is None:
            return
        
        return self.left < platform.obstacle.right and \
               self.right > platform.obstacle.left and \
                self.y < platform.obstacle.top

    
    # keks = 0
    def _floor_check(self, platform: Platform):
        platform.offset_player(self)
