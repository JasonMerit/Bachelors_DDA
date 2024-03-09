import random
import numpy as np
from math import sqrt
import typing

from config import *

class Platform():
    """x and top define position, representing the top left corner of the platform.
    """
    scroll_speed = 5
    rest_area_width = 300
    def __init__(self, topleft, width, level = 0):
        self.x, self.top = topleft
        self.width = width
        self.is_rest_area = level
    
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

class Player():
    """x and y define position, representing the BOTTOM left corner of the player.
    Since platform uses TOP left corner, this allows for easy collision detection.
    TODO: replace with vector when dashing"""
    gravity = 2
    speed = 0
    is_floor = True
    
    # jumping
    jump_speed = 15
    is_holding = False
    max_hold_frames = 10
    jump_times = [42, max_hold_frames, max_hold_frames // 2, 0]  # 42 is for no jump, but index is never 0
    hold_frames = 0
    jump_threshold = 10

    # Rotation (visual)
    angle = 0
    angle_speed = 0
    rotations = 2

    # pre computations for physics constraints
    max_jump_height = jump_speed * max_hold_frames + 0.5 * jump_speed ** 2 / gravity
    up_time = jump_speed / gravity + max_hold_frames  # Increasing position time
    fly_time = lambda self, delta_y: self.up_time + sqrt(2 * delta_y / self.gravity)

    def __init__(self, pos, size):
        self.x, self.y = pos
        self.size = size
    
    def reset(self):
        self.x, self.y = self.pos[0], 100
        self.speed = 0
        self.is_floor = True
        self.is_holding = False
        self.angle = 0
        self.angle_speed = 0
    
    @property
    def pos(self):
        return self.x, self.y

    @property
    def right(self):
        return self.x + self.size
    
    @property
    def left(self):
        return self.x
    
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
        # print(f'y: {self.y}')
    
    def jump(self, hold_frames=None):
        """Jump and hold jump if long is True. 
        Written this way to account for agent's jump."""
        self.is_holding = True
        if hold_frames is None:  # Human player
            self.hold_frames = 0
        else:
            self.hold_frames = self.jump_times[hold_frames]  # -1 is for no jump, but action is never 0
        self.speed = self.jump_speed
        self.fall()
    
    def fall(self):
        self.is_floor = False

    def floor_collision(self, height):
        if self.y < height:  
            self.y = height
            self.is_floor = True
            self.speed = 0
            self.angle = 0
            self.angle_speed = 0
import time
class EndlessRunner():

    def __init__(self):
        self.platforms = []  # List of platforms that are moved every tick
        self.max_height, self.min_height = HEIGHT - 100, 100
        self.min_gap = 50
        self.rest_width = 300 if not FLAT else 100000
        self.platform_width = 300

        # Player
        self.player_pos = WIDTH // 8, 100
        self.player : Player = self.construct_player(self.player_pos, size=30)
        self.deaths = -1
    
    def reset(self):
        self.deaths += 1
        self.score = 0
        self.level = 1
    
        # Player
        self.player.reset()
        # pos = WIDTH // 8, HEIGHT // 5
        # reset player position and rotation
        # self.player_max_jump_height = self.player.jump_speed * self.player.max_hold_frames

        # Platforms
        self.platforms = []
        self.current_platform = self.construct_platform(self.player_pos, self.level)
        self.platforms.append(self.current_platform)
        
        self.platforms += self.create_level()
        self.platforms += self.create_level()
        

    def tick(self):
        self.update_positions()
        self.current_platform = self.platform_transition(self.current_platform)
        if self.current_platform is False:
            return True  # Terminated
        
        if self.floor_collision(self.current_platform) is False:
            return True  # Terminated
        
        self.score += 1
        return False  # Terminated (replace all self.restart() with return True)
    
    def update_positions(self):
        """Update player and platforms positions. Also remove off screen platform."""
        self.player.move()

        for platform in self.platforms:
            platform.move()
        
        if self.platforms[0].right < 0:
            self.remove_platform()

    def platform_transition(self, platform : Platform):
        """Check if player is leaving current platform and reaching new platform.
        Also checks for wall collision when reaching new platform.

        :param platform: current platform
        :return: new platform
        """

        # Leaving current platform
        if platform and self.player.right > platform.right + 20:  # Grace
            platform = None
            self.player.fall()  # Let player fall

        # Reaching new platform 
        # ASSUMPTION A Leaving current platform assumes next platform is platforms[1]
            # this seems guraranteed currently?
        if platform is None and self.player.right > self.platforms[1].left:
            platform = self.platforms[1]

            # Wall collision
            if self.player.y < platform.top - 30:  # 30 Grace
                if not GOD:
                    print('Wall collision')
                    return False
                self.player.y = platform.top  # Assuming flat surface
            
            
            # Generate next level upon completing current level
            if platform.is_rest_area:
                self.platforms += self.create_level()

        return platform

    def floor_collision(self, platform : Platform):
        """Floor collision with platform and obstacle collision with player.
        Also checks for off screen death.

        :param platform: current platform
        """
        if platform:
            self.player.floor_collision(self.current_platform.top)

            # Check for obstacle collision
            # if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
            #     self.restart()
            #     return
        else:
            # Check for off screen
            if self.player.y < 0:
                if not GOD:
                    print("Off screen")
                    return False
                self.player.y = HEIGHT


    def create_level(self, count=3):
        self.level += 1
        platforms = []
        topright = self.platforms[-1].topright
        for _ in range(count):
            topleft = self._get_next_position(*topright)
            platforms.append(self.construct_platform(topleft))
            
            topright = platforms[-1].topright
            
        # Append rest area
        topleft = platforms[-1].topright
        platforms.append(self.construct_platform(topleft, self.level))

        return platforms

    def _get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        # max_jump_height = jump_speed * max_hold_frames + 0.5 * jump_speed ** 2 / gravity
        # up_time = jump_speed / gravity + max_hold_frames  # Increasing position time
        # fly_time = lambda self, delta_y: self.up_time + sqrt(2 * delta_y / self.gravity)
        
        v = self.player.jump_speed
        t1 = self.player.max_hold_frames
        h = v * t1

        g = self.player.gravity
        t2 = (v + sqrt(v ** 2 + 2*g*h)) / g

        max_y = min(int(y + 0.7 * h), self.max_height)  # 0.7 grace
        new_y = random.randrange(self.min_height, max_y)

        t = t1 + t2
        max_x = int(t * Platform.scroll_speed * 0.7)  # 0.7 grace
        new_x = x + random.randrange(self.min_gap, max_x)
        # print(f'---- {self.level} ----')
        # max_y = min(int(y + 0.7 * self.player.max_jump_height), self.max_height)  # 0.7 grace
        # new_y = random.randrange(self.min_height, max_y)

        # max_x = int(self.player.fly_time(new_y - max_y) * self.scroll_speed * 0.7)  # 0.7 grace
        # new_x = x + random.randrange(self.min_gap, max_x)
        
        return new_x, new_y
    
    def jump(self, action):
        if self.player.is_floor:
            self.player.jump(action)

    def construct_player(self, pos, size):
        return Player(pos, size)
    
    def construct_platform(self, topleft, level=0):
        width = self.rest_width if level else self.platform_width
        return Platform(topleft, width, level=level)

    def remove_platform(self):
        self.platforms.pop(0)



def main():
    game = EndlessRunner()
    game.reset()
    for _ in range(PRE_ACTIONS):
        game.tick()

if __name__ == "__main__":
    main()