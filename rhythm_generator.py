import numpy as np
import random

from config import *
# from entities import Player

random.seed(SEED)
np.random.seed(SEED)

class LevelGenerator():

    def generate(self):
        """Returns the geometry of a level"""
        rhythm = self._get_rhythm()
        return self._get_geometry(rhythm)

    def _get_rhythm(self, density = DENSITY, duration = DURATION, pattern = "regular"):
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


        # hold_down time multiple of UNIT
        type = (np.random.randint(1, 4, density) * UNIT).tolist() 
        jumps = list(zip(hatches, type))
        jumps.sort()  # Sort by hatch and then type

        return duration, jumps

    def _get_geometry(self, rhythm: tuple):
        """Convert a rhythm into a geometry of jumps constrained by physics
        :param rhythm: A tuple of duration, [hatches, and type (hold_down times)]
        :return: A list of jumps with hold_down times"""
        _, jumps = rhythm
        jumps = jumps.copy()

        geometry = [jumps[0]]
        for jump in jumps[1:]: # If jump to quick after prior, skip it
            if jump[0] - geometry[-1][0] > UNIT + geometry[-1][1]:
                geometry.append((jump))
        
        return geometry
    
