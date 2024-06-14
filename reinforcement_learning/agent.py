from math import sqrt
from icecream import ic

class CheaterAgent():
    
    from game.config import Config
    from game.entities import Platform
    from game.player import Player


    speed = Platform.scroll_speed
    jump_speed = Player.jump_speed
    air_times = Player.jump_times  # [max_hold_frames, max_hold_frames // 2, 0] 
    jump_times = Player.jump_times
    max_hold_frames = Player.max_hold_frames
    gravity = Player.gravity   
    size = Player.size
    
    peak = jump_speed ** 2 / (2 * gravity)
    jump_height = jump_speed * max_hold_frames + peak
    peak_time = speed / gravity

    def __init__(self, verbose=False):
        self.verbose = verbose

    def predict(self, obs, state=None, episode_start=None, deterministic=True):
        x1, dx, dy = obs[0]
        # return [0], None
        # return [1], None
        # action = int(x1 < 50) * 3 
        # return [action], None
        
        # ic(x1)
        # return 1 if lower than 18

        # time to reach x1 + dx (next platform)
        t_travel = (x1 + dx) / self.speed

        # first jump to exceed t_travel in time is used
        # d = self.jump_speed**2 + 2 * self.gravity * (self.jump_speed * self.max_hold_frames - dy)
        # t = self.max_hold_frames + (self.jump_speed + sqrt(d)) / self.gravity
        # if t > t_travel:
        #     return [3], None
        # return [0], None
        if dy < 0: # Wait until end of platform and fall
            t_wait = (x1 + self.size) / self.speed
            t_fall = sqrt(-2 * dy / self.gravity)

            if t_fall + t_wait > t_travel:
                return [0], None
            
        for i, hold_time in enumerate(self.jump_times[::-1]):
            hold_time += 1
            d = self.jump_speed**2 + 2 * self.gravity * (self.jump_speed * hold_time - dy)
            if d < 0:
                continue
            t = hold_time + (self.jump_speed + sqrt(d)) / self.gravity
            if t > t_travel:
                return [i + 1], None
        return [0], None
    