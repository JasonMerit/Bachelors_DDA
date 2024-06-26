from typing import Tuple
import random
from math import sqrt

from game.config import Config
from game.entities import Platform
from game.player import Player

class GameMaster():
    """Generates levels for the endless runner"""

    # Physics model
    size = Player.size
    speed = Platform.scroll_speed
    jump_speed = Player.jump_speed
    air_times = Player.jump_times
    max_hold_frames = Player.max_hold_frames
    gravity = Player.gravity   

    max_height, min_height = Config.height - 100, 100
    min_gap = 20
    platform_width = 100#50

    # Precomputed values
    jump_height = jump_speed * max_hold_frames + jump_speed ** 2 / (2 * gravity)


    # def __init__(self):
    #     random.seed(39)
    
    def set_difficulty(self, difficulty: Tuple[int, int]):
        assert 0 <= difficulty[0] <= 10, "Difficulty must be between 0 and 10"
        self.gap_multiplier = sqrt(difficulty[0] / 10)
        self.death_prob = difficulty[1] ** 0.5 / 100
        # self.death_prob = difficulty[1] / 50

    def clamp(self, y):
        return min(max(int(y), self.min_height), self.max_height)
    
    # def seed(self, seed):
    #     return #  When evaluating, since stablebaselines3 sets to same seed everytime
    #     random.seed(seed)
    
    # def get_state(self):
    #     return random.getstate()
    
    # def set_state(self, state):
    #     random.setstate((3, state, None))

    def next_platform(self, x, y):
        """Returns the next platform's position and width."""
        # return (x + 100, y), 150
        return self._get_next_position(x, y), self.platform_width
    
    def _fly_time(self, a, b):
        """Using the kinematic equation for constant acceleration, solve for time to reach a certain height.
        This includes the duration of the constant velocity jump."""
        return self.max_hold_frames + (self.jump_speed + sqrt(self.jump_speed**2 + 2 * self.gravity * (self.jump_speed * self.max_hold_frames + a - b))) / self.gravity

    def _get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        if random.random() < self.death_prob:
            return x, int(1.5 * Config.height)
        
        H = min(int(y + self.jump_height), self.max_height)
        dy = random.randrange(self.min_height, H) - y
        y_new = y + self.gap_multiplier * dy

        T = self._fly_time(y, y_new)
        dx = T * self.speed  #(0.3, 0.6)
        dx = random.randrange(int(dx / 4), int(dx))  # Randomize distance
        x_new = x + int(self.gap_multiplier * dx)
        # print(int(y_new))
        return x_new, int(y_new)