from typing import Tuple
import numpy as np
import random
from math import sqrt

from game.config import Config
from game.entities import Player, Platform

random.seed(Config.SEED)
np.random.seed(Config.SEED)

class LevelGenerator():
    """Generates levels for the endless runner"""

    # Physics model
    size = Player.size
    speed = Platform.scroll_speed
    jump_speed = Player.jump_speed
    max_hold_frames = Player.max_hold_frames
    gravity = Player.gravity   

    max_height, min_height = Config.HEIGHT - 100, 100
    min_gap = 50

    air_times = [42, Player.max_hold_frames, Player.max_hold_frames // 2, 0]  # 42 is for no jump, but index is never 0

    def __init__(self):
        pass

    def get_level(self, start: Tuple[int, int], count: int):
        """Returns a level with a given number of platforms.
        :param start: x, y: top right of first platform.
        :param: count: Number of platforms.
        :return: A list of doubles (start, width).
        """
        platforms = []
        topright = start
        width = 300
        for _ in range(count):
            topleft = self._get_next_position(*topright)
            platforms.append((topleft, width))
            
            topright = topleft[0] + width, topleft[1]
            
        # Append rest area
        topleft = topleft[0] + width, topleft[1]
        platforms.append((topleft, width))
        return platforms

    def _get_next_position(self, x, y):
        """
        :param x, y: top right of previous platform
        :return: x, y: top left of next platform
        """
        v = self.jump_speed
        t1 = self.max_hold_frames
        h = v * t1

        g = self.gravity
        t2 = (v + sqrt(v ** 2 + 2*g*h)) / g

        max_y = min(int(y + 0.7 * h), self.max_height)  # 0.7 grace
        new_y = random.randrange(self.min_height, max_y)

        t = t1 + t2
        max_x = int(t * Platform.scroll_speed * 0.7)  # 0.7 grace
        new_x = x + random.randrange(self.min_gap, max_x)

        return new_x, new_y

    def generate(self):
        """Returns the geometry of a level"""
        rhythm = self._get_rhythm()
        return self._get_geometry(rhythm)

    def _get_rhythm(self, density = Config.DENSITY, duration = Config.DURATION, pattern = "random"):
        """Returns a rhythm of hatches. Rhythms are not constrained in any way.
        :param density: Number of hatches
        :param duration: Duration of the rhythm
        :param pattern: Pattern of hatches, either "regular" or "random"
        :return: A tuple of duration, [hatches, and type (hold_down times)]
        """
        if pattern == "regular":
            x = duration / (density + 1)
            hatches = [i * x for i in range(1, density + 1)]

        elif pattern == "random":    
            hatches = random.sample(np.arange(Config.UNIT, duration, 0.25).tolist(), density)
            # hatches = [random.randint(0, duration / UNIT ) * UNIT for _ in range(density)]


        # hold_down times
        # type = (np.random.randint(1, 4, density) * UNIT).tolist() 
        type = np.random.choice([0.3, 0.4, 0.5], 5, replace=True)
        jumps = list(zip(hatches, type))
        jumps.sort()  # Sort by hatch and then type

        return duration, jumps

    def _get_geometry(self, rhythm: tuple):
        """Convert a rhythm into a geometry of jumps constrained by physics
        :param rhythm: A tuple of duration, [hatches, and type (hold_down times)]
        :return: A list of jumps with hold_down times"""
        _, jumps = rhythm

        geometry = [jumps[0]]
        for jump in jumps[1:]: 
            # start time of next jump > end time of previous jump + hold_down time + unit
            if jump[0] > geometry[-1][0] + geometry[-1][1] + Config.UNIT: # 1.0 > 0.25 + 0.25 + 0.75 = 1.25
                geometry.append((jump))
        
        return geometry
    
# Rhythm   (5, [(0.25, 0.75), (1.0, 0.5), (1.5, 0.5), (2.5, 0.75), (3.25, 0.25), (3.5, 0.5), (4.0, 0.25), (4.25, 0.75), (4.5, 0.5), (4.75, 0.5)])
# Geo      [(0.25, 0.75), (1.5, 0.5), (2.5, 0.75), (4.0, 0.25), (4.75, 0.5)]
    
if __name__ == "__main__":
    level_generator = LevelGenerator()
    print(level_generator.generate())