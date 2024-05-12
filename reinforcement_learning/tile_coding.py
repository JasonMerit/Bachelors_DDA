from math import floor
import numpy as np

class LinearQEncoder():
    """Num-tilings should be a power of 2, e.g., 16. To make the offsetting work properly, 
    it should also be greater than or equal to four times the number of floats."""
    def __init__(self, env, tilings=2**10, max_size=2**12):
        # 9, because 2^9 = 512 and obs_range = 656

        # os = env.observation_space
        # low = os.low    # [325. 210. 210.]
        # high = os.high  # [   0.   45. -400.]

        low = np.array([0, 45, -400], dtype=np.float16)
        high = np.array([325, 210, 210], dtype=np.float16)

        scale = tilings / (high - low)
        hash_table = IHT(max_size)
        self.max_size = max_size
        def tile_representation(s):
        # def tile_representation(s, action):
            s_ = list( (s*scale).flat )
            active_tiles = tiles(hash_table, tilings, s_,) # (s * scale).tolist()
            # active_tiles = tiles(hash_table, tilings, s_, [action]) # (s * scale).tolist()
            return active_tiles
        
        self.get_active_tiles = tile_representation

        np.random.seed(42)  # Same representation for same state
        [self.x((np.random.uniform(low, high))) for _ in range(max_size // tilings)]
        assert hash_table.count() >= max_size
    
    def x(self, s):
    # def x(self, s, a):
        x = np.zeros(self.max_size)
        at = self.get_active_tiles(s)
        # at = self.get_active_tiles(s, a)
        x[at] = 1.0
        return x
    
"""
Following code contains the tile-coding utilities copied from:
http://incompleteideas.net/tiles/tiles3.py-remove
"""
class IHT:
    "Structure to handle collisions"

    def __init__(self, size_val):
        self.size = size_val
        self.overfull_count = 0
        self.dictionary = {}

    def count(self):
        return len(self.dictionary)

    def full(self):
        return len(self.dictionary) >= self.size

    def get_index(self, obj, read_only=False):
        d = self.dictionary
        if obj in d:
            return d[obj]
        elif read_only:
            return None
        size = self.size
        count = self.count()
        if count >= size:
            # if self.overfull_count == 0: print('IHT full, starting to allow collisions')
            self.overfull_count += 1
            return hash(obj) % self.size
        else:
            d[obj] = count
            return count


def hash_coords(coordinates, m, read_only=False):
    if isinstance(m, IHT): return m.get_index(tuple(coordinates), read_only)
    if isinstance(m, int): return hash(tuple(coordinates)) % m
    if m is None: return coordinates


def tiles(iht_or_size, num_tilings, floats, ints=None, read_only=False):
    """returns num-tilings tile indices corresponding to the floats and ints"""
    if ints is None:
        ints = []
    qfloats = [floor(f * num_tilings) for f in floats]
    tiles = []
    for tiling in range(num_tilings):
        tilingX2 = tiling * 2
        coords = [tiling]
        b = tiling
        for q in qfloats:
            coords.append((q + b) // num_tilings)
            b += tilingX2
        coords.extend(ints)
        tiles.append(hash_coords(coords, iht_or_size, read_only))
    return tiles

