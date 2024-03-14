import random
import numpy as np
from math import sqrt
import typing


from rhythm_generator import LevelGenerator
from config import *
from util import *
from entities import Player, Platform


class EndlessRunner():

    def __init__(self):
        self.level_generator = LevelGenerator()
        self.max_height, self.min_height = HEIGHT - 100, 100
        self.min_gap = 50
        self.rest_width = 300 if not FLAT else 100000
        self.platform_width = 300

        # Player
        Player.init_pos = Player.init_pos[0], HEIGHT//2
        self.player : Player = self.construct_player()
        self.deaths = -1
    
    def reset(self):
        self.deaths += 1
        self.score = 0
        self.level = 1
    
        # Player
        self.player.reset()

        # List of platforms that are moved every tick
        self.platforms = [self.construct_platform(Player.init_pos, level=self.level)]  
        self.platforms[0].outline() # debug
        
        self.platforms += self._create_level()
        self.platforms += self._create_level()
        
        self.player.platforms = self.platforms  # Dirty coupling
        self.player.current_platform = self.platforms[0]  # Dirty coupling
        self.player.next_platform = self.platforms[1]  # Dirty coupling

    def tick(self):
        self._update_positions()

        if self.player.tick() is True:
            return True  # Terminated
        
        self.score += 1  # Increase score every tick
        return False  # Terminated (replace all self.restart() with return True)

    def render(self):
        pass  # Implemented in Display
    
    def _update_positions(self):
        """Update player and platforms positions. Also remove off screen platform."""

        for platform in self.platforms:
            platform.move()
        
        if self.platforms[0].right < 0:
            if VERBOSE:
                print("Removing", self.platforms[0])
            
            if self.platforms[0].is_rest_area:
                self.platforms += self._create_level()
                
            self.remove_platform()

    def _create_level(self, count=3):
        """Create a new level of platforms and rest area.
        :param count: number of platforms in the level
        :return: list of platforms
        """
        
        self.level += 1
        platforms = []
        
        # if self.level_generator is None:
        if not GAME:
            topright = self.platforms[-1].topright
            for _ in range(count):
                topleft = self._get_next_position(*topright)
                platforms.append(self.construct_platform(topleft))
                
                topright = platforms[-1].topright
                
            # Append rest area
            topleft = platforms[-1].topright
            platforms.append(self.construct_platform(topleft, level=self.level))
            return platforms
        

        # Geometry: [(4.0, 0.5), (8.0, 0.25), (12.0, 0.75), (16.0, 0.75)]
        # geometry = self.level_generator.generate()
        # start = self.platforms[-1].right
        # unit = 300
        # stamp_prev = 0
        # for geo in geometry:
        #     stamp, hold = geo
        #     width = (stamp - stamp_prev) * unit
        #     topleft = (start + hold * unit, self.player_pos[1])
        #     platform = self.construct_platform(topleft, width)

        #     print(topleft, width)
        #     platforms.append(platform)
        #     start = platform.right
        #     stamp_prev = stamp + hold

        # topleft = platforms[-1].topright
        # platforms.append(self.construct_platform(topleft, level=self.level))
        
        topright = self.platforms[-1].topright
        for _ in range(count):
            platforms.append(self.construct_platform(topright))
            topright = platforms[-1].topright
        # topleft = platforms[-1].topright
        platforms.append(self.construct_platform(topright, level=self.level))

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
        
        # return 1000, new_y
        if TOUCHING:
            return x, new_y
        return new_x, new_y
    
    def jump(self, action):
        if self.player.is_floor:
            self.player.jump(action)


    ### ===== Inherited by Display ===== ###
    def construct_player(self):
        return Player()
    
    def construct_platform(self, topleft, width=300, level=0):
        return Platform(topleft, width, level=level)

    def remove_platform(self):
        self.platforms.pop(0)


def main():
    game = EndlessRunner()
    game.reset()
    for _ in range(PRE_ACTIONS):
        done = game.tick()
        if done:
            game.reset()

if __name__ == "__main__":
    main()