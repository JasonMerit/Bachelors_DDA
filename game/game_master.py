from typing import Tuple
import numpy as np
import random
from math import sqrt

from game.config import Config
from game.entities import Player, Platform

class GameMaster():
    """Generates levels for the endless runner"""

    # Physics model
    size = Player.size
    speed = Platform.scroll_speed
    jump_speed = Player.jump_speed
    max_hold_frames = Player.max_hold_frames
    gravity = Player.gravity   

    max_height, min_height = Config.HEIGHT - 100, 100
    min_gap = 50
    min_width = 100

    air_times = Player.jump_times

    def __init__(self):
        self.difficulty = 0.7

    def seed(self, seed):
        random.seed(seed)
        np.random.seed(seed)
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def get_level(self, start: Tuple[int, int], count: int):
        """Returns a level with a given number of platforms.
        :param start: x, y: top right of first platform.
        :param: count: Number of platforms.
        :return: A list of doubles (start, width).
        """
        platforms = []
        topright = start
        width = self.min_width# + random.randrange(0, int(100 * (1 - difficulty)))
        for _ in range(count):
            topleft = self._get_next_position(*topright)
            platforms.append((topleft, width))
            
            topright = topleft[0] + width, topleft[1]
            
        # Append rest area
        topleft = topleft[0] + width, topleft[1]
        platforms.append((topleft, width))
        return platforms
    
    def next_platform(self, x, y):
        return self._get_next_position(x, y), self.min_width

    def _get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        v = self.jump_speed
        t1 = self.max_hold_frames
        g = self.gravity

        # First constant velocity jump
        h1 = v * t1

        # Second projectile motion jump
        ### y(t) = h1 + vt - 1/2gt^2 = b = min_height

        # Time of peak of projectile motion is when v(t) = 0 <=> t = v/g
        # peak = v / g * v - 0.5 * g * (v / g) ** 2 = v ** 2 / (2 * g)
        h2 = v ** 2 / (2 * g)
        
        H = min(int(y + h1 + h2), self.max_height)
        
        new_y = random.randrange(self.min_height, int(H * Config.grace_multiply))

        # Max possible air time lands at minimum height
        t2 = (v + sqrt(v ** 2 + 2*g*(y + h1 - new_y))) / g
        T = (t1 + t2) * self.difficulty
        G = int(T * Platform.scroll_speed) 
        new_x = x + G
        # new_x = x + random.randrange(self.min_gap, G)

        # return max_x, H
        return new_x, new_y