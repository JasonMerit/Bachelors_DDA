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
    air_times = Player.jump_times
    max_hold_frames = Player.max_hold_frames
    gravity = Player.gravity   

    max_height, min_height = Config.HEIGHT - 100, 100
    min_gap = 50
    min_width = 100

    # Precomputed values
    jump_height = jump_speed * max_hold_frames + jump_speed ** 2 / (2 * gravity)


    def __init__(self):
        self.difficulty = 0.7

    def clamp(self, y):
        return min(max(int(y), self.min_height), self.max_height)
    
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
    
    def _fly_time(self, a, b):
        """Using the kinematic equation for constant acceleration, solve for time to reach a certain height.
        This includes the duration of the constant velocity jump."""
        return self.max_hold_frames + (self.jump_speed + sqrt(self.jump_speed**2 + 2 * self.gravity * (self.jump_speed * self.max_hold_frames + a - b))) / self.gravity

    def _get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        H = min(int(y + self.jump_height), self.max_height)
        dy = random.randrange(self.min_height, H) - y
        y_new = y + self.difficulty * dy

        T = self._fly_time(y, y_new)
        x_new = x + int(self.difficulty * T * self.speed)

        return x_new, int(y_new)