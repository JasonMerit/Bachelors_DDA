import random
import numpy as np
from math import sqrt

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
    hold_frames = 0
    jump_threshold = 10
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
    
    def restart(self):
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

            self.y += self.speed
        # print(f'y: {self.y}')
    
    def jump(self):
        """Jump and hold jump if long is True. Written this way to accound for agent's jump."""
        self.is_holding = True
        self.hold_frames = 0
        self.speed = self.jump_speed
        self.fall()
    
    def fall(self):
        self.is_floor = False
        
        # d = self.jump_speed ** 2 + 2 * self.gravity * self.jump_speed * self.max_hold_frames
        # t = (self.jump_speed + sqrt(d)) / self.gravity + self.max_hold_frames
        # omega = self.rotations * 90 / t
        # # d = self.jump_speed ** 2 + 2 * self.gravity * (self.rect.bottom - self.max_jump_height)
        # self.angle_speed = omega

        # self.angle_speed = 5

    def floor_collision(self, height):
        if self.y < height:  
            self.y = height
            self.is_floor = True
            self.speed = 0
            self.angle = 0
            self.angle_speed = 0
    

class Game():
    

    def __init__(self):
        self.platforms = []  # List of platforms that are moved every tick
        self.rest_width = 300
        self.max_height, self.min_height = HEIGHT - 100, 100
        self.min_gap = 50
        self.platform_width = 300 if not FLAT else 100000

        # Player
        self.player_pos = WIDTH // 8, 100
        self.player = self.construct_player(self.player_pos, size=30)
        self.deaths = -1
    
    def restart(self):
        self.deaths += 1
        self.score = 0
        self.level = 0
    
        # Player
        self.player.restart()
        # pos = WIDTH // 8, HEIGHT // 5
        # reset player position and rotation
        # self.player_max_jump_height = self.player.jump_speed * self.player.max_hold_frames

        # Platforms
        self.platforms = []
        self.current_platform = self.construct_platform(self.player_pos, self.level + 1)
        # self.current_platform = self.construct_platform(pos, self.level + 1)
        self.platforms.append(self.current_platform)
        self.level += 1
        self.create_level()
        self.level += 1
        self.create_level()

    def tick(self):
        
        self.player.move()
        # Platform.move_all(-self.scroll_speed)
        for platform in self.platforms:
            platform.move()
            # platform.move(-self.scroll_speed)

            # if platform.right < 0:
            #     self.remove_platform()
        
        if self.platforms[0].right < 0:
            self.remove_platform()
        
        # -----| Platform Transitions |-----
        # Leaving current platform
        if self.current_platform and self.player.right > self.current_platform.right + 20:  # Grace
            self.current_platform = None
            self.player.fall()  # Let player fall

        # Reaching new platform 
        # ASSUMPTION A Leaving current platform assumes next platform is platforms[1]
        if self.current_platform is None and self.player.right > self.platforms[1].left:
            platform = self.platforms[1]

            # Wall collision
            if self.player.y < platform.top - 30:  # 30 Grace
                if not GOD:
                    self.restart()
                    return
                self.player.y = platform.top
            
            
            # Generate next level upon completing current level
            if platform.is_rest_area:
                self.level += 1
                self.create_level()

            self.current_platform = platform

        # -----| Collision check |-----
        if self.current_platform:
            self.player.floor_collision(self.current_platform.top)

            # Check for obstacle collision
            # if not GOD and pg.sprite.spritecollide(self.player, self.obstacle_sprites, False):
            #     self.restart()
            #     return
        else:
            # Check for off screen
            if self.player.y < 0:
                if not GOD:
                    self.restart()
                    return
                self.player.y = HEIGHT
        self.score += 1
    
    def create_level(self, count=4):
        for _ in range(count):
            x, y = self.get_next_position(*self.platforms[-1].topright)
            # x, y = self.platforms[-1].topright
            # x += self.min_gap
            self.platforms.append(self.construct_platform((x, y)))
        # Append rest area
        topleft = self.platforms[-1].topright
        self.platforms.append(self.construct_platform(topleft, self.level + 1))

    def get_next_position(self, x, y):
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
    

    def construct_player(self, pos, size):
        return Player(pos, size)
    
    def construct_platform(self, topleft, level=0):
        width = self.rest_width if level else self.platform_width
        return Platform(topleft, width, level=level)

    def remove_platform(self):
        self.platforms.pop(0)
    
def main():
    game = Game()
    game.restart()
    for _ in range(PRE_ACTIONS):
        game.tick()

if __name__ == "__main__":
    main()