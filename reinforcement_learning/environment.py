from typing import Tuple
import random
from math import sqrt

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from game.display import Display
from game.endless_runner import EndlessRunner

class EndlessRunnerEnv(gym.Env):
    """The purpose of the environment is to provide a standard interface for the 
    agent to interact with the game. Display enherits from EndlessRunner, so it
    can be used to run the game with rendering."""

    action_space = spaces.Discrete(2)  # Binary (Update step too)
    # action_space = spaces.Discrete(4)  # Multiple
    
    # x1, dx, dy
    # Update _step too
    # observation_space = spaces.Box(low=np.array([0.0, 45.0, -400], dtype=np.float16), 
    #                                high=np.array([325.0, 210.0, 210.0], dtype=np.float16), 
    #                                shape=(3,), dtype=np.float16)
    # x1
    observation_space = spaces.Box(low=np.array([0.0], dtype=np.float16), 
                                   high=np.array([325.0], dtype=np.float16), 
                                   shape=(1,), dtype=np.float16)
    # x1, dist_obstacle
    # observation_space = spaces.Box(low=np.array([0.0, 0.0], dtype=np.float16), 
    #                             high=np.array([325.0, 300.0], dtype=np.float16), 
    #                             shape=(2,), dtype=np.float16)
    # x0 in [0.0, 325.0] 
    # dx in [45.0, 209.0]
    # dy in [-399.0, 205.0]
    # observation_space = spaces.Box(low=range[0], high=range[1], shape=(3,), dtype=np.float16)
    # observation_space = spaces.Box(low=0, high=1000, shape=(3,), dtype=np.float16)
    max_steps = 2_500
    max_platforms = 100

    def __init__(self, difficulty=None, render=False, truncated=True):
        """
        If difficulty is given, the game difficulty won't change.
        """
        self.game = Display() if render else EndlessRunner()
        self.difficulty = difficulty  # If not None, difficulty won't change
        if difficulty:
            self.game.set_difficulty(difficulty)
        self._truncate = lambda: self.current_cleard_platforms >= self.max_platforms if truncated else False
        # self._truncate = lambda: self.step_count >= self.max_steps if truncated else False
        self._render = render
        
        self.player = self.game.player
        self.current_cleard_platforms = 0
        

    def step(self, action):
        """Actions:
        0: Do nothing
        1-3: Jump ranges from short to long
        """
        self.step_count += 1
        # cleared_platforms = self.game.player.cleared_platforms
        if action > 0:
            self.game.take_action(2)              # Binary
            # self.game.take_action(action - 1)     # Multiple
        
        terminated = self.game.tick()
        self.render()

        # keep ticking until player is on floor or game is over
        while not self.game.player.is_floor and not terminated:
            terminated = self.game.tick()
            self.render()

        # REWARD
        # reward = -10 if terminated else 1  # Tue
        # reward = 1 - int(terminated)
        reward = int(self.game.player.cleared_platforms > self.current_cleard_platforms)
        self.current_cleard_platforms = self.game.player.cleared_platforms
        
        return self._state(), reward, terminated, self._truncate(), {}
    
    def reset(self, seed=None, difficulty=None):
        # super().reset()
        # super().reset(seed=seed)

        if self.difficulty is None:
            if difficulty is None:
                difficulty = random.randint(1, 10), 0
                # difficulty = random.randint(1, 3), 0
            self.game.set_difficulty(difficulty)
        
        self.game.reset()
        # self.game.reset(seed)
        self.step_count = 0
        self.current_cleard_platforms = 0
        return self._state(), {}
    
    def render(self, state=None):
        if self._render:
            self.game.render(state, self.step_count)
    
    def close(self):
        self.game.close()
    
    def _state(self):
        """Return the state consisting of the tuple
        - player on floor (0, 1)
        - topright of the first platform
        - topleft of the second platform
        """
        # First platform with platform_left > player_right
        index = 0
        plat1 = self.game.platforms[index]
        while plat1.right < self.game.player.left:
            index += 1
            plat1 = self.game.platforms[index]
            assert index < len(self.game.platforms), "Player is not on a platform"
        plat2 = self.game.platforms[index + 1]
        

        topright = plat1.topright
        topleft = plat2.topleft
        x1 = topright[0] - self.game.player.left
        dx = topleft[0] - topright[0]
        dy = topleft[1] - topright[1]
        
        # Search for next obstacle
        dist_obstacle = 0
        for obstacle in self.game.obstacles:
            if obstacle.left > self.game.player.left:
                dist_obstacle = obstacle.left - self.game.player.left
                break
        # dist_obstacle = self.game.obstacles[0].left - self.game.player.left \
        #     if len(self.game.obstacles) > 0 else 0
        
        return np.array([x1]).astype(np.float16)  # Scalar
        return np.array([x1, dist_obstacle]).astype(np.float16)  # Scalar + obstacle
        return np.array([x1, dx, dy]).astype(np.float16)
    
    # def get_random_state(self):
    #     return self.game.get_random_state()
    
    # def get_player_state(self):
    #     p = self.game.player
    #     print(f"{p.y = }, {p.speed = }") 
    #     return p.y, p.speed

from reinforcement_learning.tile_coding import LinearQEncoder

class TileER(EndlessRunnerEnv):
    """Tile Encoding Rewarder"""
    observation_space = spaces.MultiBinary(4096)
    
    def __init__(self, render=False, truncated=True):
        super().__init__(render, truncated=truncated)
        self.encoder = LinearQEncoder(self)

    def _state(self):
        state = super()._state()
        return self.encoder.x(state)

class Parrot(gym.Env):
    max_steps = 10

    def __init__(self, difficulty=None, render=False):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Discrete(2)
    
    def step(self, action):
        self.step_count += 1
        reward = int(action == self.last_observation)
        self.last_observation = self.observation_space.sample()
        truncated = self.step_count >= self.max_steps
        return np.array(self.last_observation).astype(np.float16), reward, False, truncated, {}
    
    def reset(self, seed=None):
        self.step_count = 0
        self.last_observation = self.observation_space.sample()
        return np.array(self.last_observation).astype(np.float16), {}
    
    def render(self, state=None):
        pass

    def close(self):
        pass

class BoxEnv(gym.Env):
    max_steps = 10

    action_space = spaces.Discrete(2)
    observation_space = spaces.Box(low=np.array([0.0], dtype=np.float16), 
                                   high=np.array([100.0], dtype=np.float16), 
                                   shape=(1,), dtype=np.float16)
    def __init__(self):
        pass

    def step(self, action):
        self.step_count += 1
        reward = int(action == self.last_observation)
        self.last_observation = self.observation_space.sample()
        truncated = self.step_count >= self.max_steps
        return np.array(self.last_observation).astype(np.float32), reward, False, truncated, {}
    
    def reset(self, seed=None):
        self.step_count = 0
        self.last_observation = self.observation_space.sample()
        return np.array(self.last_observation).astype(np.float32), {}
    
    def render(self, state=None):
        pass

    def close(self):
        pass


# from stable_baselines3.common.env_checker import check_env
# check_env(env, warn=True)
    # https://colab.research.google.com/github/araffin/rl-tutorial-jnrr19/blob/sb3/5_custom_gym_env.ipynb#scrollTo=1CcUVatq-P0l
# https://stable-baselines3.readthedocs.io/en/master/guide/custom_env.html
    
