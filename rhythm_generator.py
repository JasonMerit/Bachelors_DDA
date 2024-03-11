import numpy as np
import random

from config import *
from entities import Player, Platform

random.seed(SEED)
np.random.seed(SEED)

class LevelGenerator():
    """Generates levels for the endless runner"""

    # Physics model
    size = Player.size
    speed = Platform.scroll_speed
    jump_speed = Player.jump_speed
    gravity = Player.gravity   

    air_times = [42, Player.max_hold_frames, Player.max_hold_frames // 2, 0]  # 42 is for no jump, but index is never 0

    def __init__(self):
        pass

    def generate(self):
        """Returns the geometry of a level"""
        rhythm = self._get_rhythm()
        return self._get_geometry(rhythm)

    def _get_rhythm(self, density = DENSITY, duration = DURATION, pattern = "random"):
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
            hatches = random.sample(np.arange(UNIT, duration, 0.25).tolist(), density)
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
            if jump[0] > geometry[-1][0] + geometry[-1][1] + UNIT: # 1.0 > 0.25 + 0.25 + 0.75 = 1.25
                geometry.append((jump))
        
        return geometry
    
# Rhythm   (5, [(0.25, 0.75), (1.0, 0.5), (1.5, 0.5), (2.5, 0.75), (3.25, 0.25), (3.5, 0.5), (4.0, 0.25), (4.25, 0.75), (4.5, 0.5), (4.75, 0.5)])
# Geo      [(0.25, 0.75), (1.5, 0.5), (2.5, 0.75), (4.0, 0.25), (4.75, 0.5)]
    
if __name__ == "__main__":
    level_generator = LevelGenerator()
    print(level_generator.generate())